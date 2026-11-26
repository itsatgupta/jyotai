"""NEXT-PROVISIONAL-01: attach matched provisional rules to an answer, only on request.

This runs after the reviewed answer is complete and never changes it: no reviewed text,
claim, ledger, evidence item, rule review type or benchmark count depends on it.  It adds
``provisional_interpretations`` only when the request sets ``include_provisional``.

Guards: every displayed provisional sentence passes the ranking and evaluative guards and
may not call itself reviewed.  A sentence that fails is dropped (fail closed).

NEXT-MARRIAGE-01: a rule whose wording is held shows only the held notice; its draft
translation is not sent (it stays in the final review pack).  Marriage items also pass the
marriage wording guard (no fear-based or fatalistic wording).

NEXT-WEALTH-01: Wealth items pass the wealth wording guard (no poverty, loss or debt
wording); a shown rule whose translation is held sends the reason instead of the translation.
"""

import re
from collections.abc import Callable, Mapping

from astrologer.composition.comparison_guard import ranking_violation
from astrologer.composition.evaluative_guard import evaluative_violation
from astrologer.composition.marriage_guard import marriage_wording_violation
from astrologer.composition.models import (
    ProvisionalInterpretation,
    ProvisionalJustificationView,
)
from astrologer.composition.wealth_guard import wealth_wording_violation
from astrologer.knowledge.provisional import (
    ProvisionalCorpus,
    evaluate_provisional,
    provisional_badge,
)
from astrologer.knowledge.provisional_signification import ProvisionalSignificationCorpus

# Domain wording guards applied to every provisional statement and placement line.
_DOMAIN_GUARDS: dict[str, Callable[[str], str | None]] = {
    "marriage": marriage_wording_violation,
    "wealth": wealth_wording_violation,
}
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
        if _domain_guard_fails(domain, rule.statement, placement):
            continue
        justification = rule.justification
        held = rule.wording == "held"
        translation_held = held or rule.translation_held_reason is not None
        items.append(
            ProvisionalInterpretation(
                rule_id=rule.rule_id,
                rule_version=rule.rule.rule_version,
                badge=provisional_badge(justification.confidence),
                domain=rule.domain.value,
                placement_explanation=placement,
                statement=rule.statement,
                fact_ids=result.resolved_fact_ids,
                corpus_release=corpus.release_id,
                justification=ProvisionalJustificationView(
                    source_work=justification.source_work,
                    locator=justification.locator,
                    original_text=justification.original_text,
                    draft_translation=(
                        None if translation_held else justification.draft_translation
                    ),
                    interpretive_reasoning=justification.interpretive_reasoning,
                    conventions=justification.conventions,
                    confidence=justification.confidence.value,
                    author=justification.author,
                    status="provisional",
                    transcription_notes=justification.transcription_notes,
                    held_reason=rule.held_reason or rule.translation_held_reason,
                ),
                wording_held=held,
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


def _domain_guard_fails(domain: str, *texts: str) -> bool:
    guard = _DOMAIN_GUARDS.get(domain)
    return guard is not None and any(guard(text) is not None for text in texts)


def _passes_guards(*texts: str) -> bool:
    return all(
        ranking_violation(text) is None
        and evaluative_violation(text) is None
        and _REVIEWED.search(text) is None
        for text in texts
    )


def provisional_signification_items(
    corpus: ProvisionalSignificationCorpus, facts: Mapping[str, object], domain: str
) -> tuple[ProvisionalInterpretation, ...]:
    """NEXT-MARRIAGE-02: the domain's provisional signification terms, each with the chart's
    calculated D1 subject (the house's sign and lord, or the graha's house) and its full
    justification.  A term whose subject facts are unavailable is left out (UNKNOWN)."""
    items: list[ProvisionalInterpretation] = []
    for term in corpus.for_domain(domain):
        subject = _subject(term.subject_kind, term.subject, facts)
        if subject is None:
            continue
        placement, fact_ids = subject
        if not _passes_guards(term.statement, placement):
            continue
        if _domain_guard_fails(domain, term.statement, placement):
            continue
        justification = term.justification
        held = term.translation_held_reason is not None
        items.append(
            ProvisionalInterpretation(
                rule_id=term.term_id,
                rule_version=term.term_version,
                badge=provisional_badge(justification.confidence),
                domain=domain,
                placement_explanation=placement,
                statement=term.statement,
                fact_ids=fact_ids,
                corpus_release=corpus.release_id,
                justification=ProvisionalJustificationView(
                    source_work=justification.source_work,
                    locator=justification.locator,
                    original_text=justification.original_text,
                    draft_translation=None if held else justification.draft_translation,
                    interpretive_reasoning=justification.interpretive_reasoning,
                    conventions=justification.conventions,
                    confidence=justification.confidence.value,
                    author=justification.author,
                    status="provisional",
                    transcription_notes=justification.transcription_notes,
                    held_reason=term.translation_held_reason,
                ),
                kind="signification",
            )
        )
    return tuple(items)


def _subject(
    kind: str, subject: str, facts: Mapping[str, object]
) -> tuple[str, tuple[str, ...]] | None:
    if kind == "graha":
        fact_id = f"jyotish.d1.planet.{subject}.placement_house"
        house = facts.get(fact_id)
        if not isinstance(house, int) or isinstance(house, bool) or house not in _ORDINALS:
            return None
        return (
            f"Provisional signification: {subject.title()}, placed in your D1 "
            f"{_numeric_ordinal(house)} house.",
            (fact_id,),
        )
    sign_id, lord_id = f"jyotish.d1.house.{subject}.sign", f"jyotish.d1.house.{subject}.lord"
    sign, lord = facts.get(sign_id), facts.get(lord_id)
    if not isinstance(sign, str) or not isinstance(lord, str):
        return None
    return (
        f"Provisional signification: your D1 {_numeric_ordinal(int(subject))} house, "
        f"{sign.title()}, whose lord is {lord.title()}.",
        (sign_id, lord_id),
    )


def _numeric_ordinal(number: int) -> str:
    suffix = (
        "th" if 10 <= number % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    )
    return f"{number}{suffix}"
