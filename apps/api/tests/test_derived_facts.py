"""Synthetic, deterministic tests for Task 09A D1 structural facts."""

from datetime import UTC, date, datetime, time
from decimal import Decimal

import pytest

from astrologer.astrology.chart import (
    Ascendant,
    Chart,
    ChartMethodology,
    ChartPlanet,
    WholeSignHouse,
    ZodiacSign,
    nakshatra_for_longitude,
)
from astrologer.astrology.derived_facts import (
    DEBILITATION_SIGNS,
    EXALTATION_SIGNS,
    GRAHA_DRISHTI_HOUSES,
    SIGN_RULERS,
    DerivedFactInputError,
    DerivedFactsEngine,
    SourceStatus,
    to_fact_set,
)
from astrologer.astrology.ephemeris import (
    CelestialBody,
    EphemerisConfiguration,
    EphemerisProvenance,
    ProviderMetadata,
)
from astrologer.birth.models import BirthInput
from astrologer.knowledge.evaluation import FactEvaluationProvenance, fact_set_sha256
from astrologer.rules.evaluator import RuleEvaluator
from astrologer.rules.models import (
    ConditionDefinition,
    ConditionKind,
    ConditionOperation,
    EvaluationStatus,
    RuleDefinition,
    RuleEffect,
)

_BODIES = tuple(CelestialBody)
_SIGNS = tuple(ZodiacSign)
_INSTANT = datetime(2000, 1, 1, tzinfo=UTC)


def _chart(
    *,
    ascendant: ZodiacSign = ZodiacSign.ARIES,
    planet_signs: dict[CelestialBody, ZodiacSign] | None = None,
) -> Chart:
    signs = planet_signs or {body: _SIGNS[(index + 1) % 12] for index, body in enumerate(_BODIES)}
    configuration = EphemerisConfiguration()
    houses = tuple(
        WholeSignHouse(number=number, sign=_SIGNS[(_SIGNS.index(ascendant) + number - 1) % 12])
        for number in range(1, 13)
    )
    planets = tuple(_planet(body, signs[body], ascendant) for body in _BODIES)
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
            longitude=Decimal(_SIGNS.index(ascendant) * 30),
            sign=ascendant,
            degree_in_sign=Decimal("0"),
            nakshatra=nakshatra_for_longitude(Decimal(_SIGNS.index(ascendant) * 30)),
        ),
        houses=houses,
        planets=planets,
        provenance=EphemerisProvenance(
            provider=ProviderMetadata(provider_name="synthetic", provider_version="1"),
            calculation_instant=_INSTANT,
            configuration=configuration,
        ),
    )


def _planet(body: CelestialBody, sign: ZodiacSign, ascendant: ZodiacSign) -> ChartPlanet:
    longitude = Decimal(_SIGNS.index(sign) * 30)
    return ChartPlanet(
        body=body,
        longitude=longitude,
        sign=sign,
        degree_in_sign=Decimal("0"),
        nakshatra=nakshatra_for_longitude(longitude),
        house_number=((_SIGNS.index(sign) - _SIGNS.index(ascendant)) % 12) + 1,
    )


def _facts(chart: Chart) -> dict[str, bool | int | str]:
    return {fact.fact_id: fact.value for fact in DerivedFactsEngine().calculate(chart).facts}


def test_task09a_bundle_builds_deterministic_bridge_provenance() -> None:
    bundle = DerivedFactsEngine().calculate(_chart())
    provenance = FactEvaluationProvenance.from_derived_fact_bundle(bundle)

    assert provenance == FactEvaluationProvenance.from_derived_fact_bundle(bundle)
    assert provenance.methodology_id == "jyotish-derived-facts-v1"
    assert provenance.source_register_version == "task09a-v1-approved-conventions"
    assert bundle.provenance.methodology.source_status is SourceStatus.REVIEWED_EXACT_LOCATOR
    assert provenance.fact_set_sha256 == fact_set_sha256(to_fact_set(bundle))


def test_rulership_table_covers_every_sign_and_excludes_nodes() -> None:
    assert SIGN_RULERS == {
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
    assert CelestialBody.RAHU not in SIGN_RULERS.values()
    assert CelestialBody.KETU not in SIGN_RULERS.values()


def test_house_lordship_wraps_and_preserves_multiple_owned_houses() -> None:
    facts = _facts(_chart(ascendant=ZodiacSign.AQUARIUS))

    assert facts["jyotish.d1.house.1.sign"] == "aquarius"
    assert facts["jyotish.d1.house.1.lord"] == "saturn"
    assert facts["jyotish.d1.house.12.sign"] == "capricorn"
    assert facts["jyotish.d1.house.12.lord"] == "saturn"
    assert facts["jyotish.d1.house_lord.1.placement_house"] == 10
    assert facts["jyotish.d1.house_lord.12.placement_house"] == 10


def test_house_lord_self_placement_is_structural_only() -> None:
    signs = {body: ZodiacSign.PISCES for body in _BODIES}
    signs[CelestialBody.MARS] = ZodiacSign.ARIES
    facts = _facts(_chart(planet_signs=signs))

    assert facts["jyotish.d1.house.1.lord"] == "mars"
    assert facts["jyotish.d1.house_lord.1.placement_house"] == 1


def test_every_house_classification_is_emitted_and_can_overlap() -> None:
    facts = _facts(_chart())

    assert facts["jyotish.d1.house.1.kendra"] is True
    assert facts["jyotish.d1.house.1.trikona"] is True
    assert facts["jyotish.d1.house.1.dusthana"] is False
    assert facts["jyotish.d1.house.6.dusthana"] is True
    assert facts["jyotish.d1.house.6.upachaya"] is True
    assert facts["jyotish.d1.house.11.upachaya"] is True
    assert len([key for key in facts if ".kendra" in key]) == 12


def test_graha_drishti_is_inclusive_directional_and_expands_to_planets() -> None:
    signs = {body: ZodiacSign.PISCES for body in _BODIES}
    signs[CelestialBody.JUPITER] = ZodiacSign.TAURUS  # house 2 from Aries
    signs[CelestialBody.SATURN] = ZodiacSign.VIRGO  # house 6, Jupiter's 5th aspect
    signs[CelestialBody.MARS] = ZodiacSign.GEMINI  # house 3, not aspected by Jupiter
    facts = _facts(_chart(planet_signs=signs))

    assert facts["jyotish.d1.aspect.jupiter.house.6"] is True
    assert facts["jyotish.d1.aspect.jupiter.house.8"] is True
    assert facts["jyotish.d1.aspect.jupiter.house.10"] is True
    assert facts["jyotish.d1.aspect.jupiter.house.2"] is False
    assert facts["jyotish.d1.aspect.jupiter.planet.saturn"] is True
    assert facts["jyotish.d1.aspect.jupiter.planet.mars"] is False
    assert facts["jyotish.d1.aspect.saturn.planet.jupiter"] is False


@pytest.mark.parametrize(
    ("body", "source_sign", "expected_houses"),
    [
        (CelestialBody.SUN, ZodiacSign.ARIES, {7}),
        (CelestialBody.MOON, ZodiacSign.TAURUS, {8}),
        (CelestialBody.MERCURY, ZodiacSign.GEMINI, {9}),
        (CelestialBody.VENUS, ZodiacSign.CANCER, {10}),
        (CelestialBody.MARS, ZodiacSign.ARIES, {4, 7, 8}),
        (CelestialBody.JUPITER, ZodiacSign.ARIES, {5, 7, 9}),
        (CelestialBody.SATURN, ZodiacSign.ARIES, {3, 7, 10}),
    ],
)
def test_every_approved_graha_drishti_table_is_emitted(
    body: CelestialBody, source_sign: ZodiacSign, expected_houses: set[int]
) -> None:
    signs = {candidate: ZodiacSign.PISCES for candidate in _BODIES}
    signs[body] = source_sign
    facts = _facts(_chart(planet_signs=signs))

    actual = {
        house
        for house in range(1, 13)
        if facts[f"jyotish.d1.aspect.{body.value}.house.{house}"] is True
    }
    assert actual == expected_houses
    assert GRAHA_DRISHTI_HOUSES[body]


def test_nodes_have_no_aspect_source_facts_but_can_be_aspected_targets() -> None:
    facts = _facts(_chart())

    assert not any("jyotish.d1.aspect.rahu." in key for key in facts)
    assert not any("jyotish.d1.aspect.ketu." in key for key in facts)
    assert "jyotish.d1.aspect.sun.planet.rahu" in facts
    assert "jyotish.d1.aspect.sun.planet.ketu" in facts


def test_same_sign_is_symmetric_without_reverse_duplicate_facts() -> None:
    signs = {body: ZodiacSign.PISCES for body in _BODIES}
    signs[CelestialBody.SUN] = ZodiacSign.LEO
    signs[CelestialBody.MOON] = ZodiacSign.LEO
    facts = _facts(_chart(planet_signs=signs))

    assert facts["jyotish.d1.same_sign.sun.moon"] is True
    assert "jyotish.d1.same_sign.moon.sun" not in facts
    assert facts["jyotish.d1.same_sign.sun.mars"] is False
    assert len([key for key in facts if key.startswith("jyotish.d1.same_sign.")]) == 36


def test_dignity_tables_are_independent_and_exclude_nodes() -> None:
    signs = {
        CelestialBody.SUN: ZodiacSign.ARIES,
        CelestialBody.MOON: ZodiacSign.TAURUS,
        CelestialBody.MARS: ZodiacSign.CAPRICORN,
        CelestialBody.MERCURY: ZodiacSign.VIRGO,
        CelestialBody.JUPITER: ZodiacSign.CANCER,
        CelestialBody.VENUS: ZodiacSign.PISCES,
        CelestialBody.SATURN: ZodiacSign.LIBRA,
        CelestialBody.RAHU: ZodiacSign.ARIES,
        CelestialBody.KETU: ZodiacSign.LIBRA,
    }
    facts = _facts(_chart(planet_signs=signs))

    for body in tuple(CelestialBody)[:7]:
        assert facts[f"jyotish.d1.planet.{body.value}.exaltation_sign"] is True
        assert facts[f"jyotish.d1.planet.{body.value}.debilitation_sign"] is False
    assert facts["jyotish.d1.planet.mercury.own_sign"] is True
    assert not any("jyotish.d1.planet.rahu.exaltation_sign" == key for key in facts)
    assert not any("jyotish.d1.planet.ketu.own_sign" == key for key in facts)
    assert EXALTATION_SIGNS[CelestialBody.SUN] is ZodiacSign.ARIES
    assert DEBILITATION_SIGNS[CelestialBody.SATURN] is ZodiacSign.ARIES
    assert EXALTATION_SIGNS == {
        CelestialBody.SUN: ZodiacSign.ARIES,
        CelestialBody.MOON: ZodiacSign.TAURUS,
        CelestialBody.MARS: ZodiacSign.CAPRICORN,
        CelestialBody.MERCURY: ZodiacSign.VIRGO,
        CelestialBody.JUPITER: ZodiacSign.CANCER,
        CelestialBody.VENUS: ZodiacSign.PISCES,
        CelestialBody.SATURN: ZodiacSign.LIBRA,
    }
    assert DEBILITATION_SIGNS == {
        CelestialBody.SUN: ZodiacSign.LIBRA,
        CelestialBody.MOON: ZodiacSign.SCORPIO,
        CelestialBody.MARS: ZodiacSign.CANCER,
        CelestialBody.MERCURY: ZodiacSign.PISCES,
        CelestialBody.JUPITER: ZodiacSign.CAPRICORN,
        CelestialBody.VENUS: ZodiacSign.VIRGO,
        CelestialBody.SATURN: ZodiacSign.ARIES,
    }

    debilitated_signs = signs.copy()
    debilitated_signs[CelestialBody.SUN] = ZodiacSign.LIBRA
    debilitated = _facts(_chart(planet_signs=debilitated_signs))
    assert debilitated["jyotish.d1.planet.sun.exaltation_sign"] is False
    assert debilitated["jyotish.d1.planet.sun.debilitation_sign"] is True
    assert debilitated["jyotish.d1.planet.sun.own_sign"] is False


def test_bundle_provenance_ordering_and_adapter_are_reproducible() -> None:
    chart = _chart()
    first = DerivedFactsEngine().calculate(chart)
    second = DerivedFactsEngine().calculate(chart)
    fact_set = to_fact_set(first)

    assert first.model_dump(mode="json") == second.model_dump(mode="json")
    assert first.provenance.source_chart_methodology == chart.methodology
    assert first.provenance.inherited_ephemeris_provenance == chart.provenance
    assert first.provenance.methodology.methodology_id == "jyotish-derived-facts-v1"
    assert first.provenance.methodology.angular_separation == "deferred"
    assert len(fact_set.facts) == len({fact.fact_id for fact in fact_set.facts})
    assert fact_set.facts[0].fact_id == "jyotish.d1.house.1.sign"
    assert fact_set.facts[-1].fact_id == "jyotish.d1.same_sign.rahu.ketu"


def test_task08_adapter_supports_three_state_rule_evaluation() -> None:
    facts = to_fact_set(DerivedFactsEngine().calculate(_chart()))
    rule = RuleDefinition(
        rule_id="TEST_STRUCTURAL_FACT",
        rule_version="1",
        ruleset_version="test-v1",
        name="Synthetic structural fact test",
        domain="test",
        is_synthetic_demo=True,
        condition=ConditionDefinition(
            kind=ConditionKind.LEAF,
            operation=ConditionOperation.EQUALS,
            fact_id="jyotish.d1.house.1.kendra",
            expected_value=True,
        ),
        effect=RuleEffect(effect_key="test.structural", label="Synthetic"),
    )

    assert RuleEvaluator().evaluate_rule(rule, facts).status is EvaluationStatus.TRUE


def test_invalid_non_d1_shape_fails_without_calculation() -> None:
    chart = _chart().model_copy(update={"houses": ()})

    with pytest.raises(DerivedFactInputError, match="houses ordered"):
        DerivedFactsEngine().calculate(chart)
