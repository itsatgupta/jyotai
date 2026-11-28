"""NEXT-CHILDREN-01: no medical, fatalistic or promising wording in children answers.

The cross-domain hard guard (``children_guard``: no child-sex word, no childlessness or loss
wording) runs first on every text.  This guard adds what a Children answer itself may never
say: a medical statement (fertility, pregnancy, conception, IVF, miscarriage: out of scope,
consult a doctor), a fatalistic pronouncement (dosha, curse, fate, destiny) or a promise of
children ("you will have children", "guaranteed", "assured").  Reviewer verdict (Sitting 1
item 16): a children rule "should never answer 'you will have children' by itself".

It covers every template sentence of a children answer (sections, out-of-scope replies,
provisional statements and placements).  Quoted source text and admitted reviewed statements
are passed as ``quoted`` and removed first, as in the other domain guards.
"""

import re
from collections.abc import Iterable
from typing import Final

CHILDREN_DOMAIN_LANGUAGE: Final = re.compile(
    r"\b(?:fertil\w*|infertil\w*|pregnan\w*|conceiv\w*|conception|ivf|iui|miscarr\w*|"
    r"embryos?|f(?:o)?etus|womb|dosh(?:a|as|am)?|curse(?:s|d)?|doom(?:s|ed)?|fated?|"
    r"destin(?:y|ed)|inevitabl[ey]|guarantee[sd]?|assured|certain(?:ly|ty)?|"
    r"(?:you|you'll|the\s+native)\s+(?:will|shall)\s+(?:have|get|be\s+blessed\s+with)|"
    r"will\s+(?:surely|definitely|certainly)\s+(?:have|get))\b",
    re.IGNORECASE,
)
"""Medical, fatalistic or promising wording barred from children answers outside quoted
source text and admitted statements."""


def children_domain_violation(text: str, quoted: Iterable[str] = ()) -> str | None:
    """The first medical, fatalistic or promising phrase in ``text`` outside ``quoted``,
    else None.  Each exact quoted passage is removed (longest first) first."""
    remaining = text
    for passage in sorted({item for item in quoted if item}, key=len, reverse=True):
        remaining = remaining.replace(passage, " ")
    match = CHILDREN_DOMAIN_LANGUAGE.search(remaining)
    return match.group() if match else None
