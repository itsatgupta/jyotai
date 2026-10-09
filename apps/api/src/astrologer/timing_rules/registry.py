"""Immutable timing releases and explicit production release selection."""

from datetime import UTC, datetime
from typing import Final

from astrologer.timing_rules.models import (
    ActiveTimingReleasePointer,
    CareerTimingRule,
    ProductionTimingRegistryRelease,
    TimingRegistryRelease,
    TimingSourceRecord,
)

SOURCE_RECORD: Final = TimingSourceRecord()
CAREER_TIMING_RULE: Final = CareerTimingRule()

# This release is intentionally candidate-admitted, not a global production release.
CANDIDATE_TIMING_RELEASE: Final = TimingRegistryRelease(
    source=SOURCE_RECORD,
    rules=(CAREER_TIMING_RULE,),
)

# Admission copies neither doctrine nor mutable candidate state: it binds the reviewed,
# immutable source and rule records into a separately named immutable production release.
PRODUCTION_CAREER_TIMING_RELEASE: Final = ProductionTimingRegistryRelease(
    source=SOURCE_RECORD,
    rules=(CAREER_TIMING_RULE,),
    activated_at=datetime(2026, 10, 9, tzinfo=UTC),
)

# This dedicated pointer is intentionally independent of the static production manifest.
ACTIVE_TIMING_RELEASE_POINTER: Final = ActiveTimingReleasePointer()
_PRODUCTION_RELEASES: Final = {
    (
        PRODUCTION_CAREER_TIMING_RELEASE.release_id,
        PRODUCTION_CAREER_TIMING_RELEASE.release_version,
    ): PRODUCTION_CAREER_TIMING_RELEASE,
}


def get_active_timing_release() -> ProductionTimingRegistryRelease:
    """Resolve only the explicitly pointed production release; never a candidate fallback."""
    key = (
        ACTIVE_TIMING_RELEASE_POINTER.release_id,
        ACTIVE_TIMING_RELEASE_POINTER.release_version,
    )
    return _PRODUCTION_RELEASES[key]
