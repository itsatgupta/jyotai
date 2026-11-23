"""Career consultation acceptance cases against synthetic test profiles."""

import json
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from astrologer.application.analyze import (
    DeterministicAnalysisRequest,
    DeterministicAnalysisService,
)
from astrologer.application.answer import AskJyotAIService
from astrologer.application.context import DeterministicAstrologyContextService
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.birth.models import BirthInput
from astrologer.composition import DeterministicAnswerComposer
from astrologer.composition.career_claims import ClaimKind, ClaimStatus
from astrologer.evidence import InterpretationEvidenceBuilder
from astrologer.knowledge import ACTIVE_PRODUCTION_RELEASE
from astrologer.questions.models import CareerQuestionFocus, QuestionShape, RequestedTimingPrecision
from astrologer.timing_rules.registry import get_active_timing_release
from astrologer.timing_rules.service import CareerTimingAnalysisService

_BIRTH = BirthInput(
    birth_date="1978-01-01", birth_time="12:00:00", timezone="UTC", latitude=0, longitude=0
)
_AS_OF = datetime(2026, 1, 1, tzinfo=UTC)


def _ask(question: str, as_of: datetime = _AS_OF):
    provider = SwissEphemerisProvider()
    service = AskJyotAIService(
        DeterministicAnalysisService(DeterministicAstrologyContextService(provider)),
        InterpretationEvidenceBuilder(),
        DeterministicAnswerComposer(),
        CareerTimingAnalysisService(provider),
    )
    return service.answer(
        DeterministicAnalysisRequest(birth_input=_BIRTH, as_of=as_of, question=question)
    )


@pytest.mark.parametrize(
    ("question", "focus", "expected"),
    [
        ("What are my career strengths?", CareerQuestionFocus.STRENGTHS, "does not rank"),
        (
            "How will my career develop?",
            CareerQuestionFocus.DEVELOPMENT,
            "future career trajectory",
        ),
        (
            "How will my career be in 2027?",
            CareerQuestionFocus.PERIOD,
            "does not establish a specific Career outcome for 2027",
        ),
        (
            "In which exact month will I get promoted?",
            CareerQuestionFocus.PROMOTION,
            "exact-month promotion methodology",
        ),
    ],
)
def test_four_question_specific_answers(
    question: str, focus: CareerQuestionFocus, expected: str
) -> None:
    result = _ask(question)
    assert result.routing.status.value == "routable"
    intent = result.routing.intents[0]
    assert intent.career_focus is focus
    answer = result.answers[0]
    assert "Your D1 tenth-house lord is placed in the fourth house." in answer.answer
    assert expected in answer.answer
    assert answer.claim_ledger is not None
    assert answer.claim_ledger.requested_question_shape is focus
    assert "Timing is not established by the current governed evidence" not in answer.answer
    assert "D9" not in answer.answer and "D10" not in answer.answer
    if focus in {CareerQuestionFocus.STRENGTHS, CareerQuestionFocus.DEVELOPMENT}:
        assert "knowledge, comfort, courage" in answer.answer
        assert answer.timing is None
        assert "strongest" not in answer.answer.lower()
    elif focus is CareerQuestionFocus.PERIOD:
        assert answer.timing is not None and answer.timing.status == "MATCH"
        assert answer.timing_answered is True
        assert answer.answer.startswith("For 2027, the available reviewed natal Career context")
        assert "Calculated Vimshottari periods in 2027" in answer.answer
        assert "Reviewed Career timing context: broad period Jan 1–Dec 31" in answer.answer
        assert "promotion will" not in answer.answer
    else:
        assert intent.shape is QuestionShape.TIMING
        assert intent.requested_timing_precision is RequestedTimingPrecision.EXACT_MONTH
        assert answer.timing_answered is False
        assert "cannot identify a promotion month" in answer.answer


def test_every_substantive_career_claim_resolves_to_active_evidence() -> None:
    result = _ask("How will my career be in 2027?")
    answer = result.answers[0]
    assert answer.claim_ledger is not None and answer.timing is not None
    selected = {item.evidence_item_id: item for item in result.selections[0].selected_matched}
    static_rules = {rule.rule_id for rule in ACTIVE_PRODUCTION_RELEASE.manifest.rules}
    timing_rules = {rule.rule_id for rule in get_active_timing_release().rules}
    for claim in answer.claim_ledger.claims:
        assert claim.source_reference
        if claim.kind is ClaimKind.APPROVED_INTERPRETATION:
            assert claim.evaluation_status is ClaimStatus.MATCH
            assert claim.evidence_item_ids[0] in selected
            assert claim.rule_ids[0] in static_rules
            assert (
                claim.permitted_wording in answer.answer
                or claim.permitted_wording in answer.reviewed_interpretations
            )
        if claim.kind is ClaimKind.APPROVED_TIMING_INTERPRETATION:
            assert claim.rule_ids[0] in timing_rules
            assert claim.permitted_wording in answer.answer
            assert claim.timing_reference and claim.authorized_precision
            assert any(window.rule_id == claim.rule_ids[0] for window in answer.timing.windows)
    assert not any(
        claim.kind is ClaimKind.UNSUPPORTED_REQUEST for claim in answer.claim_ledger.claims
    )


def test_two_year_comparison_preserves_both_years_and_does_not_synthesize() -> None:
    result = _ask("Compare my career in 2027 vs 2028")
    intent = result.routing.intents[0]
    assert intent.comparison_years == (2027, 2028)
    assert intent.time_range is not None
    assert (intent.time_range.start_date.year, intent.time_range.end_date.year) == (2027, 2028)
    answer = result.answers[0]
    assert "2027 and 2028" in answer.answer
    assert "requested comparison was not evaluated" in answer.answer
    assert answer.timing is not None and answer.timing.status == "UNSUPPORTED"
    assert answer.claim_ledger is not None
    assert not any(
        claim.kind is ClaimKind.APPROVED_TIMING_INTERPRETATION
        for claim in answer.claim_ledger.claims
    )
    plain = _ask("How will my career be in 2027 and 2028?")
    assert plain.routing.intents[0].comparison_years == (2027, 2028)
    assert "requested comparison was not evaluated" in plain.answers[0].answer


def test_unsupported_profession_and_requested_precision_are_explicit() -> None:
    profession = _ask("Which profession should I choose?").answers[0]
    assert "No approved Career rule identifies a profession" in profession.answer
    assert profession.claim_ledger is not None
    assert any(
        claim.kind is ClaimKind.UNSUPPORTED_REQUEST for claim in profession.claim_ledger.claims
    )

    month = _ask("Which exact month will my career change?").answers[0]
    assert "requested timing precision is unsupported" in month.answer.lower()
    assert month.timing is not None and month.timing.status == "UNSUPPORTED"
    assert month.timing.scope == "precision_unsupported"
    assert not month.timing.windows
    assert month.timing_answered is False
    assert "overlaps the requested period" not in month.answer
    assert month.claim_ledger is not None
    assert any(claim.kind is ClaimKind.UNSUPPORTED_REQUEST for claim in month.claim_ledger.claims)


def test_2027_window_is_the_authorized_utc_half_open_intersection_at_both_as_of_dates() -> None:
    for as_of in (datetime(2026, 1, 1, tzinfo=UTC), datetime(2026, 10, 29, tzinfo=UTC)):
        result = _ask("How will my career be in 2027?", as_of)
        assert result.context.normalized_as_of_utc == as_of
        answer = result.answers[0]
        assert answer.timing is not None and answer.timing.status == "MATCH"
        assert answer.timing_answered is True
        assert answer.timing.evaluated_start == datetime(2027, 1, 1, tzinfo=UTC)
        assert answer.timing.evaluated_end == datetime(2028, 1, 1, tzinfo=UTC)
        for window in answer.timing.windows:
            assert window.effective_start == max(window.source_start, answer.timing.evaluated_start)
            assert window.effective_end == min(window.source_end, answer.timing.evaluated_end)
            assert window.effective_start < window.effective_end
        assert "promotion will" not in answer.answer
        assert "income will" not in answer.answer


def test_timing_no_match_is_distinct_from_static_rule_nonmatches() -> None:
    birth = BirthInput(
        birth_date="1980-06-15",
        birth_time="12:00:00",
        timezone="UTC",
        latitude=0,
        longitude=0,
    )
    provider = SwissEphemerisProvider()
    service = AskJyotAIService(
        DeterministicAnalysisService(DeterministicAstrologyContextService(provider)),
        InterpretationEvidenceBuilder(),
        DeterministicAnswerComposer(),
        CareerTimingAnalysisService(provider),
    )
    result = service.answer(
        DeterministicAnalysisRequest(
            birth_input=birth,
            as_of=_AS_OF,
            question="How will my career be in 2027?",
        )
    )
    answer = result.answers[0]
    assert answer.timing is not None and answer.timing.status == "NO_MATCH"
    assert answer.claim_ledger is not None
    assert any(
        claim.claim_id == "career-timing-status" and claim.evaluation_status is ClaimStatus.NO_MATCH
        for claim in answer.claim_ledger.claims
    )
    assert "No reviewed Career timing rule matched" in answer.answer
    plan = answer.career_answer_plan
    assert plan is not None and plan.answerability == "NATAL_CONTEXT_ONLY"
    assert plan.dasha_segments
    assert plan.timing_evidence_ids == ()
    assert answer.consultation_sections[0].kind == "direct"
    assert "reviewed natal Career context" in answer.consultation_sections[0].text
    assert answer.consultation_sections[-1].text == (
        "The available reviewed timing evidence does not establish a specific "
        "Career outcome for 2027."
    )


def test_year_plan_links_claims_sources_and_calculated_transition() -> None:
    result = _ask(
        "How will my career be in 2027?", datetime(2026, 1, 1, tzinfo=ZoneInfo("Asia/Kolkata"))
    )
    answer = result.answers[0]
    plan = answer.career_answer_plan
    assert plan is not None and answer.claim_ledger is not None
    approved = {
        claim.claim_id: claim
        for claim in answer.claim_ledger.claims
        if claim.kind
        in {ClaimKind.APPROVED_INTERPRETATION, ClaimKind.APPROVED_TIMING_INTERPRETATION}
    }
    assert set(plan.matched_claim_ids) == set(approved)
    assert set(plan.approved_source_locators) == {
        claim.source_reference for claim in approved.values()
    }
    assert plan.timing_evidence_ids == tuple(
        rule_id
        for claim in approved.values()
        if claim.kind is ClaimKind.APPROVED_TIMING_INTERPRETATION
        for rule_id in claim.rule_ids
    )
    assert plan.timing_references == tuple(
        claim.timing_reference
        for claim in approved.values()
        if claim.kind is ClaimKind.APPROVED_TIMING_INTERPRETATION
    )
    assert len(plan.dasha_segments) == 2
    first, second = plan.dasha_segments
    assert first.effective_end == second.effective_start
    assert first.local_end == second.local_start
    assert first.mahadasha_lord == second.mahadasha_lord
    assert first.antardasha_lord != second.antardasha_lord
    assert (
        first.effective_start.astimezone(ZoneInfo("Asia/Kolkata")).date().isoformat()
        == "2027-01-01"
    )
    assert (
        second.effective_end.astimezone(ZoneInfo("Asia/Kolkata")).date().isoformat() == "2028-01-01"
    )
    assert answer.answer.count("Calculated Vimshottari periods in 2027") == 1
    assert "career-year-outcome-unestablished" in plan.limitation_ids
    assert all(claim.permitted_wording in answer.answer for claim in approved.values())


def test_no_natal_match_and_month_promotion_keep_honest_answerability() -> None:
    fixture = json.loads(
        (Path(__file__).parent / "fixtures" / "consultation_quality_v1.json").read_text()
    )
    other = BirthInput.model_validate(fixture["profiles"]["P_OTHER"])
    provider = SwissEphemerisProvider()
    service = AskJyotAIService(
        DeterministicAnalysisService(DeterministicAstrologyContextService(provider)),
        InterpretationEvidenceBuilder(),
        DeterministicAnswerComposer(),
        CareerTimingAnalysisService(provider),
    )
    year = service.answer(
        DeterministicAnalysisRequest(
            birth_input=other, as_of=_AS_OF, question="How is my career in 2027?"
        )
    ).answers[0]
    assert year.career_answer_plan is not None
    assert year.career_answer_plan.answerability == "FACTS_ONLY"
    assert year.career_answer_plan.calculated_fact_ids
    assert not year.career_answer_plan.matched_claim_ids
    assert "No reviewed natal Career interpretation matched" in year.answer
    assert "does not establish a specific Career outcome for 2027" in year.answer

    promotion = _ask("Will I get promoted in March 2027?").answers[0]
    assert promotion.career_answer_plan is not None
    assert promotion.career_answer_plan.answerability == "UNSUPPORTED"
    assert promotion.timing_answered is False
    assert promotion.timing is not None and promotion.timing.status == "UNSUPPORTED"
    assert not promotion.timing.windows
    assert "will get promoted" not in promotion.answer.lower()


def test_tenth_house_lord_question_uses_only_reviewed_placement_meaning() -> None:
    result = _ask("What does my tenth-house lord mean?")
    assert result.routing.intents[0].career_focus is CareerQuestionFocus.PLACEMENT
    answer = result.answers[0]
    assert answer.timing is None
    assert answer.claim_ledger is not None
    reviewed = [
        claim
        for claim in answer.claim_ledger.claims
        if claim.kind is ClaimKind.APPROVED_INTERPRETATION
    ]
    assert len(reviewed) == 1
    assert reviewed[0].permitted_wording in answer.answer
    assert "promotion will" not in answer.answer.lower()
