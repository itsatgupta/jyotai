"""Tests for validated, canonical birth input."""

from datetime import UTC, date, datetime, time

import pytest
from pydantic import ValidationError

from astrologer.birth.models import BirthDetails, BirthInput
from astrologer.birth.normalization import BirthInputNormalizer


def test_normalizer_creates_canonical_timezone_aware_birth_input() -> None:
    details = BirthDetails(
        birth_date=date(1990, 1, 15),
        birth_time=time(9, 30),
        timezone="Asia/Kolkata",
        latitude=19.076,
        longitude=72.8777,
        place_name="  Mumbai  ",
        display_name="  Example Person  ",
    )

    normalized = BirthInputNormalizer().normalize(details)

    assert isinstance(normalized, BirthInput)
    assert normalized.place_name == "Mumbai"
    assert normalized.display_name == "Example Person"
    assert normalized.local_datetime.replace(tzinfo=None) == datetime(1990, 1, 15, 9, 30)
    assert normalized.local_datetime.tzinfo is not None
    assert normalized.utc_datetime == datetime(1990, 1, 15, 4, 0, tzinfo=UTC)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("timezone", "Not/A_Zone"),
        ("latitude", 90.1),
        ("latitude", -90.1),
        ("longitude", 180.1),
        ("longitude", -180.1),
        ("birth_time", "09:30+05:30"),
    ],
)
def test_birth_details_rejects_invalid_values(field: str, value: object) -> None:
    payload: dict[str, object] = {
        "birth_date": "1990-01-15",
        "birth_time": "09:30",
        "timezone": "Asia/Kolkata",
        "latitude": 19.076,
        "longitude": 72.8777,
    }
    payload[field] = value

    with pytest.raises(ValidationError):
        BirthDetails.model_validate(payload)


@pytest.mark.parametrize(
    ("birth_date", "birth_time", "expected_message"),
    [
        ("2025-03-09", "02:30", "do not exist"),
        ("2025-11-02", "01:30", "ambiguous"),
    ],
)
def test_canonical_birth_input_rejects_unresolvable_dst_times(
    birth_date: str, birth_time: str, expected_message: str
) -> None:
    with pytest.raises(ValidationError, match=expected_message):
        BirthInput(
            birth_date=birth_date,
            birth_time=birth_time,
            timezone="America/New_York",
            latitude=40.7128,
            longitude=-74.006,
        )


def test_empty_optional_text_is_normalized_to_none() -> None:
    details = BirthDetails(
        birth_date="1990-01-15",
        birth_time="09:30",
        timezone="Asia/Kolkata",
        latitude=19.076,
        longitude=72.8777,
        place_name="   ",
        display_name="\t",
    )

    assert details.place_name is None
    assert details.display_name is None
