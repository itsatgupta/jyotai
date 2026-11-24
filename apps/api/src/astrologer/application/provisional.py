"""NEXT-PROVISIONAL-01: attach matched provisional rules to an answer, only on request.

This runs after the reviewed answer is complete and never changes it: no reviewed text,
claim, ledger, evidence item, rule review type or benchmark count depends on it.  It adds
``provisional_interpretations`` only when the request sets ``include_provisional``.

Guards: every displayed provisional sentence passes the ranking and evaluative guards and
may not call itself reviewed.  A sentence that fails is dropped (fail closed).
"""

import re
from collections.abc import Mapping

from astrologer.composition.comparison_guard import ranking_violation
from astrologer.composition.evaluative_guard import evaluative_violation
from astrologer.composition.models import (
    ProvisionalInterpretation,
    ProvisionalJustificationView,
)
from astrologer.knowledge.provisional import (
    PROVISIONAL_BADGE,
    ProvisionalCorpus,
    evaluate_provisional,
)

_PLACEMENT = re.compile(r"^jyotish\.d1\.house_lord\.(?P<lord>[1-9]|1[0-2])\.placement_house$")
_REVIEWED = re.compile(r"\b(?:reviewed|approved|admitted|certified|verified)\b", re.IGNORECASE)
_ORDINALS = {
    1: "first",
    2: "second",
    3: "third",
    4: "fourth",
    5: "fifth",
    6: "sixth",
    7: "seventh",
    8: "eighth",
    9: "ninth",
    10: "tenth",
    11: "eleventh",
    12: "twelfth",
}


def provisional_interpretations(
    corpus: ProvisionalCorpus, facts: Mapping[str, object], domain: str
) -> tuple[ProvisionalInterpretation, ...]:
    """The domain's matched provisional rules, each with its full justification."""
    items: list[ProvisionalInterpretation] = []
    for rule, result in evaluate_provisional(corpus, facts, domain):
        placement = _placement(result.resolved_fact_ids, facts)
        if placement is None or not _passes_guards(rule.statement, placement):
            continue
        justification = rule.justification
        items.append(
            ProvisionalInterpretation(
                rule_id=rule.rule_id,
                rule_version=rule.rule.rule_version,
                badge=PROVISIONAL_BADGE,
                domain=rule.domain.value,
                placement_explanation=placement,
                statement=rule.statement,
                fact_ids=result.resolved_fact_ids,
                corpus_release=corpus.release_id,
                justification=ProvisionalJustificationView(
                    source_work=justification.source_work,
                    locator=justification.locator,
                    original_text=justification.original_text,
                    draft_translation=justification.draft_translation,
                    interpretive_reasoning=justification.interpretive_reasoning,
                    conventions=justification.conventions,
                    confidence=justification.confidence.value,
                    author="project owner, provisional",
                    status="provisional",
                    transcription_notes=justification.transcription_notes,
                ),
            )
        )
    return tuple(items)


def _placement(fact_ids: tuple[str, ...], facts: Mapping[str, object]) -> str | None:
    if len(fact_ids) != 1 or (match := _PLACEMENT.fullmatch(fact_ids[0])) is None:
        return None
    house = facts.get(fact_ids[0])
    if not isinstance(house, int) or house not in _ORDINALS:
        return None
    lord = _ORDINALS[int(match.group("lord"))]
    return f"Your D1 {lord}-house lord is placed in the {_ORDINALS[house]} house."


def _passes_guards(*texts: str) -> bool:
    return all(
        ranking_violation(text) is None
        and evaluative_violation(text) is None
        and _REVIEWED.search(text) is None
        for text in texts
    )
