"""Pydantic models for collecting and canonicalizing birth details."""

from datetime import UTC, date, datetime, time
from typing import Annotated
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator

Latitude = Annotated[float, Field(ge=-90, le=90)]
Longitude = Annotated[float, Field(ge=-180, le=180)]


class BirthDetails(BaseModel):
    """User-provided local birth details before canonical normalization."""

    model_config = ConfigDict(str_strip_whitespace=True)

    birth_date: date
    birth_time: time
    timezone: str = Field(min_length=1)
    latitude: Latitude
    longitude: Longitude
    place_name: str | None = Field(default=None, max_length=256)
    display_name: str | None = Field(default=None, max_length=100)

    @field_validator("birth_time")
    @classmethod
    def birth_time_must_be_local_wall_time(cls, value: time) -> time:
        """Reject times carrying an offset because timezone is supplied separately."""
        if value.tzinfo is not None:
            msg = "birth_time must not include a UTC offset; provide timezone separately"
            raise ValueError(msg)
        return value

    @field_validator("timezone")
    @classmethod
    def timezone_must_be_an_iana_identifier(cls, value: str) -> str:
        """Validate and canonicalize the supplied IANA timezone identifier."""
        try:
            return ZoneInfo(value).key
        except ZoneInfoNotFoundError as error:
            msg = "timezone must be a valid IANA timezone identifier"
            raise ValueError(msg) from error

    @field_validator("place_name", "display_name", mode="before")
    @classmethod
    def empty_optional_text_is_none(cls, value: object) -> object:
        """Normalize optional empty text so canonical data has one empty representation."""
        if isinstance(value, str) and not value.strip():
            return None
        return value


class BirthInput(BirthDetails):
    """Canonical, timezone-aware birth input suitable for the chart engine.

    This model deliberately contains no astrology calculations. It preserves the
    entered local date, time, coordinates, and IANA timezone, while exposing
    unambiguous local and UTC timestamps for a future deterministic engine.
    """

    @model_validator(mode="after")
    def local_time_must_map_to_one_instant(self) -> "BirthInput":
        """Reject nonexistent or ambiguous civil times rather than guessing a UTC instant."""
        self._resolved_local_datetime()
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def local_datetime(self) -> datetime:
        """Return the entered local date and time with its IANA timezone attached."""
        return self._resolved_local_datetime()

    @computed_field  # type: ignore[prop-decorator]
    @property
    def utc_datetime(self) -> datetime:
        """Return the same birth instant represented in UTC."""
        return self.local_datetime.astimezone(UTC)

    def _resolved_local_datetime(self) -> datetime:
        local_wall_time = datetime.combine(self.birth_date, self.birth_time)
        timezone = ZoneInfo(self.timezone)
        candidates = [
            local_wall_time.replace(tzinfo=timezone, fold=fold)
            for fold in (0, 1)
            if _round_trips_to_local_time(local_wall_time, timezone, fold)
        ]
        instants = {candidate.astimezone(UTC) for candidate in candidates}

        if not instants:
            msg = "birth date and time do not exist in the supplied timezone"
            raise ValueError(msg)
        if len(instants) > 1:
            msg = "birth date and time are ambiguous in the supplied timezone"
            raise ValueError(msg)
        return candidates[0]


def _round_trips_to_local_time(local_wall_time: datetime, timezone: ZoneInfo, fold: int) -> bool:
    candidate = local_wall_time.replace(tzinfo=timezone, fold=fold)
    round_trip = candidate.astimezone(UTC).astimezone(timezone)
    return round_trip.replace(tzinfo=None) == local_wall_time and round_trip.fold == fold
