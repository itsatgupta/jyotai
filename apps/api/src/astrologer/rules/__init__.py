"""Declarative, deterministic rule-framework primitives.

This package evaluates supplied facts only. It does not calculate astrology.
"""

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
    RuleSet,
)

__all__ = [
    "RULE_FRAMEWORK_VERSION",
    "ConditionDefinition",
    "ConditionKind",
    "ConditionOperation",
    "EvaluationStatus",
    "Fact",
    "FactSet",
    "RuleDefinition",
    "RuleEffect",
    "RuleEvaluator",
    "RuleLoadError",
    "RuleLoader",
    "RuleSet",
]
