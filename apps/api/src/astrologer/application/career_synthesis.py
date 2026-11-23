"""Governed structural synthesis: co-references between reviewed Career claims and Dasha.

``career-synthesis-v1`` joins two already-governed sides of a Career year answer:

* reviewed claims (approved natal and approved timing interpretations in the plan), and
* calculated ``jyotish.dasha_linkage.v1`` facts for the asked year's MD/AD periods.

It recognises exactly three deterministic co-reference links:

``SAME_PLANET``  a claim's fact ids resolve to a planet that is also a period lord.
``SAME_HOUSE``   a claim's fact ids name a house that a period lord rules or occupies
                 (only when that lord is not already a ``SAME_PLANET`` link for the claim).
``SAME_PERIOD``  a claim's timing window overlaps a planned MD/AD segment of the year.

A link states only the shared reference.  It never combines, weighs, ranks, or explains
meanings, and it never asserts that one side causes the other.  A claim whose fact ids do
not resolve to a planet or house simply has no link; that is not negative evidence.
"""

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta, tzinfo
from typing import Final, Literal

from astrologer.astrology.chart import Chart
from astrologer.astrology.dasha_linkage import (
    DASHA_LINKAGE_METHODOLOGY_ID,
    DashaLordLinkage,
    LinkageStatus,
)
from astrologer.astrology.derived_facts import DerivedFactsEngine
from astrologer.composition.career_claims import CareerClaim, ClaimKind
from astrologer.composition.models import (
    CareerSynthesis,
    ConsultationSection,
    DashaInterpretationSlot,
    DashaSegmentLinkage,
    PlannedDashaSegment,
    SynthesisLink,
)

SYNTHESIS_VERSION: Final = "career-synthesis-v1"
VIMSHOTTARI_METHODOLOGY_ID: Final = "vimshottari-v1"
OUT_OF_SCOPE: Final[tuple[str, ...]] = (
    "claim-agreement-or-conflict: no admitted rule carries an approved polarity, so claims "
    "are never combined, weighed, or set against each other",
    "dasha-interpretation: linkage facts are calculated relationships, not reviewed meanings",
)
WHY_FRAMING: Final = (
    "Each line states only a shared calculated reference between a reviewed indication and a "
    "period; it does not combine, weigh, or rank the indications."
)
YEAR_OUTCOME_LIMIT_ID: Final = "career-year-outcome-unestablished"

_HOUSE_LORD = re.compile(r"^jyotish\.d1\.house\.(\d{1,2})\.lord$")
_HOUSE_LORD_PLACEMENT = re.compile(r"^jyotish\.d1\.house_lord\.(\d{1,2})\.placement_house$")
_PLANET_PLACEMENT = re.compile(r"^jyotish\.d1\.planet\.([a-z]+)\.placement_house$")
_HOUSE_ATTRIBUTE = re.compile(
    r"^jyotish\.d1\.house\.(\d{1,2})\.(?:sign|kendra|trikona|dusthana|upachaya)$"
)
_INTERVAL = re.compile(r"^\[([^,\]]+),([^,)]+)\)$")

Role = Literal["Mahadasha", "Antardasha"]


@dataclass(frozen=True)
class _PlanetReference:
    planet: str
    lord_of_house: int | None
    fact_ids: tuple[str, ...]


@dataclass(frozen=True)
class _HouseReference:
    house: int
    fact_ids: tuple[str, ...]


@dataclass(frozen=True)
class _Period:
    role: Role
    linkage: DashaLordLinkage
    label: str
    segment_ids: tuple[str, ...]


def build_career_synthesis(
    year: int,
    claims: Sequence[CareerClaim],
    chart: Chart,
    linkages: Sequence[DashaSegmentLinkage],
    segments: Sequence[PlannedDashaSegment],
    slot: DashaInterpretationSlot | None,
) -> CareerSynthesis:
    """Return every deterministic co-reference for the year's reviewed Career claims."""
    reviewed = tuple(
        claim
        for claim in claims
        if claim.kind
        in {ClaimKind.APPROVED_INTERPRETATION, ClaimKind.APPROVED_TIMING_INTERPRETATION}
    )
    values = {fact.fact_id: fact.value for fact in DerivedFactsEngine().calculate(chart).facts}
    periods = _periods(linkages, segments)
    links: list[SynthesisLink] = []
    for claim in reviewed:
        planets = _planet_references(claim, values)
        houses = _house_references(claim, values)
        for period in periods:
            rule_ids = _dasha_rule_ids(slot, period.segment_ids)
            planet_link = _same_planet(claim, planets, period, rule_ids)
            if planet_link is not None:
                links.append(planet_link)
                continue
            links.extend(_same_house(claim, houses, period, rule_ids))
        links.extend(_same_period(claim, segments))
    return CareerSynthesis(
        year=year,
        reviewed_claim_ids=tuple(claim.claim_id for claim in reviewed),
        links=tuple(links),
        out_of_scope=OUT_OF_SCOPE,
    )


def why_section(synthesis: CareerSynthesis) -> ConsultationSection:
    """Render the synthesis; every sentence is one link's template text."""
    if not synthesis.reviewed_claim_ids:
        text = (
            f"No reviewed Career indication applies to {synthesis.year}, so there was nothing "
            "to compare with the calculated Dasha periods."
        )
    elif not synthesis.links:
        noun = "indication" if len(synthesis.reviewed_claim_ids) == 1 else "indications"
        text = (
            f"No shared planet, house, or period was found between the reviewed Career {noun} "
            f"and the {synthesis.year} Dasha periods among the calculated links. "
            "Finding none is not evidence for or against any indication."
        )
    else:
        text = f"{' '.join(link.text for link in synthesis.links)} {WHY_FRAMING}"
    return ConsultationSection(
        kind="why",
        text=text,
        framing=WHY_FRAMING if synthesis.links else None,
        synthesis_links=synthesis.links,
    )


def opening_line(
    synthesis: CareerSynthesis,
    claims: Sequence[CareerClaim],
    limitation_ids: Sequence[str],
) -> str:
    """Templated year-answer opening: counts and co-reference presence only, no evaluation."""
    year = synthesis.year
    by_id = {claim.claim_id: claim for claim in claims}
    reviewed = [by_id[claim_id] for claim_id in synthesis.reviewed_claim_ids]
    parts: list[str] = []
    if not reviewed:
        parts.append(f"For {year}, no reviewed Career indication applies.")
    else:
        natal = sum(1 for c in reviewed if c.kind is ClaimKind.APPROVED_INTERPRETATION)
        timed = len(reviewed) - natal
        noun = "indication applies" if len(reviewed) == 1 else "indications apply"
        kinds = _join(
            [
                label
                for count, label in ((natal, f"{natal} natal"), (timed, f"{timed} timing"))
                if count
            ]
        )
        parts.append(f"For {year}, {len(reviewed)} reviewed Career {noun} ({kinds}).")
        lord_links = [link for link in synthesis.links if link.link_type != "SAME_PERIOD"]
        linked = len({link.claim_id for link in lord_links})
        if lord_links:
            lords = _join(
                list(
                    dict.fromkeys(
                        f"{link.period_lord} ({link.period_role})"
                        for link in lord_links
                        if link.period_lord is not None
                    )
                )
            )
            parts.append(
                f"A {year} period lord shares a calculated planet or house reference with "
                f"{linked} of {len(reviewed)}: {lords}."
            )
        else:
            pronoun = "it" if len(reviewed) == 1 else "them"
            parts.append(
                f"No {year} period lord shares a calculated planet or house reference with "
                f"{pronoun} among the calculated links."
            )
    if YEAR_OUTCOME_LIMIT_ID in limitation_ids:
        parts.append(f"No reviewed rule establishes a specific Career event in {year}.")
    return " ".join(parts)


def _periods(
    linkages: Sequence[DashaSegmentLinkage], segments: Sequence[PlannedDashaSegment]
) -> list[_Period]:
    by_segment = {item.segment_id: item for item in linkages}
    order: list[tuple[str, str, str]] = []
    found: dict[tuple[str, str, str], tuple[Role, DashaLordLinkage, str, list[str]]] = {}
    for segment in segments:
        item = by_segment.get(segment.segment_id)
        if item is None:
            continue
        zone = segment.local_start.tzinfo
        md_start = segment.mahadasha_start.isoformat()
        for role, lord, start, end, key in (
            (
                "Mahadasha",
                item.linkage.mahadasha,
                segment.mahadasha_start,
                segment.mahadasha_end,
                ("MD", md_start, ""),
            ),
            (
                "Antardasha",
                item.linkage.antardasha,
                segment.antardasha_start,
                segment.antardasha_end,
                ("AD", md_start, segment.antardasha_start.isoformat()),
            ),
        ):
            if key not in found:
                order.append(key)
                found[key] = (
                    role,  # type: ignore[assignment]
                    lord,
                    f"{role} lord ({_span(start, end, zone)})",
                    [],
                )
            found[key][3].append(segment.segment_id)
    return [
        _Period(role=role, linkage=lord, label=label, segment_ids=tuple(ids))
        for role, lord, label, ids in (found[key] for key in order)
    ]


def _planet_references(
    claim: CareerClaim, values: Mapping[str, object]
) -> tuple[_PlanetReference, ...]:
    references: list[_PlanetReference] = []
    for fact_id in claim.fact_ids:
        if match := _HOUSE_LORD.match(fact_id):
            planet = values.get(fact_id)
            if isinstance(planet, str):
                references.append(_PlanetReference(planet, int(match.group(1)), (fact_id,)))
        elif match := _HOUSE_LORD_PLACEMENT.match(fact_id):
            lord_id = f"jyotish.d1.house.{match.group(1)}.lord"
            planet = values.get(lord_id)
            if isinstance(planet, str):
                references.append(_PlanetReference(planet, int(match.group(1)), (fact_id, lord_id)))
        elif match := _PLANET_PLACEMENT.match(fact_id):
            references.append(_PlanetReference(match.group(1), None, (fact_id,)))
    return tuple(references)


def _house_references(
    claim: CareerClaim, values: Mapping[str, object]
) -> tuple[_HouseReference, ...]:
    references: list[_HouseReference] = []
    for fact_id in claim.fact_ids:
        if match := _HOUSE_LORD.match(fact_id) or _HOUSE_ATTRIBUTE.match(fact_id):
            references.append(_HouseReference(int(match.group(1)), (fact_id,)))
        elif match := _HOUSE_LORD_PLACEMENT.match(fact_id):
            references.append(_HouseReference(int(match.group(1)), (fact_id,)))
            placement = values.get(fact_id)
            if isinstance(placement, int) and not isinstance(placement, bool):
                references.append(_HouseReference(placement, (fact_id,)))
        elif _PLANET_PLACEMENT.match(fact_id):
            placement = values.get(fact_id)
            if isinstance(placement, int) and not isinstance(placement, bool):
                references.append(_HouseReference(placement, (fact_id,)))
    return tuple(references)


def _same_planet(
    claim: CareerClaim,
    references: Sequence[_PlanetReference],
    period: _Period,
    dasha_rule_ids: tuple[str, ...],
) -> SynthesisLink | None:
    lord = period.linkage.lord.value
    matching = [ref for ref in references if ref.planet == lord]
    if not matching:
        return None
    name = lord.title()
    reference = matching[0]
    dasha_ids: list[str] = []
    if reference.lord_of_house is not None:
        ruled = period.linkage.fact("ruled_houses")
        if (
            ruled.status is LinkageStatus.KNOWN
            and isinstance(ruled.value, tuple)
            and reference.lord_of_house in ruled.value
        ):
            dasha_ids.append(ruled.fact_id)
        tenth = period.linkage.fact("is_tenth_lord")
        if reference.lord_of_house == 10 and tenth.status is LinkageStatus.KNOWN and tenth.value:
            dasha_ids.append(tenth.fact_id)
        subject = f"your {_ordinal(reference.lord_of_house)} lord, {name}"
    else:
        subject = name
    if not dasha_ids:
        dasha_ids.append(period.linkage.fact("placement_house").fact_id)
    return SynthesisLink(
        link_type="SAME_PLANET",
        claim_id=claim.claim_id,
        claim_fact_ids=_claim_fact_ids(claim, matching),
        claim_rule_ids=claim.rule_ids,
        dasha_fact_ids=tuple(dict.fromkeys(dasha_ids)),
        dasha_rule_ids=dasha_rule_ids,
        segment_ids=period.segment_ids,
        period_role=period.role,
        period_lord=name,
        shared_reference=f"planet:{lord}",
        text=(
            f"Shared planet, {name}: the {_claim_label(claim)} concerns {subject}, and {name} "
            f"is the {period.label}."
        ),
    )


def _same_house(
    claim: CareerClaim,
    references: Sequence[_HouseReference],
    period: _Period,
    dasha_rule_ids: tuple[str, ...],
) -> list[SynthesisLink]:
    ruled = period.linkage.fact("ruled_houses")
    placement = period.linkage.fact("placement_house")
    ruled_houses = (
        ruled.value
        if ruled.status is LinkageStatus.KNOWN and isinstance(ruled.value, tuple)
        else ()
    )
    occupied = (
        placement.value
        if placement.status is LinkageStatus.KNOWN
        and isinstance(placement.value, int)
        and not isinstance(placement.value, bool)
        else None
    )
    name = period.linkage.lord.value.title()
    links: list[SynthesisLink] = []
    for house in dict.fromkeys(ref.house for ref in references):
        dasha_ids: list[str] = []
        verbs: list[str] = []
        if house in ruled_houses:
            dasha_ids.append(ruled.fact_id)
            verbs.append("rules")
        if house == occupied:
            dasha_ids.append(placement.fact_id)
            verbs.append("occupies")
        if not dasha_ids:
            continue
        matching = [ref for ref in references if ref.house == house]
        ordinal = _ordinal(house)
        links.append(
            SynthesisLink(
                link_type="SAME_HOUSE",
                claim_id=claim.claim_id,
                claim_fact_ids=_claim_fact_ids(claim, matching),
                claim_rule_ids=claim.rule_ids,
                dasha_fact_ids=tuple(dasha_ids),
                dasha_rule_ids=dasha_rule_ids,
                segment_ids=period.segment_ids,
                period_role=period.role,
                period_lord=name,
                shared_reference=f"house:{house}",
                text=(
                    f"Shared house, the {ordinal}: the {_claim_label(claim)} concerns your "
                    f"{ordinal} house, and {name}, the {period.label}, "
                    f"{' and '.join(verbs)} your {ordinal} house."
                ),
            )
        )
    return links


def _same_period(
    claim: CareerClaim, segments: Sequence[PlannedDashaSegment]
) -> list[SynthesisLink]:
    if claim.timing_reference is None:
        return []
    match = _INTERVAL.match(claim.timing_reference)
    if match is None:
        raise ValueError("approved Career timing claim has a malformed interval reference")
    start, end = (datetime.fromisoformat(value) for value in match.groups())
    links: list[SynthesisLink] = []
    for segment in segments:
        lo = max(start, segment.effective_start)
        hi = min(end, segment.effective_end)
        if lo >= hi:
            continue
        zone = segment.local_start.tzinfo
        md = segment.mahadasha_lord.title()
        ad = segment.antardasha_lord.title()
        segment_span = _span(segment.local_start, segment.local_end, zone)
        links.append(
            SynthesisLink(
                link_type="SAME_PERIOD",
                claim_id=claim.claim_id,
                claim_fact_ids=claim.fact_ids or (claim.claim_id,),
                claim_rule_ids=claim.rule_ids,
                dasha_fact_ids=(segment.segment_id,),
                dasha_rule_ids=(VIMSHOTTARI_METHODOLOGY_ID,),
                segment_ids=(segment.segment_id,),
                shared_reference=f"interval:[{lo.isoformat()},{hi.isoformat()})",
                text=(
                    f"Shared period, {_span(lo, hi, zone)}: the window of the "
                    f"{_claim_label(claim)} ({_span(start, end, zone)}) overlaps the {md} "
                    f"Mahadasha, {ad} Antardasha segment ({segment_span})."
                ),
            )
        )
    return links


def _claim_fact_ids(
    claim: CareerClaim, references: Sequence[_PlanetReference | _HouseReference]
) -> tuple[str, ...]:
    resolution = (fact_id for ref in references for fact_id in ref.fact_ids)
    return tuple(dict.fromkeys((*claim.fact_ids, *resolution)))


def _dasha_rule_ids(
    slot: DashaInterpretationSlot | None, segment_ids: Sequence[str]
) -> tuple[str, ...]:
    admitted = tuple(
        dict.fromkeys(
            f"{claim.rule_id}@{claim.rule_version}"
            for claim in (slot.claims if slot is not None else ())
            if claim.segment_id in segment_ids
        )
    )
    return admitted or (DASHA_LINKAGE_METHODOLOGY_ID,)


def _claim_label(claim: CareerClaim) -> str:
    kind = (
        "reviewed Career timing indication"
        if claim.kind is ClaimKind.APPROVED_TIMING_INTERPRETATION
        else "reviewed natal Career indication"
    )
    return f"{kind} ({', '.join(claim.rule_ids)})"


def _span(start: datetime, end: datetime, zone: tzinfo | None) -> str:
    local_start = start.astimezone(zone)
    local_end = (end - timedelta(microseconds=1)).astimezone(zone)
    return f"{_date(local_start)} to {_date(local_end)}"


def _date(value: datetime) -> str:
    return f"{value.day} {value.strftime('%b %Y')}"


def _ordinal(number: int) -> str:
    suffix = (
        "th" if 10 <= number % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    )
    return f"{number}{suffix}"


def _join(items: Sequence[str]) -> str:
    values = list(items)
    if len(values) <= 1:
        return "".join(values)
    return ", ".join(values[:-1]) + " and " + values[-1]
