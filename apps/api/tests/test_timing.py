"""Deterministic factual timing-foundation and interval-contract tests."""

from datetime import UTC, datetime, timedelta, timezone
from inspect import getsource

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from astrologer.api.timing import get_vimshottari_timing_service
from astrologer.application.timing import (
    TimingEvidenceLevel,
    TimingPrecision,
    VimshottariTimingRequest,
    VimshottariTimingService,
)
from astrologer.astrology.intervals import TimeInterval, sort_intervals
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.birth.models import BirthInput
from astrologer.main import create_app

_BIRTH = BirthInput(
    birth_date="1990-01-15",
    birth_time="09:30:00",
    timezone="Asia/Kolkata",
    latitude=19.076,
    longitude=72.8777,
    place_name="Mumbai",
)
_AS_OF = datetime(2026, 10, 2, 12, tzinfo=UTC)
_HORIZON = datetime(2040, 10, 2, 12, tzinfo=UTC)
_BIRTH_REQUEST = {
    "birth_date": "1990-01-15",
    "birth_time": "09:30:00",
    "timezone": "Asia/Kolkata",
    "latitude": 19.076,
    "longitude": 72.8777,
    "place_name": "Mumbai",
}


def _request(
    as_of: datetime = _AS_OF, horizon_end: datetime = _HORIZON
) -> VimshottariTimingRequest:
    return VimshottariTimingRequest(
        birth_input=_BIRTH,
        as_of=as_of,
        horizon_end=horizon_end,
    )


def _facts():
    return VimshottariTimingService(SwissEphemerisProvider()).build(_request())


def test_complete_md_timeline_is_ordered_contiguous_and_matches_current_md() -> None:
    facts = _facts()
    timeline = facts.timeline

    assert timeline
    assert tuple(item.start for item in timeline) == tuple(sorted(item.start for item in timeline))
    assert all(left.end == right.start for left, right in zip(timeline, timeline[1:], strict=False))
    assert all(item.start < item.end for item in timeline)
    current = next(item for item in timeline if item.start <= _AS_OF < item.end)
    assert current.planet is facts.current.mahadasha_lord
    assert current.start == facts.current.mahadasha_start
    assert current.end == facts.current.mahadasha_end


def test_complete_ads_are_ordered_nested_contiguous_and_match_current_ad() -> None:
    facts = _facts()
    for mahadasha in facts.timeline:
        ads = mahadasha.antardashas
        assert len(ads) == 9
        assert tuple(item.start for item in ads) == tuple(sorted(item.start for item in ads))
        assert all(item.mahadasha_lord is mahadasha.planet for item in ads)
        assert all(mahadasha.start <= item.start < item.end <= mahadasha.end for item in ads)
        assert ads[0].start == mahadasha.start
        assert ads[-1].end == mahadasha.end
        assert all(left.end == right.start for left, right in zip(ads, ads[1:], strict=False))

    current_md = next(item for item in facts.timeline if item.start <= _AS_OF < item.end)
    ads = current_md.antardashas
    current_ad = next(item for item in ads if item.start <= _AS_OF < item.end)
    assert current_ad.antardasha_lord is facts.current.antardasha_lord
    assert current_ad.start == facts.current.antardasha_start
    assert current_ad.end == facts.current.antardasha_end


def test_as_of_timezone_normalization_and_historical_future_reproducibility() -> None:
    service = VimshottariTimingService(SwissEphemerisProvider())
    local_as_of = datetime(2026, 10, 2, 17, 30, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    local_horizon = datetime(2040, 10, 2, 17, 30, tzinfo=timezone(timedelta(hours=5, minutes=30)))

    facts = service.build(_request(local_as_of, local_horizon))
    historical_request = _request(
        datetime(2001, 1, 1, tzinfo=UTC), datetime(2005, 1, 1, tzinfo=UTC)
    )
    historical = service.build(historical_request)
    future_request = _request(datetime(2050, 1, 1, tzinfo=UTC), datetime(2055, 1, 1, tzinfo=UTC))

    assert facts.normalized_as_of_utc == _AS_OF
    assert facts.normalized_horizon_end_utc == _HORIZON
    assert historical == service.build(historical_request)
    assert service.build(future_request) == service.build(future_request)


def test_exact_boundary_selects_the_new_half_open_period() -> None:
    service = VimshottariTimingService(SwissEphemerisProvider())
    initial = service.build(_request())
    boundary = initial.current.antardasha_end
    facts = service.build(_request(boundary, boundary + timedelta(days=365)))

    assert facts.current.antardasha_start == boundary
    assert facts.current.antardasha_lord is not initial.current.antardasha_lord


def test_timing_contract_is_factual_availability_not_interpretation() -> None:
    facts = _facts()

    assert facts.timing_fact_contract.contract_id == "jyotish.timing.vimshottari@v1"
    assert facts.timing_fact_contract.interval_boundary_convention == "[start,end)"
    assert facts.timing_fact_contract.pratyantardasha_status == "deferred"
    assert facts.evidence_status.level is TimingEvidenceLevel.MAHADASHA_ANTARDASHA_AVAILABLE
    assert facts.evidence_status.precision is TimingPrecision.SUB_PERIOD
    assert facts.evidence_status.timing_answerability_established is False


def test_request_rejects_naive_reversed_and_unbounded_horizons() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        _request(datetime(2026, 10, 2, 12), _HORIZON)
    with pytest.raises(ValidationError, match="after as_of"):
        _request(_AS_OF, _AS_OF)
    with pytest.raises(ValidationError, match="120 dasha years"):
        _request(_AS_OF, _AS_OF + timedelta(days=365.25 * 121))


def test_factual_timing_api_is_additive_and_does_not_depend_on_governance_or_llm() -> None:
    app = create_app()
    app.dependency_overrides[get_vimshottari_timing_service] = lambda: VimshottariTimingService(
        SwissEphemerisProvider()
    )
    response = TestClient(app).post(
        "/api/v1/timing/vimshottari",
        json={
            "birth_input": _BIRTH_REQUEST,
            "as_of": _AS_OF.isoformat(),
            "horizon_end": _HORIZON.isoformat(),
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["timing_fact_contract"]["contract_id"] == "jyotish.timing.vimshottari@v1"
    assert payload["evidence_status"]["timing_answerability_established"] is False
    assert "prediction" not in str(payload).lower()
    source = getsource(VimshottariTimingService)
    assert "FactContract" not in source
    assert "EvidenceBuilder" not in source
    assert "LLM" not in source


def test_interval_utility_uses_half_open_boundaries_and_deterministic_ordering() -> None:
    base = TimeInterval(start=_AS_OF, end=_AS_OF + timedelta(days=10))
    full = TimeInterval(start=_AS_OF, end=_AS_OF + timedelta(days=10))
    partial = TimeInterval(start=_AS_OF + timedelta(days=5), end=_AS_OF + timedelta(days=15))
    touching = TimeInterval(start=_AS_OF + timedelta(days=10), end=_AS_OF + timedelta(days=11))
    earlier = TimeInterval(start=_AS_OF - timedelta(days=2), end=_AS_OF - timedelta(days=1))

    assert base.contains(_AS_OF)
    assert not base.contains(base.end)
    assert base.intersection(full) == base
    assert base.intersection(partial) == TimeInterval(
        start=_AS_OF + timedelta(days=5), end=_AS_OF + timedelta(days=10)
    )
    assert base.intersection(touching) is None
    assert base.clip(partial) == base.intersection(partial)
    assert sort_intervals((base, earlier, touching)) == (earlier, base, touching)
    with pytest.raises(ValidationError, match="after start"):
        TimeInterval(start=_AS_OF, end=_AS_OF)
    with pytest.raises(ValidationError, match="normalized to UTC"):
        TimeInterval(
            start=_AS_OF.astimezone(timezone(timedelta(hours=5, minutes=30))),
            end=_HORIZON,
        )
