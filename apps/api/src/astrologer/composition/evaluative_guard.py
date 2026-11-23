"""Evaluative-language guard, parallel to the ranking-word guard (``comparison_guard``).

No strength or polarity model is admitted, so prose may not call a chart, a period or an
indication favourable, auspicious, strong, weak, good, bad, lucky and so on.  The guard
applies to the optional language-model narrative and to deterministic template output, but
**not** to admitted rule text or approved signification terms: those are reviewed wording
quoted verbatim (e.g. an admitted statement that mentions "good companions or friends"), so
they are removed from the text before it is checked.

Gate (docs/HANDOVER.md): ``LLM_ENABLED`` stays off until this guard and the ranking-word guard
pass against a real model on the full benchmark.
"""

import re
from collections.abc import Iterable
from typing import Final

EVALUATIVE_LANGUAGE: Final = re.compile(
    r"\b(?:favou?rabl[ey]|unfavou?rabl[ey]|auspicious(?:ly)?|inauspicious(?:ly)?|"
    r"strong(?:ly)?|weak(?:ly)?|good|bad(?:ly)?|lucky|unlucky|luckily|unluckily|"
    r"fortunate(?:ly)?|unfortunate(?:ly)?|positive(?:ly)?|negative(?:ly)?|excellent|poor(?:ly)?|"
    r"promising|great|ideal|blessed|powerful|harmful|beneficial|benefic|malefic|wonderful|"
    r"terrible|ominous)\b",
    re.IGNORECASE,
)
"""Words that judge a chart, period or indication as good or bad, strong or weak."""


def evaluative_violation(text: str, allowed: Iterable[str] = ()) -> str | None:
    """Return the first evaluative word in ``text`` outside the ``allowed`` passages, else None.

    ``allowed`` holds admitted rule text and approved signification terms.  Each exact
    occurrence is removed (longest first) before the search, so reviewed wording quoted
    verbatim never trips the guard, while the same word anywhere else still does.
    """
    remaining = text
    for passage in sorted({item for item in allowed if item}, key=len, reverse=True):
        remaining = remaining.replace(passage, " ")
    match = EVALUATIVE_LANGUAGE.search(remaining)
    return match.group() if match else None
