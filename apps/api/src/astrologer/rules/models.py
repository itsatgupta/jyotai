"""Validated data models for the deterministic rule framework.

The models deliberately do not encode Jyotish concepts. A future derived-fact
layer may supply those concepts as fact identifiers and JSON-compatible values.
"""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator


class EvaluationStatus(StrEnum):
    """Three-valued condition result used by the framework."""

    TRUE = "true"
    FALSE = "false"
    UNKNOWN = "unknown"


class ConditionKind(StrEnum):
    """The intentionally small, declarative condition-tree grammar."""

    LEAF = "leaf"
    ALL = "all"
    ANY = "any"
    NOT = "not"


class ConditionOperation(StrEnum):
    """Supported non-executable comparisons against one supplied fact."""

    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    IN = "in"
    NOT_IN = "not_in"
    EXISTS = "exists"


class Fact(BaseModel):
    """One immutable, referenceable fact supplied by an upstream layer."""

    model_config = ConfigDict(frozen=True)

    fact_id: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$")
    value: JsonValue


class FactSet(BaseModel):
    """A validated collection of uniquely identified input facts."""

    model_config = ConfigDict(frozen=True)

    facts: tuple[Fact, ...] = ()

    @model_validator(mode="after")
    def fact_ids_must_be_unique(self) -> "FactSet":
        identifiers = tuple(fact.fact_id for fact in self.facts)
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("fact IDs must be unique")
        return self

    def by_id(self) -> dict[str, Fact]:
        """Return a lookup built from the ordered, validated input collection."""
        return {fact.fact_id: fact for fact in self.facts}


class ConditionDefinition(BaseModel):
    """A data-only condition tree; it cannot contain executable expressions."""

    model_config = ConfigDict(frozen=True)

    kind: ConditionKind
    operation: ConditionOperation | None = None
    fact_id: str | None = Field(
        default=None,
        pattern=r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$",
    )
    expected_value: JsonValue | None = None
    expected_values: tuple[JsonValue, ...] | None = None
    children: tuple["ConditionDefinition", ...] = ()

    @model_validator(mode="after")
    def shape_must_match_kind_and_operation(self) -> "ConditionDefinition":
        if self.kind is ConditionKind.LEAF:
            self._validate_leaf()
        else:
            self._validate_compound()
        return self

    def _validate_leaf(self) -> None:
        if self.operation is None or self.fact_id is None:
            raise ValueError("leaf conditions require operation and fact_id")
        if self.children:
            raise ValueError("leaf conditions must not contain children")
        if self.operation in {ConditionOperation.EQUALS, ConditionOperation.NOT_EQUALS}:
            if self.expected_value is None or self.expected_values is not None:
                raise ValueError("equals operations require exactly expected_value")
        elif self.operation in {ConditionOperation.IN, ConditionOperation.NOT_IN}:
            if self.expected_value is not None or not self.expected_values:
                raise ValueError("membership operations require non-empty expected_values only")
        elif self.operation is ConditionOperation.EXISTS:
            if self.expected_value is not None or self.expected_values is not None:
                raise ValueError("exists operations do not accept expected values")

    def _validate_compound(self) -> None:
        if (
            self.operation is not None
            or self.fact_id is not None
            or self.expected_value is not None
            or self.expected_values is not None
        ):
            raise ValueError("compound conditions may contain only kind and children")
        if self.kind in {ConditionKind.ALL, ConditionKind.ANY} and not self.children:
            raise ValueError("all and any conditions require at least one child")
        if self.kind is ConditionKind.NOT and len(self.children) != 1:
            raise ValueError("not conditions require exactly one child")


class RuleSource(BaseModel):
    """Placeholder source metadata for future reviewed knowledge rules."""

    model_config = ConfigDict(frozen=True)

    reference: str = Field(min_length=1, max_length=256)
    notes: str | None = Field(default=None, max_length=2000)


class RuleEffect(BaseModel):
    """Rule-supplied structured result metadata, not an evaluated prediction."""

    model_config = ConfigDict(frozen=True)

    effect_key: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$")
    label: str = Field(min_length=1, max_length=256)
    strength_label: str | None = Field(default=None, min_length=1, max_length=64)


class RuleDefinition(BaseModel):
    """An immutable declarative rule evaluated against precomputed facts."""

    model_config = ConfigDict(frozen=True)

    rule_id: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$")
    rule_version: str = Field(min_length=1, max_length=64)
    ruleset_version: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=256)
    domain: str = Field(min_length=1, max_length=64)
    description: str | None = Field(default=None, max_length=2000)
    source: RuleSource | None = None
    is_synthetic_demo: bool = False
    condition: ConditionDefinition
    effect: RuleEffect


class RuleSet(BaseModel):
    """A loader-validated, deterministically ordered collection of rules."""

    model_config = ConfigDict(frozen=True)

    ruleset_version: str = Field(min_length=1, max_length=64)
    rules: tuple[RuleDefinition, ...]

    @model_validator(mode="after")
    def rules_must_share_ruleset_version_and_be_unique(self) -> "RuleSet":
        keys = tuple((rule.rule_id, rule.rule_version) for rule in self.rules)
        if len(keys) != len(set(keys)):
            raise ValueError("rule ID and version pairs must be unique")
        if any(rule.ruleset_version != self.ruleset_version for rule in self.rules):
            raise ValueError("every rule must use the containing ruleset_version")
        return self


class EvaluatedCondition(BaseModel):
    """Trace of one evaluated condition and the facts it referenced or resolved."""

    model_config = ConfigDict(frozen=True)

    path: tuple[int, ...]
    kind: ConditionKind
    operation: ConditionOperation | None = None
    status: EvaluationStatus
    referenced_fact_ids: tuple[str, ...] = ()
    resolved_fact_ids: tuple[str, ...] = ()
    children: tuple["EvaluatedCondition", ...] = ()


class RuleEvaluationResult(BaseModel):
    """Traceable deterministic result for a single rule."""

    model_config = ConfigDict(frozen=True)

    rule_id: str
    rule_version: str
    ruleset_version: str
    framework_version: str
    status: EvaluationStatus
    effect: RuleEffect
    condition: EvaluatedCondition
    referenced_fact_ids: tuple[str, ...]
    resolved_fact_ids: tuple[str, ...]


ConditionDefinition.model_rebuild()
EvaluatedCondition.model_rebuild()
