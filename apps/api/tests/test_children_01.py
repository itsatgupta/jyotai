"""NEXT-CHILDREN-01: the Children domain on the domain template, and the carry-overs.

A1 (open item 19): "Which Dasha applies?" after a Marriage, Wealth, Property or Children answer
points to the calculated periods that answer lists, never "no timing evidence".
A3: the held notices say "held for expert review" (no rule name).
B: Children answers (5th house, 5th lord, Jupiter), the two reviewed Children rules the
reviewer confirmed (Sitting 1 items 16 and 17), provisional Children rules (all 12 fifth-lord
placements accounted for) and significations, router words, timing (periods only).

All births are synthetic (lat/long 0, UTC); none describes a real person.
"""

import re
from datetime import UTC, datetime

import pytest
from test_career_answer_wording import _ask, _birth

from astrologer.application.analyze import DeterministicAnalysisRequest
from astrologer.application.children import CHILD_SCOPE_REPLIES
from astrologer.application.children_domain import (
    CHILDREN_DOMAIN,
    LIMIT_OUTLOOK,
    LIMIT_TIMING,
    NO_TIMING_RULE,
    OUT_OF_SCOPE_REPLIES,
    THEMES_PENDING,
    TIMING_STATUS,
    TIMING_STATUS_PERIODS,
)
from astrologer.application.consultation import (
    ConsultationRequest,
    ConsultationService,
    ConsultationStore,
)
from astrologer.application.domains import domain_config
from astrologer.application.provisional import (
    provisional_interpretations,
    provisional_signification_items,
)
from astrologer.astrology.vargas import DivisionalChartType
from astrologer.composition.children_domain_guard import children_domain_violation
from astrologer.composition.children_guard import (
    CHILD_HELD_NOTICE,
    PUTRA_CONVENTION,
    PUTRA_GLOSS,
    SOURCE_HELD_NOTICE,
    child_wording_violation,
    source_child_clause,
)
from astrologer.composition.models import DetailedComposedAnswer
from astrologer.knowledge import ACTIVE_PRODUCTION_RELEASE
from astrologer.knowledge.models import JyotishDomain
from astrologer.knowledge.provisional import HELD_STATEMENT
from astrologer.knowledge.provisional_pack_v5 import PROVISIONAL_CORPUS_V5
from astrologer.knowledge.provisional_pack_v6 import (
    ACTIVE_PROVISIONAL_CORPUS,
    CHILDREN_RULES,
    NOT_DRAFTED,
    PROVISIONAL_CORPUS_V6,
)
from astrologer.knowledge.provisional_signification import (
    ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS,
    CHILDREN_SIGNIFICATIONS,
    EDUCATION_SIGNIFICATIONS,
    FIFTH_HOUSE_CHILDREN,
    JUPITER_KARAKA_CHILDREN,
    PROVISIONAL_SIGNIFICATION_CORPUS_V4,
)
from astrologer.questions.models import QuestionDomain
from astrologer.questions.router import question_domains

_AS_OF = datetime(2026, 1, 1, tzinfo=UTC)
PROFILES = {
    "fifth_in_11": _birth("1960-01-01", "12:00:00"),  # 5th lord Moon in the 11th (item 16)
    "eleventh_in_2": _birth("1962-01-01", "00:00:00"),  # 11th lord in the 2nd (item 17)
    "eleventh_in_5": _birth("1960-01-01", "00:00:00"),  # 11th lord in the 5th (item 17)
    "tenth_in_11": _birth("1960-10-01", "12:00:00"),  # 10th lord in the 11th (item 18, out)
    "tenth_in_5": _birth("1963-01-01", "00:00:00"),  # 10th lord in the 5th (item 18, out)
    "fifth_in_9": _birth("1960-04-01", "12:00:00"),  # v.41 shown
    "fifth_in_10": _birth("1965-01-01", "06:00:00"),  # v.41 shown
    "fifth_in_5": _birth("1960-07-15", "18:00:00"),  # v.38 held
    "fifth_in_2": _birth("1960-07-15", "06:00:00"),  # v.36 held
    "fifth_in_12": _birth("1960-01-01", "06:00:00"),  # v.39 held
    "fifth_in_1": _birth("1962-01-01", "06:00:00"),  # v.35 not drafted
}
OUTLOOK = "What does my chart say about children?"
TIMING = "When will I have children?"
YEAR = "children in 2027?"
REVIEWED_CHILDREN_RULES = {
    "bphs.d1.house_lord.5.in_11.children.v1": "Sitting 1 item 16",
    "bphs.d1.house_lord.11.in_2_or_5.children.v1": "Sitting 1 item 17",
}
TENTH_LORD_CHILDREN_RULE = "bphs.d1.house_lord.10.in_5_or_11.children.v1"


def _statement(rule_id: str) -> str:
    """The admitted statement of a reviewed rule (the evidence items carry it, not the id)."""
    interpretations = {
        record.interpretation_id: record.statement
        for record in ACTIVE_PRODUCTION_RELEASE.registry.interpretations
    }
    (envelope,) = [e for e in ACTIVE_PRODUCTION_RELEASE.envelopes if e.rule.rule_id == rule_id]
    return interpretations[envelope.interpretation_id]


def _answer(name: str, question: str, *, provisional: bool = False) -> DetailedComposedAnswer:
    result = _ask().answer(
        DeterministicAnalysisRequest(
            birth_input=PROFILES[name],
            as_of=_AS_OF,
            question=question,
            include_provisional=provisional,
        )
    )
    (answer,) = result.answers
    return answer


def _kinds(answer: DetailedComposedAnswer) -> list[str]:
    return [section.kind for section in answer.consultation_sections]


def _section(answer: DetailedComposedAnswer, kind: str) -> str:
    return next(s.text for s in answer.consultation_sections if s.kind == kind)


@pytest.fixture
def consultation() -> ConsultationService:
    return ConsultationService(_ask(), ConsultationStore())


def _consult(
    service: ConsultationService, name: str, question: str, consultation_id: str | None = None
) -> object:
    return service.respond(
        ConsultationRequest(
            birth_input=PROFILES[name],
            as_of=_AS_OF,
            question=question,
            consultation_id=consultation_id,
        )
    )


# --- A1: "Which Dasha applies?" points to the listed periods ------------------------------------


@pytest.mark.parametrize(
    ("question", "domain"),
    [
        ("When will I get married?", "marriage"),
        ("When will my wealth grow?", "wealth"),
        ("When will I buy a house?", "property"),
        (TIMING, "children"),
    ],
)
def test_a1_dasha_follow_up_points_to_the_listed_periods(
    consultation: ConsultationService, question: str, domain: str
) -> None:
    first = _consult(consultation, "fifth_in_11", question)
    answer = first.analysis.answers[0]  # type: ignore[attr-defined]
    periods = _section(answer, "periods")
    reply = _consult(
        consultation,
        "fifth_in_11",
        "Which Dasha applies?",
        first.state.consultation_id,  # type: ignore[attr-defined]
    )
    text = reply.reply or ""  # type: ignore[attr-defined]
    assert reply.status == "answered"  # type: ignore[attr-defined]
    assert "No approved timing evidence" not in text
    assert text.startswith("The Dasha periods for this answer are the calculated periods it")
    assert periods in text
    assert f"Timing rules for {domain}: none reviewed yet." in text
    kinds = [s.kind for s in reply.consultation_sections]  # type: ignore[attr-defined]
    assert kinds == ["periods", "timing_status"]


def test_a1_outlook_answer_names_how_to_see_the_periods(
    consultation: ConsultationService,
) -> None:
    first = _consult(consultation, "fifth_in_11", OUTLOOK)
    reply = _consult(
        consultation,
        "fifth_in_11",
        "Which Dasha applies?",
        first.state.consultation_id,  # type: ignore[attr-defined]
    )
    text = reply.reply or ""  # type: ignore[attr-defined]
    assert reply.status == "answered"  # type: ignore[attr-defined]
    assert "No approved timing evidence" not in text
    assert text.startswith("This answer lists no Dasha periods because the question gave no time")
    assert TIMING_STATUS in text


def test_a1_career_follow_ups_are_unchanged(consultation: ConsultationService) -> None:
    first = _consult(consultation, "fifth_in_11", "In which exact month will I get promoted?")
    reply = _consult(
        consultation,
        "fifth_in_11",
        "Which Dasha applies?",
        first.state.consultation_id,  # type: ignore[attr-defined]
    )
    assert reply.status == "unsupported"  # type: ignore[attr-defined]
    assert "month or date precision is not supported" in (reply.reply or "")  # type: ignore[attr-defined]


# --- A3: held notices -------------------------------------------------------------------------


def test_a3_held_notices_drop_the_rule_name() -> None:
    assert CHILD_HELD_NOTICE == "This text is held for expert review."
    assert SOURCE_HELD_NOTICE == (
        "The source verse is held for expert review; the full verse is in the final review pack."
    )
    for notice in (CHILD_HELD_NOTICE, SOURCE_HELD_NOTICE):
        assert "wording rule" not in notice and "JyotAI" not in notice
        assert child_wording_violation(notice) is None


# --- Guards (strengthened, never weakened) ------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "सुतेशे पञ्चमे यस्य तस्य पुत्रो न जीवति ।",  # the son does not live (v.38)
        "मृतापत्यो दत्तपुत्रो धनपुत्रोऽथवा भवेत्",  # whose children die (v.39)
        "सुतेश ५वें भाव में हो तो जातक का पुत्र नहीं जीता है",
        "और उसके पुत्र मर जाते हैं",
        "बहुपुत्रधनान्वितः",  # a number of children (v.42)
        "विख्यातः कुलदीपकः",  # an epithet of a son (v.41)
    ],
)
def test_source_verses_with_a_death_number_or_sex_epithet_are_held(text: str) -> None:
    assert source_child_clause(text) is not None


@pytest.mark.parametrize(
    "text", ["the native's children die", "the child does not live", "his kids won't survive"]
)
def test_child_death_wording_is_barred_in_answers(text: str) -> None:
    assert child_wording_violation(text) is not None


@pytest.mark.parametrize(
    "text",
    [
        "Your fertility is indicated.",
        "A pregnancy is likely.",
        "There is a santan dosha.",
        "You will have children.",
        "Children are guaranteed.",
        "It is your destiny.",
    ],
)
def test_children_domain_guard(text: str) -> None:
    assert children_domain_violation(text) is not None


def test_children_texts_pass_every_guard() -> None:
    texts = (
        NO_TIMING_RULE,
        TIMING_STATUS,
        TIMING_STATUS_PERIODS,
        LIMIT_OUTLOOK,
        LIMIT_TIMING,
        THEMES_PENDING,
        *OUT_OF_SCOPE_REPLIES.values(),
    )
    for text in texts:
        assert child_wording_violation(text) is None, text
        assert children_domain_violation(text) is None, text


# --- B: the domain configuration ------------------------------------------------------------


def test_children_runs_on_the_domain_template() -> None:
    assert domain_config(QuestionDomain.CHILDREN) is CHILDREN_DOMAIN
    assert CHILDREN_DOMAIN.composer == "generic"
    assert CHILDREN_DOMAIN.houses == (5,)
    assert CHILDREN_DOMAIN.karakas == ("jupiter",)
    assert CHILDREN_DOMAIN.tag_domain is JyotishDomain.CHILDREN
    # D7 is not calculated, so no divisional fact is shown (open item).
    assert "d7" not in {chart.value for chart in DivisionalChartType}
    assert CHILDREN_DOMAIN.divisional is None


def test_the_karaka_cites_the_verses_that_name_jupiter_for_children() -> None:
    locator = JUPITER_KARAKA_CHILDREN.justification.locator
    assert "verse 5; PDF p. 109" in locator
    assert "vv. 30 and 33, PDF p. 107" in locator and "v.37, PDF p. 108" in locator
    original = JUPITER_KARAKA_CHILDREN.justification.original_text
    assert "पुत्रमित्रान्दोलनादिकारको गुरुः" in original  # v.5
    assert "देवेज्यात्पञ्चमे पुत्रो" in original  # v.33
    assert "गुरुणा चात्र विज्ञेया पुत्र" in original  # v.30


@pytest.mark.parametrize(
    "question",
    [
        "What does my chart say about children?",
        "Tell me about my child",
        "What about kids?",
        "santan ke baare mein batao",
        "bachcha kab hoga?",
        "What does my chart say about progeny?",
    ],
)
def test_router_sends_children_words_to_children(question: str) -> None:
    assert question_domains(question) == (QuestionDomain.CHILDREN,)


@pytest.mark.parametrize("question", ["kya bacha hai?", "paise bache?", "How is my career?"])
def test_router_does_not_take_left_over_words_as_children(question: str) -> None:
    assert QuestionDomain.CHILDREN not in question_domains(question)


# --- B: answers ------------------------------------------------------------------------------


def test_outlook_lists_the_fifth_lord_and_jupiter_as_calculated_facts() -> None:
    answer = _answer("tenth_in_11", OUTLOOK)
    assert _kinds(answer) == ["direct", "chart_factors", "limit"]
    direct = _section(answer, "direct")
    assert direct.startswith("No reviewed Children interpretation is shown for your chart")
    assert "your 5th lord, Mars, is in the 7th house and Jupiter is in the 1st house." in direct
    factors = _section(answer, "chart_factors")
    assert "Your 5th lord is Mars, placed in the 7th house." in factors
    assert "Calculated fact (sign dignity): Jupiter" in factors
    assert _section(answer, "limit") == LIMIT_OUTLOOK
    assert not answer.evidence


@pytest.mark.parametrize("name", ["tenth_in_11", "tenth_in_5"])
def test_the_tenth_lord_rule_never_shows_in_children(name: str) -> None:
    answer = _answer(name, OUTLOOK, provisional=True)
    assert answer.evidence == ()
    assert "tenth-house lord" not in answer.model_dump_json()
    manifest = {rule.rule_id for rule in ACTIVE_PRODUCTION_RELEASE.manifest.rules}
    assert TENTH_LORD_CHILDREN_RULE not in manifest


@pytest.mark.parametrize(
    ("name", "rule_id"),
    [
        ("fifth_in_11", "bphs.d1.house_lord.5.in_11.children.v1"),
        ("eleventh_in_2", "bphs.d1.house_lord.11.in_2_or_5.children.v1"),
        ("eleventh_in_5", "bphs.d1.house_lord.11.in_2_or_5.children.v1"),
    ],
)
def test_the_two_confirmed_rules_show_as_supporting_and_verbatim(name: str, rule_id: str) -> None:
    answer = _answer(name, OUTLOOK)
    (item,) = answer.evidence
    assert item.reviewed_statement == _statement(rule_id) and item.domain == "children"
    assert item.weight == "secondary"
    natal = _section(answer, "natal")
    assert natal.startswith("Supporting: ")
    assert item.reviewed_statement in natal
    assert _section(answer, "direct").startswith(
        "Your D1 chart has reviewed natal Children context, shown below"
    )


def test_the_confirmed_rules_carry_the_reviewer_records() -> None:
    interpretations = {
        record.interpretation_id: record
        for record in ACTIVE_PRODUCTION_RELEASE.registry.interpretations
    }
    envelopes = {
        envelope.rule.rule_id: envelope
        for envelope in ACTIVE_PRODUCTION_RELEASE.envelopes
        if envelope.domain is JyotishDomain.CHILDREN
    }
    assert set(envelopes) == set(REVIEWED_CHILDREN_RULES)
    for rule_id, item in REVIEWED_CHILDREN_RULES.items():
        review = interpretations[envelopes[rule_id].interpretation_id].review
        assert review.reviewer == "Pandit ji (full name pending)"
        assert f"Verdict: {item} (pandit-ji-verdicts-2026-11-24.md)" in review.notes
        assert "jyotish.admit02.sitting-1-2.admission.v1.md" in review.notes


def test_timing_lists_periods_only_with_the_pending_line() -> None:
    answer = _answer("fifth_in_11", TIMING)
    assert _kinds(answer) == [
        "direct",
        "periods",
        "period_themes",
        "natal",
        "chart_factors",
        "timing_status",
        "limit",
    ]
    direct = _section(answer, "direct")
    assert direct.startswith(NO_TIMING_RULE)
    assert "the Mahadasha and Antardasha periods of your 5th lord, Moon, and of Jupiter" in direct
    themes = _section(answer, "period_themes")
    assert themes.endswith(THEMES_PENDING)
    assert "reviewed themes" not in themes
    assert _section(answer, "timing_status") == TIMING_STATUS_PERIODS
    assert _section(answer, "limit") == LIMIT_TIMING
    periods = _section(answer, "periods")
    assert all(lord in periods for lord in ("Moon (your 5th lord)", "Jupiter"))


def test_a_year_question_lists_the_running_periods() -> None:
    answer = _answer("fifth_in_11", YEAR)
    assert _section(answer, "direct").startswith(f"{NO_TIMING_RULE} In 2027,")
    assert "dasha" in _kinds(answer)


def test_a_comparison_is_not_ranked() -> None:
    answer = _answer("fifth_in_11", "Which is better for children, 2027 or 2028?")
    assert "the years are not ranked" in _section(answer, "direct")


@pytest.mark.parametrize(
    ("question", "scope"),
    [
        ("Will my children be healthy?", "health"),
        ("Is there a santan dosh in my chart?", "fatalistic"),
    ],
)
def test_out_of_scope_children_questions_get_one_line(question: str, scope: str) -> None:
    answer = _answer("fifth_in_11", question, provisional=True)
    assert _kinds(answer) == ["direct"]
    assert answer.answer == OUT_OF_SCOPE_REPLIES[scope]
    assert answer.provisional_interpretations == ()


@pytest.mark.parametrize(
    ("question", "scope"),
    [("When will I have a son?", "child_sex"), ("Will I get pregnant?", "medical")],
)
def test_the_hard_guards_still_answer_first(question: str, scope: str) -> None:
    answer = _answer("fifth_in_11", question, provisional=True)
    replies = {key.value: value for key, value in CHILD_SCOPE_REPLIES.items()}
    assert answer.answer == replies[scope]
    assert answer.provisional_interpretations == () and answer.evidence == ()


@pytest.mark.parametrize("name", list(PROFILES))
@pytest.mark.parametrize("question", [OUTLOOK, TIMING, YEAR])
def test_children_answers_show_no_other_domain_term_and_pass_every_guard(
    name: str, question: str
) -> None:
    answer = _answer(name, question, provisional=True)
    admitted = [item.reviewed_statement for item in answer.evidence]
    texts = [answer.answer, *(section.text for section in answer.consultation_sections)]
    for statement in admitted:  # admitted text is quoted verbatim, not a term list
        texts = [text.replace(statement, " ") for text in texts]
    for item in answer.provisional_interpretations:
        assert item.domain == "children"
        texts += [item.statement, item.placement_explanation]
        if item.kind == "signification":
            assert item.rule_id in {term.term_id for term in CHILDREN_SIGNIFICATIONS}
    for text in texts:
        assert child_wording_violation(text) is None, text
    for term in ("learning", "intellect", "wealth", "spouse", "house (kāraka)", "adviser"):
        assert all(term not in text for text in texts if "Provisional" not in text), term
    assert not re.search(
        r"\b(?:on|by|before|after)\s+\d{1,2}\s+[A-Z][a-z]{2}\s+\d{4}\b", " ".join(texts)
    )


def test_the_flag_off_shows_no_provisional_item() -> None:
    assert _answer("fifth_in_9", OUTLOOK).provisional_interpretations == ()


# --- B: provisional Children rules, all 12 placements -----------------------------------------


SHOWN = {9, 10}
HELD = {2, 5, 6, 8, 12}
NOT_DRAFTED_HOUSES = {1, 3, 4, 7, 11}


def test_v6_adds_children_rules_only() -> None:
    assert ACTIVE_PROVISIONAL_CORPUS is PROVISIONAL_CORPUS_V6
    assert PROVISIONAL_CORPUS_V6.release_id == "jyotish.provisional@v6"
    v5 = {rule.rule_id: rule for rule in PROVISIONAL_CORPUS_V5.rules}
    added = [rule for rule in PROVISIONAL_CORPUS_V6.rules if rule.rule_id not in v5]
    assert sorted(rule.rule_id for rule in added) == sorted(r.rule_id for r in CHILDREN_RULES)
    assert all(rule in PROVISIONAL_CORPUS_V6.rules for rule in v5.values())


def test_all_twelve_fifth_lord_placements_are_accounted_for() -> None:
    by_house: dict[int, str] = {}
    for rule in CHILDREN_RULES:
        house = rule.rule.condition.expected_value
        assert isinstance(house, int)
        by_house[house] = rule.wording
        assert rule.domain is JyotishDomain.CHILDREN
        assert rule.fact_dependencies == ("jyotish.d1.house_lord.5.placement_house",)
        assert PUTRA_CONVENTION in rule.justification.conventions
    assert {house for house, wording in by_house.items() if wording == "shown"} == SHOWN
    assert {house for house, wording in by_house.items() if wording == "held"} == HELD
    assert set(range(1, 13)) - set(by_house) == NOT_DRAFTED_HOUSES
    notes = " ".join(NOT_DRAFTED["children"])
    for phrase in ("1st or 3rd house", "4th house", "7th house", "11th house"):
        assert f"Fifth lord in the {phrase}" in notes
    assert "Sitting 1 item 16" in notes


@pytest.mark.parametrize("house", range(1, 13))
def test_each_placement_shows_as_recorded(house: int) -> None:
    facts = {"jyotish.d1.house_lord.5.placement_house": house}
    items = provisional_interpretations(ACTIVE_PROVISIONAL_CORPUS, facts, "children")
    if house in NOT_DRAFTED_HOUSES:
        assert items == ()
        return
    (item,) = items
    # Every Children source verse is held in the app (death, number, sex epithet).
    assert item.justification.original_text == SOURCE_HELD_NOTICE
    assert item.justification.original_text_held
    assert item.justification.draft_translation is None
    texts = [
        item.statement,
        item.placement_explanation,
        item.justification.interpretive_reasoning,
        *item.justification.conventions,
        item.justification.transcription_notes or "",
        item.justification.held_reason or "",
    ]
    assert CHILD_HELD_NOTICE not in texts  # nothing the guard had to hold in the record text
    for text in texts:
        assert child_wording_violation(text) is None, text
    if house in HELD:
        assert item.wording_held and item.statement == HELD_STATEMENT
        assert item.badge == "Provisional · low confidence"
    else:
        assert not item.wording_held
        assert item.badge == "Provisional · medium confidence"
        assert item.statement == (
            f"With the D1 fifth-house lord in the {['ninth', 'tenth'][house - 9]} house, the "
            f"text compares {PUTRA_GLOSS} to a king (पुत्रो भूपसमो). It does not say whether, "
            "when or how many children there will be."
        )
        assert children_domain_violation(item.statement) is None


# --- B: provisional significations ---------------------------------------------------------


def test_signification_v5_adds_children_and_education_terms_only() -> None:
    corpus = ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS
    assert corpus.release_id == "jyotish.provisional.signification@v5"
    assert corpus.terms[: len(PROVISIONAL_SIGNIFICATION_CORPUS_V4.terms)] == (
        PROVISIONAL_SIGNIFICATION_CORPUS_V4.terms
    )
    added = corpus.terms[len(PROVISIONAL_SIGNIFICATION_CORPUS_V4.terms) :]
    assert added == (*CHILDREN_SIGNIFICATIONS, *EDUCATION_SIGNIFICATIONS)
    for term in CHILDREN_SIGNIFICATIONS:
        assert [tag.domain for tag in term.tags] == [JyotishDomain.CHILDREN]
        assert term.sanskrit == "पुत्र" and PUTRA_GLOSS in term.display
        assert PUTRA_GLOSS in term.statement
        assert PUTRA_CONVENTION in term.justification.conventions
    for term in EDUCATION_SIGNIFICATIONS:
        assert [tag.domain for tag in term.tags] == [JyotishDomain.EDUCATION]
        assert term.subject == "5" and term.display in {"learning", "intellect"}
    assert FIFTH_HOUSE_CHILDREN.subject == "5" and JUPITER_KARAKA_CHILDREN.subject == "jupiter"


def test_education_answers_show_the_fifth_house_learning_terms() -> None:
    answer = _answer("fifth_in_11", "What does my chart say about education?", provisional=True)
    shown = {item.rule_id for item in answer.provisional_interpretations}
    assert {term.term_id for term in EDUCATION_SIGNIFICATIONS} <= shown
    assert not {term.term_id for term in CHILDREN_SIGNIFICATIONS} & shown
    facts = {
        "jyotish.d1.house.5.sign": "cancer",
        "jyotish.d1.house.5.lord": "moon",
        "jyotish.d1.planet.jupiter.placement_house": 9,
    }
    children = provisional_signification_items(
        ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS, facts, "children"
    )
    assert [item.rule_id for item in children] == [t.term_id for t in CHILDREN_SIGNIFICATIONS]
    assert all(not item.justification.original_text_held for item in children)
