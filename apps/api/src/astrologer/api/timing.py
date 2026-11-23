"""Factual Vimshottari timing endpoint; it deliberately has no interpretation path."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from astrologer.api.dependencies import DashaEngineDependency, get_dasha_engine
from astrologer.application.timing import (
    VimshottariTimingFacts,
    VimshottariTimingRequest,
    VimshottariTimingService,
)
from astrologer.astrology.chart import ChartEngine
from astrologer.astrology.swiss_ephemeris import (
    SwissEphemerisCalculationError,
    SwissEphemerisProvider,
)
from astrologer.timing_rules import (
    CareerTimingAnalysisService,
    CareerTimingRequest,
    CareerTimingResponse,
)

router = APIRouter(prefix="/api/v1/timing", tags=["timing"])

__all__ = ["get_dasha_engine", "router"]


def get_vimshottari_timing_service(
    dasha_engine: DashaEngineDependency,
) -> VimshottariTimingService:
    """Construct the provider-backed factual timing service on the injected engine."""
    return VimshottariTimingService(SwissEphemerisProvider(), dasha_engine=dasha_engine)


def get_career_timing_analysis_service(
    dasha_engine: DashaEngineDependency,
) -> CareerTimingAnalysisService:
    """Construct the explicitly selected production Career timing service."""
    provider = SwissEphemerisProvider()
    chart_engine = ChartEngine(provider)
    return CareerTimingAnalysisService(
        provider,
        chart_engine=chart_engine,
        timing_service=VimshottariTimingService(provider, chart_engine, dasha_engine=dasha_engine),
    )


@router.post("/vimshottari", response_model=VimshottariTimingFacts)
async def calculate_vimshottari_timing(
    request: VimshottariTimingRequest,
    service: Annotated[VimshottariTimingService, Depends(get_vimshottari_timing_service)],
    dasha_engine: DashaEngineDependency,
) -> VimshottariTimingFacts:
    """Return bounded deterministic MD/AD facts only; never an event prediction."""
    try:
        return service.build(request, dasha_engine=dasha_engine)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error
    except (SwissEphemerisCalculationError, RuntimeError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Deterministic timing calculation is temporarily unavailable.",
        ) from error


@router.post("/analyze", response_model=CareerTimingResponse)
async def analyze_governed_career_timing(
    request: CareerTimingRequest,
    service: Annotated[CareerTimingAnalysisService, Depends(get_career_timing_analysis_service)],
    dasha_engine: DashaEngineDependency,
) -> CareerTimingResponse:
    """Return governed broad Career timing from the active production release only."""
    try:
        return service.analyze(request, dasha_engine=dasha_engine)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error
    except (SwissEphemerisCalculationError, RuntimeError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Deterministic timing calculation is temporarily unavailable.",
        ) from error
