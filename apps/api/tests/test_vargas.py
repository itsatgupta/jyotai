"""Deterministic mapping and integration tests for initial Parashari Vargas."""

from datetime import UTC, date, datetime, time
from decimal import Decimal

import pytest

from astrologer.astrology.chart import ChartEngine, ZodiacSign
from astrologer.astrology.ephemeris import CelestialBody
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.astrology.vargas import (
    DivisionalChartType,
    VargaEngine,
    VargaMappingVariant,
    derive_varga_longitude,
)
from astrologer.birth.models import BirthInput

_BIRTH_INPUT = BirthInput(
    birth_date=date(1990, 1, 15),
    birth_time=time(9, 30),
    timezone="Asia/Kolkata",
    latitude=19.076,
    longitude=72.8777,
    place_name="Mumbai",
)


def _longitude(sign: ZodiacSign, degree: Decimal) -> Decimal:
    return Decimal(list(ZodiacSign).index(sign)) * Decimal("30") + degree


@pytest.mark.parametrize(
    ("source_sign", "degree", "expected_sign", "expected_degree"),
    [
        (ZodiacSign.ARIES, Decimal("0"), ZodiacSign.LEO, Decimal("0")),
        (ZodiacSign.ARIES, Decimal("15"), ZodiacSign.CANCER, Decimal("0")),
        (ZodiacSign.TAURUS, Decimal("0"), ZodiacSign.CANCER, Decimal("0")),
        (ZodiacSign.TAURUS, Decimal("15"), ZodiacSign.LEO, Decimal("0")),
        (
            ZodiacSign.ARIES,
            Decimal("29.999999999999"),
            ZodiacSign.CANCER,
            Decimal("29.999999999998"),
        ),
    ],
)
def test_d2_parashari_sun_moon_hora_mapping_and_boundaries(
    source_sign: ZodiacSign,
    degree: Decimal,
    expected_sign: ZodiacSign,
    expected_degree: Decimal,
) -> None:
    longitude = derive_varga_longitude(
        _longitude(source_sign, degree),
        DivisionalChartType.D2,
    )

    assert list(ZodiacSign)[int(longitude // Decimal("30"))] is expected_sign
    assert longitude % Decimal("30") == expected_degree


@pytest.mark.parametrize(
    ("source_sign", "degree", "expected_sign"),
    [
        # Movable: starts from the same sign, then advances zodiacally.
        (ZodiacSign.ARIES, Decimal("0"), ZodiacSign.ARIES),
        (ZodiacSign.ARIES, Decimal("10") / Decimal("3"), ZodiacSign.TAURUS),
        # Fixed: starts from the ninth sign, then advances zodiacally.
        (ZodiacSign.TAURUS, Decimal("0"), ZodiacSign.CAPRICORN),
        (ZodiacSign.TAURUS, Decimal("10") / Decimal("3"), ZodiacSign.AQUARIUS),
        # Dual: starts from the fifth sign, then advances zodiacally.
        (ZodiacSign.GEMINI, Decimal("0"), ZodiacSign.LIBRA),
        (ZodiacSign.GEMINI, Decimal("10") / Decimal("3"), ZodiacSign.SCORPIO),
    ],
)
def test_d9_parashari_mapping_explicitly_covers_sign_modalities(
    source_sign: ZodiacSign,
    degree: Decimal,
    expected_sign: ZodiacSign,
) -> None:
    longitude = derive_varga_longitude(
        _longitude(source_sign, degree),
        DivisionalChartType.D9,
    )

    assert list(ZodiacSign)[int(longitude // Decimal("30"))] is expected_sign


def test_d9_boundary_and_pisces_wraparound_are_exact() -> None:
    boundary = Decimal("10") / Decimal("3")
    before_boundary = boundary - Decimal("0.000000000000000000000000001")
    aries_before = derive_varga_longitude(
        _longitude(ZodiacSign.ARIES, before_boundary),
        DivisionalChartType.D9,
    )
    aries_at = derive_varga_longitude(
        _longitude(ZodiacSign.ARIES, boundary),
        DivisionalChartType.D9,
    )
    pisces_final = derive_varga_longitude(
        _longitude(ZodiacSign.PISCES, Decimal("30") - Decimal("0.000000000001")),
        DivisionalChartType.D9,
    )

    assert aries_before < Decimal("30")
    assert aries_at == Decimal("30")
    assert pisces_final < Decimal("360")


@pytest.mark.parametrize(
    ("source_sign", "degree", "expected_sign"),
    [
        # Odd: starts from the same sign, then advances zodiacally.
        (ZodiacSign.ARIES, Decimal("0"), ZodiacSign.ARIES),
        (ZodiacSign.ARIES, Decimal("3"), ZodiacSign.TAURUS),
        # Even: starts from the ninth sign, then advances zodiacally.
        (ZodiacSign.TAURUS, Decimal("0"), ZodiacSign.CAPRICORN),
        (ZodiacSign.TAURUS, Decimal("3"), ZodiacSign.AQUARIUS),
    ],
)
def test_d10_parashari_mapping_explicitly_covers_odd_even_starts_and_advance(
    source_sign: ZodiacSign,
    degree: Decimal,
    expected_sign: ZodiacSign,
) -> None:
    longitude = derive_varga_longitude(
        _longitude(source_sign, degree),
        DivisionalChartType.D10,
    )

    assert list(ZodiacSign)[int(longitude // Decimal("30"))] is expected_sign


def test_d10_division_boundary_advances_to_the_following_sign() -> None:
    before_boundary = derive_varga_longitude(
        _longitude(ZodiacSign.ARIES, Decimal("3") - Decimal("0.000000000001")),
        DivisionalChartType.D10,
    )
    at_boundary = derive_varga_longitude(
        _longitude(ZodiacSign.ARIES, Decimal("3")),
        DivisionalChartType.D10,
    )

    assert before_boundary < Decimal("30")
    assert at_boundary == Decimal("30")


def test_d1_is_an_identity_transformation() -> None:
    source = _longitude(ZodiacSign.TAURUS, Decimal("12.5"))

    assert derive_varga_longitude(source, DivisionalChartType.D1) == source


def test_varga_engine_derives_all_supported_charts_without_a_provider() -> None:
    source_chart = ChartEngine(SwissEphemerisProvider()).calculate(_BIRTH_INPUT)
    varga_engine = VargaEngine()

    charts = varga_engine.calculate_all(source_chart)

    assert tuple(chart.methodology.chart_type for chart in charts) == tuple(DivisionalChartType)
    assert {chart.methodology.mapping_variant for chart in charts} == {
        VargaMappingVariant.RASHI_IDENTITY,
        VargaMappingVariant.PARASHARI_SUN_MOON_HORA,
        VargaMappingVariant.PARASHARI_NAVAMSA,
        VargaMappingVariant.PARASHARI_DASAMSA,
    }
    for chart in charts:
        assert chart.birth_input == source_chart.birth_input
        assert chart.calculation_instant == source_chart.calculation_instant
        assert chart.provenance == source_chart.provenance
        assert chart.methodology.source_chart_methodology == source_chart.methodology
        assert len(chart.houses) == 12
        assert chart.houses[0].sign is chart.ascendant.sign
        assert {planet.body for planet in chart.planets} == set(CelestialBody)
        for planet in chart.planets:
            assert planet.inherited_motion_speed is not None
            assert planet.inherited_retrograde in {True, False}
            expected_house = (
                (list(ZodiacSign).index(planet.sign) - list(ZodiacSign).index(chart.ascendant.sign))
                % 12
            ) + 1
            assert planet.house_number == expected_house


def test_varga_results_are_reproducible_and_serializable() -> None:
    source_chart = ChartEngine(SwissEphemerisProvider()).calculate(_BIRTH_INPUT)
    engine = VargaEngine()

    first = engine.calculate(source_chart, DivisionalChartType.D9)
    second = engine.calculate(source_chart, DivisionalChartType.D9)

    assert first == second
    assert first.calculation_instant == datetime(1990, 1, 15, 4, 0, tzinfo=UTC)
    dumped = first.model_dump(mode="json")
    assert set(dumped) == {
        "methodology",
        "birth_input",
        "calculation_instant",
        "ascendant",
        "houses",
        "planets",
        "provenance",
    }
    assert "swisseph" not in str(type(first))
