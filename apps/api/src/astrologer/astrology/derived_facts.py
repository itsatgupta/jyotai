"""Deterministic D1 Jyotish structural facts for ``jyotish-derived-facts-v1``.

This module consumes a completed D1 chart.  It neither calls an ephemeris
provider nor interprets the structural relationships it derives.
"""

from enum import StrEnum
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field

from astrologer.astrology.chart import Chart, ChartMethodology, ZodiacSign
from astrologer.astrology.ephemeris import CelestialBody, EphemerisProvenance, HouseSystem
from astrologer.rules.models import Fact, FactSet

DERIVED_FACTS_METHODOLOGY_ID: Final[Literal["jyotish-derived-facts-v1"]] = (
    "jyotish-derived-facts-v1"
)
SOURCE_REGISTER_VERSION: Final[Literal["task09a-v1-approved-conventions"]] = (
    "task09a-v1-approved-conventions"
)
FACT_ORDERING_VERSION: Final[Literal["jyotish-d1-fact-order-v1"]] = "jyotish-d1-fact-order-v1"

_SIGNS = tuple(ZodiacSign)
_BODIES = tuple(CelestialBody)
_CLASSICAL_BODIES = _BODIES[:7]
_HOUSE_CLASSIFICATIONS: tuple[tuple[str, frozenset[int]], ...] = (
    ("kendra", frozenset({1, 4, 7, 10})),
    ("trikona", frozenset({1, 5, 9})),
    ("dusthana", frozenset({6, 8, 12})),
    ("upachaya", frozenset({3, 6, 10, 11})),
)

# These are explicit JyotAI-v1 computational conventions, not claims about
# every Jyotish tradition. Nodes deliberately have no entry in these tables.
SIGN_RULERS: dict[ZodiacSign, CelestialBody] = {
    ZodiacSign.ARIES: CelestialBody.MARS,
    ZodiacSign.TAURUS: CelestialBody.VENUS,
    ZodiacSign.GEMINI: CelestialBody.MERCURY,
    ZodiacSign.CANCER: CelestialBody.MOON,
    ZodiacSign.LEO: CelestialBody.SUN,
    ZodiacSign.VIRGO: CelestialBody.MERCURY,
    ZodiacSign.LIBRA: CelestialBody.VENUS,
    ZodiacSign.SCORPIO: CelestialBody.MARS,
    ZodiacSign.SAGITTARIUS: CelestialBody.JUPITER,
    ZodiacSign.CAPRICORN: CelestialBody.SATURN,
    ZodiacSign.AQUARIUS: CelestialBody.SATURN,
    ZodiacSign.PISCES: CelestialBody.JUPITER,
}
EXALTATION_SIGNS: dict[CelestialBody, ZodiacSign] = {
    CelestialBody.SUN: ZodiacSign.ARIES,
    CelestialBody.MOON: ZodiacSign.TAURUS,
    CelestialBody.MARS: ZodiacSign.CAPRICORN,
    CelestialBody.MERCURY: ZodiacSign.VIRGO,
    CelestialBody.JUPITER: ZodiacSign.CANCER,
    CelestialBody.VENUS: ZodiacSign.PISCES,
    CelestialBody.SATURN: ZodiacSign.LIBRA,
}
DEBILITATION_SIGNS: dict[CelestialBody, ZodiacSign] = {
    CelestialBody.SUN: ZodiacSign.LIBRA,
    CelestialBody.MOON: ZodiacSign.SCORPIO,
    CelestialBody.MARS: ZodiacSign.CANCER,
    CelestialBody.MERCURY: ZodiacSign.PISCES,
    CelestialBody.JUPITER: ZodiacSign.CAPRICORN,
    CelestialBody.VENUS: ZodiacSign.VIRGO,
    CelestialBody.SATURN: ZodiacSign.ARIES,
}
GRAHA_DRISHTI_HOUSES: dict[CelestialBody, tuple[int, ...]] = {
    CelestialBody.SUN: (7,),
    CelestialBody.MOON: (7,),
    CelestialBody.MARS: (4, 7, 8),
    CelestialBody.MERCURY: (7,),
    CelestialBody.JUPITER: (5, 7, 9),
    CelestialBody.VENUS: (7,),
    CelestialBody.SATURN: (3, 7, 10),
}


class SourceStatus(StrEnum):
    """Status of the approved computational tables' bibliography."""

    REVIEWED_EXACT_LOCATOR = "reviewed_exact_locator"


class DerivedFact(BaseModel):
    """One deterministic scalar structural fact before Task 08 adaptation."""

    model_config = ConfigDict(frozen=True)

    fact_id: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$")
    value: bool | int | str


class DerivedFactsMethodology(BaseModel):
    """Frozen Task 09A-v1 convention and ordering metadata."""

    model_config = ConfigDict(frozen=True)

    methodology_id: Literal["jyotish-derived-facts-v1"] = DERIVED_FACTS_METHODOLOGY_ID
    source_register_version: Literal["task09a-v1-approved-conventions"] = SOURCE_REGISTER_VERSION
    source_status: SourceStatus = SourceStatus.REVIEWED_EXACT_LOCATOR
    chart_type: Literal["D1/Rashi"] = "D1/Rashi"
    applicability: Literal["d1_only"] = "d1_only"
    house_system: Literal["whole_sign"] = "whole_sign"
    graha_drishti_counting: Literal["inclusive_occupied_house_is_one"] = (
        "inclusive_occupied_house_is_one"
    )
    graha_drishti_directionality: Literal["directional"] = "directional"
    rahu_ketu_aspects: Literal["unmodeled"] = "unmodeled"
    rahu_ketu_ownership: Literal["unmodeled"] = "unmodeled"
    rahu_ketu_dignity: Literal["unmodeled"] = "unmodeled"
    same_sign_relationship: Literal["structural_symmetric"] = "structural_symmetric"
    angular_separation: Literal["deferred"] = "deferred"
    fact_ordering_version: Literal["jyotish-d1-fact-order-v1"] = FACT_ORDERING_VERSION
    unavailable_fact_families: tuple[str, ...] = (
        "angular_separation",
        "conjunction_orbs",
        "rahu_ketu_aspects",
        "rahu_ketu_dignity",
        "rahu_ketu_ownership",
        "moolatrikona",
        "deep_exaltation",
        "deep_debilitation",
        "degree_strength",
        "natural_friendship",
        "temporary_friendship",
        "compound_friendship",
        "combustion",
        "dignity_cancellation",
        "shadbala",
        "avasthas",
    )


class DerivedFactProvenance(BaseModel):
    """Task 09A methodology plus references to the D1 calculation provenance."""

    model_config = ConfigDict(frozen=True)

    methodology: DerivedFactsMethodology = Field(default_factory=DerivedFactsMethodology)
    source_chart_methodology: ChartMethodology
    inherited_ephemeris_provenance: EphemerisProvenance


class DerivedFactBundle(BaseModel):
    """Immutable, deterministically ordered D1 structural facts."""

    model_config = ConfigDict(frozen=True)

    provenance: DerivedFactProvenance
    facts: tuple[DerivedFact, ...]


class DerivedFactInputError(ValueError):
    """Raised when a chart cannot safely support the D1-only convention."""


class DerivedFactsEngine:
    """Derive approved Task 09A-v1 structural facts from one canonical D1 chart."""

    def calculate(self, chart: Chart) -> DerivedFactBundle:
        """Derive facts without ephemeris access, rules, or interpretation."""
        _validate_d1_chart(chart)
        planets = {planet.body: planet for planet in chart.planets}
        facts: list[DerivedFact] = []

        for house in chart.houses:
            facts.append(_fact(f"jyotish.d1.house.{house.number}.sign", house.sign.value))
        for house in chart.houses:
            facts.append(
                _fact(f"jyotish.d1.house.{house.number}.lord", SIGN_RULERS[house.sign].value)
            )
        for house in chart.houses:
            lord = SIGN_RULERS[house.sign]
            facts.append(
                _fact(
                    f"jyotish.d1.house_lord.{house.number}.placement_house",
                    planets[lord].house_number,
                )
            )
        for classification, members in _HOUSE_CLASSIFICATIONS:
            for house_number in range(1, 13):
                facts.append(
                    _fact(
                        f"jyotish.d1.house.{house_number}.{classification}",
                        house_number in members,
                    )
                )

        for body in _BODIES:
            facts.append(
                _fact(f"jyotish.d1.planet.{body.value}.placement_house", planets[body].house_number)
            )
        for dignity_name, table in (
            ("own_sign", None),
            ("exaltation_sign", EXALTATION_SIGNS),
            ("debilitation_sign", DEBILITATION_SIGNS),
        ):
            for body in _CLASSICAL_BODIES:
                expected_sign = table[body] if table is not None else None
                value = (
                    SIGN_RULERS[planets[body].sign] is body
                    if expected_sign is None
                    else planets[body].sign is expected_sign
                )
                facts.append(_fact(f"jyotish.d1.planet.{body.value}.{dignity_name}", value))

        aspected_houses_by_body = {
            body: _aspected_houses(planets[body].house_number, GRAHA_DRISHTI_HOUSES[body])
            for body in _CLASSICAL_BODIES
        }
        for body in _CLASSICAL_BODIES:
            aspected_houses = aspected_houses_by_body[body]
            for house_number in range(1, 13):
                facts.append(
                    _fact(
                        f"jyotish.d1.aspect.{body.value}.house.{house_number}",
                        house_number in aspected_houses,
                    )
                )
        for body in _CLASSICAL_BODIES:
            aspected_houses = aspected_houses_by_body[body]
            for target in _BODIES:
                facts.append(
                    _fact(
                        f"jyotish.d1.aspect.{body.value}.planet.{target.value}",
                        planets[target].house_number in aspected_houses,
                    )
                )
        for left_index, left in enumerate(_BODIES):
            for right in _BODIES[left_index + 1 :]:
                facts.append(
                    _fact(
                        f"jyotish.d1.same_sign.{left.value}.{right.value}",
                        planets[left].sign is planets[right].sign,
                    )
                )

        return DerivedFactBundle(
            provenance=DerivedFactProvenance(
                source_chart_methodology=chart.methodology,
                inherited_ephemeris_provenance=chart.provenance,
            ),
            facts=tuple(facts),
        )


def to_fact_set(bundle: DerivedFactBundle) -> FactSet:
    """Adapt ordered Task 09A scalar facts to the isolated Task 08 abstraction."""
    return FactSet(
        facts=tuple(Fact(fact_id=fact.fact_id, value=fact.value) for fact in bundle.facts)
    )


def _fact(fact_id: str, value: bool | int | str) -> DerivedFact:
    return DerivedFact(fact_id=fact_id, value=value)


def _aspected_houses(source_house: int, aspect_numbers: tuple[int, ...]) -> frozenset[int]:
    """Return inclusive Whole Sign targets for the approved aspect numbers."""
    return frozenset(
        ((source_house + aspect_number - 2) % 12) + 1 for aspect_number in aspect_numbers
    )


def _validate_d1_chart(chart: Chart) -> None:
    configuration = chart.methodology.configuration
    if chart.methodology.chart_type != "D1/Rashi":
        raise DerivedFactInputError("derived facts v1 requires a canonical D1/Rashi chart")
    if configuration.house_system is not HouseSystem.WHOLE_SIGN:
        raise DerivedFactInputError("derived facts v1 requires Whole Sign houses")
    if len(chart.houses) != 12 or tuple(house.number for house in chart.houses) != tuple(
        range(1, 13)
    ):
        raise DerivedFactInputError("derived facts v1 requires houses ordered one through twelve")
    expected_house_signs = tuple(
        _SIGNS[(_SIGNS.index(chart.ascendant.sign) + house_number - 1) % 12]
        for house_number in range(1, 13)
    )
    if tuple(house.sign for house in chart.houses) != expected_house_signs:
        raise DerivedFactInputError("derived facts v1 requires consistent Whole Sign house signs")
    bodies = tuple(planet.body for planet in chart.planets)
    if len(bodies) != len(set(bodies)) or set(bodies) != set(_BODIES):
        raise DerivedFactInputError(
            "derived facts v1 requires exactly one position for every D1 body"
        )
    if any(not 1 <= planet.house_number <= 12 for planet in chart.planets):
        raise DerivedFactInputError("derived facts v1 requires valid D1 Whole Sign placements")
