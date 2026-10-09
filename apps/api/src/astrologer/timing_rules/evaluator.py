"""Three-valued evaluator for the single, bounded Career timing rule."""

from astrologer.timing_rules.models import (
    CareerTimingEvaluation,
    CareerTimingRule,
    MahadashaTimingCondition,
    NatalTimingCondition,
    TimingRuleStatus,
)


class CareerTimingRuleEvaluator:
    """Evaluate supplied deterministic facts without changing UNKNOWN to FALSE."""

    def evaluate(
        self,
        rule: CareerTimingRule,
        natal: NatalTimingCondition,
        mahadasha: MahadashaTimingCondition,
    ) -> CareerTimingEvaluation:
        required = (
            natal.tenth_house_lord,
            natal.placement_house,
            mahadasha.lord,
            mahadasha.start,
            mahadasha.end,
        )
        if any(value is None for value in required):
            status = TimingRuleStatus.UNKNOWN
        elif natal.placement_house != 4 or mahadasha.lord != natal.tenth_house_lord:
            status = TimingRuleStatus.FALSE
        else:
            status = TimingRuleStatus.MATCH
        return CareerTimingEvaluation(
            rule_id=rule.rule_id,
            status=status,
            natal_condition=natal,
            mahadasha=mahadasha,
        )
