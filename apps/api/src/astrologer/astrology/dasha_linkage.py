"""Deterministic D1 chart-linkage facts for operating Vimshottari Dasha lords.

``jyotish.dasha_linkage.v1`` projects existing ``jyotish-derived-facts-v1`` facts onto the
lords of one operating Mahadasha/Antardasha pair.  It adds no doctrine: it never labels a
relationship, scores a lord, or interprets a period.  Every house is counted from the D1
Lagna (Whole Sign) only.  The single exception, ``ad_house_from_md``, is a plain inclusive
sign count from the Mahadasha lord's sign to the Antardasha lord's sign.
"""

from enum import StrEnum
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator

from astrologer.astrology.chart import Chart, ZodiacSign
from astrologer.astrology.dasha import DashaLord
from astrologer.astrology.derived_facts import DERIVED_FACTS_METHODOLOGY_ID, DerivedFactBundle
from astrologer.astrology.ephemeris import CelestialBody
from astrologer.rules.models import Fact, FactSet

DASHA_LINKAGE_METHODOLOGY_ID: Final[Literal["jyotish.dasha_linkage.v1"]] = (
    "jyotish.dasha_linkage.v1"
)
# Lord-level fact ids, used for display and the sentence -> fact-id mapping.
LORD_FACT_PREFIX: Final = f"{DASHA_LINKAGE_METHODOLOGY_ID}.lord"
PAIR_FACT_PREFIX: Final = f"{DASHA_LINKAGE_METHODOLOGY_ID}.pair"
# Role-based fact ids, used only as rule-evaluation input for admitted Dasha rules.
SEGMENT_FACT_PREFIX: Final = f"{DASHA_LINKAGE_METHODOLOGY_ID}.segment"

_SIGNS: Final = tuple(ZodiacSign)
_BODIES: Final = tuple(CelestialBody)
_CLASSICAL: Final = frozenset(_BODIES[:7])
_FACT_ID = r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$"

LORDSHIP_NOTE: Final = (
    "lordship_convention: classical seven-planet sign rulers; Rahu and Ketu are not "
    "assigned sign rulership under this convention"
)
NODE_ASPECT_NOTE: Final = (
    "aspect_convention: seven-planet graha drishti; Rahu/Ketu aspects are unmodeled"
)
NODE_DIGNITY_NOTE: Final = "dignity_convention: Rahu/Ketu own/exaltation signs are unmodeled"
SELF_TENTH_LORD_NOTE: Final = "this lord is the 10th lord; a relation to itself does not apply"


class LinkageStatus(StrEnum):
    """Availability of one linkage fact.  UNKNOWN is never FALSE."""

    KNOWN = "KNOWN"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


LinkageFactName = Literal[
    "ruled_houses",
    "placement_house",
    "sign",
    "own_sign",
    "exaltation_sign",
    "is_tenth_lord",
    "occupies_tenth",
    "aspects_tenth_house",
    "aspects_tenth_lord",
    "same_sign_as_tenth_lord",
    "ad_house_from_md",
]
LORD_FACT_NAMES: Final[tuple[LinkageFactName, ...]] = (
    "ruled_houses",
    "placement_house",
    "sign",
    "own_sign",
    "exaltation_sign",
    "is_tenth_lord",
    "occupies_tenth",
    "aspects_tenth_house",
    "aspects_tenth_lord",
    "same_sign_as_tenth_lord",
)


class DashaLinkageInputError(ValueError):
    """Raised when the chart and its derived facts do not describe the same D1 chart."""


class LinkageFact(BaseModel):
    """One structural fact about a Dasha lord, traceable to D1 derived facts."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    fact_id: str = Field(pattern=_FACT_ID)
    name: LinkageFactName
    status: LinkageStatus
    value: bool | int | str | tuple[int, ...] | None = None
    source_fact_ids: tuple[str, ...] = ()
    note: str | None = None

    @model_validator(mode="after")
    def status_and_value_must_agree(self) -> "LinkageFact":
        if self.status is LinkageStatus.KNOWN:
            if self.value is None or not self.source_fact_ids:
                raise ValueError("a KNOWN linkage fact needs a value and source fact ids")
        elif self.value is not None:
            raise ValueError("UNKNOWN and NOT_APPLICABLE linkage facts carry no value")
        elif self.note is None:
            raise ValueError("UNKNOWN and NOT_APPLICABLE linkage facts must state why")
        return self


class DashaLinkageMethodology(BaseModel):
    """Frozen conventions; the reference point is the D1 Lagna and nothing else."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    methodology_id: Literal["jyotish.dasha_linkage.v1"] = DASHA_LINKAGE_METHODOLOGY_ID
    reference_point: Literal["d1_lagna"] = "d1_lagna"
    house_system: Literal["whole_sign"] = "whole_sign"
    chart_scope: Literal["D1/Rashi"] = "D1/Rashi"
    lordship_convention: Literal["classical_seven_planet_sign_rulers"] = (
        "classical_seven_planet_sign_rulers"
    )
    rahu_ketu_ownership: Literal["unmodeled"] = "unmodeled"
    aspect_convention: Literal["seven_planet_graha_drishti"] = "seven_planet_graha_drishti"
    rahu_ketu_aspects: Literal["unmodeled"] = "unmodeled"
    dignity_facts: tuple[Literal["own_sign", "exaltation_sign"], ...] = (
        "own_sign",
        "exaltation_sign",
    )
    ad_house_from_md_counting: Literal["inclusive_sign_count_from_mahadasha_lord_sign"] = (
        "inclusive_sign_count_from_mahadasha_lord_sign"
    )
    derived_facts_methodology_id: Literal["jyotish-derived-facts-v1"] = DERIVED_FACTS_METHODOLOGY_ID


class DashaLordLinkage(BaseModel):
    """All linkage facts for one operating Dasha lord."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    lord: DashaLord
    facts: tuple[LinkageFact, ...]

    @model_validator(mode="after")
    def facts_must_be_complete_and_ordered(self) -> "DashaLordLinkage":
        if tuple(fact.name for fact in self.facts) != LORD_FACT_NAMES:
            raise ValueError("lord linkage must carry every lord fact in canonical order")
        return self

    def fact(self, name: LinkageFactName) -> LinkageFact:
        return next(fact for fact in self.facts if fact.name == name)


class DashaPairLinkage(BaseModel):
    """Linkage facts for one operating Mahadasha/Antardasha pair."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    methodology: DashaLinkageMethodology = Field(default_factory=DashaLinkageMethodology)
    mahadasha: DashaLordLinkage
    antardasha: DashaLordLinkage
    ad_house_from_md: LinkageFact

    def fact_ids(self) -> tuple[str, ...]:
        facts = (*self.mahadasha.facts, *self.antardasha.facts, self.ad_house_from_md)
        return tuple(dict.fromkeys(fact.fact_id for fact in facts))


def count_signs_inclusive(from_sign: ZodiacSign, to_sign: ZodiacSign) -> int:
    """Return the 1-12 inclusive count from ``from_sign`` to ``to_sign`` (same sign is 1)."""
    return ((_SIGNS.index(to_sign) - _SIGNS.index(from_sign)) % 12) + 1


def build_lord_linkage(
    chart: Chart, derived: DerivedFactBundle, lord: DashaLord
) -> DashaLordLinkage:
    """Project the D1 derived facts relevant to one Dasha lord, counted from the Lagna."""
    lookup = _lookup(chart, derived)
    body = CelestialBody(lord.value)
    prefix = f"{LORD_FACT_PREFIX}.{lord.value}"

    def fact(
        name: LinkageFactName,
        status: LinkageStatus,
        value: bool | int | str | tuple[int, ...] | None,
        sources: tuple[str, ...],
        note: str | None = None,
    ) -> LinkageFact:
        return LinkageFact(
            fact_id=f"{prefix}.{name}",
            name=name,
            status=status,
            value=value,
            source_fact_ids=sources,
            note=note,
        )

    known = LinkageStatus.KNOWN
    lord_ids = tuple(f"jyotish.d1.house.{house}.lord" for house in range(1, 13))
    ruled = tuple(house for house in range(1, 13) if lookup[lord_ids[house - 1]] == body.value)
    placement_id = f"jyotish.d1.planet.{body.value}.placement_house"
    placement = _int(lookup[placement_id])
    sign_id = f"jyotish.d1.house.{placement}.sign"
    tenth_lord_id = "jyotish.d1.house.10.lord"
    tenth_lord = CelestialBody(str(lookup[tenth_lord_id]))
    is_classical = body in _CLASSICAL
    facts = [
        fact(
            "ruled_houses",
            known,
            ruled,
            lord_ids,
            None if is_classical else LORDSHIP_NOTE,
        ),
        fact("placement_house", known, placement, (placement_id,)),
        fact("sign", known, str(lookup[sign_id]), (placement_id, sign_id)),
    ]
    dignities: tuple[LinkageFactName, ...] = ("own_sign", "exaltation_sign")
    for dignity in dignities:
        dignity_id = f"jyotish.d1.planet.{body.value}.{dignity}"
        facts.append(
            fact(dignity, known, _bool(lookup[dignity_id]), (dignity_id,))
            if is_classical
            else fact(dignity, LinkageStatus.UNKNOWN, None, (), NODE_DIGNITY_NOTE)
        )
    facts.append(
        fact(
            "is_tenth_lord",
            known,
            tenth_lord is body,
            (tenth_lord_id,),
            None if is_classical else LORDSHIP_NOTE,
        )
    )
    facts.append(fact("occupies_tenth", known, placement == 10, (placement_id,)))
    if is_classical:
        house_aspect_id = f"jyotish.d1.aspect.{body.value}.house.10"
        facts.append(
            fact("aspects_tenth_house", known, _bool(lookup[house_aspect_id]), (house_aspect_id,))
        )
    else:
        facts.append(fact("aspects_tenth_house", LinkageStatus.UNKNOWN, None, (), NODE_ASPECT_NOTE))
    if tenth_lord is body:
        not_applicable = LinkageStatus.NOT_APPLICABLE
        facts.append(fact("aspects_tenth_lord", not_applicable, None, (), SELF_TENTH_LORD_NOTE))
        facts.append(
            fact("same_sign_as_tenth_lord", not_applicable, None, (), SELF_TENTH_LORD_NOTE)
        )
    else:
        if is_classical:
            lord_aspect_id = f"jyotish.d1.aspect.{body.value}.planet.{tenth_lord.value}"
            facts.append(
                fact(
                    "aspects_tenth_lord",
                    known,
                    _bool(lookup[lord_aspect_id]),
                    (tenth_lord_id, lord_aspect_id),
                )
            )
        else:
            facts.append(
                fact("aspects_tenth_lord", LinkageStatus.UNKNOWN, None, (), NODE_ASPECT_NOTE)
            )
        left, right = sorted((body, tenth_lord), key=_BODIES.index)
        same_sign_id = f"jyotish.d1.same_sign.{left.value}.{right.value}"
        facts.append(
            fact(
                "same_sign_as_tenth_lord",
                known,
                _bool(lookup[same_sign_id]),
                (tenth_lord_id, same_sign_id),
            )
        )
    return DashaLordLinkage(lord=lord, facts=tuple(facts))


def build_pair_linkage(
    chart: Chart,
    derived: DerivedFactBundle,
    mahadasha_lord: DashaLord,
    antardasha_lord: DashaLord,
) -> DashaPairLinkage:
    """Return linkage facts for both lords of one operating MD/AD pair."""
    mahadasha = build_lord_linkage(chart, derived, mahadasha_lord)
    antardasha = build_lord_linkage(chart, derived, antardasha_lord)
    md_sign = mahadasha.fact("sign")
    ad_sign = antardasha.fact("sign")
    distance = count_signs_inclusive(ZodiacSign(str(md_sign.value)), ZodiacSign(str(ad_sign.value)))
    return DashaPairLinkage(
        mahadasha=mahadasha,
        antardasha=antardasha,
        ad_house_from_md=LinkageFact(
            fact_id=(
                f"{PAIR_FACT_PREFIX}.{mahadasha_lord.value}.{antardasha_lord.value}"
                ".ad_house_from_md"
            ),
            name="ad_house_from_md",
            status=LinkageStatus.KNOWN,
            value=distance,
            source_fact_ids=tuple(
                dict.fromkeys((*md_sign.source_fact_ids, *ad_sign.source_fact_ids))
            ),
        ),
    )


def to_segment_fact_set(pair: DashaPairLinkage) -> FactSet:
    """Adapt KNOWN pair facts to role-based rule input; UNKNOWN/NOT_APPLICABLE are omitted."""
    facts = [
        Fact(fact_id=f"{SEGMENT_FACT_PREFIX}.mahadasha.lord", value=pair.mahadasha.lord.value),
        Fact(fact_id=f"{SEGMENT_FACT_PREFIX}.antardasha.lord", value=pair.antardasha.lord.value),
    ]
    for role, linkage in (("mahadasha", pair.mahadasha), ("antardasha", pair.antardasha)):
        for item in linkage.facts:
            if item.status is LinkageStatus.KNOWN:
                facts.append(
                    Fact(
                        fact_id=f"{SEGMENT_FACT_PREFIX}.{role}.{item.name}",
                        value=_json_value(item.value),
                    )
                )
    facts.append(
        Fact(
            fact_id=f"{SEGMENT_FACT_PREFIX}.ad_house_from_md",
            value=_json_value(pair.ad_house_from_md.value),
        )
    )
    return FactSet(facts=tuple(facts))


def _json_value(value: bool | int | str | tuple[int, ...] | None) -> JsonValue:
    if isinstance(value, tuple):
        return list(value)
    return value


def _lookup(chart: Chart, derived: DerivedFactBundle) -> dict[str, bool | int | str]:
    if derived.provenance.methodology.methodology_id != DERIVED_FACTS_METHODOLOGY_ID:
        raise DashaLinkageInputError("unsupported derived-facts methodology")
    lookup = {fact.fact_id: fact.value for fact in derived.facts}
    for planet in chart.planets:
        placement = lookup.get(f"jyotish.d1.planet.{planet.body.value}.placement_house")
        if placement != planet.house_number:
            raise DashaLinkageInputError("derived facts do not describe the supplied D1 chart")
    return lookup


def _int(value: bool | int | str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise DashaLinkageInputError("expected an integer derived fact")
    return value


def _bool(value: bool | int | str) -> bool:
    if not isinstance(value, bool):
        raise DashaLinkageInputError("expected a boolean derived fact")
    return value
