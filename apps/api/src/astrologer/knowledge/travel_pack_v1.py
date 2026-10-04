"""Reviewed Travel / Foreign Residence Pack v1 and cumulative immutable release v9."""

from datetime import UTC, datetime
from typing import Final

from astrologer.knowledge.corpus import (
    ManifestRule,
    ProductionCorpusManifest,
    ProductionRelease,
    envelope_sha256,
)
from astrologer.knowledge.models import (
    ChartScope,
    EvidenceDirection,
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
from astrologer.knowledge.spirituality_pack_v1 import ACTIVE_PRODUCTION_RELEASE as RELEASE_V8
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
TRAVEL_RULE_ID: Final = "bphs.d1.house_lord.6.in_2_or_10.travel.v1"
TRAVEL_INTERPRETATION_ID: Final = "bphs.shashthesha-phala.6th-lord.2-or-10.travel.interpretation.v1"
_PASSAGE_ID: Final = "bphs.shashthesha-phala.6th-lord.2-or-10"
_TRANSLATION_ID: Final = "bphs.shashthesha-phala.6th-lord.2-or-10.hindi-rendering"


def _review(category: ReviewCategory, notes: str = _REVIEW_LIMITATION) -> ReviewRecord:
    return ReviewRecord(
        category=category,
        status=ReviewStatus.REVIEWED,
        reviewer=_REVIEWER,
        reviewed_at=_REVIEWED_AT,
        notes=notes,
    )


# v5 already admits this D1 house-lord placement fact; this pack changes no fact vocabulary.
FACT_CONTRACT: Final = RELEASE_V8.fact_contract

_TRAVEL_INTERPRETATION: Final = ReviewedInterpretation(
    interpretation_id=TRAVEL_INTERPRETATION_ID,
    interpretation_version="v1",
    passage_id=_PASSAGE_ID,
    translation_id=_TRANSLATION_ID,
    translation_applicability=TranslationApplicability.REQUIRED,
    statement=(
        "This is contextual natal evidence related to travel or residence away from the native "
        "place. In the selected BPHS passage, the D1 sixth-house lord in the second or tenth "
        "house is associated with being comfortable in a foreign place. It does not establish "
        "relocation timing, permanent foreign settlement, immigration status, visa or "
        "citizenship outcomes, or a specific destination."
    ),
    scope_notes=(
        "D1/Rashi only; static contextual natal evidence. No timing, permanent settlement, "
        "immigration, visa, citizenship, exact destination, scoring, or prediction claim."
    ),
    review=_review(ReviewCategory.INTERPRETATION_REVIEW),
)

SOURCE_REGISTRY: Final = SourceRegistry(
    registry_version="jyotish-source-registry-v10",
    sources=RELEASE_V8.registry.sources,
    passages=RELEASE_V8.registry.passages
    + (
        SourcePassage(
            passage_id=_PASSAGE_ID,
            source_id="bphs.selected-edition",
            locator="Bhavesha-phala / Shashthesha-phala v44; PDF p. 189",
            passage_reference=(
                "Selected-edition BPHS passage reviewed for the stated D1 house-lord placement."
            ),
            ambiguity_notes=(
                "The reviewed interpretation is scoped to the sole approved Travel candidate."
            ),
            review=_review(ReviewCategory.SOURCE_VERIFICATION),
        ),
    ),
    translations=RELEASE_V8.registry.translations
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
    interpretations=RELEASE_V8.registry.interpretations + (_TRAVEL_INTERPRETATION,),
)

TRAVEL_RULE_ENVELOPE: Final = ProductionRuleEnvelope(
    rule=RuleDefinition(
        rule_id=TRAVEL_RULE_ID,
        rule_version="v1",
        ruleset_version="jyotish.production-rules-v8",
        name="D1 6th-house lord placement in second or tenth house",
        domain="travel",
        condition=ConditionDefinition(
            kind=ConditionKind.LEAF,
            operation=ConditionOperation.IN,
            fact_id=SIXTH_LORD_FACT_ID,
            expected_values=(2, 10),
        ),
        effect=RuleEffect(
            effect_key="bphs.d1.house_lord.6.in_2_or_10.travel.contextual",
            label="Contextual natal evidence",
        ),
    ),
    lifecycle=RuleLifecycle.PRODUCTION_ACTIVE,
    domain=JyotishDomain.TRAVEL,
    taxonomy=RuleTaxonomy.NATAL_STRUCTURAL,
    posture=RulePosture.STATIC,
    evidence_direction=EvidenceDirection.CONTEXTUAL,
    chart_scope=ChartScope.D1_RASHI,
    fact_contract_id=FACT_CONTRACT.contract_id,
    fact_contract_version=FACT_CONTRACT.contract_version,
    fact_contract_methodology_id=FACT_CONTRACT.methodology_id,
    fact_dependencies=(FactDependency(fact_id=SIXTH_LORD_FACT_ID),),
    interpretation_id=TRAVEL_INTERPRETATION_ID,
    formalization_review=_review(ReviewCategory.FORMALIZATION_REVIEW),
)

# v8 objects are copied only for v9 admission; v8 itself remains immutable.
HISTORICAL_V8_ENVELOPES: Final = tuple(RELEASE_V8.envelopes)
PRODUCTION_ENVELOPES: Final = HISTORICAL_V8_ENVELOPES + (TRAVEL_RULE_ENVELOPE,)
PRODUCTION_MANIFEST: Final = ProductionCorpusManifest(
    manifest_id="jyotish.production.cumulative",
    manifest_version="v9",
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
    release_version="v9",
    manifest=PRODUCTION_MANIFEST,
    registry=SOURCE_REGISTRY,
    fact_contract=FACT_CONTRACT,
    envelopes=PRODUCTION_ENVELOPES,
)
