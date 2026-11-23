"""Both request paths must cut Dasha periods from the one injected Vimshottari engine."""

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pytest

from astrologer.application import analyze as analyze_module
from astrologer.application import answer_plan as answer_plan_module
from astrologer.application.analyze import (
    DeterministicAnalysisRequest,
    DeterministicAnalysisService,
)
from astrologer.application.answer import AskJyotAIService
from astrologer.application.context import (
    DeterministicAstrologyContextService,
    DeterministicContextRequest,
)
from astrologer.astrology.chart import Chart
from astrologer.astrology.dasha import DashaTimeline, VimshottariDashaEngine
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.birth.models import BirthInput
from astrologer.composition import DeterministicAnswerComposer
from astrologer.evidence import InterpretationEvidenceBuilder
from astrologer.timing_rules.service import CareerTimingAnalysisService

# Synthetic profile shared with test_career_consultation.py; not a real person.
_BIRTH = BirthInput(
    birth_date="1978-01-01", birth_time="12:00:00", timezone="UTC", latitude=0, longitude=0
)
_ZONE = ZoneInfo("Asia/Kolkata")
_AS_OF = datetime(2026, 1, 1, tzinfo=_ZONE)
_YEAR = 2027

Boundary = tuple[str, str, datetime, datetime, datetime, datetime, datetime, datetime]


class _SpyEngine(VimshottariDashaEngine):
    """Real engine that records every full-timeline calculation it performs."""

    def __init__(self) -> None:
        super().__init__()
        self.calculations: list[datetime] = []

    def calculate(self, chart: Chart, through: datetime) -> DashaTimeline:
        self.calculations.append(through)
        return super().calculate(chart, through)


class _ForbiddenEngine:
    def __init__(self, *args: object, **kwargs: object) -> None:
        raise AssertionError("a default VimshottariDashaEngine was constructed")


def _year_bounds() -> tuple[datetime, datetime]:
    start = datetime.combine(date(_YEAR, 1, 1), time.min, tzinfo=_ZONE)
    end = datetime.combine(date(_YEAR + 1, 1, 1), time.min, tzinfo=_ZONE)
    return start, end


def _cut(timeline: DashaTimeline) -> list[Boundary]:
    start, end = _year_bounds()
    rows: list[Boundary] = []
    for major in timeline.mahadashas:
        for minor in major.antardashas:
            lo = max(start, major.start, minor.start)
            hi = min(end, major.end, minor.end)
            if lo < hi:
                rows.append(
                    (
                        major.lord.value,
                        minor.lord.value,
                        major.start,
                        major.end,
                        minor.start,
                        minor.end,
                        lo,
                        hi,
                    )
                )
    return rows


def test_answer_plan_and_dasha_timeline_share_one_injected_engine(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = SwissEphemerisProvider()
    spy = _SpyEngine()
    context_service = DeterministicAstrologyContextService(provider, dasha_engine=spy)
    service = AskJyotAIService(
        DeterministicAnalysisService(context_service),
        InterpretationEvidenceBuilder(),
        DeterministicAnswerComposer(),
        CareerTimingAnalysisService(provider),
    )
    # Neither path may fall back to constructing its own engine.
    monkeypatch.setattr(analyze_module, "VimshottariDashaEngine", _ForbiddenEngine)
    monkeypatch.setattr(answer_plan_module, "VimshottariDashaEngine", _ForbiddenEngine)
    request = DeterministicAnalysisRequest(
        birth_input=_BIRTH, as_of=_AS_OF, question="How will my career be in 2027?"
    )
    _, end = _year_bounds()

    # One reference calculation from the injected engine.
    d1 = context_service.build(DeterministicContextRequest(birth_input=_BIRTH, as_of=_AS_OF)).d1
    reference = spy.calculate(d1, end)
    expected = _cut(reference)
    assert len(expected) == 2  # the 2027 MD/AD transition is exercised

    spy.calculations.clear()
    plan = service.answer(request).answers[0].career_answer_plan
    assert plan is not None
    plan_rows = [
        (
            s.mahadasha_lord,
            s.antardasha_lord,
            s.mahadasha_start,
            s.mahadasha_end,
            s.antardasha_start,
            s.antardasha_end,
            s.effective_start,
            s.effective_end,
        )
        for s in plan.dasha_segments
    ]
    assert spy.calculations, "answer-plan path did not use the injected engine"

    spy.calculations.clear()
    follow_up_rows = _cut(service.dasha_timeline(request, end))
    assert spy.calculations == [end], "dasha_timeline path did not use the injected engine"

    assert plan_rows == expected
    assert follow_up_rows == expected
