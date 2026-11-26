"""NEXT-PROPERTY-01: no fear-based or fatalistic wording in property answers.

Property answers may not frighten or pronounce fate: no "loss", "dispute", "litigation",
"accident", "ruin", "doomed" and the like (owner rule: a verse predicting loss, misfortune or
an accusation is held, not shown).  Property answers also never advise on a price, a purchase
or a sale, and never forecast a legal result, so the template text may not say "good time to
buy", "will appreciate" or "you will win".  The guard covers every template sentence of a
property answer (sections, out-of-scope replies, provisional statements and placements).
Quoted source text (the Sanskrit original and its draft translation, kept for the evidence
disclosure or the review pack) and admitted reviewed statements are passed as ``quoted`` and
removed first.
"""

import re
from collections.abc import Iterable
from typing import Final

PROPERTY_FEAR_LANGUAGE: Final = re.compile(
    r"\b(?:loss(?:es)?|lose|loses|losing|lost|ruin(?:s|ed|ous)?|dispute[sd]?|litigation|"
    r"lawsuits?|accidents?|disasters?|disastrous|calamit(?:y|ies)|misfortunes?|"
    r"homeless\w*|evict\w*|seiz(?:e|ed|ure)|confiscat\w*|debts?|bankrupt\w*|thie(?:f|ves)|"
    r"theft|doom(?:s|ed)?|curse(?:s|d)?|dosh(?:a|as|am)?|fatal(?:ism|istic)?|fated?|"
    r"destin(?:y|ed)|inevitabl[ey]|never\s+(?:own|have|get|buy)|will\s+not\s+(?:own|get|buy)|"
    r"(?:good|right|best|auspicious)\s+time\s+to\s+(?:buy|sell|purchase)|"
    r"will\s+(?:appreciate|win|gain\s+in\s+value)|price\s+will)\b",
    re.IGNORECASE,
)
"""Fear-based, fatalistic or advisory wording barred from property answers outside quoted
source text."""


def property_wording_violation(text: str, quoted: Iterable[str] = ()) -> str | None:
    """The first fear-based, fatalistic or advisory phrase in ``text`` outside the ``quoted``
    passages, else None.  Each exact quoted passage is removed (longest first) first."""
    remaining = text
    for passage in sorted({item for item in quoted if item}, key=len, reverse=True):
        remaining = remaining.replace(passage, " ")
    match = PROPERTY_FEAR_LANGUAGE.search(remaining)
    return match.group() if match else None
