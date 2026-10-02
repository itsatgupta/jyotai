"""Small synthetic rules used to demonstrate framework wiring only.

They make no Jyotish claim and are not an approved production rule corpus.
"""

from astrologer.rules.models import (
    ConditionDefinition,
    ConditionKind,
    ConditionOperation,
    RuleDefinition,
    RuleEffect,
)

DEMO_RULES = (
    RuleDefinition(
        rule_id="TEST_RULE_ALL_TRUE",
        rule_version="1",
        ruleset_version="task08-demo-v1",
        name="Synthetic all condition",
        domain="test",
        is_synthetic_demo=True,
        condition=ConditionDefinition(
            kind=ConditionKind.ALL,
            children=(
                ConditionDefinition(
                    kind=ConditionKind.LEAF,
                    operation=ConditionOperation.EQUALS,
                    fact_id="test.flag_a",
                    expected_value=True,
                ),
                ConditionDefinition(
                    kind=ConditionKind.LEAF,
                    operation=ConditionOperation.EXISTS,
                    fact_id="test.flag_b",
                ),
            ),
        ),
        effect=RuleEffect(effect_key="test.all_true", label="Synthetic demonstration effect"),
    ),
    RuleDefinition(
        rule_id="TEST_RULE_ANY_TRUE",
        rule_version="1",
        ruleset_version="task08-demo-v1",
        name="Synthetic any condition",
        domain="test",
        is_synthetic_demo=True,
        condition=ConditionDefinition(
            kind=ConditionKind.ANY,
            children=(
                ConditionDefinition(
                    kind=ConditionKind.LEAF,
                    operation=ConditionOperation.EQUALS,
                    fact_id="test.flag_a",
                    expected_value=False,
                ),
                ConditionDefinition(
                    kind=ConditionKind.LEAF,
                    operation=ConditionOperation.EXISTS,
                    fact_id="test.flag_b",
                ),
            ),
        ),
        effect=RuleEffect(effect_key="test.any_true", label="Synthetic demonstration effect"),
    ),
    RuleDefinition(
        rule_id="TEST_RULE_UNKNOWN",
        rule_version="1",
        ruleset_version="task08-demo-v1",
        name="Synthetic unknown condition",
        domain="test",
        is_synthetic_demo=True,
        condition=ConditionDefinition(
            kind=ConditionKind.LEAF,
            operation=ConditionOperation.EQUALS,
            fact_id="test.unavailable",
            expected_value=True,
        ),
        effect=RuleEffect(effect_key="test.unknown", label="Synthetic demonstration effect"),
    ),
)
