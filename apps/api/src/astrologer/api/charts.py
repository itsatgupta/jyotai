"""Stateless deterministic chart-calculation endpoint for staging verification."""

from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict

from astrologer.astrology.chart import Chart, ChartEngine, ChartMethodology
from astrologer.astrology.ephemeris import EphemerisProvenance
from astrologer.astrology.swiss_ephemeris import (
    SwissEphemerisCalculationError,
    SwissEphemerisProvider,
)
from astrologer.astrology.vargas import DivisionalChart, DivisionalChartType, VargaEngine
from astrologer.birth.models import BirthInput

router = APIRouter(prefix="/api/v1/charts", tags=["charts"])


class ChartCalculationResponse(BaseModel):
    """Deterministic D1 and supported Varga facts from one validated birth input."""

    model_config = ConfigDict(frozen=True)

    birth_input: BirthInput
    calculation_instant: datetime
    d1: Chart
    d2: DivisionalChart
    d9: DivisionalChart
    d10: DivisionalChart
    calculation_methodology: ChartMethodology
    ephemeris_provenance: EphemerisProvenance


@router.post("/calculate", response_model=ChartCalculationResponse)
async def calculate_chart(birth_input: BirthInput) -> ChartCalculationResponse:
    """Calculate existing deterministic D1, D2, D9, and D10 facts without persistence."""
    try:
        d1 = ChartEngine(SwissEphemerisProvider()).calculate(birth_input)
        vargas = {chart.methodology.chart_type: chart for chart in VargaEngine().calculate_all(d1)}
    except (SwissEphemerisCalculationError, RuntimeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chart calculation is temporarily unavailable.",
        ) from error

    return ChartCalculationResponse(
        birth_input=birth_input,
        calculation_instant=d1.calculation_instant,
        d1=d1,
        d2=vargas[DivisionalChartType.D2],
        d9=vargas[DivisionalChartType.D9],
        d10=vargas[DivisionalChartType.D10],
        calculation_methodology=d1.methodology,
        ephemeris_provenance=d1.provenance,
    )
