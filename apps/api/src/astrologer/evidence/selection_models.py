"""Immutable contracts for deterministic, domain-scoped evidence selection."""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from astrologer.evidence.models import EvidenceItem
from astrologer.knowledge.evaluation import canonical_sha256
from astrologer.knowledge.models import EvidenceDirection, JyotishDomain, RulePosture
from astrologer.questions.models import QuestionIntent
from astrologer.rules.models import EvaluationStatus

_SHA256 = r"^[a-f0-9]{64}$"


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class DomainMatching(StrEnum):
    EXACT_ONLY = "exact_only"


class EvidenceExclusionReason(StrEnum):
    DOMAIN_MISMATCH = "domain_mismatch"


class EvidenceSelectionPolicy(_FrozenModel):
    """The explicit, versioned selection semantics used for one result."""

    policy_schema: Literal["jyotish-evidence-selection-policy"] = (
        "jyotish-evidence-selection-policy"
    )
    policy_version: Literal["v1"] = "v1"
    policy_id: Literal["exact-domain-selection"] = "exact-domain-selection"
    domain_matching: Literal[DomainMatching.EXACT_ONLY] = DomainMatching.EXACT_ONLY
    include_relevant_unmatched: Literal[True] = True
    include_relevant_unknown: Literal[True] = True
    include_general_context_for_other_domains: Literal[False] = False


EXACT_DOMAIN_SELECTION_POLICY_V1 = EvidenceSelectionPolicy()


class ExcludedEvidenceReference(_FrozenModel):
    """Compact audit reference for an item ineligible for this atomic intent."""

    evidence_item_id: str
    rule_id: str
    rule_version: str
    evaluation_status: EvaluationStatus
    evidence_direction: EvidenceDirection
    domain: JyotishDomain
    posture: RulePosture
    exclusion_reason: Literal[EvidenceExclusionReason.DOMAIN_MISMATCH]

    @classmethod
    def from_item(cls, item: EvidenceItem) -> "ExcludedEvidenceReference":
        return cls(
            evidence_item_id=item.evidence_item_id,
            rule_id=item.rule_id,
            rule_version=item.rule_version,
            evaluation_status=item.evaluation_status,
            evidence_direction=item.evidence_direction,
            domain=item.domain,
            posture=item.posture,
            exclusion_reason=EvidenceExclusionReason.DOMAIN_MISMATCH,
        )


class SelectionCapabilitySummary(_FrozenModel):
    """Factual availability and unmet-posture flags, never astrological conclusions."""

    has_matched_evidence: bool
    has_supporting_match: bool
    has_challenging_match: bool
    has_contextual_match: bool
    timing_requested: bool
    has_static_match: bool
    has_timing_required_match: bool
    has_corroboration_required_match: bool
    timing_answerability_established: Literal[False] = False
    corroboration_handling_deferred: bool


class EvidenceSelectionResult(_FrozenModel):
    """Hashable selection of already-built evidence for exactly one intent."""

    result_schema: Literal["jyotish-evidence-selection-result"] = (
        "jyotish-evidence-selection-result"
    )
    result_version: Literal["v1"] = "v1"
    selector_version: Literal["evidence-selector-v1"] = "evidence-selector-v1"
    policy: EvidenceSelectionPolicy
    question_intent: QuestionIntent
    evidence_package_content_sha256: str = Field(pattern=_SHA256)
    manifest_id: str
    manifest_version: str
    manifest_content_sha256: str = Field(pattern=_SHA256)
    selected_matched: tuple[EvidenceItem, ...] = ()
    relevant_unmatched: tuple[EvidenceItem, ...] = ()
    relevant_unknown: tuple[EvidenceItem, ...] = ()
    excluded: tuple[ExcludedEvidenceReference, ...] = ()
    capability_summary: SelectionCapabilitySummary
    selection_content_sha256: str = Field(pattern=_SHA256)

    @model_validator(mode="after")
    def collections_must_be_ordered_disjoint_and_hashable(self) -> "EvidenceSelectionResult":
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
                    "relevant evidence items must use deterministic rule ID/version order"
                )
            if any(item.evaluation_status is not status for item in items):
                raise ValueError("relevant evidence item is in the wrong status collection")
            keys.extend(item_keys)
        excluded_keys = tuple((item.rule_id, item.rule_version) for item in self.excluded)
        if excluded_keys != tuple(sorted(excluded_keys)):
            raise ValueError("excluded evidence must use deterministic rule ID/version order")
        if len(keys) + len(excluded_keys) != len(set(keys + list(excluded_keys))):
            raise ValueError("selection evidence rule revisions must be unique")
        if self.selection_content_sha256 != self.content_sha256():
            raise ValueError("evidence selection content hash is invalid")
        return self

    def content_sha256(self) -> str:
        """Hash all selection content except the self-referential result hash."""
        payload = self.model_dump(mode="json", exclude={"selection_content_sha256"})
        return canonical_sha256(payload)
