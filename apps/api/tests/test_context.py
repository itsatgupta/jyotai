"""Deterministic application-context composition and API tests without rule evidence."""

from datetime import UTC, datetime
from inspect import getsource
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from astrologer.api.context import get_context_service
from astrologer.application.context import (
    DeterministicAstrologyContextService,
    DeterministicContextInputError,
    DeterministicContextRequest,
)
from astrologer.astrology.chart import ChartEngine
from astrologer.astrology.ephemeris import EphemerisResult
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
_AS_OF = datetime(2026, 10, 2, 12, 0, tzinfo=UTC)
_BIRTH_REQUEST = {
    "birth_date": "1990-01-15",
    "birth_time": "09:30:00",
    "timezone": "Asia/Kolkata",
    "latitude": 19.076,
    "longitude": 72.8777,
    "place_name": "Mumbai",
}


def _api_request(as_of: str) -> dict[str, object]:
    return {"birth_input": _BIRTH_REQUEST, "as_of": as_of}


class MoshierReportingProvider(SwissEphemerisProvider):
    """Test adapter that preserves a provider-reported internal ephemeris label."""

    def calculate(self, request: object) -> EphemerisResult:  # type: ignore[override]
        result = super().calculate(request)  # type: ignore[arg-type]
        provider = result.provenance.provider.model_copy(
            update={"ephemeris_data_version": "Moshier internal ephemeris"}
        )
        provenance = result.provenance.model_copy(update={"provider": provider})
        return result.model_copy(update={"provenance": provenance})


def _request(as_of: datetime = _AS_OF) -> DeterministicContextRequest:
    return DeterministicContextRequest(birth_input=_BIRTH, as_of=as_of)


def test_context_composes_existing_deterministic_outputs_from_one_d1() -> None:
    provider = SwissEphemerisProvider()
    chart_engine = ChartEngine(provider)
    service = DeterministicAstrologyContextService(provider, chart_engine=chart_engine)

    with patch.object(chart_engine, "calculate", wraps=chart_engine.calculate) as calculate:
        context = service.build(_request())

    assert calculate.call_count == 1
    assert context.d1.methodology.chart_type == "D1/Rashi"
    assert context.d9.methodology.chart_type == "d9"
    assert context.d10.methodology.chart_type == "d10"
    assert context.active_dasha.mahadasha is not None
    assert context.active_dasha.antardasha is not None
    assert tuple(position.body.value for position in context.transit_snapshot.positions) == (
        "jupiter",
        "saturn",
        "rahu",
        "ketu",
    )
    assert context.derived_facts.provenance.source_chart_methodology == context.d1.methodology
    assert context.derived_facts.provenance.inherited_ephemeris_provenance == context.d1.provenance
    assert context.context_version == "deterministic-astrology-context-v1"


def test_context_normalizes_explicit_non_utc_as_of_and_is_reproducible() -> None:
    requested = datetime.fromisoformat("2026-10-02T17:30:00+05:30")
    service = DeterministicAstrologyContextService(SwissEphemerisProvider())

    first = service.build(_request(requested))
    second = service.build(_request(requested))

    assert first == second
    assert first.requested_as_of == requested
    assert first.normalized_as_of_utc == _AS_OF
    assert first.provenance.requested_as_of == requested
    assert first.provenance.normalized_as_of_utc == _AS_OF
    assert first.active_dasha.instant == _AS_OF
    assert first.transit_snapshot.normalized_utc_instant == _AS_OF


def test_context_rejects_naive_and_pre_birth_as_of() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        _request(datetime(2026, 10, 2, 12, 0))
    with pytest.raises(DeterministicContextInputError, match="before the birth"):
        DeterministicAstrologyContextService(SwissEphemerisProvider()).build(
            _request(datetime(1989, 1, 1, tzinfo=UTC))
        )


def test_context_preserves_provider_reported_moshier_provenance() -> None:
    context = DeterministicAstrologyContextService(MoshierReportingProvider()).build(_request())

    assert (
        context.provenance.d1_ephemeris_provider.ephemeris_data_version
        == "Moshier internal ephemeris"
    )
    assert (
        context.provenance.transit_ephemeris_provider.ephemeris_data_version
        == "Moshier internal ephemeris"
    )


def test_context_has_no_governance_rule_or_llm_dependency() -> None:
    source = getsource(DeterministicAstrologyContextService)

    assert "ProductionCorpusLoader" not in source
    assert "GovernedRuleEvaluator" not in source
    assert "RuleEvaluator" not in source
    assert "LLM" not in source


def test_context_snapshot_api_returns_composed_contract_and_chart_route_is_unchanged() -> None:
    client = TestClient(create_app())
    response = client.post("/api/v1/context/snapshot", json=_api_request(_AS_OF.isoformat()))
    chart_response = client.post("/api/v1/charts/calculate", json=_BIRTH_REQUEST)

    assert response.status_code == 200
    payload = response.json()
    assert payload["context_version"] == "deterministic-astrology-context-v1"
    assert {"d1", "d9", "d10", "active_dasha", "transit_snapshot", "derived_facts"} <= set(payload)
    assert "d2" not in payload
    assert [position["body"] for position in payload["transit_snapshot"]["positions"]] == [
        "jupiter",
        "saturn",
        "rahu",
        "ketu",
    ]
    assert (
        payload["provenance"]["derived_facts_methodology"]["methodology_id"]
        == "jyotish-derived-facts-v1"
    )
    assert payload["provenance"]["transit_methodology"]["methodology_id"] == "transit-v1"
    assert payload["provenance"]["vimshottari_methodology"]["methodology_id"] == "vimshottari-v1"
    assert chart_response.status_code == 200
    assert "d2" in chart_response.json()


@pytest.mark.parametrize(
    ("as_of", "status_code"),
    [
        ("2026-10-02T12:00:00", 422),
        ("1989-01-01T00:00:00Z", 422),
    ],
)
def test_context_snapshot_api_rejects_invalid_times(as_of: str, status_code: int) -> None:
    response = TestClient(create_app()).post("/api/v1/context/snapshot", json=_api_request(as_of))

    assert response.status_code == status_code


def test_context_snapshot_api_rejects_invalid_birth_input() -> None:
    response = TestClient(create_app()).post(
        "/api/v1/context/snapshot",
        json={
            "birth_input": {**_BIRTH_REQUEST, "timezone": "Invalid/Timezone"},
            "as_of": _AS_OF.isoformat(),
        },
    )

    assert response.status_code == 422


def test_context_snapshot_api_hides_provider_failure() -> None:
    class FailingService:
        def build(self, request: DeterministicContextRequest) -> object:
            raise RuntimeError("internal provider detail")

    app = create_app()
    app.dependency_overrides[get_context_service] = FailingService
    response = TestClient(app).post(
        "/api/v1/context/snapshot", json=_api_request(_AS_OF.isoformat())
    )

    assert response.status_code == 503
    assert (
        response.json()["detail"] == "Deterministic context calculation is temporarily unavailable."
    )
