"""Reviewed Career Pack v1 and its cumulative immutable production release."""

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
from astrologer.knowledge.production import (
    FACT_ID as RULE_ONE_FACT_ID,
)
from astrologer.knowledge.production import (
    RULE_ENVELOPE as HISTORICAL_RULE_ONE_ENVELOPE,
)
from astrologer.knowledge.production import (
    SOURCE_REGISTRY as HISTORICAL_SOURCE_REGISTRY,
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
FACT_ID: Final = "jyotish.d1.house_lord.10.placement_house"
RULE_ONE_ENVELOPE: Final = HISTORICAL_RULE_ONE_ENVELOPE.model_copy(
    update={
        "fact_contract_version": "v2",
    }
)

FACT_CONTRACT: Final = FactContract(
    contract_id="jyotish.d1.structural.rule1",
    contract_version="v2",
    chart_scope=ChartScope.D1_RASHI,
    methodology_id="jyotish-derived-facts-v1",
    available_fact_ids=(FACT_ID, RULE_ONE_FACT_ID),
)


def _review(category: ReviewCategory, notes: str = _REVIEW_LIMITATION) -> ReviewRecord:
    return ReviewRecord(
        category=category,
        status=ReviewStatus.REVIEWED,
        reviewer=_REVIEWER,
        reviewed_at=_REVIEWED_AT,
        notes=notes,
    )


_CAREER_PASSAGES: Final = (
    (
        "bphs.bhavesha-phala.10th-lord.4-or-10",
        "73",
        "PDF p. 193",
        "knowledge, comfort, courage, devotion/worship, and dharmic and truth-oriented qualities",
    ),
    (
        "bphs.bhavesha-phala.10th-lord.5-or-11",
        "74",
        "PDF p. 193",
        "wealth, children, contentment, truthfulness, and comfort",
    ),
    (
        "bphs.bhavesha-phala.10th-lord.6-or-12",
        "75",
        "PDF p. 193",
        "enemy-related difficulty or affliction, cleverness, and lack of comfort",
    ),
    (
        "bphs.bhavesha-phala.10th-lord.9",
        "77",
        "PDF p. 194; running-page label approximately 196",
        (
            "support or protection of family, good companions or friends, maternal devotion, "
            "and worship"
        ),
    ),
)

_CAREER_USER_FACING_STATEMENTS: Final = {
    "bphs.bhavesha-phala.10th-lord.4-or-10": (
        "With the D1 tenth-house lord in the fourth or tenth house, this is contextual "
        "evidence for career matters. The text associates this placement with knowledge, "
        "comfort, courage, devotion or worship, and dharmic and truth-oriented qualities. "
        "These broader life themes do not by themselves establish a profession, promotion, "
        "income, or timing."
    ),
    "bphs.bhavesha-phala.10th-lord.5-or-11": (
        "With the D1 tenth-house lord in the fifth or eleventh house, this is contextual "
        "evidence for career matters. The text associates this placement with wealth, "
        "children, contentment, truthfulness, and comfort. These are broader life themes, "
        "not a specific career outcome; they do not by themselves establish a profession, "
        "promotion, income, or timing."
    ),
    "bphs.bhavesha-phala.10th-lord.6-or-12": (
        "With the D1 tenth-house lord in the sixth or twelfth house, this is contextual "
        "evidence for career matters. The text associates this placement with adversarial "
        "difficulty or affliction, cleverness, and less comfort. These broader life themes "
        "do not by themselves establish a profession, promotion, income, or timing."
    ),
    "bphs.bhavesha-phala.10th-lord.9": (
        "With the D1 tenth-house lord in the ninth house, this is contextual evidence for "
        "career matters. The text associates this placement with family support or protection, "
        "good companions or friends, maternal devotion, and worship. These are broader life "
        "themes, not a specific career outcome; they do not by themselves establish a "
        "profession, promotion, income, or timing."
    ),
}

_CAREER_INTERPRETATION_IDS_V1: Final = {
    passage_id: f"{passage_id}.interpretation"
    for passage_id, _verse, _page, _summary in _CAREER_PASSAGES
}
_CAREER_INTERPRETATION_IDS_V2: Final = {
    passage_id: f"{passage_id}.interpretation.v2"
    for passage_id, _verse, _page, _summary in _CAREER_PASSAGES
}


def _historical_statement(summary: str) -> str:
    return (
        "Within the selected Brihat Parashara Hora Shastra edition, this D1 tenth-house "
        "lord placement is associated with the compound outcome cluster described by the "
        f"adjacent Hindi rendering: {summary}. This is contextual natal evidence only; it "
        "does not guarantee that any outcome will manifest, nor assert timing, "
        "probability, magnitude, career success, profession, promotion, or a prediction."
    )


def _career_interpretations(
    *,
    interpretation_ids: dict[str, str],
    interpretation_version: str,
    statements: dict[str, str],
) -> tuple[ReviewedInterpretation, ...]:
    return tuple(
        ReviewedInterpretation(
            interpretation_id=interpretation_ids[passage_id],
            interpretation_version=interpretation_version,
            passage_id=passage_id,
            translation_id=f"{passage_id}.hindi-rendering",
            translation_applicability=TranslationApplicability.REQUIRED,
            statement=statements[passage_id],
            scope_notes=(
                "D1/Rashi only; static natal structural context. Compound outcome scope is "
                "retained. "
                "No scoring, polarity, aggregation, timing, D9/D10 interpretation, or modern "
                "career prediction."
            ),
            review=_review(ReviewCategory.INTERPRETATION_REVIEW),
        )
        for passage_id, _verse, _page, _summary in _CAREER_PASSAGES
    )


_CAREER_INTERPRETATIONS_V1: Final = _career_interpretations(
    interpretation_ids=_CAREER_INTERPRETATION_IDS_V1,
    interpretation_version="v1",
    statements={
        passage_id: _historical_statement(summary)
        for passage_id, _verse, _page, summary in _CAREER_PASSAGES
    },
)
_CAREER_INTERPRETATIONS_V2: Final = _career_interpretations(
    interpretation_ids=_CAREER_INTERPRETATION_IDS_V2,
    interpretation_version="v2",
    statements=_CAREER_USER_FACING_STATEMENTS,
)

HISTORICAL_SOURCE_REGISTRY_V2: Final = SourceRegistry(
    registry_version="jyotish-source-registry-v3",
    sources=HISTORICAL_SOURCE_REGISTRY.sources,
    passages=HISTORICAL_SOURCE_REGISTRY.passages
    + tuple(
        SourcePassage(
            passage_id=passage_id,
            source_id="bphs.selected-edition",
            locator=(f"भावेशफलाध्यायः, अथ कर्मेशभावफलम्, verse {verse}; {page}."),
            passage_reference=(
                "Selected-edition passage concerning the D1 tenth-house lord placement; "
                "the governed summary relies on the adjacent Hindi rendering."
            ),
            ambiguity_notes=(
                "No independent Sanskrit scholarly translation is claimed. The compound "
                "outcome cluster is retained in the reviewed interpretation."
            ),
            review=_review(ReviewCategory.SOURCE_VERIFICATION),
        )
        for passage_id, verse, page, _summary in _CAREER_PASSAGES
    ),
    translations=HISTORICAL_SOURCE_REGISTRY.translations
    + tuple(
        TranslationRecord(
            translation_id=f"{passage_id}.hindi-rendering",
            translation_version="v1",
            passage_id=passage_id,
            language="Hindi",
            text=(
                f"Adjacent Hindi rendering basis reviewed for verse {verse}; source wording is "
                "not reproduced in this reference-only registry."
            ),
            review=_review(
                ReviewCategory.TRANSLATION_VERIFICATION,
                "Internal project-owner review using the selected edition's adjacent Hindi "
                "rendering; not independent Sanskrit scholarly certification.",
            ),
        )
        for passage_id, verse, _page, _summary in _CAREER_PASSAGES
    ),
    interpretations=HISTORICAL_SOURCE_REGISTRY.interpretations + _CAREER_INTERPRETATIONS_V1,
)
SOURCE_REGISTRY: Final = HISTORICAL_SOURCE_REGISTRY_V2.model_copy(
    update={
        "registry_version": "jyotish-source-registry-v4",
        "interpretations": HISTORICAL_SOURCE_REGISTRY_V2.interpretations
        + _CAREER_INTERPRETATIONS_V2,
    }
)


def _career_rule(
    rule_id: str,
    name: str,
    operation: ConditionOperation,
    values: tuple[int, ...],
    *,
    interpretation_ids: dict[str, str],
) -> ProductionRuleEnvelope:
    condition = (
        ConditionDefinition(
            kind=ConditionKind.LEAF,
            operation=operation,
            fact_id=FACT_ID,
            expected_value=values[0],
        )
        if operation is ConditionOperation.EQUALS
        else ConditionDefinition(
            kind=ConditionKind.LEAF,
            operation=operation,
            fact_id=FACT_ID,
            expected_values=values,
        )
    )
    passage_id = {
        "bphs.d1.house_lord.10.in_4_or_10.v1": "bphs.bhavesha-phala.10th-lord.4-or-10",
        "bphs.d1.house_lord.10.in_5_or_11.v1": "bphs.bhavesha-phala.10th-lord.5-or-11",
        "bphs.d1.house_lord.10.in_6_or_12.v1": "bphs.bhavesha-phala.10th-lord.6-or-12",
        "bphs.d1.house_lord.10.equals_9.v1": "bphs.bhavesha-phala.10th-lord.9",
    }[rule_id]
    return ProductionRuleEnvelope(
        rule=RuleDefinition(
            rule_id=rule_id,
            rule_version="v1",
            ruleset_version="jyotish.production-rules-v2",
            name=name,
            domain="career",
            condition=condition,
            effect=RuleEffect(
                effect_key=f"{rule_id.removesuffix('.v1')}.contextual",
                label="Contextual natal evidence",
            ),
        ),
        lifecycle=RuleLifecycle.PRODUCTION_ACTIVE,
        domain=JyotishDomain.CAREER,
        taxonomy=RuleTaxonomy.NATAL_STRUCTURAL,
        posture=RulePosture.STATIC,
        evidence_direction=EvidenceDirection.CONTEXTUAL,
        chart_scope=ChartScope.D1_RASHI,
        fact_contract_id=FACT_CONTRACT.contract_id,
        fact_contract_version=FACT_CONTRACT.contract_version,
        fact_contract_methodology_id=FACT_CONTRACT.methodology_id,
        fact_dependencies=(FactDependency(fact_id=FACT_ID),),
        interpretation_id=interpretation_ids[passage_id],
        formalization_review=_review(ReviewCategory.FORMALIZATION_REVIEW),
    )


def _career_rule_envelopes(
    interpretation_ids: dict[str, str],
) -> tuple[ProductionRuleEnvelope, ...]:
    return (
        _career_rule(
            "bphs.d1.house_lord.10.in_4_or_10.v1",
            "D1 10th-house lord placement in fourth or tenth house",
            ConditionOperation.IN,
            (4, 10),
            interpretation_ids=interpretation_ids,
        ),
        _career_rule(
            "bphs.d1.house_lord.10.in_5_or_11.v1",
            "D1 10th-house lord placement in fifth or eleventh house",
            ConditionOperation.IN,
            (5, 11),
            interpretation_ids=interpretation_ids,
        ),
        _career_rule(
            "bphs.d1.house_lord.10.in_6_or_12.v1",
            "D1 10th-house lord placement in sixth or twelfth house",
            ConditionOperation.IN,
            (6, 12),
            interpretation_ids=interpretation_ids,
        ),
        _career_rule(
            "bphs.d1.house_lord.10.equals_9.v1",
            "D1 10th-house lord placement in ninth house",
            ConditionOperation.EQUALS,
            (9,),
            interpretation_ids=interpretation_ids,
        ),
    )


HISTORICAL_CAREER_RULE_ENVELOPES_V2: Final = _career_rule_envelopes(_CAREER_INTERPRETATION_IDS_V1)
CAREER_RULE_ENVELOPES: Final = _career_rule_envelopes(_CAREER_INTERPRETATION_IDS_V2)
HISTORICAL_PRODUCTION_ENVELOPES_V2: Final = (
    RULE_ONE_ENVELOPE,
) + HISTORICAL_CAREER_RULE_ENVELOPES_V2
PRODUCTION_ENVELOPES: Final = (RULE_ONE_ENVELOPE,) + CAREER_RULE_ENVELOPES
HISTORICAL_PRODUCTION_MANIFEST_V2: Final = ProductionCorpusManifest(
    manifest_id="jyotish.production.cumulative",
    manifest_version="v2",
    registry_version=HISTORICAL_SOURCE_REGISTRY_V2.registry_version,
    fact_contract_id=FACT_CONTRACT.contract_id,
    fact_contract_version=FACT_CONTRACT.contract_version,
    rules=tuple(
        ManifestRule(
            rule_id=item.rule.rule_id,
            rule_version=item.rule.rule_version,
            envelope_sha256=envelope_sha256(item),
        )
        for item in sorted(
            HISTORICAL_PRODUCTION_ENVELOPES_V2,
            key=lambda item: (item.rule.rule_id, item.rule.rule_version),
        )
    ),
)
HISTORICAL_PRODUCTION_RELEASE_V2: Final = ProductionRelease(
    release_id="jyotish.production.cumulative",
    release_version="v2",
    manifest=HISTORICAL_PRODUCTION_MANIFEST_V2,
    registry=HISTORICAL_SOURCE_REGISTRY_V2,
    fact_contract=FACT_CONTRACT,
    envelopes=HISTORICAL_PRODUCTION_ENVELOPES_V2,
)
PRODUCTION_MANIFEST: Final = ProductionCorpusManifest(
    manifest_id="jyotish.production.cumulative",
    manifest_version="v3",
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
    release_version="v3",
    manifest=PRODUCTION_MANIFEST,
    registry=SOURCE_REGISTRY,
    fact_contract=FACT_CONTRACT,
    envelopes=PRODUCTION_ENVELOPES,
)
