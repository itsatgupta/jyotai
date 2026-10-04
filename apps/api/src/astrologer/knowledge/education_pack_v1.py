"""Reviewed Education Pack v1 and cumulative immutable production release v5."""

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
from astrologer.knowledge.wealth_pack_v1 import ACTIVE_PRODUCTION_RELEASE as RELEASE_V4
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
FOURTH_LORD_FACT_ID: Final = "jyotish.d1.house_lord.4.placement_house"
FIFTH_LORD_FACT_ID: Final = "jyotish.d1.house_lord.5.placement_house"
ELEVENTH_LORD_FACT_ID: Final = "jyotish.d1.house_lord.11.placement_house"
TENTH_LORD_FACT_ID: Final = "jyotish.d1.house_lord.10.placement_house"


def _review(category: ReviewCategory, notes: str = _REVIEW_LIMITATION) -> ReviewRecord:
    return ReviewRecord(
        category=category,
        status=ReviewStatus.REVIEWED,
        reviewer=_REVIEWER,
        reviewed_at=_REVIEWED_AT,
        notes=notes,
    )


# This is a new contract, rather than a mutation of v3. The existing D1
# derivation already exposes all house-lord placement facts and their missing-fact semantics.
FACT_CONTRACT: Final = FactContract(
    contract_id="jyotish.d1.structural.rule1",
    contract_version="v4",
    chart_scope=ChartScope.D1_RASHI,
    methodology_id="jyotish-derived-facts-v1",
    available_fact_ids=(
        TENTH_LORD_FACT_ID,
        ELEVENTH_LORD_FACT_ID,
        FIFTH_LORD_FACT_ID,
        FOURTH_LORD_FACT_ID,
    ),
)

_EDUCATION_PASSAGES: Final = (
    (
        "bphs.sukhesha-phala.4th-lord.1-or-7",
        "Sukhesha-phala verse 32; PDF p. 187",
        "bphs.sukhesha-phala.4th-lord.1-or-7.hindi-rendering",
    ),
    (
        "bphs.labhesha-phala.11th-lord.11",
        "Labhesha-phala verse 84; PDF p. 195",
        "bphs.labhesha-phala.11th-lord.11.hindi-rendering",
    ),
)
_SHARED_WEALTH_PASSAGE_ID: Final = "bphs.bhavesha-phala.5th-lord.11"
_SHARED_WEALTH_TRANSLATION_ID: Final = "bphs.sutesha-phala.5th-lord.11.hindi-rendering"

_EDUCATION_INTERPRETATIONS: Final = (
    ReviewedInterpretation(
        interpretation_id="bphs.sukhesha-phala.4th-lord.1-or-7.education.interpretation.v1",
        interpretation_version="v1",
        passage_id=_EDUCATION_PASSAGES[0][0],
        translation_id=_EDUCATION_PASSAGES[0][2],
        translation_applicability=TranslationApplicability.REQUIRED,
        statement=(
            "With the fourth-house lord in the first or seventh house, the chart is associated "
            "with breadth of learning and familiarity with multiple fields of knowledge. This "
            "is static natal context; it does not guarantee educational results or establish "
            "timing."
        ),
        scope_notes=(
            "D1/Rashi only; static contextual natal evidence. No timing, health, scoring, "
            "or prediction."
        ),
        review=_review(ReviewCategory.INTERPRETATION_REVIEW),
    ),
    ReviewedInterpretation(
        interpretation_id="bphs.sutesha-phala.5th-lord.11.education.interpretation.v1",
        interpretation_version="v1",
        passage_id=_SHARED_WEALTH_PASSAGE_ID,
        translation_id=_SHARED_WEALTH_TRANSLATION_ID,
        translation_applicability=TranslationApplicability.REQUIRED,
        statement=(
            "With the fifth-house lord in the eleventh house, the chart is associated with "
            "scholarship, authorship, and skill. This is static natal context; it does not "
            "guarantee educational outcomes or establish timing."
        ),
        scope_notes=(
            "D1/Rashi only; static contextual natal evidence. No timing, health, scoring, "
            "or prediction."
        ),
        review=_review(ReviewCategory.INTERPRETATION_REVIEW),
    ),
    ReviewedInterpretation(
        interpretation_id="bphs.labhesha-phala.11th-lord.11.education.interpretation.v1",
        interpretation_version="v1",
        passage_id=_EDUCATION_PASSAGES[1][0],
        translation_id=_EDUCATION_PASSAGES[1][2],
        translation_applicability=TranslationApplicability.REQUIRED,
        statement=(
            "With the eleventh-house lord in the eleventh house, the chart is associated with "
            "scholarship and poetic or literary expression. This is static natal context and "
            "does not establish timing, scores, exam results, or future academic achievement."
        ),
        scope_notes=(
            "D1/Rashi only; static contextual natal evidence. No timing, health, scoring, "
            "or prediction."
        ),
        review=_review(ReviewCategory.INTERPRETATION_REVIEW),
    ),
)

SOURCE_REGISTRY: Final = SourceRegistry(
    registry_version="jyotish-source-registry-v6",
    sources=RELEASE_V4.registry.sources,
    passages=RELEASE_V4.registry.passages
    + tuple(
        SourcePassage(
            passage_id=passage_id,
            source_id="bphs.selected-edition",
            locator=locator,
            passage_reference=(
                "Selected-edition BPHS passage reviewed for the stated D1 house-lord placement."
            ),
            ambiguity_notes=(
                "The reviewed interpretation is scoped to the approved Education candidate only."
            ),
            review=_review(ReviewCategory.SOURCE_VERIFICATION),
        )
        for passage_id, locator, _translation_id in _EDUCATION_PASSAGES
    ),
    translations=RELEASE_V4.registry.translations
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
        for passage_id, _locator, translation_id in _EDUCATION_PASSAGES
    ),
    interpretations=RELEASE_V4.registry.interpretations + _EDUCATION_INTERPRETATIONS,
)


def _education_rule(
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
            ruleset_version="jyotish.production-rules-v4",
            name=name,
            domain="education",
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
        domain=JyotishDomain.EDUCATION,
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


EDUCATION_RULE_ENVELOPES: Final = (
    _education_rule(
        "bphs.d1.house_lord.4.in_1_or_7.education.v1",
        "D1 4th-house lord placement in first or seventh house",
        FOURTH_LORD_FACT_ID,
        (1, 7),
        _EDUCATION_INTERPRETATIONS[0].interpretation_id,
    ),
    _education_rule(
        "bphs.d1.house_lord.5.in_11.education.v1",
        "D1 5th-house lord placement in eleventh house",
        FIFTH_LORD_FACT_ID,
        (11,),
        _EDUCATION_INTERPRETATIONS[1].interpretation_id,
    ),
    _education_rule(
        "bphs.d1.house_lord.11.in_11.education.v1",
        "D1 11th-house lord placement in eleventh house",
        ELEVENTH_LORD_FACT_ID,
        (11,),
        _EDUCATION_INTERPRETATIONS[2].interpretation_id,
    ),
)

# v4 objects are copied only for v5 admission; their original v4 identities and
# hashes remain immutable in the historical release.
HISTORICAL_V4_ENVELOPES: Final = tuple(
    item.model_copy(update={"fact_contract_version": FACT_CONTRACT.contract_version})
    for item in RELEASE_V4.envelopes
)
PRODUCTION_ENVELOPES: Final = HISTORICAL_V4_ENVELOPES + EDUCATION_RULE_ENVELOPES
PRODUCTION_MANIFEST: Final = ProductionCorpusManifest(
    manifest_id="jyotish.production.cumulative",
    manifest_version="v5",
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
    release_version="v5",
    manifest=PRODUCTION_MANIFEST,
    registry=SOURCE_REGISTRY,
    fact_contract=FACT_CONTRACT,
    envelopes=PRODUCTION_ENVELOPES,
)
