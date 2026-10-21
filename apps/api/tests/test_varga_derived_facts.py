"""Synthetic, production-inert D9/D10 structural fact contracts and validation."""

from datetime import UTC, date, datetime, time
from decimal import Decimal

import pytest
from pydantic import ValidationError

from astrologer.astrology.chart import (
    Ascendant,
    Chart,
    ChartMethodology,
    ChartPlanet,
    WholeSignHouse,
    ZodiacSign,
    nakshatra_for_longitude,
)
from astrologer.astrology.ephemeris import (
    CelestialBody,
    EphemerisConfiguration,
    EphemerisProvenance,
    ProviderMetadata,
)
from astrologer.astrology.varga_derived_facts import (
    D9_FACT_CONTRACT,
    D10_FACT_CONTRACT,
    VargaDerivedFactInputError,
    VargaStructuralFactsEngine,
)
from astrologer.astrology.vargas import DivisionalChartType, VargaEngine
from astrologer.birth.models import BirthInput
from astrologer.knowledge.models import ChartScope, FactContract

_BODIES = tuple(CelestialBody)
_SIGNS = tuple(ZodiacSign)
_INSTANT = datetime(2000, 1, 1, tzinfo=UTC)


def _source_chart() -> Chart:
    configuration = EphemerisConfiguration()
    planets = tuple(
        ChartPlanet(
            body=body,
            longitude=Decimal(index * 30),
            sign=_SIGNS[index],
            degree_in_sign=Decimal(0),
            nakshatra=nakshatra_for_longitude(Decimal(index * 30)),
            house_number=index + 1,
        )
        for index, body in enumerate(_BODIES)
    )
    return Chart(
        methodology=ChartMethodology(configuration=configuration),
        birth_input=BirthInput(
            birth_date=date(2000, 1, 1),
            birth_time=time(5, 30),
            timezone="Asia/Kolkata",
            latitude=0,
            longitude=0,
        ),
        calculation_instant=_INSTANT,
        ascendant=Ascendant(
            longitude=Decimal(0),
            sign=ZodiacSign.ARIES,
            degree_in_sign=Decimal(0),
            nakshatra=nakshatra_for_longitude(Decimal(0)),
        ),
        houses=tuple(WholeSignHouse(number=n, sign=_SIGNS[n - 1]) for n in range(1, 13)),
        planets=planets,
        provenance=EphemerisProvenance(
            provider=ProviderMetadata(provider_name="synthetic", provider_version="1"),
            calculation_instant=_INSTANT,
            configuration=configuration,
        ),
    )


@pytest.mark.parametrize(
    ("chart_type", "scope", "contract", "prefix", "methodology_id"),
    [
        (
            DivisionalChartType.D9,
            ChartScope.D9_NAVAMSA,
            D9_FACT_CONTRACT,
            "jyotish.d9",
            "jyotish-d9-derived-facts-v1",
        ),
        (
            DivisionalChartType.D10,
            ChartScope.D10_DASAMSA,
            D10_FACT_CONTRACT,
            "jyotish.d10",
            "jyotish-d10-derived-facts-v1",
        ),
    ],
)
def test_safe_fact_families_order_contract_and_provenance(
    chart_type: DivisionalChartType,
    scope: ChartScope,
    contract: FactContract,
    prefix: str,
    methodology_id: str,
) -> None:
    source = _source_chart()
    chart = VargaEngine().calculate(source, chart_type)
    bundle = VargaStructuralFactsEngine().calculate(chart, scope)
    facts = {fact.fact_id: fact.value for fact in bundle.facts}
    ids = tuple(fact.fact_id for fact in bundle.facts)

    assert ids == contract.available_fact_ids
    assert len(ids) == len(set(ids)) == 66
    assert ids[:12] == tuple(f"{prefix}.house.{n}.sign" for n in range(1, 13))
    assert ids[12:21] == tuple(f"{prefix}.planet.{b.value}.sign" for b in _BODIES)
    assert ids[21:30] == tuple(f"{prefix}.planet.{b.value}.placement_house" for b in _BODIES)
    assert len(ids[30:]) == 36
    for house in chart.houses:
        assert facts[f"{prefix}.house.{house.number}.sign"] == house.sign.value
    for planet in chart.planets:
        assert facts[f"{prefix}.planet.{planet.body.value}.sign"] == planet.sign.value
        assert facts[f"{prefix}.planet.{planet.body.value}.placement_house"] == (
            planet.house_number
        )
    assert facts[f"{prefix}.same_sign.sun.moon"] is (chart.planets[0].sign is chart.planets[1].sign)
    assert bundle == VargaStructuralFactsEngine().calculate(chart, scope)
    assert bundle.provenance.chart_scope is scope
    assert bundle.provenance.methodology.methodology_id == methodology_id
    assert bundle.provenance.methodology.methodology_version == "v1"
    assert bundle.provenance.source_varga_methodology == chart.methodology
    assert bundle.provenance.source_chart_methodology == source.methodology
    assert bundle.provenance.inherited_ephemeris_provenance == source.provenance
    assert bundle.provenance.calculation_methodology_identity == chart.methodology.mapping_variant
    assert bundle.provenance.fact_count == 66
    assert bundle.provenance.longitude_semantics == (
        "divisional_coordinate_not_astronomical_position"
    )
    assert contract.chart_scope is scope
    assert contract.methodology_id == methodology_id
    assert contract.available_fact_family_prefixes == ()
    assert all(".lord" not in key and "house_lord" not in key for key in ids)
    assert all("dignity" not in key and "own_sign" not in key for key in ids)
    assert all("aspect" not in key for key in ids)
    assert all("motion" not in key and "retrograde" not in key for key in ids)


@pytest.mark.parametrize(
    ("chart_type", "scope", "other_scope", "prefix"),
    [
        (DivisionalChartType.D9, ChartScope.D9_NAVAMSA, ChartScope.D10_DASAMSA, "jyotish.d9"),
        (DivisionalChartType.D10, ChartScope.D10_DASAMSA, ChartScope.D9_NAVAMSA, "jyotish.d10"),
    ],
)
def test_same_sign_true_false_and_invalid_inputs(
    chart_type: DivisionalChartType,
    scope: ChartScope,
    other_scope: ChartScope,
    prefix: str,
) -> None:
    chart = VargaEngine().calculate(_source_chart(), chart_type)
    first = chart.planets[0]
    second = chart.planets[1].model_copy(
        update={"sign": first.sign, "house_number": first.house_number}
    )
    together = chart.model_copy(update={"planets": (first, second, *chart.planets[2:])})
    together_bundle = VargaStructuralFactsEngine().calculate(together, scope)
    facts = {fact.fact_id: fact.value for fact in together_bundle.facts}
    assert facts[f"{prefix}.same_sign.sun.moon"] is True
    assert facts[f"{prefix}.same_sign.sun.mars"] is False

    with pytest.raises(VargaDerivedFactInputError, match="matching D9/D10"):
        VargaStructuralFactsEngine().calculate(chart, other_scope)
    with pytest.raises(VargaDerivedFactInputError, match="only d9_navamsa"):
        VargaStructuralFactsEngine().calculate(chart, ChartScope.D1_RASHI)
    with pytest.raises(VargaDerivedFactInputError, match="DivisionalChart"):
        VargaStructuralFactsEngine().calculate(_source_chart(), scope)  # type: ignore[arg-type]
    with pytest.raises(VargaDerivedFactInputError, match="houses ordered"):
        missing_house = chart.model_copy(update={"houses": chart.houses[:-1]})
        VargaStructuralFactsEngine().calculate(missing_house, scope)
    with pytest.raises(VargaDerivedFactInputError, match="exactly one"):
        missing_planet = chart.model_copy(update={"planets": chart.planets[:-1]})
        VargaStructuralFactsEngine().calculate(missing_planet, scope)
    with pytest.raises(VargaDerivedFactInputError, match="conflicts"):
        bad = chart.planets[0].model_copy(update={"house_number": 12})
        VargaStructuralFactsEngine().calculate(
            chart.model_copy(update={"planets": (bad, *chart.planets[1:])}), scope
        )
    with pytest.raises(VargaDerivedFactInputError, match="invalid placement house"):
        bad = chart.planets[0].model_copy(update={"house_number": 0})
        VargaStructuralFactsEngine().calculate(
            chart.model_copy(update={"planets": (bad, *chart.planets[1:])}), scope
        )
    with pytest.raises(VargaDerivedFactInputError, match="matching D9/D10"):
        bad_methodology = chart.methodology.model_copy(update={"division_factor": 2})
        VargaStructuralFactsEngine().calculate(
            chart.model_copy(update={"methodology": bad_methodology}), scope
        )
    bundle = VargaStructuralFactsEngine().calculate(chart, scope)
    with pytest.raises(ValidationError, match="scope-specific contract"):
        type(bundle).model_validate({"provenance": bundle.provenance, "facts": ()})
    with pytest.raises(ValidationError, match="scope-specific contract"):
        wrong_fact = bundle.facts[0].model_copy(update={"fact_id": "jyotish.d1.house.1.sign"})
        type(bundle).model_validate(
            {"provenance": bundle.provenance, "facts": (wrong_fact, *bundle.facts[1:])}
        )
