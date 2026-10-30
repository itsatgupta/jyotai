"""Versioned synthetic regression for the observed live Career consultation."""

import json
from dataclasses import replace
from datetime import datetime
from pathlib import Path

import pytest

from astrologer.application.analyze import DeterministicAnalysisService
from astrologer.application.answer import AskJyotAIService
from astrologer.application.consultation import (
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
from astrologer.timing_rules.service import CareerTimingAnalysisService

FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures" / "live_career_followup_v1.json").read_text()
)


@pytest.fixture
def live_service() -> ConsultationService:
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
        birth_input=BirthInput.model_validate(FIXTURE["synthetic_birth_input"]),
        as_of=datetime.fromisoformat(FIXTURE["as_of"]),
        question=question,
        consultation_id=consultation_id,
    )


def test_live_sequence_separates_natal_claim_timing_limit_and_dasha_facts(
    live_service: ConsultationService,
) -> None:
    initial, why_question, dasha_question = FIXTURE["questions"]
    first = live_service.respond(_request(initial))
    assert first.analysis is not None
    answer = first.analysis.answers[0]
    assert FIXTURE["expected_placement"] in answer.answer
    assert answer.timing is not None and answer.timing.status == FIXTURE["expected_timing_status"]
    ledger = answer.claim_ledger
    assert ledger is not None
    natal = next(c for c in ledger.claims if c.kind is ClaimKind.APPROVED_INTERPRETATION)
    limit = next(c for c in ledger.claims if c.claim_id == "career-timing-status")

    why = live_service.respond(_request(why_question, first.state.consultation_id))
    assert why.status == "clarification"
    assert "fifth-house Career interpretation" in (why.reply or "")
    assert "no reviewed Career timing rule matched 2027" in (why.reply or "")
    assert not why.resolved_claim_ids

    natal_reply = live_service.respond(
        _request("Explain the fifth-house Career interpretation", first.state.consultation_id)
    )
    assert natal_reply.resolved_claim_ids == (natal.claim_id,)
    assert natal.permitted_wording in (natal_reply.reply or "")
    assert natal.source_reference in natal_reply.source_references
    timing_reply = live_service.respond(
        _request("Why no reviewed Career timing rule matched 2027?", first.state.consultation_id)
    )
    assert timing_reply.resolved_claim_ids == (limit.claim_id,)
    assert "No reviewed Career timing window" in (timing_reply.reply or "")

    dasha = live_service.respond(_request(dasha_question, first.state.consultation_id))
    assert dasha.status == "answered"
    assert "calculated Vimshottari periods" in (dasha.reply or "")
    assert "source MD" in (dasha.reply or "") and "source AD" in (dasha.reply or "")
    assert "local overlap" in (dasha.reply or "")
    assert "+05:30" in (dasha.reply or "")
    assert "No reviewed Career timing rule matched 2027" in (dasha.reply or "")
    assert (dasha.reply or "").count("Antardasha: source MD") >= 1
    assert not dasha.resolved_claim_ids
    assert "do not establish a promotion" in (dasha.reply or "")


def test_dasha_transition_in_requested_year_lists_both_source_periods(
    live_service: ConsultationService,
) -> None:
    birth = BirthInput.model_validate(
        {**FIXTURE["synthetic_birth_input"], "birth_date": "1980-05-15"}
    )
    first_request = _request(FIXTURE["questions"][0]).model_copy(update={"birth_input": birth})
    first = live_service.respond(first_request)
    follow_request = _request("Which Dasha applies?", first.state.consultation_id).model_copy(
        update={"birth_input": birth}
    )
    reply = live_service.respond(follow_request)
    assert (reply.reply or "").count("Antardasha: source MD") >= 2
    assert "Jupiter Mahadasha" in (reply.reply or "")
    assert "Saturn Mahadasha" in (reply.reply or "")
    assert "source MD" in (reply.reply or "") and "overlap with 2027" in (reply.reply or "")


def test_missing_dasha_facts_are_not_reported_as_timing_no_match(
    live_service: ConsultationService, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = live_service.respond(_request(FIXTURE["questions"][0]))

    def unavailable(*_args: object) -> None:
        raise ValueError("synthetic unavailable")

    monkeypatch.setattr(live_service._ask, "dasha_timeline", unavailable)
    reply = live_service.respond(_request("Which Dasha applies?", first.state.consultation_id))
    assert reply.status == "unsupported"
    assert "Calculated Dasha facts for 2027 are unavailable" in (reply.reply or "")
    assert "Career timing window" not in (reply.reply or "")


def test_unknown_timing_does_not_become_no_match(live_service: ConsultationService) -> None:
    first = live_service.respond(_request(FIXTURE["questions"][0]))
    record = live_service._store.get(first.state.consultation_id)
    assert record.anchor is not None and record.anchor.answer.timing is not None
    unknown = record.anchor.answer.timing.model_copy(update={"status": "UNKNOWN"})
    changed_answer = record.anchor.answer.model_copy(update={"timing": unknown})
    live_service._store.put(
        first.state.consultation_id,
        replace(record, anchor=replace(record.anchor, answer=changed_answer)),
    )
    reply = live_service.respond(_request("Which Dasha applies?", first.state.consultation_id))
    assert "Career timing could not be evaluated" in (reply.reply or "")
    assert "No reviewed Career timing rule matched" not in (reply.reply or "")


def test_why_explains_single_timing_claim_directly(live_service: ConsultationService) -> None:
    birth = BirthInput.model_validate(
        {**FIXTURE["synthetic_birth_input"], "birth_date": "1980-03-15"}
    )
    first = live_service.respond(
        _request(FIXTURE["questions"][0]).model_copy(update={"birth_input": birth})
    )
    assert first.analysis is not None
    ledger = first.analysis.answers[0].claim_ledger
    assert ledger is not None
    assert not any(c.kind is ClaimKind.APPROVED_INTERPRETATION for c in ledger.claims)
    follow = _request("Why did you say that?", first.state.consultation_id).model_copy(
        update={"birth_input": birth}
    )
    reply = live_service.respond(follow)
    assert reply.status == "unsupported"
    assert reply.resolved_claim_ids == ("career-timing-status",)
