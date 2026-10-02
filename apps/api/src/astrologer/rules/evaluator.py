"""Deterministic, three-valued evaluation of declarative rule definitions."""

from collections.abc import Iterable

from astrologer.rules.models import (
    ConditionDefinition,
    ConditionKind,
    ConditionOperation,
    EvaluatedCondition,
    EvaluationStatus,
    Fact,
    FactSet,
    RuleDefinition,
    RuleEvaluationResult,
)

RULE_FRAMEWORK_VERSION = "rule-framework-v1"


class RuleEvaluator:
    """Evaluate rules against supplied facts without deriving any new facts."""

    def evaluate_rule(self, rule: RuleDefinition, facts: FactSet) -> RuleEvaluationResult:
        """Evaluate one rule and retain a complete condition/fact trace."""
        condition = self._evaluate_condition(rule.condition, facts.by_id(), ())
        return RuleEvaluationResult(
            rule_id=rule.rule_id,
            rule_version=rule.rule_version,
            ruleset_version=rule.ruleset_version,
            framework_version=RULE_FRAMEWORK_VERSION,
            status=condition.status,
            effect=rule.effect,
            condition=condition,
            referenced_fact_ids=_unique_fact_ids(condition, "referenced_fact_ids"),
            resolved_fact_ids=_unique_fact_ids(condition, "resolved_fact_ids"),
        )

    def evaluate_rules(
        self, rules: Iterable[RuleDefinition], facts: FactSet
    ) -> tuple[RuleEvaluationResult, ...]:
        """Evaluate rules in stable rule-ID/version order."""
        ordered_rules = sorted(rules, key=lambda rule: (rule.rule_id, rule.rule_version))
        return tuple(self.evaluate_rule(rule, facts) for rule in ordered_rules)

    def _evaluate_condition(
        self,
        definition: ConditionDefinition,
        facts_by_id: dict[str, Fact],
        path: tuple[int, ...],
    ) -> EvaluatedCondition:
        if definition.kind is ConditionKind.LEAF:
            return self._evaluate_leaf(definition, facts_by_id, path)
        children = tuple(
            self._evaluate_condition(child, facts_by_id, path + (index,))
            for index, child in enumerate(definition.children)
        )
        return EvaluatedCondition(
            path=path,
            kind=definition.kind,
            status=_compound_status(definition.kind, tuple(child.status for child in children)),
            children=children,
        )

    @staticmethod
    def _evaluate_leaf(
        definition: ConditionDefinition,
        facts_by_id: dict[str, Fact],
        path: tuple[int, ...],
    ) -> EvaluatedCondition:
        assert definition.operation is not None
        assert definition.fact_id is not None
        fact = facts_by_id.get(definition.fact_id)
        if definition.operation is ConditionOperation.EXISTS:
            status = EvaluationStatus.TRUE if fact is not None else EvaluationStatus.FALSE
        elif fact is None:
            status = EvaluationStatus.UNKNOWN
        else:
            status = _leaf_status(definition, fact)
        return EvaluatedCondition(
            path=path,
            kind=ConditionKind.LEAF,
            operation=definition.operation,
            status=status,
            referenced_fact_ids=(definition.fact_id,),
            resolved_fact_ids=(definition.fact_id,) if fact is not None else (),
        )


def _leaf_status(definition: ConditionDefinition, fact: Fact) -> EvaluationStatus:
    """Evaluate a validated leaf condition whose input fact is present."""
    assert definition.operation is not None
    if definition.operation is ConditionOperation.EQUALS:
        return _boolean_status(fact.value == definition.expected_value)
    if definition.operation is ConditionOperation.NOT_EQUALS:
        return _boolean_status(fact.value != definition.expected_value)
    assert definition.expected_values is not None
    contains = fact.value in definition.expected_values
    if definition.operation is ConditionOperation.IN:
        return _boolean_status(contains)
    return _boolean_status(not contains)


def _compound_status(
    kind: ConditionKind, statuses: tuple[EvaluationStatus, ...]
) -> EvaluationStatus:
    """Apply Kleene three-valued logic to a validated compound condition."""
    if kind is ConditionKind.NOT:
        return {
            EvaluationStatus.TRUE: EvaluationStatus.FALSE,
            EvaluationStatus.FALSE: EvaluationStatus.TRUE,
            EvaluationStatus.UNKNOWN: EvaluationStatus.UNKNOWN,
        }[statuses[0]]
    if kind is ConditionKind.ALL:
        if EvaluationStatus.FALSE in statuses:
            return EvaluationStatus.FALSE
        if EvaluationStatus.UNKNOWN in statuses:
            return EvaluationStatus.UNKNOWN
        return EvaluationStatus.TRUE
    if kind is ConditionKind.ANY:
        if EvaluationStatus.TRUE in statuses:
            return EvaluationStatus.TRUE
        if EvaluationStatus.UNKNOWN in statuses:
            return EvaluationStatus.UNKNOWN
        return EvaluationStatus.FALSE
    raise ValueError(f"unsupported compound condition kind: {kind}")


def _boolean_status(value: bool) -> EvaluationStatus:
    return EvaluationStatus.TRUE if value else EvaluationStatus.FALSE


def _unique_fact_ids(condition: EvaluatedCondition, attribute: str) -> tuple[str, ...]:
    """Collect fact IDs in deterministic condition-tree traversal order."""
    identifiers = list(getattr(condition, attribute))
    for child in condition.children:
        identifiers.extend(_unique_fact_ids(child, attribute))
    return tuple(dict.fromkeys(identifiers))
