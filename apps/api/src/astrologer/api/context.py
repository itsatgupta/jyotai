"""Stateless deterministic astrology-context endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from astrologer.application.context import (
    DeterministicAstrologyContext,
    DeterministicAstrologyContextService,
    DeterministicContextInputError,
    DeterministicContextRequest,
)
from astrologer.astrology.swiss_ephemeris import (
    SwissEphemerisCalculationError,
    SwissEphemerisProvider,
)

router = APIRouter(prefix="/api/v1/context", tags=["context"])


def get_context_service() -> DeterministicAstrologyContextService:
    """Construct one explicit deterministic service with the configured provider adapter."""
    return DeterministicAstrologyContextService(SwissEphemerisProvider())


@router.post("/snapshot", response_model=DeterministicAstrologyContext)
async def calculate_context_snapshot(
    request: DeterministicContextRequest,
    service: Annotated[DeterministicAstrologyContextService, Depends(get_context_service)],
) -> DeterministicAstrologyContext:
    """Compose deterministic chart, timing, transit, and D1 structural outputs only."""
    try:
        return service.build(request)
    except DeterministicContextInputError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error
    except (SwissEphemerisCalculationError, RuntimeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Deterministic context calculation is temporarily unavailable.",
        ) from error
