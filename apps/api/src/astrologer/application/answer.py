"""Application orchestration for public, governed Ask JyotAI answers."""

import logging
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from typing import Literal

from astrologer.application.analyze import (
    DeterministicAnalysisRequest,
    DeterministicAnalysisResult,
    DeterministicAnalysisService,
)
from astrologer.application.career_claims import answer_career, build_career_ledger
from astrologer.application.detailed_answer import DetailedAnswerBuilder
from astrologer.astrology.intervals import TimeInterval
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
from astrologer.evidence import InterpretationEvidence, InterpretationEvidenceBuilder
from astrologer.evidence.selection_models import EvidenceSelectionResult
from astrologer.questions.models import (
    CareerQuestionFocus,
    QuestionDomain,
    RequestedTimingPrecision,
    ResolvedTimeRange,
    TemporalIntent,
)
from astrologer.timing_rules import CareerTimingAnalysisService, CareerTimingRequest
from astrologer.timing_rules.models import (
    CareerTimingEvidence,
    CareerTimingResponse,
    MoonVenusCareerTimingEvidence,
    NinthLordInTenthCareerTimingEvidence,
    TimingRuleStatus,
)
from astrologer.timing_rules.registry import get_active_timing_release

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
            return self._finish(request, selection, evidence, deterministic)
        if deterministic.corpus_limitation or evidence.relevant_unknown:
            self._logger.info("senior_narrative_composition_skipped reason=corpus_limit_or_unknown")
            return self._finish(request, selection, evidence, deterministic)
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
            return self._finish(request, selection, evidence, deterministic)
        if narrative is None:
            self._logger.info("senior_narrative_composition_fallback reason=not_composable")
            return self._finish(request, selection, evidence, deterministic)
        self._logger.info("senior_narrative_composition_succeeded")
        return self._finish(
            request, selection, evidence, deterministic.model_copy(update={"narrative": narrative})
        )

    def _finish(
        self,
        request: DeterministicAnalysisRequest,
        selection: EvidenceSelectionResult,
        evidence: InterpretationEvidence,
        answer: DetailedComposedAnswer,
    ) -> DetailedComposedAnswer:
        timed = self._with_timing(request, selection, answer)
        if selection.question_intent.domain is not QuestionDomain.CAREER:
            return timed
        ledger = build_career_ledger(evidence, selection.question_intent, timed.timing)
        return answer_career(timed, ledger, selection.question_intent)

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
        if intent.career_focus is CareerQuestionFocus.COMPARISON:
            release = get_active_timing_release()
            return answer.model_copy(
                update={
                    "timing": CareerTimingContext(
                        timing_answerability_established=False,
                        status="UNSUPPORTED",
                        scope="requested_range",
                        requested_start_date=intent.time_range.start_date
                        if intent.time_range
                        else None,
                        requested_end_date=intent.time_range.end_date
                        if intent.time_range
                        else None,
                        timing_release_id=release.release_id,
                        timing_release_version=release.release_version,
                        message=(
                            "Two-period Career comparison is not implemented; "
                            "timing was not evaluated."
                        ),
                    )
                }
            )
        if intent.requested_timing_precision in {
            RequestedTimingPrecision.MONTH,
            RequestedTimingPrecision.EXACT_MONTH,
            RequestedTimingPrecision.EXACT_DATE,
        }:
            release = get_active_timing_release()
            return answer.model_copy(
                update={
                    "timing": CareerTimingContext(
                        timing_answerability_established=False,
                        status="UNSUPPORTED",
                        scope="precision_unsupported",
                        requested_start_date=intent.time_range.start_date
                        if intent.time_range
                        else None,
                        requested_end_date=intent.time_range.end_date
                        if intent.time_range
                        else None,
                        timing_release_id=release.release_id,
                        timing_release_version=release.release_version,
                        message=(
                            "The requested month or date precision is not supported by active "
                            "Career timing rules; timing was not evaluated."
                        ),
                    )
                }
            )
        if self._career_timing_service is None:
            self._logger.info(
                "career_timing_complete windows=0 status=absent reason=timing_service_unavailable"
            )
            return answer
        as_of = request.as_of.astimezone(UTC)
        supported = TimeInterval(start=as_of, end=as_of + ASK_TIMING_HORIZON)
        requested_range = intent.time_range
        if requested_range is not None:
            requested = _calendar_interval(requested_range, request.as_of)
            evaluated = requested.intersection(supported)
        elif intent.temporal_intent is TemporalIntent.HISTORICAL:
            evaluated = None
        else:
            evaluated = supported
        if evaluated is None:
            release = get_active_timing_release()
            return answer.model_copy(
                update={
                    "timing": CareerTimingContext(
                        timing_answerability_established=False,
                        status="UNSUPPORTED",
                        scope="requested_range" if requested_range else "historical_unbounded",
                        requested_start_date=requested_range.start_date
                        if requested_range
                        else None,
                        requested_end_date=requested_range.end_date if requested_range else None,
                        calendar_timezone_offset=request.as_of.strftime("%z")
                        if requested_range
                        else None,
                        timing_release_id=release.release_id,
                        timing_release_version=release.release_version,
                        message=(
                            "The requested period is outside the supported forward Career timing "
                            "horizon; no timing rule was evaluated for it."
                        ),
                    )
                }
            )
        self._logger.info("career_timing_service_invoked")
        try:
            result = self._career_timing_service.analyze(
                CareerTimingRequest(
                    birth_input=request.birth_input,
                    domain="career",
                    as_of=evaluated.start,
                    horizon_end=evaluated.end,
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
        return answer.model_copy(
            update={
                "timing": _timing_context(result).model_copy(
                    update={
                        "scope": "requested_range"
                        if requested_range
                        else "default_40_year_horizon",
                        "requested_start_date": requested_range.start_date
                        if requested_range
                        else None,
                        "requested_end_date": requested_range.end_date if requested_range else None,
                        "calendar_timezone_offset": request.as_of.strftime("%z")
                        if requested_range
                        else None,
                        "evaluated_start": evaluated.start,
                        "evaluated_end": evaluated.end,
                        "partially_supported": requested_range is not None
                        and requested != evaluated,
                    }
                )
            }
        )


def _calendar_interval(time_range: ResolvedTimeRange, reference: datetime) -> TimeInterval:
    """Turn inclusive local calendar dates into a UTC half-open interval."""
    zone = reference.tzinfo
    assert zone is not None  # validated by DeterministicAnalysisRequest
    start = datetime.combine(time_range.start_date, datetime.min.time(), tzinfo=zone)
    if time_range.end_date == date.max:
        # The representable upper bound is far beyond the supported 40-year horizon.
        end_utc = datetime.max.replace(tzinfo=UTC)
    else:
        end = datetime.combine(
            time_range.end_date + timedelta(days=1), datetime.min.time(), tzinfo=zone
        )
        end_utc = end.astimezone(UTC)
    return TimeInterval(start=start.astimezone(UTC), end=end_utc)


def _log_timing_rule_summaries(logger: logging.Logger, result: CareerTimingResponse) -> None:
    """Emit one privacy-safe INFO diagnostic per rule, not per evaluated interval.

    A diagnostic summary is MATCH if any interval matches, otherwise UNKNOWN if any interval is
    unknown, and FALSE otherwise. This is logging-only aggregation; response evidence remains
    interval-level and unchanged.
    """
    grouped: dict[
        str,
        list[
            CareerTimingEvidence
            | MoonVenusCareerTimingEvidence
            | NinthLordInTenthCareerTimingEvidence
        ],
    ] = defaultdict(list)
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
