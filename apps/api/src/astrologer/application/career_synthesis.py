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

Prose never contains claim, rule, or method ids.  Claims are named by plain labels derived
from their fact ids ("the reviewed indication about your 10th lord's placement"); every
rendered sentence keeps its ids in a ``SynthesisSentence`` (the sentence-to-fact mapping).
"""

import re
from collections.abc import Callable, Iterable, Mapping, Sequence
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
    SynthesisSentence,
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
_PLANET_DIGNITY = re.compile(r"^jyotish\.d1\.planet\.([a-z]+)\.(own_sign|exaltation_sign)$")
_INTERVAL = re.compile(r"^\[([^,\]]+),([^,)]+)\)$")
_MAHADASHA_LORD_FACT = "jyotish.timing.vimshottari.mahadasha.lord"
_ROLE_ORDER: Final = {"Mahadasha": 0, "Antardasha": 1}

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
    span: str
    covers_year: bool
    segment_ids: tuple[str, ...]

    @property
    def label(self) -> str:
        return f"{self.role} lord ({self.span})"


def claim_label(claim: CareerClaim) -> str:
    """Plain-language name for a reviewed claim, derived only from its fact ids (no ids)."""
    timed = claim.kind is ClaimKind.APPROVED_TIMING_INTERPRETATION
    if timed and claim.period_lords:
        return f"the reviewed timing indication for {period_name(claim.period_lords)}"
    topic = _topic(claim.fact_ids, timed)
    if topic is None:
        return (
            "the reviewed Career timing indication"
            if timed
            else "the reviewed natal Career indication"
        )
    noun = "the reviewed timing indication" if timed else "the reviewed indication"
    return f"{noun} about {topic}"


def period_name(lords: Sequence[str]) -> str:
    """'Jupiter Mahadasha' or 'Moon Mahadasha with Venus Antardasha' from calculated lords."""
    name = f"{lords[0].title()} Mahadasha"
    if len(lords) > 1:
        name += f" with {lords[1].title()} Antardasha"
    return name


def claim_labels(claims: Sequence[CareerClaim]) -> dict[str, str]:
    """Labels for several claims; identical labels are disambiguated by position."""
    labels = {claim.claim_id: claim_label(claim) for claim in claims}
    totals: dict[str, int] = {}
    for label in labels.values():
        totals[label] = totals.get(label, 0) + 1
    seen: dict[str, int] = {}
    for claim_id, label in labels.items():
        if totals[label] > 1:
            seen[label] = seen.get(label, 0) + 1
            labels[claim_id] = f"{label} ({seen[label]} of {totals[label]})"
    return labels


def _topic(fact_ids: Sequence[str], timed: bool) -> str | None:
    for fact_id in fact_ids:
        if match := _HOUSE_LORD_PLACEMENT.match(fact_id):
            lord = f"your {_ordinal(int(match.group(1)))} lord"
            if timed and _MAHADASHA_LORD_FACT in fact_ids:
                return f"{lord}'s Mahadasha"
            return f"{lord}'s placement"
    dignities: dict[str, list[str]] = {}
    for fact_id in fact_ids:
        if match := _PLANET_DIGNITY.match(fact_id):
            kind = "own" if match.group(2) == "own_sign" else "exaltation"
            dignities.setdefault(match.group(1), []).append(kind)
    for planet, kinds in dignities.items():
        return f"{planet.title()}'s {' or '.join(kinds)} sign"
    for fact_id in fact_ids:
        if match := _PLANET_PLACEMENT.match(fact_id):
            return f"{match.group(1).title()}'s placement"
    for fact_id in fact_ids:
        if match := _HOUSE_LORD.match(fact_id):
            return f"your {_ordinal(int(match.group(1)))} lord"
    for fact_id in fact_ids:
        if match := _HOUSE_ATTRIBUTE.match(fact_id):
            return f"your {_ordinal(int(match.group(1)))} house"
    return None


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
    labels = claim_labels(reviewed)
    year_start = min((segment.effective_start for segment in segments), default=None)
    year_end = max((segment.effective_end for segment in segments), default=None)
    periods = _periods(linkages, segments, year_start, year_end)
    links: list[SynthesisLink] = []
    spanning: list[str] = []
    for claim in reviewed:
        label = labels[claim.claim_id]
        planets = _planet_references(claim, values)
        houses = _house_references(claim, values)
        for period in periods:
            rule_ids = _dasha_rule_ids(slot, period.segment_ids)
            planet_link = _same_planet(claim, label, planets, period, rule_ids)
            if planet_link is not None:
                links.append(planet_link)
                continue
            links.extend(_same_house(claim, label, houses, period, rule_ids))
        period_links = _same_period(claim, label, segments)
        links.extend(period_links)
        window = _window(claim)
        if (
            period_links
            and window is not None
            and year_start is not None
            and year_end is not None
            and window[0] <= year_start
            and window[1] >= year_end
        ):
            spanning.append(claim.claim_id)
    return CareerSynthesis(
        year=year,
        reviewed_claim_ids=tuple(claim.claim_id for claim in reviewed),
        links=tuple(links),
        year_spanning_claim_ids=tuple(spanning),
        out_of_scope=OUT_OF_SCOPE,
    )


def why_section(synthesis: CareerSynthesis) -> ConsultationSection:
    """Render the synthesis: one line per period planet, then the period lines.

    The fixed framing sentence is carried only in ``framing`` (NEXT-TONE-01), where the
    evidence disclosure shows it; the visible text holds the co-reference lines alone.
    """
    sentences = why_sentences(synthesis)
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
        text = " ".join(sentence.text for sentence in sentences)
    return ConsultationSection(
        kind="why",
        text=text,
        framing=WHY_FRAMING if synthesis.links else None,
        synthesis_links=synthesis.links,
        synthesis_sentences=sentences,
    )


def why_sentences(synthesis: CareerSynthesis) -> tuple[SynthesisSentence, ...]:
    """One sentence per (planet, period role), merged across claims and across MD/AD.

    SAME_PERIOD links of a timing claim whose window spans the whole asked year are replaced
    by one sentence saying so; otherwise each SAME_PERIOD link keeps its own sentence.
    """
    total = len(synthesis.reviewed_claim_ids)
    sentences = [
        _lord_sentence(group, total, lambda link: f"({link.period_span})")
        for group in _lord_groups(synthesis.links)
    ]
    by_claim: dict[str, list[SynthesisLink]] = {}
    for link in synthesis.links:
        if link.link_type == "SAME_PERIOD":
            by_claim.setdefault(link.claim_id, []).append(link)
    for claim_id, period_links in by_claim.items():
        if claim_id in synthesis.year_spanning_claim_ids:
            sentences.append(
                _sentence(
                    f"The window of {period_links[0].claim_label} spans all of {synthesis.year}.",
                    period_links,
                )
            )
        else:
            sentences.extend(_sentence(link.text, (link,)) for link in period_links)
    return tuple(sentences)


def co_reference_sentence(
    synthesis: CareerSynthesis, claims: Sequence[CareerClaim] = ()
) -> SynthesisSentence:
    """The direct line's plain statement of which period planet the indications concern."""
    year = synthesis.year
    if not synthesis.reviewed_claim_ids:
        return SynthesisSentence(text="No reviewed Career indication applies.")
    groups = _lord_groups(synthesis.links)
    if not groups:
        reviewed = [claim for claim in claims if claim.claim_id in synthesis.reviewed_claim_ids]
        labels = list(claim_labels(reviewed).values())
        target = (
            "the reviewed indication"
            if len(synthesis.reviewed_claim_ids) == 1
            else "the reviewed indications"
        )
        return SynthesisSentence(
            text=(
                f"No {year} period lord shares a calculated planet or house with "
                f"{_join(labels) if labels else target}."
            ),
            claim_ids=synthesis.reviewed_claim_ids,
        )
    total = len(synthesis.reviewed_claim_ids)
    parts = [
        _lord_sentence(
            group,
            total,
            lambda link: (
                f"throughout {year}" if link.period_covers_year else f"({link.period_span})"
            ),
        )
        for group in groups
    ]
    if len(parts) == 1:
        return parts[0]
    return SynthesisSentence(
        text="; ".join(part.text.rstrip(".") for part in parts) + ".",
        claim_ids=_union(part.claim_ids for part in parts),
        fact_ids=_union(part.fact_ids for part in parts),
        rule_ids=_union(part.rule_ids for part in parts),
        calc_method_ids=_union(part.calc_method_ids for part in parts),
    )


def year_limit_sentence(year: int, limitation_ids: Sequence[str]) -> str | None:
    if YEAR_OUTCOME_LIMIT_ID in limitation_ids:
        return f"No reviewed rule establishes a specific Career event in {year}."
    return None


def _lord_groups(links: Sequence[SynthesisLink]) -> list[list[SynthesisLink]]:
    """Planet/house links grouped by period planet, Mahadasha planets first."""
    groups: dict[str, list[SynthesisLink]] = {}
    for link in links:
        if link.link_type != "SAME_PERIOD" and link.period_lord is not None:
            groups.setdefault(link.period_lord, []).append(link)
    return sorted(
        groups.values(),
        key=lambda group: min(_ROLE_ORDER[link.period_role or "Antardasha"] for link in group),
    )


def _lord_sentence(
    group: Sequence[SynthesisLink],
    total: int,
    when: Callable[[SynthesisLink], str],
) -> SynthesisSentence:
    planet = group[0].period_lord or ""
    roles: dict[str, str] = {}
    for link in sorted(group, key=lambda item: _ROLE_ORDER[item.period_role or "Antardasha"]):
        roles.setdefault(link.period_role or "", when(link))
    phrases = list(roles.values())
    if len(roles) == 1:
        role, phrase = next(iter(roles.items()))
        role_text = f"the {role} lord {phrase}"
    elif len(set(phrases)) == 1:
        role_text = f"both the Mahadasha lord and the Antardasha lord {phrases[0]}"
    else:
        role_text = (
            f"both the Mahadasha lord {roles['Mahadasha']} and the Antardasha lord "
            f"{roles['Antardasha']}"
        )
    subjects: dict[str, list[str]] = {}
    houses: dict[int, tuple[list[str], list[str]]] = {}
    for link in group:
        if link.link_type == "SAME_PLANET":
            labels = subjects.setdefault(link.claim_subject or planet, [])
            if link.claim_label not in labels:
                labels.append(link.claim_label)
        else:
            house = int(link.shared_reference.split(":", 1)[1])
            labels, verbs = houses.setdefault(house, ([], []))
            if link.claim_label not in labels:
                labels.append(link.claim_label)
            for fact_id in link.dasha_fact_ids:
                verb = "rules" if fact_id.endswith(".ruled_houses") else "occupies"
                if verb not in verbs:
                    verbs.append(verb)
    parts = [
        f"{_who(labels, total)} {_concern(labels)} {subject}"
        for subject, labels in subjects.items()
    ]
    parts += [
        f"{_who(labels, total)} {_concern(labels)} your {_ordinal(house)} house"
        for house, (labels, _) in houses.items()
    ]
    if houses:
        house_text = " and ".join(
            f"{' and '.join(verbs)} your {_ordinal(house)} house"
            for house, (_, verbs) in houses.items()
        )
        tail = f"{planet}, {role_text}, {house_text}"
    else:
        tail = f"{planet} is {role_text}"
    text = f"{parts[0]}, and {tail}." if len(parts) == 1 else f"{'; '.join(parts)}; and {tail}."
    return _sentence(text, group)


def _sentence(text: str, links: Sequence[SynthesisLink]) -> SynthesisSentence:
    return SynthesisSentence(
        text=text[0].upper() + text[1:],
        claim_ids=_union((link.claim_id,) for link in links),
        fact_ids=_union((*link.claim_fact_ids, *link.dasha_fact_ids) for link in links),
        rule_ids=_union((*link.claim_rule_ids, *link.dasha_rule_ids) for link in links),
        calc_method_ids=_union(link.calc_method_ids for link in links),
    )


def _who(labels: Sequence[str], total: int) -> str:
    count = len(labels)
    if count == 1:
        return labels[0]
    if count == total:
        return "both reviewed indications" if count == 2 else f"all {count} reviewed indications"
    return f"{_join(labels)} {'both' if count == 2 else 'all'}"


def _concern(labels: Sequence[str]) -> str:
    return "concerns" if len(labels) == 1 else "concern"


def _union(groups: Iterable[Sequence[str]]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group))


def _periods(
    linkages: Sequence[DashaSegmentLinkage],
    segments: Sequence[PlannedDashaSegment],
    year_start: datetime | None,
    year_end: datetime | None,
) -> list[_Period]:
    by_segment = {item.segment_id: item for item in linkages}
    order: list[tuple[str, str, str]] = []
    found: dict[tuple[str, str, str], tuple[Role, DashaLordLinkage, str, bool, list[str]]] = {}
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
                    _span(start, end, zone),
                    year_start is not None
                    and year_end is not None
                    and start <= year_start
                    and end >= year_end,
                    [],
                )
            found[key][4].append(segment.segment_id)
    return [
        _Period(role=role, linkage=lord, span=span, covers_year=covers, segment_ids=tuple(ids))
        for role, lord, span, covers, ids in (found[key] for key in order)
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
    label: str,
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
        claim_label=label,
        claim_subject=subject,
        claim_fact_ids=_claim_fact_ids(claim, matching),
        claim_rule_ids=claim.rule_ids,
        dasha_fact_ids=tuple(dict.fromkeys(dasha_ids)),
        dasha_rule_ids=dasha_rule_ids,
        calc_method_ids=(DASHA_LINKAGE_METHODOLOGY_ID,),
        segment_ids=period.segment_ids,
        period_role=period.role,
        period_lord=name,
        period_span=period.span,
        period_covers_year=period.covers_year,
        shared_reference=f"planet:{lord}",
        text=(
            f"Shared planet, {name}: {label} concerns {subject}, and {name} is the {period.label}."
        ),
    )


def _same_house(
    claim: CareerClaim,
    label: str,
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
                claim_label=label,
                claim_subject=f"your {ordinal} house",
                claim_fact_ids=_claim_fact_ids(claim, matching),
                claim_rule_ids=claim.rule_ids,
                dasha_fact_ids=tuple(dasha_ids),
                dasha_rule_ids=dasha_rule_ids,
                calc_method_ids=(DASHA_LINKAGE_METHODOLOGY_ID,),
                segment_ids=period.segment_ids,
                period_role=period.role,
                period_lord=name,
                period_span=period.span,
                period_covers_year=period.covers_year,
                shared_reference=f"house:{house}",
                text=(
                    f"Shared house, the {ordinal}: {label} concerns your "
                    f"{ordinal} house, and {name}, the {period.label}, "
                    f"{' and '.join(verbs)} your {ordinal} house."
                ),
            )
        )
    return links


def _window(claim: CareerClaim) -> tuple[datetime, datetime] | None:
    if claim.timing_reference is None:
        return None
    match = _INTERVAL.match(claim.timing_reference)
    if match is None:
        raise ValueError("approved Career timing claim has a malformed interval reference")
    start, end = (datetime.fromisoformat(value) for value in match.groups())
    return start, end


def _same_period(
    claim: CareerClaim, label: str, segments: Sequence[PlannedDashaSegment]
) -> list[SynthesisLink]:
    window = _window(claim)
    if window is None:
        return []
    start, end = window
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
                claim_label=label,
                claim_fact_ids=claim.fact_ids or (claim.claim_id,),
                claim_rule_ids=claim.rule_ids,
                dasha_fact_ids=(segment.segment_id,),
                calc_method_ids=(VIMSHOTTARI_METHODOLOGY_ID,),
                segment_ids=(segment.segment_id,),
                shared_reference=f"interval:[{lo.isoformat()},{hi.isoformat()})",
                text=(
                    f"Shared period, {_span(lo, hi, zone)}: the window of "
                    f"{label} ({_span(start, end, zone)}) overlaps the {md} "
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
    """Admitted Dasha interpretation rules only; calculation methods are never rules."""
    return tuple(
        dict.fromkeys(
            f"{claim.rule_id}@{claim.rule_version}"
            for claim in (slot.claims if slot is not None else ())
            if claim.segment_id in segment_ids
        )
    )


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
