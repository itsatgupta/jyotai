"""Small deterministic utilities for timezone-aware half-open time intervals.

The common convention is ``[start, end)``: an interval includes its start and
excludes its end.  Therefore adjacent intervals touch without overlapping.
"""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, model_validator


class TimeInterval(BaseModel):
    """One normalized UTC half-open interval, ``[start, end)``."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    start: datetime
    end: datetime

    @model_validator(mode="after")
    def bounds_must_be_aware_ordered_and_normalized(self) -> "TimeInterval":
        for name, value in (("start", self.start), ("end", self.end)):
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError(f"{name} must be timezone-aware")
            if value.utcoffset() != UTC.utcoffset(value):
                raise ValueError(f"{name} must be normalized to UTC")
        if self.end <= self.start:
            raise ValueError("interval end must be after start")
        return self

    def contains(self, instant: datetime) -> bool:
        """Return whether an aware instant lies in this interval."""
        normalized = _as_utc(instant, "instant")
        return self.start <= normalized < self.end

    def intersection(self, other: "TimeInterval") -> "TimeInterval | None":
        """Return the shared half-open interval, or ``None`` when empty."""
        start = max(self.start, other.start)
        end = min(self.end, other.end)
        if end <= start:
            return None
        return TimeInterval(start=start, end=end)

    def clip(self, horizon: "TimeInterval") -> "TimeInterval | None":
        """Return this interval restricted to a requested horizon."""
        return self.intersection(horizon)


def sort_intervals(intervals: tuple[TimeInterval, ...]) -> tuple[TimeInterval, ...]:
    """Return deterministic ascending start/end ordering without merging intervals."""
    return tuple(sorted(intervals, key=lambda interval: (interval.start, interval.end)))


def _as_utc(value: datetime, name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)
