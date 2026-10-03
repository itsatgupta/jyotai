"""Internal, renderer-safe projection of selected governed evidence.

This boundary deliberately admits only an exact-domain selection from the
explicit active production release.  It is evidence for a future renderer, not
an answer, and it neither calculates nor interprets astrology.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from astrologer.evidence.models import EvidenceItem
from astrologer.evidence.selection_models import (
    EXACT_DOMAIN_SELECTION_POLICY_V1,
    EvidenceSelectionPolicy,
    EvidenceSelectionResult,
)
from astrologer.knowledge.career_pack_v1 import ACTIVE_PRODUCTION_RELEASE
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
from astrologer.questions.models import QuestionDomain, QuestionShape
from astrologer.rules.models import EvaluationStatus

_SHA256 = r"^[a-f0-9]{64}$"


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class InterpretationEvidenceBuildError(ValueError):
    """Raised when non-selected or non-admitted material reaches this boundary."""


class InterpretationEvidenceIntent(_FrozenModel):
    """The minimal question context safe for an interpretation consumer.

    Time ranges are intentionally absent.  They are language-routing context,
    not astrological timing evidence.
    """

    intent_id: str
    domain: QuestionDomain
    shape: QuestionShape
    timing_requested: bool


class InterpretationEvidenceItem(_FrozenModel):
    """One selected, status-preserving governed finding without source prose."""

    evidence_item_id: str
    rule_id: str
    rule_version: str
    effect_key: str
    domain: JyotishDomain
    taxonomy: RuleTaxonomy
    posture: RulePosture
    chart_scope: ChartScope
    evaluation_status: EvaluationStatus
    evidence_direction: EvidenceDirection
    referenced_fact_ids: tuple[str, ...]
    resolved_fact_ids: tuple[str, ...]
    unresolved_fact_ids: tuple[str, ...]
    governance_provenance: GovernedEvaluationProvenance
    fact_provenance: FactEvaluationProvenance

    @model_validator(mode="after")
    def item_must_remain_a_governed_fact_partition(self) -> "InterpretationEvidenceItem":
        if set(self.resolved_fact_ids) | set(self.unresolved_fact_ids) != set(
            self.referenced_fact_ids
        ):
            raise ValueError("resolved and unresolved fact IDs must partition referenced fact IDs")
        if set(self.resolved_fact_ids) & set(self.unresolved_fact_ids):
            raise ValueError("a fact ID cannot be both resolved and unresolved")
        if self.rule_id != self.governance_provenance.rule_id or self.rule_version != (
            self.governance_provenance.rule_version
        ):
            raise ValueError("interpretation evidence identity must match governance provenance")
        return self

    @classmethod
    def from_selected_item(cls, item: EvidenceItem) -> "InterpretationEvidenceItem":
        """Project only the governed fields permitted beyond selection."""
        return cls(
            evidence_item_id=item.evidence_item_id,
            rule_id=item.rule_id,
            rule_version=item.rule_version,
            effect_key=item.effect_key,
            domain=item.domain,
            taxonomy=item.taxonomy,
            posture=item.posture,
            chart_scope=item.chart_scope,
            evaluation_status=item.evaluation_status,
            evidence_direction=item.evidence_direction,
            referenced_fact_ids=item.referenced_fact_ids,
            resolved_fact_ids=tuple(fact.fact_id for fact in item.resolved_facts),
            unresolved_fact_ids=item.unresolved_fact_ids,
            governance_provenance=item.governance_provenance,
            fact_provenance=item.fact_provenance,
        )


class InterpretationEvidence(_FrozenModel):
    """Immutable contract containing only selected, admitted interpretation evidence."""

    contract_schema: Literal["jyotish-interpretation-evidence"] = "jyotish-interpretation-evidence"
    contract_version: Literal["v1"] = "v1"
    builder_version: Literal["interpretation-evidence-builder-v1"] = (
        "interpretation-evidence-builder-v1"
    )
    intent: InterpretationEvidenceIntent
    selection_policy: EvidenceSelectionPolicy
    selection_content_sha256: str = Field(pattern=_SHA256)
    evidence_package_content_sha256: str = Field(pattern=_SHA256)
    manifest_id: str
    manifest_version: str
    manifest_content_sha256: str = Field(pattern=_SHA256)
    timing_answerability_established: Literal[False] = False
    selected_matched: tuple[InterpretationEvidenceItem, ...] = ()
    relevant_unmatched: tuple[InterpretationEvidenceItem, ...] = ()
    relevant_unknown: tuple[InterpretationEvidenceItem, ...] = ()
    contract_content_sha256: str = Field(pattern=_SHA256)

    @model_validator(mode="after")
    def evidence_must_be_exact_domain_status_partition_and_hashable(
        self,
    ) -> "InterpretationEvidence":
        collections = (
            (self.selected_matched, EvaluationStatus.TRUE),
            (self.relevant_unmatched, EvaluationStatus.FALSE),
            (self.relevant_unknown, EvaluationStatus.UNKNOWN),
        )
        keys: list[tuple[str, str]] = []
        for items, status in collections:
            item_keys = tuple((item.rule_id, item.rule_version) for item in items)
            if item_keys != tuple(sorted(item_keys)):
                raise ValueError(
                    "interpretation evidence items must use deterministic rule ID/version order"
                )
            if any(item.evaluation_status is not status for item in items):
                raise ValueError("interpretation evidence item is in the wrong status collection")
            if any(item.domain.value != self.intent.domain.value for item in items):
                raise ValueError("interpretation evidence must remain exact-domain")
            keys.extend(item_keys)
        if len(keys) != len(set(keys)):
            raise ValueError("interpretation evidence rule revisions must be unique")
        if self.timing_answerability_established is not False:
            raise ValueError(
                "current interpretation evidence cannot establish timing answerability"
            )
        if self.contract_content_sha256 != self.content_sha256():
            raise ValueError("interpretation evidence content hash is invalid")
        return self

    def content_sha256(self) -> str:
        """Hash contract content except its self-referential hash."""
        return canonical_sha256(self.model_dump(mode="json", exclude={"contract_content_sha256"}))


class InterpretationEvidenceBuilder:
    """Build the internal contract from one exact-domain selected release view."""

    builder_version = "interpretation-evidence-builder-v1"

    def __init__(
        self,
        production_manifest: ProductionCorpusManifest = ACTIVE_PRODUCTION_RELEASE.manifest,
    ) -> None:
        self._production_manifest = production_manifest

    def build(self, selection: EvidenceSelectionResult) -> InterpretationEvidence:
        """Admit only selected items proven to belong to this immutable release."""
        self._validate_selection(selection)
        matched = self._project(selection.selected_matched)
        unmatched = self._project(selection.relevant_unmatched)
        unknown = self._project(selection.relevant_unknown)
        intent = InterpretationEvidenceIntent(
            intent_id=selection.question_intent.intent_id,
            domain=selection.question_intent.domain,
            shape=selection.question_intent.shape,
            timing_requested=selection.capability_summary.timing_requested,
        )
        provisional = InterpretationEvidence.model_construct(
            intent=intent,
            selection_policy=selection.policy,
            selection_content_sha256=selection.selection_content_sha256,
            evidence_package_content_sha256=selection.evidence_package_content_sha256,
            manifest_id=selection.manifest_id,
            manifest_version=selection.manifest_version,
            manifest_content_sha256=selection.manifest_content_sha256,
            timing_answerability_established=False,
            selected_matched=matched,
            relevant_unmatched=unmatched,
            relevant_unknown=unknown,
            contract_content_sha256="0" * 64,
        )
        return InterpretationEvidence(
            intent=intent,
            selection_policy=selection.policy,
            selection_content_sha256=selection.selection_content_sha256,
            evidence_package_content_sha256=selection.evidence_package_content_sha256,
            manifest_id=selection.manifest_id,
            manifest_version=selection.manifest_version,
            manifest_content_sha256=selection.manifest_content_sha256,
            timing_answerability_established=False,
            selected_matched=matched,
            relevant_unmatched=unmatched,
            relevant_unknown=unknown,
            contract_content_sha256=provisional.content_sha256(),
        )

    def _validate_selection(self, selection: EvidenceSelectionResult) -> None:
        manifest = self._production_manifest
        if selection.policy != EXACT_DOMAIN_SELECTION_POLICY_V1:
            raise InterpretationEvidenceBuildError(
                "interpretation evidence requires exact-domain policy"
            )
        if (
            selection.manifest_id != manifest.manifest_id
            or selection.manifest_version != manifest.manifest_version
            or selection.manifest_content_sha256 != manifest.content_sha256()
        ):
            raise InterpretationEvidenceBuildError(
                "interpretation evidence requires the explicit active production release"
            )
        admitted = {(rule.rule_id, rule.rule_version): rule for rule in manifest.rules}
        for item in (
            selection.selected_matched + selection.relevant_unmatched + selection.relevant_unknown
        ):
            member = admitted.get((item.rule_id, item.rule_version))
            if (
                member is None
                or item.governance_provenance.envelope_sha256 != member.envelope_sha256
            ):
                raise InterpretationEvidenceBuildError(
                    "interpretation evidence item is not admitted to the active production release"
                )
            provenance = item.governance_provenance
            if (
                provenance.manifest_id != manifest.manifest_id
                or provenance.manifest_version != manifest.manifest_version
                or provenance.manifest_content_sha256 != manifest.content_sha256()
            ):
                raise InterpretationEvidenceBuildError(
                    "interpretation evidence provenance does not match the active production "
                    "release"
                )

    @staticmethod
    def _project(items: tuple[EvidenceItem, ...]) -> tuple[InterpretationEvidenceItem, ...]:
        return tuple(
            InterpretationEvidenceItem.from_selected_item(item)
            for item in sorted(items, key=lambda item: (item.rule_id, item.rule_version))
        )
