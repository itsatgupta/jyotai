"""NEXT-WEALTH-01: no fear-based or fatalistic wording in wealth answers.

Wealth answers may not frighten or pronounce fate: no "poverty", "loss", "debt", "ruin",
"bankrupt", "doomed" and the like (owner rule: a verse predicting poverty or loss is held,
not shown).  The guard covers every template sentence of a wealth answer (sections,
out-of-scope replies, provisional statements and placements).  Quoted source text (the
Sanskrit original and its draft translation, kept for the evidence disclosure or the review
pack) and admitted reviewed statements are passed as ``quoted`` and removed first.
"""

import re
from collections.abc import Iterable
from typing import Final

WEALTH_FEAR_LANGUAGE: Final = re.compile(
    r"\b(?:povert(?:y|ies)|poor|penniless|destitut\w*|bankrupt\w*|broke|ruin(?:s|ed|ous)?|"
    r"loss(?:es)?|lose|loses|losing|lost|debts?|indebted\w*|beggar\w*|starv\w*|"
    r"misfortunes?|disasters?|disastrous|calamit(?:y|ies)|doom(?:s|ed)?|curse(?:s|d)?|"
    r"dosh(?:a|as|am)?|fatal(?:ism|istic)?|fated?|destin(?:y|ed)|inevitabl[ey]|"
    r"never\s+(?:be|become|get)\s+(?:rich|wealthy)|will\s+not\s+(?:be|become|get)\s+"
    r"(?:rich|wealthy)|no\s+wealth|without\s+wealth)\b",
    re.IGNORECASE,
)
"""Fear-based or fatalistic wording barred from wealth answers outside quoted source text."""


def wealth_wording_violation(text: str, quoted: Iterable[str] = ()) -> str | None:
    """The first fear-based or fatalistic phrase in ``text`` outside the ``quoted``
    passages, else None.  Each exact quoted passage is removed (longest first) first."""
    remaining = text
    for passage in sorted({item for item in quoted if item}, key=len, reverse=True):
        remaining = remaining.replace(passage, " ")
    match = WEALTH_FEAR_LANGUAGE.search(remaining)
    return match.group() if match else None
