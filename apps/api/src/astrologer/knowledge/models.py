"""Immutable governance models for reviewed Jyotish knowledge.

These models govern source-reviewed, declarative rule data.  They do not
contain astrology calculations or interpretive doctrine.
"""

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from astrologer.rules.models import ConditionDefinition, RuleDefinition

_IDENTIFIER = r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$"
_SHA256 = r"^[a-f0-9]{64}$"


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class SourceKind(StrEnum):
    PRIMARY = "primary"
    SECONDARY = "secondary"


class RightsStatus(StrEnum):
    UNKNOWN = "unknown"
    PERMITTED_EXCERPT = "permitted_excerpt"
    REFERENCE_ONLY = "reference_only"


class ReviewStatus(StrEnum):
    DRAFT = "draft"
    REVIEWED = "reviewed"


class ReviewCategory(StrEnum):
    """The distinct governance review asserted by a lightweight review record."""

    SOURCE_VERIFICATION = "source_verification"
    TRANSLATION_VERIFICATION = "translation_verification"
    INTERPRETATION_REVIEW = "interpretation_review"
    FORMALIZATION_REVIEW = "formalization_review"


class TranslationApplicability(StrEnum):
    """Whether a reviewed interpretation requires an identified translation."""

    REQUIRED = "required"
    NOT_APPLICABLE = "not_applicable"


class RuleLifecycle(StrEnum):
    DRAFT = "draft"
    SOURCE_IDENTIFIED = "source_identified"
    SOURCE_VERIFIED = "source_verified"
    INTERPRETATION_REVIEWED = "interpretation_reviewed"
    FORMALIZED = "formalized"
    TESTED = "tested"
    APPROVED = "approved"
    PRODUCTION_ACTIVE = "production_active"
    REJECTED = "rejected"
    ON_HOLD = "on_hold"
    DISPUTED = "disputed"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"


class EvidenceDirection(StrEnum):
    """Qualitative semantics; never scores, probability, or confidence."""

    SUPPORTING = "supporting"
    CHALLENGING = "challenging"
    CONTEXTUAL = "contextual"


class JyotishDomain(StrEnum):
    GENERAL = "general"
    CAREER = "career"
    BUSINESS = "business"
    EDUCATION = "education"
    WEALTH = "wealth"
    CHILDREN = "children"
    SPIRITUALITY = "spirituality"
    TRAVEL = "travel"
    FRIENDS = "friends"
    MARRIAGE = "marriage"
    HEALTH = "health"
    PROPERTY = "property"


class RuleTaxonomy(StrEnum):
    NATAL_STRUCTURAL = "natal_structural"


class RulePosture(StrEnum):
    STATIC = "static"
    TIMING_REQUIRED = "timing_required"
    CORROBORATION_REQUIRED = "corroboration_required"


class ChartScope(StrEnum):
    D1_RASHI = "d1_rashi"
    D9_NAVAMSA = "d9_navamsa"
    D10_DASAMSA = "d10_dasamsa"


class SourceRecord(_FrozenModel):
    """Bibliographic source metadata only; production registry starts empty."""

    source_id: str = Field(pattern=_IDENTIFIER)
    source_version: str = Field(min_length=1, max_length=64)
    kind: SourceKind
    title: str = Field(min_length=1, max_length=512)
    tradition: str | None = Field(default=None, max_length=256)
    edition: str | None = Field(default=None, max_length=256)
    publisher: str | None = Field(default=None, max_length=256)
    publication_year: int | None = Field(default=None, ge=1, le=9999)
    original_language: str = Field(min_length=1, max_length=128)
    translator: str | None = Field(default=None, max_length=256)
    rights_status: RightsStatus
    rights_notes: str | None = Field(default=None, max_length=2000)
    review_notes: str | None = Field(default=None, max_length=4000)


class SourcePassage(_FrozenModel):
    """An exact locator and an optional permitted excerpt for one source."""

    passage_id: str = Field(pattern=_IDENTIFIER)
    source_id: str = Field(pattern=_IDENTIFIER)
    locator: str = Field(min_length=1, max_length=512)
    excerpt: str | None = Field(default=None, min_length=1, max_length=8000)
    passage_reference: str | None = Field(default=None, min_length=1, max_length=2000)
    content_sha256: str | None = Field(default=None, pattern=_SHA256)
    ambiguity_notes: str | None = Field(default=None, max_length=4000)
    review: "ReviewRecord | None" = None

    @model_validator(mode="after")
    def excerpt_or_reference_is_required(self) -> "SourcePassage":
        if self.excerpt is None and self.passage_reference is None:
            raise ValueError("source passage requires an excerpt or passage_reference")
        return self


class ReviewRecord(_FrozenModel):
    category: ReviewCategory
    status: ReviewStatus
    reviewer: str = Field(min_length=1, max_length=256)
    reviewed_at: datetime
    notes: str | None = Field(default=None, max_length=4000)

    @model_validator(mode="after")
    def reviewed_time_must_be_aware(self) -> "ReviewRecord":
        if self.reviewed_at.tzinfo is None or self.reviewed_at.utcoffset() is None:
            raise ValueError("reviewed_at must be timezone-aware")
        return self


class TranslationRecord(_FrozenModel):
    translation_id: str = Field(pattern=_IDENTIFIER)
    translation_version: str = Field(min_length=1, max_length=64)
    passage_id: str = Field(pattern=_IDENTIFIER)
    language: str = Field(min_length=1, max_length=128)
    text: str = Field(min_length=1, max_length=8000)
    translator: str | None = Field(default=None, max_length=256)
    review: ReviewRecord

    @model_validator(mode="after")
    def review_must_verify_translation(self) -> "TranslationRecord":
        if self.review.category is not ReviewCategory.TRANSLATION_VERIFICATION:
            raise ValueError("translation review category must be translation_verification")
        return self


class ReviewedInterpretation(_FrozenModel):
    """A human-reviewed rendering, deliberately separate from source wording."""

    interpretation_id: str = Field(pattern=_IDENTIFIER)
    interpretation_version: str = Field(min_length=1, max_length=64)
    passage_id: str = Field(pattern=_IDENTIFIER)
    translation_id: str | None = Field(default=None, pattern=_IDENTIFIER)
    translation_applicability: TranslationApplicability
    statement: str = Field(min_length=1, max_length=4000)
    scope_notes: str | None = Field(default=None, max_length=4000)
    review: ReviewRecord

    @model_validator(mode="after")
    def translation_link_and_review_category_must_match(self) -> "ReviewedInterpretation":
        if self.review.category is not ReviewCategory.INTERPRETATION_REVIEW:
            raise ValueError("interpretation review category must be interpretation_review")
        if (
            self.translation_applicability is TranslationApplicability.REQUIRED
            and self.translation_id is None
        ):
            raise ValueError("translation_id is required when translation is required")
        if (
            self.translation_applicability is TranslationApplicability.NOT_APPLICABLE
            and self.translation_id is not None
        ):
            raise ValueError("translation_id must be absent when translation is not applicable")
        return self


class SourceRegistry(_FrozenModel):
    """Versioned, internally linked register. It may validly be empty."""

    registry_version: str = Field(min_length=1, max_length=64)
    sources: tuple[SourceRecord, ...] = ()
    passages: tuple[SourcePassage, ...] = ()
    translations: tuple[TranslationRecord, ...] = ()
    interpretations: tuple[ReviewedInterpretation, ...] = ()

    @model_validator(mode="after")
    def references_must_be_unique_and_resolved(self) -> "SourceRegistry":
        _unique(self.sources, "source_id", "source")
        _unique(self.passages, "passage_id", "passage")
        _unique(self.translations, "translation_id", "translation")
        _unique(self.interpretations, "interpretation_id", "interpretation")
        source_ids = {source.source_id for source in self.sources}
        passage_ids = {passage.passage_id for passage in self.passages}
        translation_ids = {translation.translation_id for translation in self.translations}
        if any(passage.source_id not in source_ids for passage in self.passages):
            raise ValueError("source passage references an unknown source")
        if any(translation.passage_id not in passage_ids for translation in self.translations):
            raise ValueError("translation references an unknown passage")
        if any(
            interpretation.passage_id not in passage_ids for interpretation in self.interpretations
        ):
            raise ValueError("interpretation references an unknown passage")
        if any(
            interpretation.translation_id is not None
            and interpretation.translation_id not in translation_ids
            for interpretation in self.interpretations
        ):
            raise ValueError("interpretation references an unknown translation")
        return self


class FactContract(_FrozenModel):
    """Declared deterministic fact vocabulary compatible with one rule scope."""

    contract_id: str = Field(pattern=_IDENTIFIER)
    contract_version: str = Field(min_length=1, max_length=64)
    chart_scope: ChartScope
    methodology_id: str = Field(min_length=1, max_length=128)
    available_fact_ids: tuple[str, ...] = ()
    available_fact_family_prefixes: tuple[str, ...] = ()

    @model_validator(mode="after")
    def fact_contract_entries_must_be_unique_and_well_formed(self) -> "FactContract":
        if any(not _matches_identifier(value) for value in self.available_fact_ids):
            raise ValueError("fact contract contains an invalid fact ID")
        if any(
            not value.endswith(".") or not _matches_identifier(value[:-1])
            for value in self.available_fact_family_prefixes
        ):
            raise ValueError("fact family prefixes must be identifier prefixes ending in a period")
        if len(self.available_fact_ids) != len(set(self.available_fact_ids)):
            raise ValueError("fact contract IDs must be unique")
        if len(self.available_fact_family_prefixes) != len(
            set(self.available_fact_family_prefixes)
        ):
            raise ValueError("fact contract family prefixes must be unique")
        return self


class FactDependency(_FrozenModel):
    fact_id: str | None = Field(default=None, pattern=_IDENTIFIER)
    fact_family_prefix: str | None = Field(default=None, max_length=128)

    @model_validator(mode="after")
    def exactly_one_dependency_kind_is_required(self) -> "FactDependency":
        if (self.fact_id is None) == (self.fact_family_prefix is None):
            raise ValueError(
                "fact dependency requires exactly one of fact_id or fact_family_prefix"
            )
        if self.fact_family_prefix is not None and (
            not self.fact_family_prefix.endswith(".")
            or not _matches_identifier(self.fact_family_prefix[:-1])
        ):
            raise ValueError("fact_family_prefix must be an identifier prefix ending in a period")
        return self

    @property
    def key(self) -> str:
        return self.fact_id or self.fact_family_prefix or ""


class DeclarativeClause(_FrozenModel):
    """A labeled, non-executable condition used for governance traceability."""

    label: str = Field(min_length=1, max_length=256)
    condition: ConditionDefinition


class ProductionRuleEnvelope(_FrozenModel):
    """Governed metadata around the unchanged Task 08 generic rule object."""

    governance_version: Literal["jyotish-knowledge-governance-v1"] = (
        "jyotish-knowledge-governance-v1"
    )
    rule: RuleDefinition
    lifecycle: RuleLifecycle
    domain: JyotishDomain
    taxonomy: RuleTaxonomy
    posture: RulePosture
    evidence_direction: EvidenceDirection
    chart_scope: ChartScope
    fact_contract_id: str = Field(pattern=_IDENTIFIER)
    fact_contract_version: str = Field(min_length=1, max_length=64)
    fact_contract_methodology_id: str = Field(min_length=1, max_length=128)
    fact_dependencies: tuple[FactDependency, ...]
    applicability: DeclarativeClause | None = None
    prerequisites: tuple[DeclarativeClause, ...] = ()
    exceptions: tuple[DeclarativeClause, ...] = ()
    interpretation_id: str = Field(pattern=_IDENTIFIER)
    formalization_review: ReviewRecord | None = None
    framework_version: Literal["rule-framework-v1"] = "rule-framework-v1"

    @model_validator(mode="after")
    def envelope_must_have_unique_dependencies_and_clause_labels(self) -> "ProductionRuleEnvelope":
        if not self.fact_dependencies:
            raise ValueError("production rule requires explicit fact dependencies")
        keys = tuple(dependency.key for dependency in self.fact_dependencies)
        if len(keys) != len(set(keys)):
            raise ValueError("fact dependencies must be unique")
        labels = tuple(clause.label for clause in self.prerequisites + self.exceptions)
        if len(labels) != len(set(labels)):
            raise ValueError("prerequisite and exception labels must be unique")
        return self


def _unique(items: tuple[object, ...], attribute: str, label: str) -> None:
    values = tuple(getattr(item, attribute) for item in items)
    if len(values) != len(set(values)):
        raise ValueError(f"{label} IDs must be unique")


def _matches_identifier(value: str) -> bool:
    import re

    return re.fullmatch(_IDENTIFIER, value) is not None


EMPTY_SOURCE_REGISTRY = SourceRegistry(registry_version="jyotish-source-registry-v1")
