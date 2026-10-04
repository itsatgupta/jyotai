"""Reviewed Business Pack v1 and cumulative immutable production release v6."""

from datetime import UTC, datetime
from typing import Final

from astrologer.knowledge.corpus import (
    ManifestRule,
    ProductionCorpusManifest,
    ProductionRelease,
    envelope_sha256,
)
from astrologer.knowledge.education_pack_v1 import ACTIVE_PRODUCTION_RELEASE as RELEASE_V5
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
    RuleLifecycle,
    RulePosture,
    RuleTaxonomy,
    SourcePassage,
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

_REVIEWED_AT: Final = datetime(2026, 10, 4, tzinfo=UTC)
_REVIEWER: Final = "JyotAI project-owner review"
_REVIEW_LIMITATION: Final = (
    "Internal project-owner review of the selected edition; not independently certified by a "
    "Sanskrit or Jyotish expert."
)
SIXTH_LORD_FACT_ID: Final = "jyotish.d1.house_lord.6.placement_house"
BUSINESS_RULE_ID: Final = "bphs.d1.house_lord.6.in_9.business.v1"
BUSINESS_INTERPRETATION_ID: Final = "bphs.bhavesha-phala.6th-lord.9.business.interpretation.v1"
_PASSAGE_ID: Final = "bphs.bhavesha-phala.6th-lord.9"
_TRANSLATION_ID: Final = "bphs.bhavesha-phala.6th-lord.9.hindi-rendering"


def _review(category: ReviewCategory, notes: str = _REVIEW_LIMITATION) -> ReviewRecord:
    return ReviewRecord(
        category=category,
        status=ReviewStatus.REVIEWED,
        reviewer=_REVIEWER,
        reviewed_at=_REVIEWED_AT,
        notes=notes,
    )


# This is a new contract, rather than a mutation of v4. The existing D1
# derivation already exposes this house-lord placement and missing-fact semantics.
FACT_CONTRACT: Final = FactContract(
    contract_id="jyotish.d1.structural.rule1",
    contract_version="v5",
    chart_scope=ChartScope.D1_RASHI,
    methodology_id="jyotish-derived-facts-v1",
    available_fact_ids=RELEASE_V5.fact_contract.available_fact_ids + (SIXTH_LORD_FACT_ID,),
)

_BUSINESS_INTERPRETATION: Final = ReviewedInterpretation(
    interpretation_id=BUSINESS_INTERPRETATION_ID,
    interpretation_version="v1",
    passage_id=_PASSAGE_ID,
    translation_id=_TRANSLATION_ID,
    translation_applicability=TranslationApplicability.REQUIRED,
    statement=(
        "With the D1 sixth-house lord in the ninth house, this is contextual natal evidence for "
        "commercial activity. The selected BPHS rendering associates this placement with selling "
        "goods such as wood or stone and with trade. It does not establish business success, "
        "profit or loss, livelihood, self-employment, timing, or certainty."
    ),
    scope_notes=(
        "D1/Rashi only; static contextual natal evidence. No timing, success, profit, revenue, "
        "or prediction."
    ),
    review=_review(ReviewCategory.INTERPRETATION_REVIEW),
)

SOURCE_REGISTRY: Final = SourceRegistry(
    registry_version="jyotish-source-registry-v7",
    sources=RELEASE_V5.registry.sources,
    passages=RELEASE_V5.registry.passages
    + (
        SourcePassage(
            passage_id=_PASSAGE_ID,
            source_id="bphs.selected-edition",
            locator="Bhavesha-phala, verse 49; PDF p. 190",
            passage_reference=(
                "Selected-edition BPHS passage reviewed for the stated D1 house-lord placement."
            ),
            ambiguity_notes=(
                "The reviewed interpretation is scoped to the sole approved Business candidate."
            ),
            review=_review(ReviewCategory.SOURCE_VERIFICATION),
        ),
    ),
    translations=RELEASE_V5.registry.translations
    + (
        TranslationRecord(
            translation_id=_TRANSLATION_ID,
            translation_version="v1",
            passage_id=_PASSAGE_ID,
            language="Hindi",
            text=(
                "Selected-edition Hindi rendering reviewed; source wording is not reproduced in "
                "this reference-only registry."
            ),
            review=_review(ReviewCategory.TRANSLATION_VERIFICATION),
        ),
    ),
    interpretations=RELEASE_V5.registry.interpretations + (_BUSINESS_INTERPRETATION,),
)

BUSINESS_RULE_ENVELOPE: Final = ProductionRuleEnvelope(
    rule=RuleDefinition(
        rule_id=BUSINESS_RULE_ID,
        rule_version="v1",
        ruleset_version="jyotish.production-rules-v5",
        name="D1 6th-house lord placement in ninth house",
        domain="business",
        condition=ConditionDefinition(
            kind=ConditionKind.LEAF,
            operation=ConditionOperation.EQUALS,
            fact_id=SIXTH_LORD_FACT_ID,
            expected_value=9,
        ),
        effect=RuleEffect(
            effect_key="bphs.d1.house_lord.6.in_9.business.contextual",
            label="Contextual natal evidence",
        ),
    ),
    lifecycle=RuleLifecycle.PRODUCTION_ACTIVE,
    domain=JyotishDomain.BUSINESS,
    taxonomy=RuleTaxonomy.NATAL_STRUCTURAL,
    posture=RulePosture.STATIC,
    evidence_direction=EvidenceDirection.CONTEXTUAL,
    chart_scope=ChartScope.D1_RASHI,
    fact_contract_id=FACT_CONTRACT.contract_id,
    fact_contract_version=FACT_CONTRACT.contract_version,
    fact_contract_methodology_id=FACT_CONTRACT.methodology_id,
    fact_dependencies=(FactDependency(fact_id=SIXTH_LORD_FACT_ID),),
    interpretation_id=BUSINESS_INTERPRETATION_ID,
    formalization_review=_review(ReviewCategory.FORMALIZATION_REVIEW),
)

# v5 objects are copied only for v6 admission; their original v5 identities and
# hashes remain immutable in the historical release.
HISTORICAL_V5_ENVELOPES: Final = tuple(
    item.model_copy(update={"fact_contract_version": FACT_CONTRACT.contract_version})
    for item in RELEASE_V5.envelopes
)
PRODUCTION_ENVELOPES: Final = HISTORICAL_V5_ENVELOPES + (BUSINESS_RULE_ENVELOPE,)
PRODUCTION_MANIFEST: Final = ProductionCorpusManifest(
    manifest_id="jyotish.production.cumulative",
    manifest_version="v6",
    registry_version=SOURCE_REGISTRY.registry_version,
    fact_contract_id=FACT_CONTRACT.contract_id,
    fact_contract_version=FACT_CONTRACT.contract_version,
    rules=tuple(
        ManifestRule(
            rule_id=item.rule.rule_id,
            rule_version=item.rule.rule_version,
            envelope_sha256=envelope_sha256(item),
        )
        for item in sorted(
            PRODUCTION_ENVELOPES, key=lambda item: (item.rule.rule_id, item.rule.rule_version)
        )
    ),
)
ACTIVE_PRODUCTION_RELEASE: Final = ProductionRelease(
    release_id="jyotish.production.cumulative",
    release_version="v6",
    manifest=PRODUCTION_MANIFEST,
    registry=SOURCE_REGISTRY,
    fact_contract=FACT_CONTRACT,
    envelopes=PRODUCTION_ENVELOPES,
)
