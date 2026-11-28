"""NEXT-CHILDREN-GUARD-01: hard guards for child-sex, medical and childlessness wording.

Owner decision (a product decision, not legal advice): JyotAI never predicts or hints at the
sex of a child, in any wording; fertility, pregnancy, miscarriage, IVF, "will I have children
at all" and counts are out of scope; पुत्र is shown with the gloss "children (the text says
'son')".  All births are synthetic (lat/long 0, UTC); none describes a real person.
"""

from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient
from test_career_answer_wording import _ask, _birth
from test_evaluative_guard import (
    _career_request,
    _EvaluativeTransport,
    _matched_career_detailed,
    _senior_client,
)
from test_provisional_tier import _CONTRACT, _SOURCE, _reviews

from astrologer.application.analyze import DeterministicAnalysisRequest
from astrologer.application.children import (
    CHILD_SCOPE_REPLIES,
    CHILD_SEX_REPLY,
    child_clean_answer,
    child_clean_sections,
)
from astrologer.application.detailed_answer import DetailedAnswerBuilder
from astrologer.application.domain_pipeline import _clean
from astrologer.application.domains import domain_config
from astrologer.application.provisional import (
    provisional_interpretations,
    provisional_signification_items,
)
from astrologer.common.config import Settings
from astrologer.composition import AnswerCompositionError, SeniorAstrologerComposer
from astrologer.composition.children_guard import (
    CHILD_HELD_NOTICE,
    CHILD_TERMS,
    PUTRA_CONVENTION,
    PUTRA_GLOSS,
    SOURCE_HELD_NOTICE,
    SUTA,
    child_loss_violation,
    child_sex_violation,
    child_wording_violation,
    source_child_clause,
)
from astrologer.composition.models import ConsultationSection
from astrologer.knowledge import ACTIVE_PRODUCTION_RELEASE
from astrologer.knowledge.admission import AdmissionError
from astrologer.knowledge.models import ReviewStatus
from astrologer.knowledge.provisional import (
    HELD_STATEMENT,
    ProvisionalRule,
    promote_to_reviewed,
    reviewed_rule_id,
)
from astrologer.knowledge.provisional_pack_v1 import (
    RULE_5_IN_4_EDUCATION,
    RULE_5_IN_7_SPIRITUALITY,
    RULE_7_IN_5_WEALTH,
)
from astrologer.knowledge.provisional_pack_v3 import (
    RULE_2_IN_1_WEALTH,
    RULE_2_IN_2_WEALTH,
    RULE_2_IN_5_WEALTH,
    RULE_2_IN_10_WEALTH,
    RULE_2_IN_12_WEALTH,
)
from astrologer.knowledge.provisional_pack_v4 import PROVISIONAL_CORPUS_V4
from astrologer.knowledge.provisional_pack_v5 import (
    ACTIVE_PROVISIONAL_CORPUS,
    CHILDREN_GUARD_REVISIONS,
    NOT_DRAFTED,
    PROVISIONAL_CORPUS_V5,
    REVIEWER_QUESTIONS,
    RULE_2_IN_5_WEALTH_V2,
    SUTA_CONVENTION_REVISIONS,
)
from astrologer.knowledge.provisional_signification import (
    ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS,
    CHILDREN_GUARD_SIGNIFICATION_REVISIONS,
    MARS_KARAKA_LAND,
    PROVISIONAL_SIGNIFICATION_CORPUS_V3,
    ProvisionalSignificationCorpus,
)
from astrologer.knowledge.review_pack import build_markdown
from astrologer.main import create_app
from astrologer.questions import QuestionIntentRouter, QuestionRequest, RoutingStatus
from astrologer.questions.children_scope import ChildQuestionScope, child_question_scope
from astrologer.questions.models import QuestionDomain

_AS_OF = datetime(2026, 1, 1, tzinfo=UTC)
FIFTH_IN_11 = _birth("1960-01-01", "12:00:00")  # reviewed Children rule: 5th lord in the 11th
SECOND_IN_5 = _birth("1978-01-01", "12:00:00")  # provisional Wealth v.12: 2nd lord in the 5th

CHILD_SEX = [
    "Will I have a son?",
    "Boy or girl?",
    "girl or boy",
    "When will I have a baby boy?",
    "Will my wife have a son or a daughter?",
    "How is my career in 2027, and will I have a son?",
    "What is the gender of my baby?",
    "baby's sex?",
    "Is my pregnancy a boy?",
    "Will it be a girl?",
    "Will my first child be a son?",
    "Chances of a son in my chart?",
    "What are the odds of a baby girl?",
    "Son likely in 2027?",
    "Is a male child indicated?",
    "Am I expecting a boy?",
    "Will I get a daughter?",
    "How many sons will I have?",
    "Will my wealth come through a son?",
    "Will any daughter be born to me?",
    "When will my son be born?",
    "putra yog hai kya?",
    "putra prapti kab hogi",
    "beta hoga ya beti?",
    "ladka kab hoga",
    "kitne bete honge?",
    "मुझे बेटा होगा?",
    "पुत्र प्राप्ति कब होगी",
    "लड़का या लड़की?",
]
MEDICAL = [
    "Will I get pregnant?",
    "When will I conceive?",
    "Will IVF work for me?",
    "Am I fertile?",
    "Will I have a miscarriage?",
    "Will I lose the baby?",
    "garbh kab theharega?",
    "गर्भधारण कब होगा?",
]
WHETHER_OR_COUNT = [
    "Will I have children?",
    "Will I ever have a child?",
    "Can we have kids?",
    "Am I able to have children?",
    "Will I have two children?",
    "Is there any chance of children?",
    "How many children will I have?",
    "Will I be childless?",
    "Do I have children yoga?",
    "Will we ever have children, and when?",
    "santan hogi?",
    "kitne bachche honge?",
    "संतान होगी?",
]
ANSWERED = [
    "What does my chart say about children?",
    "What does my 5th house say about children?",
    "When will I have children?",
    "Will my children be successful?",
    "Will my son do well in exams?",
    "When will my daughter marry?",
    "How is my daughter's career?",
    "Will I have a boyfriend?",
    "Will I get a girlfriend?",
    "Will I marry a girl from Delhi?",
    "How is my career in 2027?",
    "Will my income grow?",
    "Who is the reason for my success?",
    "Is the beta toggle on?",
    "Tell me about the Brahmaputra",
]


# --- The question scope (language only) --------------------------------------------------------


@pytest.mark.parametrize("question", CHILD_SEX)
def test_child_sex_questions_in_any_wording(question: str) -> None:
    assert child_question_scope(question) is ChildQuestionScope.CHILD_SEX


@pytest.mark.parametrize("question", MEDICAL)
def test_fertility_and_pregnancy_questions(question: str) -> None:
    assert child_question_scope(question) is ChildQuestionScope.MEDICAL


@pytest.mark.parametrize("question", WHETHER_OR_COUNT)
def test_whether_and_how_many_children_questions(question: str) -> None:
    assert child_question_scope(question) is ChildQuestionScope.WHETHER_OR_COUNT


@pytest.mark.parametrize("question", ANSWERED)
def test_other_questions_keep_their_answer(question: str) -> None:
    assert child_question_scope(question) is None


def test_child_sex_takes_precedence_over_medical_and_count() -> None:
    assert (
        child_question_scope("Will my IVF give me a boy or girl?") is ChildQuestionScope.CHILD_SEX
    )
    assert child_question_scope("How many daughters will I have?") is ChildQuestionScope.CHILD_SEX


def test_the_replies_are_one_line_and_pass_every_guard() -> None:
    assert CHILD_SEX_REPLY == "JyotAI does not predict a child's sex."
    assert set(CHILD_SCOPE_REPLIES) == set(ChildQuestionScope)
    for reply in CHILD_SCOPE_REPLIES.values():
        assert "\n" not in reply and reply.count(".") == 1
        assert child_wording_violation(reply) is None
    for scope in (ChildQuestionScope.MEDICAL, ChildQuestionScope.WHETHER_OR_COUNT):
        assert CHILD_SCOPE_REPLIES[scope].endswith(
            "out of scope for JyotAI; for medical matters, please consult a doctor."
        )


@pytest.mark.parametrize(
    "question", [*CHILD_SEX[:6], MEDICAL[0], WHETHER_OR_COUNT[0], "Boy or girl?"]
)
def test_router_sends_a_guarded_question_to_children_only(question: str) -> None:
    result = QuestionIntentRouter().route(
        QuestionRequest(question=question, reference_instant=_AS_OF)
    )
    assert result.status is RoutingStatus.ROUTABLE
    assert [intent.domain for intent in result.intents] == [QuestionDomain.CHILDREN]


# --- The output wording guards ------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "The text describes wealth through a son.",
        "A daughter is indicated.",
        "Your chart favours boys.",
        "A male child is possible.",
        "beta hoga",
        "बेटा",
        "पुत्रतो धनवान्",  # पुत्र without its gloss
    ],
)
def test_child_sex_wording_is_barred(text: str) -> None:
    assert child_sex_violation(text) is not None


@pytest.mark.parametrize(
    "text",
    [
        "You may remain childless.",
        "The verse says without children.",
        "This indicates no children.",
        "It warns of the loss of a child.",
        "a miscarriage",
        "You will never have children.",
        "barren",
        "पुत्रहीन",
        "सुतहीन",
    ],
)
def test_childlessness_and_loss_wording_is_barred(text: str) -> None:
    assert child_loss_violation(text) is not None


def test_the_putra_gloss_is_the_only_allowed_son() -> None:
    glossed = f"The text describes wealth through {PUTRA_GLOSS}: पुत्रतो धनवान्."
    assert child_wording_violation(glossed) is None
    assert child_sex_violation(f"{glossed} It also says son.") == "son"
    assert child_wording_violation(PUTRA_CONVENTION) is None
    # Quoted source text is removed first, as in the other wording guards.
    assert child_wording_violation("Quoted: पुत्रहीनः प्रजायते.", quoted=("पुत्रहीनः",)) is None


@pytest.mark.parametrize(
    "text",
    [
        "This evidence does not establish the number of children, a specific outcome, "
        "certainty, or timing.",
        "Your D1 fifth-house lord is placed in the eleventh house.",
        "A person with reason and season.",
        "The verses address a male native.",
    ],
)
def test_neutral_text_passes(text: str) -> None:
    assert child_wording_violation(text) is None


def test_every_reviewed_statement_passes() -> None:
    for interpretation in ACTIVE_PRODUCTION_RELEASE.registry.interpretations:
        assert child_wording_violation(interpretation.statement) is None, (
            interpretation.interpretation_id
        )


# --- Answers ------------------------------------------------------------------------------------


def _answer(birth: object, question: str) -> Any:
    result = _ask().answer(
        DeterministicAnalysisRequest(  # type: ignore[arg-type]
            birth_input=birth, as_of=_AS_OF, question=question, include_provisional=True
        )
    )
    return result


@pytest.mark.parametrize(
    ("question", "scope"),
    [
        ("Will I have a son?", ChildQuestionScope.CHILD_SEX),
        ("Will I get pregnant?", ChildQuestionScope.MEDICAL),
        ("How many children will I have?", ChildQuestionScope.WHETHER_OR_COUNT),
    ],
)
def test_the_answer_is_one_line_without_evidence(question: str, scope: ChildQuestionScope) -> None:
    result = _answer(FIFTH_IN_11, question)
    # The chart does match a reviewed Children rule; none of it is shown.
    assert result.selections[0].selected_matched
    (answer,) = result.answers
    assert answer.answer == CHILD_SCOPE_REPLIES[scope]
    assert [section.kind for section in answer.consultation_sections] == ["direct"]
    assert answer.evidence == () and answer.reviewed_interpretations == ()
    assert answer.why_it_applies == () and answer.limitations == ()
    assert answer.provisional_interpretations == ()
    assert answer.corpus_limitation is False


def test_a_child_sex_question_in_another_domain_gets_only_the_line() -> None:
    result = _answer(SECOND_IN_5, "Will my wife have a son?")
    assert [intent.domain for intent in result.routing.intents] == [QuestionDomain.CHILDREN]
    (answer,) = result.answers
    assert answer.answer == CHILD_SEX_REPLY
    assert answer.provisional_interpretations == ()


def test_the_children_answer_stays_for_other_children_questions() -> None:
    (answer,) = _answer(FIFTH_IN_11, "What does my chart say about children?").answers
    assert answer.answer not in CHILD_SCOPE_REPLIES.values()
    assert answer.evidence
    for text in (answer.answer, *answer.reviewed_interpretations, *answer.limitations):
        assert child_wording_violation(text) is None


def test_the_wealth_v12_item_shows_the_putra_gloss() -> None:
    (answer,) = _answer(SECOND_IN_5, "What does my chart say about wealth?").answers
    (item,) = [
        i for i in answer.provisional_interpretations if i.rule_id == RULE_2_IN_5_WEALTH.rule_id
    ]
    assert item.rule_version == "v2"
    assert item.statement == RULE_2_IN_5_WEALTH_V2.statement
    assert PUTRA_GLOSS in item.statement and "पुत्रतो धनवान्" in item.statement
    assert PUTRA_CONVENTION in item.justification.conventions


def test_the_language_model_is_never_called_for_a_guarded_question() -> None:
    transport = _EvaluativeTransport("unused")
    response = _senior_client(transport).post(  # type: ignore[arg-type]
        "/api/v1/analyze", json=_career_request("Will I have a son?")
    )
    assert response.status_code == 200
    assert response.json()["answers"][0]["answer"] == CHILD_SEX_REPLY
    assert transport.calls == 0


@pytest.mark.parametrize(
    "summary",
    ["Your chart suggests a son.", "This may point to a childless period.", "पुत्र योग"],
)
def test_the_narrative_is_rejected_on_child_wording(summary: str) -> None:
    detailed, evidence = _matched_career_detailed()
    with pytest.raises(AnswerCompositionError) as raised:
        SeniorAstrologerComposer(_EvaluativeTransport(summary)).compose(
            "How is my career?", detailed, evidence
        )
    assert raised.value.reason_code == "children_wording"


# --- Consultation -------------------------------------------------------------------------------


def _consult(body: dict[str, Any]) -> dict[str, Any]:
    response = TestClient(create_app(Settings(llm_enabled=False))).post(
        "/api/v1/consultation", json=body
    )
    assert response.status_code == 200
    return response.json()  # type: ignore[no-any-return]


def _body(question: str, **extra: Any) -> dict[str, Any]:
    return {
        "birth_input": FIFTH_IN_11.model_dump(mode="json"),
        "as_of": _AS_OF.isoformat(),
        "question": question,
        **extra,
    }


def test_a_bare_comparison_about_a_child_s_sex_is_not_a_clarification() -> None:
    response = _consult(_body("Boy or girl, 2027 or 2028?"))
    assert response["status"] == "answered"
    assert response["analysis"]["answers"][0]["answer"] == CHILD_SEX_REPLY


@pytest.mark.parametrize(
    ("followup", "reply"),
    [
        ("Will it be a boy?", CHILD_SEX_REPLY),
        ("Will I ever have a child?", CHILD_SCOPE_REPLIES[ChildQuestionScope.WHETHER_OR_COUNT]),
    ],
)
def test_a_follow_up_gets_the_line_as_a_new_turn(followup: str, reply: str) -> None:
    first = _consult(_body("How is my career in 2027?"))
    second = _consult(_body(followup, consultation_id=first["state"]["consultation_id"]))
    (answer,) = second["analysis"]["answers"]
    assert answer["answer"] == reply
    assert second["state"]["domain"] == "children"


# --- Records and fail-closed display ------------------------------------------------------------


def test_v5_and_signification_v4_re_record_only_the_glossed_items() -> None:
    assert ACTIVE_PROVISIONAL_CORPUS is PROVISIONAL_CORPUS_V5
    assert PROVISIONAL_CORPUS_V5.release_id == "jyotish.provisional@v5"
    revised = {rule.rule_id for rule in CHILDREN_GUARD_REVISIONS}
    assert len(revised) == 6
    suta = {rule.rule_id: rule for rule in SUTA_CONVENTION_REVISIONS}
    assert set(suta) == {
        RULE_5_IN_4_EDUCATION.rule_id,
        RULE_5_IN_7_SPIRITUALITY.rule_id,
        RULE_7_IN_5_WEALTH.rule_id,
    }
    for old, new in zip(PROVISIONAL_CORPUS_V4.rules, PROVISIONAL_CORPUS_V5.rules, strict=True):
        if old.rule_id in suta:
            # सुत names the fifth house: the convention is the only change.
            assert int(new.rule.rule_version[1:]) == int(old.rule.rule_version[1:]) + 1
            assert new.model_dump(exclude={"rule", "justification"}) == old.model_dump(
                exclude={"rule", "justification"}
            )
            assert new.rule.model_dump(exclude={"rule_version"}) == old.rule.model_dump(
                exclude={"rule_version"}
            )
            assert new.justification.model_dump(
                exclude={"conventions", "recorded_at"}
            ) == old.justification.model_dump(exclude={"conventions", "recorded_at"})
            assert new.justification.conventions == (
                *old.justification.conventions,
                PUTRA_CONVENTION,
            )
            continue
        if old.rule_id not in revised:
            assert new == old
            continue
        assert new.rule.rule_version == "v2"
        assert new.rule.condition == old.rule.condition
        assert new.justification.original_text == old.justification.original_text
        assert new.justification.draft_translation == old.justification.draft_translation
        assert new.justification.confidence == old.justification.confidence
        assert new.wording == old.wording
        assert new.justification.conventions == (*old.justification.conventions, PUTRA_CONVENTION)
    corpus = ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS
    assert corpus.release_id == "jyotish.provisional.signification@v4"
    terms = {term.term_id for term in CHILDREN_GUARD_SIGNIFICATION_REVISIONS}
    assert len(terms) == 6
    for old_term, new_term in zip(
        PROVISIONAL_SIGNIFICATION_CORPUS_V3.terms, corpus.terms, strict=True
    ):
        if old_term.term_id not in terms:
            assert new_term == old_term
            continue
        assert new_term.term_version == "v2"
        assert (new_term.statement, new_term.sanskrit, new_term.display, new_term.tags) == (
            old_term.statement,
            old_term.sanskrit,
            old_term.display,
            old_term.tags,
        )


def _shown_texts(item: Any) -> list[str]:
    j = item.justification
    held = getattr(item, "wording", "shown") == "held" or item.translation_held_reason is not None
    return [
        item.statement,
        j.interpretive_reasoning,
        *j.conventions,
        j.transcription_notes or "",
        getattr(item, "held_reason", None) or "",
        item.translation_held_reason or "",
        *([] if held else [j.draft_translation]),
    ]


def test_every_active_record_passes_and_records_the_gloss_where_it_has_putra_or_suta() -> None:
    items = (*ACTIVE_PROVISIONAL_CORPUS.rules, *ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS.terms)
    for item in items:
        texts = _shown_texts(item)
        for text in texts:
            assert child_wording_violation(text) is None, (item, text)
            assert source_child_clause(text) is None, (item, text)
        if any(
            term in text
            for term in CHILD_TERMS
            for text in (*texts, item.justification.original_text)
        ):
            assert PUTRA_CONVENTION in item.justification.conventions, item


def _placement_facts(lord: int, house: int) -> dict[str, object]:
    return {f"jyotish.d1.house_lord.{lord}.placement_house": house}


def test_an_old_record_with_son_wording_shows_the_held_notice() -> None:
    facts = _placement_facts(2, 1)
    # The v4 record (reasoning "पुत्री (has sons)") stays, with the held notice in place of
    # the reasoning and the source verse.
    (old,) = provisional_interpretations(PROVISIONAL_CORPUS_V4, facts, "wealth")
    assert old.rule_version == "v1"
    assert old.statement == RULE_2_IN_1_WEALTH.statement
    assert old.justification.interpretive_reasoning == CHILD_HELD_NOTICE
    assert old.justification.original_text == SOURCE_HELD_NOTICE
    assert old.justification.original_text_held is True
    assert old.justification.held_reason == CHILD_HELD_NOTICE  # it named "sons"
    (item,) = provisional_interpretations(ACTIVE_PROVISIONAL_CORPUS, facts, "wealth")
    assert item.rule_version == "v2"
    assert "has sons" not in item.justification.interpretive_reasoning
    assert item.justification.interpretive_reasoning != CHILD_HELD_NOTICE


def test_a_record_with_putra_but_no_recorded_gloss_holds_the_verse() -> None:
    clean_reasoning = RULE_2_IN_1_WEALTH.justification.model_copy(
        update={"interpretive_reasoning": "The wealth clause is धनवान् (wealthy)."}
    )
    rule = RULE_2_IN_1_WEALTH.model_copy(
        update={"justification": clean_reasoning, "translation_held_reason": "Held."}
    )
    corpus = PROVISIONAL_CORPUS_V4.model_copy(update={"rules": (rule,)})
    # The original verse quotes पुत्री; without PUTRA_CONVENTION it is held, the item stays.
    (item,) = provisional_interpretations(corpus, _placement_facts(2, 1), "wealth")
    assert item.justification.original_text == SOURCE_HELD_NOTICE
    assert item.justification.interpretive_reasoning == "The wealth clause is धनवान् (wealthy)."


def test_a_statement_the_guard_holds_shows_the_held_statement() -> None:
    rule = RULE_2_IN_5_WEALTH  # v3 record: "wealth through a son"
    corpus = PROVISIONAL_CORPUS_V4.model_copy(update={"rules": (rule,)})
    (item,) = provisional_interpretations(corpus, _placement_facts(2, 5), "wealth")
    assert item.statement == HELD_STATEMENT and item.wording_held is True
    assert item.justification.draft_translation is None
    assert item.justification.held_reason == CHILD_HELD_NOTICE
    assert item.placement_explanation == "Your D1 second-house lord is placed in the fifth house."


def test_a_sent_translation_the_guard_holds_is_not_sent() -> None:
    justification = RULE_2_IN_1_WEALTH.justification.model_copy(
        update={
            "original_text": "धनवान्",
            "interpretive_reasoning": "The wealth clause is धनवान् (wealthy).",
            "draft_translation": "Wealthy, and has sons.",
        }
    )
    rule = RULE_2_IN_1_WEALTH.model_copy(
        update={"justification": justification, "translation_held_reason": None}
    )
    corpus = PROVISIONAL_CORPUS_V4.model_copy(update={"rules": (rule,)})
    (item,) = provisional_interpretations(corpus, _placement_facts(2, 1), "wealth")
    assert item.justification.draft_translation is None
    assert item.justification.held_reason == CHILD_HELD_NOTICE
    assert item.justification.original_text == "धनवान्"
    assert item.justification.original_text_held is False


def test_an_old_signification_record_with_sons_shows_the_held_notice() -> None:
    facts = {"jyotish.d1.planet.mars.placement_house": 4}
    old = ProvisionalSignificationCorpus(
        corpus_id="test", corpus_version="v1", terms=(MARS_KARAKA_LAND,)
    )
    (item,) = provisional_signification_items(old, facts, "property")
    assert item.statement == MARS_KARAKA_LAND.statement
    assert item.justification.interpretive_reasoning == CHILD_HELD_NOTICE
    assert item.justification.held_reason == CHILD_HELD_NOTICE
    # Mars's verse lists पुत्र; without the recorded convention the verse is held too.
    assert item.justification.original_text == SOURCE_HELD_NOTICE
    shown = provisional_signification_items(
        ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS, facts, "property"
    )
    (mars,) = [item for item in shown if item.rule_id == MARS_KARAKA_LAND.term_id]
    assert mars.justification.original_text == MARS_KARAKA_LAND.justification.original_text
    assert CHILD_HELD_NOTICE not in (
        mars.justification.interpretive_reasoning,
        mars.justification.held_reason,
    )


def test_a_section_with_child_wording_shows_the_held_notice() -> None:
    sections = (
        ConsultationSection(kind="direct", text="Your 2nd lord is in the 5th house."),
        ConsultationSection(kind="natal", text="The text describes wealth through a son."),
    )
    held = child_clean_sections(sections, "wealth")
    assert [s.kind for s in held] == ["direct", "natal"]
    assert held[0] == sections[0]
    assert held[1].text == CHILD_HELD_NOTICE
    config = domain_config(QuestionDomain.WEALTH)
    assert config is not None
    shown = _clean(config, sections[1], admitted=(sections[1].text,))
    assert shown is not None and shown.kind == "natal" and shown.text == CHILD_HELD_NOTICE
    assert _clean(config, sections[0], admitted=()) == sections[0]


def test_the_answer_line_with_child_wording_shows_the_held_notice() -> None:
    (answer,) = _answer(FIFTH_IN_11, "What does my chart say about children?").answers
    bad = answer.model_copy(
        update={
            "answer": "A son is indicated.",
            "consultation_sections": (
                ConsultationSection(kind="direct", text="A son is indicated."),
            ),
        }
    )
    held = child_clean_answer(bad, "children")
    assert held.answer == CHILD_HELD_NOTICE
    assert [s.text for s in held.consultation_sections] == [CHILD_HELD_NOTICE]
    assert child_clean_answer(answer, "children") == answer


def test_a_reviewed_statement_with_child_wording_shows_the_held_notice() -> None:
    result = _answer(FIFTH_IN_11, "What does my chart say about children?")
    evidence = _ask()._interpretation_evidence_builder.build(result.selections[0])
    (first, *rest) = evidence.selected_matched
    bad = evidence.model_copy(
        update={
            "selected_matched": (
                first.model_copy(update={"reviewed_statement": "A son is indicated."}),
                *rest,
            )
        }
    )
    built = DetailedAnswerBuilder().build(bad)
    assert len(built.evidence) == len(evidence.selected_matched)
    statements = [item.reviewed_statement for item in built.evidence]
    assert CHILD_HELD_NOTICE in statements and "A son is indicated." not in statements
    assert CHILD_HELD_NOTICE in built.reviewed_interpretations


def test_promotion_rejects_a_statement_naming_a_son() -> None:
    with pytest.raises(AdmissionError, match="children wording guard"):
        promote_to_reviewed(
            RULE_2_IN_5_WEALTH,
            _reviews(),
            source=_SOURCE,
            fact_contract=_CONTRACT,
            registry_version="jyotish-source-registry-children-guard-test",
        )


def test_a_provisional_rule_object_is_unchanged_by_the_guard() -> None:
    # The v3 records stay immutable history; only the display drops them.
    assert isinstance(RULE_2_IN_5_WEALTH, ProvisionalRule)
    assert "a son" in RULE_2_IN_5_WEALTH.statement


# --- Source verses with a child-sex or childlessness clause (owner, item 1) --------------------

# Second-lord Wealth verses whose source text has such a clause: v.9 पुत्री ("has sons"),
# v.10 पुत्रहीनः, v.12 पुत्रवान्, v.17 सुतहीनो, v.18 ज्येष्ठपुत्रसुखं न हि.
HELD_VERSES = {
    RULE_2_IN_1_WEALTH.rule_id: (1, "पुत्री"),
    RULE_2_IN_2_WEALTH.rule_id: (2, "पुत्रहीनः"),
    RULE_2_IN_5_WEALTH.rule_id: (5, "पुत्रवान्"),
    RULE_2_IN_10_WEALTH.rule_id: (10, "सुतहीनो"),
    RULE_2_IN_12_WEALTH.rule_id: (12, "ज्येष्ठपुत्रसुखं न हि"),
}


@pytest.mark.parametrize(
    "text",
    [
        "पुत्रहीनः प्रजायते",
        "सुतहीनो प्रजायते",
        "धनेशे तनौ पुत्री",
        "पुत्रवान् भवेत्",
        "ज्येष्ठपुत्रसुखं न हि",
        "सुता",
        "बेटी होगी",
    ],
)
def test_source_child_clauses_are_found(text: str) -> None:
    assert source_child_clause(text) is not None


@pytest.mark.parametrize(
    "text",
    [
        "पुत्रतो धनवान् भवेत्",
        "सुतेशे मातृभवने",
        "धनेशे सुतभावस्थे",
        "सप्तमेशे सुते स्थिते",
        "देवेज्यात्पञ्चमे पुत्रो",
        "गुरुश्चन्द्रसुतो जीवो",
        "चारुकन्या भवेद्भार्या",
    ],
)
def test_glossable_terms_and_house_names_are_not_source_clauses(text: str) -> None:
    assert source_child_clause(text) is None


@pytest.mark.parametrize("rule_id", sorted(HELD_VERSES))
def test_a_source_verse_with_a_child_clause_shows_the_held_notice(rule_id: str) -> None:
    house, clause = HELD_VERSES[rule_id]
    (rule,) = [rule for rule in ACTIVE_PROVISIONAL_CORPUS.rules if rule.rule_id == rule_id]
    assert clause in rule.justification.original_text  # the record keeps the verse
    (item,) = provisional_interpretations(
        ACTIVE_PROVISIONAL_CORPUS, _placement_facts(2, house), "wealth"
    )
    assert item.rule_id == rule_id
    assert item.justification.original_text == SOURCE_HELD_NOTICE
    assert item.justification.original_text_held is True
    shown = item.model_dump_json()
    assert clause not in shown and "हीन" not in shown
    # Only the verse is held: the item, its statement and its reasoning stay.
    assert item.statement == rule.statement
    assert item.justification.interpretive_reasoning == rule.justification.interpretive_reasoning


def test_wealth_vv_10_and_17_show_the_held_notice_in_the_answer() -> None:
    for birth_house in (2, 10):
        rule_id = next(rid for rid, (house, _) in HELD_VERSES.items() if house == birth_house)
        (item,) = provisional_interpretations(
            ACTIVE_PROVISIONAL_CORPUS, _placement_facts(2, birth_house), "wealth"
        )
        assert item.rule_id == rule_id
        assert item.justification.original_text == SOURCE_HELD_NOTICE
    (answer,) = _answer(SECOND_IN_5, "What does my chart say about wealth?").answers
    for item in answer.provisional_interpretations:
        assert source_child_clause(item.justification.original_text) is None
    (v12,) = [
        i for i in answer.provisional_interpretations if i.rule_id == RULE_2_IN_5_WEALTH.rule_id
    ]
    assert v12.justification.original_text_held is True


def test_a_verse_without_a_child_clause_is_shown_verbatim() -> None:
    (item,) = provisional_interpretations(
        ACTIVE_PROVISIONAL_CORPUS, _placement_facts(7, 5), "wealth"
    )
    assert item.justification.original_text_held is False
    assert "सुते स्थिते" in item.justification.original_text
    assert PUTRA_CONVENTION in item.justification.conventions


def test_the_review_pack_keeps_every_held_verse_in_full() -> None:
    pack = build_markdown(
        ACTIVE_PROVISIONAL_CORPUS,
        _AS_OF.date(),
        NOT_DRAFTED,
        ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS,
        REVIEWER_QUESTIONS,
    )
    for rule_id, (_, clause) in HELD_VERSES.items():
        (rule,) = [rule for rule in ACTIVE_PROVISIONAL_CORPUS.rules if rule.rule_id == rule_id]
        assert rule.justification.original_text in pack
        assert clause in pack
    assert pack.count("- **Source verse:** held in the app") == len(HELD_VERSES)
    assert "पुत्रहीनः" in pack and "सुतहीनो" in pack
    # Q7 stays for the reviewer, now covering सुत.
    (q7_title, q7_text) = REVIEWER_QUESTIONS[6]
    assert "सुत" in q7_title and PUTRA_GLOSS in q7_title
    assert "Please confirm" in q7_text
    assert f"### Q7. {q7_title}" in pack


def test_the_held_notices_pass_every_guard() -> None:
    for notice in (SOURCE_HELD_NOTICE, CHILD_HELD_NOTICE, PUTRA_CONVENTION):
        assert child_wording_violation(notice) is None
        assert source_child_clause(notice) is None


# --- सुत (owner, item 2) -----------------------------------------------------------------------


@pytest.mark.parametrize("text", ["सुतभाव is the fifth house.", "सुतेशे", "सुतहीनो"])
def test_suta_without_its_gloss_is_barred(text: str) -> None:
    assert child_wording_violation(text) is not None


def test_suta_with_its_gloss_passes() -> None:
    assert SUTA == "सुत"
    assert (
        child_wording_violation(f"सुतभाव, the house of {PUTRA_GLOSS}, is the fifth house.") is None
    )


def test_the_v12_reasoning_glosses_sutabhava() -> None:
    reasoning = RULE_2_IN_5_WEALTH_V2.justification.interpretive_reasoning
    assert reasoning.startswith(f"सुतभाव, the house of {PUTRA_GLOSS}, is the fifth house.")
    (item,) = provisional_interpretations(
        ACTIVE_PROVISIONAL_CORPUS, _placement_facts(2, 5), "wealth"
    )
    assert item.justification.interpretive_reasoning == reasoning


def test_every_displayed_suta_has_the_gloss_or_the_recorded_convention() -> None:
    houses = range(1, 13)
    for lord in (2, 4, 5, 7):
        for house in houses:
            for domain in ("wealth", "education", "spirituality", "marriage", "property"):
                for item in provisional_interpretations(
                    ACTIVE_PROVISIONAL_CORPUS, _placement_facts(lord, house), domain
                ):
                    j = item.justification
                    for text in (
                        item.statement,
                        j.interpretive_reasoning,
                        j.transcription_notes or "",
                        j.held_reason or "",
                        j.draft_translation or "",
                    ):
                        if SUTA in text:
                            assert PUTRA_GLOSS in text, (item.rule_id, text)
                    if SUTA in j.original_text:
                        assert PUTRA_CONVENTION in j.conventions, item.rule_id


# --- No re-versioned record was REVIEWED (owner, item 4) ---------------------------------------


def test_no_re_versioned_record_was_reviewed() -> None:
    reviewed_ids = {envelope.rule.rule_id for envelope in ACTIVE_PRODUCTION_RELEASE.envelopes}
    for rule in (*CHILDREN_GUARD_REVISIONS, *SUTA_CONVENTION_REVISIONS):
        assert rule.tier == "provisional"
        assert rule.justification.status is ReviewStatus.PROVISIONAL
        assert rule.rule_id.startswith("provisional.")
        assert rule.rule_id not in reviewed_ids
        assert reviewed_rule_id(rule.rule_id) not in reviewed_ids
    for term in CHILDREN_GUARD_SIGNIFICATION_REVISIONS:
        assert term.justification.status is ReviewStatus.PROVISIONAL
