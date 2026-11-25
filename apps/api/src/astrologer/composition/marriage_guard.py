"""NEXT-MARRIAGE-01: no fear-based or fatalistic wording in marriage answers.

Marriage answers may not frighten or pronounce fate: no "delay", "denial", "unhappy
marriage", "dosha", "doomed" and the like.  The guard covers every template sentence of a
marriage answer (sections, out-of-scope replies, provisional statements and placements).
Quoted source text (the Sanskrit original and its draft translation, shown only in the
evidence disclosure or the review pack) is passed as ``quoted`` and removed before the
check, so a verse quoted verbatim never trips it while the same word anywhere else does.
"""

import re
from collections.abc import Iterable
from typing import Final

FEAR_LANGUAGE: Final = re.compile(
    r"\b(?:delay(?:s|ed|ing)?|deni(?:al|als|ed|es)|deny(?:ing)?|unhapp(?:y|iness)|"
    r"dosh(?:a|as|am)?|doom(?:s|ed)?|curse(?:s|d)?|afflict(?:s|ed|ion|ions)?|ill-fated|"
    r"misfortunes?|dangers?|dangerous|suffer(?:s|ed|ing)?|fatal(?:ism|istic)?|destin(?:y|ed)|"
    r"fated?|inevitabl[ey]|widow(?:ed|hood)?|obstacles?|obstructions?|"
    r"never\s+(?:marry|marries|be\s+married|get\s+married)|"
    r"will\s+not\s+(?:marry|be\s+married|get\s+married)|"
    r"no\s+marriage|(?:bad|broken|failed|troubled|late)\s+marriages?)\b",
    re.IGNORECASE,
)
"""Fear-based or fatalistic wording barred from marriage answers outside quoted source text."""


def marriage_wording_violation(text: str, quoted: Iterable[str] = ()) -> str | None:
    """The first fear-based or fatalistic phrase in ``text`` outside the ``quoted`` source
    passages, else None.  Each exact quoted passage is removed (longest first) first."""
    remaining = text
    for passage in sorted({item for item in quoted if item}, key=len, reverse=True):
        remaining = remaining.replace(passage, " ")
    match = FEAR_LANGUAGE.search(remaining)
    return match.group() if match else None
