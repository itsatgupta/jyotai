"""Governed evaluation that preserves Task 09B provenance around Task 08 results."""

import hashlib
import json
from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict, Field

from astrologer.astrology.derived_facts import DerivedFactBundle
from astrologer.knowledge.corpus import (
    ProductionCorpusLoader,
    ProductionCorpusManifest,
    envelope_sha256,
)
from astrologer.knowledge.models import (
    ChartScope,
    EvidenceDirection,
    FactContract,
    ProductionRuleEnvelope,
    SourceRegistry,
)
from astrologer.rules.evaluator import RULE_FRAMEWORK_VERSION, RuleEvaluator
from astrologer.rules.models import FactSet, RuleEvaluationResult

_SHA256 = r"^[a-f0-9]{64}$"


class GovernedEvaluationError(ValueError):
    """Raised when governed evaluation inputs cannot form a reproducible result."""


class FactEvaluationProvenance(BaseModel):
    """Hashes and identifies the upstream Task 09A fact input without embedding it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    methodology_id: str = Field(min_length=1, max_length=128)
    source_register_version: str = Field(min_length=1, max_length=128)
    derived_fact_provenance_sha256: str = Field(pattern=_SHA256)
    fact_set_sha256: str = Field(pattern=_SHA256)

    @classmethod
    def from_derived_fact_bundle(cls, bundle: DerivedFactBundle) -> "FactEvaluationProvenance":
        """Create explicit bridge provenance from an immutable Task 09A bundle."""
        from astrologer.astrology.derived_facts import to_fact_set

        return cls(
            methodology_id=bundle.provenance.methodology.methodology_id,
            source_register_version=bundle.provenance.methodology.source_register_version,
            derived_fact_provenance_sha256=canonical_sha256(bundle.provenance),
            fact_set_sha256=fact_set_sha256(to_fact_set(bundle)),
        )


class GovernedEvaluationProvenance(BaseModel):
    """Compact references from an evaluated rule to immutable governance inputs."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rule_id: str
    rule_version: str
    envelope_sha256: str = Field(pattern=_SHA256)
    manifest_id: str
    manifest_version: str
    manifest_content_sha256: str = Field(pattern=_SHA256)
    registry_version: str
    source_id: str
    source_version: str
    passage_id: str
    translation_id: str | None = None
    translation_version: str | None = None
    interpretation_id: str
    interpretation_version: str
    fact_contract_id: str
    fact_contract_version: str
    methodology_id: str
    chart_scope: ChartScope
    governance_version: str
    framework_version: str


class GovernedEvaluationResult(BaseModel):
    """An immutable Task 08 result paired with its admitted governance provenance."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    evaluation: RuleEvaluationResult
    evidence_direction: EvidenceDirection
    governance_provenance: GovernedEvaluationProvenance
    fact_provenance: FactEvaluationProvenance


class GovernedRuleEvaluator:
    """Evaluate only admitted rules while retaining source and release provenance."""

    def __init__(
        self,
        corpus_loader: ProductionCorpusLoader | None = None,
        rule_evaluator: RuleEvaluator | None = None,
    ) -> None:
        self._corpus_loader = corpus_loader or ProductionCorpusLoader()
        self._rule_evaluator = rule_evaluator or RuleEvaluator()

    def evaluate(
        self,
        manifest: ProductionCorpusManifest,
        envelopes: Iterable[ProductionRuleEnvelope],
        registry: SourceRegistry,
        contract: FactContract,
        facts: FactSet,
        fact_provenance: FactEvaluationProvenance,
    ) -> tuple[GovernedEvaluationResult, ...]:
        """Validate, evaluate, and bind admitted rule results to their provenance."""
        supplied_envelopes = tuple(envelopes)
        admitted_rules = self._corpus_loader.load(manifest, supplied_envelopes, registry, contract)
        if fact_provenance.methodology_id != contract.methodology_id:
            raise GovernedEvaluationError(
                "fact provenance methodology is incompatible with contract"
            )
        if fact_provenance.fact_set_sha256 != fact_set_sha256(facts):
            raise GovernedEvaluationError("fact provenance hash does not match supplied FactSet")

        envelopes_by_key = {
            (envelope.rule.rule_id, envelope.rule.rule_version): envelope
            for envelope in supplied_envelopes
        }
        sources = {source.source_id: source for source in registry.sources}
        passages = {passage.passage_id: passage for passage in registry.passages}
        translations = {
            translation.translation_id: translation for translation in registry.translations
        }
        interpretations = {
            interpretation.interpretation_id: interpretation
            for interpretation in registry.interpretations
        }

        results: list[GovernedEvaluationResult] = []
        for evaluation in self._rule_evaluator.evaluate_rules(admitted_rules, facts):
            envelope = envelopes_by_key[(evaluation.rule_id, evaluation.rule_version)]
            interpretation = interpretations[envelope.interpretation_id]
            passage = passages[interpretation.passage_id]
            source = sources[passage.source_id]
            translation = (
                translations[interpretation.translation_id]
                if interpretation.translation_id is not None
                else None
            )
            results.append(
                GovernedEvaluationResult(
                    evaluation=evaluation,
                    evidence_direction=envelope.evidence_direction,
                    governance_provenance=GovernedEvaluationProvenance(
                        rule_id=evaluation.rule_id,
                        rule_version=evaluation.rule_version,
                        envelope_sha256=envelope_sha256(envelope),
                        manifest_id=manifest.manifest_id,
                        manifest_version=manifest.manifest_version,
                        manifest_content_sha256=manifest.content_sha256(),
                        registry_version=registry.registry_version,
                        source_id=source.source_id,
                        source_version=source.source_version,
                        passage_id=passage.passage_id,
                        translation_id=translation.translation_id if translation else None,
                        translation_version=(
                            translation.translation_version if translation else None
                        ),
                        interpretation_id=interpretation.interpretation_id,
                        interpretation_version=interpretation.interpretation_version,
                        fact_contract_id=contract.contract_id,
                        fact_contract_version=contract.contract_version,
                        methodology_id=contract.methodology_id,
                        chart_scope=envelope.chart_scope,
                        governance_version=envelope.governance_version,
                        framework_version=RULE_FRAMEWORK_VERSION,
                    ),
                    fact_provenance=fact_provenance,
                )
            )
        return tuple(results)


def fact_set_sha256(facts: FactSet) -> str:
    """Return a canonical hash for the exact ordered Task 08 fact input."""
    return canonical_sha256(facts)


def canonical_sha256(value: object) -> str:
    """Hash Pydantic/JSON-compatible data with stable canonical JSON serialization."""
    dumped = value.model_dump(mode="json") if isinstance(value, BaseModel) else value
    encoded = json.dumps(dumped, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(encoded).hexdigest()
