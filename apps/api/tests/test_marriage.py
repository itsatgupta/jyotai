"""NEXT-MARRIAGE-01: marriage answers, the provisional 7th-lord rules and the wording guard.

Updated for NEXT-MARRIAGE-02: no reviewed signification term is tagged Marriage, so Period
themes list the periods only with the pending line; every answer has a D9 factors section.

All births are synthetic (lat/long 0, UTC); none describes a real person.
"""

import json
import re
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from test_career_answer_wording import _ask, _birth
from test_tone import _SENTENCES, NON_PREDICTION

from astrologer.application.analyze import DeterministicAnalysisRequest
from astrologer.application.answer import _d1_fact_values
from astrologer.application.marriage import (
    LIMIT_OUTLOOK,
    LIMIT_TIMING,
    LIMIT_TIMING_PERIODS_ONLY,
    MARRIAGE_TIMING_HORIZON_YEARS,
    NO_RANKING,
    NO_TIMING_RULE,
    OUT_OF_SCOPE_REPLIES,
    THEMES_PENDING,
    TIMING_STATUS,
    TIMING_STATUS_PERIODS,
    MarriageScope,
    marriage_scope,
)
from astrologer.application.provisional import provisional_interpretations
from astrologer.common.config import Settings
from astrologer.composition.comparison_guard import ranking_violation
from astrologer.composition.evaluative_guard import evaluative_violation
from astrologer.composition.marriage_guard import marriage_wording_violation
from astrologer.composition.models import DetailedComposedAnswer
from astrologer.knowledge.models import JyotishDomain
from astrologer.knowledge.provisional import HELD_STATEMENT, ProvisionalRule
from astrologer.knowledge.provisional_pack_v1 import PROVISIONAL_CORPUS_V1
from astrologer.knowledge.provisional_pack_v2 import (
    ACTIVE_PROVISIONAL_CORPUS,
    MARRIAGE_RULES,
    NOT_DRAFTED,
    RULE_7_IN_12_MARRIAGE,
)
from astrologer.knowledge.signification_admit02_v1 import (
    ACTIVE_SIGNIFICATION_CORPUS,
    PERIOD_THEMES_CLOSING_V2,
)
from astrologer.main import create_app
from astrologer.questions import QuestionIntentRouter, QuestionRequest
from astrologer.questions.models import QuestionDomain

_AS_OF = datetime(2026, 1, 1, tzinfo=UTC)
# One synthetic birth per house of the D1 7th lord (found by search; lat/long 0, UTC).
BY_SEVENTH_LORD_HOUSE = {
    1: _birth("1970-01-15", "06:00:00"),
    2: _birth("1972-04-15", "06:00:00"),  # Venus is the 7th lord
    3: _birth("1971-04-15", "18:00:00"),
    4: _birth("1971-07-15", "12:00:00"),
    5: _birth("1970-01-15", "18:00:00"),
    6: _birth("1971-01-15", "18:00:00"),
    7: _birth("1971-10-15", "18:00:00"),
    8: _birth("1970-04-15", "18:00:00"),
    9: _birth("1970-01-15", "12:00:00"),
    10: _birth("1970-07-15", "12:00:00"),
    11: _birth("1971-04-15", "06:00:00"),
    12: _birth("1970-10-15", "06:00:00"),
}
P_MATCH = _birth("1978-01-01", "12:00:00")  # benchmark profile: 7th lord Mercury in the 9th
OUTLOOK = "What does my chart say about marriage?"
TIMING = "When will I get married?"
YEAR = "marriage in 2027?"
QUESTIONS = (
    OUTLOOK,
    TIMING,
    YEAR,
    "Will I get married in 2038?",
    "When will my wedding be?",
    "Which is better for marriage, 2027 or 2028?",
    "What does my D9 say about marriage?",
)
OUT_OF_SCOPE = {
    "Is my kundli compatible with my partner's chart?": MarriageScope.COMPATIBILITY,
    "Can you do guna milan for us?": MarriageScope.COMPATIBILITY,
    "Do I have mangal dosha?": MarriageScope.MANGAL,
    "Am I manglik for marriage?": MarriageScope.MANGAL,
    "Will I get divorced?": MarriageScope.SEPARATION,
    "Will my marriage end in separation?": MarriageScope.SEPARATION,
    "Will my marriage be delayed?": MarriageScope.FATALISTIC,
    "Will I ever get married?": MarriageScope.FATALISTIC,
    "Is there denial of marriage in my chart?": MarriageScope.FATALISTIC,
    "Will I have an unhappy marriage?": MarriageScope.FATALISTIC,
}


def _answer(birth: object, question: str) -> DetailedComposedAnswer:
    result = _ask().answer(
        DeterministicAnalysisRequest(
            birth_input=birth,  # type: ignore[arg-type]
            as_of=_AS_OF,
            question=question,
        )
    )
    (answer,) = result.answers
    return answer


def _kinds(answer: DetailedComposedAnswer) -> list[str]:
    return [section.kind for section in answer.consultation_sections]


def _section(answer: DetailedComposedAnswer, kind: str) -> str:
    return next(s.text for s in answer.consultation_sections if s.kind == kind)


@pytest.fixture(scope="module")
def answers() -> dict[tuple[int, str], DetailedComposedAnswer]:
    return {
        (house, question): _answer(birth, question)
        for house, birth in BY_SEVENTH_LORD_HOUSE.items()
        for question in QUESTIONS
    }


# --- Routing -------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("question", "requires_timing", "year"),
    [
        (OUTLOOK, False, None),
        (TIMING, True, None),
        (YEAR, True, 2027),
        ("When will my wedding be?", True, None),
        ("What does my chart say about my future spouse?", False, None),
        ("Tell me about my husband", False, None),
        ("Do I have mangal dosha?", False, None),
        ("Can you do guna milan for us?", False, None),
    ],
)
def test_marriage_questions_route_to_the_marriage_domain(
    question: str, requires_timing: bool, year: int | None
) -> None:
    routed = QuestionIntentRouter().route(
        QuestionRequest(question=question, reference_instant=_AS_OF)
    )
    (intent,) = routed.intents
    assert intent.domain is QuestionDomain.MARRIAGE
    assert intent.requires_timing is requires_timing
    if year is not None:
        assert intent.time_range is not None and intent.time_range.start_date.year == year


@pytest.mark.parametrize(("question", "scope"), sorted(OUT_OF_SCOPE.items()))
def test_out_of_scope_questions_are_classified(question: str, scope: MarriageScope) -> None:
    (intent,) = (
        QuestionIntentRouter()
        .route(QuestionRequest(question=question, reference_instant=_AS_OF))
        .intents
    )
    assert marriage_scope(question, intent) is scope


def test_in_scope_questions_are_outlook_or_timing() -> None:
    router = QuestionIntentRouter()
    for question, scope in (
        (OUTLOOK, MarriageScope.OUTLOOK),
        (TIMING, MarriageScope.TIMING),
        (YEAR, MarriageScope.TIMING),
    ):
        (intent,) = router.route(
            QuestionRequest(question=question, reference_instant=_AS_OF)
        ).intents
        assert marriage_scope(question, intent) is scope


# --- Answers -------------------------------------------------------------------------------


def test_outlook_states_calculated_factors_only(answers: dict) -> None:  # type: ignore[type-arg]
    answer = answers[(9, OUTLOOK)]
    assert _kinds(answer) == ["direct", "chart_factors", "d9_factors", "limit"]
    facts = _d1_fact_values(answer_chart(BY_SEVENTH_LORD_HOUSE[9]))
    seventh = str(facts["jyotish.d1.house.7.lord"]).title()
    factors = next(s for s in answer.consultation_sections if s.kind == "chart_factors")
    texts = [sentence.text for sentence in factors.synthesis_sentences]
    assert texts[0] == f"Your 7th lord is {seventh}, placed in the 9th house."
    venus = [text for text in texts if text.startswith("Calculated fact") and "Venus" in text]
    assert len(venus) == 1 and "modifier only" in venus[0]
    assert all(sentence.fact_ids for sentence in factors.synthesis_sentences)
    assert answer.consultation_sections[-1].text == LIMIT_OUTLOOK
    assert answer.corpus_limitation and answer.claim_ledger is None


def test_venus_as_seventh_lord_is_named_once_with_one_dignity_line(answers: dict) -> None:  # type: ignore[type-arg]
    factors = next(
        s for s in answers[(2, OUTLOOK)].consultation_sections if s.kind == "chart_factors"
    )
    texts = [sentence.text for sentence in factors.synthesis_sentences]
    assert texts[0] == "Your 7th lord is Venus, placed in the 2nd house."
    assert sum(text.startswith("Calculated fact") for text in texts) == 1


def answer_chart(birth: object):  # type: ignore[no-untyped-def]
    from astrologer.application.context import (
        DeterministicAstrologyContextService,
        DeterministicContextRequest,
    )
    from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider

    return (
        DeterministicAstrologyContextService(SwissEphemerisProvider())
        .build(DeterministicContextRequest(birth_input=birth, as_of=_AS_OF))  # type: ignore[arg-type]
        .d1
    )


def _expected_periods(birth: object, start: datetime, end: datetime) -> list[tuple[str, str, str]]:
    """The 7th lord's and Venus's MD/AD overlapping [start, end), from the Dasha engine."""
    chart = answer_chart(birth)
    seventh = str(_d1_fact_values(chart)["jyotish.d1.house.7.lord"])
    targets = {seventh, "venus"}
    timeline = _ask().dasha_timeline(
        DeterministicAnalysisRequest(birth_input=birth, as_of=_AS_OF, question=TIMING),  # type: ignore[arg-type]
        end,
    )
    found: list[tuple[str, str, str]] = []
    for major in timeline.mahadashas:
        if major.end <= start or major.start >= end:
            continue
        if major.lord.value in targets:
            found.append(("Mahadasha", major.lord.value, major.start.date().isoformat()))
        for minor in major.antardashas:
            if minor.end > start and minor.start < end and minor.lord.value in targets:
                found.append(("Antardasha", minor.lord.value, minor.start.date().isoformat()))
    return found


def _listed(answer: DetailedComposedAnswer) -> list[str]:
    section = next((s for s in answer.consultation_sections if s.kind == "periods"), None)
    return [sentence.text for sentence in section.synthesis_sentences] if section else []


@pytest.mark.parametrize("house", sorted(BY_SEVENTH_LORD_HOUSE))
def test_timing_lists_exactly_the_seventh_lord_and_venus_periods(answers: dict, house: int) -> None:  # type: ignore[type-arg]
    birth = BY_SEVENTH_LORD_HOUSE[house]
    end = _AS_OF + timedelta(days=365.25 * MARRIAGE_TIMING_HORIZON_YEARS)
    expected = _expected_periods(birth, _AS_OF, end)
    listed = _listed(answers[(house, TIMING)])
    assert len(listed) == len(expected)
    for (role, lord, start), text in zip(expected, listed, strict=True):
        assert text.startswith(lord.title()) and role in text
        day = datetime.fromisoformat(start)
        assert f"{day.day} {day.strftime('%b %Y')} to " in text


@pytest.mark.parametrize("house", sorted(BY_SEVENTH_LORD_HOUSE))
def test_year_answer_lists_only_periods_overlapping_the_year(answers: dict, house: int) -> None:  # type: ignore[type-arg]
    birth = BY_SEVENTH_LORD_HOUSE[house]
    expected = _expected_periods(
        birth, datetime(2027, 1, 1, tzinfo=UTC), datetime(2028, 1, 1, tzinfo=UTC)
    )
    answer = answers[(house, YEAR)]
    assert len(_listed(answer)) == len(expected)
    direct = _section(answer, "direct")
    assert direct.startswith(NO_TIMING_RULE)
    if expected:
        assert direct.endswith("are listed below.")
        assert "reviewed Period themes" not in direct
        assert "period_themes" in _kinds(answer)
        assert _section(answer, "timing_status") == TIMING_STATUS_PERIODS
    else:
        assert "Mahadasha or Antardasha period" in direct
        assert _section(answer, "timing_status") == TIMING_STATUS
    # Every MD/AD running in the year is in Chart details ("dasha").
    assert "dasha" in _kinds(answer)
    assert answer.consultation_sections[-1].text == LIMIT_TIMING_PERIODS_ONLY


def test_period_themes_list_the_periods_only_with_the_pending_line(answers: dict) -> None:  # type: ignore[type-arg]
    # NEXT-MARRIAGE-02: no reviewed term is tagged Marriage, so no Career term is shown.
    answer = answers[(9, TIMING)]
    themes = next(s for s in answer.consultation_sections if s.kind == "period_themes")
    lines = themes.synthesis_sentences
    assert lines[-1].text == THEMES_PENDING
    assert PERIOD_THEMES_CLOSING_V2 not in answer.answer
    seventh_line = next(line for line in lines[:-1] if "(your 7th lord)" in line.text)
    assert "house" not in seventh_line.text and "reviewed themes" not in seventh_line.text
    for line in lines[:-1]:
        assert re.fullmatch(r"[A-Z][a-z]+( \(your 7th lord\))? [A-Za-z ()]+\.", line.text)
    for term in (t.display for e in _entries() for t in e.terms):
        assert term not in themes.text
    reviewed = {item.rule_id for item in answer.rule_review_types}
    assert not any(rule.startswith("bphs.signification.") for rule in reviewed)


def test_no_date_is_predicted_and_no_year_is_ranked(answers: dict) -> None:  # type: ignore[type-arg]
    compared = answers[(9, "Which is better for marriage, 2027 or 2028?")]
    assert NO_RANKING in _section(compared, "direct")
    for answer in answers.values():
        # The fixed closing ("… whether or when a marriage will happen.") is the only place
        # such words may appear.
        text = (
            answer.answer.replace(LIMIT_OUTLOOK, "")
            .replace(LIMIT_TIMING, "")
            .replace(LIMIT_TIMING_PERIODS_ONLY, "")
        )
        assert not re.search(r"\byou will (?:get )?marr", text, re.I)
        assert not re.search(
            r"\b(?:marriage|wedding) (?:is likely|will happen|in (?:19|20)\d\d)", text, re.I
        )
        if "periods" in _kinds(answer) or "timing_status" in _kinds(answer):
            assert NO_TIMING_RULE in text


def test_out_of_scope_questions_get_one_polite_line_and_no_provisional_items() -> None:
    client = TestClient(create_app(Settings(llm_enabled=False)))
    for question, scope in OUT_OF_SCOPE.items():
        body = {
            "birth_input": P_MATCH.model_dump(mode="json"),
            "as_of": _AS_OF.isoformat(),
            "question": question,
            "include_provisional": True,
        }
        response = client.post("/api/v1/consultation", json=body)
        assert response.status_code == 200, question
        (answer,) = response.json()["analysis"]["answers"]
        assert [s["kind"] for s in answer["consultation_sections"]] == ["direct"]
        assert answer["answer"] == OUT_OF_SCOPE_REPLIES[scope]
        assert answer["provisional_interpretations"] == []


# --- Wording guard -------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "Your marriage may face delay.",
        "There is denial of marriage.",
        "This suggests an unhappy marriage.",
        "You have Mangal dosha.",
        "The marriage is doomed.",
        "You will never get married.",
        "It is your destiny.",
    ],
)
def test_guard_catches_fear_based_and_fatalistic_wording(text: str) -> None:
    assert marriage_wording_violation(text) is not None


def test_guard_ignores_quoted_source_text() -> None:
    verse = "रोगिणी कामिनी लभेत् (obtains a sickly wife; finds no happiness, delayed)"
    assert marriage_wording_violation(f"The verse reads: {verse}.", quoted=(verse,)) is None
    assert marriage_wording_violation(f"The verse reads: {verse}.") == "delayed"


def test_every_marriage_answer_passes_the_guards(answers: dict) -> None:  # type: ignore[type-arg]
    allowed = (
        *(term.display for e in _entries() for term in e.terms),
        PERIOD_THEMES_CLOSING_V2,
    )
    texts = [answer.answer for answer in answers.values()] + list(OUT_OF_SCOPE_REPLIES.values())
    for text in texts:
        assert marriage_wording_violation(text) is None, text
        assert evaluative_violation(text, allowed) is None, text
        remaining = text
        for passage in sorted(set(allowed), key=len, reverse=True):
            remaining = remaining.replace(passage, " ")
        assert ranking_violation(remaining) is None, text


def _entries():  # type: ignore[no-untyped-def]
    corpus = ACTIVE_SIGNIFICATION_CORPUS
    lords = ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu")
    found = [corpus.graha(lord) for lord in lords] + [corpus.bhava(h) for h in range(1, 13)]
    return [entry for entry in found if entry is not None]


def test_at_most_one_non_prediction_sentence_at_the_end(answers: dict) -> None:  # type: ignore[type-arg]
    for answer in answers.values():
        text = answer.answer.replace(PERIOD_THEMES_CLOSING_V2, "")
        hits = [s for s in _SENTENCES.split(text) if NON_PREDICTION.search(s)]
        assert len(hits) <= 1, hits
        if hits:
            assert answer.answer.endswith(hits[0])


# --- Provisional 7th-lord rules ------------------------------------------------------------


def test_corpus_v2_keeps_v1_and_adds_the_marriage_rules() -> None:
    assert ACTIVE_PROVISIONAL_CORPUS.release_id == "jyotish.provisional@v2"
    assert PROVISIONAL_CORPUS_V1.release_id == "jyotish.provisional@v1"
    assert set(PROVISIONAL_CORPUS_V1.rules) <= set(ACTIVE_PROVISIONAL_CORPUS.rules)
    assert ACTIVE_PROVISIONAL_CORPUS.for_domain("marriage") == tuple(
        sorted(MARRIAGE_RULES, key=lambda rule: rule.rule_id)
    )


def _house(rule: ProvisionalRule) -> int:
    return int(rule.rule.condition.expected_value)  # type: ignore[arg-type]


def test_every_house_is_drafted_or_recorded_as_not_drafted() -> None:
    drafted = {_house(rule) for rule in MARRIAGE_RULES}
    assert drafted == {1, 2, 4, 6, 7, 8, 9, 10, 12}
    notes = " ".join(NOT_DRAFTED["marriage"])
    assert "3rd or the 11th" in notes and "verse 52" in notes
    assert "5th house" in notes and "verse 54" in notes


def test_marriage_rules_records() -> None:
    for rule in MARRIAGE_RULES:
        j = rule.justification
        assert rule.domain is JyotishDomain.MARRIAGE
        assert rule.fact_dependencies == ("jyotish.d1.house_lord.7.placement_house",)
        assert j.author == "drafted_by: AI agent; adopted_by: project owner (pending)"
        assert "Saptamesha-phala" in j.locator and re.search(r"verse 5[0-6]", j.locator)
        assert j.transcription_notes and j.original_text.endswith("॥")
        # Template and reasoning text pass the wording guard; the verse and its draft
        # translation are quoted source text.
        for text in (rule.statement, j.interpretive_reasoning, rule.held_reason or ""):
            assert marriage_wording_violation(text) is None, (rule.rule_id, text)
    shown = [rule for rule in MARRIAGE_RULES if rule.wording == "shown"]
    assert shown == [RULE_7_IN_12_MARRIAGE]
    assert RULE_7_IN_12_MARRIAGE.justification.confidence.value == "medium"
    for rule in MARRIAGE_RULES:
        if rule.wording == "held":
            assert rule.statement == HELD_STATEMENT and rule.held_reason


def test_held_rules_never_send_the_draft_translation() -> None:
    for house, rule in ((_house(rule), rule) for rule in MARRIAGE_RULES):
        facts = {"jyotish.d1.house_lord.7.placement_house": house}
        (item,) = provisional_interpretations(ACTIVE_PROVISIONAL_CORPUS, facts, "marriage")
        assert item.rule_id == rule.rule_id
        assert item.badge == f"Provisional · {rule.justification.confidence.value} confidence"
        if rule.wording == "held":
            assert item.wording_held and item.statement == HELD_STATEMENT
            assert item.justification.draft_translation is None
            assert item.justification.held_reason == rule.held_reason
        else:
            assert not item.wording_held
            assert item.justification.draft_translation == rule.justification.draft_translation
    for house in (3, 5, 11):
        facts = {"jyotish.d1.house_lord.7.placement_house": house}
        assert provisional_interpretations(ACTIVE_PROVISIONAL_CORPUS, facts, "marriage") == ()


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


@pytest.mark.parametrize("question", [OUTLOOK, TIMING, YEAR])
def test_provisional_only_with_the_flag_and_reviewed_parts_unchanged(question: str) -> None:
    birth = BY_SEVENTH_LORD_HOUSE[12]
    off = _consult(question, birth, False)
    on = _consult(question, birth, True)
    assert off["provisional_interpretations"] == []
    item, *significations = on["provisional_interpretations"]
    assert item["kind"] == "rule"
    # NEXT-MARRIAGE-02: the provisional Marriage signification terms follow the rule.
    assert [s["kind"] for s in significations] == ["signification"] * 3
    assert item["rule_id"] == RULE_7_IN_12_MARRIAGE.rule_id
    assert item["statement"] == RULE_7_IN_12_MARRIAGE.statement
    assert item["badge"] == "Provisional · medium confidence"
    strip = {k: v for k, v in on.items() if k != "provisional_interpretations"}
    assert strip == {k: v for k, v in off.items() if k != "provisional_interpretations"}
    assert RULE_7_IN_12_MARRIAGE.rule_id not in json.dumps(strip)
