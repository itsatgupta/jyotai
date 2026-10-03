"""Stateless deterministic analysis endpoint for the first browser vertical slice."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from astrologer.application.analyze import (
    DeterministicAnalysisRequest,
    DeterministicAnalysisResult,
    DeterministicAnalysisService,
)
from astrologer.application.context import (
    DeterministicAstrologyContextService,
    DeterministicContextInputError,
)
from astrologer.astrology.swiss_ephemeris import (
    SwissEphemerisCalculationError,
    SwissEphemerisProvider,
)

router = APIRouter(prefix="/api/v1", tags=["analysis"])


def get_analysis_service() -> DeterministicAnalysisService:
    """Construct the approved service graph once per stateless request."""
    provider = SwissEphemerisProvider()
    return DeterministicAnalysisService(DeterministicAstrologyContextService(provider))


@router.post("/analyze", response_model=DeterministicAnalysisResult)
async def analyze(
    request: DeterministicAnalysisRequest,
    service: Annotated[DeterministicAnalysisService, Depends(get_analysis_service)],
) -> DeterministicAnalysisResult:
    """Return deterministic facts, routing, and selected governed evidence only."""
    try:
        return service.analyze(request)
    except DeterministicContextInputError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error
    except (SwissEphemerisCalculationError, RuntimeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Deterministic analysis is temporarily unavailable.",
        ) from error
