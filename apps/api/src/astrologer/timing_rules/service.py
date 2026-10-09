"""Application-owned Career timing analysis over deterministic Vimshottari facts."""

from datetime import UTC

from astrologer.application.timing import VimshottariTimingRequest, VimshottariTimingService
from astrologer.astrology.chart import ChartEngine
from astrologer.astrology.dasha import DashaLord
from astrologer.astrology.derived_facts import DerivedFactsEngine
from astrologer.astrology.ephemeris import EphemerisProvider
from astrologer.astrology.intervals import TimeInterval
from astrologer.timing_rules.evaluator import CareerTimingRuleEvaluator
from astrologer.timing_rules.models import (
    CareerTimingEvidence,
    CareerTimingRequest,
    CareerTimingResponse,
    CareerTimingWindow,
    MahadashaTimingCondition,
    NatalTimingCondition,
    ProductionTimingRegistryRelease,
    TimingRuleStatus,
)
from astrologer.timing_rules.registry import get_active_timing_release


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
        timing_release: ProductionTimingRegistryRelease | None = None,
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
                            source_interval=source_interval,
                            effective_window=effective_window,
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
            evidence=tuple(evidence),
            windows=ordered_windows,
            reviewed_statement=self._timing_release.source.reviewed_interpretation,
            limitations=rule.exclusions,
            deterministic_wording=_wording(ordered_windows, answerable),
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
