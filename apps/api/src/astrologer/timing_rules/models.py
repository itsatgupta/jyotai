"""Immutable models for the separately governed Career timing package."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from astrologer.astrology.dasha import DashaLord
from astrologer.astrology.intervals import TimeInterval
from astrologer.birth.models import BirthInput


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class TimingRuleStatus(StrEnum):
    MATCH = "MATCH"
    FALSE = "FALSE"
    UNKNOWN = "UNKNOWN"


class TimingPrecision(StrEnum):
    BROAD_PERIOD = "BROAD_PERIOD"


class TimingReleaseStatus(StrEnum):
    CANDIDATE_ADMITTED = "candidate_admitted"
    PRODUCTION_ACTIVE = "production_active"


class TimingSourceRecord(_FrozenModel):
    """Reviewed source metadata owned by the timing-governance package only."""

    source_work: Literal["Brihat Parāśara Horā Śāstra"] = "Brihat Parāśara Horā Śāstra"
    section: Literal["अथ दशाफलाध्यायः / Dasha-phala"] = "अथ दशाफलाध्यायः / Dasha-phala"
    verse: Literal["87"] = "87"
    page_locator: Literal[
        "printed p. 439; local artifact PDF p. 437; adjacent Hindi continuation PDF p. 438"
    ] = "printed p. 439; local artifact PDF p. 437; adjacent Hindi continuation PDF p. 438"
    sanskrit: Literal["सुखराशिस्थकर्मेशदशा राज्यप्रदायिनी ॥ ८७ ॥"] = "सुखराशिस्थकर्मेशदशा राज्यप्रदायिनी ॥ ८७ ॥"
    reviewed_translation: Literal[
        "The Dasha of the tenth-house lord situated in the fourth house is described as giving "
        "rājya-related results."
    ] = (
        "The Dasha of the tenth-house lord situated in the fourth house is described as giving "
        "rājya-related results."
    )
    reviewed_interpretation: Literal[
        "In the reviewed BPHS Dasha-phala passage, when the D1 tenth-house lord is placed in "
        "the fourth house, that lord’s Dasha is described as rājya-pradāyinī—giving "
        "rājya-related results. Within JyotishAI, a matching Vimshottari Mahadasha is "
        "presented only as broad career-related timing context. It does not guarantee "
        "employment, promotion, office, authority, income, a government role, or a specific "
        "event or date."
    ] = (
        "In the reviewed BPHS Dasha-phala passage, when the D1 tenth-house lord is placed in "
        "the fourth house, that lord’s Dasha is described as rājya-pradāyinī—giving "
        "rājya-related results. Within JyotishAI, a matching Vimshottari Mahadasha is "
        "presented only as broad career-related timing context. It does not guarantee "
        "employment, promotion, office, authority, income, a government role, or a specific "
        "event or date."
    )


class CareerTimingRule(_FrozenModel):
    rule_id: Literal["bphs.timing.vimshottari.career.10th_lord.in_4.md.v1"] = (
        "bphs.timing.vimshottari.career.10th_lord.in_4.md.v1"
    )
    rule_version: Literal["v1"] = "v1"
    domain: Literal["career"] = "career"
    chart_scope: Literal["D1/Rashi"] = "D1/Rashi"
    dasha_system: Literal["Vimshottari"] = "Vimshottari"
    precision: Literal[TimingPrecision.BROAD_PERIOD] = TimingPrecision.BROAD_PERIOD
    required_fact_ids: tuple[str, ...] = (
        "jyotish.d1.house.10.lord",
        "jyotish.d1.house_lord.10.placement_house",
        "jyotish.timing.vimshottari.mahadasha.lord",
        "jyotish.timing.vimshottari.mahadasha.start",
        "jyotish.timing.vimshottari.mahadasha.end",
    )
    exclusions: tuple[str, ...] = (
        "no Antardasha narrowing",
        "no Pratyantardasha narrowing",
        "no transit refinement",
        "no exact event date",
        "no promotion claim",
        "no job-change claim",
        "no salary/income claim",
        "no government-role claim",
        "no authority guarantee",
        "no guaranteed event",
    )


class TimingRegistryRelease(_FrozenModel):
    release_id: Literal["jyotish.timing.career.candidate.v1"] = "jyotish.timing.career.candidate.v1"
    release_version: Literal["v1"] = "v1"
    status: Literal[TimingReleaseStatus.CANDIDATE_ADMITTED] = TimingReleaseStatus.CANDIDATE_ADMITTED
    source: TimingSourceRecord
    rules: tuple[CareerTimingRule, ...]
    activated_at: None = None


class CareerTimingRequest(_FrozenModel):
    birth_input: BirthInput
    domain: Literal["career"]
    as_of: datetime
    horizon_end: datetime

    @field_validator("as_of", "horizon_end")
    @classmethod
    def requires_aware_instant(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("as_of and horizon_end must be timezone-aware")
        return value

    @model_validator(mode="after")
    def requires_ordered_horizon(self) -> "CareerTimingRequest":
        if self.horizon_end.astimezone(UTC) <= self.as_of.astimezone(UTC):
            raise ValueError("horizon_end must be after as_of")
        return self


class NatalTimingCondition(_FrozenModel):
    tenth_house_lord: DashaLord | None
    placement_house: int | None


class MahadashaTimingCondition(_FrozenModel):
    lord: DashaLord | None
    start: datetime | None
    end: datetime | None


class CareerTimingEvaluation(_FrozenModel):
    rule_id: str
    status: TimingRuleStatus
    natal_condition: NatalTimingCondition
    mahadasha: MahadashaTimingCondition


class CareerTimingEvidence(_FrozenModel):
    domain: Literal["career"] = "career"
    rule_id: str
    status: TimingRuleStatus
    source: TimingSourceRecord
    natal_condition: NatalTimingCondition
    mahadasha: MahadashaTimingCondition
    precision: Literal[TimingPrecision.BROAD_PERIOD] = TimingPrecision.BROAD_PERIOD
    timing_answerability_established: bool
    reviewed_statement: str
    exclusions: tuple[str, ...]


class CareerTimingWindow(_FrozenModel):
    source_interval: TimeInterval
    effective_window: TimeInterval
    mahadasha_lord: DashaLord


class CareerTimingResponse(_FrozenModel):
    timing_release_id: str
    timing_release_version: str
    timing_release_status: TimingReleaseStatus
    timing_answerability_established: bool
    precision: Literal[TimingPrecision.BROAD_PERIOD] = TimingPrecision.BROAD_PERIOD
    evidence: tuple[CareerTimingEvidence, ...]
    windows: tuple[CareerTimingWindow, ...]
    reviewed_statement: str
    limitations: tuple[str, ...]
    deterministic_wording: str
