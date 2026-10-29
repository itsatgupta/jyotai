"""Internal CALC-01 verification; pending references are not certification."""

import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import pytest
from calc01_support import (
    OFFSETS_MINUTES,
    ReferenceFixture,
    VerificationStatus,
    angular_difference,
    compare_longitude,
    compare_recorded_longitudes,
    compare_utc_boundary,
    load_fixtures,
    sensitivity,
)
from pydantic import ValidationError

from astrologer.astrology.chart import ChartEngine, ZodiacSign, sign_for_longitude
from astrologer.astrology.dasha import VimshottariDashaEngine
from astrologer.astrology.ephemeris import CelestialBody, EphemerisRequest
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.astrology.vargas import DivisionalChartType, derive_varga_longitude


def test_all_six_reference_candidates_are_fully_specified_and_honestly_pending() -> None:
    fixtures = load_fixtures()

    assert len(fixtures) == 6
    assert len({fixture.id for fixture in fixtures}) == 6
    assert all(fixture.birth().utc_datetime == fixture.utc for fixture in fixtures)
    assert all(
        fixture.reference_status is VerificationStatus.REFERENCE_UNAVAILABLE
        and not fixture.expected.has_values()
        and fixture.tolerance_degrees is None
        for fixture in fixtures
    )


def test_missing_reference_cannot_be_promoted_to_independent_verified() -> None:
    fixture = load_fixtures()[0]
    with pytest.raises(ValidationError, match="verification status is a test result"):
        ReferenceFixture.model_validate(
            fixture.model_dump()
            | {"reference_status": VerificationStatus.INDEPENDENT_VERIFIED}
        )


def test_longitude_comparison_handles_wraparound_and_declared_tolerance() -> None:
    close = compare_longitude(
        "sun", Decimal("359.99"), Decimal("0.01"), Decimal("0.03")
    )
    far = compare_longitude(
        "moon", Decimal("0.01"), Decimal("359.95"), Decimal("0.03")
    )

    assert close.difference == Decimal("0.02")
    assert close.passed
    assert far.difference == Decimal("-0.06")
    assert not far.passed
    assert angular_difference(Decimal("0"), Decimal("180")) == Decimal("-180")
    assert angular_difference(Decimal("0"), Decimal("-700")) == Decimal("20")
    assert compare_recorded_longitudes(load_fixtures()[0], {"sun": Decimal("1")}) == ()


def test_external_values_need_provenance_and_compare_without_promoting_status() -> None:
    fixture = load_fixtures()[0]
    with pytest.raises(ValidationError, match="full source provenance"):
        ReferenceFixture.model_validate(
            fixture.model_dump()
            | {
                "reference_status": VerificationStatus.EXTERNAL_COMPARISON_UNRESOLVED,
                "expected": {"longitudes": {"sun": "359.99"}},
                "tolerance_degrees": "0.03",
            }
        )
    # Synthetic schema exercise only; these values are not stored as reference evidence.
    sourced = ReferenceFixture.model_validate(
        fixture.model_dump()
        | {
            "reference_status": VerificationStatus.EXTERNAL_COMPARISON_UNRESOLVED,
            "reference_source": "test source",
            "reference_version": "test version",
            "reference_data_provenance": "test data",
            "reference_settings": {"zodiac": "sidereal", "ayanamsa": "lahiri"},
            "reference_artifact_sha256": "a" * 64,
            "expected": {"longitudes": {"sun": "359.99"}},
            "tolerance_degrees": "0.03",
        }
    )
    result = compare_recorded_longitudes(sourced, {"sun": Decimal("0.01")})
    assert len(result) == 1 and result[0].passed
    assert sourced.reference_status is VerificationStatus.EXTERNAL_COMPARISON_UNRESOLVED
    with pytest.raises(ValueError, match="missing reference fields"):
        compare_recorded_longitudes(sourced, {})


def test_utc_boundary_comparison_preserves_signed_subsecond_difference() -> None:
    expected = datetime(2000, 1, 1, tzinfo=UTC)
    actual = expected - timedelta(microseconds=1)
    result = compare_utc_boundary("dasha.end", expected, actual, Decimal("0.000001"))
    assert result.difference == Decimal("-0.000001") and result.passed
    with pytest.raises(ValueError, match="aware UTC"):
        compare_utc_boundary("dasha.end", expected.replace(tzinfo=None), actual, Decimal("0"))


def test_archived_astrosage_moon_comparisons_are_screening_only() -> None:
    path = Path(__file__).parent / "fixtures" / "calc01_archived_comparisons.json"
    cases = json.loads(path.read_text(encoding="utf-8"))
    provider = SwissEphemerisProvider()
    documented_arcseconds = {
        "astrosage_1975_moon": Decimal("19.90798"),
        "astrosage_2007_moon": Decimal("35.70897"),
    }
    assert {case["id"] for case in cases} == set(documented_arcseconds)
    for case in cases:
        assert case["status"] == VerificationStatus.EXTERNAL_COMPARISON_UNRESOLVED
        sign_name, dms = case["expected_dms"].split()
        degrees, minutes, seconds = (int(part) for part in dms.split(":"))
        converted_degrees = (
            Decimal(list(ZodiacSign).index(ZodiacSign(sign_name.lower())) * 30 + degrees)
            + Decimal(minutes * 60 + seconds) / Decimal("3600")
        )
        assert Decimal(case["expected_degrees"]) == converted_degrees
        actual = provider.calculate(
            EphemerisRequest(
                calculation_instant=datetime.fromisoformat(case["utc"].replace("Z", "+00:00")),
                requested_bodies=(CelestialBody.MOON,),
            )
        ).positions[0]
        result = compare_longitude(
            case["body"],
            Decimal(case["expected_degrees"]),
            actual.longitude,
            Decimal(case["screening_tolerance_arcseconds"]) / Decimal("3600"),
        )
        assert not result.passed
        assert result.unit == "degrees"
        assert result.difference > 0
        assert round(result.difference * Decimal("3600"), 5) == documented_arcseconds[
            case["id"]
        ]


def test_live_dasha_intervals_are_utc_contiguous_and_half_open() -> None:
    fixture = load_fixtures()[0]
    chart = ChartEngine(SwissEphemerisProvider()).calculate(fixture.birth())
    engine = VimshottariDashaEngine()
    timeline = engine.calculate(chart, fixture.utc + timedelta(days=36525))
    year_us = 31_557_600_000_000
    years = {item.lord: item.years for item in timeline.provenance.methodology.mahadasha_years}
    sequence = tuple(timeline.provenance.methodology.lord_sequence)

    assert timeline.mahadashas[0].start <= fixture.utc < timeline.mahadashas[0].end
    assert all(
        period.start.tzinfo is UTC and period.end.tzinfo is UTC
        for period in timeline.mahadashas
    )
    for index, period in enumerate(timeline.mahadashas):
        assert period.end - period.start == timedelta(microseconds=years[period.lord] * year_us)
        assert period.antardashas[0].start == period.start
        assert period.antardashas[-1].end == period.end
        lord_index = sequence.index(period.lord)
        expected_lords = sequence[lord_index:] + sequence[:lord_index]
        assert tuple(item.lord for item in period.antardashas) == expected_lords
        parent_us = years[period.lord] * year_us
        for child in period.antardashas:
            actual_us = (child.end - child.start) // timedelta(microseconds=1)
            ideal_us = Fraction(parent_us * years[child.lord], 120)
            assert abs(Fraction(actual_us) - ideal_us) <= 1
        for left, right in zip(period.antardashas, period.antardashas[1:], strict=False):
            assert left.end == right.start
            if right.start >= fixture.utc:
                assert engine.at(chart, right.start).antardasha.lord == right.lord
        if index + 1 < len(timeline.mahadashas):
            next_period = timeline.mahadashas[index + 1]
            assert period.end == next_period.start
            assert next_period.lord == sequence[(lord_index + 1) % len(sequence)]
            assert engine.at(chart, next_period.start).mahadasha.lord == next_period.lord


def test_sensitivity_detects_actual_ascendant_and_nakshatra_boundary_changes() -> None:
    fixtures = {fixture.id: fixture for fixture in load_fixtures()}
    asc = sensitivity(fixtures["ascendant_sign_boundary"])
    moon = sensitivity(fixtures["moon_nakshatra_boundary"])

    assert tuple(asc) == OFFSETS_MINUTES
    assert asc[0]["ascendant_sign"] != asc[15]["ascendant_sign"]
    assert asc[0]["d1_houses"] != asc[15]["d1_houses"]
    assert asc[0]["house_lords"] != asc[15]["house_lords"]
    assert moon[-15]["moon_nakshatra"] != moon[15]["moon_nakshatra"]
    assert moon[-15]["birth_mahadasha_lord"] != moon[15]["birth_mahadasha_lord"]
    assert moon[-15]["birth_mahadasha_end_utc"] != moon[15]["birth_mahadasha_end_utc"]


@pytest.mark.parametrize(
    ("chart_type", "boundary_degrees"),
    [
        (DivisionalChartType.D9, (10, 20)),
        (DivisionalChartType.D10, tuple(range(3, 30, 3))),
    ],
)
def test_all_signs_advance_at_exact_representable_divisional_edges(
    chart_type: DivisionalChartType, boundary_degrees: tuple[int, ...]
) -> None:
    epsilon = Decimal("0.000000000001")
    for sign_index, _ in enumerate(ZodiacSign):
        for boundary in boundary_degrees:
            edge = Decimal(sign_index * 30 + boundary)
            before_sign = sign_for_longitude(derive_varga_longitude(edge - epsilon, chart_type))
            at_sign = sign_for_longitude(derive_varga_longitude(edge, chart_type))
            assert before_sign != at_sign
