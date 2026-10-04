"""Application-owned governed dashboard insight retrieval.

The dashboard deliberately names its fixed supported domains. It never uses
the natural-language question router to discover them.
"""

from datetime import datetime
from typing import Literal, cast

from pydantic import BaseModel, ConfigDict, Field, field_validator

from astrologer.application.analyze import (
    DeterministicAnalysisRequest,
    DeterministicAnalysisService,
)
from astrologer.birth.models import BirthInput
from astrologer.composition import ComposedAnswer, DeterministicAnswerComposer
from astrologer.evidence import EvidenceSelectionResult, InterpretationEvidenceBuilder
from astrologer.questions.models import (
    QuestionDomain,
    QuestionIntent,
    QuestionShape,
    TemporalIntent,
)

DashboardDomain = Literal[
    "career", "wealth", "education", "business", "children", "spirituality", "travel", "friends"
]

_DASHBOARD_DOMAINS: tuple[QuestionDomain, ...] = (
    QuestionDomain.CAREER,
    QuestionDomain.WEALTH,
    QuestionDomain.EDUCATION,
    QuestionDomain.BUSINESS,
    QuestionDomain.CHILDREN,
    QuestionDomain.SPIRITUALITY,
    QuestionDomain.TRAVEL,
    QuestionDomain.FRIENDS,
)


class DashboardInsightsRequest(BaseModel):
    """Inputs needed to deterministically derive one dashboard insight set."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    birth_input: BirthInput
    as_of: datetime

    @field_validator("as_of")
    @classmethod
    def as_of_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("as_of must be timezone-aware")
        return value


class DashboardInsight(BaseModel):
    """One exact-domain view of governed availability and reviewed wording."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    domain: DashboardDomain
    answers: tuple[ComposedAnswer, ...] = ()
    has_matched_evidence: bool
    matched_count: int = Field(ge=0)
    unmatched_count: int = Field(ge=0)
    unknown_count: int = Field(ge=0)


class DashboardInsightsResult(BaseModel):
    """Stable, ordered dashboard response without question-routing output."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    insights: tuple[DashboardInsight, ...]


class DashboardInsightsService:
    """Compose fixed dashboard domains through the existing governed pipeline."""

    def __init__(
        self,
        analysis_service: DeterministicAnalysisService,
        interpretation_evidence_builder: InterpretationEvidenceBuilder,
        answer_composer: DeterministicAnswerComposer,
    ) -> None:
        self._analysis_service = analysis_service
        self._interpretation_evidence_builder = interpretation_evidence_builder
        self._answer_composer = answer_composer

    def retrieve(self, request: DashboardInsightsRequest) -> DashboardInsightsResult:
        """Return exactly the application-owned dashboard domain sequence."""
        _, selections = self._analysis_service.analyze_explicit_intents(
            DeterministicAnalysisRequest(
                birth_input=request.birth_input,
                as_of=request.as_of,
                question="Dashboard governed insight",
            ),
            _dashboard_intents(),
        )
        return DashboardInsightsResult(insights=tuple(self._insight(item) for item in selections))

    def _insight(self, selection: EvidenceSelectionResult) -> DashboardInsight:
        evidence = self._interpretation_evidence_builder.build(selection)
        answers = (
            (self._answer_composer.compose("Dashboard governed insight", evidence),)
            if selection.selected_matched
            else ()
        )
        return DashboardInsight(
            domain=cast(DashboardDomain, selection.question_intent.domain.value),
            answers=answers,
            has_matched_evidence=selection.capability_summary.has_matched_evidence,
            matched_count=len(selection.selected_matched),
            unmatched_count=len(selection.relevant_unmatched),
            unknown_count=len(selection.relevant_unknown),
        )


def _dashboard_intents() -> tuple[QuestionIntent, ...]:
    """Create fixed application intents without natural-language routing."""
    return tuple(
        QuestionIntent(
            intent_id=f"intent-{index}",
            domain=domain,
            shape=QuestionShape.DESCRIPTIVE,
            temporal_intent=TemporalIntent.TIMELESS,
            requires_timing=False,
        )
        for index, domain in enumerate(_DASHBOARD_DOMAINS, start=1)
    )
