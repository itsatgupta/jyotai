"""Reviewed Spirituality / Dharma Pack v1 and cumulative immutable release v8."""

from datetime import UTC, datetime
from typing import Final

from astrologer.knowledge.children_pack_v1 import ACTIVE_PRODUCTION_RELEASE as RELEASE_V7
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

TENTH_LORD_FACT_ID: Final = "jyotish.d1.house_lord.10.placement_house"
ELEVENTH_LORD_FACT_ID: Final = "jyotish.d1.house_lord.11.placement_house"

SPIRITUALITY_RULE_IDS: Final = (
    "bphs.d1.house_lord.10.in_4_or_10.spirituality.v1",
    "bphs.d1.house_lord.10.equals_9.spirituality.v1",
    "bphs.d1.house_lord.11.in_2_or_5.spirituality.v1",
    "bphs.d1.house_lord.11.in_9_or_10.spirituality.v1",
)
SPIRITUALITY_INTERPRETATION_IDS: Final = (
    "bphs.karmeshas-phala.10th-lord.4-or-10.spirituality.interpretation.v1",
    "bphs.karmeshas-phala.10th-lord.9.spirituality.interpretation.v1",
    "bphs.labhesha-phala.11th-lord.2-or-5.spirituality.interpretation.v1",
    "bphs.labhesha-phala.11th-lord.9-or-10.spirituality.interpretation.v1",
)


def _review(category: ReviewCategory, notes: str = _REVIEW_LIMITATION) -> ReviewRecord:
    return ReviewRecord(
        category=category,
        status=ReviewStatus.REVIEWED,
        reviewer=_REVIEWER,
        reviewed_at=_REVIEWED_AT,
        notes=notes,
    )


# v5 already admits both D1 house-lord placement facts; this pack changes no fact vocabulary.
FACT_CONTRACT: Final = RELEASE_V7.fact_contract

_SPIRITUALITY_INTERPRETATIONS: Final = (
    ReviewedInterpretation(
        interpretation_id=SPIRITUALITY_INTERPRETATION_IDS[0],
        interpretation_version="v1",
        passage_id="bphs.bhavesha-phala.10th-lord.4-or-10",
        translation_id="bphs.bhavesha-phala.10th-lord.4-or-10.hindi-rendering",
        translation_applicability=TranslationApplicability.REQUIRED,
        statement=(
            "This is contextual natal evidence for dharmic or devotional orientation. The "
            "selected BPHS passage associates the D1 tenth-house lord in the fourth or tenth "
            "house with worship and dharmic, truth-oriented conduct. It does not establish "
            "religious identity, moral standing, timing, or certainty."
        ),
        scope_notes=(
            "D1/Rashi only; static contextual natal evidence. No religious identity, moral "
            "ranking, moksha, supernatural attainment, timing, scoring, or prediction claim."
        ),
        review=_review(ReviewCategory.INTERPRETATION_REVIEW),
    ),
    ReviewedInterpretation(
        interpretation_id=SPIRITUALITY_INTERPRETATION_IDS[1],
        interpretation_version="v1",
        passage_id="bphs.bhavesha-phala.10th-lord.9",
        translation_id="bphs.bhavesha-phala.10th-lord.9.hindi-rendering",
        translation_applicability=TranslationApplicability.REQUIRED,
        statement=(
            "This is contextual natal evidence for devotional or worship-oriented practice. "
            "The selected BPHS passage associates the D1 tenth-house lord in the ninth house "
            "with worship. It does not establish religious identity, family outcomes, timing, "
            "or certainty."
        ),
        scope_notes=(
            "D1/Rashi only; static contextual natal evidence. No religious identity, family "
            "outcomes, moral ranking, moksha, supernatural attainment, timing, scoring, or "
            "prediction claim."
        ),
        review=_review(ReviewCategory.INTERPRETATION_REVIEW),
    ),
    ReviewedInterpretation(
        interpretation_id=SPIRITUALITY_INTERPRETATION_IDS[2],
        interpretation_version="v1",
        passage_id="bphs.bhavesha-phala.11th-lord.2-or-5",
        translation_id="bphs.bhavesha-phala.11th-lord.2-or-5.hindi-rendering",
        translation_applicability=TranslationApplicability.REQUIRED,
        statement=(
            "This is contextual natal evidence for religious or dharmic orientation. The "
            "selected BPHS passage associates the D1 eleventh-house lord in the second or fifth "
            "house with being religious. It does not establish religious identity, children-"
            "related outcomes, comfort, timing, or certainty."
        ),
        scope_notes=(
            "D1/Rashi only; static contextual natal evidence. No religious identity, children "
            "outcomes, moral ranking, moksha, supernatural attainment, timing, scoring, or "
            "prediction claim."
        ),
        review=_review(ReviewCategory.INTERPRETATION_REVIEW),
    ),
    ReviewedInterpretation(
        interpretation_id=SPIRITUALITY_INTERPRETATION_IDS[3],
        interpretation_version="v1",
        passage_id="bphs.bhavesha-phala.11th-lord.9-or-10",
        translation_id="bphs.bhavesha-phala.11th-lord.9-or-10.hindi",
        translation_applicability=TranslationApplicability.REQUIRED,
        statement=(
            "This is contextual natal evidence for dharmic orientation. The selected BPHS "
            "passage associates the D1 eleventh-house lord in the ninth or tenth house with "
            "one’s own dharma and truthfulness. It does not establish moral superiority, wealth, "
            "status, timing, or certainty."
        ),
        scope_notes=(
            "D1/Rashi only; static contextual natal evidence. No religious identity, moral "
            "ranking, wealth, status, moksha, supernatural attainment, timing, scoring, or "
            "prediction claim. The source's verse numbering ambiguity around 82/83 is retained."
        ),
        review=_review(ReviewCategory.INTERPRETATION_REVIEW),
    ),
)

# Passages and translations are shared provenance only; these interpretations are new identities.
SOURCE_REGISTRY: Final = SourceRegistry(
    registry_version="jyotish-source-registry-v9",
    sources=RELEASE_V7.registry.sources,
    passages=RELEASE_V7.registry.passages,
    translations=RELEASE_V7.registry.translations,
    interpretations=RELEASE_V7.registry.interpretations + _SPIRITUALITY_INTERPRETATIONS,
)


def _spirituality_rule(
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
            ruleset_version="jyotish.production-rules-v7",
            name=name,
            domain="spirituality",
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
        domain=JyotishDomain.SPIRITUALITY,
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


SPIRITUALITY_RULE_ENVELOPES: Final = (
    _spirituality_rule(
        SPIRITUALITY_RULE_IDS[0],
        "D1 10th-house lord placement in fourth or tenth house",
        TENTH_LORD_FACT_ID,
        (4, 10),
        SPIRITUALITY_INTERPRETATION_IDS[0],
    ),
    _spirituality_rule(
        SPIRITUALITY_RULE_IDS[1],
        "D1 10th-house lord placement in ninth house",
        TENTH_LORD_FACT_ID,
        (9,),
        SPIRITUALITY_INTERPRETATION_IDS[1],
    ),
    _spirituality_rule(
        SPIRITUALITY_RULE_IDS[2],
        "D1 11th-house lord placement in second or fifth house",
        ELEVENTH_LORD_FACT_ID,
        (2, 5),
        SPIRITUALITY_INTERPRETATION_IDS[2],
    ),
    _spirituality_rule(
        SPIRITUALITY_RULE_IDS[3],
        "D1 11th-house lord placement in ninth or tenth house",
        ELEVENTH_LORD_FACT_ID,
        (9, 10),
        SPIRITUALITY_INTERPRETATION_IDS[3],
    ),
)

# v7 objects are copied only for v8 admission; v7 itself remains immutable.
HISTORICAL_V7_ENVELOPES: Final = tuple(
    item.model_copy(update={"fact_contract_version": FACT_CONTRACT.contract_version})
    for item in RELEASE_V7.envelopes
)
PRODUCTION_ENVELOPES: Final = HISTORICAL_V7_ENVELOPES + SPIRITUALITY_RULE_ENVELOPES
PRODUCTION_MANIFEST: Final = ProductionCorpusManifest(
    manifest_id="jyotish.production.cumulative",
    manifest_version="v8",
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
    release_version="v8",
    manifest=PRODUCTION_MANIFEST,
    registry=SOURCE_REGISTRY,
    fact_contract=FACT_CONTRACT,
    envelopes=PRODUCTION_ENVELOPES,
)
