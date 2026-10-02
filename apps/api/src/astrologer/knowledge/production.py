"""The first reviewed, allowlisted JyotAI production rule release.

This module contains immutable reviewed data only. It adds no calculation,
interpretation logic, aggregation, or runtime loading behavior.
"""

from datetime import UTC, datetime
from typing import Final

from astrologer.knowledge.corpus import (
    ManifestRule,
    ProductionCorpusManifest,
    envelope_sha256,
)
from astrologer.knowledge.models import (
    ChartScope,
    EvidenceDirection,
    FactContract,
    FactDependency,
    JyotishDomain,
    ProductionRuleEnvelope,
    ReviewCategory,
    ReviewedInterpretation,
    ReviewRecord,
    ReviewStatus,
    RightsStatus,
    RuleLifecycle,
    RulePosture,
    RuleTaxonomy,
    SourceKind,
    SourcePassage,
    SourceRecord,
    SourceRegistry,
    TranslationApplicability,
    TranslationRecord,
)
from astrologer.rules.models import (
    ConditionDefinition,
    ConditionKind,
    ConditionOperation,
    RuleDefinition,
    RuleEffect,
)

_REVIEWED_AT: Final = datetime(2026, 10, 2, tzinfo=UTC)
_REVIEWER: Final = "JyotAI project-owner review"
_REVIEW_LIMITATION: Final = (
    "Internal project review of the selected edition; not independently certified by a "
    "Sanskrit or Jyotish expert."
)

RULE_ID: Final = "bphs.d1.house_lord.11.in_9_or_10.v1"
RULE_VERSION: Final = "v1"
FACT_ID: Final = "jyotish.d1.house_lord.11.placement_house"

SOURCE_REGISTRY: Final = SourceRegistry(
    registry_version="jyotish-source-registry-v2",
    sources=(
        SourceRecord(
            source_id="bphs.selected-edition",
            source_version="v1",
            kind=SourceKind.PRIMARY,
            title="Brihat Parashara Hora Shastra / Brihat Parashara Hora Shastram",
            original_language="Sanskrit",
            rights_status=RightsStatus.REFERENCE_ONLY,
            rights_notes=(
                "Conservative internal classification for the referenced modern edition; "
                "it asserts no redistribution rights or broader legal conclusion."
            ),
            review_notes=_REVIEW_LIMITATION,
        ),
    ),
    passages=(
        SourcePassage(
            passage_id="bphs.bhavesha-phala.11th-lord.9-or-10",
            source_id="bphs.selected-edition",
            locator=(
                "Bhavesha-phala section (भावेशफलाध्यायः), selected edition; source "
                "extraction associates the passage with verse numbering around 82/83."
            ),
            passage_reference=(
                "Selected-edition Bhavesha-phala passage concerning the 11th-house lord "
                "in the ninth or tenth house; verse numbering is ambiguous around 82/83."
            ),
            ambiguity_notes=(
                "The selected-edition source extraction associates this passage with verse "
                "numbering around 82/83. JyotAI does not normalize that ambiguity."
            ),
            review=ReviewRecord(
                category=ReviewCategory.SOURCE_VERIFICATION,
                status=ReviewStatus.REVIEWED,
                reviewer=_REVIEWER,
                reviewed_at=_REVIEWED_AT,
                notes=_REVIEW_LIMITATION,
            ),
        ),
    ),
    translations=(
        TranslationRecord(
            translation_id="bphs.bhavesha-phala.11th-lord.9-or-10.hindi",
            translation_version="v1",
            passage_id="bphs.bhavesha-phala.11th-lord.9-or-10",
            language="Hindi",
            text=(
                "लाभेश दशम या नवम भाव मे हो तो जातक राजा से पूज्य, धनी, चतुर, "
                "सत्यवक्ता और अपने धर्म से युत होता है।"
            ),
            review=ReviewRecord(
                category=ReviewCategory.TRANSLATION_VERIFICATION,
                status=ReviewStatus.REVIEWED,
                reviewer=_REVIEWER,
                reviewed_at=_REVIEWED_AT,
                notes=(
                    "Internal project-owner verification against the selected edition's Hindi "
                    "rendering; not independent Sanskrit scholarly certification."
                ),
            ),
        ),
    ),
    interpretations=(
        ReviewedInterpretation(
            interpretation_id="bphs.bhavesha-phala.11th-lord.9-or-10.interpretation",
            interpretation_version="v1",
            passage_id="bphs.bhavesha-phala.11th-lord.9-or-10",
            translation_id="bphs.bhavesha-phala.11th-lord.9-or-10.hindi",
            translation_applicability=TranslationApplicability.REQUIRED,
            statement=(
                "Within the selected Brihat Parashara Hora Shastra edition, placement of the "
                "D1 11th-house lord in either the 9th or 10th house is associated with the "
                "favorable cluster of qualities/results stated in the cited passage. This rule "
                "records that textual association as contextual natal evidence only. It does "
                "not independently assert probability, timing, magnitude, certainty, or that "
                "every stated result must manifest."
            ),
            scope_notes=(
                "D1/Rashi only. Static natal structural association only. No Dasha timing. "
                "No transit timing. No D9/D10 interpretation. No scoring. No probability. "
                "No strength/magnitude claim. No claim that all listed classical outcomes "
                "necessarily manifest. No favorable/adverse aggregation. No prediction is "
                "generated from this rule alone."
            ),
            review=ReviewRecord(
                category=ReviewCategory.INTERPRETATION_REVIEW,
                status=ReviewStatus.REVIEWED,
                reviewer=_REVIEWER,
                reviewed_at=_REVIEWED_AT,
                notes=_REVIEW_LIMITATION,
            ),
        ),
    ),
)

FACT_CONTRACT: Final = FactContract(
    contract_id="jyotish.d1.structural.rule1",
    contract_version="v1",
    chart_scope=ChartScope.D1_RASHI,
    methodology_id="jyotish-derived-facts-v1",
    available_fact_ids=(FACT_ID,),
)

RULE_ENVELOPE: Final = ProductionRuleEnvelope(
    rule=RuleDefinition(
        rule_id=RULE_ID,
        rule_version=RULE_VERSION,
        ruleset_version="jyotish.production-rules-v1",
        name="D1 11th-house lord placement in ninth or tenth house",
        domain="general",
        condition=ConditionDefinition(
            kind=ConditionKind.LEAF,
            operation=ConditionOperation.IN,
            fact_id=FACT_ID,
            expected_values=(9, 10),
        ),
        effect=RuleEffect(
            effect_key="bphs.d1.house_lord.11.in_9_or_10.contextual",
            label="Contextual natal evidence",
        ),
    ),
    lifecycle=RuleLifecycle.PRODUCTION_ACTIVE,
    domain=JyotishDomain.GENERAL,
    taxonomy=RuleTaxonomy.NATAL_STRUCTURAL,
    posture=RulePosture.STATIC,
    evidence_direction=EvidenceDirection.CONTEXTUAL,
    chart_scope=ChartScope.D1_RASHI,
    fact_contract_id=FACT_CONTRACT.contract_id,
    fact_contract_version=FACT_CONTRACT.contract_version,
    fact_contract_methodology_id=FACT_CONTRACT.methodology_id,
    fact_dependencies=(FactDependency(fact_id=FACT_ID),),
    interpretation_id="bphs.bhavesha-phala.11th-lord.9-or-10.interpretation",
    formalization_review=ReviewRecord(
        category=ReviewCategory.FORMALIZATION_REVIEW,
        status=ReviewStatus.REVIEWED,
        reviewer=_REVIEWER,
        reviewed_at=_REVIEWED_AT,
        notes=_REVIEW_LIMITATION,
    ),
)

PRODUCTION_MANIFEST: Final = ProductionCorpusManifest(
    manifest_id="jyotish.production.rule1",
    manifest_version="v1",
    registry_version=SOURCE_REGISTRY.registry_version,
    fact_contract_id=FACT_CONTRACT.contract_id,
    fact_contract_version=FACT_CONTRACT.contract_version,
    rules=(
        ManifestRule(
            rule_id=RULE_ID,
            rule_version=RULE_VERSION,
            envelope_sha256=envelope_sha256(RULE_ENVELOPE),
        ),
    ),
)
