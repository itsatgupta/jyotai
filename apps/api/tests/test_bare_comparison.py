"""Bare year-vs-year questions ("Which is better, 2027 or 2028?") in a consultation.

With a Career turn the question is the Career comparison; with no Career turn the reply is a
short clarifying question with one button per comparison domain (only Career today).  The
stateless router is unchanged.  All births are synthetic (lat/long 0, UTC).
"""

from datetime import UTC, datetime

import pytest
from test_career_answer_wording import _ask

from astrologer.application.consultation import (
    BARE_COMPARISON_CLARIFICATION,
    COMPARISON_DOMAINS,
    ConsultationRequest,
    ConsultationResponse,
    ConsultationService,
    ConsultationStore,
)
from astrologer.birth.models import BirthInput
from astrologer.composition.comparison_guard import ranking_violation
from astrologer.questions.models import QuestionDomain, QuestionRequest, RoutingIssue
from astrologer.questions.router import (
    QuestionIntentRouter,
    bare_year_comparison,
    question_domains,
)

BIRTH = BirthInput(
    birth_date="1978-01-01", birth_time="12:00:00", timezone="UTC", latitude=0, longitude=0
)
AS_OF = datetime(2026, 1, 1, tzinfo=UTC)
BARE = [
    "Which is better, 2027 or 2028?",
    "2027 or 2028?",
    "compare 2027 and 2028",
    "is 2028 better than 2027?",
]


@pytest.fixture
def service() -> ConsultationService:
    return ConsultationService(_ask(), ConsultationStore())


def _request(
    question: str, consultation_id: str | None = None, **extra: object
) -> ConsultationRequest:
    return ConsultationRequest(
        birth_input=BIRTH,
        as_of=AS_OF,
        question=question,
        consultation_id=consultation_id,
        **extra,  # type: ignore[arg-type]
    )


def _comparison_years(response: ConsultationResponse) -> tuple[int, ...] | None:
    if response.career_comparison is not None:
        return response.career_comparison.years
    if response.analysis is not None and response.analysis.answers:
        comparison = response.analysis.answers[0].career_comparison
        return comparison.years if comparison is not None else None
    return None


def _assert_clarification(response: ConsultationResponse) -> None:
    assert response.status == "clarification"
    assert response.reply == BARE_COMPARISON_CLARIFICATION.format(a=2027, b=2028)
    assert response.reply == "Which area should I compare 2027 and 2028 for?"
    assert [(c.label, c.question, c.claim_ids) for c in response.choices] == [
        ("Career", "Compare 2027 and 2028 for my career", ())
    ]
    assert response.career_comparison is None and response.analysis is None
    assert ranking_violation(response.reply) is None


# --- detection -----------------------------------------------------------------------------


@pytest.mark.parametrize("question", BARE)
def test_bare_phrasings_are_detected_in_ascending_year_order(question: str) -> None:
    assert bare_year_comparison(question) == (2027, 2028)


@pytest.mark.parametrize(
    "question",
    [
        "Which is better for my career, 2027 or 2028?",  # names a domain
        "Is 2028 better for my wealth than 2027?",
        "How is 2027?",  # one year
        "Compare 2026, 2027 and 2028",  # three years
        "What happened between 2027 and 2028?",  # a range, not a comparison
        "Does my tenth-house lord differ in 2027 or 2028?",
    ],
)
def test_non_bare_questions_are_not_detected(question: str) -> None:
    assert bare_year_comparison(question) is None


def test_question_domains_follow_the_router() -> None:
    assert question_domains("Compare 2027 and 2028 for my career") == (QuestionDomain.CAREER,)
    assert question_domains("Career") == (QuestionDomain.CAREER,)
    assert question_domains("2027 or 2028?") == ()
    assert COMPARISON_DOMAINS == (QuestionDomain.CAREER,)


@pytest.mark.parametrize("question", BARE)
def test_the_stateless_router_is_unchanged(question: str) -> None:
    result = QuestionIntentRouter().route(
        QuestionRequest(question=question, reference_instant=AS_OF)
    )
    assert result.intents == ()
    assert set(result.issues) <= {
        RoutingIssue.UNSUPPORTED_LANGUAGE,
        RoutingIssue.AMBIGUOUS_DOMAIN,
    }


# --- with a prior Career turn ----------------------------------------------------------------


@pytest.mark.parametrize("question", BARE)
def test_after_a_career_turn_a_bare_question_is_the_career_comparison(
    service: ConsultationService, question: str
) -> None:
    first = service.respond(_request("How is my career in 2027?"))
    reply = service.respond(_request(question, first.state.consultation_id))
    assert reply.career_comparison is not None
    assert reply.career_comparison.years == (2027, 2028)
    assert reply.career_comparison.ranking_status == "unsupported"
    assert reply.reply == reply.career_comparison.text()
    assert "can't rank 2027 against 2028" in (reply.reply or "")
    # Comparison follow-ups keep working.
    why = service.respond(_request("Why?", first.state.consultation_id))
    assert why.reply is not None and "I don't rank 2027 and 2028" in why.reply


# --- with no prior Career turn ---------------------------------------------------------------


@pytest.mark.parametrize("question", BARE)
def test_fresh_bare_question_asks_which_area_and_the_button_compares(
    service: ConsultationService, question: str
) -> None:
    clarify = service.respond(_request(question))
    _assert_clarification(clarify)
    consultation_id = clarify.state.consultation_id
    choice = clarify.choices[0]
    answered = service.respond(_request(choice.question, consultation_id))
    assert _comparison_years(answered) == (2027, 2028)
    why = service.respond(_request("Why?", consultation_id))
    assert why.reply is not None and "I don't rank 2027 and 2028" in why.reply


def test_fresh_clarification_accepts_a_typed_domain(service: ConsultationService) -> None:
    clarify = service.respond(_request("2027 or 2028?"))
    answered = service.respond(_request("Career", clarify.state.consultation_id))
    assert _comparison_years(answered) == (2027, 2028)


def test_fresh_clarification_with_an_unsupported_reply_does_not_compare(
    service: ConsultationService,
) -> None:
    clarify = service.respond(_request("2027 or 2028?"))
    reply = service.respond(_request("Wealth", clarify.state.consultation_id))
    assert _comparison_years(reply) is None
    assert reply.status == "clarification"


def test_bare_question_after_an_unsupported_first_turn_asks_which_area(
    service: ConsultationService,
) -> None:
    first = service.respond(_request("Tell me something nice"))
    assert first.analysis is not None and not first.analysis.answers
    _assert_clarification(service.respond(_request("2027 or 2028?", first.state.consultation_id)))


@pytest.mark.parametrize("question", BARE)
def test_after_a_non_career_turn_a_bare_question_asks_which_area(
    service: ConsultationService, question: str
) -> None:
    first = service.respond(_request("What does my chart say about wealth?"))
    anchor_turn = first.state.turn_id
    clarify = service.respond(_request(question, first.state.consultation_id))
    _assert_clarification(clarify)
    # The web sends the button with the anchor turn reference and no claim ids.
    answered = service.respond(
        _request(
            clarify.choices[0].question,
            first.state.consultation_id,
            reference_turn_id=anchor_turn,
        )
    )
    assert _comparison_years(answered) == (2027, 2028)


def test_a_named_non_career_comparison_still_says_no_method(
    service: ConsultationService,
) -> None:
    first = service.respond(_request("What does my chart say about wealth?"))
    reply = service.respond(
        _request("Is 2028 better for my wealth than 2027?", first.state.consultation_id)
    )
    assert reply.status == "unsupported"
    assert reply.reply == "No approved comparison method is active for this domain."
