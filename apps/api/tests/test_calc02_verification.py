"""CALC-02 comparison safeguards; no synthetic value is external evidence."""

from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from calc01_support import (
    ReferenceFixture,
    VerificationStatus,
    compare_exact,
    compare_longitude_arcseconds,
    compare_utc_boundary,
    load_fixtures,
)
from pydantic import ValidationError


def test_angular_difference_has_explicit_arcseconds_and_wraparound() -> None:
    result = compare_longitude_arcseconds(
        "moon", Decimal("359.999"), Decimal("0.001"), Decimal("8")
    )
    assert result.unit == "arcseconds"
    assert result.difference == Decimal("7.200")
    assert result.tolerance == Decimal("8")
    assert result.passed
    assert not compare_longitude_arcseconds(
        "moon", Decimal("0.001"), Decimal("359.999"), Decimal("7")
    ).passed


def test_exact_placements_and_period_order_report_both_sides() -> None:
    sign = compare_exact("d9.moon.sign", "aries", "taurus")
    house = compare_exact("d1.moon.house", 4, 4)
    order = compare_exact(
        "mahadasha.order", ("ketu", "venus", "sun"), ("ketu", "sun", "venus")
    )
    assert not sign.passed and (sign.expected, sign.actual) == ("aries", "taurus")
    assert house.passed
    assert not order.passed and order.actual == ("ketu", "sun", "venus")


def test_boundary_comparison_requires_explicit_utc_normalization() -> None:
    expected = datetime(2024, 7, 1, 16, tzinfo=UTC)
    local = expected.astimezone(timezone(-timedelta(hours=4)))
    with pytest.raises(ValueError, match="aware UTC"):
        compare_utc_boundary("md.end", expected, local, Decimal("0"))
    result = compare_utc_boundary("md.end", expected, local.astimezone(UTC), Decimal("0"))
    assert result.difference == Decimal("0") and result.passed


def test_pending_fixture_cannot_be_promoted_to_mismatch_or_verified() -> None:
    fixture = load_fixtures()[0]
    for status in (
        VerificationStatus.REFERENCE_MISMATCH_INVESTIGATION_REQUIRED,
        VerificationStatus.INDEPENDENT_VERIFIED,
    ):
        with pytest.raises(ValidationError, match="verification status is a test result"):
            ReferenceFixture.model_validate(
                fixture.model_dump() | {"reference_status": status}
            )
