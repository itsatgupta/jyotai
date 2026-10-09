"""Factual Vimshottari timing endpoint; it deliberately has no interpretation path."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from astrologer.application.timing import (
    VimshottariTimingFacts,
    VimshottariTimingRequest,
    VimshottariTimingService,
)
from astrologer.astrology.swiss_ephemeris import (
    SwissEphemerisCalculationError,
    SwissEphemerisProvider,
)

router = APIRouter(prefix="/api/v1/timing", tags=["timing"])


def get_vimshottari_timing_service() -> VimshottariTimingService:
    """Construct the provider-backed factual timing service."""
    return VimshottariTimingService(SwissEphemerisProvider())


@router.post("/vimshottari", response_model=VimshottariTimingFacts)
async def calculate_vimshottari_timing(
    request: VimshottariTimingRequest,
    service: Annotated[VimshottariTimingService, Depends(get_vimshottari_timing_service)],
) -> VimshottariTimingFacts:
    """Return bounded deterministic MD/AD facts only; never an event prediction."""
    try:
        return service.build(request)
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
