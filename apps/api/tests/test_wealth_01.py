"""NEXT-WEALTH-01: carry-overs (A1–A4), the domain template, provisional Wealth.

All births are synthetic (lat/long 0, UTC); none describes a real person.
"""

import json
import re
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from test_career_answer_wording import _ask, _birth

from astrologer.application.analyze import DeterministicAnalysisRequest
from astrologer.application.domain_pipeline import CONTINUES
from astrologer.application.domains import CAREER_DOMAIN, DOMAIN_CONFIGS, domain_config
from astrologer.application.lord_dignity import DIGNITY_PREFIX
from astrologer.application.marriage import MARRIAGE_DOMAIN
from astrologer.application.wealth import (
    LIMIT_OUTLOOK,
    LIMIT_TIMING,
    NO_TIMING_RULE,
    OUT_OF_SCOPE_REPLIES,
    THEMES_PENDING,
    WEALTH_DOMAIN,
)
from astrologer.common.config import Settings
from astrologer.composition.models import DetailedComposedAnswer
from astrologer.composition.wealth_guard import wealth_wording_violation
from astrologer.knowledge import ACTIVE_PRODUCTION_RELEASE
from astrologer.knowledge.models import JyotishDomain
from astrologer.knowledge.provisional import HELD_STATEMENT
from astrologer.knowledge.provisional_pack_v3 import (
    ACTIVE_PROVISIONAL_CORPUS,
    NOT_DRAFTED,
    RULE_2_IN_6_WEALTH,
    RULE_2_IN_12_WEALTH,
    WEALTH_RULES,
)
from astrologer.knowledge.provisional_signification import (
    ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS,
    SECOND_HOUSE_FAMILY_V2,
)
from astrologer.knowledge.signification import admit_entries
from astrologer.knowledge.signification_admit02_v1 import ACTIVE_SIGNIFICATION_CORPUS
from astrologer.knowledge.signification_tags import (
    ACTIVE_SIGNIFICATION_TAG_SET,
    UNTAGGED_CAREER_CORPORA,
    domain_view,
)
from astrologer.main import create_app
from astrologer.questions.models import QuestionDomain

_AS_OF = datetime(2026, 1, 1, tzinfo=UTC)
PROFILES = {
    "no_reviewed": _birth("1978-01-01", "12:00:00"),  # 2nd lord Mars in the 5th
    "reviewed": _birth("1960-01-15", "12:00:00"),  # 11th lord in the 9th: Wealth + General
    "jupiter_lord": _birth("1980-06-15", "00:00:00"),  # Jupiter rules the 2nd and 11th
    "second_in_6": _birth("1970-07-15", "06:00:00"),  # v.13, held
    "second_in_12": _birth("1970-10-15", "06:00:00"),  # v.18, held
}
OUTLOOK = "What does my chart say about wealth?"
TIMING = "When will my wealth grow?"
YEAR = "wealth in 2027?"
COMPARE = "Which is better for wealth, 2027 or 2028?"
INVEST = "Should I invest my wealth in stocks?"
AMOUNT = "How much wealth will I have?"
FATAL = "Will I lose my wealth?"
QUESTIONS = (OUTLOOK, TIMING, YEAR, COMPARE, INVEST, AMOUNT, FATAL)
REVIEWED_WEALTH_RULES = {
    "bphs.d1.house_lord.11.in_1.wealth.v1",
    "bphs.d1.house_lord.11.in_2_or_5.wealth.v1",
    "bphs.d1.house_lord.11.in_9_or_10.wealth.v1",
    "bphs.d1.house_lord.5.in_11.wealth.v1",
}
GENERAL_11_IN_9_OR_10 = "bphs.d1.house_lord.11.in_9_or_10.v1"


def _answer(birth: object, question: str) -> DetailedComposedAnswer:
    result = _ask().answer(
        DeterministicAnalysisRequest(birth_input=birth, as_of=_AS_OF, question=question)  # type: ignore[arg-type]
    )
    (answer,) = result.answers
    return answer


@pytest.fixture(scope="module")
def answers() -> dict[tuple[str, str], DetailedComposedAnswer]:
    return {
        (name, question): _answer(birth, question)
        for name, birth in PROFILES.items()
        for question in QUESTIONS
    }


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


def _kinds(answer: DetailedComposedAnswer) -> list[str]:
    return [section.kind for section in answer.consultation_sections]


# --- A1: dignity prefix ----------------------------------------------------------------------


def test_a1_dignity_prefix_is_short_in_every_domain(answers: dict) -> None:  # type: ignore[type-arg]
    assert DIGNITY_PREFIX == "Calculated fact (sign dignity)"
    text = answers[("no_reviewed", OUTLOOK)].answer
    assert f"{DIGNITY_PREFIX}: your 2nd lord, Mars, is in its debilitation sign." in text
    assert "modifier only" not in text
    career = _answer(PROFILES["no_reviewed"], "How is my career in 2027?")
    assert "modifier only" not in json.dumps(career.model_dump(mode="json"))


# --- A3: untagged corpora --------------------------------------------------------------------


def test_a3_an_untagged_non_legacy_corpus_shows_in_no_domain() -> None:
    entry = ACTIVE_SIGNIFICATION_CORPUS.entries[0]
    other = admit_entries("other.signification", "v1", (entry,))
    assert other.version not in UNTAGGED_CAREER_CORPORA
    assert other.version not in ACTIVE_SIGNIFICATION_TAG_SET.covers_corpora
    for domain in JyotishDomain:
        assert domain_view(other, domain, ACTIVE_SIGNIFICATION_TAG_SET).entries == (), domain


def test_a3_the_named_legacy_and_test_corpora_stay_career_only() -> None:
    assert UNTAGGED_CAREER_CORPORA == {
        "jyotish.signification.production@v0-empty",
        "fixture.signification@v1",
    }
    entry = ACTIVE_SIGNIFICATION_CORPUS.entries[0]
    fixture = admit_entries("fixture.signification", "v1", (entry,))
    career = domain_view(fixture, JyotishDomain.CAREER, ACTIVE_SIGNIFICATION_TAG_SET)
    assert career is fixture
    for domain in (JyotishDomain.MARRIAGE, JyotishDomain.WEALTH):
        assert domain_view(fixture, domain, ACTIVE_SIGNIFICATION_TAG_SET).entries == ()


# --- A4: periods past the window -------------------------------------------------------------


def test_a4_only_periods_ending_after_the_window_are_marked(answers: dict) -> None:  # type: ignore[type-arg]
    periods = next(
        s for s in answers[("no_reviewed", TIMING)].consultation_sections if s.kind == "periods"
    )
    lines = [sentence.text for sentence in periods.synthesis_sentences]
    marked = [line for line in lines if CONTINUES in line]
    assert marked == [
        "Saturn (your 11th lord) Mahadasha: 18 Mar 2031 to 17 Mar 2050 " + CONTINUES + "."
    ]
    # A period that started before the window but ends inside it is not marked.
    assert "Jupiter Mahadasha: 18 Mar 2015 to 18 Mar 2031." in lines


# --- B: the domain template ------------------------------------------------------------------


def test_domain_registry() -> None:
    assert set(DOMAIN_CONFIGS) == {
        QuestionDomain.CAREER,
        QuestionDomain.MARRIAGE,
        QuestionDomain.WEALTH,
        QuestionDomain.PROPERTY,  # NEXT-PROPERTY-01
        QuestionDomain.CHILDREN,  # NEXT-CHILDREN-01
    }
    assert CAREER_DOMAIN.composer == "career" and CAREER_DOMAIN.houses == (10,)
    assert MARRIAGE_DOMAIN.houses == (7,) and MARRIAGE_DOMAIN.karakas == ("venus",)
    assert WEALTH_DOMAIN.houses == (2, 11) and WEALTH_DOMAIN.karakas == ("jupiter",)
    assert WEALTH_DOMAIN.tag_domain is JyotishDomain.WEALTH
    assert WEALTH_DOMAIN.divisional is None and MARRIAGE_DOMAIN.divisional is not None
    assert domain_config(QuestionDomain.EDUCATION) is None


# --- C: Wealth answers -----------------------------------------------------------------------


def test_outlook_and_timing_layout(answers: dict) -> None:  # type: ignore[type-arg]
    outlook = answers[("no_reviewed", OUTLOOK)]
    assert _kinds(outlook) == ["direct", "chart_factors", "limit"]
    assert outlook.consultation_sections[-1].text == LIMIT_OUTLOOK
    timing = answers[("no_reviewed", TIMING)]
    assert _kinds(timing) == [
        "direct",
        "periods",
        "period_themes",
        "chart_factors",
        "timing_status",
        "limit",
    ]
    assert timing.answer.startswith(NO_TIMING_RULE)
    assert timing.consultation_sections[-1].text == LIMIT_TIMING
    themes = next(s.text for s in timing.consultation_sections if s.kind == "period_themes")
    assert themes.endswith(THEMES_PENDING) and "reviewed themes" not in themes
    assert "not ranked" in answers[("no_reviewed", COMPARE)].answer
    for answer in (outlook, timing):
        assert answer.timing_answered is False and answer.limitations == ()


def test_a_lord_ruling_both_wealth_houses_is_named_once(answers: dict) -> None:  # type: ignore[type-arg]
    direct = answers[("jupiter_lord", OUTLOOK)].consultation_sections[0].text
    assert direct.endswith(": your 2nd and 11th lord, Jupiter, is in the 7th house.")
    factors = next(
        s
        for s in answers[("jupiter_lord", OUTLOOK)].consultation_sections
        if s.kind == "chart_factors"
    )
    lines = [sentence.text for sentence in factors.synthesis_sentences]
    assert lines[0] == "Your 2nd and 11th lord is Jupiter, placed in the 7th house."
    assert sum(line.startswith(DIGNITY_PREFIX) for line in lines) == 1


def test_reviewed_rules_in_wealth_are_wealth_rules_confirmed_in_sittings_1_2(
    answers: dict,  # type: ignore[type-arg]
) -> None:
    # Condition 1: only rules whose domain is Wealth (Sitting 1 items 8–11, confirmed,
    # interpretation records ``…wealth.interpretation.admit02``).  The General 11th-lord rule
    # matches the same chart but the selector is exact-domain, so it never appears.
    envelopes = {e.rule.rule_id: e for e in ACTIVE_PRODUCTION_RELEASE.envelopes}
    for rule_id in REVIEWED_WEALTH_RULES:
        assert envelopes[rule_id].rule.domain == "wealth"
        assert envelopes[rule_id].interpretation_id.endswith(".wealth.interpretation.admit02")
    assert envelopes[GENERAL_11_IN_9_OR_10].rule.domain == "general"
    reviewed = answers[("reviewed", OUTLOOK)]
    assert {item.domain for item in reviewed.evidence} == {"wealth"}
    natal = next(s for s in reviewed.consultation_sections if s.kind == "natal")
    for item in reviewed.evidence:
        assert item.reviewed_statement in natal.text  # quoted verbatim
    statements = {
        i.interpretation_id: i.statement for i in ACTIVE_PRODUCTION_RELEASE.registry.interpretations
    }
    general = statements[envelopes[GENERAL_11_IN_9_OR_10].interpretation_id]
    for answer in answers.values():
        assert general not in answer.answer
        assert all(item.domain == "wealth" for item in answer.evidence)
    assert reviewed.corpus_limitation is False
    assert answers[("no_reviewed", OUTLOOK)].corpus_limitation is True


def _career_terms() -> set[str]:
    # Every reviewed (Career-tagged) term display, except the two words the Wealth answer
    # uses in its own template ("wealth", "gain"); those are matched as theme lines below.
    displays = {
        term.display for entry in ACTIVE_SIGNIFICATION_CORPUS.entries for term in entry.terms
    }
    return displays - {"wealth", "gain"}


def test_no_career_or_marriage_term_in_any_wealth_answer(answers: dict) -> None:  # type: ignore[type-arg]
    career = _career_terms()
    assert {"trade or business", "adviser or counsellor"} <= career
    marriage = {"spouse", "spouse (kāraka)", "family", "marriage"}
    for key, answer in answers.items():
        text = answer.answer
        for term in career | marriage:
            assert not re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE), (key, term)
        assert "reviewed themes" not in text, key
        for section in answer.consultation_sections:
            for sentence in section.synthesis_sentences:
                assert not any(r.startswith("bphs.signification.") for r in sentence.rule_ids)
    # Provisional items (toggle on): Wealth-tagged terms only, no Career or Marriage term.
    on = _consult(TIMING, PROFILES["no_reviewed"], True)
    for item in on["provisional_interpretations"]:
        assert item["domain"] == "wealth"
        for term in career | {"spouse", "marriage"}:
            assert not re.search(rf"\b{re.escape(term)}\b", item["statement"], re.IGNORECASE)


@pytest.mark.parametrize(
    ("question", "scope"), [(INVEST, "investment"), (AMOUNT, "amount"), (FATAL, "fatalistic")]
)
def test_out_of_scope_replies(question: str, scope: str, answers: dict) -> None:  # type: ignore[type-arg]
    answer = answers[("no_reviewed", question)]
    assert _kinds(answer) == ["direct"]
    assert answer.answer == OUT_OF_SCOPE_REPLIES[scope]
    assert wealth_wording_violation(answer.answer) is None
    on = _consult(question, PROFILES["no_reviewed"], True)
    assert on["provisional_interpretations"] == []


def test_investment_reply_names_a_financial_adviser() -> None:
    assert "financial adviser" in OUT_OF_SCOPE_REPLIES["investment"]
    assert "amounts of money" in OUT_OF_SCOPE_REPLIES["amount"]


def test_every_wealth_section_passes_the_wealth_guard(answers: dict) -> None:  # type: ignore[type-arg]
    for key, answer in answers.items():
        admitted = [item.reviewed_statement for item in answer.evidence]
        for section in answer.consultation_sections:
            assert wealth_wording_violation(section.text, admitted) is None, (key, section.kind)


# --- C: provisional Wealth records -----------------------------------------------------------


def test_the_guard_blocks_the_text_of_v13_and_v18() -> None:
    for rule in (RULE_2_IN_6_WEALTH, RULE_2_IN_12_WEALTH):
        assert rule.wording == "held" and rule.statement == HELD_STATEMENT
        assert wealth_wording_violation(rule.justification.draft_translation) is not None
        assert rule.held_reason is not None and "poverty or loss" in rule.held_reason
    assert wealth_wording_violation("the native is without wealth (धनवर्जितः)") is not None
    assert wealth_wording_violation("there is a loss of wealth through an enemy") is not None


@pytest.mark.parametrize(
    ("name", "rule"), [("second_in_6", RULE_2_IN_6_WEALTH), ("second_in_12", RULE_2_IN_12_WEALTH)]
)
def test_held_verses_show_only_the_held_notice(name: str, rule: object) -> None:
    on = _consult(OUTLOOK, PROFILES[name], True)
    (item,) = [i for i in on["provisional_interpretations"] if i["rule_id"] == rule.rule_id]  # type: ignore[attr-defined]
    assert item["statement"] == HELD_STATEMENT and item["wording_held"] is True
    assert item["justification"]["draft_translation"] is None
    text = json.dumps(on, ensure_ascii=False)
    assert rule.justification.draft_translation not in text  # type: ignore[attr-defined]


def test_second_lord_verses_cover_all_twelve_placements() -> None:
    # Condition 2: 12 placements = 7 shown + 2 held (v.13: 6th, v.18: 12th) + 3 not drafted
    # (v.11: 3rd and 4th, no wealth clause; v.14: 7th, no wealth clause).
    houses = {
        int(rule.rule.rule_id.split("equals_")[1].split(".")[0]): rule for rule in WEALTH_RULES
    }
    shown = {h for h, r in houses.items() if r.wording == "shown"}
    held = {h for h, r in houses.items() if r.wording == "held"}
    assert shown == {1, 2, 5, 8, 9, 10, 11}
    assert held == {6, 12}
    notes = " ".join(NOT_DRAFTED["wealth"])
    assert "3rd or the 4th house: verse 11" in notes and "7th house: verse 14" in notes
    assert shown | held | {3, 4, 7} == set(range(1, 13))
    for rule in WEALTH_RULES:
        assert rule in ACTIVE_PROVISIONAL_CORPUS.rules
        if rule.wording == "shown":
            assert rule.translation_held_reason is not None
            assert wealth_wording_violation(rule.statement) is None


def test_provisional_wealth_significations() -> None:
    wealth = ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS.for_domain("wealth")
    assert {(t.subject, t.sanskrit, t.justification.confidence.value) for t in wealth} == {
        ("2", "धन", "high"),
        ("2", "कुटुम्ब", "low"),
        ("11", "लाभ", "high"),
        ("jupiter", "धन", "high"),
    }
    assert SECOND_HOUSE_FAMILY_V2 not in ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS.for_domain(
        "marriage"
    )
    for term in wealth:
        j = term.justification
        assert "PDF p." in j.locator and j.transcription_notes and term.translation_held_reason
        assert term.sanskrit in j.original_text and term.sanskrit in term.statement


def test_provisional_only_with_the_flag_and_reviewed_parts_unchanged() -> None:
    off = _consult(OUTLOOK, PROFILES["reviewed"], False)
    on = _consult(OUTLOOK, PROFILES["reviewed"], True)
    assert off["provisional_interpretations"] == []
    assert on["provisional_interpretations"]
    strip = {k: v for k, v in on.items() if k != "provisional_interpretations"}
    assert strip == {k: v for k, v in off.items() if k != "provisional_interpretations"}
    for item in on["provisional_interpretations"]:
        assert item["badge"].startswith("Provisional · ")
        assert item["justification"]["draft_translation"] is None  # held for every Wealth item
        assert item["justification"]["held_reason"]
