"""Invariant and adapter-mapping tests for the deterministic D1 chart engine.

The tests do not contain externally asserted planetary positions. They verify
provider outputs against the installed Swiss Ephemeris API and chart invariants.
Independent, legally usable chart-fixture validation remains a separate task.
"""

from datetime import UTC, date, datetime, time
from decimal import Decimal

import pytest
import swisseph as swe

from astrologer.astrology.chart import (
    ChartEngine,
    Nakshatra,
    ZodiacSign,
    degree_in_sign,
    nakshatra_for_longitude,
    sign_for_longitude,
)
from astrologer.astrology.ephemeris import CelestialBody, EphemerisConfiguration
from astrologer.astrology.swiss_ephemeris import SWISS_LAHIRI_MODE, SwissEphemerisProvider
from astrologer.birth.models import BirthInput

_BIRTH_INPUT = BirthInput(
    birth_date=date(1990, 1, 15),
    birth_time=time(9, 30),
    timezone="Asia/Kolkata",
    latitude=19.076,
    longitude=72.8777,
    place_name="Mumbai",
)
_UTC_INSTANT = datetime(1990, 1, 15, 4, 0, tzinfo=UTC)


@pytest.fixture
def chart_engine() -> ChartEngine:
    return ChartEngine(SwissEphemerisProvider())


def test_d1_chart_returns_required_facts_and_whole_sign_houses(chart_engine: ChartEngine) -> None:
    chart = chart_engine.calculate(_BIRTH_INPUT)

    assert chart.calculation_instant == _UTC_INSTANT
    assert chart.birth_input.timezone == "Asia/Kolkata"
    assert chart.birth_input.latitude == 19.076
    assert chart.birth_input.longitude == 72.8777
    assert {planet.body for planet in chart.planets} == set(CelestialBody)
    assert Decimal("0") <= chart.ascendant.longitude < Decimal("360")
    assert len(chart.houses) == 12
    assert chart.houses[0].number == 1
    assert chart.houses[0].sign is chart.ascendant.sign

    for planet in chart.planets:
        assert Decimal("0") <= planet.longitude < Decimal("360")
        assert planet.ecliptic_latitude is not None
        assert Decimal("-90") <= planet.ecliptic_latitude <= Decimal("90")
        assert planet.distance is not None
        assert planet.motion_speed is not None
        assert planet.retrograde is planet.retrograde_input
        expected_house = (
            (list(ZodiacSign).index(planet.sign) - list(ZodiacSign).index(chart.ascendant.sign))
            % 12
        ) + 1
        assert planet.house_number == expected_house
        assert planet.nakshatra == nakshatra_for_longitude(planet.longitude)

    assert chart.ascendant.nakshatra == nakshatra_for_longitude(chart.ascendant.longitude)


def test_swiss_adapter_uses_sidereal_lahiri_and_true_lunar_node(chart_engine: ChartEngine) -> None:
    chart = chart_engine.calculate(_BIRTH_INPUT)
    julian_day_ut = swe.julday(1990, 1, 15, 4.0, swe.GREG_CAL)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED

    direct_sun, returned_flags = swe.calc_ut(julian_day_ut, swe.SUN, flags)
    direct_rahu, _ = swe.calc_ut(julian_day_ut, swe.TRUE_NODE, flags)
    tropical_sun, _ = swe.calc_ut(julian_day_ut, swe.SUN, swe.FLG_SPEED)
    sun = next(planet for planet in chart.planets if planet.body is CelestialBody.SUN)
    rahu = next(planet for planet in chart.planets if planet.body is CelestialBody.RAHU)
    ketu = next(planet for planet in chart.planets if planet.body is CelestialBody.KETU)

    assert returned_flags & swe.FLG_SIDEREAL
    assert sun.longitude == Decimal(str(direct_sun[0])) % Decimal("360")
    assert sun.longitude != Decimal(str(tropical_sun[0])) % Decimal("360")
    assert rahu.longitude == Decimal(str(direct_rahu[0])) % Decimal("360")
    assert ketu.longitude == (rahu.longitude + Decimal("180")) % Decimal("360")
    assert chart.provenance.configuration.ayanamsa_provider_mode == SWISS_LAHIRI_MODE
    assert chart.provenance.configuration.lunar_node_definition.value == "true"


def test_chart_calculation_is_reproducible_and_preserves_provenance(
    chart_engine: ChartEngine,
) -> None:
    first = chart_engine.calculate(_BIRTH_INPUT)
    second = chart_engine.calculate(_BIRTH_INPUT)

    assert first == second
    assert first.provenance.provider.provider_name == "pyswisseph"
    assert first.provenance.provider.provider_version == "2.10.3.2"
    assert first.provenance.provider.library_version == "2.10.03"
    assert first.provenance.provider.ephemeris_data_version is not None
    assert first.provenance.provider.ephemeris_data_hash is None
    assert first.provenance.configuration.zodiac.value == "sidereal"
    assert first.provenance.configuration.ayanamsa.value == "lahiri"
    assert first.provenance.configuration.house_system.value == "whole_sign"


@pytest.mark.parametrize(
    ("longitude", "expected_sign", "expected_degree"),
    [
        (Decimal("0"), ZodiacSign.ARIES, Decimal("0")),
        (Decimal("29.999999999999"), ZodiacSign.ARIES, Decimal("29.999999999999")),
        (Decimal("30"), ZodiacSign.TAURUS, Decimal("0")),
        (Decimal("359.999999999999"), ZodiacSign.PISCES, Decimal("29.999999999999")),
    ],
)
def test_sign_and_degree_boundaries_are_exact(
    longitude: Decimal,
    expected_sign: ZodiacSign,
    expected_degree: Decimal,
) -> None:
    assert sign_for_longitude(longitude) is expected_sign
    assert degree_in_sign(longitude) == expected_degree


@pytest.mark.parametrize(
    ("longitude", "expected_nakshatra", "expected_pada"),
    [
        (Decimal("0"), Nakshatra.ASHWINI, 1),
        (Decimal("3.333333333333333333333333333"), Nakshatra.ASHWINI, 2),
        (Decimal("13.33333333333333333333333333"), Nakshatra.BHARANI, 1),
        (Decimal("359.9999999999999999999999999"), Nakshatra.REVATI, 4),
    ],
)
def test_nakshatra_and_pada_boundaries_are_exact(
    longitude: Decimal,
    expected_nakshatra: Nakshatra,
    expected_pada: int,
) -> None:
    placement = nakshatra_for_longitude(longitude)

    assert placement.nakshatra is expected_nakshatra
    assert placement.pada == expected_pada


def test_chart_result_contains_only_provider_neutral_domain_models(
    chart_engine: ChartEngine,
) -> None:
    chart = chart_engine.calculate(_BIRTH_INPUT)
    dumped = chart.model_dump(mode="json")

    assert set(dumped) == {
        "methodology",
        "birth_input",
        "calculation_instant",
        "ascendant",
        "houses",
        "planets",
        "provenance",
    }
    assert "swisseph" not in str(type(chart))
    assert "swisseph" not in str(type(chart.planets[0]))


def test_mean_nodes_are_not_silently_substituted(chart_engine: ChartEngine) -> None:
    configuration = EphemerisConfiguration.model_validate(
        {"lunar_node_definition": "mean"},
    )

    with pytest.raises(ValueError, match="lunar_nodes:mean"):
        chart_engine.calculate(_BIRTH_INPUT, configuration=configuration)
