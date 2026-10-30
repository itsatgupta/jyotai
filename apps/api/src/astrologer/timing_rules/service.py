"""Application-owned Career timing analysis over deterministic Vimshottari facts."""
# ruff: noqa: E501

import logging
from datetime import UTC

from astrologer.application.timing import VimshottariTimingRequest, VimshottariTimingService
from astrologer.astrology.chart import ChartEngine
from astrologer.astrology.dasha import DashaLord
from astrologer.astrology.derived_facts import DerivedFactsEngine
from astrologer.astrology.ephemeris import EphemerisProvider
from astrologer.astrology.intervals import TimeInterval
from astrologer.timing_rules.dignity import TimingDignityProjector
from astrologer.timing_rules.evaluator import CareerTimingRuleEvaluator
from astrologer.timing_rules.models import (
    AntardashaTimingCondition,
    CareerTimingCandidateReleaseV2,
    CareerTimingCandidateReleaseV89,
    CareerTimingEvidence,
    CareerTimingRequest,
    CareerTimingResponse,
    CareerTimingRule,
    CareerTimingWindow,
    MahadashaTimingCondition,
    MoonVenusCareerTimingEvidence,
    MoonVenusOwnExaltationCareerTimingRule,
    MoonVenusOwnExaltationTimingSourceRecord,
    NatalTimingCondition,
    NinthLordInTenthCareerTimingEvidence,
    NinthLordTenthPlacementTimingCondition,
    ProductionCareerTimingReleaseV2,
    ProductionTimingRegistryRelease,
    TimingPrecision,
    TimingRuleStatus,
    TimingSourceRecord,
    VenusDignityTimingCondition,
)
from astrologer.timing_rules.registry import get_active_timing_release

_V1_WHY_THIS_PERIOD_APPLIES = (
    "Your D1 tenth-house lord is placed in the fourth house, and this period corresponds to "
    "the Vimshottari Mahadasha of that tenth-house lord."
)
_V2_WHY_THIS_PERIOD_APPLIES = (
    "This sub-period corresponds to Moon Mahadasha and Venus Antardasha, with natal Venus "
    "in its own sign or exaltation sign."
)

_LOGGER = logging.getLogger(__name__)


class CareerTimingAnalysisService:
    """Evaluate only the explicitly active production Career release; no LLM is involved."""

    def __init__(
        self,
        provider: EphemerisProvider,
        *,
        chart_engine: ChartEngine | None = None,
        derived_facts_engine: DerivedFactsEngine | None = None,
        timing_service: VimshottariTimingService | None = None,
        evaluator: CareerTimingRuleEvaluator | None = None,
        timing_release: ProductionTimingRegistryRelease
        | ProductionCareerTimingReleaseV2
        | CareerTimingCandidateReleaseV2
        | CareerTimingCandidateReleaseV89
        | None = None,
    ) -> None:
        self._chart_engine = chart_engine or ChartEngine(provider)
        self._derived_facts_engine = derived_facts_engine or DerivedFactsEngine()
        self._timing_service = timing_service or VimshottariTimingService(
            provider, self._chart_engine
        )
        self._evaluator = evaluator or CareerTimingRuleEvaluator()
        self._timing_release = timing_release or get_active_timing_release()

    def analyze(self, request: CareerTimingRequest) -> CareerTimingResponse:
        """Return source MD intervals plus their requested-horizon intersections."""
        _LOGGER.info("career_timing_start release=%s", self._timing_release.release_id)
        if isinstance(self._timing_release, CareerTimingCandidateReleaseV89):
            return self._analyze_ninth_lord_in_tenth_candidate(request)
        if isinstance(
            self._timing_release,
            (CareerTimingCandidateReleaseV2, ProductionCareerTimingReleaseV2),
        ):
            return self._analyze_mixed_release_v2(request)
        timing_facts = self._timing_service.build(
            VimshottariTimingRequest(
                birth_input=request.birth_input,
                as_of=request.as_of,
                horizon_end=request.horizon_end,
            )
        )
        chart = self._chart_engine.calculate(request.birth_input)
        derived = self._derived_facts_engine.calculate(chart)
        values = {fact.fact_id: fact.value for fact in derived.facts}
        natal = NatalTimingCondition(
            tenth_house_lord=_dasha_lord(values.get("jyotish.d1.house.10.lord")),
            placement_house=_house_number(values.get("jyotish.d1.house_lord.10.placement_house")),
        )
        horizon = TimeInterval(
            start=request.as_of.astimezone(UTC), end=request.horizon_end.astimezone(UTC)
        )
        rule = self._timing_release.rules[0]
        evidence: list[CareerTimingEvidence] = []
        windows: list[CareerTimingWindow] = []
        for period in timing_facts.timeline:
            mahadasha = MahadashaTimingCondition(
                lord=period.planet, start=period.start, end=period.end
            )
            evaluation = self._evaluator.evaluate(rule, natal, mahadasha)
            evidence.append(
                CareerTimingEvidence(
                    rule_id=rule.rule_id,
                    status=evaluation.status,
                    source=self._timing_release.source,
                    natal_condition=natal,
                    mahadasha=mahadasha,
                    timing_answerability_established=False,
                    reviewed_statement=self._timing_release.source.reviewed_interpretation,
                    exclusions=rule.exclusions,
                )
            )
            if evaluation.status is TimingRuleStatus.MATCH:
                source_interval = TimeInterval(start=period.start, end=period.end)
                effective_window = source_interval.intersection(horizon)
                if effective_window is not None:
                    windows.append(
                        CareerTimingWindow(
                            rule_id=rule.rule_id,
                            precision=rule.precision,
                            source_interval=source_interval,
                            effective_window=effective_window,
                            reviewed_statement=self._timing_release.source.reviewed_interpretation,
                            why_this_period_applies=_V1_WHY_THIS_PERIOD_APPLIES,
                            limitations=rule.exclusions,
                            source=self._timing_release.source,
                            dasha_scope="Vimshottari Mahadasha",
                            mahadasha_lord=period.planet,
                        )
                    )
        answerable = bool(windows)
        evidence = [
            item.model_copy(update={"timing_answerability_established": answerable})
            for item in evidence
        ]
        ordered_windows = tuple(
            sorted(
                windows,
                key=lambda item: (item.effective_window.start, item.effective_window.end),
            )
        )
        return CareerTimingResponse(
            timing_release_id=self._timing_release.release_id,
            timing_release_version=self._timing_release.release_version,
            timing_release_status=self._timing_release.status,
            timing_answerability_established=answerable,
            precision=rule.precision,
            precisions=(rule.precision,),
            evidence=tuple(evidence),
            windows=ordered_windows,
            reviewed_statement=self._timing_release.source.reviewed_interpretation,
            limitations=rule.exclusions,
            deterministic_wording=_wording(ordered_windows, answerable),
        )

    def _analyze_ninth_lord_in_tenth_candidate(
        self, request: CareerTimingRequest
    ) -> CareerTimingResponse:
        """Evaluate the v.89 candidate without admitting it to production or Ask."""
        assert isinstance(self._timing_release, CareerTimingCandidateReleaseV89)
        timing_facts = self._timing_service.build(
            VimshottariTimingRequest(
                birth_input=request.birth_input,
                as_of=request.as_of,
                horizon_end=request.horizon_end,
            )
        )
        chart = self._chart_engine.calculate(request.birth_input)
        values = {
            fact.fact_id: fact.value for fact in self._derived_facts_engine.calculate(chart).facts
        }
        natal = NinthLordTenthPlacementTimingCondition(
            ninth_house_lord=_dasha_lord(values.get("jyotish.d1.house.9.lord")),
            placement_house=_house_number(values.get("jyotish.d1.house_lord.9.placement_house")),
        )
        rule = self._timing_release.rules[0]
        horizon = TimeInterval(
            start=request.as_of.astimezone(UTC), end=request.horizon_end.astimezone(UTC)
        )
        evidence: list[NinthLordInTenthCareerTimingEvidence] = []
        windows: list[CareerTimingWindow] = []
        for period in timing_facts.timeline:
            mahadasha = MahadashaTimingCondition(
                lord=period.planet, start=period.start, end=period.end
            )
            evaluation = self._evaluator.evaluate_ninth_lord_in_tenth_mahadasha(
                rule, natal, mahadasha
            )
            source_interval = (
                TimeInterval(start=period.start, end=period.end)
                if evaluation.status is TimingRuleStatus.MATCH
                else None
            )
            effective_window = source_interval.intersection(horizon) if source_interval else None
            evidence.append(
                NinthLordInTenthCareerTimingEvidence(
                    rule_id=rule.rule_id,
                    status=evaluation.status,
                    source=self._timing_release.source,
                    natal_condition=natal,
                    mahadasha=mahadasha,
                    source_interval=source_interval,
                    effective_window=effective_window,
                    timing_answerability_established=False,
                    reviewed_statement=self._timing_release.source.reviewed_interpretation,
                    exclusions=rule.exclusions,
                )
            )
            if effective_window is not None and source_interval is not None:
                windows.append(
                    CareerTimingWindow(
                        rule_id=rule.rule_id,
                        precision=rule.precision,
                        source_interval=source_interval,
                        effective_window=effective_window,
                        reviewed_statement=self._timing_release.source.reviewed_interpretation,
                        why_this_period_applies=(
                            "Your D1 ninth-house lord is placed in the tenth house, and this "
                            "period corresponds to the Vimshottari Mahadasha of that ninth-house lord."
                        ),
                        limitations=rule.exclusions,
                        source=self._timing_release.source,
                        dasha_scope="Vimshottari Mahadasha",
                        mahadasha_lord=period.planet,
                    )
                )
        answerable = bool(windows)
        established = tuple(
            item.model_copy(update={"timing_answerability_established": answerable})
            for item in evidence
        )
        ordered_windows = tuple(
            sorted(
                windows, key=lambda item: (item.effective_window.start, item.effective_window.end)
            )
        )
        return CareerTimingResponse(
            timing_release_id=self._timing_release.release_id,
            timing_release_version=self._timing_release.release_version,
            timing_release_status=self._timing_release.status,
            timing_answerability_established=answerable,
            precision=rule.precision,
            precisions=(rule.precision,),
            evidence=established,
            windows=ordered_windows,
            reviewed_statement=self._timing_release.source.reviewed_interpretation,
            limitations=rule.exclusions,
            deterministic_wording=(
                "Candidate-only source-governed status-related timing context is available. "
                "It does not establish employment, promotion, government position, salary or wealth "
                "increase, authority acquisition, an exact event date, or predictive certainty."
                if answerable
                else "Candidate-only source-governed timing context is not available for this requested "
                "horizon. It does not establish employment, promotion, government position, salary or "
                "wealth increase, authority acquisition, an exact event date, or predictive certainty."
            ),
        )

    def _analyze_mixed_release_v2(self, request: CareerTimingRequest) -> CareerTimingResponse:
        """Evaluate the independently governed v1/v2 rules without ranking or synthesis."""
        assert isinstance(
            self._timing_release,
            (CareerTimingCandidateReleaseV2, ProductionCareerTimingReleaseV2),
        )
        timing_facts = self._timing_service.build(
            VimshottariTimingRequest(
                birth_input=request.birth_input,
                as_of=request.as_of,
                horizon_end=request.horizon_end,
            )
        )
        chart = self._chart_engine.calculate(request.birth_input)
        values = {
            fact.fact_id: fact.value for fact in self._derived_facts_engine.calculate(chart).facts
        }
        natal = NatalTimingCondition(
            tenth_house_lord=_dasha_lord(values.get("jyotish.d1.house.10.lord")),
            placement_house=_house_number(values.get("jyotish.d1.house_lord.10.placement_house")),
        )
        dignity = {
            fact.fact_id: fact.value for fact in TimingDignityProjector().project(values).facts
        }
        venus_dignity = VenusDignityTimingCondition(
            own_sign=dignity.get("jyotish.d1.planet.venus.own_sign"),
            exaltation_sign=dignity.get("jyotish.d1.planet.venus.exaltation_sign"),
        )
        v1_rule = next(
            rule for rule in self._timing_release.rules if isinstance(rule, CareerTimingRule)
        )
        v2_rule = next(
            rule
            for rule in self._timing_release.rules
            if isinstance(rule, MoonVenusOwnExaltationCareerTimingRule)
        )
        v1_source = next(
            source
            for source in self._timing_release.sources
            if isinstance(source, TimingSourceRecord)
        )
        v2_source = next(
            source
            for source in self._timing_release.sources
            if isinstance(source, MoonVenusOwnExaltationTimingSourceRecord)
        )
        horizon = TimeInterval(
            start=request.as_of.astimezone(UTC), end=request.horizon_end.astimezone(UTC)
        )
        evidence: list[CareerTimingEvidence | MoonVenusCareerTimingEvidence] = []
        windows: list[CareerTimingWindow] = []
        for period in timing_facts.timeline:
            md = MahadashaTimingCondition(lord=period.planet, start=period.start, end=period.end)
            v1_evaluation = self._evaluator.evaluate(v1_rule, natal, md)
            evidence.append(
                CareerTimingEvidence(
                    rule_id=v1_rule.rule_id,
                    status=v1_evaluation.status,
                    source=v1_source,
                    natal_condition=natal,
                    mahadasha=md,
                    timing_answerability_established=False,
                    reviewed_statement=v1_source.reviewed_interpretation,
                    exclusions=v1_rule.exclusions,
                )
            )
            if v1_evaluation.status is TimingRuleStatus.MATCH:
                source_interval = TimeInterval(start=period.start, end=period.end)
                effective_window = source_interval.intersection(horizon)
                if effective_window is not None:
                    windows.append(
                        CareerTimingWindow(
                            rule_id=v1_rule.rule_id,
                            precision=v1_rule.precision,
                            source_interval=source_interval,
                            effective_window=effective_window,
                            reviewed_statement=v1_source.reviewed_interpretation,
                            why_this_period_applies=_V1_WHY_THIS_PERIOD_APPLIES,
                            limitations=v1_rule.exclusions,
                            source=v1_source,
                            dasha_scope="Vimshottari Mahadasha",
                            mahadasha_lord=period.planet,
                        )
                    )
            for period_ad in period.antardashas:
                ad = AntardashaTimingCondition(
                    lord=period_ad.antardasha_lord, start=period_ad.start, end=period_ad.end
                )
                evaluation = self._evaluator.evaluate_moon_venus_own_or_exaltation(
                    v2_rule, md, ad, venus_dignity
                )
                source_interval = TimeInterval(start=period_ad.start, end=period_ad.end)
                effective_window = (
                    source_interval.intersection(horizon)
                    if evaluation.status is TimingRuleStatus.MATCH
                    else None
                )
                evidence.append(
                    MoonVenusCareerTimingEvidence(
                        rule_id=v2_rule.rule_id,
                        status=evaluation.status,
                        source=v2_source,
                        mahadasha=md,
                        antardasha=ad,
                        venus_dignity=venus_dignity,
                        source_interval=source_interval
                        if evaluation.status is TimingRuleStatus.MATCH
                        else None,
                        effective_window=effective_window,
                        timing_answerability_established=False,
                        reviewed_statement=v2_source.reviewed_interpretation,
                        exclusions=v2_rule.exclusions,
                    )
                )
                if effective_window is not None:
                    windows.append(
                        CareerTimingWindow(
                            rule_id=v2_rule.rule_id,
                            precision=v2_rule.precision,
                            source_interval=source_interval,
                            effective_window=effective_window,
                            reviewed_statement=v2_source.reviewed_interpretation,
                            why_this_period_applies=_V2_WHY_THIS_PERIOD_APPLIES,
                            limitations=v2_rule.exclusions,
                            source=v2_source,
                            dasha_scope="Vimshottari Moon Mahadasha / Venus Antardasha",
                            mahadasha_lord=period.planet,
                            antardasha_lord=period_ad.antardasha_lord,
                        )
                    )
        answerable = bool(windows) or any(
            isinstance(item, MoonVenusCareerTimingEvidence) and item.effective_window is not None
            for item in evidence
        )
        established = tuple(
            item.model_copy(update={"timing_answerability_established": answerable})
            for item in evidence
        )
        return CareerTimingResponse(
            timing_release_id=self._timing_release.release_id,
            timing_release_version=self._timing_release.release_version,
            timing_release_status=self._timing_release.status,
            timing_answerability_established=answerable,
            precision=None,
            precisions=(TimingPrecision.BROAD_PERIOD, TimingPrecision.SUB_PERIOD),
            evidence=established,
            windows=tuple(
                sorted(
                    windows,
                    key=lambda item: (
                        item.effective_window.start,
                        item.effective_window.end,
                        item.precision.value,
                        item.rule_id,
                    ),
                )
            ),
            reviewed_statement="Production release contains independently governed v1 and v2 evidence.",
            limitations=tuple(dict.fromkeys(v1_rule.exclusions + v2_rule.exclusions)),
            deterministic_wording=(
                "Independently governed Career timing evidence is available without ranking or "
                "confirmation between rules. It does not guarantee employment, promotion, office, "
                "authority, income, a government role, salary change, or a specific event."
            ),
        )


def _dasha_lord(value: bool | int | str | None) -> DashaLord | None:
    if not isinstance(value, str):
        return None
    try:
        return DashaLord(value)
    except ValueError:
        return None


def _house_number(value: bool | int | str | None) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 12:
        return value
    return None


def _wording(windows: tuple[CareerTimingWindow, ...], answerable: bool) -> str:
    limitation = (
        "This identifies source-governed Career timing context only. It does not guarantee "
        "employment, promotion, office, authority, income, a government role, or a specific event."
    )
    if not answerable:
        return (
            "Reviewed Career timing context is not available for this requested horizon. "
            f"{limitation}"
        )
    periods = "; ".join(
        f"{item.effective_window.start.isoformat()} – {item.effective_window.end.isoformat()}"
        for item in windows
    )
    return (
        "Reviewed Career timing context is available for this chart. Because the D1 tenth-house "
        "lord is placed in the fourth house, the reviewed BPHS Dasha-phala passage treats the "
        "Mahadasha of that tenth-house lord as a rājya-related period. Supported broad timing "
        f"period: {periods}. {limitation}"
    )
