"""Coverage for the fixed, non-question-driven dashboard insights API."""

from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from astrologer.application.analyze import (
    DeterministicAnalysisRequest,
    DeterministicAnalysisService,
)
from astrologer.application.context import (
    DeterministicAstrologyContextService,
    DeterministicContextRequest,
)
from astrologer.application.dashboard_insights import DashboardInsightsService, _dashboard_intents
from astrologer.astrology.derived_facts import to_fact_set
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.composition import DeterministicAnswerComposer
from astrologer.evidence import EvidenceBuilder, EvidenceSelector, InterpretationEvidenceBuilder
from astrologer.knowledge import (
    ACTIVE_PRODUCTION_RELEASE,
    FactEvaluationProvenance,
    GovernedRuleEvaluator,
)
from astrologer.main import create_app
from astrologer.questions.router import QuestionIntentRouter

_AS_OF = "2026-10-02T12:00:00Z"
_MATCHED_CAREER_BIRTH_INPUT = {
    "birth_date": "1980-01-01",
    "birth_time": "12:00:00",
    "timezone": "UTC",
    "latitude": 0,
    "longitude": 0,
}


def _request() -> dict[str, object]:
    return {"birth_input": _MATCHED_CAREER_BIRTH_INPUT, "as_of": _AS_OF}


def test_dashboard_insights_returns_exact_fixed_domain_order_and_reviewed_match() -> None:
    response = TestClient(create_app()).post("/api/v1/insights/dashboard", json=_request())

    assert response.status_code == 200
    insights = response.json()["insights"]
    assert [item["domain"] for item in insights] == [
        "career",
        "wealth",
        "education",
        "business",
        "children",
        "spirituality",
        "travel",
        "friends",
    ]
    career = insights[0]
    assert career["has_matched_evidence"] is True
    assert career["matched_count"] > 0
    assert career["answers"][0]["answer"]
    assert career["answers"][0]["corpus_limitation"] is False
    assert career["answers"][0]["provider_id"] == "deterministic-governed-composer"


def test_dashboard_insights_keeps_no_match_as_a_non_negative_empty_answer_state() -> None:
    response = TestClient(create_app()).post("/api/v1/insights/dashboard", json=_request())

    assert response.status_code == 200
    wealth = next(item for item in response.json()["insights"] if item["domain"] == "wealth")
    assert wealth["has_matched_evidence"] is False
    assert wealth["matched_count"] == 0
    assert wealth["unmatched_count"] > 0
    assert wealth["unknown_count"] == 0
    assert wealth["answers"] == []


def test_dashboard_insights_does_not_invoke_natural_language_routing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_if_routed(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("dashboard endpoint must not invoke the question router")

    monkeypatch.setattr(QuestionIntentRouter, "route", fail_if_routed)  # type: ignore[attr-defined]

    response = TestClient(create_app()).post("/api/v1/insights/dashboard", json=_request())

    assert response.status_code == 200


def test_dashboard_intents_keep_existing_exact_domain_selection_isolation() -> None:
    analysis_service = DeterministicAnalysisService(
        DeterministicAstrologyContextService(SwissEphemerisProvider())
    )
    request = DeterministicAnalysisRequest.model_validate(_request() | {"question": "unused"})
    _, selections = analysis_service.analyze_explicit_intents(
        request,
        _dashboard_intents(),
    )

    for selection in selections:
        relevant = (
            selection.selected_matched + selection.relevant_unmatched + selection.relevant_unknown
        )
        assert all(item.domain.value == selection.question_intent.domain.value for item in relevant)


def test_unknown_is_explicitly_distinct_from_no_match() -> None:
    context_service = DeterministicAstrologyContextService(SwissEphemerisProvider())
    context = context_service.build(DeterministicContextRequest.model_validate(_request()))
    missing_career_fact = "jyotish.d1.house_lord.10.placement_house"
    partial_bundle = context.derived_facts.model_copy(
        update={
            "facts": tuple(
                fact for fact in context.derived_facts.facts if fact.fact_id != missing_career_fact
            )
        }
    )
    partial_context = context.model_copy(update={"derived_facts": partial_bundle})
    evaluations = GovernedRuleEvaluator().evaluate(
        ACTIVE_PRODUCTION_RELEASE.manifest,
        ACTIVE_PRODUCTION_RELEASE.envelopes,
        ACTIVE_PRODUCTION_RELEASE.registry,
        ACTIVE_PRODUCTION_RELEASE.fact_contract,
        to_fact_set(partial_bundle),
        FactEvaluationProvenance.from_derived_fact_bundle(partial_bundle),
    )
    package = EvidenceBuilder().build(
        partial_context, ACTIVE_PRODUCTION_RELEASE.manifest, evaluations
    )
    selection = EvidenceSelector().select(_dashboard_intents()[0], package)
    composer = Mock(spec=DeterministicAnswerComposer)
    service = DashboardInsightsService(Mock(), InterpretationEvidenceBuilder(), composer)

    insight = service._insight(selection)

    assert insight.has_matched_evidence is False
    assert insight.matched_count == 0
    assert insight.unmatched_count == 0
    assert insight.unknown_count == 4
    assert insight.answers == ()
    composer.compose.assert_not_called()


def test_dashboard_endpoint_uses_active_governance_without_release_mutation() -> None:
    release = ACTIVE_PRODUCTION_RELEASE

    assert (release.manifest.manifest_id, release.manifest.manifest_version) == (
        "jyotish.production.cumulative",
        "v10",
    )
    assert (release.fact_contract.contract_id, release.fact_contract.contract_version) == (
        "jyotish.d1.structural.rule1",
        "v5",
    )
    assert len(release.envelopes) == 22
