"""NEXT-THEMES-01: each cited rule's review type, from the existing records only.

The label is shown in the evidence disclosure, never in the main answer text.  Synthetic
births only.
"""

import json
from datetime import UTC, datetime

from test_career_answer_wording import PROFILES, _ask
from test_year_glance import _answer

from astrologer.application.analyze import DeterministicAnalysisRequest
from astrologer.application.review_types import (
    CONVENTION_REVIEW,
    INDEPENDENT_REVIEW,
    OWNER_REVIEW,
    rule_review_types,
)
from astrologer.knowledge import ACTIVE_PRODUCTION_RELEASE
from astrologer.knowledge.career_part0_pack_v1 import (
    ACTIVE_PRODUCTION_RELEASE as RELEASE_V11,
)
from astrologer.knowledge.career_part0_pack_v1 import (
    RULE_IN_1,
    RULE_IN_2_3_OR_7,
    RULE_IN_8,
)
from astrologer.knowledge.signification_admit02_v1 import ACTIVE_SIGNIFICATION_CORPUS
from astrologer.timing_rules.registry import get_active_timing_release

PART0 = {RULE_IN_1, RULE_IN_2_3_OR_7, RULE_IN_8}


def _labels(rule_ids: list[str]) -> dict[str, str]:
    return {
        item.rule_id: item.review_type
        for item in rule_review_types(rule_ids, ACTIVE_SIGNIFICATION_CORPUS)
    }


def test_natal_rules_carry_the_review_type_of_their_record() -> None:
    # NEXT-ADMIT-02: every v12 rule now carries the reviewer's record (Sitting 1 items 1–24
    # confirmed; the split and paused rules are new records under the same review).
    labels = _labels([e.rule.rule_id for e in ACTIVE_PRODUCTION_RELEASE.envelopes])
    assert len(labels) == 26
    assert set(labels.values()) == {INDEPENDENT_REVIEW}
    # v11 records are unchanged: only Part 0 was independently reviewed there.
    v11 = {
        item.interpretation_id: item.review.reviewer
        for item in RELEASE_V11.registry.interpretations
    }
    owner = [e for e in RELEASE_V11.envelopes if v11[e.interpretation_id] != "Pandit ji"]
    assert len(owner) == 22
    assert {e.rule.rule_id for e in RELEASE_V11.envelopes} - {e.rule.rule_id for e in owner} == (
        PART0
    )


def test_significations_and_timing_are_independent_x18_is_a_convention() -> None:
    corpus = ACTIVE_SIGNIFICATION_CORPUS
    principle = corpus.lordship_principle
    assert principle is not None
    ids = [f"{e.rule_id}@{e.rule_version}" for e in corpus.entries]
    ids.append(f"{principle.rule_id}@{principle.rule_version}")
    labels = _labels(ids)
    assert set(labels) == set(ids)  # the cited id (with @version) is returned unchanged
    x18 = f"{principle.rule_id}@{principle.rule_version}"
    # NEXT-ADMIT-02, Sitting 2 item 30: X18 has no source verse identified.
    assert labels.pop(x18) == CONVENTION_REVIEW
    assert set(labels.values()) == {INDEPENDENT_REVIEW}
    # Timing production v3 carries the reviewer's record (Sitting 1 items 1 and 2).
    timing = _labels([str(rule.rule_id) for rule in get_active_timing_release().rules])
    assert len(timing) == 2 and set(timing.values()) == {INDEPENDENT_REVIEW}


def test_unknown_rules_are_never_labelled_and_order_is_first_seen() -> None:
    assert _labels(["fixture.unknown.rule"]) == {}
    ordered = rule_review_types([RULE_IN_8, RULE_IN_1, RULE_IN_8], ACTIVE_SIGNIFICATION_CORPUS)
    assert [item.rule_id for item in ordered] == [RULE_IN_8, RULE_IN_1]


def test_a_career_year_answer_lists_every_cited_rule_and_never_shows_the_label() -> None:
    answer = _answer(PROFILES["period_lord"], 2027)
    cited = {item.rule_id for item in answer.rule_review_types}
    assert answer.claim_ledger is not None
    for claim in answer.claim_ledger.claims:
        if claim.kind.value.startswith("APPROVED"):
            assert set(claim.rule_ids) <= cited
    plan = answer.career_answer_plan
    assert plan is not None
    for sentence in plan.period_themes:
        assert set(sentence.rule_ids) <= cited
    visible = answer.answer + json.dumps([s.text for s in answer.consultation_sections])
    for label in (
        INDEPENDENT_REVIEW,
        OWNER_REVIEW,
        CONVENTION_REVIEW,
        "Pandit ji",
        "Project-owner",
    ):
        assert label not in visible


def test_other_domains_list_the_review_type_of_their_matched_rules() -> None:
    request = DeterministicAnalysisRequest(
        birth_input=PROFILES["rahu_rahu"],
        as_of=datetime(2026, 1, 1, tzinfo=UTC),
        question="What does my chart say about wealth?",
    )
    result = _ask().answer(request)
    answer = result.answers[0]
    matched = {item.rule_id for s in result.selections for item in s.selected_matched}
    assert matched == {"bphs.d1.house_lord.5.in_11.wealth.v1"}
    assert {item.rule_id for item in answer.rule_review_types} == matched
    assert all(item.review_type == INDEPENDENT_REVIEW for item in answer.rule_review_types)
    assert INDEPENDENT_REVIEW not in answer.answer


def test_production_rahu_rahu_year_gives_one_merged_period_themes_line() -> None:
    plan = _answer(PROFILES["rahu_rahu"], 2027).career_answer_plan
    assert plan is not None
    rahu = [s.text for s in plan.period_themes if "Rahu" in s.text]
    assert len(rahu) == 1
    # X18 v2 compact form, one merged same-lord line.  NEXT-PROPERTY-01: Mahadasha primary,
    # Antardasha secondary on the merged line too (each label once).
    assert rahu[0].startswith(
        "Rahu Mahadasha (primary) and Antardasha (secondary) (throughout 2027): reviewed themes"
    )
    assert rahu[0].count("(primary)") == rahu[0].count("(secondary)") == 1
    assert plan.period_themes_glance is not None
    # Rahu occupies the 6th house, whose शत्रु entry corpus v3 restores (Sitting 1 item 28).
    assert plan.period_themes_glance.text == "Period themes: Rahu: 6th house."
