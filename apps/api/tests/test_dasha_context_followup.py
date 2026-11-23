"""NEXT-DASHA-01: the "Which Dasha applies?" follow-up carries the same Dasha context."""

import pytest
from test_dasha_context import _AS_OF, _QUESTION, _RAHU, _REFERENCE, _service
from test_dasha_linkage import blocklisted_terms

from astrologer.application.consultation import (
    ConsultationRequest,
    ConsultationService,
    ConsultationStore,
)
from astrologer.application.dasha_context import DASHA_CONTEXT_FRAMING, dasha_context_section
from astrologer.birth.models import BirthInput


@pytest.mark.parametrize("birth", [_REFERENCE, _RAHU])
def test_which_dasha_follow_up_carries_the_same_dasha_context(birth: BirthInput) -> None:
    consultation = ConsultationService(_service(), ConsultationStore())
    first = consultation.respond(
        ConsultationRequest(birth_input=birth, as_of=_AS_OF, question=_QUESTION)
    )
    assert first.analysis is not None
    initial = [
        s for s in first.analysis.answers[0].consultation_sections if s.kind == "dasha_context"
    ][0]
    reply = consultation.respond(
        ConsultationRequest(
            birth_input=birth,
            as_of=_AS_OF,
            question="Which Dasha applies?",
            consultation_id=first.state.consultation_id,
        )
    )
    assert reply.reply is not None
    assert [s.kind for s in reply.consultation_sections] == ["dasha_context"]
    follow_up = reply.consultation_sections[0]
    # Same calculated linkage facts; the standalone reply also names the 10th lord, which
    # the year answer leaves to its glance (NEXT-UX-SUMMARY).
    plan = first.analysis.answers[0].career_answer_plan
    assert plan is not None
    args = (plan.dasha_linkages, plan.dasha_interpretation, plan.dasha_segments)
    assert follow_up == dasha_context_section(*args)
    assert initial == dasha_context_section(*args, name_tenth_lord=False)
    assert follow_up.fact_sentences[0].text.startswith("Your 10th lord is ")
    assert initial.framing == follow_up.framing
    assert reply.reply.count(follow_up.text) == 1
    assert reply.reply.count(DASHA_CONTEXT_FRAMING) == 1
    assert reply.reply.index("the calculated Vimshottari periods are") < reply.reply.index(
        follow_up.text
    )
    assert blocklisted_terms(follow_up.text) == []
