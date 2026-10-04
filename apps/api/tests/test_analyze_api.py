"""Coverage for the stateless Task 14 deterministic analysis endpoint."""

import json
import logging
from datetime import UTC, datetime
from unittest.mock import Mock
from urllib.error import HTTPError

import pytest
from fastapi.testclient import TestClient

from astrologer.api.analyze import get_ask_jyotai_service
from astrologer.application.analyze import (
    DeterministicAnalysisRequest,
    DeterministicAnalysisService,
)
from astrologer.application.answer import AskJyotAIService
from astrologer.application.context import DeterministicAstrologyContextService
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.composition import (
    AnswerComposer,
    AnswerCompositionError,
    CompositionProviderRequest,
    CompositionProviderResponse,
    LanguageModelTransportError,
)
from astrologer.composition.openai_compatible import OpenAICompatibleTransport
from astrologer.evidence import InterpretationEvidenceBuilder
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
_MATCHED_CAREER_BIRTH_INPUT = {
    "birth_date": "1980-01-01",
    "birth_time": "12:00:00",
    "timezone": "UTC",
    "latitude": 0,
    "longitude": 0,
}


def _request(question: str) -> dict[str, object]:
    return {"birth_input": _BIRTH_INPUT, "as_of": _AS_OF, "question": question}


def _matched_career_request(question: str) -> dict[str, object]:
    return {"birth_input": _MATCHED_CAREER_BIRTH_INPUT, "as_of": _AS_OF, "question": question}


class _SafeTransport:
    def __init__(self) -> None:
        self.calls = 0

    def complete(self, request: CompositionProviderRequest) -> CompositionProviderResponse:
        self.calls += 1
        return CompositionProviderResponse(
            output_json=json.dumps(
                {
                    "answer": "The reviewed governed evidence is limited to its stated scope.",
                    "timing_answered": False,
                }
            ),
            provider_id="test-provider",
            model_id="test-model",
        )


def _client(transport: _SafeTransport | None = None) -> TestClient:
    app = create_app()
    service = AskJyotAIService(
        DeterministicAnalysisService(
            DeterministicAstrologyContextService(SwissEphemerisProvider())
        ),
        InterpretationEvidenceBuilder(),
        AnswerComposer(transport or _SafeTransport()),
    )
    app.dependency_overrides[get_ask_jyotai_service] = lambda: service
    return TestClient(app)


def test_analyze_returns_context_routing_and_general_evidence() -> None:
    response = _client().post("/api/v1/analyze", json=_request("How is my overall reading?"))

    assert response.status_code == 200
    payload = response.json()
    assert {"context", "routing", "evidence_package", "selections", "answers"} == set(payload)
    assert payload["answers"][0]["answer"]
    assert payload["context"]["context_version"] == "deterministic-astrology-context-v1"
    assert payload["routing"]["request"]["reference_instant"] == _AS_OF
    assert len(payload["selections"]) == 1
    selection = payload["selections"][0]
    assert selection["question_intent"]["domain"] == "general"
    assert len(selection["selected_matched"]) + len(selection["relevant_unmatched"]) == 1
    assert "लाभेश" not in str(payload["evidence_package"])
    assert "Interpretation layer" not in str(payload)


def test_analyze_keeps_exact_domain_semantics_for_career_and_wealth() -> None:
    client = _client()
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
        assert bool(relevant) is True
        assert all(item["domain"] == domain for item in selection["selected_matched"])
        assert all(item["domain"] == domain for item in selection["relevant_unmatched"])
        assert any(item["exclusion_reason"] == "domain_mismatch" for item in selection["excluded"])


def test_matched_wealth_returns_from_api_with_selected_governed_evidence() -> None:
    transport = _SafeTransport()
    response = _client(transport).post("/api/v1/analyze", json=_request("How is my wealth?"))

    assert response.status_code == 200
    assert response.json()["answers"][0]["corpus_limitation"] is False
    assert transport.calls == 0


def test_llm_disabled_returns_selected_reviewed_career_wording_without_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LLM_ENABLED", "false")
    monkeypatch.setattr(
        "astrologer.api.analyze.OpenAICompatibleTransport",
        lambda **_kwargs: pytest.fail(
            "disabled composition must not construct a provider transport"
        ),
    )
    response = TestClient(create_app()).post(
        "/api/v1/analyze", json=_matched_career_request("How is my career?")
    )

    assert response.status_code == 200
    payload = response.json()
    selected = payload["selections"][0]["selected_matched"]
    answer = payload["answers"][0]
    assert selected
    assert answer["referenced_evidence_item_ids"] == [item["evidence_item_id"] for item in selected]
    assert answer["corpus_limitation"] is False
    assert answer["provider_id"] == "deterministic-detailed-answer-builder"
    assert answer["why_it_applies"]
    assert answer["reviewed_interpretations"]
    assert (
        answer["evidence"][0]["source_work"]
        == "Brihat Parashara Hora Shastra / Brihat Parashara Hora Shastram"
    )


def test_llm_disabled_timing_answer_uses_static_wording_without_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LLM_ENABLED", "false")
    response = TestClient(create_app()).post(
        "/api/v1/analyze", json=_matched_career_request("When will my career improve?")
    )

    assert response.status_code == 200
    answer = response.json()["answers"][0]
    assert answer["timing_answered"] is False
    assert answer["answer"].endswith("Timing is not established by the current governed evidence.")
    assert answer["provider_id"] == "deterministic-detailed-answer-builder"


def test_llm_disabled_wealth_uses_reviewed_static_wording_and_timing_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LLM_ENABLED", "false")
    response = TestClient(create_app()).post(
        "/api/v1/analyze", json=_request("When will my wealth improve?")
    )

    assert response.status_code == 200
    answer = response.json()["answers"][0]
    assert answer["corpus_limitation"] is False
    assert answer["timing_answered"] is False
    assert answer["provider_id"] == "deterministic-detailed-answer-builder"
    assert answer["reviewed_interpretations"]
    assert answer["answer"].endswith("Timing is not established by the current governed evidence.")


def test_analyze_keeps_multi_domain_selections_separate() -> None:
    response = _client().post(
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
    response = _client().post("/api/v1/analyze", json=_request("When will my career improve?"))

    assert response.status_code == 200
    capability = response.json()["selections"][0]["capability_summary"]
    assert capability["timing_requested"] is True
    assert capability["has_static_match"] is True
    assert capability["timing_answerability_established"] is False
    answer = response.json()["answers"][0]
    assert answer["timing_answered"] is False
    assert answer["answer"].endswith("Timing is not established by the current governed evidence.")


def test_analyze_returns_routing_without_selection_when_unsupported() -> None:
    response = TestClient(create_app()).post("/api/v1/analyze", json=_request("Tell me a poem."))

    assert response.status_code == 200
    assert response.json()["routing"]["status"] == "unsupported"
    assert response.json()["selections"] == []


def test_analyze_rejects_invalid_input_and_pre_birth_as_of() -> None:
    client = _client()
    invalid = client.post("/api/v1/analyze", json={**_request("How is my career?"), "as_of": "bad"})
    pre_birth = client.post(
        "/api/v1/analyze",
        json={**_request("How is my career?"), "as_of": "1989-01-01T00:00:00Z"},
    )

    assert invalid.status_code == 422
    assert pre_birth.status_code == 422


def test_analyze_hides_provider_failure() -> None:
    app = create_app()
    ask_service = Mock(spec=AskJyotAIService)
    ask_service.answer.side_effect = RuntimeError("provider detail")
    app.dependency_overrides[get_ask_jyotai_service] = lambda: ask_service

    response = TestClient(app).post("/api/v1/analyze", json=_request("How is my career?"))

    assert response.status_code == 503
    assert response.json()["detail"] == "Deterministic analysis is temporarily unavailable."


@pytest.mark.parametrize(
    "error",
    (
        AnswerCompositionError("malformed structured response"),
        AnswerCompositionError("unsupported evidence reference"),
        LanguageModelTransportError("timeout"),
    ),
)
def test_analyze_fails_closed_for_composition_errors(error: Exception) -> None:
    app = create_app()
    ask_service = Mock(spec=AskJyotAIService)
    ask_service.answer.side_effect = error
    app.dependency_overrides[get_ask_jyotai_service] = lambda: ask_service

    response = TestClient(app).post("/api/v1/analyze", json=_request("How is my career?"))

    assert response.status_code == 503
    assert response.json()["detail"] == "Governed answer composition is temporarily unavailable."


@pytest.mark.parametrize("http_status_code", (400, 401, 403, 404, 429, 500))
def test_openai_compatible_http_failure_keeps_safe_status_metadata(
    monkeypatch: pytest.MonkeyPatch, http_status_code: int
) -> None:
    transport = OpenAICompatibleTransport(
        base_url="https://provider.example/v1",
        model="safe-model",
        provider_id="openai_compatible",
        api_key="sk-test-secret",
        timeout_seconds=1,
    )
    monkeypatch.setattr(
        "astrologer.composition.openai_compatible.urlopen",
        Mock(
            side_effect=HTTPError(
                "https://provider.example/v1/chat/completions",
                http_status_code,
                "private",
                {},
                None,
            )
        ),
    )

    with pytest.raises(LanguageModelTransportError) as raised:
        transport.complete(
            CompositionProviderRequest(
                system_instructions="private system prompt",
                user_payload_json='{"question":"private"}',
            )
        )

    assert raised.value.category == "provider_http"
    assert raised.value.http_status_code == http_status_code
    assert raised.value.provider_id == "openai_compatible"
    assert raised.value.model_id == "safe-model"


def test_composition_failure_log_is_sanitized_and_response_stays_generic(
    caplog: pytest.LogCaptureFixture,
) -> None:
    app = create_app()
    ask_service = Mock(spec=AskJyotAIService)
    ask_service.answer.side_effect = LanguageModelTransportError(
        "provider_http",
        provider_id="openai_compatible",
        model_id="safe-model",
        http_status_code=401,
    )
    app.dependency_overrides[get_ask_jyotai_service] = lambda: ask_service

    with caplog.at_level(logging.WARNING, logger="astrologer.api.analyze"):
        response = TestClient(app).post("/api/v1/analyze", json=_request("private user question"))

    assert response.status_code == 503
    assert response.json()["detail"] == "Governed answer composition is temporarily unavailable."
    assert "category=provider_http" in caplog.text
    assert "provider_id=openai_compatible" in caplog.text
    assert "model_id=safe-model" in caplog.text
    assert "http_status_code=401" in caplog.text
    assert "reason_code=not_applicable" in caplog.text
    for secret_or_payload in (
        "sk-test-secret",
        "Authorization",
        "private user question",
        "1990-01-15",
        "private system prompt",
    ):
        assert secret_or_payload not in caplog.text


def test_schema_failure_log_contains_only_structural_diagnostics(
    caplog: pytest.LogCaptureFixture,
) -> None:
    app = create_app()
    ask_service = Mock(spec=AskJyotAIService)
    ask_service.answer.side_effect = AnswerCompositionError(
        reason_code="invalid_output_shape",
        provider_id="openai_compatible",
        model_id="safe-model",
        returned_fields="answer,reason",
        missing_fields="timing_answered",
        unexpected_fields="reason",
        field_types="answer=str,reason=str",
        validation_errors="missing:timing_answered",
    )
    app.dependency_overrides[get_ask_jyotai_service] = lambda: ask_service

    with caplog.at_level(logging.WARNING, logger="astrologer.api.analyze"):
        response = TestClient(app).post("/api/v1/analyze", json=_request("private user question"))

    assert response.status_code == 503
    assert "returned_fields=answer,reason" in caplog.text
    assert "missing_fields=timing_answered" in caplog.text
    assert "unexpected_fields=reason" in caplog.text
    assert "field_types=answer=str,reason=str" in caplog.text
    assert "validation_errors=missing:timing_answered" in caplog.text
    assert "private user question" not in caplog.text


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
