"""Immutable models for the separately governed Career timing package."""
# ruff: noqa: E501

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
    SUB_PERIOD = "SUB_PERIOD"


class TimingReleaseStatus(StrEnum):
    CANDIDATE_ADMITTED = "candidate_admitted"
    PRODUCTION_ACTIVE = "production_active"


class TimingSourceRecord(_FrozenModel):
    """Immutable v1 provenance; it is not changed by the v2 candidate."""

    source_work: Literal["Brihat Parāśara Horā Śāstra"] = "Brihat Parāśara Horā Śāstra"
    section: Literal["अथ दशाफलाध्यायः / Dasha-phala"] = "अथ दशाफलाध्यायः / Dasha-phala"
    verse: Literal["87"] = "87"
    page_locator: Literal[
        "printed p. 439; local artifact PDF p. 437; adjacent Hindi continuation PDF p. 438"
    ] = "printed p. 439; local artifact PDF p. 437; adjacent Hindi continuation PDF p. 438"
    sanskrit: Literal["सुखराशिस्थकर्मेशदशा राज्यप्रदायिनी ॥ ८७ ॥"] = "सुखराशिस्थकर्मेशदशा राज्यप्रदायिनी ॥ ८७ ॥"
    reviewed_translation: Literal[
        "The Dasha of the tenth-house lord situated in the fourth house is described as giving rājya-related results."
    ] = "The Dasha of the tenth-house lord situated in the fourth house is described as giving rājya-related results."
    reviewed_interpretation: Literal[
        "In the reviewed BPHS Dasha-phala passage, when the D1 tenth-house lord is placed in the fourth house, that lord’s Dasha is described as rājya-pradāyinī—giving rājya-related results. Within JyotishAI, a matching Vimshottari Mahadasha is presented only as broad career-related timing context. It does not guarantee employment, promotion, office, authority, income, a government role, or a specific event or date."
    ] = "In the reviewed BPHS Dasha-phala passage, when the D1 tenth-house lord is placed in the fourth house, that lord’s Dasha is described as rājya-pradāyinī—giving rājya-related results. Within JyotishAI, a matching Vimshottari Mahadasha is presented only as broad career-related timing context. It does not guarantee employment, promotion, office, authority, income, a government role, or a specific event or date."


class MoonVenusOwnExaltationTimingSourceRecord(_FrozenModel):
    source_id: Literal["bphs.timing.source.moon_md.venus_ad.140.v1"] = (
        "bphs.timing.source.moon_md.venus_ad.140.v1"
    )
    source_work: Literal["Brihat Parāśara Horā Śāstra"] = "Brihat Parāśara Horā Śāstra"
    section: Literal["अथान्तर्दशादिफलविचाराध्यायः"] = "अथान्तर्दशादिफलविचाराध्यायः"
    verse: Literal["140"] = "140"
    page_locator: Literal["printed p. 468; local artifact PDF p. 466"] = (
        "printed p. 468; local artifact PDF p. 466"
    )
    sanskrit: Literal["चन्द्रस्यान्तर्गते शुक्रे केन्द्रलाभत्रिकोणगे ।\nस्वोच्चे स्वक्षेत्रगे वापि राज्यलाभं करोति च ॥"] = (
        "चन्द्रस्यान्तर्गते शुक्रे केन्द्रलाभत्रिकोणगे ।\nस्वोच्चे स्वक्षेत्रगे वापि राज्यलाभं करोति च ॥"
    )
    reviewed_translation: Literal[
        "During a Moon Mahadasha and Venus Antardasha, Venus in a kendra, trine, or gain place, or in exaltation or its own sign, is described as producing rājya-lābha."
    ] = "During a Moon Mahadasha and Venus Antardasha, Venus in a kendra, trine, or gain place, or in exaltation or its own sign, is described as producing rājya-lābha."
    reviewed_interpretation: Literal[
        "During a Moon Mahadasha and Venus Antardasha, when natal D1 Venus is in its own sign or exaltation sign, the reviewed BPHS passage describes rājya-lābha. JyotishAI presents the complete deterministic Moon/Venus Antardasha interval only as bounded career/status-related timing context. It does not guarantee employment, promotion, office, authority, government role, income, salary change, or a specific event."
    ] = "During a Moon Mahadasha and Venus Antardasha, when natal D1 Venus is in its own sign or exaltation sign, the reviewed BPHS passage describes rājya-lābha. JyotishAI presents the complete deterministic Moon/Venus Antardasha interval only as bounded career/status-related timing context. It does not guarantee employment, promotion, office, authority, government role, income, salary change, or a specific event."
    local_hindi_ocr_note: Literal[
        "The local Hindi/OCR rendering appears to omit the Sanskrit lābha term; the Sanskrit v.140 record is retained exactly as reviewed."
    ] = "The local Hindi/OCR rendering appears to omit the Sanskrit lābha term; the Sanskrit v.140 record is retained exactly as reviewed."
    dignity_source_admission_references: tuple[str, ...] = (
        "jyotish.dignity.source-admission.v1: Rāśi-prabheda vv. 7–24 (own-sign)",
        "jyotish.dignity.source-admission.v1: Graha-svarūpa v. 38 (exaltation sign)",
    )
    scope: tuple[str, ...] = ("Moon MD / Venus AD", "D1 Venus own-sign OR exaltation-sign only")
    exclusions: tuple[str, ...] = (
        "no kendra/trikona/11th-house branch",
        "no vv.141–145",
        "no AD strengthening beyond the complete AD interval",
        "no event guarantee",
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


class MoonVenusOwnExaltationCareerTimingRule(_FrozenModel):
    rule_id: Literal["bphs.timing.vimshottari.career.moon_md.venus_ad.own_or_exaltation.v1"] = (
        "bphs.timing.vimshottari.career.moon_md.venus_ad.own_or_exaltation.v1"
    )
    rule_version: Literal["v1"] = "v1"
    source_id: Literal["bphs.timing.source.moon_md.venus_ad.140.v1"] = (
        "bphs.timing.source.moon_md.venus_ad.140.v1"
    )
    domain: Literal["career"] = "career"
    chart_scope: Literal["D1/Rashi"] = "D1/Rashi"
    dasha_system: Literal["Vimshottari"] = "Vimshottari"
    precision: Literal[TimingPrecision.SUB_PERIOD] = TimingPrecision.SUB_PERIOD
    required_fact_ids: tuple[str, ...] = (
        "jyotish.timing.vimshottari.mahadasha.lord",
        "jyotish.timing.vimshottari.antardasha.lord",
        "jyotish.timing.vimshottari.antardasha.start",
        "jyotish.timing.vimshottari.antardasha.end",
        "jyotish.d1.planet.venus.own_sign",
        "jyotish.d1.planet.venus.exaltation_sign",
    )
    exclusions: tuple[str, ...] = (
        "no kendra/trikona/11th-house branch",
        "no vv.141–145",
        "no AD strengthening beyond the complete AD interval",
        "no Pratyantardasha narrowing",
        "no transit refinement",
        "no exact event date",
        "no employment, promotion, office, authority, government-role, income, or salary-change guarantee",
        "no guaranteed event",
    )


class TimingRegistryRelease(_FrozenModel):
    release_id: Literal["jyotish.timing.career.candidate.v1"] = "jyotish.timing.career.candidate.v1"
    release_version: Literal["v1"] = "v1"
    status: Literal[TimingReleaseStatus.CANDIDATE_ADMITTED] = TimingReleaseStatus.CANDIDATE_ADMITTED
    source: TimingSourceRecord
    rules: tuple[CareerTimingRule, ...]
    activated_at: None = None


class CareerTimingCandidateReleaseV2(_FrozenModel):
    release_id: Literal["jyotish.timing.career.candidate@v2"] = "jyotish.timing.career.candidate@v2"
    release_version: Literal["v2"] = "v2"
    status: Literal[TimingReleaseStatus.CANDIDATE_ADMITTED] = TimingReleaseStatus.CANDIDATE_ADMITTED
    sources: tuple[TimingSourceRecord | MoonVenusOwnExaltationTimingSourceRecord, ...]
    rules: tuple[CareerTimingRule | MoonVenusOwnExaltationCareerTimingRule, ...]
    activated_at: None = None


class ProductionTimingRegistryRelease(_FrozenModel):
    release_id: Literal["jyotish.timing.production.career@v1"] = (
        "jyotish.timing.production.career@v1"
    )
    release_version: Literal["v1"] = "v1"
    status: Literal[TimingReleaseStatus.PRODUCTION_ACTIVE] = TimingReleaseStatus.PRODUCTION_ACTIVE
    source: TimingSourceRecord
    rules: tuple[CareerTimingRule, ...]
    activated_at: datetime

    @model_validator(mode="after")
    def requires_exactly_one_rule(self) -> "ProductionTimingRegistryRelease":
        if len(self.rules) != 1:
            raise ValueError("Career timing production v1 must contain exactly one rule")
        return self


class ActiveTimingReleasePointer(_FrozenModel):
    release_id: Literal["jyotish.timing.production.career@v1"] = (
        "jyotish.timing.production.career@v1"
    )
    release_version: Literal["v1"] = "v1"


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


class AntardashaTimingCondition(_FrozenModel):
    lord: DashaLord | None
    start: datetime | None
    end: datetime | None


class VenusDignityTimingCondition(_FrozenModel):
    own_sign: bool | None
    exaltation_sign: bool | None


class CareerTimingEvaluation(_FrozenModel):
    rule_id: str
    status: TimingRuleStatus
    natal_condition: NatalTimingCondition
    mahadasha: MahadashaTimingCondition


class MoonVenusCareerTimingEvaluation(_FrozenModel):
    rule_id: str
    status: TimingRuleStatus
    mahadasha: MahadashaTimingCondition
    antardasha: AntardashaTimingCondition
    venus_dignity: VenusDignityTimingCondition


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


class MoonVenusCareerTimingEvidence(_FrozenModel):
    domain: Literal["career"] = "career"
    rule_id: str
    status: TimingRuleStatus
    source: MoonVenusOwnExaltationTimingSourceRecord
    mahadasha: MahadashaTimingCondition
    antardasha: AntardashaTimingCondition
    venus_dignity: VenusDignityTimingCondition
    source_interval: TimeInterval | None
    effective_window: TimeInterval | None
    precision: Literal[TimingPrecision.SUB_PERIOD] = TimingPrecision.SUB_PERIOD
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
    precision: TimingPrecision | None = None
    precisions: tuple[TimingPrecision, ...] = ()
    evidence: tuple[CareerTimingEvidence | MoonVenusCareerTimingEvidence, ...]
    windows: tuple[CareerTimingWindow, ...]
    reviewed_statement: str
    limitations: tuple[str, ...]
    deterministic_wording: str
