"""Reviewed Children / Progeny Pack v1 and cumulative immutable release v7."""

from datetime import UTC, datetime
from typing import Final

from astrologer.knowledge.business_pack_v1 import ACTIVE_PRODUCTION_RELEASE as RELEASE_V6
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
    SourceRegistry,
    TranslationApplicability,
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

FIFTH_LORD_FACT_ID: Final = "jyotish.d1.house_lord.5.placement_house"
TENTH_LORD_FACT_ID: Final = "jyotish.d1.house_lord.10.placement_house"
ELEVENTH_LORD_FACT_ID: Final = "jyotish.d1.house_lord.11.placement_house"

CHILDREN_RULE_IDS: Final = (
    "bphs.d1.house_lord.5.in_11.children.v1",
    "bphs.d1.house_lord.11.in_2_or_5.children.v1",
    "bphs.d1.house_lord.10.in_5_or_11.children.v1",
)
CHILDREN_INTERPRETATION_IDS: Final = (
    "bphs.sutesha-phala.5th-lord.11.children.interpretation.v1",
    "bphs.labhesha-phala.11th-lord.2-or-5.children.interpretation.v1",
    "bphs.karmeshas-phala.10th-lord.5-or-11.children.interpretation.v1",
)


def _review(category: ReviewCategory, notes: str = _REVIEW_LIMITATION) -> ReviewRecord:
    return ReviewRecord(
        category=category,
        status=ReviewStatus.REVIEWED,
        reviewer=_REVIEWER,
        reviewed_at=_REVIEWED_AT,
        notes=notes,
    )


# No fact vocabulary changes are needed: v5 already admits these D1 placement facts.
FACT_CONTRACT: Final = RELEASE_V6.fact_contract

_CHILDREN_INTERPRETATIONS: Final = (
    ReviewedInterpretation(
        interpretation_id=CHILDREN_INTERPRETATION_IDS[0],
        interpretation_version="v1",
        passage_id="bphs.bhavesha-phala.5th-lord.11",
        translation_id="bphs.sutesha-phala.5th-lord.11.hindi-rendering",
        translation_applicability=TranslationApplicability.REQUIRED,
        statement=(
            "With the D1 fifth-house lord in the eleventh house, this is contextual natal "
            "evidence related to children/progeny. The selected BPHS passage also associates "
            "the placement with scholarship, authorship, skill, and wealth. It does not "
            "guarantee children, establish their number, or provide timing."
        ),
        scope_notes=(
            "D1/Rashi only; static contextual natal evidence. No fertility, child count, "
            "gender, health, loss, reproductive, timing, scoring, or prediction claim."
        ),
        review=_review(ReviewCategory.INTERPRETATION_REVIEW),
    ),
    ReviewedInterpretation(
        interpretation_id=CHILDREN_INTERPRETATION_IDS[1],
        interpretation_version="v1",
        passage_id="bphs.bhavesha-phala.11th-lord.2-or-5",
        translation_id="bphs.bhavesha-phala.11th-lord.2-or-5.hindi-rendering",
        translation_applicability=TranslationApplicability.REQUIRED,
        statement=(
            "With the D1 eleventh-house lord in the second or fifth house, this is contextual "
            "natal evidence related to children/progeny. The selected BPHS passage also "
            "describes comforts, dharmic orientation, and broader attainments. It does not "
            "guarantee children or establish timing."
        ),
        scope_notes=(
            "D1/Rashi only; static contextual natal evidence. No fertility, child count, "
            "gender, health, loss, reproductive, timing, scoring, or prediction claim."
        ),
        review=_review(ReviewCategory.INTERPRETATION_REVIEW),
    ),
    ReviewedInterpretation(
        interpretation_id=CHILDREN_INTERPRETATION_IDS[2],
        interpretation_version="v1",
        passage_id="bphs.bhavesha-phala.10th-lord.5-or-11",
        translation_id="bphs.bhavesha-phala.10th-lord.5-or-11.hindi-rendering",
        translation_applicability=TranslationApplicability.REQUIRED,
        statement=(
            "With the D1 tenth-house lord in the fifth or eleventh house, this is contextual "
            "natal evidence related to children/progeny. The selected BPHS passage also "
            "includes wealth, contentment, truthfulness, and comfort. It does not guarantee "
            "children or establish timing."
        ),
        scope_notes=(
            "D1/Rashi only; static contextual natal evidence. No fertility, child count, "
            "gender, health, loss, reproductive, timing, scoring, or prediction claim."
        ),
        review=_review(ReviewCategory.INTERPRETATION_REVIEW),
    ),
)

# The passages and translations are provenance shared with existing domain-specific rules;
# interpretations below are new immutable Children identities.
SOURCE_REGISTRY: Final = SourceRegistry(
    registry_version="jyotish-source-registry-v8",
    sources=RELEASE_V6.registry.sources,
    passages=RELEASE_V6.registry.passages,
    translations=RELEASE_V6.registry.translations,
    interpretations=RELEASE_V6.registry.interpretations + _CHILDREN_INTERPRETATIONS,
)


def _children_rule(
    rule_id: str,
    name: str,
    fact_id: str,
    values: tuple[int, ...],
    interpretation_id: str,
) -> ProductionRuleEnvelope:
    return ProductionRuleEnvelope(
        rule=RuleDefinition(
            rule_id=rule_id,
            rule_version="v1",
            ruleset_version="jyotish.production-rules-v6",
            name=name,
            domain="children",
            condition=ConditionDefinition(
                kind=ConditionKind.LEAF,
                operation=ConditionOperation.EQUALS if len(values) == 1 else ConditionOperation.IN,
                fact_id=fact_id,
                **(
                    {"expected_value": values[0]}
                    if len(values) == 1
                    else {"expected_values": values}
                ),
            ),
            effect=RuleEffect(
                effect_key=f"{rule_id.removesuffix('.v1')}.contextual",
                label="Contextual natal evidence",
            ),
        ),
        lifecycle=RuleLifecycle.PRODUCTION_ACTIVE,
        domain=JyotishDomain.CHILDREN,
        taxonomy=RuleTaxonomy.NATAL_STRUCTURAL,
        posture=RulePosture.STATIC,
        evidence_direction=EvidenceDirection.CONTEXTUAL,
        chart_scope=ChartScope.D1_RASHI,
        fact_contract_id=FACT_CONTRACT.contract_id,
        fact_contract_version=FACT_CONTRACT.contract_version,
        fact_contract_methodology_id=FACT_CONTRACT.methodology_id,
        fact_dependencies=(FactDependency(fact_id=fact_id),),
        interpretation_id=interpretation_id,
        formalization_review=_review(ReviewCategory.FORMALIZATION_REVIEW),
    )


CHILDREN_RULE_ENVELOPES: Final = (
    _children_rule(
        CHILDREN_RULE_IDS[0],
        "D1 5th-house lord placement in eleventh house",
        FIFTH_LORD_FACT_ID,
        (11,),
        CHILDREN_INTERPRETATION_IDS[0],
    ),
    _children_rule(
        CHILDREN_RULE_IDS[1],
        "D1 11th-house lord placement in second or fifth house",
        ELEVENTH_LORD_FACT_ID,
        (2, 5),
        CHILDREN_INTERPRETATION_IDS[1],
    ),
    _children_rule(
        CHILDREN_RULE_IDS[2],
        "D1 10th-house lord placement in fifth or eleventh house",
        TENTH_LORD_FACT_ID,
        (5, 11),
        CHILDREN_INTERPRETATION_IDS[2],
    ),
)

# v6 objects are copied only for v7 admission; v6 itself remains immutable.
HISTORICAL_V6_ENVELOPES: Final = tuple(
    item.model_copy(update={"fact_contract_version": FACT_CONTRACT.contract_version})
    for item in RELEASE_V6.envelopes
)
PRODUCTION_ENVELOPES: Final = HISTORICAL_V6_ENVELOPES + CHILDREN_RULE_ENVELOPES
PRODUCTION_MANIFEST: Final = ProductionCorpusManifest(
    manifest_id="jyotish.production.cumulative",
    manifest_version="v7",
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
    release_version="v7",
    manifest=PRODUCTION_MANIFEST,
    registry=SOURCE_REGISTRY,
    fact_contract=FACT_CONTRACT,
    envelopes=PRODUCTION_ENVELOPES,
)
