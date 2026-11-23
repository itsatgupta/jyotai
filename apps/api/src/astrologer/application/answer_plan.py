"""Select Career consultation material from approved claims and calculated chronology."""

from datetime import UTC, date, datetime, time
from typing import Literal

from astrologer.astrology.chart import Chart
from astrologer.astrology.dasha import VimshottariDashaEngine
from astrologer.composition.career_claims import CareerClaimLedger, ClaimKind
from astrologer.composition.models import (
    CareerAnswerPlan,
    CareerTimingContext,
    PlannedDashaSegment,
)
from astrologer.questions.models import CareerQuestionFocus, QuestionIntent, TimeRangeKind


def build_career_answer_plan(
    intent: QuestionIntent,
    ledger: CareerClaimLedger,
    timing: CareerTimingContext | None,
    chart: Chart,
    reference: datetime,
) -> CareerAnswerPlan:
    """Keep computed periods distinct from the reviewed interpretation ledger."""
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
        segments = _year_dasha_segments(chart, scope.start_date.year, reference)
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
    )


def _year_dasha_segments(
    chart: Chart, year: int, reference: datetime
) -> tuple[PlannedDashaSegment, ...]:
    zone = reference.tzinfo
    assert zone is not None  # validated request
    start = datetime.combine(date(year, 1, 1), time.min, tzinfo=zone).astimezone(UTC)
    end = datetime.combine(date(year + 1, 1, 1), time.min, tzinfo=zone).astimezone(UTC)
    try:
        timeline = VimshottariDashaEngine().calculate(chart, end)
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
                    segment_id=f"vimshottari-v1:{major.start.isoformat()}:{minor.start.isoformat()}",
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
