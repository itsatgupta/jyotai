"""NEXT-PROVISIONAL-01: the provisional rule tier, kept apart from reviewed knowledge.

Project-owner decision (2026-11-24): build every domain first with PROVISIONAL rules, then
hold one final expert review.  Reviewed and provisional content must never be confused, so:

* A provisional rule lives only in a :class:`ProvisionalCorpus`.  It never enters a
  ``ProductionRelease``, a manifest, the governed evaluator or the evidence package, and
  the reviewed answer text never quotes it.
* Admission to the provisional corpus requires a complete justification record: source and
  verse/locator, original text, draft translation, interpretive reasoning, conventions
  used, confidence (high/medium/low) and the author: ``PROVISIONAL_AUTHOR_AI_DRAFTED``
  (``"drafted_by: AI agent; adopted_by: project owner (pending)"``) for a rule an AI agent
  drafted, or ``PROVISIONAL_AUTHOR_OWNER`` (``"project owner, provisional"``) for one the
  project owner wrote.  Its status is ``ReviewStatus.PROVISIONAL``, never
  ``REVIEWED``, and its display text may not call itself reviewed, approved or admitted.
* The display statement passes the same ranking and evaluative guards as template text.
* A provisional rule becomes REVIEWED only through :func:`promote_to_reviewed`, which
  needs four human review records (source, translation, interpretation, formalization) and
  then runs the existing ``AdmissionValidator.validate_production_active``.  The provisional
  author can never be the reviewer, and an AI agent never is (``reviewer_guard``).

Provisional rules are D1/Rashi, static, contextual natal evidence only, conditioned on
deterministic D1 house-lord placement facts.  They carry no polarity, weight, score or timing.
"""

import re
from collections.abc import Iterable, Mapping
from datetime import datetime
from enum import StrEnum
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from astrologer.composition.comparison_guard import ranking_violation
from astrologer.composition.evaluative_guard import evaluative_violation
from astrologer.knowledge.admission import AdmissionError, AdmissionValidator
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
    SourceRecord,
    SourceRegistry,
    TranslationApplicability,
    TranslationRecord,
)
from astrologer.rules.evaluator import RuleEvaluator
from astrologer.rules.models import (
    ConditionDefinition,
    EvaluationStatus,
    Fact,
    FactSet,
    RuleDefinition,
    RuleEffect,
    RuleEvaluationResult,
)

# Who wrote the provisional rule.  An AI-drafted rule names the agent as the drafter and the
# project owner as the (pending) adopter; the owner's adoption is not a review.
PROVISIONAL_AUTHOR_OWNER: Final = "project owner, provisional"
PROVISIONAL_AUTHOR_AI_DRAFTED: Final = "drafted_by: AI agent; adopted_by: project owner (pending)"
PROVISIONAL_AUTHORS: Final = frozenset({PROVISIONAL_AUTHOR_OWNER, PROVISIONAL_AUTHOR_AI_DRAFTED})
ProvisionalAuthor = Literal[
    "project owner, provisional",
    "drafted_by: AI agent; adopted_by: project owner (pending)",
]
PROVISIONAL_BADGE: Final = "Provisional — pending expert review"
PROVISIONAL_RULE_PREFIX: Final = "provisional."
PROVISIONAL_RULESET_VERSION: Final = "jyotish.provisional-rules-v1"
REVIEWED_RULESET_VERSION: Final = "jyotish.production-rules-v1"

_PLACEMENT_FACT: Final = re.compile(r"^jyotish\.d1\.house_lord\.(?:[1-9]|1[0-2])\.placement_house$")
# Display text of a provisional rule may never present it as reviewed knowledge.
_REVIEWED_LABEL: Final = re.compile(
    r"\b(?:reviewed|approved|admitted|certified|verified)\b", re.IGNORECASE
)


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ProvisionalConfidence(StrEnum):
    """The author's own confidence in the reading; not a strength of the indication."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ProvisionalJustification(_Frozen):
    """Why the project owner proposes this rule; everything the final reviewer needs."""

    source_work: str = Field(min_length=1, max_length=512)
    locator: str = Field(min_length=1, max_length=512)
    original_text: str = Field(min_length=1, max_length=4000)
    draft_translation: str = Field(min_length=1, max_length=4000)
    interpretive_reasoning: str = Field(min_length=1, max_length=4000)
    conventions: tuple[str, ...] = Field(min_length=1)
    confidence: ProvisionalConfidence
    author: ProvisionalAuthor
    recorded_at: datetime
    status: Literal[ReviewStatus.PROVISIONAL] = ReviewStatus.PROVISIONAL
    transcription_notes: str | None = Field(default=None, max_length=4000)

    @field_validator("author", mode="before")
    @classmethod
    def author_is_a_provisional_author(cls, value: object) -> object:
        if value not in PROVISIONAL_AUTHORS:
            raise ValueError(f"provisional author must be one of {sorted(PROVISIONAL_AUTHORS)!r}")
        return value

    @field_validator("conventions")
    @classmethod
    def conventions_are_non_empty(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if any(not item.strip() for item in value):
            raise ValueError("conventions must not contain empty entries")
        return value

    @field_validator("recorded_at")
    @classmethod
    def recorded_time_is_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("recorded_at must be timezone-aware")
        return value


class ProvisionalRule(_Frozen):
    """One provisional D1 natal rule with its justification."""

    tier: Literal["provisional"] = "provisional"
    rule: RuleDefinition
    domain: JyotishDomain
    chart_scope: Literal[ChartScope.D1_RASHI] = ChartScope.D1_RASHI
    posture: Literal[RulePosture.STATIC] = RulePosture.STATIC
    evidence_direction: Literal[EvidenceDirection.CONTEXTUAL] = EvidenceDirection.CONTEXTUAL
    fact_dependencies: tuple[str, ...] = Field(min_length=1)
    statement: str = Field(min_length=1, max_length=2000)
    justification: ProvisionalJustification

    @model_validator(mode="after")
    def rule_is_admissible(self) -> "ProvisionalRule":
        if (violation := provisional_violation(self)) is not None:
            raise ValueError(violation)
        return self

    @property
    def rule_id(self) -> str:
        return self.rule.rule_id


def provisional_violation(rule: ProvisionalRule) -> str | None:
    """Why ``rule`` cannot enter the provisional corpus, or None when it can."""
    definition = rule.rule
    if not definition.rule_id.startswith(PROVISIONAL_RULE_PREFIX):
        return f"provisional rule ids must start with {PROVISIONAL_RULE_PREFIX!r}"
    if definition.ruleset_version != PROVISIONAL_RULESET_VERSION:
        return f"provisional rules must use ruleset {PROVISIONAL_RULESET_VERSION!r}"
    if definition.domain != rule.domain.value:
        return "rule domain does not match the provisional domain"
    if definition.is_synthetic_demo or definition.source is not None:
        return "provisional provenance must use the justification record"
    if definition.effect.strength_label is not None:
        return "provisional rules carry no strength label"
    if len(set(rule.fact_dependencies)) != len(rule.fact_dependencies):
        return "fact dependencies must be unique"
    if any(_PLACEMENT_FACT.fullmatch(item) is None for item in rule.fact_dependencies):
        return "provisional rules may depend only on D1 house-lord placement facts"
    if any(
        item not in rule.fact_dependencies for item in _condition_fact_ids(definition.condition)
    ):
        return "rule condition uses a fact that is not declared as a dependency"
    if (match := ranking_violation(rule.statement)) is not None:
        return f"statement fails the ranking guard: {match!r}"
    if (match := evaluative_violation(rule.statement)) is not None:
        return f"statement fails the evaluative guard: {match!r}"
    if (label := _REVIEWED_LABEL.search(rule.statement)) is not None:
        return f"provisional statement may not present itself as reviewed: {label.group()!r}"
    return None


class ProvisionalCorpus(_Frozen):
    """A versioned set of provisional rules; it may be empty."""

    corpus_id: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$")
    corpus_version: str = Field(min_length=1, max_length=64)
    rules: tuple[ProvisionalRule, ...] = ()

    @model_validator(mode="after")
    def rules_are_unique_and_ordered(self) -> "ProvisionalCorpus":
        ids = tuple(rule.rule_id for rule in self.rules)
        if len(ids) != len(set(ids)):
            raise ValueError("provisional rule ids must be unique")
        if ids != tuple(sorted(ids)):
            raise ValueError("provisional rules must be in rule-id order")
        return self

    @property
    def release_id(self) -> str:
        return f"{self.corpus_id}@{self.corpus_version}"

    def for_domain(self, domain: str) -> tuple[ProvisionalRule, ...]:
        return tuple(rule for rule in self.rules if rule.domain.value == domain)


def require_disjoint(corpus: ProvisionalCorpus, reviewed_rule_ids: Iterable[str]) -> None:
    """A provisional rule id may never collide with a reviewed rule id."""
    reviewed = set(reviewed_rule_ids)
    clashes = sorted(rule.rule_id for rule in corpus.rules if rule.rule_id in reviewed)
    if clashes:
        raise AdmissionError(f"provisional rule ids collide with reviewed rules: {clashes}")


def evaluate_provisional(
    corpus: ProvisionalCorpus, facts: Mapping[str, object], domain: str
) -> tuple[tuple[ProvisionalRule, RuleEvaluationResult], ...]:
    """The domain's provisional rules whose condition is TRUE on the chart's D1 facts.

    FALSE and UNKNOWN are dropped: a provisional rule never yields a negative statement.
    """
    rules = corpus.for_domain(domain)
    if not rules:
        return ()
    needed = {fact_id for rule in rules for fact_id in rule.fact_dependencies}
    fact_set = FactSet(
        facts=tuple(
            Fact(fact_id=fact_id, value=facts[fact_id])  # type: ignore[arg-type]
            for fact_id in sorted(needed)
            if fact_id in facts
        )
    )
    evaluator = RuleEvaluator()
    matches: list[tuple[ProvisionalRule, RuleEvaluationResult]] = []
    for rule in rules:
        result = evaluator.evaluate_rule(rule.rule, fact_set)
        if result.status is EvaluationStatus.TRUE:
            matches.append((rule, result))
    return tuple(matches)


class PromotionReviews(_Frozen):
    """The four human review records the existing admission flow requires."""

    source_verification: ReviewRecord
    translation_verification: ReviewRecord
    interpretation_review: ReviewRecord
    formalization_review: ReviewRecord


class PromotionResult(_Frozen):
    """A REVIEWED envelope and the registry entries that admit it."""

    envelope: ProductionRuleEnvelope
    registry: SourceRegistry


def reviewed_rule_id(provisional_rule_id: str) -> str:
    """The reviewed id a provisional rule is promoted to (the prefix is dropped)."""
    return provisional_rule_id.removeprefix(PROVISIONAL_RULE_PREFIX)


def promote_to_reviewed(
    rule: ProvisionalRule,
    reviews: PromotionReviews | None,
    *,
    source: SourceRecord,
    fact_contract: FactContract,
    registry_version: str,
    reviewed_statement: str | None = None,
) -> PromotionResult:
    """Promote one provisional rule to REVIEWED through the existing admission flow.

    Without a complete set of human review records this always raises
    :class:`AdmissionError`.  The reviewer may change the statement (``reviewed_statement``);
    otherwise the provisional statement is carried over unchanged.
    """
    if reviews is None:
        raise AdmissionError("promotion to reviewed requires a review record")
    for field, category in (
        ("source_verification", ReviewCategory.SOURCE_VERIFICATION),
        ("translation_verification", ReviewCategory.TRANSLATION_VERIFICATION),
        ("interpretation_review", ReviewCategory.INTERPRETATION_REVIEW),
        ("formalization_review", ReviewCategory.FORMALIZATION_REVIEW),
    ):
        review: ReviewRecord = getattr(reviews, field)
        if review.category is not category:
            raise AdmissionError(f"{field} must be a {category.value} review")
        if review.status is not ReviewStatus.REVIEWED:
            raise AdmissionError(f"{field} must be a completed (reviewed) review record")
        reviewer = review.reviewer.lower()
        if (
            "provisional" in reviewer
            or "ai agent" in reviewer
            or review.reviewer in PROVISIONAL_AUTHORS
        ):
            raise AdmissionError("the provisional author is never the reviewer of the rule")
    base = reviewed_rule_id(rule.rule_id)
    justification = rule.justification
    passage = SourcePassage(
        passage_id=f"{base}.passage",
        source_id=source.source_id,
        locator=justification.locator,
        excerpt=justification.original_text,
        ambiguity_notes=justification.transcription_notes,
        review=reviews.source_verification,
    )
    translation = TranslationRecord(
        translation_id=f"{base}.translation",
        translation_version="v1",
        passage_id=passage.passage_id,
        language="English",
        text=justification.draft_translation,
        review=reviews.translation_verification,
    )
    interpretation = ReviewedInterpretation(
        interpretation_id=f"{base}.interpretation",
        interpretation_version="v1",
        passage_id=passage.passage_id,
        translation_id=translation.translation_id,
        translation_applicability=TranslationApplicability.REQUIRED,
        statement=reviewed_statement or rule.statement,
        scope_notes="D1/Rashi, static, contextual natal evidence only. No timing or scoring.",
        review=reviews.interpretation_review,
    )
    registry = SourceRegistry(
        registry_version=registry_version,
        sources=(source,),
        passages=(passage,),
        translations=(translation,),
        interpretations=(interpretation,),
    )
    envelope = ProductionRuleEnvelope(
        rule=RuleDefinition(
            rule_id=base,
            rule_version=rule.rule.rule_version,
            ruleset_version=REVIEWED_RULESET_VERSION,
            name=rule.rule.name,
            domain=rule.domain.value,
            condition=rule.rule.condition,
            effect=RuleEffect(
                effect_key=reviewed_rule_id(rule.rule.effect.effect_key),
                label=rule.rule.effect.label,
            ),
        ),
        lifecycle=RuleLifecycle.PRODUCTION_ACTIVE,
        domain=rule.domain,
        taxonomy=RuleTaxonomy.NATAL_STRUCTURAL,
        posture=RulePosture.STATIC,
        evidence_direction=EvidenceDirection.CONTEXTUAL,
        chart_scope=ChartScope.D1_RASHI,
        fact_contract_id=fact_contract.contract_id,
        fact_contract_version=fact_contract.contract_version,
        fact_contract_methodology_id=fact_contract.methodology_id,
        fact_dependencies=tuple(FactDependency(fact_id=item) for item in rule.fact_dependencies),
        interpretation_id=interpretation.interpretation_id,
        formalization_review=reviews.formalization_review,
    )
    AdmissionValidator().validate_production_active(envelope, registry, fact_contract)
    return PromotionResult(envelope=envelope, registry=registry)


def _condition_fact_ids(definition: ConditionDefinition) -> Iterable[str]:
    if definition.fact_id is not None:
        yield definition.fact_id
    for child in definition.children:
        yield from _condition_fact_ids(child)
