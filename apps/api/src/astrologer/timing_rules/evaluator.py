"""Three-valued evaluator for the single, bounded Career timing rule."""

from astrologer.astrology.dasha import DashaLord
from astrologer.timing_rules.models import (
    AntardashaTimingCondition,
    CareerTimingEvaluation,
    CareerTimingRule,
    MahadashaTimingCondition,
    MoonVenusCareerTimingEvaluation,
    MoonVenusOwnExaltationCareerTimingRule,
    NatalTimingCondition,
    NinthLordInTenthCareerTimingEvaluation,
    NinthLordInTenthMahadashaCareerTimingRule,
    NinthLordTenthPlacementTimingCondition,
    TimingRuleStatus,
    VenusDignityTimingCondition,
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

    def evaluate_moon_venus_own_or_exaltation(
        self,
        rule: MoonVenusOwnExaltationCareerTimingRule,
        mahadasha: MahadashaTimingCondition,
        antardasha: AntardashaTimingCondition,
        venus_dignity: VenusDignityTimingCondition,
    ) -> MoonVenusCareerTimingEvaluation:
        """Evaluate the admitted OR without turning an unavailable dignity fact into false."""
        required_period = (
            mahadasha.lord,
            mahadasha.start,
            mahadasha.end,
            antardasha.lord,
            antardasha.start,
            antardasha.end,
        )
        if mahadasha.lord is not None and mahadasha.lord is not DashaLord.MOON:
            status = TimingRuleStatus.FALSE
        elif antardasha.lord is not None and antardasha.lord is not DashaLord.VENUS:
            status = TimingRuleStatus.FALSE
        elif any(value is None for value in required_period):
            status = TimingRuleStatus.UNKNOWN
        elif venus_dignity.own_sign is True or venus_dignity.exaltation_sign is True:
            status = TimingRuleStatus.MATCH
        elif venus_dignity.own_sign is False and venus_dignity.exaltation_sign is False:
            status = TimingRuleStatus.FALSE
        else:
            status = TimingRuleStatus.UNKNOWN
        return MoonVenusCareerTimingEvaluation(
            rule_id=rule.rule_id,
            status=status,
            mahadasha=mahadasha,
            antardasha=antardasha,
            venus_dignity=venus_dignity,
        )

    def evaluate_ninth_lord_in_tenth_mahadasha(
        self,
        rule: NinthLordInTenthMahadashaCareerTimingRule,
        natal: NinthLordTenthPlacementTimingCondition,
        mahadasha: MahadashaTimingCondition,
    ) -> NinthLordInTenthCareerTimingEvaluation:
        """Evaluate only v.89's ninth-lord/tenth-house clause with three-valued facts."""
        required = (
            natal.ninth_house_lord,
            natal.placement_house,
            mahadasha.lord,
            mahadasha.start,
            mahadasha.end,
        )
        if any(value is None for value in required):
            status = TimingRuleStatus.UNKNOWN
        elif natal.placement_house != 10 or mahadasha.lord != natal.ninth_house_lord:
            status = TimingRuleStatus.FALSE
        else:
            status = TimingRuleStatus.MATCH
        return NinthLordInTenthCareerTimingEvaluation(
            rule_id=rule.rule_id,
            status=status,
            natal_condition=natal,
            mahadasha=mahadasha,
        )
