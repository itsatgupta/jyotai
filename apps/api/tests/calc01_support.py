"""CALC-01 test-only reference intake and factual birth-time sensitivity.

No pending fixture is treated as an independent astronomical reference.
"""

import json
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from enum import StrEnum
from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, model_validator

from astrologer.astrology.chart import ChartEngine
from astrologer.astrology.dasha import VimshottariDashaEngine
from astrologer.astrology.derived_facts import SIGN_RULERS
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.astrology.vargas import DivisionalChartType, VargaEngine
from astrologer.birth.models import BirthInput

FIXTURES = Path(__file__).parent / "fixtures" / "calc01_profiles.json"
PROFILE = "sidereal-lahiri-true-node-whole-sign-parashari-d9-d10-vimshottari-v1"
OFFSETS_MINUTES = (-15, -5, 0, 5, 15)


class VerificationStatus(StrEnum):
    """Evidence status; only an independently sourced fixture can earn the first value."""

    INDEPENDENT_VERIFIED = "INDEPENDENT_VERIFIED"
    EXTERNAL_COMPARISON_UNRESOLVED = "EXTERNAL_COMPARISON_UNRESOLVED"
    INTERNAL_VERIFIED = "INTERNAL_VERIFIED"
    REFERENCE_UNAVAILABLE = "REFERENCE_UNAVAILABLE"


class ExpectedValues(BaseModel):
    """Reference values imported from a documented, separate calculation source."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    longitudes: dict[str, Decimal] = Field(default_factory=dict)
    signs: dict[str, str] = Field(default_factory=dict)
    houses: dict[str, int] = Field(default_factory=dict)
    house_lords: dict[str, str] = Field(default_factory=dict)
    d9_signs: dict[str, str] = Field(default_factory=dict)
    d10_signs: dict[str, str] = Field(default_factory=dict)
    birth_nakshatra: str | None = None
    birth_mahadasha_lord: str | None = None
    birth_mahadasha_end_utc: datetime | None = None

    def has_values(self) -> bool:
        return any(
            (
                self.longitudes,
                self.signs,
                self.houses,
                self.house_lords,
                self.d9_signs,
                self.d10_signs,
                self.birth_nakshatra,
                self.birth_mahadasha_lord,
                self.birth_mahadasha_end_utc,
            )
        )


class ReferenceFixture(BaseModel):
    """Fully specified synthetic input with an honest reference evidence state."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    purpose: str
    birth_date: date
    birth_time: time
    timezone: str
    latitude: float
    longitude: float
    utc: datetime
    calculation_profile: str
    reference_status: VerificationStatus
    reference_source: str | None = None
    reference_version: str | None = None
    reference_data_provenance: str | None = None
    reference_settings: dict[str, str] | None = None
    reference_artifact_sha256: str | None = Field(
        default=None, pattern=r"^[0-9a-f]{64}$"
    )
    expected: ExpectedValues = Field(default_factory=ExpectedValues)
    tolerance_degrees: Decimal | None = None
    tolerance_seconds: Decimal | None = None

    @model_validator(mode="after")
    def validate_reference(self) -> "ReferenceFixture":
        if self.calculation_profile != PROFILE:
            raise ValueError("fixture calculation profile differs from the fixed CALC-01 profile")
        if self.utc.tzinfo is None or self.utc.utcoffset() != timedelta(0):
            raise ValueError("fixture UTC instant must be timezone-aware UTC")
        if self.birth().utc_datetime != self.utc.astimezone(UTC):
            raise ValueError("fixture local time does not match its declared UTC instant")
        if self.reference_status is VerificationStatus.REFERENCE_UNAVAILABLE:
            if any(
                (
                    self.expected.has_values(),
                    self.reference_source,
                    self.reference_version,
                    self.reference_data_provenance,
                    self.reference_settings,
                    self.reference_artifact_sha256,
                )
            ):
                raise ValueError("pending fixture cannot contain reference values or source claims")
        elif self.reference_status is VerificationStatus.EXTERNAL_COMPARISON_UNRESOLVED:
            if not all(
                (
                    self.reference_source,
                    self.reference_version,
                    self.reference_data_provenance,
                    self.reference_settings,
                    self.reference_artifact_sha256,
                    self.expected.has_values(),
                )
            ):
                raise ValueError("external fixture requires full source provenance and values")
            if self.expected.longitudes and self.tolerance_degrees is None:
                raise ValueError("longitude references require a declared angular tolerance")
        else:
            raise ValueError("verification status is a test result, not a fixture input")
        return self

    def birth(self) -> BirthInput:
        return BirthInput(
            birth_date=self.birth_date,
            birth_time=self.birth_time,
            timezone=self.timezone,
            latitude=self.latitude,
            longitude=self.longitude,
        )


def load_fixtures() -> tuple[ReferenceFixture, ...]:
    """Load only the explicitly listed synthetic inputs."""
    raw = json.loads(FIXTURES.read_text(encoding="utf-8"))
    return tuple(ReferenceFixture.model_validate(item) for item in raw)


def angular_difference(expected: Decimal, actual: Decimal) -> Decimal:
    """Return the shortest signed difference on a 360-degree circle."""
    circle = Decimal("360")
    wrapped = (actual - expected) % circle
    if wrapped < 0:
        wrapped += circle
    return wrapped - Decimal("360") if wrapped >= Decimal("180") else wrapped


class Comparison(BaseModel):
    """One numerical comparison with declared units and acceptance tolerance."""

    model_config = ConfigDict(frozen=True)

    field: str
    expected: str
    actual: str
    difference: Decimal
    tolerance: Decimal
    unit: str
    passed: bool


def compare_longitude(
    field: str, expected: Decimal, actual: Decimal, tolerance_degrees: Decimal
) -> Comparison:
    if not Decimal("0") <= expected < Decimal("360"):
        raise ValueError("expected longitude must be normalized")
    if not Decimal("0") <= actual < Decimal("360"):
        raise ValueError("actual longitude must be normalized")
    if tolerance_degrees < 0:
        raise ValueError("tolerance must be nonnegative")
    difference = angular_difference(expected, actual)
    return Comparison(
        field=field,
        expected=str(expected),
        actual=str(actual),
        difference=difference,
        tolerance=tolerance_degrees,
        unit="degrees",
        passed=abs(difference) <= tolerance_degrees,
    )


def compare_utc_boundary(
    field: str, expected: datetime, actual: datetime, tolerance_seconds: Decimal
) -> Comparison:
    """Compare two explicitly aware UTC boundaries with a signed time difference."""
    if (
        expected.tzinfo is None
        or expected.utcoffset() != timedelta(0)
        or actual.tzinfo is None
        or actual.utcoffset() != timedelta(0)
    ):
        raise ValueError("boundary comparisons require aware UTC datetimes")
    if tolerance_seconds < 0:
        raise ValueError("tolerance must be nonnegative")
    difference_us = (actual - expected) // timedelta(microseconds=1)
    difference = Decimal(difference_us) / Decimal("1000000")
    return Comparison(
        field=field,
        expected=expected.isoformat(),
        actual=actual.isoformat(),
        difference=difference,
        tolerance=tolerance_seconds,
        unit="seconds",
        passed=abs(difference) <= tolerance_seconds,
    )


def compare_recorded_longitudes(
    fixture: ReferenceFixture, actual: dict[str, Decimal]
) -> tuple[Comparison, ...]:
    """Compare only sourced expected values; never synthesize missing references."""
    if fixture.reference_status is VerificationStatus.REFERENCE_UNAVAILABLE:
        return ()
    if fixture.tolerance_degrees is None:
        raise ValueError("reference longitude tolerance is missing")
    missing = set(fixture.expected.longitudes) - set(actual)
    if missing:
        raise ValueError(f"actual chart is missing reference fields: {sorted(missing)}")
    return tuple(
        compare_longitude(field, expected, actual[field], fixture.tolerance_degrees)
        for field, expected in fixture.expected.longitudes.items()
    )


def _shifted_birth(fixture: ReferenceFixture, offset_minutes: int) -> BirthInput:
    local = (fixture.utc + timedelta(minutes=offset_minutes)).astimezone(ZoneInfo(fixture.timezone))
    return BirthInput(
        birth_date=local.date(),
        birth_time=local.timetz().replace(tzinfo=None),
        timezone=fixture.timezone,
        latitude=fixture.latitude,
        longitude=fixture.longitude,
    )


def factual_snapshot(birth: BirthInput) -> dict[str, object]:
    """Calculate factual outputs for internal test analysis; no interpretation."""
    chart = ChartEngine(SwissEphemerisProvider()).calculate(birth)
    vargas = VargaEngine()
    d9 = vargas.calculate(chart, DivisionalChartType.D9)
    d10 = vargas.calculate(chart, DivisionalChartType.D10)
    chain = VimshottariDashaEngine().at(chart, birth.utc_datetime)
    moon = next(planet for planet in chart.planets if planet.body.value == "moon")
    return {
        "utc": birth.utc_datetime.isoformat(),
        "ascendant_longitude": str(chart.ascendant.longitude),
        "ascendant_sign": chart.ascendant.sign.value,
        "d1_signs": {planet.body.value: planet.sign.value for planet in chart.planets},
        "d1_houses": {planet.body.value: planet.house_number for planet in chart.planets},
        "house_lords": {
            str(house.number): SIGN_RULERS[house.sign].value for house in chart.houses
        },
        "d9_ascendant_sign": d9.ascendant.sign.value,
        "d9_signs": {planet.body.value: planet.sign.value for planet in d9.planets},
        "d9_houses": {planet.body.value: planet.house_number for planet in d9.planets},
        "d10_ascendant_sign": d10.ascendant.sign.value,
        "d10_signs": {planet.body.value: planet.sign.value for planet in d10.planets},
        "d10_houses": {planet.body.value: planet.house_number for planet in d10.planets},
        "moon_longitude": str(moon.longitude),
        "moon_nakshatra": moon.nakshatra.nakshatra.value,
        "birth_mahadasha_lord": chain.mahadasha.lord.value,
        "birth_antardasha_lord": chain.antardasha.lord.value,
        "birth_mahadasha_balance_microseconds": (
            (chain.mahadasha.end - birth.utc_datetime) // timedelta(microseconds=1)
        ),
        "birth_mahadasha_end_utc": chain.mahadasha.end.isoformat(),
        "birth_antardasha_end_utc": chain.antardasha.end.isoformat(),
        "provider": chart.provenance.provider.model_dump(mode="json"),
    }


def sensitivity(fixture: ReferenceFixture) -> dict[int, dict[str, object]]:
    """Return snapshots at fixed UTC offsets around the supplied birth instant."""
    return {
        offset: factual_snapshot(_shifted_birth(fixture, offset))
        for offset in OFFSETS_MINUTES
    }
