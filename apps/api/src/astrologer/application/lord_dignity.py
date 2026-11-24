"""The sign dignity of a rule's house lord, as a calculated fact shown next to the rule.

NEXT-ADMIT-02, Sitting 1 item 26 (X2): dignity is a MODIFIER only.  It is one strength factor,
not a strength model, so this module only states which of the admitted sign-dignity facts
(own, exaltation, debilitation sign) are true for the lord.  It never inverts, negates,
weakens, strengthens or otherwise changes a rule's result, and it never calls a lord strong
or weak.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final

DIGNITY_PREFIX: Final = (
    "Calculated fact (sign dignity, shown as a modifier only; it does not change the reviewed "
    "indication)"
)
_KINDS: Final = (
    ("own_sign", "its own sign"),
    ("exaltation_sign", "its exaltation sign"),
    ("debilitation_sign", "its debilitation sign"),
)


@dataclass(frozen=True)
class LordDignity:
    text: str
    fact_ids: tuple[str, ...]


def lord_dignity(facts: Mapping[str, object], house: int) -> LordDignity | None:
    """'…: your 10th lord, Mars, is in its own sign.' from existing D1 facts, or None when the
    lord or any of its three dignity facts is not available (UNKNOWN is never FALSE)."""
    lord_fact = f"jyotish.d1.house.{house}.lord"
    lord = facts.get(lord_fact)
    if not isinstance(lord, str):
        return None
    fact_ids = [lord_fact]
    held: list[str] = []
    for kind, phrase in _KINDS:
        fact_id = f"jyotish.d1.planet.{lord}.{kind}"
        value = facts.get(fact_id)
        if not isinstance(value, bool):
            return None
        fact_ids.append(fact_id)
        if value:
            held.append(phrase)
    state = (
        "is in " + " and ".join(held)
        if held
        else "is in none of its own, exaltation or debilitation signs"
    )
    return LordDignity(
        text=f"{DIGNITY_PREFIX}: your {_ordinal(house)} lord, {lord.title()}, {state}.",
        fact_ids=tuple(fact_ids),
    )


def _ordinal(number: int) -> str:
    suffix = (
        "th" if 10 <= number % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    )
    return f"{number}{suffix}"
