"""Synthetic, active-release multi-turn consultation acceptance cases."""

from dataclasses import replace
from datetime import UTC, date, datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from astrologer.application.analyze import DeterministicAnalysisService
from astrologer.application.answer import AskJyotAIService
from astrologer.application.consultation import (
    ConsultationError,
    ConsultationRequest,
    ConsultationService,
    ConsultationStore,
)
from astrologer.application.context import DeterministicAstrologyContextService
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.birth.models import BirthInput
from astrologer.composition import DeterministicAnswerComposer
from astrologer.composition.career_claims import ClaimKind
from astrologer.evidence import InterpretationEvidenceBuilder
from astrologer.main import create_app
from astrologer.timing_rules.service import CareerTimingAnalysisService

_BIRTH = BirthInput(
    birth_date="1978-01-01", birth_time="12:00:00", timezone="UTC", latitude=0, longitude=0
)
_AS_OF = datetime(2026, 1, 1, tzinfo=UTC)


@pytest.fixture
def consultation() -> ConsultationService:
    provider = SwissEphemerisProvider()
    ask = AskJyotAIService(
        DeterministicAnalysisService(DeterministicAstrologyContextService(provider)),
        InterpretationEvidenceBuilder(),
        DeterministicAnswerComposer(),
        CareerTimingAnalysisService(provider),
    )
    return ConsultationService(ask, ConsultationStore())


def _request(question: str, consultation_id: str | None = None) -> ConsultationRequest:
    return ConsultationRequest(
        birth_input=_BIRTH, as_of=_AS_OF, question=question, consultation_id=consultation_id
    )


def test_five_consecutive_career_questions_share_one_consultation(
    consultation: ConsultationService,
) -> None:
    questions = (
        "How will my career be in 2027?",
        "Why did you say that?",
        "Which Dasha applies?",
        "What about next year?",
        "Is next year better?",
    )
    responses = []
    for question in questions:
        consultation_id = responses[0].state.consultation_id if responses else None
        responses.append(consultation.respond(_request(question, consultation_id)))

    assert len({response.state.consultation_id for response in responses}) == 1
    assert len({response.state.turn_id for response in responses}) == 5
    assert all(response.analysis is not None or response.reply for response in responses)
    assert responses[3].analysis is not None
    assert responses[3].analysis.routing.intents[0].time_range.start_date.year == 2028
    assert responses[4].status == "unsupported"
    assert "cannot rank" in (responses[4].reply or "")


def test_why_resolves_same_2027_timing_claim(consultation: ConsultationService) -> None:
    first = consultation.respond(_request("How will my career be in 2027?"))
    assert first.analysis is not None
    claim = next(
        item
        for item in first.analysis.answers[0].claim_ledger.claims  # type: ignore[union-attr]
        if item.kind is ClaimKind.APPROVED_TIMING_INTERPRETATION
    )
    reply = consultation.respond(
        _request("Why did you say that about 2027?", first.state.consultation_id)
    )
    assert reply.resolved_claim_ids == (claim.claim_id,)
    assert claim.permitted_wording in (reply.reply or "")
    assert claim.source_reference in reply.source_references
    assert "promotion" in (reply.reply or "")


def test_placement_followup_has_fact_rule_and_source(consultation: ConsultationService) -> None:
    first = consultation.respond(
        _request("What does my tenth-house-lord placement say about career?")
    )
    reply = consultation.respond(
        _request("Which planetary placement supports this?", first.state.consultation_id)
    )
    assert reply.status == "answered"
    assert "tenth-house lord is placed in the fourth house" in (reply.reply or "")
    assert "Approved rule:" in (reply.reply or "")
    assert reply.source_references


def test_dasha_followup_preserves_complete_and_intersected_periods(
    consultation: ConsultationService,
) -> None:
    first = consultation.respond(_request("How will my career be in 2027?"))
    assert first.analysis is not None
    window = first.analysis.answers[0].timing.windows[0]  # type: ignore[union-attr]
    reply = consultation.respond(_request("Which Dasha applies?", first.state.consultation_id))
    assert window.source.dasha_scope in (reply.reply or "")
    assert window.mahadasha_lord is not None
    assert f"{window.mahadasha_lord.title()} Mahadasha" in (reply.reply or "")
    assert window.source_start.isoformat() in (reply.reply or "")
    assert window.effective_start.isoformat() in (reply.reply or "")
    assert "exact date" in (reply.reply or "")


def test_new_year_is_independently_evaluated(consultation: ConsultationService) -> None:
    first = consultation.respond(_request("How will my career be in 2027?"))
    second = consultation.respond(_request("What about 2028?", first.state.consultation_id))
    assert second.analysis is not None
    assert second.analysis.routing.intents[0].time_range.start_date.year == 2028  # type: ignore[union-attr]
    assert second.state.consultation_id == first.state.consultation_id
    assert second.state.turn_id != first.state.turn_id


def test_comparison_is_recognized_without_ranking(consultation: ConsultationService) -> None:
    first = consultation.respond(_request("How will my career be in 2027?"))
    reply = consultation.respond(_request("Is 2028 better than 2027?", first.state.consultation_id))
    assert reply.status == "unsupported"
    assert "2027 and 2028" in (reply.reply or "") or "2028 and 2027" in (reply.reply or "")
    assert "cannot rank" in (reply.reply or "")
    assert "2027:" in (reply.reply or "") and "2028:" in (reply.reply or "")
    assert "These periods do not establish events or relative outcomes" in (reply.reply or "")


def test_profile_switch_blocks_previous_evidence(consultation: ConsultationService) -> None:
    first = consultation.respond(_request("How will my career be in 2027?"))
    changed = _request("Why did you say that?", first.state.consultation_id).model_copy(
        update={"birth_input": _BIRTH.model_copy(update={"birth_date": date(1978, 1, 2)})}
    )
    with pytest.raises(ConsultationError, match="Start a new consultation"):
        consultation.respond(changed)


def test_generic_why_with_static_and_timing_claims_asks_which_claim(
    consultation: ConsultationService,
) -> None:
    first = consultation.respond(_request("How will my career be in 2027?"))
    assert first.analysis is not None
    approved = [
        claim
        for claim in first.analysis.answers[0].claim_ledger.claims  # type: ignore[union-attr]
        if claim.kind
        in {ClaimKind.APPROVED_INTERPRETATION, ClaimKind.APPROVED_TIMING_INTERPRETATION}
    ]
    assert len(approved) > 1
    reply = consultation.respond(_request("Why did you say that?", first.state.consultation_id))
    assert reply.status == "clarification"
    assert not reply.resolved_claim_ids
    assert all(claim.claim_id in (reply.reply or "") for claim in approved[:4])


def test_changed_reference_time_rejects_prior_claims(consultation: ConsultationService) -> None:
    first = consultation.respond(_request("How is my career?"))
    changed = _request("Why did you say that?", first.state.consultation_id).model_copy(
        update={"as_of": datetime(2027, 1, 1, tzinfo=UTC)}
    )
    with pytest.raises(ConsultationError, match="Start a new consultation"):
        consultation.respond(changed)


def test_expired_record_is_evicted_and_cannot_be_continued(
    consultation: ConsultationService,
) -> None:
    first = consultation.respond(_request("How is my career?"))
    store = consultation._store
    record = store.get(first.state.consultation_id)
    store.put(first.state.consultation_id, replace(record, expires_at=0))
    with pytest.raises(ConsultationError, match="Start a new consultation"):
        consultation.respond(_request("Why?", first.state.consultation_id))
    assert first.state.consultation_id not in store._records


def test_stale_concurrent_replacement_cannot_overwrite_new_anchor(
    consultation: ConsultationService,
) -> None:
    first = consultation.respond(_request("How is my career?"))
    store = consultation._store
    original = store.get(first.state.consultation_id)
    updated = replace(original, expires_at=original.expires_at + 1)
    store.replace(first.state.consultation_id, original, updated)
    with pytest.raises(ConsultationError, match="Start a new consultation"):
        store.replace(first.state.consultation_id, original, original)
    assert store.get(first.state.consultation_id) is updated


def test_active_release_change_invalidates_anchor(
    consultation: ConsultationService, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = consultation.respond(_request("How is my career?"))
    monkeypatch.setattr(
        "astrologer.application.consultation._active_release", lambda: ("new-release",)
    )
    with pytest.raises(ConsultationError, match="Start a new consultation"):
        consultation.respond(_request("Why?", first.state.consultation_id))


def test_old_turn_reference_is_rejected_after_new_year_analysis(
    consultation: ConsultationService,
) -> None:
    first = consultation.respond(_request("How will my career be in 2027?"))
    old_claim_id = first.state.claim_ids[0]
    second = consultation.respond(_request("What about 2028?", first.state.consultation_id))
    assert old_claim_id in second.state.claim_ids
    stale = _request("Explain that claim", first.state.consultation_id).model_copy(
        update={"claim_ids": (old_claim_id,), "reference_turn_id": first.state.turn_id}
    )
    with pytest.raises(ConsultationError, match="no longer current"):
        consultation.respond(stale)


@pytest.mark.parametrize("field", ["claim_ids", "evidence_item_ids", "timing_references"])
def test_forged_references_are_rejected(consultation: ConsultationService, field: str) -> None:
    first = consultation.respond(_request("How will my career be in 2027?"))
    forged = _request("Why did you say that?", first.state.consultation_id).model_copy(
        update={field: ("forged-reference",), "reference_turn_id": first.state.turn_id}
    )
    with pytest.raises(ConsultationError, match="not in this consultation"):
        consultation.respond(forged)


@pytest.mark.parametrize("domain", ["marriage", "property"])
def test_unsupported_domain_timing_is_honest(
    consultation: ConsultationService, domain: str
) -> None:
    first = consultation.respond(_request(f"When will {domain} happen in 2027?"))
    assert first.analysis is not None
    assert not first.analysis.selections[0].selected_matched
    reply = consultation.respond(_request("Which Dasha applies?", first.state.consultation_id))
    assert reply.status == "unsupported"
    assert "No approved timing evidence" in (reply.reply or "")


def test_exact_promotion_month_stays_unsupported(consultation: ConsultationService) -> None:
    first = consultation.respond(_request("In which exact month will I get promoted?"))
    assert first.analysis is not None
    timing = first.analysis.answers[0].timing
    assert timing is not None and timing.status == "UNSUPPORTED" and not timing.windows
    reply = consultation.respond(_request("Which Dasha applies?", first.state.consultation_id))
    assert reply.status == "unsupported"
    assert "month or date precision is not supported" in (reply.reply or "")


def test_api_rejects_forged_reference_with_conflict_status() -> None:
    client = TestClient(create_app())
    first = client.post(
        "/api/v1/consultation", json=_request("How is my career?").model_dump(mode="json")
    )
    assert first.status_code == 200
    request = _request("Why did you say that?", first.json()["state"]["consultation_id"])
    forged = request.model_copy(
        update={
            "claim_ids": ("forged-reference",),
            "reference_turn_id": first.json()["state"]["turn_id"],
        }
    )
    response = client.post("/api/v1/consultation", json=forged.model_dump(mode="json"))
    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Previous consultation is no longer available. Start a new consultation."
    )


def test_ambiguous_prior_domain_requests_clarification(
    consultation: ConsultationService,
) -> None:
    first = consultation.respond(_request("What about career and wealth?"))
    assert first.analysis is not None and len(first.analysis.answers) == 2
    reply = consultation.respond(_request("Why did you say that?", first.state.consultation_id))
    assert reply.status == "clarification"
    assert "career, wealth" in (reply.reply or "")


def test_exact_displayed_claim_id_resolves_to_approved_evidence(
    consultation: ConsultationService,
) -> None:
    first = consultation.respond(_request("How is my career?"))
    assert first.analysis is not None
    claim = next(
        item
        for item in first.analysis.answers[0].claim_ledger.claims  # type: ignore[union-attr]
        if item.kind is ClaimKind.APPROVED_INTERPRETATION
    )
    reply = consultation.respond(
        _request(f"Explain claim {claim.claim_id}", first.state.consultation_id)
    )
    assert reply.resolved_claim_ids == (claim.claim_id,)
    assert reply.resolved_evidence_item_ids == claim.evidence_item_ids
    assert claim.source_reference in reply.source_references


@pytest.mark.parametrize(
    "question",
    [
        "What are the limitations?",
        "What can't you conclude?",
        "What does this not establish?",
        "How certain is that interpretation?",
    ],
)
def test_limitations_use_approved_claim_and_wording(
    consultation: ConsultationService, question: str
) -> None:
    first = consultation.respond(_request("What are my career strengths?"))
    assert first.analysis is not None
    answer = first.analysis.answers[0]
    approved = next(
        claim for claim in answer.claim_ledger.claims  # type: ignore[union-attr]
        if claim.kind is ClaimKind.APPROVED_INTERPRETATION
    )
    reply = consultation.respond(_request(question, first.state.consultation_id))
    assert reply.status == "answered"
    assert answer.limitations[0] in (reply.reply or "")
    assert reply.resolved_claim_ids == (approved.claim_id,)
    assert reply.source_references == (approved.source_reference,)
    assert reply.resolved_evidence_item_ids == approved.evidence_item_ids
    assert "1978-01-01" not in reply.model_dump_json()


def test_multiple_approved_claims_require_limitation_selection(
    consultation: ConsultationService,
) -> None:
    first = consultation.respond(_request("How will my career be in 2027?"))
    assert first.analysis is not None
    approved = tuple(
        claim for claim in first.analysis.answers[0].claim_ledger.claims  # type: ignore[union-attr]
        if claim.kind
        in {ClaimKind.APPROVED_INTERPRETATION, ClaimKind.APPROVED_TIMING_INTERPRETATION}
    )
    assert len(approved) > 1
    reply = consultation.respond(_request("What are the limitations?", first.state.consultation_id))
    assert reply.status == "clarification"
    assert not reply.resolved_claim_ids
    assert all(claim.claim_id in (reply.reply or "") for claim in approved)
    selected = consultation.respond(
        _request("What are the limitations?", first.state.consultation_id).model_copy(
            update={"claim_ids": (approved[0].claim_id,), "reference_turn_id": first.state.turn_id}
        )
    )
    assert selected.status == "answered"
    assert selected.resolved_claim_ids == (approved[0].claim_id,)
    answer = first.analysis.answers[0]
    assert answer.timing is not None
    assert answer.limitations[0] in (selected.reply or "")
    assert answer.timing.windows[0].limitations[0] not in (selected.reply or "")
    timing_claim = next(
        claim for claim in approved if claim.kind is ClaimKind.APPROVED_TIMING_INTERPRETATION
    )
    timing_limits = consultation.respond(
        _request("What are the limitations?", first.state.consultation_id).model_copy(
            update={"claim_ids": (timing_claim.claim_id,), "reference_turn_id": first.state.turn_id}
        )
    )
    assert timing_limits.resolved_claim_ids == (timing_claim.claim_id,)
    assert answer.timing.windows[0].limitations[0] in (timing_limits.reply or "")
    assert answer.limitations[0] not in (timing_limits.reply or "")


@pytest.mark.parametrize(
    "question",
    ["What about next year?", "And the following year?", "How about the year after that?"],
)
def test_relative_year_uses_prior_requested_calendar_year(
    consultation: ConsultationService, question: str
) -> None:
    first = consultation.respond(_request("How will my career be in 2027?"))
    reply = consultation.respond(_request(question, first.state.consultation_id))
    assert reply.status == "answered"
    assert reply.analysis is not None
    intent = reply.analysis.routing.intents[0]
    assert intent.time_range is not None
    assert (intent.time_range.start_date.year, intent.time_range.end_date.year) == (2028, 2028)
    assert reply.analysis.answers[0].timing is not None
    assert reply.analysis.answers[0].timing.requested_start_date == date(2028, 1, 1)
    assert reply.state.turn_id != first.state.turn_id
    assert reply.state.consultation_id == first.state.consultation_id


@pytest.mark.parametrize("offset_hours", [-10, 14])
def test_relative_year_uses_anchor_across_local_year_rollover(
    consultation: ConsultationService, offset_hours: int
) -> None:
    local_as_of = datetime(
        2026, 12, 31, 23, 30, tzinfo=timezone(timedelta(hours=offset_hours))
    )
    first_request = _request("How will my career be in 2027?").model_copy(
        update={"as_of": local_as_of}
    )
    first = consultation.respond(first_request)
    follow_request = _request("What about next year?", first.state.consultation_id).model_copy(
        update={"as_of": local_as_of}
    )
    reply = consultation.respond(follow_request)
    assert reply.analysis is not None
    time_range = reply.analysis.routing.intents[0].time_range
    assert time_range is not None
    assert (time_range.start_date, time_range.end_date) == (date(2028, 1, 1), date(2028, 12, 31))


@pytest.mark.parametrize(
    "question",
    [
        "Is next year better?",
        "Will the following year be better?",
        "Is it more favorable than this year?",
    ],
)
def test_relative_comparison_evaluates_both_years_without_ranking(
    consultation: ConsultationService, question: str
) -> None:
    first = consultation.respond(_request("How will my career be in 2027?"))
    reply = consultation.respond(_request(question, first.state.consultation_id))
    assert reply.status == "unsupported"
    assert "cannot rank" in (reply.reply or "")
    assert "2027:" in (reply.reply or "") and "2028:" in (reply.reply or "")
    assert "No approved two-period comparison methodology" in (reply.reply or "")
    assert "These periods do not establish events or relative outcomes" in (reply.reply or "")
    assert (reply.reply or "").count("Approved limits:") == 2


def test_relative_year_rejects_ambiguous_multi_year_anchor(
    consultation: ConsultationService,
) -> None:
    first = consultation.respond(_request("Compare my career in 2027 vs 2028"))
    reply = consultation.respond(_request("What about next year?", first.state.consultation_id))
    assert reply.status == "clarification"
    assert reply.analysis is None
    assert "Which single calendar year" in (reply.reply or "")


def test_relative_year_requires_live_matching_anchor(consultation: ConsultationService) -> None:
    first = consultation.respond(_request("How will my career be in 2027?"))
    store = consultation._store
    record = store.get(first.state.consultation_id)
    store.put(first.state.consultation_id, replace(record, expires_at=0))
    with pytest.raises(ConsultationError, match="Start a new consultation"):
        consultation.respond(_request("What about next year?", first.state.consultation_id))
    fresh = consultation.respond(_request("What about next year?"))
    assert fresh.analysis is not None
    assert not fresh.analysis.routing.intents
    assert not fresh.analysis.answers


def test_relative_year_rejects_changed_profile_and_forged_reference(
    consultation: ConsultationService,
) -> None:
    first = consultation.respond(_request("How will my career be in 2027?"))
    changed = _request("What about next year?", first.state.consultation_id).model_copy(
        update={"birth_input": _BIRTH.model_copy(update={"birth_date": date(1978, 1, 2)})}
    )
    with pytest.raises(ConsultationError, match="Start a new consultation"):
        consultation.respond(changed)
    forged = _request("What about next year?", first.state.consultation_id).model_copy(
        update={"claim_ids": ("forged",), "reference_turn_id": first.state.turn_id}
    )
    with pytest.raises(ConsultationError, match="not in this consultation"):
        consultation.respond(forged)


def test_relative_year_outside_horizon_stays_unsupported(
    consultation: ConsultationService,
) -> None:
    first = consultation.respond(_request("How will my career be in 2070?"))
    reply = consultation.respond(_request("What about next year?", first.state.consultation_id))
    assert reply.analysis is not None
    timing = reply.analysis.answers[0].timing
    assert timing is not None
    assert timing.status == "UNSUPPORTED" and not timing.windows
    assert timing.requested_start_date == date(2071, 1, 1)


def test_relative_year_preserves_no_match(consultation: ConsultationService) -> None:
    birth = _BIRTH.model_copy(update={"birth_date": date(1980, 6, 15)})
    first_request = _request("How will my career be in 2027?").model_copy(
        update={"birth_input": birth}
    )
    first = consultation.respond(first_request)
    follow = _request("What about next year?", first.state.consultation_id).model_copy(
        update={"birth_input": birth}
    )
    reply = consultation.respond(follow)
    assert reply.analysis is not None
    assert reply.analysis.answers[0].timing is not None
    assert reply.analysis.answers[0].timing.status == "NO_MATCH"
