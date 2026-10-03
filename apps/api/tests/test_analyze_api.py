"""Coverage for the stateless Task 14 deterministic analysis endpoint."""

from datetime import UTC, datetime
from unittest.mock import Mock

from fastapi.testclient import TestClient

from astrologer.api.analyze import get_analysis_service
from astrologer.application.analyze import (
    DeterministicAnalysisRequest,
    DeterministicAnalysisService,
)
from astrologer.application.context import DeterministicAstrologyContextService
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.main import create_app

_BIRTH_INPUT = {
    "birth_date": "1990-01-15",
    "birth_time": "09:30:00",
    "timezone": "Asia/Kolkata",
    "latitude": 19.076,
    "longitude": 72.8777,
    "place_name": "Mumbai",
}
_AS_OF = "2026-10-02T12:00:00Z"


def _request(question: str) -> dict[str, object]:
    return {"birth_input": _BIRTH_INPUT, "as_of": _AS_OF, "question": question}


def test_analyze_returns_context_routing_and_general_evidence() -> None:
    response = TestClient(create_app()).post(
        "/api/v1/analyze", json=_request("How is my overall reading?")
    )

    assert response.status_code == 200
    payload = response.json()
    assert {"context", "routing", "evidence_package", "selections"} == set(payload)
    assert payload["context"]["context_version"] == "deterministic-astrology-context-v1"
    assert payload["routing"]["request"]["reference_instant"] == _AS_OF
    assert len(payload["selections"]) == 1
    selection = payload["selections"][0]
    assert selection["question_intent"]["domain"] == "general"
    assert len(selection["selected_matched"]) + len(selection["relevant_unmatched"]) == 1
    assert "लाभेश" not in str(payload["evidence_package"])
    assert "Interpretation layer" not in str(payload)


def test_analyze_keeps_exact_domain_semantics_for_career_and_wealth() -> None:
    client = TestClient(create_app())
    for question, domain in (("How is my career?", "career"), ("How is my wealth?", "wealth")):
        response = client.post("/api/v1/analyze", json=_request(question))

        assert response.status_code == 200
        selection = response.json()["selections"][0]
        assert selection["question_intent"]["domain"] == domain
        relevant = (
            selection["selected_matched"]
            + selection["relevant_unmatched"]
            + selection["relevant_unknown"]
        )
        assert bool(relevant) is (domain == "career")
        assert all(item["domain"] == domain for item in selection["selected_matched"])
        assert all(item["domain"] == domain for item in selection["relevant_unmatched"])
        assert any(item["exclusion_reason"] == "domain_mismatch" for item in selection["excluded"])


def test_analyze_keeps_multi_domain_selections_separate() -> None:
    response = TestClient(create_app()).post(
        "/api/v1/analyze", json=_request("How are my career and wealth this year?")
    )

    assert response.status_code == 200
    payload = response.json()
    assert [item["domain"] for item in payload["routing"]["intents"]] == ["career", "wealth"]
    assert [item["question_intent"]["domain"] for item in payload["selections"]] == [
        "career",
        "wealth",
    ]


def test_analyze_time_bound_career_question_remains_without_timing_answerability() -> None:
    response = TestClient(create_app()).post(
        "/api/v1/analyze", json=_request("How is my career this year?")
    )

    assert response.status_code == 200
    capability = response.json()["selections"][0]["capability_summary"]
    assert capability["timing_requested"] is True
    assert capability["has_static_match"] is True
    assert capability["timing_answerability_established"] is False


def test_analyze_returns_routing_without_selection_when_unsupported() -> None:
    response = TestClient(create_app()).post("/api/v1/analyze", json=_request("Tell me a poem."))

    assert response.status_code == 200
    assert response.json()["routing"]["status"] == "unsupported"
    assert response.json()["selections"] == []


def test_analyze_rejects_invalid_input_and_pre_birth_as_of() -> None:
    client = TestClient(create_app())
    invalid = client.post("/api/v1/analyze", json={**_request("How is my career?"), "as_of": "bad"})
    pre_birth = client.post(
        "/api/v1/analyze",
        json={**_request("How is my career?"), "as_of": "1989-01-01T00:00:00Z"},
    )

    assert invalid.status_code == 422
    assert pre_birth.status_code == 422


def test_analyze_hides_provider_failure() -> None:
    service = Mock(spec=DeterministicAnalysisService)
    service.analyze.side_effect = RuntimeError("provider detail")
    app = create_app()
    app.dependency_overrides[get_analysis_service] = lambda: service

    response = TestClient(app).post("/api/v1/analyze", json=_request("How is my career?"))

    assert response.status_code == 503
    assert response.json()["detail"] == "Deterministic analysis is temporarily unavailable."


def test_analysis_builds_context_once_and_reuses_explicit_as_of_for_router() -> None:
    context_service = Mock(spec=DeterministicAstrologyContextService)
    real_context = DeterministicAstrologyContextService(SwissEphemerisProvider()).build
    context_service.build.side_effect = real_context
    service = DeterministicAnalysisService(context_service)
    request = _request("How is my career this year?")
    service_request = DeterministicAnalysisRequest.model_validate(request)
    result = service.analyze(service_request)

    assert context_service.build.call_count == 1
    assert result.routing.request.reference_instant == datetime(2026, 10, 2, 12, 0, tzinfo=UTC)
    assert service_request.as_of == result.routing.request.reference_instant
