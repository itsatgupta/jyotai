"""An AI agent is never a reviewer: reject review records that name or cite one.

Governance (``docs/HANDOVER.md``): new doctrine enters only through independent human
review, and "an AI preparer is never a reviewer".  The ``jyotish-prereview`` sub-agent
(``.claude/agents/jyotish-prereview.md``) writes proposals under ``research/prereview/``;
those proposals are working material for the human reviewer and may never stand in for a
review.  Every admission path calls :func:`ai_review_violation` on each review record.

- ``reviewer`` must not name an AI, an agent, the preparer, or a pre-review.
- ``notes`` must not cite a pre-review or an AI agent as the basis of the decision.  Notes
  may still mention "the preparer's draft" (the packet's own term for its drafted text),
  which records provenance, not who decided.
"""

import re
from typing import Final

from astrologer.knowledge.models import ReviewRecord

_PREREVIEW: Final = r"pre-?reviews?"
_AI_REVIEWER: Final = re.compile(
    rf"{_PREREVIEW}|\b(?:ai|assistant|claude|gpt|chatgpt|llm|model|preparer|bot|"
    r"agents?|sub-?agents?)\b",
    re.IGNORECASE,
)
_AI_IN_NOTES: Final = re.compile(
    rf"{_PREREVIEW}|\bsub-?agents?\b|\b(?:claude|gpt|chatgpt|llm)\b|"
    r"\bai[ -](?:agents?|assistants?|preparers?|models?|reviewers?)\b",
    re.IGNORECASE,
)


def ai_review_violation(review: ReviewRecord) -> str | None:
    """Why ``review`` cannot count as a human review, or None if it can."""
    if match := _AI_REVIEWER.search(review.reviewer):
        return f"reviewer {review.reviewer!r} names an AI agent or pre-review ({match.group()!r})"
    if review.notes and (match := _AI_IN_NOTES.search(review.notes)):
        return f"review notes cite an AI agent or pre-review ({match.group()!r})"
    return None
