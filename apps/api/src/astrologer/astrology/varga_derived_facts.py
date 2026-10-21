"""Internal, production-inert structural projection of completed D9 and D10 charts.

The Varga longitude is a divisional coordinate, not a new ephemeris position.
Only signs and house numbers already supplied by the deterministic chart are read.
"""

from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from astrologer.astrology.chart import ChartMethodology, ZodiacSign
from astrologer.astrology.ephemeris import CelestialBody, EphemerisProvenance, HouseSystem
from astrologer.astrology.vargas import (
    DivisionalChart,
    DivisionalChartType,
    VargaMappingVariant,
    VargaMethodology,
)
from astrologer.knowledge.models import ChartScope, FactContract

_SIGNS = tuple(ZodiacSign)
_BODIES = tuple(CelestialBody)
_HOUSE_NUMBERS = tuple(range(1, 13))
FACT_ORDERING_VERSION: Final = "jyotish-varga-structural-fact-order-v1"


class VargaDerivedFactInputError(ValueError):
    """A chart does not satisfy the selected Varga structural methodology."""


class VargaStructuralFact(BaseModel):
    model_config = ConfigDict(frozen=True)

    fact_id: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$")
    value: bool | int | str


class VargaFactMethodology(BaseModel):
    model_config = ConfigDict(frozen=True)

    methodology_id: str
    methodology_version: Literal["v1"] = "v1"
    chart_scope: ChartScope
    fact_ordering_version: Literal["jyotish-varga-structural-fact-order-v1"] = FACT_ORDERING_VERSION

    @model_validator(mode="after")
    def scope_matches_methodology(self) -> "VargaFactMethodology":
        if self.methodology_id != _SPECIFICATIONS[self.chart_scope][1]:
            raise ValueError("Varga fact methodology does not match chart scope")
        return self


class VargaFactProvenance(BaseModel):
    model_config = ConfigDict(frozen=True)

    chart_scope: ChartScope
    methodology: VargaFactMethodology
    source_varga_methodology: VargaMethodology
    source_chart_methodology: ChartMethodology
    inherited_ephemeris_provenance: EphemerisProvenance
    calculation_methodology_identity: str
    position_origin: Literal["deterministic_varga_transformation"] = (
        "deterministic_varga_transformation"
    )
    longitude_semantics: Literal["divisional_coordinate_not_astronomical_position"] = (
        "divisional_coordinate_not_astronomical_position"
    )
    fact_count: int = Field(ge=0)

    @model_validator(mode="after")
    def identities_agree(self) -> "VargaFactProvenance":
        chart_type, _, factor, variant = _SPECIFICATIONS[self.chart_scope]
        if self.methodology.chart_scope is not self.chart_scope:
            raise ValueError("provenance chart scope differs from fact methodology")
        if (
            self.source_varga_methodology.chart_type is not chart_type
            or self.source_varga_methodology.division_factor != factor
            or self.source_varga_methodology.mapping_variant is not variant
            or self.source_varga_methodology.source_chart_methodology
            != self.source_chart_methodology
            or self.calculation_methodology_identity != variant.value
        ):
            raise ValueError("provenance does not match deterministic Varga methodology")
        return self


class VargaFactBundle(BaseModel):
    model_config = ConfigDict(frozen=True)

    provenance: VargaFactProvenance
    facts: tuple[VargaStructuralFact, ...]

    @model_validator(mode="after")
    def facts_match_scope_and_contract(self) -> "VargaFactBundle":
        contract = _CONTRACTS[self.provenance.chart_scope]
        identifiers = tuple(fact.fact_id for fact in self.facts)
        if identifiers != contract.available_fact_ids:
            raise ValueError("Varga facts must exactly match the ordered scope-specific contract")
        if self.provenance.fact_count != len(self.facts):
            raise ValueError("Varga provenance fact count differs from facts")
        return self


def _fact_ids(scope: ChartScope) -> tuple[str, ...]:
    prefix = "jyotish.d9" if scope is ChartScope.D9_NAVAMSA else "jyotish.d10"
    return (
        *(f"{prefix}.house.{number}.sign" for number in _HOUSE_NUMBERS),
        *(f"{prefix}.planet.{body.value}.sign" for body in _BODIES),
        *(f"{prefix}.planet.{body.value}.placement_house" for body in _BODIES),
        *(
            f"{prefix}.same_sign.{left.value}.{right.value}"
            for index, left in enumerate(_BODIES)
            for right in _BODIES[index + 1 :]
        ),
    )


_SPECIFICATIONS: Final = {
    ChartScope.D9_NAVAMSA: (
        DivisionalChartType.D9,
        "jyotish-d9-derived-facts-v1",
        9,
        VargaMappingVariant.PARASHARI_NAVAMSA,
    ),
    ChartScope.D10_DASAMSA: (
        DivisionalChartType.D10,
        "jyotish-d10-derived-facts-v1",
        10,
        VargaMappingVariant.PARASHARI_DASAMSA,
    ),
}

D9_FACT_CONTRACT: Final = FactContract(
    contract_id="jyotish.d9.structural",
    contract_version="v1",
    chart_scope=ChartScope.D9_NAVAMSA,
    methodology_id="jyotish-d9-derived-facts-v1",
    available_fact_ids=_fact_ids(ChartScope.D9_NAVAMSA),
)
D10_FACT_CONTRACT: Final = FactContract(
    contract_id="jyotish.d10.structural",
    contract_version="v1",
    chart_scope=ChartScope.D10_DASAMSA,
    methodology_id="jyotish-d10-derived-facts-v1",
    available_fact_ids=_fact_ids(ChartScope.D10_DASAMSA),
)
_CONTRACTS: Final = {
    ChartScope.D9_NAVAMSA: D9_FACT_CONTRACT,
    ChartScope.D10_DASAMSA: D10_FACT_CONTRACT,
}


class VargaStructuralFactsEngine:
    """Project four safe fact families for an explicitly selected D9 or D10 scope."""

    def calculate(self, chart: DivisionalChart, scope: ChartScope) -> VargaFactBundle:
        if scope not in _SPECIFICATIONS:
            raise VargaDerivedFactInputError("only d9_navamsa and d10_dasamsa are supported")
        _validate_chart(chart, scope)
        _, methodology_id, _, variant = _SPECIFICATIONS[scope]
        prefix = "jyotish.d9" if scope is ChartScope.D9_NAVAMSA else "jyotish.d10"
        planets = {planet.body: planet for planet in chart.planets}
        houses = {house.number: house for house in chart.houses}
        facts = (
            *(
                VargaStructuralFact(
                    fact_id=f"{prefix}.house.{number}.sign", value=houses[number].sign.value
                )
                for number in _HOUSE_NUMBERS
            ),
            *(
                VargaStructuralFact(
                    fact_id=f"{prefix}.planet.{body.value}.sign", value=planets[body].sign.value
                )
                for body in _BODIES
            ),
            *(
                VargaStructuralFact(
                    fact_id=f"{prefix}.planet.{body.value}.placement_house",
                    value=planets[body].house_number,
                )
                for body in _BODIES
            ),
            *(
                VargaStructuralFact(
                    fact_id=f"{prefix}.same_sign.{left.value}.{right.value}",
                    value=planets[left].sign is planets[right].sign,
                )
                for index, left in enumerate(_BODIES)
                for right in _BODIES[index + 1 :]
            ),
        )
        return VargaFactBundle(
            provenance=VargaFactProvenance(
                chart_scope=scope,
                methodology=VargaFactMethodology(methodology_id=methodology_id, chart_scope=scope),
                source_varga_methodology=chart.methodology,
                source_chart_methodology=chart.methodology.source_chart_methodology,
                inherited_ephemeris_provenance=chart.provenance,
                calculation_methodology_identity=variant.value,
                fact_count=len(facts),
            ),
            facts=facts,
        )


def _validate_chart(chart: DivisionalChart, scope: ChartScope) -> None:
    if not isinstance(chart, DivisionalChart):
        raise VargaDerivedFactInputError("Varga facts require a D9/D10 DivisionalChart")
    chart_type, _, factor, variant = _SPECIFICATIONS[scope]
    methodology = chart.methodology
    if (
        methodology.chart_type is not chart_type
        or methodology.division_factor != factor
        or methodology.mapping_variant is not variant
    ):
        raise VargaDerivedFactInputError(f"{scope.value} requires a matching D9/D10 Varga chart")
    if (
        methodology.source_chart_methodology.chart_type != "D1/Rashi"
        or methodology.source_chart_methodology.configuration.house_system
        is not HouseSystem.WHOLE_SIGN
    ):
        raise VargaDerivedFactInputError("Varga facts require a Whole Sign D1 source chart")
    if len(chart.houses) != 12 or tuple(house.number for house in chart.houses) != _HOUSE_NUMBERS:
        raise VargaDerivedFactInputError("Varga facts require houses ordered one through twelve")
    expected_signs = tuple(
        _SIGNS[(_SIGNS.index(chart.ascendant.sign) + number - 1) % 12] for number in _HOUSE_NUMBERS
    )
    if tuple(house.sign for house in chart.houses) != expected_signs:
        raise VargaDerivedFactInputError("Varga house signs conflict with the divisional ascendant")
    bodies = tuple(planet.body for planet in chart.planets)
    if len(bodies) != len(_BODIES) or set(bodies) != set(_BODIES):
        raise VargaDerivedFactInputError("Varga facts require exactly one of each chart planet")
    house_signs = {house.number: house.sign for house in chart.houses}
    if any(planet.house_number not in house_signs for planet in chart.planets):
        raise VargaDerivedFactInputError("Varga planet has an invalid placement house")
    if any(house_signs[planet.house_number] is not planet.sign for planet in chart.planets):
        raise VargaDerivedFactInputError(
            "Varga planet sign conflicts with supplied placement house"
        )
