"""Immutable, language-only contracts for deterministic question routing."""

from datetime import date, datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class QuestionDomain(StrEnum):
    """The Task 12 vocabulary, intentionally aligned with governed domains."""

    GENERAL = "general"
    CAREER = "career"
    BUSINESS = "business"
    EDUCATION = "education"
    WEALTH = "wealth"
    CHILDREN = "children"
    SPIRITUALITY = "spirituality"
    TRAVEL = "travel"
    MARRIAGE = "marriage"
    HEALTH = "health"
    PROPERTY = "property"


class TemporalIntent(StrEnum):
    TIMELESS = "timeless"
    CURRENT = "current"
    FUTURE_GENERAL = "future_general"
    TIME_BOUND = "time_bound"
    HISTORICAL = "historical"
    MIXED = "mixed"


class QuestionShape(StrEnum):
    DESCRIPTIVE = "descriptive"
    POTENTIAL = "potential"
    TIMING = "timing"
    RETROSPECTIVE = "retrospective"
    COMPARATIVE = "comparative"
    EXPLANATORY = "explanatory"
    DECISION = "decision"


class RoutingStatus(StrEnum):
    ROUTABLE = "routable"
    NEEDS_CLARIFICATION = "needs_clarification"
    UNSUPPORTED = "unsupported"


class RoutingIssue(StrEnum):
    AMBIGUOUS_DOMAIN = "ambiguous_domain"
    UNSUPPORTED_LANGUAGE = "unsupported_language"
    REFERENCE_INSTANT_REQUIRED = "reference_instant_required"


class RelativeTimeExpression(StrEnum):
    THIS_YEAR = "this_year"
    NEXT_YEAR = "next_year"
    LAST_YEAR = "last_year"
    THIS_MONTH = "this_month"
    NEXT_MONTH = "next_month"
    LAST_MONTH = "last_month"


class TimeRangeKind(StrEnum):
    CALENDAR_YEAR = "calendar_year"
    CALENDAR_MONTH = "calendar_month"
    DATE_RANGE = "date_range"


class TimeRangeSource(StrEnum):
    ABSOLUTE = "absolute"
    RELATIVE_RESOLVED = "relative_resolved"


class QuestionRequest(_FrozenModel):
    """Original user language and an optional explicit temporal reference."""

    request_schema: Literal["jyotish-question-request"] = "jyotish-question-request"
    request_version: Literal["v1"] = "v1"
    question: str = Field(min_length=1, max_length=4000)
    reference_instant: datetime | None = None

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("question must not be blank")
        return value

    @field_validator("reference_instant")
    @classmethod
    def reference_instant_must_be_timezone_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("reference_instant must be timezone-aware")
        return value


class ResolvedTimeRange(_FrozenModel):
    """An inclusive, calendar-date range; never an astrological timing result."""

    range_kind: TimeRangeKind
    start_date: date
    end_date: date
    source: TimeRangeSource

    @model_validator(mode="after")
    def end_must_not_precede_start(self) -> "ResolvedTimeRange":
        if self.end_date < self.start_date:
            raise ValueError("end_date must not precede start_date")
        return self


class QuestionIntent(_FrozenModel):
    """One atomic, domain-scoped language classification without astrology output."""

    intent_id: str = Field(pattern=r"^intent-[1-9][0-9]*$")
    domain: QuestionDomain
    shape: QuestionShape
    temporal_intent: TemporalIntent
    requires_timing: bool
    time_range: ResolvedTimeRange | None = None
    unresolved_relative_time: RelativeTimeExpression | None = None

    @model_validator(mode="after")
    def temporal_fields_must_be_consistent(self) -> "QuestionIntent":
        if self.time_range is not None and self.unresolved_relative_time is not None:
            raise ValueError("time_range and unresolved_relative_time are mutually exclusive")
        timing_required = {
            TemporalIntent.TIME_BOUND,
            TemporalIntent.HISTORICAL,
            TemporalIntent.MIXED,
        }
        if self.temporal_intent in timing_required and not self.requires_timing:
            raise ValueError("time-bound, historical, and mixed intents require timing")
        if (
            self.temporal_intent
            in {
                TemporalIntent.TIMELESS,
                TemporalIntent.CURRENT,
                TemporalIntent.FUTURE_GENERAL,
            }
            and self.requires_timing
        ):
            raise ValueError("timeless, current, and future-general intents do not require timing")
        return self


class QuestionRoutingResult(_FrozenModel):
    """Versioned result from one deterministic, language-only routing pass."""

    result_schema: Literal["jyotish-question-routing-result"] = "jyotish-question-routing-result"
    result_version: Literal["v1"] = "v1"
    router_version: Literal["question-intent-router-v1"] = "question-intent-router-v1"
    request: QuestionRequest
    status: RoutingStatus
    intents: tuple[QuestionIntent, ...] = ()
    issues: tuple[RoutingIssue, ...] = ()

    @model_validator(mode="after")
    def result_must_preserve_a_coherent_routing_state(self) -> "QuestionRoutingResult":
        if len(self.intents) != len({intent.intent_id for intent in self.intents}):
            raise ValueError("question intent IDs must be unique")
        if len(self.issues) != len(set(self.issues)):
            raise ValueError("routing issues must be unique")
        if self.status is RoutingStatus.ROUTABLE and (not self.intents or self.issues):
            raise ValueError("routable results require intents and no issues")
        if self.status is RoutingStatus.NEEDS_CLARIFICATION and not self.issues:
            raise ValueError("needs_clarification results require at least one issue")
        if self.status is RoutingStatus.UNSUPPORTED:
            if self.intents or RoutingIssue.UNSUPPORTED_LANGUAGE not in self.issues:
                raise ValueError("unsupported results require only unsupported_language")
        return self
