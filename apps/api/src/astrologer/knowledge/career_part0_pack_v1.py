"""Review packet Part 0a: the 10th lord in houses 1, 2/3/7 and 8, cumulative release v11.

Admitted under a GENERAL expert approval (NEXT-ADMIT-01; governance records in
``docs/admissions/``).  The reviewer approved the packet "as proposed"; no item-level
readings, OCR issues or translations were individually addressed.  The notes on every review
record below say so and quote the statement verbatim.

v.76 (10th lord in the 8th) is admitted as a calculated match only.  Its reviewed statement
says that a reviewed indication exists and that its wording is withheld pending further
review; no verse content and no lifespan clause is reproduced anywhere in this module.
"""

from datetime import UTC, datetime
from typing import Final

from astrologer.knowledge.corpus import (
    ManifestRule,
    ProductionCorpusManifest,
    ProductionRelease,
    envelope_sha256,
)
from astrologer.knowledge.friends_pack_v1 import ACTIVE_PRODUCTION_RELEASE as RELEASE_V10
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
from astrologer.rules.models import (
    ConditionDefinition,
    ConditionKind,
    ConditionOperation,
    RuleDefinition,
    RuleEffect,
)

# The expert record, exactly as given by the project owner (NEXT-ADMIT-01).
EXPERT_REVIEWER: Final = "Pandit ji"
EXPERT_REVIEWED_AT: Final = datetime(2026, 11, 23, tzinfo=UTC)
EXPERT_STATEMENT: Final = (
    "All data points look good. The app is giving good calculation results. Mahadasha and "
    "Antardasha are both good, including their calculations and results. Proceed."
)
EXPERT_REVIEW_NOTES: Final = (
    "GENERAL approval, approved as proposed. Reviewer: Pandit ji (full name pending); "
    "qualification: Acharya; independence: not recorded. Channel: verbal, relayed by Atul, "
    f'2026-11-23. Statement (verbatim, as relayed): "{EXPERT_STATEMENT}" Reviewer has seen '
    "the review packet PDF (research/next_dasha_01_review/review-packet.md, Part 0). Approved "
    "as proposed; no item-level readings, OCR issues or translations individually addressed."
)

TENTH_LORD_FACT_ID: Final = "jyotish.d1.house_lord.10.placement_house"
RULE_IN_1: Final = "bphs.d1.house_lord.10.equals_1.v1"
RULE_IN_2_3_OR_7: Final = "bphs.d1.house_lord.10.in_2_3_or_7.v1"
RULE_IN_8: Final = "bphs.d1.house_lord.10.equals_8.v1"
# Rules whose reviewed statement withholds the text's wording (the glance says so).
WITHHELD_WORDING_RULE_IDS: Final = frozenset({RULE_IN_8})
WITHHELD_STATEMENT: Final = (
    "With the D1 tenth-house lord in the eighth house, a reviewed indication exists for this "
    "placement; its wording is withheld pending further review. This does not by itself "
    "establish a profession, promotion, income, or timing."
)

PASSAGE_IN_1: Final = "bphs.bhavesha-phala.10th-lord.1"
PASSAGE_IN_2_3_OR_7: Final = "bphs.bhavesha-phala.10th-lord.2-3-or-7"
PASSAGE_IN_8: Final = "bphs.bhavesha-phala.10th-lord.8"

_REVIEW_PACKET: Final = "research/next_dasha_01_review/review-packet.md"
_STATEMENTS: Final = {
    # Packet 0a-1 proposed user wording, verbatim (approved as proposed).
    PASSAGE_IN_1: (
        "With the D1 tenth-house lord in the first house, this is contextual evidence for "
        "career matters. The text associates this placement with poetic or literary ability, "
        "more comfort later in life, and wealth that grows over time. These broader life "
        "themes do not by themselves establish a profession, promotion, income, or timing."
    ),
    # Packet 0a-2 proposed user wording, verbatim (approved as proposed).
    PASSAGE_IN_2_3_OR_7: (
        "With the D1 tenth-house lord in the second, third or seventh house, this is "
        "contextual evidence for career matters. The text associates this placement with a "
        "high-minded, virtuous and articulate nature, and with truthfulness and dharma. These "
        "broader life themes do not by themselves establish a profession, promotion, income, "
        "or timing."
    ),
    # Packet 0a-3: calculated match only; wording withheld (owner decision, NEXT-ADMIT-01).
    PASSAGE_IN_8: WITHHELD_STATEMENT,
}
_PASSAGES: Final = (
    (PASSAGE_IN_1, "71", "0a-1"),
    (PASSAGE_IN_2_3_OR_7, "72", "0a-2"),
    (PASSAGE_IN_8, "76", "0a-3"),
)
_SCOPE_NOTES: Final = {
    PASSAGE_IN_1: (
        "D1/Rashi only; static contextual natal evidence. The childhood-illness clause of "
        "v.71 is left out of user wording (high-stakes health topic), as proposed. No scoring, "
        "polarity, timing, or career prediction."
    ),
    PASSAGE_IN_2_3_OR_7: (
        "D1/Rashi only; static contextual natal evidence. No scoring, polarity, timing, or "
        "career prediction."
    ),
    PASSAGE_IN_8: (
        "D1/Rashi only; calculated match only. The text's wording is withheld pending further "
        "review and is not shown. CONTEXTUAL pending X11 (polarity). No scoring, polarity, "
        "timing, or career prediction."
    ),
}


def _review(category: ReviewCategory) -> ReviewRecord:
    return ReviewRecord(
        category=category,
        status=ReviewStatus.REVIEWED,
        reviewer=EXPERT_REVIEWER,
        reviewed_at=EXPERT_REVIEWED_AT,
        notes=EXPERT_REVIEW_NOTES,
    )


FACT_CONTRACT: Final = RELEASE_V10.fact_contract

_NEW_PASSAGES: Final = tuple(
    SourcePassage(
        passage_id=passage_id,
        source_id="bphs.selected-edition",
        locator=f"भावेशफलाध्यायः, अथ कर्मेशभावफलम्, verse {verse}; PDF p. 193 (printed p. 195).",
        passage_reference=(
            f"Review packet {item} ({_REVIEW_PACKET}); D1 tenth-house lord placement."
        ),
        ambiguity_notes=(
            "OCR text and the preparer's probable reading are recorded in the review packet. "
            "The reviewer approved as proposed; readings were not individually addressed."
        ),
        review=_review(ReviewCategory.SOURCE_VERIFICATION),
    )
    for passage_id, verse, item in _PASSAGES
)
_NEW_TRANSLATIONS: Final = tuple(
    TranslationRecord(
        translation_id=f"{passage_id}.draft-translation",
        translation_version="v1",
        passage_id=passage_id,
        language="English",
        text=(
            f"Preparer's draft translation of verse {verse}, review packet {item}; approved as "
            "proposed under a general approval. Wording is not reproduced in this "
            "reference-only registry."
        ),
        review=_review(ReviewCategory.TRANSLATION_VERIFICATION),
    )
    for passage_id, verse, item in _PASSAGES
)
_NEW_INTERPRETATIONS: Final = tuple(
    ReviewedInterpretation(
        interpretation_id=f"{passage_id}.interpretation.v1",
        interpretation_version="v1",
        passage_id=passage_id,
        translation_id=f"{passage_id}.draft-translation",
        translation_applicability=TranslationApplicability.REQUIRED,
        statement=_STATEMENTS[passage_id],
        scope_notes=_SCOPE_NOTES[passage_id],
        review=_review(ReviewCategory.INTERPRETATION_REVIEW),
    )
    for passage_id, _verse, _item in _PASSAGES
)

SOURCE_REGISTRY: Final = SourceRegistry(
    registry_version="jyotish-source-registry-v12",
    sources=RELEASE_V10.registry.sources,
    passages=RELEASE_V10.registry.passages + _NEW_PASSAGES,
    translations=RELEASE_V10.registry.translations + _NEW_TRANSLATIONS,
    interpretations=RELEASE_V10.registry.interpretations + _NEW_INTERPRETATIONS,
)


def _rule(
    rule_id: str, name: str, values: tuple[int, ...], passage_id: str
) -> ProductionRuleEnvelope:
    condition = (
        ConditionDefinition(
            kind=ConditionKind.LEAF,
            operation=ConditionOperation.EQUALS,
            fact_id=TENTH_LORD_FACT_ID,
            expected_value=values[0],
        )
        if len(values) == 1
        else ConditionDefinition(
            kind=ConditionKind.LEAF,
            operation=ConditionOperation.IN,
            fact_id=TENTH_LORD_FACT_ID,
            expected_values=values,
        )
    )
    return ProductionRuleEnvelope(
        rule=RuleDefinition(
            rule_id=rule_id,
            rule_version="v1",
            ruleset_version="jyotish.production-rules-v10",
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
        fact_dependencies=(FactDependency(fact_id=TENTH_LORD_FACT_ID),),
        interpretation_id=f"{passage_id}.interpretation.v1",
        formalization_review=_review(ReviewCategory.FORMALIZATION_REVIEW),
    )


PART0_RULE_ENVELOPES: Final = (
    _rule(RULE_IN_1, "D1 10th-house lord placement in first house", (1,), PASSAGE_IN_1),
    _rule(
        RULE_IN_2_3_OR_7,
        "D1 10th-house lord placement in second, third or seventh house",
        (2, 3, 7),
        PASSAGE_IN_2_3_OR_7,
    ),
    _rule(RULE_IN_8, "D1 10th-house lord placement in eighth house", (8,), PASSAGE_IN_8),
)

# v10 objects are copied only for v11 admission; v10 itself remains immutable.
HISTORICAL_V10_ENVELOPES: Final = tuple(RELEASE_V10.envelopes)
PRODUCTION_ENVELOPES: Final = HISTORICAL_V10_ENVELOPES + PART0_RULE_ENVELOPES
PRODUCTION_MANIFEST: Final = ProductionCorpusManifest(
    manifest_id="jyotish.production.cumulative",
    manifest_version="v11",
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
    release_version="v11",
    manifest=PRODUCTION_MANIFEST,
    registry=SOURCE_REGISTRY,
    fact_contract=FACT_CONTRACT,
    envelopes=PRODUCTION_ENVELOPES,
)
