"""Reviewed Friends / Social Network Pack v1 and cumulative immutable release v10."""

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
    SourceRegistry,
    TranslationApplicability,
)
from astrologer.knowledge.travel_pack_v1 import ACTIVE_PRODUCTION_RELEASE as RELEASE_V9
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
FRIENDS_RULE_ID: Final = "bphs.d1.house_lord.10.equals_9.friends.v1"
FRIENDS_INTERPRETATION_ID: Final = "bphs.karmeshas-phala.10th-lord.9.friends.interpretation.v1"


def _review(category: ReviewCategory, notes: str = _REVIEW_LIMITATION) -> ReviewRecord:
    return ReviewRecord(
        category=category,
        status=ReviewStatus.REVIEWED,
        reviewer=_REVIEWER,
        reviewed_at=_REVIEWED_AT,
        notes=notes,
    )


# v5 already admits this D1 house-lord placement fact; this pack changes no fact vocabulary.
FACT_CONTRACT: Final = RELEASE_V9.fact_contract

_FRIENDS_INTERPRETATION: Final = ReviewedInterpretation(
    interpretation_id=FRIENDS_INTERPRETATION_ID,
    interpretation_version="v1",
    passage_id="bphs.bhavesha-phala.10th-lord.9",
    translation_id="bphs.bhavesha-phala.10th-lord.9.hindi-rendering",
    translation_applicability=TranslationApplicability.REQUIRED,
    statement=(
        "With the D1 tenth-house lord in the ninth house, this is contextual natal evidence "
        "related to friendships or supportive associations. The selected BPHS passage includes "
        "association with good companions or friends. It does not guarantee the number, "
        "loyalty, duration, or outcome of friendships, establish popularity or social standing, "
        "or provide timing."
    ),
    scope_notes=(
        "D1/Rashi only; static contextual natal evidence. No friend count, loyalty, betrayal, "
        "popularity, social standing, social-media influence, professional networking, timing, "
        "scoring, or certainty claim."
    ),
    review=_review(ReviewCategory.INTERPRETATION_REVIEW),
)

# The passage and translation are shared provenance only; this interpretation is a new identity.
SOURCE_REGISTRY: Final = SourceRegistry(
    registry_version="jyotish-source-registry-v11",
    sources=RELEASE_V9.registry.sources,
    passages=RELEASE_V9.registry.passages,
    translations=RELEASE_V9.registry.translations,
    interpretations=RELEASE_V9.registry.interpretations + (_FRIENDS_INTERPRETATION,),
)

FRIENDS_RULE_ENVELOPE: Final = ProductionRuleEnvelope(
    rule=RuleDefinition(
        rule_id=FRIENDS_RULE_ID,
        rule_version="v1",
        ruleset_version="jyotish.production-rules-v9",
        name="D1 10th-house lord placement in ninth house",
        domain="friends",
        condition=ConditionDefinition(
            kind=ConditionKind.LEAF,
            operation=ConditionOperation.EQUALS,
            fact_id=TENTH_LORD_FACT_ID,
            expected_value=9,
        ),
        effect=RuleEffect(
            effect_key="bphs.d1.house_lord.10.equals_9.friends.contextual",
            label="Contextual natal evidence",
        ),
    ),
    lifecycle=RuleLifecycle.PRODUCTION_ACTIVE,
    domain=JyotishDomain.FRIENDS,
    taxonomy=RuleTaxonomy.NATAL_STRUCTURAL,
    posture=RulePosture.STATIC,
    evidence_direction=EvidenceDirection.CONTEXTUAL,
    chart_scope=ChartScope.D1_RASHI,
    fact_contract_id=FACT_CONTRACT.contract_id,
    fact_contract_version=FACT_CONTRACT.contract_version,
    fact_contract_methodology_id=FACT_CONTRACT.methodology_id,
    fact_dependencies=(FactDependency(fact_id=TENTH_LORD_FACT_ID),),
    interpretation_id=FRIENDS_INTERPRETATION_ID,
    formalization_review=_review(ReviewCategory.FORMALIZATION_REVIEW),
)

# v9 objects are copied only for v10 admission; v9 itself remains immutable.
HISTORICAL_V9_ENVELOPES: Final = tuple(RELEASE_V9.envelopes)
PRODUCTION_ENVELOPES: Final = HISTORICAL_V9_ENVELOPES + (FRIENDS_RULE_ENVELOPE,)
PRODUCTION_MANIFEST: Final = ProductionCorpusManifest(
    manifest_id="jyotish.production.cumulative",
    manifest_version="v10",
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
    release_version="v10",
    manifest=PRODUCTION_MANIFEST,
    registry=SOURCE_REGISTRY,
    fact_contract=FACT_CONTRACT,
    envelopes=PRODUCTION_ENVELOPES,
)
