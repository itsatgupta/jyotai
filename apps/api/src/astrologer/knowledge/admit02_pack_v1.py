"""NEXT-ADMIT-02: the reviewer's Sitting 1 + 2 written verdicts, cumulative release v12.

Source of every decision: ``research/prereview/pandit-ji-verdicts-2026-11-24.md`` (the
verdicts, verbatim) and the superseding governance record
``docs/admissions/jyotish.admit02.sitting-1-2.admission.v1.md``.  Release v11
(``career_part0_pack_v1``) and every earlier record stay unchanged; this module only adds
superseding records.

What changes relative to v11:

* Items 1–24 (existing rules) are confirmed under a new review record.  A confirmed rule
  keeps its id, version and condition; it points to a new interpretation record whose
  statement is the v11 statement byte for byte, or the reviewer's changed wording where his
  verdict changes it (items 4, 5, 6, 7, 14, 15).
* Item 4: ``10th lord in the 4th or 10th`` is split into two rules, ``…equals_4`` and
  ``…equals_10``, each with its own wording.  The combined Career rule leaves the manifest.
* Item 18: the Children rule ``10th lord in the 5th or 11th`` leaves the manifest (not
  surfaced in Children answers).  Its passage and interpretation stay in the registry (the
  source ledger); its weight is recorded as secondary in ``rule_weights``.
* Sitting 2 item 29 (मद, v.72): the 7th-house part of v.72 is paused.  ``…in_2_3_or_7``
  leaves the manifest; ``…in_2_or_3`` keeps the 2nd/3rd wording, and ``…equals_7`` states
  only that a reviewed indication exists with wording pending source verification.
* Sitting 2 item 27 (v.71): the printed reading कर्मेशाधिपतौ is recorded on a new passage
  record for the 10th lord in the 1st.

Weights (primary / secondary) are display metadata in ``rule_weights``; they never score.
"""

from datetime import UTC, datetime
from typing import Final

from astrologer.knowledge.career_part0_pack_v1 import (
    ACTIVE_PRODUCTION_RELEASE as RELEASE_V11,
)
from astrologer.knowledge.career_part0_pack_v1 import (
    PASSAGE_IN_1,
    RULE_IN_1,
    RULE_IN_2_3_OR_7,
    RULE_IN_8,
    TENTH_LORD_FACT_ID,
)
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
    TranslationRecord,
)
from astrologer.rules.models import (
    ConditionDefinition,
    ConditionKind,
    ConditionOperation,
    RuleDefinition,
    RuleEffect,
)

# The review record, exactly as instructed by the project owner (NEXT-ADMIT-02).
ADMIT02_REVIEWER: Final = "Pandit ji (full name pending)"
ADMIT02_REVIEWED_AT: Final = datetime(2026, 11, 24, tzinfo=UTC)
ADMIT02_CHANNEL: Final = "written verdicts relayed by Atul, 2026-11-24"
ADMIT02_NOTE: Final = (
    "Admission instructed by the project owner; authorship of the written verdicts not "
    "independently confirmed."
)
ADMIT02_RECORD: Final = "docs/admissions/jyotish.admit02.sitting-1-2.admission.v1.md"
_INTERPRETATION_VERSION: Final = "admit02-v1"


def admit02_notes(item: str) -> str:
    """Review notes naming the reviewer, channel, the owner's note and the verdict item."""
    return (
        f"Reviewer: {ADMIT02_REVIEWER}; qualification: Acharya. Channel: {ADMIT02_CHANNEL}. "
        f"{ADMIT02_NOTE} Verdict: {item} (pandit-ji-verdicts-2026-11-24.md). "
        f"Record: {ADMIT02_RECORD}."
    )


def admit02_review(category: ReviewCategory, item: str) -> ReviewRecord:
    return ReviewRecord(
        category=category,
        status=ReviewStatus.REVIEWED,
        reviewer=ADMIT02_REVIEWER,
        reviewed_at=ADMIT02_REVIEWED_AT,
        notes=admit02_notes(item),
    )


# Rule ids (unchanged ids are listed for the confirmation table below).
RULE_11_IN_9_OR_10_GENERAL: Final = "bphs.d1.house_lord.11.in_9_or_10.v1"
RULE_10_IN_4_OR_10: Final = "bphs.d1.house_lord.10.in_4_or_10.v1"
RULE_10_IN_4: Final = "bphs.d1.house_lord.10.equals_4.v1"
RULE_10_IN_10: Final = "bphs.d1.house_lord.10.equals_10.v1"
RULE_10_IN_5_OR_11: Final = "bphs.d1.house_lord.10.in_5_or_11.v1"
RULE_10_IN_6_OR_12: Final = "bphs.d1.house_lord.10.in_6_or_12.v1"
RULE_10_IN_9: Final = "bphs.d1.house_lord.10.equals_9.v1"
RULE_IN_2_OR_3: Final = "bphs.d1.house_lord.10.in_2_or_3.v1"
RULE_IN_7: Final = "bphs.d1.house_lord.10.equals_7.v1"
RULE_CHILDREN_10_IN_5_OR_11: Final = "bphs.d1.house_lord.10.in_5_or_11.children.v1"

# Rules whose reviewed statement withholds or pauses the text's wording, with the clause the
# glance uses instead of the rule's label.
WITHHELD_WORDING_CLAUSES: Final[dict[str, str]] = {
    RULE_IN_8: (
        "a reviewed indication exists for this placement; its wording is withheld pending "
        "further review"
    ),
    RULE_IN_7: "a reviewed indication exists; wording pending source verification",
}
WITHHELD_WORDING_RULE_IDS: Final = frozenset(WITHHELD_WORDING_CLAUSES)

# Leave the manifest in v12; their v11 records stay in the registry (source ledger).
REMOVED_FROM_MANIFEST: Final = frozenset(
    {RULE_10_IN_4_OR_10, RULE_IN_2_3_OR_7, RULE_CHILDREN_10_IN_5_OR_11}
)

_NON_GUARANTEE: Final = (
    "These do not by themselves establish a specific profession, promotion, income, or timing."
)
_TEXT_4_OR_10: Final = (
    "The text also associates the placement with knowledge, comfort, courage, devotion or "
    "worship, and dharmic and truth-oriented qualities."
)
STATEMENT_10_IN_10: Final = (
    "With the D1 tenth-house lord in the tenth house, this is contextual evidence for career "
    "matters. This placement indicates a strong connection with profession, status and public "
    f"activity. {_TEXT_4_OR_10} {_NON_GUARANTEE}"
)
STATEMENT_10_IN_4: Final = (
    "With the D1 tenth-house lord in the fourth house, this is contextual evidence for career "
    "matters. This placement connects karma or profession with property, homeland, the "
    "institutional environment, public position, education or administration, depending on "
    f"the rest of the chart. {_TEXT_4_OR_10} {_NON_GUARANTEE}"
)
STATEMENT_10_IN_5_OR_11: Final = (
    "With the D1 tenth-house lord in the fifth or eleventh house, this is contextual evidence "
    "for career matters. For career, the fifth house connects karma or profession with "
    "intelligence, creativity, counsel, decision-making and merit, and the eleventh house "
    f"connects it with gains, fulfilment and networks. {_NON_GUARANTEE}"
)
STATEMENT_10_IN_6_OR_12: Final = (
    "With the D1 tenth-house lord in the sixth or twelfth house, this is contextual evidence "
    "for career matters; it is not by itself an adverse career indication. In the sixth house "
    "it can indicate service or employment, competition, disputes, subordinate or service "
    "environments, overcoming opposition, and work involving problem solving. In the twelfth "
    "house it can indicate foreign connection, institutions, hospitals or large "
    "organizations, remote or behind-the-scenes work, expenditure of effort, and work away "
    f"from the birthplace. {_NON_GUARANTEE}"
)
STATEMENT_10_IN_9: Final = (
    "With the D1 tenth-house lord in the ninth house, this is contextual evidence for career "
    "matters, read as a dharma–karma relationship between the 9th and 10th houses. It can "
    "connect career with dharma, higher learning, mentors, institutions, father or guru "
    "influences, travel or foreign connections, and ethical or advisory roles. The text also "
    "associates this placement with family support or protection, good companions or friends, "
    f"maternal devotion, and worship. {_NON_GUARANTEE}"
)
STATEMENT_EDUCATION_11_IN_11: Final = (
    "With the eleventh-house lord in the eleventh house, the chart is associated with "
    "scholarship and broader learning or intellectual accomplishment. This is static natal "
    "context and does not establish timing, scores, exam results, or future academic "
    "achievement."
)
STATEMENT_BUSINESS_6_IN_9: Final = (
    "With the D1 sixth-house lord in the ninth house, this is a secondary commercial/trade-"
    "related indication. The selected BPHS rendering associates this placement with selling "
    "goods such as wood or stone and with trade. It does not establish business success, "
    "profit or loss, livelihood, self-employment, timing, or certainty."
)
# v11 Part 0a-2 wording with the paused 7th house taken out of the condition it names.
STATEMENT_IN_2_OR_3: Final = (
    "With the D1 tenth-house lord in the second or third house, this is contextual evidence "
    "for career matters. The text associates this placement with a high-minded, virtuous and "
    "articulate nature, and with truthfulness and dharma. These broader life themes do not by "
    "themselves establish a profession, promotion, income, or timing."
)
STATEMENT_IN_7_PAUSED: Final = (
    "With the D1 tenth-house lord in the seventh house, a reviewed indication exists; wording "
    "pending source verification. This does not by itself establish a profession, promotion, "
    "income, or timing."
)

# Rule id → (verdict item, changed statement or None for "confirm, wording unchanged").
_CONFIRMED_OR_CHANGED: Final[dict[str, tuple[str, str | None]]] = {
    RULE_11_IN_9_OR_10_GENERAL: ("Sitting 1 item 3", None),
    RULE_10_IN_5_OR_11: ("Sitting 1 item 5", STATEMENT_10_IN_5_OR_11),
    RULE_10_IN_6_OR_12: ("Sitting 1 item 6", STATEMENT_10_IN_6_OR_12),
    RULE_10_IN_9: ("Sitting 1 item 7", STATEMENT_10_IN_9),
    "bphs.d1.house_lord.11.in_1.wealth.v1": ("Sitting 1 item 8", None),
    "bphs.d1.house_lord.11.in_2_or_5.wealth.v1": ("Sitting 1 item 9", None),
    "bphs.d1.house_lord.11.in_9_or_10.wealth.v1": ("Sitting 1 item 10", None),
    "bphs.d1.house_lord.5.in_11.wealth.v1": ("Sitting 1 item 11", None),
    "bphs.d1.house_lord.4.in_1_or_7.education.v1": ("Sitting 1 item 12", None),
    "bphs.d1.house_lord.5.in_11.education.v1": ("Sitting 1 item 13", None),
    "bphs.d1.house_lord.11.in_11.education.v1": (
        "Sitting 1 item 14",
        STATEMENT_EDUCATION_11_IN_11,
    ),
    "bphs.d1.house_lord.6.in_9.business.v1": ("Sitting 1 item 15", STATEMENT_BUSINESS_6_IN_9),
    "bphs.d1.house_lord.5.in_11.children.v1": ("Sitting 1 item 16", None),
    "bphs.d1.house_lord.11.in_2_or_5.children.v1": ("Sitting 1 item 17", None),
    "bphs.d1.house_lord.10.in_4_or_10.spirituality.v1": ("Sitting 1 item 19", None),
    "bphs.d1.house_lord.10.equals_9.spirituality.v1": ("Sitting 1 item 20", None),
    "bphs.d1.house_lord.11.in_2_or_5.spirituality.v1": ("Sitting 1 item 21", None),
    "bphs.d1.house_lord.11.in_9_or_10.spirituality.v1": ("Sitting 1 item 22", None),
    "bphs.d1.house_lord.6.in_2_or_10.travel.v1": ("Sitting 1 item 23", None),
    "bphs.d1.house_lord.10.equals_9.friends.v1": ("Sitting 1 item 24", None),
    RULE_IN_1: ("Sitting 2 item 27 (v.71 printed reading)", None),
}

_V11_INTERPRETATIONS: Final = {
    item.interpretation_id: item for item in RELEASE_V11.registry.interpretations
}
_V11_TRANSLATIONS: Final = {item.translation_id: item for item in RELEASE_V11.registry.translations}
_V11_PASSAGES: Final = {item.passage_id: item for item in RELEASE_V11.registry.passages}
_V11_ENVELOPES: Final = {item.rule.rule_id: item for item in RELEASE_V11.envelopes}

# Sitting 2 item 27: a new passage record carrying the printed v.71 reading.
PASSAGE_IN_1_READING: Final = f"{PASSAGE_IN_1}.printed-reading"
_PASSAGE_IN_1_V11: Final = _V11_PASSAGES[PASSAGE_IN_1]
_NEW_PASSAGES: Final = (
    SourcePassage(
        passage_id=PASSAGE_IN_1_READING,
        source_id=_PASSAGE_IN_1_V11.source_id,
        locator=_PASSAGE_IN_1_V11.locator,
        passage_reference=_PASSAGE_IN_1_V11.passage_reference,
        ambiguity_notes=(
            "Source reading recorded as printed on the page: कर्मेशाधिपतौ (verse ७१). It is "
            "kept as the source reading and is not normalized to कर्माधिपतौ; any scholarly "
            "interpretation is recorded separately. The rule's meaning is the same either way."
        ),
        review=admit02_review(ReviewCategory.SOURCE_VERIFICATION, "Sitting 2 item 27"),
    ),
)
_IN_1_TRANSLATION_V11: Final = _V11_TRANSLATIONS[f"{PASSAGE_IN_1}.draft-translation"]
_NEW_TRANSLATIONS: Final = (
    TranslationRecord(
        translation_id=f"{PASSAGE_IN_1_READING}.draft-translation",
        translation_version="v1",
        passage_id=PASSAGE_IN_1_READING,
        language=_IN_1_TRANSLATION_V11.language,
        text=_IN_1_TRANSLATION_V11.text,
        review=admit02_review(ReviewCategory.TRANSLATION_VERIFICATION, "Sitting 2 item 27"),
    ),
)


def _interpretation_id(passage_id: str, suffix: str = "") -> str:
    return f"{passage_id}{suffix}.interpretation.admit02"


def _superseding_interpretation(
    v11: ReviewedInterpretation,
    *,
    item: str,
    statement: str | None,
    passage_id: str | None = None,
    translation_id: str | None = None,
    suffix: str = "",
    scope_notes: str | None = None,
) -> ReviewedInterpretation:
    passage = passage_id or v11.passage_id
    return ReviewedInterpretation(
        interpretation_id=_interpretation_id(passage, suffix),
        interpretation_version=_INTERPRETATION_VERSION,
        passage_id=passage,
        translation_id=translation_id if translation_id is not None else v11.translation_id,
        translation_applicability=v11.translation_applicability,
        statement=statement if statement is not None else v11.statement,
        scope_notes=scope_notes if scope_notes is not None else v11.scope_notes,
        review=admit02_review(ReviewCategory.INTERPRETATION_REVIEW, item),
    )


def _confirmed(rule_id: str) -> tuple[ProductionRuleEnvelope, ReviewedInterpretation]:
    item, statement = _CONFIRMED_OR_CHANGED[rule_id]
    envelope = _V11_ENVELOPES[rule_id]
    v11 = _V11_INTERPRETATIONS[envelope.interpretation_id]
    if rule_id == RULE_IN_1:
        interpretation = _superseding_interpretation(
            v11,
            item=item,
            statement=None,
            passage_id=PASSAGE_IN_1_READING,
            translation_id=f"{PASSAGE_IN_1_READING}.draft-translation",
        )
    else:
        # One passage can back rules in several domains; the domain keeps ids unique.
        interpretation = _superseding_interpretation(
            v11, item=item, statement=statement, suffix=f".{envelope.domain.value}"
        )
    return (
        envelope.model_copy(update={"interpretation_id": interpretation.interpretation_id}),
        interpretation,
    )


FACT_CONTRACT: Final = RELEASE_V11.fact_contract


def _new_rule(
    rule_id: str,
    name: str,
    values: tuple[int, ...],
    interpretation_id: str,
    item: str,
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
            ruleset_version="jyotish.production-rules-v12",
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
        interpretation_id=interpretation_id,
        formalization_review=admit02_review(ReviewCategory.FORMALIZATION_REVIEW, item),
    )


_PASSAGE_4_OR_10: Final = "bphs.bhavesha-phala.10th-lord.4-or-10"
_V11_4_OR_10: Final = _V11_INTERPRETATIONS[_V11_ENVELOPES[RULE_10_IN_4_OR_10].interpretation_id]
_V11_2_3_OR_7: Final = _V11_INTERPRETATIONS[_V11_ENVELOPES[RULE_IN_2_3_OR_7].interpretation_id]

# (rule id, name, houses, interpretation, verdict item)
_SPLIT: Final = (
    (
        RULE_10_IN_4,
        "D1 10th-house lord placement in fourth house",
        (4,),
        _superseding_interpretation(
            _V11_4_OR_10,
            item="Sitting 1 item 4 (split)",
            statement=STATEMENT_10_IN_4,
            suffix=".in-4",
            scope_notes=(
                "D1/Rashi only; static contextual natal evidence. Split from the v11 4th-or-10th "
                "rule (Sitting 1 item 4). No scoring, polarity, timing, or career prediction."
            ),
        ),
        "Sitting 1 item 4 (split)",
    ),
    (
        RULE_10_IN_10,
        "D1 10th-house lord placement in tenth house",
        (10,),
        _superseding_interpretation(
            _V11_4_OR_10,
            item="Sitting 1 item 4 (split)",
            statement=STATEMENT_10_IN_10,
            suffix=".in-10",
            scope_notes=(
                "D1/Rashi only; static contextual natal evidence. Split from the v11 4th-or-10th "
                "rule (Sitting 1 item 4). No scoring, polarity, timing, or career prediction."
            ),
        ),
        "Sitting 1 item 4 (split)",
    ),
    (
        RULE_IN_2_OR_3,
        "D1 10th-house lord placement in second or third house",
        (2, 3),
        _superseding_interpretation(
            _V11_2_3_OR_7,
            item="Sitting 2 item 29 (7th-house part paused)",
            statement=STATEMENT_IN_2_OR_3,
            suffix=".in-2-or-3",
            scope_notes=(
                "D1/Rashi only; static contextual natal evidence. The 2nd/3rd-house part of "
                "v.72; the 7th-house part (मद) is paused pending source verification (Sitting 2 "
                "item 29). No scoring, polarity, timing, or career prediction."
            ),
        ),
        "Sitting 2 item 29 (7th-house part paused)",
    ),
    (
        RULE_IN_7,
        "D1 10th-house lord placement in seventh house (wording paused)",
        (7,),
        _superseding_interpretation(
            _V11_2_3_OR_7,
            item="Sitting 2 item 29 (7th-house part paused)",
            statement=STATEMENT_IN_7_PAUSED,
            suffix=".in-7",
            scope_notes=(
                "D1/Rashi only; calculated match only. Whether मद in v.72 means the 7th house is "
                "held for source verification (Sitting 2 item 29); the text's wording for the "
                "7th house is not shown. No scoring, polarity, timing, or career prediction."
            ),
        ),
        "Sitting 2 item 29 (7th-house part paused)",
    ),
)

_CONFIRMED: Final = tuple(_confirmed(rule_id) for rule_id in _CONFIRMED_OR_CHANGED)
ADMIT02_INTERPRETATIONS: Final = (
    *(interpretation for _, interpretation in _CONFIRMED),
    *(interpretation for _, _, _, interpretation, _ in _SPLIT),
)

SOURCE_REGISTRY: Final = SourceRegistry(
    registry_version="jyotish-source-registry-v13",
    sources=RELEASE_V11.registry.sources,
    passages=RELEASE_V11.registry.passages + _NEW_PASSAGES,
    translations=RELEASE_V11.registry.translations + _NEW_TRANSLATIONS,
    interpretations=RELEASE_V11.registry.interpretations + ADMIT02_INTERPRETATIONS,
)

_CHANGED_BY_ID: Final = {envelope.rule.rule_id: envelope for envelope, _ in _CONFIRMED}
ADMIT02_NEW_ENVELOPES: Final = tuple(
    _new_rule(rule_id, name, values, interpretation.interpretation_id, item)
    for rule_id, name, values, interpretation, item in _SPLIT
)
PRODUCTION_ENVELOPES: Final = (
    tuple(
        _CHANGED_BY_ID.get(envelope.rule.rule_id, envelope)
        for envelope in RELEASE_V11.envelopes
        if envelope.rule.rule_id not in REMOVED_FROM_MANIFEST
    )
    + ADMIT02_NEW_ENVELOPES
)

PRODUCTION_MANIFEST: Final = ProductionCorpusManifest(
    manifest_id="jyotish.production.cumulative",
    manifest_version="v12",
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
    release_version="v12",
    manifest=PRODUCTION_MANIFEST,
    registry=SOURCE_REGISTRY,
    fact_contract=FACT_CONTRACT,
    envelopes=PRODUCTION_ENVELOPES,
)
