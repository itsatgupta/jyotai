"""Public API for fixed governed post-Kundli dashboard domains."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from astrologer.api.analyze import get_analysis_service
from astrologer.application.context import DeterministicContextInputError
from astrologer.application.dashboard_insights import (
    DashboardInsightsRequest,
    DashboardInsightsResult,
    DashboardInsightsService,
)
from astrologer.astrology.swiss_ephemeris import SwissEphemerisCalculationError
from astrologer.composition import AnswerCompositionError, DeterministicAnswerComposer
from astrologer.evidence import InterpretationEvidenceBuilder, InterpretationEvidenceBuildError

router = APIRouter(prefix="/api/v1/insights", tags=["insights"])


def get_dashboard_insights_service() -> DashboardInsightsService:
    """Use deterministic reviewed wording; this endpoint never requires a provider."""
    return DashboardInsightsService(
        get_analysis_service(), InterpretationEvidenceBuilder(), DeterministicAnswerComposer()
    )


@router.post("/dashboard", response_model=DashboardInsightsResult)
async def dashboard_insights(
    request: DashboardInsightsRequest,
    service: Annotated[DashboardInsightsService, Depends(get_dashboard_insights_service)],
) -> DashboardInsightsResult:
    """Return fixed exact-domain insights without invoking question routing."""
    try:
        return service.retrieve(request)
    except DeterministicContextInputError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
        ) from error
    except (AnswerCompositionError, InterpretationEvidenceBuildError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Governed dashboard insights are temporarily unavailable.",
        ) from None
    except (SwissEphemerisCalculationError, RuntimeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Deterministic dashboard insights are temporarily unavailable.",
        ) from None
