"""NEXT-FIX-DEG-01 Part A: three wording fixes in dasha_context, the direct line and Why.

1. Each relationship is stated once per lord (no repeated occupancy sentence).
2. An Antardasha of the Mahadasha's own lord gets no "counted from <same planet>'s sign".
3. Paused/withheld rules (v.72 7th house, v.76 8th house): the direct line says only that a
   reviewed indication exists with wording pending source verification, and Why never
   co-references them.

Synthetic births only (12:00 UTC or as noted, 0°N 0°E).
"""

import re

import pytest
from test_career_answer_wording import _birth
from test_year_glance import _answer

from astrologer.composition.models import DetailedComposedAnswer
from astrologer.knowledge.admit02_pack_v1 import WITHHELD_WORDING_RULE_IDS

PENDING = (
    "A reviewed indication exists for your 10th lord's placement; its wording is pending "
    "source verification."
)
# Synthetic births found by scanning dates at 12:00 UTC, 0°N 0°E.
TENTH_LORD_IN_7 = _birth("1986-02-12", "12:00:00")  # v.72 7th house (paused); Venus MD
TENTH_LORD_IN_8 = _birth("1986-01-13", "12:00:00")  # v.76 (withheld)
RAHU_RAHU = _birth("1990-03-10", "18:00:00")  # Rahu MD and Rahu AD through 2027
DUPLICATE_OCCUPANCY = re.compile(
    r"\b([A-Z][a-z]+) occupies your (\d+(?:st|nd|rd|th)) house, [^.]*\. \1 occupies your"
)


def _sections(answer: DetailedComposedAnswer) -> dict[str, str]:
    return {section.kind: section.text for section in answer.consultation_sections}


@pytest.fixture(scope="module")
def seventh() -> DetailedComposedAnswer:
    return _answer(TENTH_LORD_IN_7, 2028)


@pytest.fixture(scope="module")
def eighth() -> DetailedComposedAnswer:
    return _answer(TENTH_LORD_IN_8, 2027)


@pytest.fixture(scope="module")
def rahu_rahu() -> DetailedComposedAnswer:
    return _answer(RAHU_RAHU, 2027)


def test_occupancy_is_stated_once_per_lord(seventh: DetailedComposedAnswer) -> None:
    text = _sections(seventh)["dasha_context"]
    # Before: "Venus occupies your 10th house, Aquarius. Venus occupies your 10th house."
    assert "Venus occupies your 10th house, Aquarius." in text
    assert text.count("Venus occupies your 10th house") == 1
    assert text.count("Jupiter occupies your 10th house") == 1
    assert not DUPLICATE_OCCUPANCY.search(text)
    # The placement sentence now cites the occupies_tenth fact it states.
    section = next(s for s in seventh.consultation_sections if s.kind == "dasha_context")
    placement = next(
        s for s in section.fact_sentences if s.text.startswith("Venus occupies your 10th house")
    )
    assert any(f.endswith(".venus.occupies_tenth") for f in placement.fact_ids)


def test_no_sentence_is_repeated_within_a_dasha_context(
    seventh: DetailedComposedAnswer,
    eighth: DetailedComposedAnswer,
    rahu_rahu: DetailedComposedAnswer,
) -> None:
    for answer in (seventh, eighth, rahu_rahu):
        section = next(s for s in answer.consultation_sections if s.kind == "dasha_context")
        texts = [s.text for s in section.fact_sentences]
        assert len(texts) == len(set(texts))


def test_same_lord_antardasha_has_no_self_count(rahu_rahu: DetailedComposedAnswer) -> None:
    text = _sections(rahu_rahu)["dasha_context"]
    assert "counted from Rahu's sign" not in text
    assert "Rahu Antardasha (28 Feb 2026 to 10 Nov 2028): the same lord as the Mahadasha" in text
    # Rahu's relationships are stated once, in the Mahadasha block.
    assert text.count("Rahu occupies your 6th house, Capricorn.") == 1
    assert text.count("Rahu is not assigned sign rulership") == 1


def test_different_lords_keep_the_counted_from_sentence(seventh: DetailedComposedAnswer) -> None:
    assert (
        "Jupiter is in the 1st sign counted from Venus's sign."
        in (_sections(seventh)["dasha_context"])
    )


@pytest.mark.parametrize("which", ["seventh", "eighth"])
def test_paused_or_withheld_direct_line(which: str, request: pytest.FixtureRequest) -> None:
    answer: DetailedComposedAnswer = request.getfixturevalue(which)
    direct = _sections(answer)["direct"]
    assert PENDING in direct
    assert "your chart matches" not in direct.lower()
    assert "the reviewed indication about your 10th lord's placement" not in direct


@pytest.mark.parametrize("which", ["seventh", "eighth"])
def test_paused_or_withheld_rules_are_excluded_from_why(
    which: str, request: pytest.FixtureRequest
) -> None:
    answer: DetailedComposedAnswer = request.getfixturevalue(which)
    plan = answer.career_answer_plan
    assert plan is not None and plan.synthesis is not None
    claims = {c.claim_id: c for c in answer.claim_ledger.claims} if answer.claim_ledger else {}
    withheld = plan.synthesis.withheld_claim_ids
    assert withheld
    for claim_id in withheld:
        assert {r.split("@")[0] for r in claims[claim_id].rule_ids} & WITHHELD_WORDING_RULE_IDS
    assert not set(withheld) & set(plan.synthesis.reviewed_claim_ids)
    assert not {link.claim_id for link in plan.synthesis.links} & set(withheld)
    why = _sections(answer)["why"]
    assert "reviewed indication about your 10th lord's placement" not in why
    assert "pending source verification" in why
    assert "not linked to the" in why
