"""Select Career consultation material from approved claims and calculated chronology."""

from datetime import UTC, date, datetime, time
from typing import Literal

from astrologer.application.career_synthesis import build_career_synthesis
from astrologer.application.dasha_context import build_dasha_context
from astrologer.astrology.chart import Chart
from astrologer.astrology.dasha import VimshottariDashaEngine
from astrologer.composition.career_claims import CareerClaimLedger, ClaimKind
from astrologer.composition.models import (
    CareerAnswerPlan,
    CareerSynthesis,
    CareerTimingContext,
    DashaInterpretationSlot,
    DashaSegmentLinkage,
    PlannedDashaSegment,
)
from astrologer.knowledge.dasha_interpretation import (
    ACTIVE_DASHA_INTERPRETATION_CORPUS,
    DashaInterpretationCorpus,
)
from astrologer.questions.models import CareerQuestionFocus, QuestionIntent, TimeRangeKind


def build_career_answer_plan(
    intent: QuestionIntent,
    ledger: CareerClaimLedger,
    timing: CareerTimingContext | None,
    chart: Chart,
    reference: datetime,
    dasha_engine: VimshottariDashaEngine,
    dasha_corpus: DashaInterpretationCorpus = ACTIVE_DASHA_INTERPRETATION_CORPUS,
) -> CareerAnswerPlan:
    """Keep computed periods distinct from the reviewed interpretation ledger.

    ``dasha_engine`` must be the request's injected engine, so plan segments are cut from the
    same Vimshottari calculation every other path uses.  Each planned segment also receives
    deterministic lord-linkage facts; ``dasha_corpus`` (empty in production) is the only
    source that can fill the Dasha interpretation slot.
    """
    facts = tuple(claim for claim in ledger.claims if claim.kind is ClaimKind.CALCULATED_FACT)
    natal = tuple(
        claim for claim in ledger.claims if claim.kind is ClaimKind.APPROVED_INTERPRETATION
    )
    timed = tuple(
        claim for claim in ledger.claims if claim.kind is ClaimKind.APPROVED_TIMING_INTERPRETATION
    )
    segments: tuple[PlannedDashaSegment, ...] = ()
    scope = intent.time_range
    if (
        intent.career_focus is CareerQuestionFocus.PERIOD
        and scope is not None
        and scope.range_kind is TimeRangeKind.CALENDAR_YEAR
        and scope.start_date.year == scope.end_date.year
    ):
        segments = _year_dasha_segments(chart, scope.start_date.year, reference, dasha_engine)
    linkages: tuple[DashaSegmentLinkage, ...] = ()
    slot: DashaInterpretationSlot | None = None
    synthesis: CareerSynthesis | None = None
    if segments:
        assert scope is not None
        linkages, slot = build_dasha_context(chart, segments, dasha_corpus)
        synthesis = build_career_synthesis(
            scope.start_date.year, (*natal, *timed), chart, linkages, segments, slot
        )
    answerability: Literal[
        "REVIEWED_TIMING_CONTEXT", "NATAL_CONTEXT_ONLY", "FACTS_ONLY", "UNKNOWN", "UNSUPPORTED"
    ]
    if intent.career_focus in {
        CareerQuestionFocus.PROMOTION,
        CareerQuestionFocus.PROFESSION,
        CareerQuestionFocus.COMPARISON,
    } or (timing is not None and timing.status == "UNSUPPORTED"):
        answerability = "UNSUPPORTED"
    elif timing is not None and timing.status == "UNKNOWN":
        answerability = "UNKNOWN"
    elif timed:
        answerability = "REVIEWED_TIMING_CONTEXT"
    elif natal:
        answerability = "NATAL_CONTEXT_ONLY"
    else:
        answerability = "FACTS_ONLY"
    limits: list[str] = []
    if scope is not None:
        limits.append("career-year-outcome-unestablished")
    if timing is not None and timing.status != "MATCH":
        limits.append(f"career-timing-{timing.status.lower()}")
    if natal and scope is not None:
        limits.append("natal-context-is-static")
    if not natal:
        limits.append("no-reviewed-natal-interpretation")
    if not segments and scope is not None and scope.range_kind is TimeRangeKind.CALENDAR_YEAR:
        limits.append("calculated-dasha-unavailable")
    return CareerAnswerPlan(
        question_intent=intent,
        requested_time_scope=scope,
        calculated_fact_ids=tuple(dict.fromkeys(fid for claim in facts for fid in claim.fact_ids)),
        matched_claim_ids=tuple(claim.claim_id for claim in (*natal, *timed)),
        timing_evidence_ids=tuple(
            dict.fromkeys(rule_id for claim in timed for rule_id in claim.rule_ids)
        ),
        timing_references=tuple(
            claim.timing_reference for claim in timed if claim.timing_reference is not None
        ),
        dasha_segments=segments,
        approved_source_locators=tuple(
            dict.fromkeys(claim.source_reference for claim in (*natal, *timed))
        ),
        limitation_ids=tuple(limits),
        answerability=answerability,
        dasha_linkages=linkages,
        dasha_interpretation=slot,
        synthesis=synthesis,
    )


def dasha_segment_id(mahadasha_start: datetime, antardasha_start: datetime) -> str:
    """Stable id for one source MD/AD pair, shared by the plan and the follow-up path."""
    return f"vimshottari-v1:{mahadasha_start.isoformat()}:{antardasha_start.isoformat()}"


def _year_dasha_segments(
    chart: Chart, year: int, reference: datetime, dasha_engine: VimshottariDashaEngine
) -> tuple[PlannedDashaSegment, ...]:
    zone = reference.tzinfo
    assert zone is not None  # validated request
    start = datetime.combine(date(year, 1, 1), time.min, tzinfo=zone).astimezone(UTC)
    end = datetime.combine(date(year + 1, 1, 1), time.min, tzinfo=zone).astimezone(UTC)
    try:
        timeline = dasha_engine.calculate(chart, end)
    except ValueError:
        return ()
    segments = []
    for major in timeline.mahadashas:
        for minor in major.antardashas:
            effective_start = max(start, major.start, minor.start)
            effective_end = min(end, major.end, minor.end)
            if effective_start >= effective_end:
                continue
            segments.append(
                PlannedDashaSegment(
                    segment_id=dasha_segment_id(major.start, minor.start),
                    mahadasha_lord=major.lord.value,
                    antardasha_lord=minor.lord.value,
                    mahadasha_start=major.start,
                    mahadasha_end=major.end,
                    antardasha_start=minor.start,
                    antardasha_end=minor.end,
                    effective_start=effective_start,
                    effective_end=effective_end,
                    local_start=effective_start.astimezone(zone),
                    local_end=effective_end.astimezone(zone),
                )
            )
    return tuple(segments)
