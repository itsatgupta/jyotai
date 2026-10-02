"""Pure assembly of Task 10 context and governed evaluations into evidence."""

from collections.abc import Iterable, Mapping

from pydantic import JsonValue

from astrologer.application.context import DeterministicAstrologyContext
from astrologer.evidence.models import (
    EvidenceContextIdentity,
    EvidenceEvaluationSummary,
    EvidenceItem,
    EvidencePackage,
    ResolvedEvidenceFact,
)
from astrologer.knowledge.corpus import ProductionCorpusManifest
from astrologer.knowledge.evaluation import (
    FactEvaluationProvenance,
    GovernedEvaluationResult,
    canonical_sha256,
)
from astrologer.rules.models import EvaluationStatus


class EvidenceBuildError(ValueError):
    """Raised when supplied context, manifest, and evaluations are incompatible."""


class EvidenceBuilder:
    """Stateless evidence assembly; it never calculates or evaluates astrology rules."""

    def build(
        self,
        context: DeterministicAstrologyContext,
        manifest: ProductionCorpusManifest,
        evaluations: Iterable[GovernedEvaluationResult],
    ) -> EvidencePackage:
        """Return the complete, status-partitioned evidence package for one release."""
        supplied = tuple(evaluations)
        self._validate_evaluations(context, manifest, supplied)
        facts_by_id: dict[str, JsonValue] = {
            fact.fact_id: fact.value for fact in context.derived_facts.facts
        }
        items = tuple(self._item_from(result, facts_by_id) for result in supplied)
        ordered = tuple(sorted(items, key=lambda item: (item.rule_id, item.rule_version)))
        matched = tuple(item for item in ordered if item.evaluation_status is EvaluationStatus.TRUE)
        unmatched = tuple(
            item for item in ordered if item.evaluation_status is EvaluationStatus.FALSE
        )
        unknown = tuple(
            item for item in ordered if item.evaluation_status is EvaluationStatus.UNKNOWN
        )
        summary = EvidenceEvaluationSummary(
            total_evaluations=len(ordered),
            matched_count=len(matched),
            unmatched_count=len(unmatched),
            unknown_count=len(unknown),
        )
        identity = EvidenceContextIdentity(
            calculation_instant=context.calculation_instant,
            requested_as_of=context.requested_as_of,
            normalized_as_of_utc=context.normalized_as_of_utc,
            context_content_sha256=canonical_sha256(context),
            context_provenance=context.provenance,
        )
        provisional = EvidencePackage.model_construct(
            context_identity=identity,
            corpus_release=manifest,
            manifest_content_sha256=manifest.content_sha256(),
            matched_evidence=matched,
            unmatched_evaluations=unmatched,
            unknown_evaluations=unknown,
            evaluation_summary=summary,
            package_content_sha256="0" * 64,
        )
        content_sha256 = provisional.content_sha256()
        return EvidencePackage(
            context_identity=identity,
            corpus_release=manifest,
            manifest_content_sha256=manifest.content_sha256(),
            matched_evidence=matched,
            unmatched_evaluations=unmatched,
            unknown_evaluations=unknown,
            evaluation_summary=summary,
            package_content_sha256=content_sha256,
        )

    @staticmethod
    def _validate_evaluations(
        context: DeterministicAstrologyContext,
        manifest: ProductionCorpusManifest,
        evaluations: tuple[GovernedEvaluationResult, ...],
    ) -> None:
        manifest_hash = manifest.content_sha256()
        manifest_members = {(rule.rule_id, rule.rule_version): rule for rule in manifest.rules}
        result_keys = tuple(
            (result.evaluation.rule_id, result.evaluation.rule_version) for result in evaluations
        )
        if len(result_keys) != len(set(result_keys)):
            raise EvidenceBuildError("governed evaluation rule revisions must be unique")
        if set(result_keys) != set(manifest_members):
            raise EvidenceBuildError("governed evaluation membership must exactly match manifest")
        expected_fact_provenance = FactEvaluationProvenance.from_derived_fact_bundle(
            context.derived_facts
        )
        for result in evaluations:
            evaluation = result.evaluation
            provenance = result.governance_provenance
            key = (evaluation.rule_id, evaluation.rule_version)
            member = manifest_members[key]
            if (provenance.rule_id, provenance.rule_version) != key:
                raise EvidenceBuildError(
                    "governed provenance rule identity does not match evaluation"
                )
            if provenance.envelope_sha256 != member.envelope_sha256:
                raise EvidenceBuildError(
                    "governed provenance envelope hash does not match manifest"
                )
            if (
                provenance.manifest_id != manifest.manifest_id
                or provenance.manifest_version != manifest.manifest_version
                or provenance.manifest_content_sha256 != manifest_hash
            ):
                raise EvidenceBuildError(
                    "governed provenance manifest identity does not match manifest"
                )
            fact_provenance = result.fact_provenance
            if (
                fact_provenance.methodology_id != expected_fact_provenance.methodology_id
                or fact_provenance.source_register_version
                != expected_fact_provenance.source_register_version
                or fact_provenance.derived_fact_provenance_sha256
                != expected_fact_provenance.derived_fact_provenance_sha256
            ):
                raise EvidenceBuildError(
                    "governed fact provenance does not match deterministic context"
                )

    @staticmethod
    def _item_from(
        result: GovernedEvaluationResult, facts_by_id: Mapping[str, JsonValue]
    ) -> EvidenceItem:
        evaluation = result.evaluation
        resolved_ids = evaluation.resolved_fact_ids
        missing_values = tuple(fact_id for fact_id in resolved_ids if fact_id not in facts_by_id)
        if missing_values:
            raise EvidenceBuildError("resolved governed fact is absent from deterministic context")
        resolved = tuple(
            ResolvedEvidenceFact(fact_id=fact_id, value=facts_by_id[fact_id])
            for fact_id in resolved_ids
        )
        resolved_id_set = set(resolved_ids)
        unresolved = tuple(
            fact_id for fact_id in evaluation.referenced_fact_ids if fact_id not in resolved_id_set
        )
        provenance = result.governance_provenance
        return EvidenceItem(
            evidence_item_id=f"{evaluation.rule_id}@{evaluation.rule_version}",
            evaluation_status=evaluation.status,
            evidence_direction=result.evidence_direction,
            rule_id=evaluation.rule_id,
            rule_version=evaluation.rule_version,
            effect_key=evaluation.effect.effect_key,
            domain=provenance.domain,
            taxonomy=provenance.taxonomy,
            posture=provenance.posture,
            chart_scope=provenance.chart_scope,
            referenced_fact_ids=evaluation.referenced_fact_ids,
            resolved_facts=resolved,
            unresolved_fact_ids=unresolved,
            condition_trace=evaluation.condition,
            governance_provenance=provenance,
            fact_provenance=result.fact_provenance,
        )
