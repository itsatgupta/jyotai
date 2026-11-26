"""NEXT-PROPERTY-01: carry-overs (router, primary/secondary labels, v.54) and Property.

All births are synthetic (lat/long 0, UTC); none describes a real person.
"""

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from test_career_answer_wording import _ask, _birth

from astrologer.application.analyze import DeterministicAnalysisRequest
from astrologer.application.domain_pipeline import _role_label
from astrologer.application.domains import domain_config
from astrologer.application.period_themes import role_label
from astrologer.application.property import (
    LIMIT_OUTLOOK,
    LIMIT_TIMING,
    NO_TIMING_RULE,
    OUT_OF_SCOPE_REPLIES,
    PROPERTY_DOMAIN,
    THEMES_PENDING,
)
from astrologer.application.wealth import OUT_OF_SCOPE_REPLIES as WEALTH_OUT_OF_SCOPE
from astrologer.astrology.vargas import DivisionalChartType
from astrologer.common.config import Settings
from astrologer.composition.models import DetailedComposedAnswer
from astrologer.composition.property_guard import property_wording_violation
from astrologer.knowledge.models import JyotishDomain
from astrologer.knowledge.provisional_pack_v1 import RULE_7_IN_5_WEALTH
from astrologer.knowledge.provisional_pack_v3 import PROVISIONAL_CORPUS_V3
from astrologer.knowledge.provisional_pack_v4 import (
    ACTIVE_PROVISIONAL_CORPUS,
    NOT_DRAFTED,
    PROPERTY_RULES,
    REVIEWER_QUESTIONS,
    RULE_4_IN_2_PROPERTY,
    RULE_7_IN_5_WEALTH_V2,
)
from astrologer.knowledge.provisional_signification import (
    ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS,
    PROPERTY_SIGNIFICATIONS,
    PROVISIONAL_SIGNIFICATION_CORPUS_V2,
)
from astrologer.knowledge.signification_admit02_v1 import ACTIVE_SIGNIFICATION_CORPUS
from astrologer.knowledge.signification_tags import ACTIVE_SIGNIFICATION_TAG_SET, domain_view
from astrologer.main import create_app
from astrologer.questions.models import QuestionDomain
from astrologer.questions.router import question_domains

_AS_OF = datetime(2026, 1, 1, tzinfo=UTC)
PROFILES = {
    "match": _birth("1978-01-01", "12:00:00"),  # 4th lord Mercury in the 9th
    "fourth_in_2": _birth("1970-07-15", "06:00:00"),  # 4th lord Mercury in the 2nd (v.27)
    "venus_lord": _birth("1985-03-10", "06:00:00"),  # 4th lord Venus (a kāraka) in the 2nd
}
OUTLOOK = "What does my chart say about property?"
TIMING = "When will I buy a house?"
YEAR = "property in 2027?"


def _answer(birth: object, question: str) -> DetailedComposedAnswer:
    result = _ask().answer(
        DeterministicAnalysisRequest(birth_input=birth, as_of=_AS_OF, question=question)  # type: ignore[arg-type]
    )
    (answer,) = result.answers
    return answer


def _consult(question: str, birth: object, flag: bool) -> dict:  # type: ignore[type-arg]
    client = TestClient(create_app(Settings(llm_enabled=False)))
    body = {
        "birth_input": birth.model_dump(mode="json"),  # type: ignore[attr-defined]
        "as_of": _AS_OF.isoformat(),
        "question": question,
        "include_provisional": flag,
    }
    response = client.post("/api/v1/consultation", json=body)
    assert response.status_code == 200
    return response.json()["analysis"]["answers"][0]  # type: ignore[no-any-return]


def _domains(question: str) -> list[str]:
    return [domain.value for domain in question_domains(question)]


# --- A1: router --------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "question",
    [
        "Will my income grow?",
        "When will I have more money?",
        "Will I be rich?",
        "How are my savings?",
        "When will my income increase?",
        "mera dhan kab badhega?",
        "paisa kab aayega?",
        "meri kamai kab badhegi?",
        "kya main amir banunga?",
        "bachat kaise hogi?",
        "Should I invest my money in stocks?",
        "How much money will I have?",
        "kitna paisa milega?",
    ],
)
def test_a1_money_and_income_questions_route_to_wealth(question: str) -> None:
    assert _domains(question) == ["wealth"]


@pytest.mark.parametrize(
    "question",
    [
        "Will my job bring more money?",
        "How is my career income in 2027?",
        "Will I get promoted and earn more money?",
        "Will my profession make me rich?",
        "Will my career give me a car?",
        "Why is my career flat?",
        "How is my career in 2027?",
        "What does my tenth-house-lord placement say about career?",
    ],
)
def test_a1_career_questions_are_not_misrouted(question: str) -> None:
    assert _domains(question) == ["career"]


def test_a1_investment_and_amount_questions_get_the_one_line_reply() -> None:
    birth = PROFILES["match"]
    for question, scope in (
        ("Should I invest my money in stocks?", "investment"),
        ("paisa nivesh kahan karun?", "investment"),
        ("How much money will I have?", "amount"),
        ("kitna paisa milega?", "amount"),
    ):
        answer = _answer(birth, question)
        assert answer.answer == WEALTH_OUT_OF_SCOPE[scope], question
        assert [section.kind for section in answer.consultation_sections] == ["direct"]
        assert _consult(question, birth, True)["provisional_interpretations"] == []


def test_a1_wealth_questions_get_the_wealth_answer() -> None:
    # "Will … grow?" is an outlook question (as "Will my wealth grow?"); "when" asks for timing.
    outlook = _answer(PROFILES["match"], "Will my income grow?")
    assert outlook.answer.startswith("No reviewed Wealth interpretation is shown for your chart")
    timing = _answer(PROFILES["match"], "When will my income grow?")
    assert timing.answer.startswith("No reviewed timing rule exists for wealth")


@pytest.mark.parametrize(
    "question",
    [
        "When will I buy a house?",
        "When will I get a flat?",
        "Will I buy land?",
        "When can I buy a plot?",
        "What does my chart say about property?",
        "When will I get a vehicle?",
        "When will I get a car?",
        "ghar kab milega?",
        "What does my chart say about my home?",
    ],
)
def test_router_sends_property_questions_to_property(question: str) -> None:
    assert _domains(question) == ["property"]


def test_numbered_houses_are_not_a_property_word() -> None:
    assert _domains("What does my 7th house say about marriage?") == ["marriage"]
    assert _domains("What does my fourth house show?") == []
    assert _domains("What do my 2nd and 11th houses say about wealth?") == ["wealth"]
    assert _domains("Will I buy a house in 2027?") == ["property"]


def test_kab_is_a_timing_word() -> None:
    answer = _answer(PROFILES["match"], "ghar kab milega?")
    assert answer.answer.startswith(NO_TIMING_RULE)


# --- A3: Mahadasha primary, Antardasha secondary -----------------------------------------------


def test_a3_every_period_theme_role_is_labelled() -> None:
    assert role_label("Mahadasha") == "Mahadasha (primary)"
    assert role_label("Antardasha") == "Antardasha (secondary)"
    assert role_label("Mahadasha and Antardasha") == (
        "Mahadasha (primary) and Antardasha (secondary)"
    )
    assert _role_label({"Mahadasha"}) == "Mahadasha (primary)"
    assert _role_label({"Antardasha"}) == "Antardasha (secondary)"
    assert _role_label({"Mahadasha", "Antardasha"}) == (
        "Mahadasha (primary) and Antardasha (secondary)"
    )


def test_a3_labels_in_career_and_generic_period_themes() -> None:
    career = _answer(PROFILES["match"], "How is my career in 2027?")
    themes = next(s for s in career.consultation_sections if s.kind == "period_themes")
    assert "Jupiter Mahadasha (primary) (throughout 2027): reviewed themes" in themes.text
    assert " Antardasha (secondary) (" in themes.text
    wealth = _answer(PROFILES["match"], "wealth in 2027?")
    themes = next(s for s in wealth.consultation_sections if s.kind == "period_themes")
    assert "Jupiter Mahadasha (primary)." in themes.text


# --- A4: v.54 ----------------------------------------------------------------------------------


def test_a4_v54_translation_stays_in_the_review_pack() -> None:
    rule = RULE_7_IN_5_WEALTH_V2
    assert rule.rule_id == RULE_7_IN_5_WEALTH.rule_id
    assert (rule.rule.rule_version, RULE_7_IN_5_WEALTH.rule.rule_version) == ("v2", "v1")
    assert rule.statement == RULE_7_IN_5_WEALTH.statement
    assert rule.justification == RULE_7_IN_5_WEALTH.justification
    assert RULE_7_IN_5_WEALTH.translation_held_reason is None
    assert rule.translation_held_reason is not None
    assert rule in ACTIVE_PROVISIONAL_CORPUS.rules
    assert RULE_7_IN_5_WEALTH not in ACTIVE_PROVISIONAL_CORPUS.rules
    # Every other v3 rule is carried over unchanged.
    others = {r for r in PROVISIONAL_CORPUS_V3.rules if r.rule_id != rule.rule_id}
    assert others | {rule, *PROPERTY_RULES} == set(ACTIVE_PROVISIONAL_CORPUS.rules)
    for item in ACTIVE_PROVISIONAL_CORPUS.for_domain("wealth"):
        assert item.wording == "held" or item.translation_held_reason is not None


# --- B: Property -------------------------------------------------------------------------------


def test_property_domain_config() -> None:
    assert domain_config(QuestionDomain.PROPERTY) is PROPERTY_DOMAIN
    assert PROPERTY_DOMAIN.houses == (4,)
    assert PROPERTY_DOMAIN.karakas == ("mars", "jupiter", "venus")
    assert PROPERTY_DOMAIN.tag_domain is JyotishDomain.PROPERTY
    assert PROPERTY_DOMAIN.composer == "generic"
    # D4 is not calculated, so no divisional facts are shown (open item).
    assert PROPERTY_DOMAIN.divisional is None
    assert "d4" not in {chart.value for chart in DivisionalChartType}
    # No reviewed signification term is tagged Property.
    view = domain_view(
        ACTIVE_SIGNIFICATION_CORPUS, JyotishDomain.PROPERTY, ACTIVE_SIGNIFICATION_TAG_SET
    )
    assert view.entries == ()


def test_property_outlook_states_calculated_factors_only() -> None:
    answer = _answer(PROFILES["match"], OUTLOOK)
    assert [s.kind for s in answer.consultation_sections] == ["direct", "chart_factors", "limit"]
    assert answer.answer.startswith("No reviewed Property interpretation is shown for your chart")
    assert "your 4th lord, Mercury, is in the 9th house" in answer.answer
    assert "Mars is in the 5th house, Jupiter is in the 4th house and Venus" in answer.answer
    assert answer.answer.endswith(LIMIT_OUTLOOK)
    assert answer.evidence == ()
    assert property_wording_violation(answer.answer) is None


def test_property_lord_that_is_a_karaka_is_named_once_in_the_direct_line() -> None:
    answer = _answer(PROFILES["venus_lord"], OUTLOOK)
    direct = answer.consultation_sections[0].text
    assert "your 4th lord, Venus, is in the 2nd house" in direct
    assert direct.count("Venus") == 1


def test_property_timing_lists_periods_only() -> None:
    answer = _answer(PROFILES["match"], TIMING)
    kinds = [s.kind for s in answer.consultation_sections]
    assert kinds == [
        "direct",
        "periods",
        "period_themes",
        "chart_factors",
        "timing_status",
        "limit",
    ]
    assert answer.answer.startswith(NO_TIMING_RULE)
    themes = next(s for s in answer.consultation_sections if s.kind == "period_themes")
    assert themes.text.endswith(THEMES_PENDING)
    assert answer.answer.endswith(LIMIT_TIMING)
    assert answer.timing_answered is False
    year = _answer(PROFILES["match"], YEAR)
    assert year.answer.startswith(f"{NO_TIMING_RULE} In 2027, the Mahadasha and Antardasha")
    compare = _answer(PROFILES["match"], "Which is better for property, 2027 or 2028?")
    assert "the years are not ranked" in compare.answer


@pytest.mark.parametrize(
    ("question", "scope"),
    [
        ("What will be the price of my flat?", "price"),
        ("How much is my land worth?", "price"),
        ("Should I sell my house?", "advice"),
        ("Is it a good time to buy a flat?", "advice"),
        ("kya mujhe ghar kharidna chahiye?", "advice"),
        ("Should I invest in property?", "advice"),
        ("Will I win the court case over my land?", "legal"),
        ("Will my property dispute end?", "legal"),
        ("Will I lose my house?", "fatalistic"),
        ("Will I ever own a house?", "fatalistic"),
        ("Will I have a car accident?", "fatalistic"),
    ],
)
def test_property_out_of_scope_questions_get_one_line(question: str, scope: str) -> None:
    answer = _answer(PROFILES["match"], question)
    assert answer.answer == OUT_OF_SCOPE_REPLIES[scope]
    assert [s.kind for s in answer.consultation_sections] == ["direct"]


def test_out_of_scope_replies_pass_the_property_guard() -> None:
    for reply in OUT_OF_SCOPE_REPLIES.values():
        assert property_wording_violation(reply) is None
    assert property_wording_violation("A good time to buy land.") is not None
    assert property_wording_violation("You may lose the house.") is not None
    assert property_wording_violation("A dispute is shown.") is not None
    assert property_wording_violation("quoted loss", quoted=("quoted loss",)) is None


def test_property_answers_show_no_other_domain_term() -> None:
    terms = {t.display for e in ACTIVE_SIGNIFICATION_CORPUS.entries for t in e.terms}
    for domain in ("marriage", "wealth"):
        terms |= {t.display for t in ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS.for_domain(domain)}
    for question in (OUTLOOK, TIMING, YEAR):
        for birth in PROFILES.values():
            text = _consult(question, birth, True)
            visible = " ".join(
                [text["answer"], *(i["statement"] for i in text["provisional_interpretations"])]
            )
            assert not [term for term in terms if f" {term}" in visible.lower()], question


# --- B: provisional Property records -----------------------------------------------------------


def test_twelve_fourth_lord_placements_are_accounted_for() -> None:
    shown = {
        rule.rule.condition.expected_value for rule in PROPERTY_RULES if rule.wording == "shown"
    }
    held = {rule.rule.condition.expected_value for rule in PROPERTY_RULES if rule.wording == "held"}
    assert (shown, held) == ({2}, set())
    notes = NOT_DRAFTED["property"]
    located = {
        "1st house: verse 26": {1},
        "3rd or 11th house: verse 28": {3, 11},
        "4th house: verse 29": {4},
        "5th or 9th house: verse 30": {5, 9},
        "6th house: verse 31": {6},
        "7th house: verse 32": {7},
        "8th or 12th house: verse 33": {8, 12},
        "10th house: verse 34": {10},
    }
    not_drafted: set[int] = set()
    for phrase, houses in located.items():
        assert sum(phrase in note for note in notes) == 1, phrase
        not_drafted |= houses
    assert shown | held | not_drafted == set(range(1, 13))
    assert not (shown & not_drafted)


def test_the_property_rule_has_a_full_justification_and_holds_its_translation() -> None:
    rule = RULE_4_IN_2_PROPERTY
    assert rule.domain is JyotishDomain.PROPERTY
    assert rule.fact_dependencies == ("jyotish.d1.house_lord.4.placement_house",)
    assert rule.justification.confidence.value == "low"
    assert "verse 27" in rule.justification.locator and "PDF p. 186" in rule.justification.locator
    assert "सर्वसम्पद्युत" in rule.statement and rule.translation_held_reason is not None
    assert property_wording_violation(rule.statement) is None
    item = next(
        i
        for i in _consult(OUTLOOK, PROFILES["fourth_in_2"], True)["provisional_interpretations"]
        if i["rule_id"] == rule.rule_id
    )
    assert item["badge"] == "Provisional · low confidence"
    assert item["justification"]["draft_translation"] is None
    assert item["justification"]["held_reason"] == rule.translation_held_reason


def test_property_significations() -> None:
    corpus = ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS
    assert corpus.release_id == "jyotish.provisional.signification@v3"
    assert corpus.terms[: len(PROVISIONAL_SIGNIFICATION_CORPUS_V2.terms)] == (
        PROVISIONAL_SIGNIFICATION_CORPUS_V2.terms
    )
    assert corpus.for_domain("property") == PROPERTY_SIGNIFICATIONS
    table = {
        (t.subject, t.sanskrit, t.display, t.justification.confidence.value)
        for t in PROPERTY_SIGNIFICATIONS
    }
    assert table == {
        ("4", "गृह", "house or home", "high"),
        ("4", "क्षेत्र", "fields or land", "high"),
        ("4", "वाहन", "vehicles", "high"),
        ("mars", "भूमि", "land (kāraka)", "high"),
        ("mars", "सद्म", "dwelling (kāraka)", "medium"),
        ("jupiter", "गृह", "house (kāraka)", "high"),
        ("venus", "यान", "vehicles (kāraka)", "high"),
        ("sun", "क्षेत्र", "fields or land (kāraka)", "medium"),
    }
    for term in PROPERTY_SIGNIFICATIONS:
        assert {tag.domain for tag in term.tags} == {JyotishDomain.PROPERTY}
        assert term.translation_held_reason is not None
        assert term.sanskrit in term.justification.original_text
        assert term.justification.locator and term.justification.interpretive_reasoning
    # Terms for the mother, relatives or happiness are not drafted or tagged Property.
    sanskrit = {t.sanskrit for t in corpus.terms}
    assert not sanskrit & {"बन्धु", "मातृसौख्य", "निधि", "सुख"}
    assert "बन्धु (relatives) and मातृसौख्य" in NOT_DRAFTED["property"][-1]
    # The pipeline kārakas each have a high-confidence property term; the Sun does not.
    high = {
        t.subject
        for t in PROPERTY_SIGNIFICATIONS
        if t.subject_kind == "graha" and t.justification.confidence.value == "high"
    }
    assert high == set(PROPERTY_DOMAIN.karakas)


def test_reviewer_questions_cover_karakas_sampad_and_d4() -> None:
    titles = " ".join(title for title, _ in REVIEWER_QUESTIONS)
    assert "kārakas" in titles and "सम्पद्" in titles and "D4" in titles


def test_flag_off_property_answers_carry_no_provisional_item() -> None:
    for question in (OUTLOOK, TIMING):
        assert (
            _consult(question, PROFILES["fourth_in_2"], False)["provisional_interpretations"] == []
        )
