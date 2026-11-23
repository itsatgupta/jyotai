"""Build and render the calculated Dasha context for planned Career Dasha segments.

Every rendered sentence is generated from linkage fact ids (or the existing D1 10th-lord
fact id it names), plus exactly one fixed framing line.  No sentence evaluates, ranks, or
interprets a lord or period; interpretation can appear only when an admitted Dasha rule
fills the review-gated slot.
"""

from collections.abc import Iterable, Sequence
from datetime import datetime, timedelta, tzinfo
from typing import Final

from astrologer.astrology.chart import Chart
from astrologer.astrology.dasha import DashaLord
from astrologer.astrology.dasha_linkage import (
    DashaLordLinkage,
    LinkageFactName,
    LinkageStatus,
    build_pair_linkage,
)
from astrologer.astrology.derived_facts import DerivedFactsEngine
from astrologer.composition.models import (
    ConsultationSection,
    D1FactReference,
    DashaContextSentence,
    DashaInterpretationSlot,
    DashaSegmentLinkage,
    PlannedDashaSegment,
)
from astrologer.knowledge.dasha_interpretation import DashaInterpretationCorpus

DASHA_CONTEXT_FRAMING: Final = (
    "These are calculated chart relationships, counted from your D1 Lagna; a reviewed Career "
    "interpretation of this Dasha is not yet available."
)
DASHA_CONTEXT_REVIEWED_FRAMING: Final = (
    "These are calculated chart relationships, counted from your D1 Lagna. The following "
    "reviewed Career interpretation of this Dasha comes from an admitted rule:"
)

_DIGNITY_WORDING: Final[tuple[tuple[LinkageFactName, str], ...]] = (
    ("own_sign", "its own sign"),
    ("exaltation_sign", "its exaltation sign"),
)
_TENTH_FACTS: Final[tuple[LinkageFactName, ...]] = (
    "is_tenth_lord",
    "occupies_tenth",
    "aspects_tenth_house",
    "aspects_tenth_lord",
    "same_sign_as_tenth_lord",
)
_ASPECT_FACTS: Final[tuple[LinkageFactName, ...]] = ("aspects_tenth_house", "aspects_tenth_lord")
TENTH_LORD_FACT_ID: Final = "jyotish.d1.house.10.lord"


def build_dasha_context(
    chart: Chart,
    segments: Sequence[PlannedDashaSegment],
    corpus: DashaInterpretationCorpus,
) -> tuple[tuple[DashaSegmentLinkage, ...], DashaInterpretationSlot]:
    """Return per-segment linkage facts and the admitted-rule slot for those segments."""
    derived = DerivedFactsEngine().calculate(chart)
    tenth_lord = next(
        (
            D1FactReference(fact_id=fact.fact_id, value=str(fact.value))
            for fact in derived.facts
            if fact.fact_id == TENTH_LORD_FACT_ID
        ),
        None,
    )
    linkages = tuple(
        DashaSegmentLinkage(
            segment_id=segment.segment_id,
            linkage=build_pair_linkage(
                chart,
                derived,
                DashaLord(segment.mahadasha_lord),
                DashaLord(segment.antardasha_lord),
            ),
            tenth_lord=tenth_lord,
        )
        for segment in segments
    )
    slot = corpus.evaluate((item.segment_id, item.linkage) for item in linkages)
    return linkages, slot


def dasha_context_section(
    linkages: Sequence[DashaSegmentLinkage],
    slot: DashaInterpretationSlot | None,
    segments: Sequence[PlannedDashaSegment],
) -> ConsultationSection | None:
    """Render fact-backed sentences grouped by period, then one framing line.

    The 10th lord is named once from the existing D1 house-lord fact.  Then there is one
    block per Mahadasha and one per Antardasha, each opening with the period's local dates.
    Calculated-FALSE 10th-house relationships for a lord are collapsed into one sentence
    that cites every underlying fact id; UNKNOWN facts keep their own explicit sentence.
    """
    if not linkages:
        return None
    by_segment = {item.segment_id: item for item in linkages}
    ordered = [
        (segment, by_segment[segment.segment_id])
        for segment in segments
        if segment.segment_id in by_segment
    ]
    if len(ordered) != len(linkages):
        raise ValueError("every Dasha linkage needs its planned segment")
    tenth_lord = linkages[0].tenth_lord
    tenth_name = tenth_lord.value.title() if tenth_lord is not None else "your 10th lord"
    sentences: list[DashaContextSentence] = []
    if tenth_lord is not None:
        # The naming sentence also states each operating lord's own TRUE is_tenth_lord fact,
        # so that lord's block does not repeat the clause.
        self_ids = [
            lord.fact("is_tenth_lord").fact_id
            for item in linkages
            for lord in (item.linkage.mahadasha, item.linkage.antardasha)
            if lord.fact("is_tenth_lord").status is LinkageStatus.KNOWN
            and lord.fact("is_tenth_lord").value is True
        ]
        sentences.append(
            DashaContextSentence(
                text=f"Your 10th lord is {tenth_name}.",
                fact_ids=tuple(dict.fromkeys((tenth_lord.fact_id, *self_ids))),
            )
        )
    seen_md: set[tuple[str, str]] = set()
    seen_ad: set[tuple[str, str, str]] = set()
    for segment, item in ordered:
        md_key = (segment.mahadasha_lord, segment.mahadasha_start.isoformat())
        if md_key not in seen_md:
            seen_md.add(md_key)
            label = _period_label(
                item.linkage.mahadasha.lord,
                "Mahadasha",
                segment.mahadasha_start,
                segment.mahadasha_end,
                segment.local_start.tzinfo,
            )
            sentences.extend(
                _lord_sentences(item.linkage.mahadasha, label, tenth_name, tenth_lord is not None)
            )
        ad_key = (*md_key, segment.antardasha_start.isoformat())
        if ad_key in seen_ad:
            continue
        seen_ad.add(ad_key)
        label = _period_label(
            item.linkage.antardasha.lord,
            "Antardasha",
            segment.antardasha_start,
            segment.antardasha_end,
            segment.local_start.tzinfo,
        )
        sentences.extend(
            _lord_sentences(item.linkage.antardasha, label, tenth_name, tenth_lord is not None)
        )
        fact = item.linkage.ad_house_from_md
        md = _name(item.linkage.mahadasha.lord)
        ad = _name(item.linkage.antardasha.lord)
        sentences.append(
            DashaContextSentence(
                text=f"{ad} is in the {_ordinal(_int(fact.value))} sign counted from {md}'s sign.",
                fact_ids=(fact.fact_id,),
            )
        )
    claims = slot.claims if slot is not None else ()
    framing = DASHA_CONTEXT_REVIEWED_FRAMING if claims else DASHA_CONTEXT_FRAMING
    parts = [sentence.text for sentence in sentences] + [framing]
    parts.extend(
        f"{claim.mahadasha_lord.title()} Mahadasha, {claim.antardasha_lord.title()} "
        f"Antardasha: {claim.permitted_wording} [{claim.rule_id} v{claim.rule_version}; "
        f"{claim.source_locator}]"
        for claim in claims
    )
    return ConsultationSection(
        kind="dasha_context",
        text=" ".join(parts),
        fact_sentences=tuple(sentences),
        framing=framing,
        interpretation_rule_ids=tuple(
            dict.fromkeys(f"{claim.rule_id}@{claim.rule_version}" for claim in claims)
        ),
    )


def _period_label(
    lord: DashaLord, role: str, start: datetime, end: datetime, zone: tzinfo | None
) -> str:
    local_start = start.astimezone(zone)
    local_end = (end - timedelta(microseconds=1)).astimezone(zone)
    return f"{_name(lord)} {role} ({_date(local_start)} to {_date(local_end)})"


def _date(value: datetime) -> str:
    return f"{value.day} {value.strftime('%b %Y')}"


def _lord_sentences(
    linkage: DashaLordLinkage, label: str, tenth_name: str, tenth_named: bool
) -> list[DashaContextSentence]:
    name = _name(linkage.lord)
    sentences: list[DashaContextSentence] = []

    ruled = linkage.fact("ruled_houses")
    houses = ruled.value if isinstance(ruled.value, tuple) else ()
    if houses:
        noun = "house" if len(houses) == 1 else "houses"
        text = f"{label}: {name} rules your {_join(_ordinal(h) for h in houses)} {noun}."
    else:
        text = (
            f"{label}: {name} is not assigned sign rulership under the classical "
            "seven-planet lordship convention used here."
        )
    sentences.append(DashaContextSentence(text=text, fact_ids=(ruled.fact_id,)))

    placement = linkage.fact("placement_house")
    sign = linkage.fact("sign")
    placement_ids = [placement.fact_id, sign.fact_id]
    dignity = ""
    for fact_name, wording in _DIGNITY_WORDING:
        dignity_fact = linkage.fact(fact_name)
        if dignity_fact.status is LinkageStatus.KNOWN and dignity_fact.value is True:
            dignity = f", {wording}"
            placement_ids.append(dignity_fact.fact_id)
    sentences.append(
        DashaContextSentence(
            text=(
                f"{name} occupies your {_ordinal(_int(placement.value))} house, "
                f"{str(sign.value).title()}{dignity}."
            ),
            fact_ids=tuple(placement_ids),
        )
    )

    known = {
        fact_name: linkage.fact(fact_name)
        for fact_name in _TENTH_FACTS
        if linkage.fact(fact_name).status is LinkageStatus.KNOWN
    }
    true_names = {n for n, fact in known.items() if fact.value is True}
    if tenth_named:
        # Already stated (and cited) by the "Your 10th lord is X." sentence.
        true_names.discard("is_tenth_lord")
    false_names = {n for n, fact in known.items() if fact.value is not True}
    if true_names:
        sentences.append(
            DashaContextSentence(
                text=f"{name} {_join(_positive_clauses(true_names, tenth_name))}.",
                fact_ids=tuple(known[n].fact_id for n in _TENTH_FACTS if n in true_names),
            )
        )
    if false_names:
        sentences.append(
            DashaContextSentence(
                text=f"{name} {_join(_negative_clauses(false_names, tenth_name))}.",
                fact_ids=tuple(known[n].fact_id for n in _TENTH_FACTS if n in false_names),
            )
        )

    unknown = [
        linkage.fact(fact_name)
        for fact_name in _ASPECT_FACTS
        if linkage.fact(fact_name).status is LinkageStatus.UNKNOWN
    ]
    if unknown:
        targets = {
            "aspects_tenth_house": "your 10th house",
            "aspects_tenth_lord": "your 10th lord",
        }
        subject = " or ".join(targets[fact.name] for fact in unknown)
        sentences.append(
            DashaContextSentence(
                text=(
                    f"Whether {name} aspects {subject} is unknown: "
                    "Rahu and Ketu aspects are not modeled under the seven-planet aspect "
                    "convention used here."
                ),
                fact_ids=tuple(fact.fact_id for fact in unknown),
            )
        )
    return sentences


def _positive_clauses(names: set[LinkageFactName], tenth_name: str) -> list[str]:
    clauses: list[str] = []
    if "is_tenth_lord" in names:
        clauses.append("is your 10th lord")
    if {"occupies_tenth", "aspects_tenth_house"} <= names:
        clauses.append("occupies and aspects your 10th house")
    elif "occupies_tenth" in names:
        clauses.append("occupies your 10th house")
    elif "aspects_tenth_house" in names:
        clauses.append("aspects your 10th house")
    if "aspects_tenth_lord" in names:
        clauses.append(f"aspects {tenth_name}")
    if "same_sign_as_tenth_lord" in names:
        clauses.append(f"is in the same sign as {tenth_name}")
    return clauses


def _negative_clauses(names: set[LinkageFactName], tenth_name: str) -> list[str]:
    clauses: list[str] = []
    if "is_tenth_lord" in names:
        clauses.append("is not your 10th lord")
    if {"occupies_tenth", "aspects_tenth_house"} <= names:
        clauses.append("does not occupy or aspect your 10th house")
    elif "occupies_tenth" in names:
        clauses.append("does not occupy your 10th house")
    elif "aspects_tenth_house" in names:
        clauses.append("does not aspect your 10th house")
    if {"aspects_tenth_lord", "same_sign_as_tenth_lord"} <= names:
        clauses.append(f"has no aspect or same-sign relationship with {tenth_name}")
    elif "aspects_tenth_lord" in names:
        clauses.append(f"does not aspect {tenth_name}")
    elif "same_sign_as_tenth_lord" in names:
        clauses.append(f"is not in the same sign as {tenth_name}")
    return clauses


def _name(lord: DashaLord) -> str:
    return lord.value.title()


def _int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("expected an integer linkage fact")
    return value


def _ordinal(number: int) -> str:
    suffix = (
        "th" if 10 <= number % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    )
    return f"{number}{suffix}"


def _join(items: Iterable[str]) -> str:
    values = list(items)
    if len(values) <= 1:
        return "".join(values)
    return ", ".join(values[:-1]) + " and " + values[-1]
