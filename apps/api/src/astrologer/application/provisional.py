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

NEXT-PROPERTY-01: Property items pass the property wording guard (no loss, dispute or accident
wording, no buy/sell advice).

NEXT-CHILDREN-GUARD-01: in every domain, every text an item sends (statement, placement,
reasoning, conventions, notes, held reason and any sent translation) passes the children
wording guard: no child-sex word outside the पुत्र / सुत gloss, no childlessness or loss
wording, and पुत्र or सुत only in a record with the gloss convention (``PUTRA_CONVENTION``).
The source verse is quoted verbatim, except one with a child-sex or childlessness clause
(``source_child_clause``) or with पुत्र / सुत but no recorded convention: it is held.  Text the
guard holds is replaced by a notice and the item stays: a held statement by the held
statement (``wording_held``), a held source verse by ``SOURCE_HELD_NOTICE``
(``original_text_held``), a held translation by the app's held-translation line, any other
held field by ``CHILD_HELD_NOTICE``.  The record itself is unchanged and the review pack
keeps every verse in full.
"""

import logging
import re
from collections.abc import Callable, Mapping
from typing import NamedTuple

from astrologer.composition.children_guard import (
    CHILD_HELD_NOTICE,
    PUTRA_CONVENTION,
    SOURCE_HELD_NOTICE,
    child_wording_violation,
    has_child_term,
    source_child_clause,
)
from astrologer.composition.comparison_guard import ranking_violation
from astrologer.composition.evaluative_guard import evaluative_violation
from astrologer.composition.marriage_guard import marriage_wording_violation
from astrologer.composition.models import (
    ProvisionalInterpretation,
    ProvisionalJustificationView,
)
from astrologer.composition.property_guard import property_wording_violation
from astrologer.composition.wealth_guard import wealth_wording_violation
from astrologer.knowledge.provisional import (
    HELD_STATEMENT,
    ProvisionalCorpus,
    ProvisionalJustification,
    evaluate_provisional,
    provisional_badge,
)
from astrologer.knowledge.provisional_signification import ProvisionalSignificationCorpus

# Domain wording guards applied to every provisional statement and placement line.
_DOMAIN_GUARDS: dict[str, Callable[[str], str | None]] = {
    "marriage": marriage_wording_violation,
    "wealth": wealth_wording_violation,
    "property": property_wording_violation,
}
_LOGGER = logging.getLogger(__name__)
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
        held = rule.wording == "held"
        shown = _children_guarded(
            rule.rule_id,
            rule.justification,
            statement=rule.statement,
            placement=placement,
            wording_held=held,
            translation_held=held or rule.translation_held_reason is not None,
            held_reason=rule.held_reason or rule.translation_held_reason,
        )
        items.append(
            ProvisionalInterpretation(
                rule_id=rule.rule_id,
                rule_version=rule.rule.rule_version,
                badge=provisional_badge(rule.justification.confidence),
                domain=rule.domain.value,
                placement_explanation=shown.placement,
                statement=shown.statement,
                fact_ids=result.resolved_fact_ids,
                corpus_release=corpus.release_id,
                justification=shown.justification,
                wording_held=shown.wording_held,
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


class _Shown(NamedTuple):
    statement: str
    placement: str
    wording_held: bool
    justification: ProvisionalJustificationView


def _children_guarded(
    item_id: str,
    justification: ProvisionalJustification,
    *,
    statement: str,
    placement: str,
    wording_held: bool,
    translation_held: bool,
    held_reason: str | None,
) -> _Shown:
    """The item's display fields after the children guard (NEXT-CHILDREN-GUARD-01): every
    field the guard holds shows a notice instead; the item is never dropped for it."""
    glossed = PUTRA_CONVENTION in justification.conventions
    held_fields: list[str] = []

    def holds(text: str) -> bool:
        return (
            child_wording_violation(text) is not None
            or source_child_clause(text) is not None
            or (has_child_term(text) and not glossed)
        )

    def guarded(name: str, text: str) -> str:
        if not holds(text):
            return text
        held_fields.append(name)
        return CHILD_HELD_NOTICE

    if holds(statement):
        held_fields.append("statement")
        statement, wording_held, translation_held = HELD_STATEMENT, True, True
        held_reason = CHILD_HELD_NOTICE
    original = justification.original_text
    original_held = source_child_clause(original) is not None or (
        has_child_term(original) and not glossed
    )
    if original_held:
        held_fields.append("original_text")
    translation = None if translation_held else justification.draft_translation
    if translation is not None and holds(translation):
        held_fields.append("draft_translation")
        translation = None
        held_reason = held_reason or CHILD_HELD_NOTICE
    notes = justification.transcription_notes
    view = ProvisionalJustificationView(
        source_work=justification.source_work,
        locator=justification.locator,
        original_text=SOURCE_HELD_NOTICE if original_held else original,
        original_text_held=original_held,
        draft_translation=translation,
        interpretive_reasoning=guarded("reasoning", justification.interpretive_reasoning),
        conventions=tuple(
            dict.fromkeys(guarded("convention", item) for item in justification.conventions)
        ),
        confidence=justification.confidence.value,
        author=justification.author,
        status="provisional",
        transcription_notes=guarded("notes", notes) if notes is not None else None,
        held_reason=guarded("held_reason", held_reason) if held_reason is not None else None,
    )
    shown = _Shown(statement, guarded("placement", placement), wording_held, view)
    if held_fields:
        _LOGGER.info("provisional item %s: children guard holds %s", item_id, held_fields)
    return shown


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
        shown = _children_guarded(
            term.term_id,
            term.justification,
            statement=term.statement,
            placement=placement,
            wording_held=False,
            translation_held=term.translation_held_reason is not None,
            held_reason=term.translation_held_reason,
        )
        items.append(
            ProvisionalInterpretation(
                rule_id=term.term_id,
                rule_version=term.term_version,
                badge=provisional_badge(term.justification.confidence),
                domain=domain,
                placement_explanation=shown.placement,
                statement=shown.statement,
                fact_ids=fact_ids,
                corpus_release=corpus.release_id,
                justification=shown.justification,
                wording_held=shown.wording_held,
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
