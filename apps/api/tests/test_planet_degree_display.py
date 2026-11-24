"""NEXT-FIX-DEG-01: D1 degree display, nakshatra/pada borders and retrograde flags.

Calculated facts only: no combustion, conjunction orb, avastha or strength is derived here.
"""

from decimal import Decimal

import pytest

from astrologer.astrology.chart import (
    ChartEngine,
    Nakshatra,
    ZodiacSign,
    _chart_planet,
    degree_in_sign,
    format_degree_in_sign,
    nakshatra_for_longitude,
    sign_for_longitude,
)
from astrologer.astrology.ephemeris import CelestialBody, PlanetaryPosition
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.birth.models import BirthInput

# One arc-minute below a border, as an exact Decimal.
_MINUTE = Decimal(1) / Decimal(60)
_NAKSHATRA = Decimal(40) / Decimal(3)
_PADA = _NAKSHATRA / Decimal(4)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (Decimal("0"), "00°00′"),
        (Decimal("0.0001"), "00°00′"),
        (Decimal("5.5"), "05°30′"),
        (Decimal("12.5833333333"), "12°34′"),
        (Decimal(29) + 59 * _MINUTE, "29°59′"),
        # Minutes are truncated, never rounded into the next sign.
        (Decimal("29.9999999999"), "29°59′"),
        # 13°20′ (40/3°, inexact in Decimal) is a nakshatra border: shown as 13°20′;
        # a millionth of a degree below it stays 13°19′.
        (_NAKSHATRA - Decimal("1e-6"), "13°19′"),
        (_NAKSHATRA, "13°20′"),
    ],
)
def test_degree_formatting_is_dd_mm_truncated(value: Decimal, expected: str) -> None:
    assert format_degree_in_sign(value) == expected


@pytest.mark.parametrize("value", [Decimal("-0.0001"), Decimal("30"), Decimal("31")])
def test_degree_formatting_rejects_values_outside_one_sign(value: Decimal) -> None:
    with pytest.raises(ValueError):
        format_degree_in_sign(value)


@pytest.mark.parametrize(
    ("longitude", "sign", "dms", "nakshatra", "pada"),
    [
        # 0° and 29°59′ of signs (synthetic longitudes).
        (Decimal("0"), ZodiacSign.ARIES, "00°00′", Nakshatra.ASHWINI, 1),
        (Decimal(29) + 59 * _MINUTE, ZodiacSign.ARIES, "29°59′", Nakshatra.KRITTIKA, 1),
        (Decimal("30"), ZodiacSign.TAURUS, "00°00′", Nakshatra.KRITTIKA, 2),
        (Decimal(359) + 59 * _MINUTE, ZodiacSign.PISCES, "29°59′", Nakshatra.REVATI, 4),
        # Nakshatra borders: 13°20′ Aries (Ashwini → Bharani), 26°40′ (Bharani → Krittika).
        (_NAKSHATRA - _MINUTE, ZodiacSign.ARIES, "13°19′", Nakshatra.ASHWINI, 4),
        (_NAKSHATRA, ZodiacSign.ARIES, "13°20′", Nakshatra.BHARANI, 1),
        (2 * _NAKSHATRA - _MINUTE, ZodiacSign.ARIES, "26°39′", Nakshatra.BHARANI, 4),
        (2 * _NAKSHATRA, ZodiacSign.ARIES, "26°40′", Nakshatra.KRITTIKA, 1),
        # Pada border inside a nakshatra: 3°20′ (Ashwini pada 1 → 2).
        (_PADA - _MINUTE, ZodiacSign.ARIES, "03°19′", Nakshatra.ASHWINI, 1),
        (_PADA, ZodiacSign.ARIES, "03°20′", Nakshatra.ASHWINI, 2),
        # A border that falls inside a sign: 120° = Magha pada 1 at 0° Leo.
        (Decimal("120") - _MINUTE, ZodiacSign.CANCER, "29°59′", Nakshatra.ASHLESHA, 4),
        (Decimal("120"), ZodiacSign.LEO, "00°00′", Nakshatra.MAGHA, 1),
    ],
)
def test_sign_degree_nakshatra_and_pada_at_borders(
    longitude: Decimal, sign: ZodiacSign, dms: str, nakshatra: Nakshatra, pada: int
) -> None:
    assert sign_for_longitude(longitude) is sign
    assert format_degree_in_sign(degree_in_sign(longitude)) == dms
    placement = nakshatra_for_longitude(longitude)
    assert (placement.nakshatra, placement.pada) == (nakshatra, pada)


def _position(speed: str | None) -> PlanetaryPosition:
    return PlanetaryPosition(
        body=CelestialBody.MARS,
        longitude=Decimal("100.5"),
        motion_speed=Decimal(speed) if speed is not None else None,
        retrograde_input=None if speed is None else Decimal(speed) < 0,
    )


@pytest.mark.parametrize(
    ("speed", "expected"), [("-0.25", True), ("0.5", False), ("0", False), (None, None)]
)
def test_retrograde_flag_is_the_computed_speed_sign(speed: str | None, expected: bool) -> None:
    planet = _chart_planet(_position(speed), ZodiacSign.ARIES)
    assert planet.retrograde is expected
    assert planet.degree_in_sign_dms == "10°30′"
    assert planet.model_dump(mode="json")["degree_in_sign_dms"] == "10°30′"


def test_real_chart_exposes_degree_nakshatra_pada_and_retrograde_for_every_graha() -> None:
    birth = BirthInput(
        birth_date="1986-02-12", birth_time="12:00:00", timezone="UTC", latitude=0, longitude=0
    )
    chart = ChartEngine(SwissEphemerisProvider()).calculate(birth)
    assert chart.methodology.configuration.lunar_node_definition.value == "true"
    dumped = chart.model_dump(mode="json")
    assert {p["body"] for p in dumped["planets"]} == {
        "sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu",
    }  # fmt: skip
    for planet, raw in zip(chart.planets, dumped["planets"], strict=True):
        assert raw["degree_in_sign_dms"] == format_degree_in_sign(planet.degree_in_sign)
        assert raw["nakshatra"]["pada"] in {1, 2, 3, 4}
        assert planet.motion_speed is not None
        assert planet.retrograde is (planet.motion_speed < 0)
    by_body = {planet.body: planet for planet in chart.planets}
    rahu, ketu = by_body[CelestialBody.RAHU], by_body[CelestialBody.KETU]
    # True nodes: Ketu is exactly opposite Rahu and shares its computed motion.
    assert (rahu.longitude + 180) % 360 == ketu.longitude
    assert rahu.degree_in_sign_dms == ketu.degree_in_sign_dms
    assert rahu.retrograde is ketu.retrograde
    assert dumped["ascendant"]["degree_in_sign_dms"] == format_degree_in_sign(
        chart.ascendant.degree_in_sign
    )
    # Calculated facts only (NEXT-FIX-DEG-01): nothing interpretive is attached to a planet.
    for raw in dumped["planets"]:
        assert not {"combust", "combustion", "orb", "avastha", "strength"} & set(raw)
