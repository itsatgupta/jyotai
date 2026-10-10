"""Application orchestration for public, governed Ask JyotAI answers."""

import logging
from collections import defaultdict
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
from astrologer.composition.models import (
    CareerTimingContext,
    CareerTimingProvenance,
    CareerTimingWindowDisplay,
)
from astrologer.evidence import InterpretationEvidenceBuilder
from astrologer.evidence.selection_models import EvidenceSelectionResult
from astrologer.questions.models import QuestionDomain
from astrologer.timing_rules import CareerTimingAnalysisService, CareerTimingRequest
from astrologer.timing_rules.models import (
    CareerTimingEvidence,
    CareerTimingResponse,
    MoonVenusCareerTimingEvidence,
    TimingRuleStatus,
)

ASK_TIMING_HORIZON = timedelta(days=365.25 * 40)
_NO_MATCH_MESSAGE = (
    "No reviewed Career timing window is currently established from the active governed "
    "timing corpus."
)
_UNKNOWN_MESSAGE = (
    "Available chart facts were not sufficient to evaluate the reviewed Career timing rule."
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
        for selection in analysis.selections:
            intent = selection.question_intent
            self._logger.info(
                "ask_routing domain=%s requires_timing=%s",
                intent.domain.value,
                str(intent.requires_timing).lower(),
            )
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
        if intent.domain is not QuestionDomain.CAREER:
            self._logger.info(
                "career_timing_complete windows=0 status=absent reason=non_career_domain"
            )
            return answer
        if not intent.requires_timing:
            self._logger.info(
                "career_timing_complete windows=0 status=absent reason=requires_timing_false"
            )
            return answer
        if self._career_timing_service is None:
            self._logger.info(
                "career_timing_complete windows=0 status=absent reason=timing_service_unavailable"
            )
            return answer
        as_of = request.as_of.astimezone(UTC)
        self._logger.info("career_timing_service_invoked")
        try:
            result = self._career_timing_service.analyze(
                CareerTimingRequest(
                    birth_input=request.birth_input,
                    domain="career",
                    as_of=as_of,
                    horizon_end=as_of + ASK_TIMING_HORIZON,
                )
            )
        except (RuntimeError, ValueError):
            self._logger.info(
                "career_timing_complete windows=0 status=absent reason=timing_service_unavailable"
            )
            raise
        _log_timing_rule_summaries(self._logger, result)
        for window in result.windows:
            self._logger.info("career_timing_window precision=%s", window.precision.value)
        if result.windows:
            self._logger.info(
                "career_timing_complete windows=%s status=attached", len(result.windows)
            )
        else:
            reason = (
                "unknown_timing"
                if any(item.status is TimingRuleStatus.UNKNOWN for item in result.evidence)
                else "no_matching_timing"
            )
            self._logger.info("career_timing_complete windows=0 status=absent reason=%s", reason)
        return answer.model_copy(update={"timing": _timing_context(result)})


def _log_timing_rule_summaries(logger: logging.Logger, result: CareerTimingResponse) -> None:
    """Emit one privacy-safe INFO diagnostic per rule, not per evaluated interval.

    A diagnostic summary is MATCH if any interval matches, otherwise UNKNOWN if any interval is
    unknown, and FALSE otherwise. This is logging-only aggregation; response evidence remains
    interval-level and unchanged.
    """
    grouped: dict[str, list[CareerTimingEvidence | MoonVenusCareerTimingEvidence]] = defaultdict(
        list
    )
    for item in result.evidence:
        grouped[item.rule_id].append(item)
    windows_by_rule: dict[str, int] = defaultdict(int)
    for window in result.windows:
        windows_by_rule[window.rule_id] += 1

    for rule_id, evaluations in grouped.items():
        statuses = [item.status for item in evaluations]
        if TimingRuleStatus.MATCH in statuses:
            status = TimingRuleStatus.MATCH
        elif TimingRuleStatus.UNKNOWN in statuses:
            status = TimingRuleStatus.UNKNOWN
        else:
            status = TimingRuleStatus.FALSE
        logger.info(
            "career_timing_rule rule_id=%s status=%s precision=%s evaluations=%s matches=%s "
            "unknown=%s windows=%s",
            rule_id,
            status.value,
            evaluations[0].precision.value,
            len(evaluations),
            statuses.count(TimingRuleStatus.MATCH),
            statuses.count(TimingRuleStatus.UNKNOWN),
            windows_by_rule[rule_id],
        )


def _timing_context(result: CareerTimingResponse) -> CareerTimingContext:
    status: Literal["MATCH", "NO_MATCH", "UNKNOWN"]
    windows = tuple(
        CareerTimingWindowDisplay(
            rule_id=window.rule_id,
            precision=window.precision.value,
            source_start=window.source_interval.start,
            source_end=window.source_interval.end,
            effective_start=window.effective_window.start,
            effective_end=window.effective_window.end,
            why_this_period_applies=window.why_this_period_applies,
            reviewed_statement=window.reviewed_statement,
            limitations=window.limitations,
            source=CareerTimingProvenance(
                source_work=window.source.source_work,
                section=window.source.section,
                verse=window.source.verse,
                chart_scope=window.chart_scope,
                dasha_scope=window.dasha_scope,
                precision=window.precision.value,
            ),
        )
        for window in sorted(
            result.windows,
            key=lambda window: (
                window.effective_window.start,
                window.effective_window.end,
                window.precision.value,
                window.rule_id,
            ),
        )
    )
    if result.timing_answerability_established:
        status = "MATCH"
        message = "Reviewed Career timing context is available for this chart."
    elif any(item.status is TimingRuleStatus.UNKNOWN for item in result.evidence):
        status = "UNKNOWN"
        message = _UNKNOWN_MESSAGE
    else:
        status = "NO_MATCH"
        message = _NO_MATCH_MESSAGE
    legacy_window = (
        windows[0] if len({window.rule_id for window in windows}) == 1 and windows else None
    )
    return CareerTimingContext(
        timing_answerability_established=result.timing_answerability_established,
        status=status,
        timing_release_id=result.timing_release_id,
        timing_release_version=result.timing_release_version,
        windows=windows,
        message=message,
        precision=legacy_window.precision if legacy_window is not None else None,
        reviewed_statement=legacy_window.reviewed_statement if legacy_window is not None else None,
        why_this_period_applies=(
            legacy_window.why_this_period_applies if legacy_window is not None else None
        ),
        limitations=legacy_window.limitations if legacy_window is not None else (),
    )
