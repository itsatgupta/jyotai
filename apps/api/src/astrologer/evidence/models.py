"""Immutable, governed deterministic evidence-package models.

These models preserve evaluated rule evidence and provenance. They deliberately
contain no prediction, aggregation, rule evaluation, or source-text rendering.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator

from astrologer.application.context import (
    CONTEXT_VERSION,
    DeterministicAstrologyContextProvenance,
)
from astrologer.knowledge.corpus import ProductionCorpusManifest
from astrologer.knowledge.evaluation import (
    FactEvaluationProvenance,
    GovernedEvaluationProvenance,
    canonical_sha256,
)
from astrologer.knowledge.models import (
    ChartScope,
    EvidenceDirection,
    JyotishDomain,
    RulePosture,
    RuleTaxonomy,
)
from astrologer.rules.models import EvaluatedCondition, EvaluationStatus

_SHA256 = r"^[a-f0-9]{64}$"


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ResolvedEvidenceFact(_FrozenModel):
    """One value actually resolved by the upstream governed evaluation."""

    fact_id: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$")
    value: JsonValue


class EvidenceItem(_FrozenModel):
    """One status-preserving governed rule evaluation for downstream use."""

    evidence_item_id: str = Field(min_length=1, max_length=256)
    evidence_item_version: Literal["evidence-item-v1"] = "evidence-item-v1"
    evaluation_status: EvaluationStatus
    evidence_direction: EvidenceDirection
    rule_id: str
    rule_version: str
    effect_key: str
    domain: JyotishDomain
    taxonomy: RuleTaxonomy
    posture: RulePosture
    chart_scope: ChartScope
    referenced_fact_ids: tuple[str, ...]
    resolved_facts: tuple[ResolvedEvidenceFact, ...]
    unresolved_fact_ids: tuple[str, ...]
    condition_trace: EvaluatedCondition
    governance_provenance: GovernedEvaluationProvenance
    fact_provenance: FactEvaluationProvenance

    @model_validator(mode="after")
    def facts_must_preserve_evaluation_partition(self) -> "EvidenceItem":
        resolved_ids = tuple(fact.fact_id for fact in self.resolved_facts)
        if len(resolved_ids) != len(set(resolved_ids)):
            raise ValueError("resolved evidence fact IDs must be unique")
        if set(resolved_ids) | set(self.unresolved_fact_ids) != set(self.referenced_fact_ids):
            raise ValueError("resolved and unresolved facts must partition referenced facts")
        if set(resolved_ids) & set(self.unresolved_fact_ids):
            raise ValueError("a fact cannot be both resolved and unresolved")
        if self.rule_id != self.governance_provenance.rule_id or self.rule_version != (
            self.governance_provenance.rule_version
        ):
            raise ValueError("evidence item rule identity must match governance provenance")
        return self


class EvidenceContextIdentity(_FrozenModel):
    """Compact identity for a Task 10 context without copying birth input."""

    context_version: Literal["deterministic-astrology-context-v1"] = CONTEXT_VERSION
    calculation_instant: datetime
    requested_as_of: datetime
    normalized_as_of_utc: datetime
    context_content_sha256: str = Field(pattern=_SHA256)
    context_provenance: DeterministicAstrologyContextProvenance


class EvidenceEvaluationSummary(_FrozenModel):
    """Counts statuses only; it deliberately has no score or confidence fields."""

    total_evaluations: int = Field(ge=0)
    matched_count: int = Field(ge=0)
    unmatched_count: int = Field(ge=0)
    unknown_count: int = Field(ge=0)

    @model_validator(mode="after")
    def counts_must_sum(self) -> "EvidenceEvaluationSummary":
        if self.total_evaluations != self.matched_count + self.unmatched_count + self.unknown_count:
            raise ValueError("evidence evaluation summary counts must sum to total")
        return self


class EvidencePackage(_FrozenModel):
    """A hashable, complete release view of governed rule evaluations."""

    package_schema: Literal["jyotish-evidence-package"] = "jyotish-evidence-package"
    package_version: Literal["v1"] = "v1"
    builder_version: Literal["evidence-builder-v1"] = "evidence-builder-v1"
    context_identity: EvidenceContextIdentity
    corpus_release: ProductionCorpusManifest
    manifest_content_sha256: str = Field(pattern=_SHA256)
    matched_evidence: tuple[EvidenceItem, ...] = ()
    unmatched_evaluations: tuple[EvidenceItem, ...] = ()
    unknown_evaluations: tuple[EvidenceItem, ...] = ()
    evaluation_summary: EvidenceEvaluationSummary
    package_content_sha256: str = Field(pattern=_SHA256)

    @model_validator(mode="after")
    def package_must_be_consistent_and_hashable(self) -> "EvidencePackage":
        if self.manifest_content_sha256 != self.corpus_release.content_sha256():
            raise ValueError("evidence package manifest hash does not match corpus release")
        collections = (
            (self.matched_evidence, EvaluationStatus.TRUE),
            (self.unmatched_evaluations, EvaluationStatus.FALSE),
            (self.unknown_evaluations, EvaluationStatus.UNKNOWN),
        )
        keys: list[tuple[str, str]] = []
        for items, status in collections:
            item_keys = tuple((item.rule_id, item.rule_version) for item in items)
            if item_keys != tuple(sorted(item_keys)):
                raise ValueError("evidence items must use deterministic rule ID/version order")
            if any(item.evaluation_status is not status for item in items):
                raise ValueError("evidence item is in the wrong status collection")
            keys.extend(item_keys)
        if len(keys) != len(set(keys)):
            raise ValueError("evidence package rule revisions must be unique")
        summary = EvidenceEvaluationSummary(
            total_evaluations=len(keys),
            matched_count=len(self.matched_evidence),
            unmatched_count=len(self.unmatched_evaluations),
            unknown_count=len(self.unknown_evaluations),
        )
        if self.evaluation_summary != summary:
            raise ValueError("evidence evaluation summary does not match item collections")
        if self.package_content_sha256 != self.content_sha256():
            raise ValueError("evidence package content hash is invalid")
        return self

    def content_sha256(self) -> str:
        """Hash all package content except the self-referential package hash."""
        payload = self.model_dump(mode="json", exclude={"package_content_sha256"})
        return canonical_sha256(payload)
