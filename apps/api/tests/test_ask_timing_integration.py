"""Ask integration coverage for separately governed Career timing."""

import json
from datetime import UTC, datetime
from unittest.mock import Mock

from astrologer.application.analyze import (
    DeterministicAnalysisRequest,
    DeterministicAnalysisService,
)
from astrologer.application.answer import AskJyotAIService, _timing_context
from astrologer.application.context import DeterministicAstrologyContextService
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.birth.models import BirthInput
from astrologer.composition import (
    CompositionProviderRequest,
    CompositionProviderResponse,
    DeterministicAnswerComposer,
    SeniorAstrologerComposer,
)
from astrologer.evidence import InterpretationEvidenceBuilder
from astrologer.timing_rules.models import CareerTimingRequest, TimingRuleStatus
from astrologer.timing_rules.registry import CANDIDATE_CAREER_TIMING_RELEASE_V2
from astrologer.timing_rules.service import CareerTimingAnalysisService

_AS_OF = datetime(2026, 1, 1, tzinfo=UTC)
_MATCHING_BIRTH = BirthInput(
    birth_date="1978-01-01",
    birth_time="12:00:00",
    timezone="UTC",
    latitude=0,
    longitude=0,
)
_NONMATCHING_BIRTH = BirthInput(
    birth_date="1980-06-15",
    birth_time="12:00:00",
    timezone="UTC",
    latitude=0,
    longitude=0,
)


def _request(birth_input: BirthInput, question: str) -> DeterministicAnalysisRequest:
    return DeterministicAnalysisRequest(birth_input=birth_input, as_of=_AS_OF, question=question)


def _service(timing_service: CareerTimingAnalysisService, *, composer=None) -> AskJyotAIService:
    return AskJyotAIService(
        DeterministicAnalysisService(
            DeterministicAstrologyContextService(SwissEphemerisProvider())
        ),
        InterpretationEvidenceBuilder(),
        composer or DeterministicAnswerComposer(),
        timing_service,
    )


def test_career_non_timing_question_does_not_invoke_timing_service() -> None:
    timing_service = Mock(spec=CareerTimingAnalysisService)
    result = _service(timing_service).answer(_request(_MATCHING_BIRTH, "How is my career?"))
    assert result.answers[0].timing is None
    timing_service.analyze.assert_not_called()


def test_career_timing_question_uses_production_release_and_broad_window() -> None:
    timing_service = CareerTimingAnalysisService(SwissEphemerisProvider())
    result = _service(timing_service).answer(
        _request(_MATCHING_BIRTH, "When is a career-related period indicated?")
    )
    timing = result.answers[0].timing
    assert timing is not None
    assert timing.timing_answerability_established is True
    assert timing.status == "MATCH"
    assert timing.timing_release_id == "jyotish.timing.production.career@v2"
    assert len(timing.windows) == 1
    assert timing.windows[0].rule_id == "bphs.timing.vimshottari.career.10th_lord.in_4.md.v1"
    assert timing.windows[0].precision == "BROAD_PERIOD"
    assert timing.windows[0].effective_start == _AS_OF
    assert timing.windows[0].effective_end > timing.windows[0].effective_start
    assert timing.windows[0].why_this_period_applies.startswith("Your D1 tenth-house lord")
    assert timing.windows[0].reviewed_statement == (
        "In the reviewed BPHS Dasha-phala passage, when the D1 tenth-house lord is placed "
        "in the fourth house, that lord’s Dasha is described as rājya-pradāyinī—giving "
        "rājya-related results. Within JyotishAI, a matching Vimshottari Mahadasha is "
        "presented only as broad career-related timing context. It does not guarantee "
        "employment, promotion, office, authority, income, a government role, or a "
        "specific event or date."
    )
    assert timing.windows[0].limitations
    assert timing.windows[0].source.verse == "87"
    assert timing.windows[0].source.precision == "BROAD_PERIOD"
    assert timing.precision == "BROAD_PERIOD"  # deprecated v1 compatibility field


def test_candidate_injection_preserves_mixed_precision_rule_specific_windows() -> None:
    raw = CareerTimingAnalysisService(
        SwissEphemerisProvider(), timing_release=CANDIDATE_CAREER_TIMING_RELEASE_V2
    ).analyze(
        CareerTimingRequest(
            birth_input=BirthInput(
                birth_date="1970-05-01",
                birth_time="12:00:00",
                timezone="UTC",
                latitude=0,
                longitude=0,
            ),
            domain="career",
            as_of=_AS_OF,
            horizon_end=datetime(2090, 1, 1, tzinfo=UTC),
        )
    )
    broad_raw = CareerTimingAnalysisService(SwissEphemerisProvider()).analyze(
        CareerTimingRequest(
            birth_input=_MATCHING_BIRTH,
            domain="career",
            as_of=_AS_OF,
            horizon_end=datetime(2090, 1, 1, tzinfo=UTC),
        )
    )
    timing = _timing_context(
        raw.model_copy(
            update={
                "timing_answerability_established": True,
                "windows": broad_raw.windows + raw.windows,
            }
        )
    )
    assert {window.precision for window in timing.windows} == {"BROAD_PERIOD", "SUB_PERIOD"}
    assert tuple(
        (window.effective_start, window.effective_end, window.precision, window.rule_id)
        for window in timing.windows
    ) == tuple(
        sorted(
            (window.effective_start, window.effective_end, window.precision, window.rule_id)
            for window in timing.windows
        )
    )
    sub_period = next(window for window in timing.windows if window.precision == "SUB_PERIOD")
    assert (
        sub_period.rule_id == "bphs.timing.vimshottari.career.moon_md.venus_ad.own_or_exaltation.v1"
    )
    assert sub_period.why_this_period_applies.startswith("This sub-period corresponds to Moon")
    assert sub_period.why_this_period_applies != timing.windows[0].why_this_period_applies
    assert sub_period.source.verse == "140"
    assert timing.precision is None
    assert timing.why_this_period_applies is None


def test_no_match_and_unknown_are_distinct_application_states() -> None:
    timing_service = CareerTimingAnalysisService(SwissEphemerisProvider())
    result = _service(timing_service).answer(
        _request(_NONMATCHING_BIRTH, "When is career timing indicated in my chart?")
    )
    no_match = result.answers[0].timing
    assert no_match is not None
    assert no_match.status == "NO_MATCH"
    assert no_match.timing_answerability_established is False
    assert "No reviewed Career timing window" in no_match.message

    raw = timing_service.analyze(
        CareerTimingRequest(
            birth_input=_MATCHING_BIRTH,
            domain="career",
            as_of=_AS_OF,
            horizon_end=datetime(2040, 1, 1, tzinfo=UTC),
        )
    )
    unknown = _timing_context(
        raw.model_copy(
            update={
                "timing_answerability_established": False,
                "windows": (),
                "evidence": tuple(
                    item.model_copy(update={"status": TimingRuleStatus.UNKNOWN})
                    for item in raw.evidence
                ),
            }
        )
    )
    assert unknown.status == "UNKNOWN"
    assert "not sufficient" in unknown.message


class _RecordingTransport:
    def __init__(self) -> None:
        self.request: CompositionProviderRequest | None = None

    def complete(self, request: CompositionProviderRequest) -> CompositionProviderResponse:
        self.request = request
        return CompositionProviderResponse(
            output_json=json.dumps(
                {
                    "summary": "Static governed career context.",
                    "explanation": "The reviewed static indication is within its stated scope.",
                    "question_relevance": "This is relevant to the career question.",
                }
            ),
            provider_id="test-provider",
            model_id="test-model",
        )


def test_senior_astrologer_does_not_receive_application_timing_dates() -> None:
    transport = _RecordingTransport()
    result = _service(
        CareerTimingAnalysisService(SwissEphemerisProvider()),
        composer=SeniorAstrologerComposer(transport),
    ).answer(_request(_MATCHING_BIRTH, "When is a career-related period indicated?"))
    assert result.answers[0].timing is not None
    assert transport.request is not None
    assert "2031-03-18" not in transport.request.user_payload_json
    assert "BROAD_PERIOD" not in transport.request.user_payload_json
