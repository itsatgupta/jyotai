"""Language guard for comparison answers: no ranking words and no tallies of matches.

A comparison answer is a factual side-by-side.  Its prose must never rank, weigh, or count
indications as a measure, whether it is produced by the deterministic templates or by the
optional language-model layer.  Both paths are checked with the same patterns.
"""

import re
from typing import Final

RANKING_LANGUAGE: Final = re.compile(
    r"\b(?:better|best|worse|worst|stronger|strongest|weaker|weakest|"
    r"(?:more|less|most|least)\s+(?:favou?rable|promising|auspicious|supportive|positive|"
    r"negative|significant|important|likely)|"
    r"favou?rs?|favou?red|favou?rable|unfavou?rable|fewer|more|less|superior|inferior|"
    r"outweighs?|outranks?|preferable|prefer(?:red|s)?|advantage(?:s|ous)?|disadvantage(?:s|ous)?|"
    r"edge over|winner|wins?|beats?|higher|lower|ahead of|ranks? (?:above|below|higher|lower)|"
    r"top|leading|recommend(?:ed|s)?)\b",
    re.IGNORECASE,
)
"""Comparative or evaluative words that would turn a side-by-side into a verdict."""

MATCH_TALLY: Final = re.compile(
    r"\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|zero)\s+(?:reviewed\s+)?"
    r"(?:timing\s+|natal\s+|career\s+)?(?:indications?|matches|matched\s+rules?|rules?|"
    r"links?|co-references?|hits?)\b|"
    r"\b(?:score[sd]?|scoring|tally|tallies|points?|rating|weight(?:ed|ing)?)\b",
    re.IGNORECASE,
)
"""A number of matches presented as a measure, or score/tally vocabulary."""


def ranking_violation(text: str) -> str | None:
    """Return the first ranking word or match tally in ``text``, or None when it is clean."""
    for pattern in (RANKING_LANGUAGE, MATCH_TALLY):
        match = pattern.search(text)
        if match is not None:
            return match.group()
    return None
