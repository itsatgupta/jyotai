"""Stateless deterministic analysis endpoint for the first browser vertical slice."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from astrologer.application.analyze import (
    DeterministicAnalysisRequest,
    DeterministicAnalysisService,
)
from astrologer.application.answer import AskJyotAIResult, AskJyotAIService
from astrologer.application.context import (
    DeterministicAstrologyContextService,
    DeterministicContextInputError,
)
from astrologer.astrology.swiss_ephemeris import (
    SwissEphemerisCalculationError,
    SwissEphemerisProvider,
)
from astrologer.common.config import Settings
from astrologer.composition import (
    AnswerComposer,
    AnswerCompositionError,
    LanguageModelTransportError,
    OpenAICompatibleTransport,
)
from astrologer.evidence import InterpretationEvidenceBuilder, InterpretationEvidenceBuildError

router = APIRouter(prefix="/api/v1", tags=["analysis"])
logger = logging.getLogger(__name__)


def get_analysis_service() -> DeterministicAnalysisService:
    """Construct the approved service graph once per stateless request."""
    provider = SwissEphemerisProvider()
    return DeterministicAnalysisService(DeterministicAstrologyContextService(provider))


def get_ask_jyotai_service(request: Request) -> AskJyotAIService:
    """Build the public composition graph using app-owned configuration."""
    settings: Settings = request.app.state.settings
    transport = OpenAICompatibleTransport(
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        provider_id=settings.llm_provider,
        api_key=settings.llm_api_key,
        timeout_seconds=settings.llm_timeout_seconds,
    )
    return AskJyotAIService(
        get_analysis_service(), InterpretationEvidenceBuilder(), AnswerComposer(transport)
    )


@router.post("/analyze", response_model=AskJyotAIResult)
async def analyze(
    request: DeterministicAnalysisRequest,
    service: Annotated[AskJyotAIService, Depends(get_ask_jyotai_service)],
) -> AskJyotAIResult:
    """Return deterministic analysis plus only validated governed compositions."""
    try:
        return service.answer(request)
    except DeterministicContextInputError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error
    except (LanguageModelTransportError, AnswerCompositionError) as error:
        logger.warning(
            "governed_answer_composition_failure exception_type=%s category=%s "
            "provider_id=%s model_id=%s http_status_code=%s",
            type(error).__name__,
            error.category,
            error.provider_id or "unknown",
            error.model_id or "unknown",
            error.http_status_code if isinstance(error, LanguageModelTransportError) else "none",
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Governed answer composition is temporarily unavailable.",
        ) from error
    except InterpretationEvidenceBuildError as error:
        logger.warning(
            "governed_answer_composition_failure "
            "exception_type=InterpretationEvidenceBuildError "
            "category=interpretation_evidence_build provider_id=unknown "
            "model_id=unknown http_status_code=none"
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Governed answer composition is temporarily unavailable.",
        ) from error
    except (SwissEphemerisCalculationError, RuntimeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Deterministic analysis is temporarily unavailable.",
        ) from error
