"""NEXT-PREREVIEW-01: an AI pre-review can never stand in for a human review.

The ``jyotish-prereview`` sub-agent writes proposals under ``research/prereview/``.  Every
admission path (production rules and Dasha corpora via ``AdmissionValidator``; significations
and X18 via ``admit_signification_corpus``) must reject a review record whose reviewer or
notes reference a pre-review or an AI agent.  Fixtures are synthetic; no real birth data.
"""

from itertools import chain

import pytest

from astrologer.knowledge.admission import AdmissionError, AdmissionValidator
from astrologer.knowledge.career_part0_pack_v1 import (
    EXPERT_REVIEW_NOTES,
    EXPERT_REVIEWER,
    FACT_CONTRACT,
    PART0_RULE_ENVELOPES,
    PRODUCTION_ENVELOPES,
    SOURCE_REGISTRY,
)
from astrologer.knowledge.models import ReviewRecord
from astrologer.knowledge.reviewer_guard import ai_review_violation
from astrologer.knowledge.signification import (
    SignificationCorpusError,
    admit_signification_corpus,
)
from astrologer.knowledge.signification_part0b_v1 import (
    LORDSHIP_PRINCIPLE,
    PRODUCTION_SIGNIFICATION_MANIFEST,
)

BAD_REVIEWERS = (
    "jyotish-prereview",
    "AI pre-review",
    "Pre-Review assistant",
    "Pandit ji (via prereview)",
    "Claude (AI preparer)",
    "AI agent",
    "review sub-agent",
)
BAD_NOTES = (
    "Decision taken from research/prereview/part1-prereview.md.",
    "Approved as in the AI PRE-REVIEW.",
    "As proposed by the AI agent.",
    "Per the jyotish-prereview subagent output.",
    "Claude's proposal accepted.",
)
# Real reviewer and notes from the admitted records; they must stay admissible.
GOOD = (
    (EXPERT_REVIEWER, EXPERT_REVIEW_NOTES),
    ("JyotAI project-owner review", None),
    ("Pandit ji", "Reviewer corrected the preparer's draft reading of v.71."),
)

RULE = PART0_RULE_ENVELOPES[0]
BASE_REVIEW = RULE.formalization_review
assert BASE_REVIEW is not None


def _bad_reviews() -> list[ReviewRecord]:
    return [BASE_REVIEW.model_copy(update={"reviewer": name}) for name in BAD_REVIEWERS] + [
        BASE_REVIEW.model_copy(update={"reviewer": EXPERT_REVIEWER, "notes": notes})
        for notes in BAD_NOTES
    ]


BAD_REVIEWS = _bad_reviews()
BAD_IDS = [f"reviewer:{name}" for name in BAD_REVIEWERS] + [f"notes:{n}" for n in BAD_NOTES]


@pytest.mark.parametrize("review", BAD_REVIEWS, ids=BAD_IDS)
def test_guard_flags_prereview_or_ai_agent(review: ReviewRecord) -> None:
    assert ai_review_violation(review) is not None


@pytest.mark.parametrize(("reviewer", "notes"), GOOD)
def test_guard_accepts_human_reviews(reviewer: str, notes: str | None) -> None:
    review = BASE_REVIEW.model_copy(update={"reviewer": reviewer, "notes": notes})
    assert ai_review_violation(review) is None


def test_every_admitted_production_review_passes_the_guard() -> None:
    reviews = chain(
        (e.formalization_review for e in PRODUCTION_ENVELOPES),
        (p.review for p in SOURCE_REGISTRY.passages),
        (t.review for t in SOURCE_REGISTRY.translations),
        (i.review for i in SOURCE_REGISTRY.interpretations),
        (e.review for e in PRODUCTION_SIGNIFICATION_MANIFEST.entries),
        (LORDSHIP_PRINCIPLE.review,),
    )
    assert [r for r in reviews if r is not None and ai_review_violation(r) is not None] == []


def test_rule_admission_accepts_the_unchanged_rule() -> None:
    AdmissionValidator().validate_production_active(RULE, SOURCE_REGISTRY, FACT_CONTRACT)


@pytest.mark.parametrize("review", BAD_REVIEWS, ids=BAD_IDS)
def test_rule_admission_rejects_ai_formalization_review(review: ReviewRecord) -> None:
    envelope = RULE.model_copy(update={"formalization_review": review})
    with pytest.raises(AdmissionError, match="never a reviewer"):
        AdmissionValidator().validate_production_active(envelope, SOURCE_REGISTRY, FACT_CONTRACT)


@pytest.mark.parametrize("review", BAD_REVIEWS, ids=BAD_IDS)
def test_rule_admission_rejects_ai_interpretation_review(review: ReviewRecord) -> None:
    interpretations = tuple(
        item.model_copy(
            update={
                "review": item.review.model_copy(
                    update={"reviewer": review.reviewer, "notes": review.notes}
                )
            }
        )
        if item.interpretation_id == RULE.interpretation_id and item.review is not None
        else item
        for item in SOURCE_REGISTRY.interpretations
    )
    registry = SOURCE_REGISTRY.model_copy(update={"interpretations": interpretations})
    with pytest.raises(AdmissionError, match="never a reviewer"):
        AdmissionValidator().validate_production_active(RULE, registry, FACT_CONTRACT)


@pytest.mark.parametrize("review", BAD_REVIEWS, ids=BAD_IDS)
def test_signification_admission_rejects_ai_entry_review(review: ReviewRecord) -> None:
    entry = PRODUCTION_SIGNIFICATION_MANIFEST.entries[0]
    swapped = entry.model_copy(
        update={
            "review": entry.review.model_copy(
                update={"reviewer": review.reviewer, "notes": review.notes}
            )
        }
    )
    manifest = PRODUCTION_SIGNIFICATION_MANIFEST.model_copy(
        update={"entries": (swapped, *PRODUCTION_SIGNIFICATION_MANIFEST.entries[1:])}
    )
    with pytest.raises(SignificationCorpusError, match="never a reviewer"):
        admit_signification_corpus(manifest)


@pytest.mark.parametrize("review", BAD_REVIEWS, ids=BAD_IDS)
def test_signification_admission_rejects_ai_x18_review(review: ReviewRecord) -> None:
    principle = LORDSHIP_PRINCIPLE.model_copy(
        update={
            "review": LORDSHIP_PRINCIPLE.review.model_copy(
                update={"reviewer": review.reviewer, "notes": review.notes}
            )
        }
    )
    manifest = PRODUCTION_SIGNIFICATION_MANIFEST.model_copy(
        update={"lordship_principle": principle}
    )
    with pytest.raises(SignificationCorpusError, match="never a reviewer"):
        admit_signification_corpus(manifest)
