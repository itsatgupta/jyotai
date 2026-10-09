"""Focused coverage for the isolated, candidate Career timing package."""

from datetime import UTC, datetime, timedelta
from inspect import getsource

from fastapi.testclient import TestClient

from astrologer.api.timing import get_career_timing_analysis_service
from astrologer.astrology.dasha import DashaLord
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.birth.models import BirthInput
from astrologer.composition.senior_composer import SeniorAstrologerComposer
from astrologer.main import create_app
from astrologer.timing_rules.evaluator import CareerTimingRuleEvaluator
from astrologer.timing_rules.models import (
    CareerTimingRequest,
    MahadashaTimingCondition,
    NatalTimingCondition,
    TimingRuleStatus,
)
from astrologer.timing_rules.registry import CANDIDATE_TIMING_RELEASE, CAREER_TIMING_RULE
from astrologer.timing_rules.service import CareerTimingAnalysisService

_BIRTH = BirthInput(
    birth_date="1978-01-01",
    birth_time="12:00:00",
    timezone="UTC",
    latitude=0,
    longitude=0,
)
_AS_OF = datetime(2026, 1, 1, tzinfo=UTC)
_HORIZON = datetime(2045, 1, 1, tzinfo=UTC)


def _service() -> CareerTimingAnalysisService:
    return CareerTimingAnalysisService(SwissEphemerisProvider())


def _request(as_of: datetime = _AS_OF, horizon_end: datetime = _HORIZON) -> CareerTimingRequest:
    return CareerTimingRequest(
        birth_input=_BIRTH,
        domain="career",
        as_of=as_of,
        horizon_end=horizon_end,
    )


def test_evaluator_preserves_match_false_and_unknown() -> None:
    evaluator = CareerTimingRuleEvaluator()
    matching_natal = NatalTimingCondition(tenth_house_lord=DashaLord.JUPITER, placement_house=4)
    matching_md = MahadashaTimingCondition(lord=DashaLord.JUPITER, start=_AS_OF, end=_HORIZON)
    assert (
        evaluator.evaluate(CAREER_TIMING_RULE, matching_natal, matching_md).status
        is TimingRuleStatus.MATCH
    )
    assert (
        evaluator.evaluate(
            CAREER_TIMING_RULE,
            NatalTimingCondition(tenth_house_lord=DashaLord.JUPITER, placement_house=5),
            matching_md,
        ).status
        is TimingRuleStatus.FALSE
    )
    assert (
        evaluator.evaluate(
            CAREER_TIMING_RULE,
            matching_natal,
            MahadashaTimingCondition(lord=DashaLord.SATURN, start=_AS_OF, end=_HORIZON),
        ).status
        is TimingRuleStatus.FALSE
    )
    assert (
        evaluator.evaluate(
            CAREER_TIMING_RULE,
            NatalTimingCondition(tenth_house_lord=None, placement_house=4),
            matching_md,
        ).status
        is TimingRuleStatus.UNKNOWN
    )
    assert (
        evaluator.evaluate(
            CAREER_TIMING_RULE,
            matching_natal,
            MahadashaTimingCondition(lord=DashaLord.JUPITER, start=None, end=_HORIZON),
        ).status
        is TimingRuleStatus.UNKNOWN
    )


def test_career_timing_enumerates_clipped_broad_md_windows_and_provenance() -> None:
    result = _service().analyze(_request())
    assert result.timing_release_status.value == "candidate_admitted"
    assert result.timing_answerability_established is True
    assert result.windows
    assert all(item.mahadasha_lord is DashaLord.JUPITER for item in result.windows)
    assert all(item.source_interval.start <= item.effective_window.start for item in result.windows)
    assert all(item.effective_window.end <= item.source_interval.end for item in result.windows)
    assert result.windows[0].effective_window.start == _AS_OF
    assert tuple(item.effective_window.start for item in result.windows) == tuple(
        sorted(item.effective_window.start for item in result.windows)
    )
    assert result.precision.value == "BROAD_PERIOD"
    assert result.evidence[0].source.verse == "87"
    assert "printed p. 439" in result.evidence[0].source.page_locator
    assert "promotion" in result.deterministic_wording
    assert "government role" in result.deterministic_wording


def test_end_boundary_and_no_matching_horizon_do_not_establish_answerability() -> None:
    initial = _service().analyze(_request())
    source_end = initial.windows[0].source_interval.end
    result = _service().analyze(_request(source_end, source_end + timedelta(days=365)))
    assert result.timing_answerability_established is False
    assert result.windows == ()
    assert all(item.status is not TimingRuleStatus.MATCH for item in result.evidence)


def test_governed_timing_api_is_additive_and_does_not_expose_llm_timing() -> None:
    app = create_app()
    service = _service()
    app.dependency_overrides[get_career_timing_analysis_service] = lambda: service
    client = TestClient(app)
    response = client.post(
        "/api/v1/timing/analyze",
        json={
            "birth_input": {
                "birth_date": "1978-01-01",
                "birth_time": "12:00:00",
                "timezone": "UTC",
                "latitude": 0,
                "longitude": 0,
            },
            "domain": "career",
            "as_of": _AS_OF.isoformat(),
            "horizon_end": _HORIZON.isoformat(),
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["timing_answerability_established"] is True
    assert body["precision"] == "BROAD_PERIOD"
    assert "antardasha" not in body["windows"][0]
    response_text = str(body).lower()
    assert "guaranteed promotion" not in response_text
    assert "government job" not in response_text
    assert "salary increase" not in response_text
    assert "job change certainty" not in response_text
    assert "timing_rules" not in getsource(SeniorAstrologerComposer)
    assert CANDIDATE_TIMING_RELEASE.activated_at is None
