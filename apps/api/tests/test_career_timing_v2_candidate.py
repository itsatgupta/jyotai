"""Focused candidate-only coverage for the reviewed Moon/Venus v.140 rule."""

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
    AntardashaTimingCondition,
    CareerTimingRequest,
    MahadashaTimingCondition,
    MoonVenusCareerTimingEvidence,
    TimingPrecision,
    TimingRuleStatus,
    VenusDignityTimingCondition,
)
from astrologer.timing_rules.registry import (
    ACTIVE_TIMING_RELEASE_POINTER,
    CANDIDATE_CAREER_TIMING_RELEASE_V2,
    CANDIDATE_TIMING_RELEASE,
    MOON_VENUS_OWN_OR_EXALTATION_TIMING_RULE,
    MOON_VENUS_OWN_OR_EXALTATION_TIMING_SOURCE,
    PRODUCTION_CAREER_TIMING_RELEASE,
)
from astrologer.timing_rules.service import CareerTimingAnalysisService

_BIRTH = BirthInput(
    birth_date="1970-05-01", birth_time="12:00:00", timezone="UTC", latitude=0, longitude=0
)
_MD = MahadashaTimingCondition(
    lord=DashaLord.MOON,
    start=datetime(2057, 1, 1, tzinfo=UTC),
    end=datetime(2067, 1, 1, tzinfo=UTC),
)
_AD = AntardashaTimingCondition(
    lord=DashaLord.VENUS,
    start=datetime(2058, 7, 3, tzinfo=UTC),
    end=datetime(2060, 3, 3, tzinfo=UTC),
)


def _evaluate(
    own: bool | None,
    exaltation: bool | None,
    *,
    md: DashaLord = DashaLord.MOON,
    ad: DashaLord = DashaLord.VENUS,
) -> TimingRuleStatus:
    return (
        CareerTimingRuleEvaluator()
        .evaluate_moon_venus_own_or_exaltation(
            MOON_VENUS_OWN_OR_EXALTATION_TIMING_RULE,
            _MD.model_copy(update={"lord": md}),
            _AD.model_copy(update={"lord": ad}),
            VenusDignityTimingCondition(own_sign=own, exaltation_sign=exaltation),
        )
        .status
    )


def test_moon_venus_rule_preserves_required_or_unknown_semantics() -> None:
    assert _evaluate(True, False) is TimingRuleStatus.MATCH
    assert _evaluate(False, True) is TimingRuleStatus.MATCH
    assert _evaluate(True, None) is TimingRuleStatus.MATCH
    assert _evaluate(False, None) is TimingRuleStatus.UNKNOWN
    assert _evaluate(False, False) is TimingRuleStatus.FALSE
    assert _evaluate(None, None) is TimingRuleStatus.UNKNOWN
    assert _evaluate(True, True, md=DashaLord.SUN) is TimingRuleStatus.FALSE
    assert _evaluate(True, True, ad=DashaLord.SUN) is TimingRuleStatus.FALSE


def test_candidate_sub_period_keeps_canonical_ad_and_clips_only_effective_window() -> None:
    service = CareerTimingAnalysisService(
        SwissEphemerisProvider(), timing_release=CANDIDATE_CAREER_TIMING_RELEASE_V2
    )
    full = service.analyze(
        CareerTimingRequest(
            birth_input=_BIRTH,
            domain="career",
            as_of=datetime(2026, 1, 1, tzinfo=UTC),
            horizon_end=datetime(2090, 1, 1, tzinfo=UTC),
        )
    )
    match = next(
        item
        for item in full.evidence
        if isinstance(item, MoonVenusCareerTimingEvidence) and item.status is TimingRuleStatus.MATCH
    )
    assert match.precision is TimingPrecision.SUB_PERIOD
    assert match.mahadasha.lord is DashaLord.MOON
    assert match.antardasha.lord is DashaLord.VENUS
    assert match.source_interval is not None
    assert match.effective_window == match.source_interval
    clipped = service.analyze(
        CareerTimingRequest(
            birth_input=_BIRTH,
            domain="career",
            as_of=match.source_interval.start + timedelta(days=10),
            horizon_end=match.source_interval.end - timedelta(days=10),
        )
    )
    clipped_match = next(
        item
        for item in clipped.evidence
        if isinstance(item, MoonVenusCareerTimingEvidence) and item.status is TimingRuleStatus.MATCH
    )
    assert clipped_match.source_interval == match.source_interval
    assert clipped_match.effective_window is not None
    assert clipped_match.effective_window.start == match.source_interval.start + timedelta(days=10)
    assert clipped_match.effective_window.end == match.source_interval.end - timedelta(days=10)


def test_candidate_release_is_immutable_and_production_api_and_llm_remain_v1_only() -> None:
    assert CANDIDATE_CAREER_TIMING_RELEASE_V2.rules[0] == PRODUCTION_CAREER_TIMING_RELEASE.rules[0]
    assert CANDIDATE_CAREER_TIMING_RELEASE_V2.rules[1] == MOON_VENUS_OWN_OR_EXALTATION_TIMING_RULE
    assert (
        CANDIDATE_CAREER_TIMING_RELEASE_V2.sources[1] == MOON_VENUS_OWN_OR_EXALTATION_TIMING_SOURCE
    )
    assert CANDIDATE_TIMING_RELEASE.release_id == "jyotish.timing.career.candidate.v1"
    assert ACTIVE_TIMING_RELEASE_POINTER.release_id == "jyotish.timing.production.career@v1"
    assert PRODUCTION_CAREER_TIMING_RELEASE.rules == (CANDIDATE_CAREER_TIMING_RELEASE_V2.rules[0],)
    app = create_app()
    app.dependency_overrides[get_career_timing_analysis_service] = lambda: (
        CareerTimingAnalysisService(SwissEphemerisProvider())
    )
    body = (
        TestClient(app)
        .post(
            "/api/v1/timing/analyze",
            json={
                "birth_input": _BIRTH.model_dump(mode="json"),
                "domain": "career",
                "as_of": "2026-01-01T00:00:00+00:00",
                "horizon_end": "2045-01-01T00:00:00+00:00",
            },
        )
        .json()
    )
    assert body["timing_release_id"] == "jyotish.timing.production.career@v1"
    assert "moon_md.venus_ad" not in str(body)
    assert "MoonVenus" not in getsource(SeniorAstrologerComposer)
