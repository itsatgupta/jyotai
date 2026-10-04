"""Reviewed Wealth Pack v1 and cumulative immutable production release v4."""

from datetime import UTC, datetime
from typing import Final

from astrologer.knowledge.career_pack_v1 import ACTIVE_PRODUCTION_RELEASE as RELEASE_V3
from astrologer.knowledge.corpus import (
    ManifestRule,
    ProductionCorpusManifest,
    ProductionRelease,
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

_REVIEWED_AT: Final = datetime(2026, 10, 3, tzinfo=UTC)
_REVIEWER: Final = "JyotAI project-owner review"
_REVIEW_LIMITATION: Final = (
    "Internal project-owner review of the selected edition; not independently certified by a "
    "Sanskrit or Jyotish expert."
)
ELEVENTH_LORD_FACT_ID: Final = "jyotish.d1.house_lord.11.placement_house"
FIFTH_LORD_FACT_ID: Final = "jyotish.d1.house_lord.5.placement_house"
# Compatibility name for the existing Career Pack's tenth-lord fact; it is
# retained in this cumulative contract unchanged.
FACT_ID: Final = "jyotish.d1.house_lord.10.placement_house"


def _review(category: ReviewCategory, notes: str = _REVIEW_LIMITATION) -> ReviewRecord:
    return ReviewRecord(
        category=category,
        status=ReviewStatus.REVIEWED,
        reviewer=_REVIEWER,
        reviewed_at=_REVIEWED_AT,
        notes=notes,
    )


# This is a new contract, rather than a mutation of v2.  The underlying D1
# derivation already exposes this fact family and its missing-fact semantics.
FACT_CONTRACT: Final = FactContract(
    contract_id="jyotish.d1.structural.rule1",
    contract_version="v3",
    chart_scope=ChartScope.D1_RASHI,
    methodology_id="jyotish-derived-facts-v1",
    available_fact_ids=(
        FACT_ID,
        ELEVENTH_LORD_FACT_ID,
        FIFTH_LORD_FACT_ID,
    ),
)

_WEALTH_PASSAGES: Final = (
    (
        "bphs.bhavesha-phala.11th-lord.1",
        "Labhesha-phala verse 78; PDF p. 194",
        "bphs.bhavesha-phala.11th-lord.1.hindi-rendering",
        "With the D1 eleventh-house lord in the first house, the selected BPHS passage "
        "associates this placement with material prosperity. This is contextual natal evidence "
        "only; it does not establish the amount, timing, or certainty of financial outcomes.",
    ),
    (
        "bphs.bhavesha-phala.11th-lord.2-or-5",
        "Labhesha-phala verse 79; PDF p. 194",
        "bphs.bhavesha-phala.11th-lord.2-or-5.hindi-rendering",
        "With the D1 eleventh-house lord in the second or fifth house, the selected BPHS passage "
        "associates this placement with many comforts and broad material resources. This is "
        "contextual natal evidence only; it does not establish income, timing, or certainty.",
    ),
    (
        "bphs.bhavesha-phala.5th-lord.11",
        "Sutesha-phala verse 42; PDF p. 188",
        "bphs.sutesha-phala.5th-lord.11.hindi-rendering",
        "With the D1 fifth-house lord in the eleventh house, the selected BPHS passage associates "
        "this placement with being endowed with wealth. The passage also contains broader "
        "non-Wealth themes, which this Wealth interpretation does not assess. This is contextual "
        "natal evidence "
        "only; it does not establish amount, timing, certainty, or career outcomes.",
    ),
)
_SHARED_GENERAL_PASSAGE_ID: Final = "bphs.bhavesha-phala.11th-lord.9-or-10"
_SHARED_GENERAL_TRANSLATION_ID: Final = "bphs.bhavesha-phala.11th-lord.9-or-10.hindi"

_WEALTH_INTERPRETATIONS: Final = (
    ReviewedInterpretation(
        interpretation_id="bphs.bhavesha-phala.11th-lord.1.wealth.interpretation.v1",
        interpretation_version="v1",
        passage_id=_WEALTH_PASSAGES[0][0],
        translation_id=_WEALTH_PASSAGES[0][2],
        translation_applicability=TranslationApplicability.REQUIRED,
        statement=_WEALTH_PASSAGES[0][3],
        scope_notes=(
            "D1/Rashi only; static contextual natal evidence. No timing, scoring, health, "
            "or prediction."
        ),
        review=_review(ReviewCategory.INTERPRETATION_REVIEW),
    ),
    ReviewedInterpretation(
        interpretation_id="bphs.bhavesha-phala.11th-lord.2-or-5.wealth.interpretation.v1",
        interpretation_version="v1",
        passage_id=_WEALTH_PASSAGES[1][0],
        translation_id=_WEALTH_PASSAGES[1][2],
        translation_applicability=TranslationApplicability.REQUIRED,
        statement=_WEALTH_PASSAGES[1][3],
        scope_notes=(
            "D1/Rashi only; static contextual natal evidence. No timing, scoring, health, "
            "or prediction."
        ),
        review=_review(ReviewCategory.INTERPRETATION_REVIEW),
    ),
    ReviewedInterpretation(
        interpretation_id="bphs.bhavesha-phala.11th-lord.9-or-10.wealth.interpretation.v1",
        interpretation_version="v1",
        passage_id=_SHARED_GENERAL_PASSAGE_ID,
        translation_id=_SHARED_GENERAL_TRANSLATION_ID,
        translation_applicability=TranslationApplicability.REQUIRED,
        statement=(
            "With the D1 eleventh-house lord in the ninth or tenth house, the selected BPHS "
            "passage associates this placement with wealth. This is contextual natal evidence "
            "only; it does "
            "not establish income level, timing, or certainty."
        ),
        scope_notes=(
            "D1/Rashi only; static contextual natal evidence. No timing, scoring, health, "
            "or prediction."
        ),
        review=_review(ReviewCategory.INTERPRETATION_REVIEW),
    ),
    ReviewedInterpretation(
        interpretation_id="bphs.sutesha-phala.5th-lord.11.wealth.interpretation.v1",
        interpretation_version="v1",
        passage_id=_WEALTH_PASSAGES[2][0],
        translation_id=_WEALTH_PASSAGES[2][2],
        translation_applicability=TranslationApplicability.REQUIRED,
        statement=_WEALTH_PASSAGES[2][3],
        scope_notes=(
            "D1/Rashi only; static contextual natal evidence. No timing, scoring, health, "
            "or career assessment."
        ),
        review=_review(ReviewCategory.INTERPRETATION_REVIEW),
    ),
)

SOURCE_REGISTRY: Final = SourceRegistry(
    registry_version="jyotish-source-registry-v5",
    sources=RELEASE_V3.registry.sources,
    passages=RELEASE_V3.registry.passages
    + tuple(
        SourcePassage(
            passage_id=passage_id,
            source_id="bphs.selected-edition",
            locator=locator,
            passage_reference=(
                "Selected-edition BPHS passage reviewed for the stated D1 house-lord placement."
            ),
            ambiguity_notes=(
                "The reviewed interpretation is scoped to the approved Wealth candidate only."
            ),
            review=_review(ReviewCategory.SOURCE_VERIFICATION),
        )
        for passage_id, locator, _translation_id, _statement in _WEALTH_PASSAGES
    ),
    translations=RELEASE_V3.registry.translations
    + tuple(
        TranslationRecord(
            translation_id=translation_id,
            translation_version="v1",
            passage_id=passage_id,
            language="Hindi",
            text=(
                "Selected-edition adjacent Hindi rendering reviewed; source wording is not "
                "reproduced in this reference-only registry."
            ),
            review=_review(ReviewCategory.TRANSLATION_VERIFICATION),
        )
        for passage_id, _locator, translation_id, _statement in _WEALTH_PASSAGES
    ),
    interpretations=RELEASE_V3.registry.interpretations + _WEALTH_INTERPRETATIONS,
)


def _wealth_rule(
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
            ruleset_version="jyotish.production-rules-v3",
            name=name,
            domain="wealth",
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
        domain=JyotishDomain.WEALTH,
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


WEALTH_RULE_ENVELOPES: Final = (
    _wealth_rule(
        "bphs.d1.house_lord.11.in_1.wealth.v1",
        "D1 11th-house lord placement in first house",
        ELEVENTH_LORD_FACT_ID,
        (1,),
        _WEALTH_INTERPRETATIONS[0].interpretation_id,
    ),
    _wealth_rule(
        "bphs.d1.house_lord.11.in_2_or_5.wealth.v1",
        "D1 11th-house lord placement in second or fifth house",
        ELEVENTH_LORD_FACT_ID,
        (2, 5),
        _WEALTH_INTERPRETATIONS[1].interpretation_id,
    ),
    _wealth_rule(
        "bphs.d1.house_lord.11.in_9_or_10.wealth.v1",
        "D1 11th-house lord placement in ninth or tenth house",
        ELEVENTH_LORD_FACT_ID,
        (9, 10),
        _WEALTH_INTERPRETATIONS[2].interpretation_id,
    ),
    _wealth_rule(
        "bphs.d1.house_lord.5.in_11.wealth.v1",
        "D1 5th-house lord placement in eleventh house",
        FIFTH_LORD_FACT_ID,
        (11,),
        _WEALTH_INTERPRETATIONS[3].interpretation_id,
    ),
)

# v3 objects are copied only for v4 admission; their original v3 identities and
# hashes remain immutable in the historical release.
HISTORICAL_V3_ENVELOPES: Final = tuple(
    item.model_copy(update={"fact_contract_version": FACT_CONTRACT.contract_version})
    for item in RELEASE_V3.envelopes
)
PRODUCTION_ENVELOPES: Final = HISTORICAL_V3_ENVELOPES + WEALTH_RULE_ENVELOPES
PRODUCTION_MANIFEST: Final = ProductionCorpusManifest(
    manifest_id="jyotish.production.cumulative",
    manifest_version="v4",
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
    release_version="v4",
    manifest=PRODUCTION_MANIFEST,
    registry=SOURCE_REGISTRY,
    fact_contract=FACT_CONTRACT,
    envelopes=PRODUCTION_ENVELOPES,
)
