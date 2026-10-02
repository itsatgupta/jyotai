"""Tests for the non-astrological deterministic Task 08 rule framework."""

from inspect import getsource

import pytest
from pydantic import ValidationError

from astrologer.rules.demo import DEMO_RULES
from astrologer.rules.evaluator import RULE_FRAMEWORK_VERSION, RuleEvaluator
from astrologer.rules.loader import RuleLoader, RuleLoadError
from astrologer.rules.models import (
    ConditionDefinition,
    ConditionKind,
    ConditionOperation,
    EvaluationStatus,
    Fact,
    FactSet,
    RuleDefinition,
    RuleEffect,
)


def _leaf(
    operation: ConditionOperation,
    fact_id: str = "test.value",
    *,
    value: object | None = None,
    values: tuple[object, ...] | None = None,
) -> ConditionDefinition:
    data: dict[str, object] = {
        "kind": ConditionKind.LEAF,
        "operation": operation,
        "fact_id": fact_id,
    }
    if value is not None:
        data["expected_value"] = value
    if values is not None:
        data["expected_values"] = values
    return ConditionDefinition.model_validate(data)


def _rule(
    condition: ConditionDefinition,
    *,
    rule_id: str = "TEST_RULE",
    rule_version: str = "1",
) -> RuleDefinition:
    return RuleDefinition(
        rule_id=rule_id,
        rule_version=rule_version,
        ruleset_version="test-rules-v1",
        name="Synthetic test rule",
        domain="test",
        is_synthetic_demo=True,
        condition=condition,
        effect=RuleEffect(effect_key="test.effect", label="Synthetic test effect"),
    )


def _facts(*facts: Fact) -> FactSet:
    return FactSet(facts=facts)


@pytest.mark.parametrize("value", [True, "value", 1.5, ["a", "b"]])
def test_valid_facts_are_immutable_and_referenceable(value: object) -> None:
    fact = Fact(fact_id="test.value", value=value)
    facts = _facts(fact)

    assert facts.by_id()["test.value"] == fact
    with pytest.raises(ValidationError):
        fact.fact_id = "changed"  # type: ignore[misc]


def test_fact_ids_are_validated_and_unique() -> None:
    with pytest.raises(ValidationError, match="fact_id"):
        Fact(fact_id="invalid id", value=True)
    with pytest.raises(ValidationError, match="unique"):
        _facts(Fact(fact_id="test.same", value=True), Fact(fact_id="test.same", value=False))


@pytest.mark.parametrize(
    ("operation", "fact_value", "kwargs", "expected"),
    [
        (ConditionOperation.EQUALS, "a", {"value": "a"}, EvaluationStatus.TRUE),
        (ConditionOperation.EQUALS, "a", {"value": "b"}, EvaluationStatus.FALSE),
        (ConditionOperation.NOT_EQUALS, "a", {"value": "b"}, EvaluationStatus.TRUE),
        (ConditionOperation.NOT_EQUALS, "a", {"value": "a"}, EvaluationStatus.FALSE),
        (ConditionOperation.IN, "a", {"values": ("a", "b")}, EvaluationStatus.TRUE),
        (ConditionOperation.IN, "c", {"values": ("a", "b")}, EvaluationStatus.FALSE),
        (ConditionOperation.NOT_IN, "c", {"values": ("a", "b")}, EvaluationStatus.TRUE),
        (ConditionOperation.NOT_IN, "a", {"values": ("a", "b")}, EvaluationStatus.FALSE),
    ],
)
def test_leaf_operations(
    operation: ConditionOperation,
    fact_value: object,
    kwargs: dict[str, object],
    expected: EvaluationStatus,
) -> None:
    result = RuleEvaluator().evaluate_rule(
        _rule(_leaf(operation, **kwargs)),
        _facts(Fact(fact_id="test.value", value=fact_value)),
    )

    assert result.status is expected
    assert result.referenced_fact_ids == ("test.value",)
    assert result.resolved_fact_ids == ("test.value",)


def test_exists_distinguishes_present_and_absent_but_other_missing_facts_are_unknown() -> None:
    evaluator = RuleEvaluator()
    exists = _rule(_leaf(ConditionOperation.EXISTS))
    comparison = _rule(_leaf(ConditionOperation.EQUALS, value=True))

    assert evaluator.evaluate_rule(exists, _facts()).status is EvaluationStatus.FALSE
    present_exists = evaluator.evaluate_rule(
        exists, _facts(Fact(fact_id="test.value", value=False))
    )
    assert present_exists.status is EvaluationStatus.TRUE
    unknown = evaluator.evaluate_rule(comparison, _facts())
    assert unknown.status is EvaluationStatus.UNKNOWN
    assert unknown.referenced_fact_ids == ("test.value",)
    assert unknown.resolved_fact_ids == ()


def _status_condition(status: EvaluationStatus) -> ConditionDefinition:
    if status is EvaluationStatus.TRUE:
        return _leaf(ConditionOperation.EQUALS, "test.true", value=True)
    if status is EvaluationStatus.FALSE:
        return _leaf(ConditionOperation.EQUALS, "test.false", value=True)
    return _leaf(ConditionOperation.EQUALS, "test.unknown", value=True)


_TRUTH_FACTS = _facts(
    Fact(fact_id="test.true", value=True),
    Fact(fact_id="test.false", value=False),
)


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        (EvaluationStatus.TRUE, EvaluationStatus.TRUE, EvaluationStatus.TRUE),
        (EvaluationStatus.TRUE, EvaluationStatus.FALSE, EvaluationStatus.FALSE),
        (EvaluationStatus.TRUE, EvaluationStatus.UNKNOWN, EvaluationStatus.UNKNOWN),
        (EvaluationStatus.FALSE, EvaluationStatus.UNKNOWN, EvaluationStatus.FALSE),
        (EvaluationStatus.UNKNOWN, EvaluationStatus.UNKNOWN, EvaluationStatus.UNKNOWN),
    ],
)
def test_all_uses_kleene_three_valued_logic(
    left: EvaluationStatus, right: EvaluationStatus, expected: EvaluationStatus
) -> None:
    condition = ConditionDefinition(
        kind=ConditionKind.ALL, children=(_status_condition(left), _status_condition(right))
    )
    assert RuleEvaluator().evaluate_rule(_rule(condition), _TRUTH_FACTS).status is expected


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        (EvaluationStatus.TRUE, EvaluationStatus.TRUE, EvaluationStatus.TRUE),
        (EvaluationStatus.TRUE, EvaluationStatus.FALSE, EvaluationStatus.TRUE),
        (EvaluationStatus.TRUE, EvaluationStatus.UNKNOWN, EvaluationStatus.TRUE),
        (EvaluationStatus.FALSE, EvaluationStatus.UNKNOWN, EvaluationStatus.UNKNOWN),
        (EvaluationStatus.UNKNOWN, EvaluationStatus.UNKNOWN, EvaluationStatus.UNKNOWN),
    ],
)
def test_any_uses_kleene_three_valued_logic(
    left: EvaluationStatus, right: EvaluationStatus, expected: EvaluationStatus
) -> None:
    condition = ConditionDefinition(
        kind=ConditionKind.ANY, children=(_status_condition(left), _status_condition(right))
    )
    assert RuleEvaluator().evaluate_rule(_rule(condition), _TRUTH_FACTS).status is expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (EvaluationStatus.TRUE, EvaluationStatus.FALSE),
        (EvaluationStatus.FALSE, EvaluationStatus.TRUE),
        (EvaluationStatus.UNKNOWN, EvaluationStatus.UNKNOWN),
    ],
)
def test_not_preserves_unknown(source: EvaluationStatus, expected: EvaluationStatus) -> None:
    condition = ConditionDefinition(kind=ConditionKind.NOT, children=(_status_condition(source),))
    assert RuleEvaluator().evaluate_rule(_rule(condition), _TRUTH_FACTS).status is expected


def test_nested_condition_trace_and_rule_provenance_are_retained() -> None:
    condition = ConditionDefinition(
        kind=ConditionKind.ALL,
        children=(
            _leaf(ConditionOperation.EQUALS, "test.a", value="yes"),
            ConditionDefinition(
                kind=ConditionKind.NOT,
                children=(_leaf(ConditionOperation.EQUALS, "test.b", value="blocked"),),
            ),
        ),
    )
    result = RuleEvaluator().evaluate_rule(
        _rule(condition, rule_id="TEST_TRACE", rule_version="2"),
        _facts(Fact(fact_id="test.a", value="yes"), Fact(fact_id="test.b", value="open")),
    )

    assert result.status is EvaluationStatus.TRUE
    assert result.rule_id == "TEST_TRACE"
    assert result.rule_version == "2"
    assert result.framework_version == RULE_FRAMEWORK_VERSION
    assert result.referenced_fact_ids == ("test.a", "test.b")
    assert result.resolved_fact_ids == ("test.a", "test.b")
    assert result.condition.children[1].children[0].path == (1, 0)


def test_rule_loader_validates_and_deterministically_orders_demo_rules() -> None:
    ruleset = RuleLoader().load("task08-demo-v1", reversed(DEMO_RULES))
    results = RuleEvaluator().evaluate_rules(
        ruleset.rules,
        _facts(
            Fact(fact_id="test.flag_a", value=True),
            Fact(fact_id="test.flag_b", value=True),
        ),
    )

    assert tuple(rule.rule_id for rule in ruleset.rules) == tuple(
        sorted(rule.rule_id for rule in DEMO_RULES)
    )
    assert tuple(result.rule_id for result in results) == tuple(
        rule.rule_id for rule in ruleset.rules
    )
    assert tuple(result.status for result in results) == (
        EvaluationStatus.TRUE,
        EvaluationStatus.TRUE,
        EvaluationStatus.UNKNOWN,
    )
    repeated = RuleEvaluator().evaluate_rules(
        ruleset.rules,
        _facts(
            Fact(fact_id="test.flag_a", value=True),
            Fact(fact_id="test.flag_b", value=True),
        ),
    )
    assert results == repeated


@pytest.mark.parametrize(
    "definition",
    [
        {"rule_id": "bad"},
        {
            "rule_id": "BAD_OPERATION",
            "rule_version": "1",
            "ruleset_version": "test-rules-v1",
            "name": "bad",
            "domain": "test",
            "condition": {"kind": "leaf", "operation": "gt", "fact_id": "test.value"},
            "effect": {"effect_key": "test.effect", "label": "bad"},
        },
        {
            "rule_id": "BAD_TREE",
            "rule_version": "1",
            "ruleset_version": "test-rules-v1",
            "name": "bad",
            "domain": "test",
            "condition": {"kind": "not", "children": []},
            "effect": {"effect_key": "test.effect", "label": "bad"},
        },
    ],
)
def test_loader_rejects_invalid_schema_unsupported_operations_and_malformed_trees(
    definition: dict[str, object],
) -> None:
    with pytest.raises(RuleLoadError, match="invalid rule definition"):
        RuleLoader().load("test-rules-v1", (definition,))


def test_loader_rejects_duplicate_id_version_and_mismatched_ruleset_version() -> None:
    rule = _rule(_leaf(ConditionOperation.EXISTS))
    with pytest.raises(RuleLoadError, match="unique"):
        RuleLoader().load("test-rules-v1", (rule, rule))
    with pytest.raises(RuleLoadError, match="ruleset_version"):
        RuleLoader().load("different-ruleset", (rule,))


@pytest.mark.parametrize(
    "condition",
    [
        {"kind": "leaf", "operation": "equals", "fact_id": "test.a"},
        {"kind": "leaf", "operation": "exists", "fact_id": "test.a", "expected_value": True},
        {"kind": "all", "children": []},
        {"kind": "any", "children": []},
        {
            "kind": "not",
            "children": [
                {"kind": "leaf", "operation": "exists", "fact_id": "a"},
                {"kind": "leaf", "operation": "exists", "fact_id": "b"},
            ],
        },
    ],
)
def test_condition_shape_is_strictly_validated(condition: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        ConditionDefinition.model_validate(condition)


def test_evaluator_has_no_astrology_calculation_dependency() -> None:
    source = getsource(RuleEvaluator)
    assert "astrologer.astrology" not in source
    assert "ChartEngine" not in source
    assert "VargaEngine" not in source
    assert "Vimshottari" not in source
    assert "TransitEngine" not in source
