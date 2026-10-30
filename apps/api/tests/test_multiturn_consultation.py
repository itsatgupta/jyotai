"""Synthetic, active-release multi-turn consultation acceptance cases."""

from dataclasses import replace
from datetime import UTC, date, datetime

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
