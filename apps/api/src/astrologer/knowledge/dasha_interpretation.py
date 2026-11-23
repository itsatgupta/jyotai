"""Review-gated Career Dasha-interpretation corpus.

Rules reach this corpus only through ``ProductionCorpusLoader`` (manifest allowlist, envelope
hash, and ``AdmissionValidator``).  The production release is deliberately EMPTY: no Dasha
interpretation doctrine is admitted yet, so the answer-plan slot stays empty in production.
The corpus is never filled from language-model output.
"""

from collections.abc import Iterable
from typing import Final

from astrologer.astrology.dasha_linkage import (
    DASHA_LINKAGE_METHODOLOGY_ID,
    LORD_FACT_NAMES,
    SEGMENT_FACT_PREFIX,
    DashaPairLinkage,
    to_segment_fact_set,
)
from astrologer.composition.models import DashaInterpretationClaim, DashaInterpretationSlot
from astrologer.knowledge.corpus import (
    ProductionCorpusLoader,
    ProductionCorpusLoadError,
    ProductionCorpusManifest,
)
from astrologer.knowledge.models import (
    ChartScope,
    FactContract,
    JyotishDomain,
    ProductionRuleEnvelope,
    SourceRegistry,
)
from astrologer.rules.evaluator import RuleEvaluator
from astrologer.rules.models import EvaluationStatus, RuleDefinition

DASHA_INTERPRETATION_FACT_CONTRACT: Final = FactContract(
    contract_id="jyotish.dasha_linkage.segment",
    contract_version="v1",
    chart_scope=ChartScope.D1_RASHI,
    methodology_id=DASHA_LINKAGE_METHODOLOGY_ID,
    available_fact_ids=(
        f"{SEGMENT_FACT_PREFIX}.mahadasha.lord",
        f"{SEGMENT_FACT_PREFIX}.antardasha.lord",
        *(
            f"{SEGMENT_FACT_PREFIX}.{role}.{name}"
            for role in ("mahadasha", "antardasha")
            for name in LORD_FACT_NAMES
        ),
        f"{SEGMENT_FACT_PREFIX}.ad_house_from_md",
    ),
)
EMPTY_DASHA_INTERPRETATION_REGISTRY: Final = SourceRegistry(
    registry_version="jyotish-dasha-interpretation-registry-v1"
)
EMPTY_DASHA_INTERPRETATION_MANIFEST: Final = ProductionCorpusManifest(
    manifest_id="jyotish.dasha_interpretation.career",
    manifest_version="v1",
    registry_version=EMPTY_DASHA_INTERPRETATION_REGISTRY.registry_version,
    fact_contract_id=DASHA_INTERPRETATION_FACT_CONTRACT.contract_id,
    fact_contract_version=DASHA_INTERPRETATION_FACT_CONTRACT.contract_version,
)

_ADMISSION_TOKEN: Final = object()


class _AdmittedRule:
    __slots__ = ("permitted_wording", "rule", "source_locator")

    def __init__(self, rule: RuleDefinition, source_locator: str, permitted_wording: str) -> None:
        self.rule = rule
        self.source_locator = source_locator
        self.permitted_wording = permitted_wording


class DashaInterpretationCorpus:
    """Admitted rules only; construct through ``admit_dasha_interpretation_corpus``."""

    def __init__(
        self,
        *,
        token: object,
        manifest: ProductionCorpusManifest,
        rules: tuple[_AdmittedRule, ...],
    ) -> None:
        if token is not _ADMISSION_TOKEN:
            raise TypeError("Dasha interpretation corpora are created only by admission")
        self._manifest = manifest
        self._rules = rules
        self._evaluator = RuleEvaluator()

    @property
    def rule_keys(self) -> tuple[tuple[str, str], ...]:
        return tuple((item.rule.rule_id, item.rule.rule_version) for item in self._rules)

    def empty_slot(self) -> DashaInterpretationSlot:
        return DashaInterpretationSlot(
            corpus_manifest_id=self._manifest.manifest_id,
            corpus_manifest_version=self._manifest.manifest_version,
        )

    def evaluate(self, segments: Iterable[tuple[str, DashaPairLinkage]]) -> DashaInterpretationSlot:
        """Fill the slot with admitted rules whose condition is TRUE for a segment."""
        claims: list[DashaInterpretationClaim] = []
        for segment_id, pair in segments:
            facts = to_segment_fact_set(pair)
            for item in self._rules:
                result = self._evaluator.evaluate_rule(item.rule, facts)
                if result.status is not EvaluationStatus.TRUE:
                    continue
                claims.append(
                    DashaInterpretationClaim(
                        rule_id=item.rule.rule_id,
                        rule_version=item.rule.rule_version,
                        source_locator=item.source_locator,
                        permitted_wording=item.permitted_wording,
                        segment_id=segment_id,
                        mahadasha_lord=pair.mahadasha.lord.value,
                        antardasha_lord=pair.antardasha.lord.value,
                        matched_fact_ids=result.resolved_fact_ids,
                    )
                )
        return self.empty_slot().model_copy(update={"claims": tuple(claims)})


def admit_dasha_interpretation_corpus(
    manifest: ProductionCorpusManifest,
    definitions: Iterable[ProductionRuleEnvelope],
    registry: SourceRegistry,
) -> DashaInterpretationCorpus:
    """Admit Career Dasha rules through the shared production admission path."""
    envelopes = tuple(definitions)
    admitted = ProductionCorpusLoader().load(
        manifest, envelopes, registry, DASHA_INTERPRETATION_FACT_CONTRACT
    )
    by_key = {(item.rule.rule_id, item.rule.rule_version): item for item in envelopes}
    rules: list[_AdmittedRule] = []
    for rule in admitted:
        envelope = by_key[(rule.rule_id, rule.rule_version)]
        if envelope.domain is not JyotishDomain.CAREER:
            raise ProductionCorpusLoadError("Dasha interpretation corpus admits Career rules only")
        interpretation = next(
            item
            for item in registry.interpretations
            if item.interpretation_id == envelope.interpretation_id
        )
        passage = next(
            item for item in registry.passages if item.passage_id == interpretation.passage_id
        )
        source = next(item for item in registry.sources if item.source_id == passage.source_id)
        rules.append(
            _AdmittedRule(
                rule=rule,
                source_locator=f"{source.title}, {passage.locator}",
                permitted_wording=interpretation.statement,
            )
        )
    return DashaInterpretationCorpus(token=_ADMISSION_TOKEN, manifest=manifest, rules=tuple(rules))


# Production: no Dasha interpretation rule is admitted.  Changing this requires a reviewed
# governance record (research/next_dasha_01_review/governance-record-template.md).
ACTIVE_DASHA_INTERPRETATION_CORPUS: Final = admit_dasha_interpretation_corpus(
    EMPTY_DASHA_INTERPRETATION_MANIFEST, (), EMPTY_DASHA_INTERPRETATION_REGISTRY
)
