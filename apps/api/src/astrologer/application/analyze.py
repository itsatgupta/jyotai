"""Stateless orchestration of approved deterministic analysis components."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from astrologer.application.context import (
    DeterministicAstrologyContext,
    DeterministicAstrologyContextService,
    DeterministicContextRequest,
)
from astrologer.astrology.derived_facts import to_fact_set
from astrologer.birth.models import BirthInput
from astrologer.evidence import (
    EvidenceBuilder,
    EvidencePackage,
    EvidenceSelectionResult,
    EvidenceSelector,
)
from astrologer.knowledge import (
    ACTIVE_PRODUCTION_RELEASE,
    FactEvaluationProvenance,
    GovernedRuleEvaluator,
)
from astrologer.questions import (
    QuestionIntentRouter,
    QuestionRequest,
    QuestionRoutingResult,
    RoutingStatus,
)


class DeterministicAnalysisRequest(BaseModel):
    """All caller-supplied inputs needed for one stateless analysis request."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    birth_input: BirthInput
    as_of: datetime
    question: str = Field(min_length=1, max_length=4000)

    @field_validator("as_of")
    @classmethod
    def as_of_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("as_of must be timezone-aware")
        return value


class DeterministicAnalysisResult(BaseModel):
    """Deterministic context, routing, and governed evidence without interpretation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    context: DeterministicAstrologyContext
    routing: QuestionRoutingResult
    evidence_package: EvidencePackage
    selections: tuple[EvidenceSelectionResult, ...] = ()


class DeterministicAnalysisService:
    """Compose existing deterministic services without adding astrology semantics."""

    def __init__(
        self,
        context_service: DeterministicAstrologyContextService,
        question_router: QuestionIntentRouter | None = None,
        governed_rule_evaluator: GovernedRuleEvaluator | None = None,
        evidence_builder: EvidenceBuilder | None = None,
        evidence_selector: EvidenceSelector | None = None,
    ) -> None:
        self._context_service = context_service
        self._question_router = question_router or QuestionIntentRouter()
        self._governed_rule_evaluator = governed_rule_evaluator or GovernedRuleEvaluator()
        self._evidence_builder = evidence_builder or EvidenceBuilder()
        self._evidence_selector = evidence_selector or EvidenceSelector()

    def analyze(self, request: DeterministicAnalysisRequest) -> DeterministicAnalysisResult:
        """Return existing approved outputs for one explicit, stateless request."""
        context = self._context_service.build(
            DeterministicContextRequest(birth_input=request.birth_input, as_of=request.as_of)
        )
        routing = self._question_router.route(
            QuestionRequest(question=request.question, reference_instant=request.as_of)
        )
        facts = to_fact_set(context.derived_facts)
        evaluations = self._governed_rule_evaluator.evaluate(
            ACTIVE_PRODUCTION_RELEASE.manifest,
            ACTIVE_PRODUCTION_RELEASE.envelopes,
            ACTIVE_PRODUCTION_RELEASE.registry,
            ACTIVE_PRODUCTION_RELEASE.fact_contract,
            facts,
            FactEvaluationProvenance.from_derived_fact_bundle(context.derived_facts),
        )
        package = self._evidence_builder.build(
            context, ACTIVE_PRODUCTION_RELEASE.manifest, evaluations
        )
        selections = (
            tuple(self._evidence_selector.select(intent, package) for intent in routing.intents)
            if routing.status is RoutingStatus.ROUTABLE
            else ()
        )
        return DeterministicAnalysisResult(
            context=context,
            routing=routing,
            evidence_package=package,
            selections=selections,
        )
