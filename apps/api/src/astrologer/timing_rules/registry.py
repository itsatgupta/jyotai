"""Explicit candidate-only release for the first governed Career timing rule."""

from typing import Final

from astrologer.timing_rules.models import (
    CareerTimingRule,
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
