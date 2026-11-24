"""NEXT-TONE-01: at most one template non-prediction sentence per answer.

Wording only: no fact, rule, term or doctrine changes.  Admitted rule text and approved
wording (the X18 Period-themes closing, natal and timing rule text, the v.76 withheld
notice) are excluded from the count and stay byte-identical where quoted.  UNKNOWN wording
is a fact, not a disclaimer, and is unchanged.  All births are synthetic (lat/long 0, UTC).
"""

import re

import pytest
from consultation_quality_benchmark import FORBIDDEN_SYNTHESIS_WORDS
from test_career_comparison import _BIRTHS as COMPARISON_BIRTHS
from test_career_comparison import _ask as _comparison_ask
from test_career_comparison import _request as _comparison_request
from test_year_glance import _answer, _birth

from astrologer.application.career_claims import (
    TIMING_FULL_TEXT_POINTER,
    timing_meaning_and_limit,
    year_closing_sentence,
)
from astrologer.application.career_comparison import (
    LIMITATION_NO_EVENT,
    LIMITATION_NO_EVENT_PERIODS_ONLY,
)
from astrologer.application.career_synthesis import WHY_FRAMING
from astrologer.application.period_themes import PERIOD_THEMES_CLOSING
from astrologer.composition.career_claims import ClaimKind
from astrologer.composition.comparison_guard import ranking_violation
from astrologer.composition.evaluative_guard import evaluative_violation
from astrologer.composition.models import CareerYearComparison, DetailedComposedAnswer
from astrologer.knowledge.career_part0_pack_v1 import WITHHELD_STATEMENT

# A sentence that says the answer does not predict, guarantee or establish an outcome, or
# that the synthesis does not combine or rank (the disclaimers this task reduces).
NON_PREDICTION = re.compile(
    r"\b(?:not a prediction|does not predict|do not predict|does not guarantee|"
    r"not guaranteed?|does not establish|do not establish|not establish(?:ed)?|"
    r"is established|establishes|no specific|does not combine|weigh, or rank|"
    r"None of this)\b",
    re.IGNORECASE,
)
_SENTENCES = re.compile(r"(?<=[.!?])\s+(?=[A-Z])|\s*\n\s*")

# Synthetic births covering: timing match (MD), no match, shared house, Rahu MD/AD, Rahu MD
# with a Mercury AD, 10th lord in the 7th (v.72) and in the 8th (v.76, wording withheld).
YEAR_CASES = [
    ("1978-01-01", "12:00:00", 2027),
    ("1978-01-01", "12:00:00", 2028),
    ("1988-02-28", "06:00:00", 2027),
    ("1995-11-05", "18:00:00", 2027),
    ("1990-03-10", "18:00:00", 2027),
    ("1978-06-12", "18:00:00", 2028),
    ("1994-10-03", "18:00:00", 2028),
    ("1985-03-10", "12:00:00", 2028),
    ("1985-01-15", "12:00:00", 2027),
]


@pytest.fixture(scope="module")
def year_answers() -> dict[tuple[str, int], DetailedComposedAnswer]:
    return {(date, year): _answer(_birth(date, time), year) for date, time, year in YEAR_CASES}


@pytest.fixture(scope="module")
def comparisons() -> dict[str, CareerYearComparison]:
    ask = _comparison_ask()
    result = {}
    for profile in COMPARISON_BIRTHS:
        comparison = ask.answer(_comparison_request(profile)).answers[0].career_comparison
        assert comparison is not None
        result[profile] = comparison
    return result


def _admitted(answer: DetailedComposedAnswer) -> list[str]:
    """Admitted and approved passages quoted in a year answer (excluded from the count)."""
    ledger = answer.claim_ledger
    assert ledger is not None
    passages = [
        claim.permitted_wording
        for claim in ledger.claims
        if claim.kind
        in {ClaimKind.APPROVED_INTERPRETATION, ClaimKind.APPROVED_TIMING_INTERPRETATION}
    ]
    for claim in ledger.claims:
        if claim.kind is ClaimKind.APPROVED_TIMING_INTERPRETATION:
            passages.extend(t for t in timing_meaning_and_limit(claim.permitted_wording) if t)
    return [*passages, PERIOD_THEMES_CLOSING, WITHHELD_STATEMENT]


def _template_non_prediction(text: str, admitted: list[str]) -> list[str]:
    remaining = text
    for passage in sorted(set(admitted), key=len, reverse=True):
        remaining = remaining.replace(passage, "\n")
    return [s for s in _SENTENCES.split(remaining) if NON_PREDICTION.search(s)]


def test_year_answer_has_one_template_non_prediction_sentence_in_the_closing_section(
    year_answers: dict[tuple[str, int], DetailedComposedAnswer],
) -> None:
    for key, answer in year_answers.items():
        admitted = _admitted(answer)
        found = _template_non_prediction(answer.answer, admitted)
        closing = answer.consultation_sections[-1]
        assert closing.kind == "limit", key
        assert found == [closing.text], (key, found)
        assert closing.text.endswith(f"for {key[1]}, not a prediction of specific events."), key
        for section in answer.consultation_sections[:-1]:
            assert _template_non_prediction(section.text, admitted) == [], (key, section.kind)


def test_closing_sentence_names_only_what_the_answer_shows(
    year_answers: dict[tuple[str, int], DetailedComposedAnswer],
) -> None:
    assert year_closing_sentence(2028, themes=True, reviewed=True) == (
        "These are reviewed themes and calculated periods for 2028, not a prediction of "
        "specific events."
    )
    assert year_closing_sentence(2028, themes=False, reviewed=True) == (
        "These are reviewed indications and calculated periods for 2028, not a prediction of "
        "specific events."
    )
    assert year_closing_sentence(2028, themes=False, reviewed=False) == (
        "These are calculated periods for 2028, not a prediction of specific events."
    )
    for answer in year_answers.values():
        plan = answer.career_answer_plan
        assert plan is not None
        themes = any(s.kind == "period_themes" for s in answer.consultation_sections)
        assert ("reviewed themes" in answer.consultation_sections[-1].text) is themes


def test_why_framing_moves_to_the_disclosure_field(
    year_answers: dict[tuple[str, int], DetailedComposedAnswer],
) -> None:
    linked = 0
    for answer in year_answers.values():
        why = next((s for s in answer.consultation_sections if s.kind == "why"), None)
        assert why is not None
        assert WHY_FRAMING not in why.text and WHY_FRAMING not in answer.answer
        if why.synthesis_links:
            linked += 1
            assert why.framing == WHY_FRAMING
    assert linked > 0


def test_direct_line_quotes_only_the_meaning_and_points_to_the_timing_section(
    year_answers: dict[tuple[str, int], DetailedComposedAnswer],
) -> None:
    matched = 0
    for key, answer in year_answers.items():
        ledger = answer.claim_ledger
        assert ledger is not None
        timed = [c for c in ledger.claims if c.kind is ClaimKind.APPROVED_TIMING_INTERPRETATION]
        direct = answer.consultation_sections[0]
        timing = next(s for s in answer.consultation_sections if s.kind == "timing")
        if len(timed) != 1:
            assert TIMING_FULL_TEXT_POINTER not in direct.text, key
            continue
        matched += 1
        meaning, guarantee = timing_meaning_and_limit(timed[0].permitted_wording)
        assert guarantee is not None
        texts = [s.text for s in direct.synthesis_sentences]
        # The meaning is quoted byte for byte, never paraphrased.
        assert texts[-2].encode() == meaning.encode(), key
        assert texts[-1] == TIMING_FULL_TEXT_POINTER, key
        assert guarantee not in direct.text, key
        # The timing section still quotes the full admitted text, non-guarantee included.
        assert timed[0].permitted_wording.encode() in timing.text.encode(), key
        assert answer.answer.count(guarantee) == 1, key
    assert matched > 0


def test_admitted_text_is_byte_identical_where_quoted(
    year_answers: dict[tuple[str, int], DetailedComposedAnswer],
) -> None:
    for key, answer in year_answers.items():
        ledger = answer.claim_ledger
        assert ledger is not None
        sections = {s.kind: s for s in answer.consultation_sections}
        for claim in ledger.claims:
            if claim.kind is ClaimKind.APPROVED_INTERPRETATION:
                assert claim.permitted_wording.encode() in sections["natal"].text.encode(), key
        themes = sections.get("period_themes")
        if themes is not None:
            # The X18 template's approved closing stays in the section that quotes it.
            assert themes.text.endswith(" " + PERIOD_THEMES_CLOSING), key
            assert themes.synthesis_sentences[-1].text == PERIOD_THEMES_CLOSING, key


def test_unknown_and_withheld_wording_is_unchanged(
    year_answers: dict[tuple[str, int], DetailedComposedAnswer],
) -> None:
    v76 = year_answers[("1985-01-15", 2027)]
    glance = next(s for s in v76.consultation_sections if s.kind == "glance")
    assert glance.synthesis_sentences[1].text == (
        "Natal: your 10th lord is Saturn, in your 8th house; a reviewed indication exists for "
        "this placement; its wording is withheld pending further review."
    )
    assert WITHHELD_STATEMENT in v76.answer
    rahu = [
        a
        for a in year_answers.values()
        if "Rahu and Ketu aspects are not modeled under the seven-planet aspect convention "
        "used here." in a.answer
    ]
    assert rahu, "expected a Rahu-period answer with the UNKNOWN aspect sentence"


def test_comparison_has_one_template_non_prediction_sentence_at_the_end(
    comparisons: dict[str, CareerYearComparison],
) -> None:
    for profile, comparison in comparisons.items():
        a, b = comparison.years
        admitted = [
            text
            for column in comparison.columns
            for indication in column.timing_indications
            for text in (indication.reviewed_statement,)
        ]
        found = _template_non_prediction(comparison.text(), admitted)
        assert [s.text for s in comparison.limitations] == found, (profile, found)
        assert found[0] in {
            LIMITATION_NO_EVENT.format(a=a, b=b),
            LIMITATION_NO_EVENT_PERIODS_ONLY.format(a=a, b=b),
        }
        assert comparison.sentences()[-1].text == found[0]


def test_new_wording_passes_ranking_evaluative_and_causal_guards(
    year_answers: dict[tuple[str, int], DetailedComposedAnswer],
    comparisons: dict[str, CareerYearComparison],
) -> None:
    new = [
        TIMING_FULL_TEXT_POINTER,
        year_closing_sentence(2028, themes=True, reviewed=True),
        year_closing_sentence(2028, themes=False, reviewed=True),
        year_closing_sentence(2028, themes=False, reviewed=False),
        LIMITATION_NO_EVENT.format(a=2027, b=2028),
        LIMITATION_NO_EVENT_PERIODS_ONLY.format(a=2027, b=2028),
    ]
    for text in new:
        assert ranking_violation(text) is None, text
        assert evaluative_violation(text) is None, text
        assert FORBIDDEN_SYNTHESIS_WORDS.search(text.lower()) is None, text
    for answer in year_answers.values():
        assert ranking_violation(answer.consultation_sections[0].text) is None
    for comparison in comparisons.values():
        for sentence in comparison.sentences():
            if sentence.basis == "fixed":
                assert ranking_violation(sentence.text) is None, sentence.text
