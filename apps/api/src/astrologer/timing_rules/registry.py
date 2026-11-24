"""Immutable timing releases and explicit production release selection."""

from datetime import UTC, datetime
from typing import Final

from astrologer.knowledge.admit02_pack_v1 import admit02_review
from astrologer.knowledge.models import ReviewCategory
from astrologer.timing_rules.models import (
    ActiveTimingReleasePointer,
    CareerTimingCandidateReleaseV2,
    CareerTimingCandidateReleaseV89,
    CareerTimingRule,
    MoonVenusOwnExaltationCareerTimingRule,
    MoonVenusOwnExaltationTimingSourceRecord,
    MoonVenusOwnExaltationTimingSourceRecordAdmit02,
    NinthLordInTenthMahadashaCareerTimingRule,
    NinthLordInTenthTimingSourceRecord,
    ProductionCareerTimingReleaseV2,
    ProductionCareerTimingReleaseV3,
    ProductionTimingRegistryRelease,
    TimingRegistryRelease,
    TimingSourceRecord,
    TimingSourceRecordAdmit02,
)

SOURCE_RECORD: Final = TimingSourceRecord()
CAREER_TIMING_RULE: Final = CareerTimingRule()
MOON_VENUS_OWN_OR_EXALTATION_TIMING_SOURCE: Final = MoonVenusOwnExaltationTimingSourceRecord()
MOON_VENUS_OWN_OR_EXALTATION_TIMING_RULE: Final = MoonVenusOwnExaltationCareerTimingRule()
NINTH_LORD_IN_TENTH_TIMING_SOURCE: Final = NinthLordInTenthTimingSourceRecord()
NINTH_LORD_IN_TENTH_TIMING_RULE: Final = NinthLordInTenthMahadashaCareerTimingRule()

# This release is intentionally candidate-admitted, not a global production release.
CANDIDATE_TIMING_RELEASE: Final = TimingRegistryRelease(
    source=SOURCE_RECORD,
    rules=(CAREER_TIMING_RULE,),
)

# This candidate is deliberately not registered in _PRODUCTION_RELEASES and cannot be
# selected by the active pointer or ordinary API dependency.
CANDIDATE_CAREER_TIMING_RELEASE_V2: Final = CareerTimingCandidateReleaseV2(
    sources=(SOURCE_RECORD, MOON_VENUS_OWN_OR_EXALTATION_TIMING_SOURCE),
    rules=(CAREER_TIMING_RULE, MOON_VENUS_OWN_OR_EXALTATION_TIMING_RULE),
)

# BPHS Dasha-phala v.89 is separately admitted for candidate evaluation only.  It is not
# composed into v1/v2 and is intentionally absent from _PRODUCTION_RELEASES.
CANDIDATE_CAREER_TIMING_RELEASE_V89: Final = CareerTimingCandidateReleaseV89(
    source=NINTH_LORD_IN_TENTH_TIMING_SOURCE,
    rules=(NINTH_LORD_IN_TENTH_TIMING_RULE,),
)

# Admission copies neither doctrine nor mutable candidate state: it binds the reviewed,
# immutable source and rule records into a separately named immutable production release.
PRODUCTION_CAREER_TIMING_RELEASE_V1: Final = ProductionTimingRegistryRelease(
    source=SOURCE_RECORD,
    rules=(CAREER_TIMING_RULE,),
    activated_at=datetime(2026, 10, 9, tzinfo=UTC),
)

# Production v2 is a new immutable admission. It reuses the reviewed records without
# mutating either the historical v1 production release or the candidate release.
PRODUCTION_CAREER_TIMING_RELEASE_V2: Final = ProductionCareerTimingReleaseV2(
    sources=(SOURCE_RECORD, MOON_VENUS_OWN_OR_EXALTATION_TIMING_SOURCE),
    rules=(CAREER_TIMING_RULE, MOON_VENUS_OWN_OR_EXALTATION_TIMING_RULE),
    activated_at=datetime(2026, 10, 10, tzinfo=UTC),
)

# Production v3 (NEXT-ADMIT-02): the same two rules and conditions, with the reviewer's wording
# for v.87 and v.140 (Sitting 1 items 1 and 2) and his review record.  v1 and v2 stay unchanged.
SOURCE_RECORD_ADMIT02: Final = TimingSourceRecordAdmit02()
MOON_VENUS_OWN_OR_EXALTATION_TIMING_SOURCE_ADMIT02: Final = (
    MoonVenusOwnExaltationTimingSourceRecordAdmit02()
)
PRODUCTION_CAREER_TIMING_RELEASE_V3: Final = ProductionCareerTimingReleaseV3(
    sources=(SOURCE_RECORD_ADMIT02, MOON_VENUS_OWN_OR_EXALTATION_TIMING_SOURCE_ADMIT02),
    rules=(CAREER_TIMING_RULE, MOON_VENUS_OWN_OR_EXALTATION_TIMING_RULE),
    activated_at=datetime(2026, 11, 24, tzinfo=UTC),
    review=admit02_review(ReviewCategory.INTERPRETATION_REVIEW, "Sitting 1 items 1 and 2"),
)

# This dedicated pointer is intentionally independent of the static production manifest.
ACTIVE_TIMING_RELEASE_POINTER: Final = ActiveTimingReleasePointer()
_PRODUCTION_RELEASES: Final[
    dict[tuple[str, str], ProductionTimingRegistryRelease | ProductionCareerTimingReleaseV2]
] = {
    (
        PRODUCTION_CAREER_TIMING_RELEASE_V1.release_id,
        PRODUCTION_CAREER_TIMING_RELEASE_V1.release_version,
    ): PRODUCTION_CAREER_TIMING_RELEASE_V1,
    (
        PRODUCTION_CAREER_TIMING_RELEASE_V2.release_id,
        PRODUCTION_CAREER_TIMING_RELEASE_V2.release_version,
    ): PRODUCTION_CAREER_TIMING_RELEASE_V2,
    (
        PRODUCTION_CAREER_TIMING_RELEASE_V3.release_id,
        PRODUCTION_CAREER_TIMING_RELEASE_V3.release_version,
    ): PRODUCTION_CAREER_TIMING_RELEASE_V3,
}


def get_active_timing_release() -> (
    ProductionTimingRegistryRelease | ProductionCareerTimingReleaseV2
):
    """Resolve only the explicitly pointed production release; never a candidate fallback."""
    key = (
        ACTIVE_TIMING_RELEASE_POINTER.release_id,
        ACTIVE_TIMING_RELEASE_POINTER.release_version,
    )
    return _PRODUCTION_RELEASES[key]
