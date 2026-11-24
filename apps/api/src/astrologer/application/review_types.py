"""Review type of every rule an answer cites, from the existing review records (NEXT-THEMES-01).

Shown only in the evidence disclosure, never in the main answer text.  Two labels exist:

* ``INDEPENDENT_REVIEW``: the rule's record names the expert reviewer of NEXT-ADMIT-01
  (``EXPERT_REVIEWER``, Acharya): the Part 0 Career rules, the 0b significations and X18.
* ``OWNER_REVIEW``: every other record.  The earlier natal packs record "JyotAI
  project-owner review"; the Career timing release carries no reviewer at all (admitted
  2026-10-09/10, before the independent record), so it is labelled conservatively as
  project-owner review.  A rule with no record found is never labelled.

This reads records only; it never changes a review, a rule or approved wording.
"""

from collections.abc import Iterable
from typing import Final

from astrologer.composition.models import ReviewTypeLabel, RuleReviewType
from astrologer.knowledge.career_part0_pack_v1 import (
    ACTIVE_PRODUCTION_RELEASE,
    EXPERT_REVIEWER,
)
from astrologer.knowledge.models import ReviewRecord
from astrologer.knowledge.signification import SignificationCorpus
from astrologer.timing_rules.registry import get_active_timing_release

INDEPENDENT_REVIEW: Final[ReviewTypeLabel] = "Independent reviewer (Pandit ji, Acharya)"
OWNER_REVIEW: Final[ReviewTypeLabel] = "Project-owner review (not independently certified)"


def review_label(review: ReviewRecord) -> ReviewTypeLabel:
    """The display label for one review record."""
    if review.reviewer == EXPERT_REVIEWER and "Acharya" in (review.notes or ""):
        return INDEPENDENT_REVIEW
    return OWNER_REVIEW


def _natal_index() -> dict[str, ReviewTypeLabel]:
    interpretations = {
        item.interpretation_id: item for item in ACTIVE_PRODUCTION_RELEASE.registry.interpretations
    }
    index: dict[str, ReviewTypeLabel] = {}
    for envelope in ACTIVE_PRODUCTION_RELEASE.envelopes:
        interpretation = interpretations.get(envelope.interpretation_id)
        if interpretation is not None:
            index[envelope.rule.rule_id] = review_label(interpretation.review)
    return index


def _timing_index() -> dict[str, ReviewTypeLabel]:
    return {str(rule.rule_id): OWNER_REVIEW for rule in get_active_timing_release().rules}


def _signification_index(corpus: SignificationCorpus) -> dict[str, ReviewTypeLabel]:
    index = {entry.rule_id: review_label(entry.review) for entry in corpus.entries}
    principle = corpus.lordship_principle
    if principle is not None:
        index[principle.rule_id] = review_label(principle.review)
    return index


def rule_review_types(
    rule_ids: Iterable[str], corpus: SignificationCorpus
) -> tuple[RuleReviewType, ...]:
    """One entry per distinct cited rule (first-seen order) that has a review record.

    Rule ids may carry an ``@version`` suffix (synthesis citations); the record is looked up
    by the bare id and the cited id is returned unchanged.
    """
    index = {**_natal_index(), **_timing_index(), **_signification_index(corpus)}
    result: list[RuleReviewType] = []
    for rule_id in dict.fromkeys(rule_ids):
        label = index.get(rule_id.split("@", 1)[0])
        if label is not None:
            result.append(RuleReviewType(rule_id=rule_id, review_type=label))
    return tuple(result)
