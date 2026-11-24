"""Reviewer weight metadata for admitted natal rules (NEXT-ADMIT-02): primary | secondary.

Source: the reviewer's Sitting 1 verdicts (``pandit-ji-verdicts-2026-11-24.md``), recorded in
``docs/admissions/jyotish.admit02.sitting-1-2.admission.v1.md``.  A rule his verdict calls a
"supporting factor", "secondary", "supporting evidence", "low/medium weight" or "not a
primary … rule" is secondary; every other admitted rule is primary.

Weight is DISPLAY ORDER ONLY.  A secondary rule is shown as "supporting" and after the
primary ones.  It is never a score, a weighted sum, a ranking of charts or periods, or a
reason to hide, invert or combine a rule's result.
"""

from collections.abc import Callable, Sequence
from typing import Final, Literal

RuleWeight = Literal["primary", "secondary"]
SUPPORTING_LABEL: Final = "Supporting"

# Rule id → the verdict item that makes it secondary.
SECONDARY_RULES: Final[dict[str, str]] = {
    "bphs.d1.house_lord.11.in_9_or_10.v1": "Sitting 1 item 3 (supporting factor)",
    "bphs.d1.house_lord.4.in_1_or_7.education.v1": "Sitting 1 item 12 (supporting factor)",
    "bphs.d1.house_lord.6.in_9.business.v1": "Sitting 1 item 15 (secondary textual indicator)",
    "bphs.d1.house_lord.5.in_11.children.v1": "Sitting 1 item 16 (supporting evidence)",
    "bphs.d1.house_lord.11.in_2_or_5.children.v1": "Sitting 1 item 17 (secondary)",
    # Not in the v12 manifest (not surfaced in Children answers); kept in the source ledger.
    "bphs.d1.house_lord.10.in_5_or_11.children.v1": "Sitting 1 item 18 (secondary/low weight)",
    "bphs.d1.house_lord.10.in_4_or_10.spirituality.v1": "Sitting 1 item 19 (supporting factor)",
    "bphs.d1.house_lord.11.in_2_or_5.spirituality.v1": "Sitting 1 item 21 (low/medium weight)",
    "bphs.d1.house_lord.10.equals_9.friends.v1": "Sitting 1 item 24 (secondary only)",
}


def rule_weight(rule_id: str) -> RuleWeight:
    """The weight of one rule id (an ``@version`` suffix is ignored)."""
    return "secondary" if rule_id.split("@", 1)[0] in SECONDARY_RULES else "primary"


def primary_first[T](items: Sequence[T], rule_id: Callable[[T], str]) -> tuple[T, ...]:
    """``items`` with primary rules first and secondary after; order within each is kept."""
    return tuple(
        sorted(items, key=lambda item: 0 if rule_weight(rule_id(item)) == "primary" else 1)
    )
