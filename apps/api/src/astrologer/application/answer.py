"""Application orchestration for public, governed Ask JyotAI answers."""

import logging
from datetime import UTC, timedelta
from typing import Literal

from astrologer.application.analyze import (
    DeterministicAnalysisRequest,
    DeterministicAnalysisResult,
    DeterministicAnalysisService,
)
from astrologer.application.detailed_answer import DetailedAnswerBuilder
from astrologer.composition import (
    AnswerComposer,
    AnswerCompositionError,
    DetailedComposedAnswer,
    DeterministicAnswerComposer,
    LanguageModelTransportError,
    SeniorAstrologerComposer,
)
from astrologer.composition.models import CareerTimingContext, CareerTimingWindowDisplay
from astrologer.evidence import InterpretationEvidenceBuilder
from astrologer.evidence.selection_models import EvidenceSelectionResult
from astrologer.questions.models import QuestionDomain
from astrologer.timing_rules import CareerTimingAnalysisService, CareerTimingRequest
from astrologer.timing_rules.models import CareerTimingResponse, TimingRuleStatus

ASK_TIMING_HORIZON = timedelta(days=365.25 * 40)
_NO_MATCH_MESSAGE = (
    "No reviewed Career timing window is currently established from the active governed "
    "timing corpus."
)
_UNKNOWN_MESSAGE = (
    "Available chart facts were not sufficient to evaluate the reviewed Career timing rule."
)
_WHY_PERIOD_APPLIES = (
    "Your D1 tenth-house lord is placed in the fourth house, and this period corresponds to "
    "the Vimshottari Mahadasha of that tenth-house lord."
)


class AskJyotAIResult(DeterministicAnalysisResult):
    """Existing analysis response plus validated composed answers, in intent order."""

    answers: tuple[DetailedComposedAnswer, ...] = ()

    @classmethod
    def from_analysis(
        cls, analysis: DeterministicAnalysisResult, answers: tuple[DetailedComposedAnswer, ...]
    ) -> "AskJyotAIResult":
        return cls(
            context=analysis.context,
            routing=analysis.routing,
            evidence_package=analysis.evidence_package,
            selections=analysis.selections,
            answers=answers,
        )


class AskJyotAIService:
    """Compose answers from approved analyzer selections without router-side rule work."""

    def __init__(
        self,
        analysis_service: DeterministicAnalysisService,
        interpretation_evidence_builder: InterpretationEvidenceBuilder,
        answer_composer: AnswerComposer | DeterministicAnswerComposer | SeniorAstrologerComposer,
        career_timing_service: CareerTimingAnalysisService | None = None,
    ) -> None:
        self._analysis_service = analysis_service
        self._interpretation_evidence_builder = interpretation_evidence_builder
        self._answer_composer = answer_composer
        self._detailed_answer_builder = DetailedAnswerBuilder()
        self._career_timing_service = career_timing_service
        self._logger = logging.getLogger(__name__)

    def answer(self, request: DeterministicAnalysisRequest) -> AskJyotAIResult:
        """Run deterministic analysis, then compose only validated evidence contracts."""
        analysis = self._analysis_service.analyze(request)
        answers = tuple(self._answer_one(request, selection) for selection in analysis.selections)
        return AskJyotAIResult.from_analysis(analysis, answers)

    def _answer_one(
        self, request: DeterministicAnalysisRequest, selection: EvidenceSelectionResult
    ) -> DetailedComposedAnswer:
        evidence = self._interpretation_evidence_builder.build(selection)
        deterministic = self._detailed_answer_builder.build(evidence)
        if not isinstance(self._answer_composer, SeniorAstrologerComposer):
            return self._with_timing(request, selection, deterministic)
        if deterministic.corpus_limitation or evidence.relevant_unknown:
            self._logger.info("senior_narrative_composition_skipped reason=corpus_limit_or_unknown")
            return self._with_timing(request, selection, deterministic)
        self._logger.info("senior_narrative_composition_attempted")
        try:
            narrative = self._answer_composer.compose(request.question, deterministic, evidence)
        except (LanguageModelTransportError, AnswerCompositionError) as error:
            self._logger.warning(
                "senior_narrative_composition_fallback category=%s reason_code=%s",
                error.category,
                error.reason_code
                if isinstance(error, AnswerCompositionError)
                else "provider_failed",
            )
            return self._with_timing(request, selection, deterministic)
        if narrative is None:
            self._logger.info("senior_narrative_composition_fallback reason=not_composable")
            return self._with_timing(request, selection, deterministic)
        self._logger.info("senior_narrative_composition_succeeded")
        return self._with_timing(
            request, selection, deterministic.model_copy(update={"narrative": narrative})
        )

    def _with_timing(
        self,
        request: DeterministicAnalysisRequest,
        selection: EvidenceSelectionResult,
        answer: DetailedComposedAnswer,
    ) -> DetailedComposedAnswer:
        intent = selection.question_intent
        if (
            intent.domain is not QuestionDomain.CAREER
            or not intent.requires_timing
            or self._career_timing_service is None
        ):
            return answer
        as_of = request.as_of.astimezone(UTC)
        result = self._career_timing_service.analyze(
            CareerTimingRequest(
                birth_input=request.birth_input,
                domain="career",
                as_of=as_of,
                horizon_end=as_of + ASK_TIMING_HORIZON,
            )
        )
        return answer.model_copy(update={"timing": _timing_context(result)})


def _timing_context(result: CareerTimingResponse) -> CareerTimingContext:
    status: Literal["MATCH", "NO_MATCH", "UNKNOWN"]
    windows = tuple(
        CareerTimingWindowDisplay(
            source_start=window.source_interval.start,
            source_end=window.source_interval.end,
            effective_start=window.effective_window.start,
            effective_end=window.effective_window.end,
        )
        for window in result.windows
    )
    if result.timing_answerability_established:
        status = "MATCH"
        message = "Reviewed Career timing context is available for this chart."
        why_this_period_applies = _WHY_PERIOD_APPLIES
        reviewed_statement = result.reviewed_statement
    elif any(item.status is TimingRuleStatus.UNKNOWN for item in result.evidence):
        status = "UNKNOWN"
        message = _UNKNOWN_MESSAGE
        why_this_period_applies = None
        reviewed_statement = None
    else:
        status = "NO_MATCH"
        message = _NO_MATCH_MESSAGE
        why_this_period_applies = None
        reviewed_statement = None
    return CareerTimingContext(
        timing_answerability_established=result.timing_answerability_established,
        status=status,
        timing_release_id=result.timing_release_id,
        timing_release_version=result.timing_release_version,
        windows=windows,
        reviewed_statement=reviewed_statement,
        why_this_period_applies=why_this_period_applies,
        message=message,
        limitations=result.limitations,
    )
