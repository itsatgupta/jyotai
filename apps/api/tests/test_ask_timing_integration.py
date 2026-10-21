"""Ask integration coverage for separately governed Career timing."""

import json
import logging
from datetime import UTC, date, datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

from astrologer.application.analyze import (
    DeterministicAnalysisRequest,
    DeterministicAnalysisService,
)
from astrologer.application.answer import AskJyotAIService, _calendar_interval, _timing_context
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
from astrologer.questions.models import ResolvedTimeRange, TimeRangeKind, TimeRangeSource
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
_V2_POSITIVE_BIRTH = BirthInput(
    birth_date="1950-05-01",
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


def test_career_non_timing_question_does_not_invoke_timing_service(
    caplog: pytest.LogCaptureFixture,
) -> None:
    timing_service = Mock(spec=CareerTimingAnalysisService)
    with caplog.at_level(logging.INFO, logger="astrologer.application.answer"):
        result = _service(timing_service).answer(_request(_MATCHING_BIRTH, "How is my career?"))
    assert result.answers[0].timing is None
    timing_service.analyze.assert_not_called()
    assert "ask_routing domain=career requires_timing=false" in caplog.text
    assert "windows=0 status=absent reason=requires_timing_false" in caplog.text


def test_career_timing_question_uses_production_release_and_broad_window(
    caplog: pytest.LogCaptureFixture,
) -> None:
    timing_service = CareerTimingAnalysisService(SwissEphemerisProvider())
    question = "When is my private career timing?"
    with caplog.at_level(logging.INFO):
        result = _service(timing_service).answer(_request(_MATCHING_BIRTH, question))
    timing = result.answers[0].timing
    assert timing is not None
    assert timing.timing_answerability_established is True
    assert timing.status == "MATCH"
    assert timing.scope == "default_40_year_horizon"
    assert timing.requested_start_date is None
    assert timing.evaluated_start == _AS_OF
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
    assert "ask_routing domain=career requires_timing=true" in caplog.text
    assert "career_timing_service_invoked" in caplog.text
    assert "career_timing_start release=jyotish.timing.production.career@v2" in caplog.text
    assert "status=MATCH precision=BROAD_PERIOD" in caplog.text
    assert "status=FALSE" in caplog.text
    assert "career_timing_window precision=BROAD_PERIOD" in caplog.text
    assert "career_timing_complete windows=1 status=attached" in caplog.text
    for sensitive_value in (
        "1978-01-01",
        "12:00:00",
        "birth_date",
        "birth_time",
        "latitude",
        "longitude",
        "private career timing question",
    ):
        assert sensitive_value not in caplog.text


def test_career_timing_question_attaches_production_v2_sub_period_window(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A deterministic birth input reaches an exalted-Venus Moon/Venus AD in the Ask horizon."""
    as_of = datetime(2061, 1, 1, tzinfo=UTC)
    with caplog.at_level(logging.INFO):
        result = _service(CareerTimingAnalysisService(SwissEphemerisProvider())).answer(
            DeterministicAnalysisRequest(
                birth_input=_V2_POSITIVE_BIRTH,
                as_of=as_of,
                question="When are my upcoming important career periods?",
            )
        )

    timing = result.answers[0].timing
    assert timing is not None
    assert timing.status == "MATCH"
    assert timing.timing_answerability_established is True
    assert timing.timing_release_id == "jyotish.timing.production.career@v2"
    window = next(window for window in timing.windows if window.precision == "SUB_PERIOD")
    assert window.rule_id == "bphs.timing.vimshottari.career.moon_md.venus_ad.own_or_exaltation.v1"
    assert window.effective_start == as_of
    assert window.source_start < window.effective_start < window.effective_end == window.source_end
    assert window.why_this_period_applies == (
        "This sub-period corresponds to Moon Mahadasha and Venus Antardasha, with natal Venus "
        "in its own sign or exaltation sign."
    )
    assert "does not guarantee employment" in window.reviewed_statement
    assert "no guaranteed event" in window.limitations
    assert window.source.verse == "140"
    assert window.source.dasha_scope == "Vimshottari Moon Mahadasha / Venus Antardasha"
    assert window.source.precision == "SUB_PERIOD"
    assert "ask_routing domain=career requires_timing=true" in caplog.text
    assert (
        "career_timing_rule "
        "rule_id=bphs.timing.vimshottari.career.moon_md.venus_ad.own_or_exaltation.v1 "
        "status=MATCH precision=SUB_PERIOD"
    ) in caplog.text


def test_timing_info_logs_one_summary_per_rule_not_per_interval(
    caplog: pytest.LogCaptureFixture,
) -> None:
    as_of = datetime(2061, 1, 1, tzinfo=UTC)
    with caplog.at_level(logging.INFO, logger="astrologer.application.answer"):
        _service(CareerTimingAnalysisService(SwissEphemerisProvider())).answer(
            DeterministicAnalysisRequest(
                birth_input=_V2_POSITIVE_BIRTH,
                as_of=as_of,
                question="When are my upcoming important career periods?",
            )
        )

    rule_records = [
        record
        for record in caplog.records
        if record.name == "astrologer.application.answer"
        and record.getMessage().startswith("career_timing_rule ")
    ]
    assert len(rule_records) == 2
    v2_record = next(
        record
        for record in rule_records
        if "moon_md.venus_ad.own_or_exaltation.v1" in record.getMessage()
    )
    assert "status=MATCH precision=SUB_PERIOD" in v2_record.getMessage()
    assert "evaluations=" in v2_record.getMessage()
    assert "matches=1" in v2_record.getMessage()
    assert "windows=1" in v2_record.getMessage()
    assert "1950-05-01" not in caplog.text
    assert "birth_date" not in caplog.text


def test_timing_diagnostics_log_unknown_and_absent_attachment(
    caplog: pytest.LogCaptureFixture,
) -> None:
    raw = CareerTimingAnalysisService(SwissEphemerisProvider()).analyze(
        CareerTimingRequest(
            birth_input=_MATCHING_BIRTH,
            domain="career",
            as_of=_AS_OF,
            horizon_end=datetime(2040, 1, 1, tzinfo=UTC),
        )
    )
    unknown_result = raw.model_copy(
        update={
            "timing_answerability_established": False,
            "windows": (),
            "evidence": tuple(
                item.model_copy(update={"status": TimingRuleStatus.UNKNOWN})
                for item in raw.evidence
            ),
        }
    )
    timing_service = Mock(spec=CareerTimingAnalysisService)
    timing_service.analyze.return_value = unknown_result

    with caplog.at_level(logging.INFO, logger="astrologer.application.answer"):
        result = _service(timing_service).answer(
            _request(_MATCHING_BIRTH, "When is career timing indicated?")
        )

    assert result.answers[0].timing is not None
    assert "status=UNKNOWN precision=BROAD_PERIOD" in caplog.text
    assert "career_timing_complete windows=0 status=absent reason=unknown_timing" in caplog.text


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

    no_match_raw = timing_service.analyze(
        CareerTimingRequest(
            birth_input=_NONMATCHING_BIRTH,
            domain="career",
            as_of=_AS_OF,
            horizon_end=datetime(2066, 1, 1, tzinfo=UTC),
        )
    )
    statuses_by_rule = {
        rule_id: {item.status for item in no_match_raw.evidence if item.rule_id == rule_id}
        for rule_id in {item.rule_id for item in no_match_raw.evidence}
    }
    assert statuses_by_rule == {
        "bphs.timing.vimshottari.career.10th_lord.in_4.md.v1": {TimingRuleStatus.FALSE},
        "bphs.timing.vimshottari.career.moon_md.venus_ad.own_or_exaltation.v1": {
            TimingRuleStatus.FALSE
        },
    }
    assert no_match_raw.windows == ()

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


@pytest.mark.parametrize(
    ("question", "start", "end"),
    [
        ("Will I get a promotion in 2027?", date(2027, 1, 1), date(2028, 1, 1)),
        ("Will my career change in March 2028?", date(2028, 3, 1), date(2028, 4, 1)),
        (
            "Will my career change from 2027-05-10 to 2027-06-15?",
            date(2027, 5, 10),
            date(2027, 6, 16),
        ),
        (
            "Will my career change between 2027-12-15 and 2028-01-15?",
            date(2027, 12, 15),
            date(2028, 1, 16),
        ),
    ],
)
def test_requested_calendar_interval_selects_only_intersecting_windows(
    question: str, start: date, end: date
) -> None:
    result = _service(CareerTimingAnalysisService(SwissEphemerisProvider())).answer(
        _request(_MATCHING_BIRTH, question)
    )
    timing = result.answers[0].timing
    assert timing is not None
    assert timing.scope == "requested_range"
    assert timing.evaluated_start == datetime.combine(start, datetime.min.time(), tzinfo=UTC)
    assert timing.evaluated_end == datetime.combine(end, datetime.min.time(), tzinfo=UTC)
    assert timing.status == "MATCH"
    assert timing.windows
    assert all(
        timing.evaluated_start
        <= window.effective_start
        < window.effective_end
        <= timing.evaluated_end
        for window in timing.windows
    )
    assert any(window.source_start < window.effective_start for window in timing.windows)
    assert timing.timing_release_id == "jyotish.timing.production.career@v2"


def test_no_matching_approved_evidence_is_not_an_adverse_prediction() -> None:
    timing = (
        _service(CareerTimingAnalysisService(SwissEphemerisProvider()))
        .answer(_request(_NONMATCHING_BIRTH, "Will my career change in 2027?"))
        .answers[0]
        .timing
    )
    assert timing is not None
    assert timing.status == "NO_MATCH"
    assert timing.windows == ()
    assert timing.evaluated_start == datetime(2027, 1, 1, tzinfo=UTC)


def test_bounded_unknown_remains_unknown_and_has_no_windows() -> None:
    raw = CareerTimingAnalysisService(SwissEphemerisProvider()).analyze(
        CareerTimingRequest(
            birth_input=_MATCHING_BIRTH,
            domain="career",
            as_of=datetime(2027, 1, 1, tzinfo=UTC),
            horizon_end=datetime(2028, 1, 1, tzinfo=UTC),
        )
    )
    service = Mock(spec=CareerTimingAnalysisService)
    service.analyze.return_value = raw.model_copy(
        update={
            "timing_answerability_established": False,
            "windows": (),
            "evidence": tuple(
                item.model_copy(update={"status": TimingRuleStatus.UNKNOWN})
                for item in raw.evidence
            ),
        }
    )
    timing = (
        _service(service)
        .answer(_request(_MATCHING_BIRTH, "Will my career change in 2027?"))
        .answers[0]
        .timing
    )
    assert timing is not None
    assert timing.status == "UNKNOWN"
    assert timing.windows == ()
    assert timing.evaluated_end == datetime(2028, 1, 1, tzinfo=UTC)


@pytest.mark.parametrize(
    ("question", "status", "partial"),
    [
        ("What happened with my career in 2020?", "UNSUPPORTED", False),
        ("Will my career change in 2070?", "UNSUPPORTED", False),
        ("Will my career change between 2065 and 2067?", "NO_MATCH", True),
    ],
)
def test_unsupported_and_partially_supported_ranges(
    question: str, status: str, partial: bool
) -> None:
    service = Mock(spec=CareerTimingAnalysisService)
    if partial:
        service.analyze.side_effect = CareerTimingAnalysisService(SwissEphemerisProvider()).analyze
    timing = _service(service).answer(_request(_NONMATCHING_BIRTH, question)).answers[0].timing
    assert timing is not None
    assert timing.status == status
    assert timing.partially_supported is partial
    assert timing.windows == ()
    if partial:
        assert timing.evaluated_start == datetime(2065, 1, 1, tzinfo=UTC)
        assert timing.evaluated_end == _AS_OF + timedelta(days=365.25 * 40)
        assert service.analyze.call_args.args[0].horizon_end == timing.evaluated_end
    else:
        assert timing.evaluated_start is None
        service.analyze.assert_not_called()


def test_unbounded_historical_question_does_not_use_forward_default() -> None:
    service = Mock(spec=CareerTimingAnalysisService)
    timing = (
        _service(service)
        .answer(_request(_MATCHING_BIRTH, "What happened with my career previously?"))
        .answers[0]
        .timing
    )
    assert timing is not None
    assert timing.status == "UNSUPPORTED"
    assert timing.scope == "historical_unbounded"
    service.analyze.assert_not_called()


def test_calendar_dates_follow_validated_reference_timezone() -> None:
    india = timezone(timedelta(hours=5, minutes=30))
    interval = _calendar_interval(
        ResolvedTimeRange(
            range_kind=TimeRangeKind.CALENDAR_MONTH,
            start_date=date(2028, 3, 1),
            end_date=date(2028, 3, 31),
            source=TimeRangeSource.ABSOLUTE,
        ),
        datetime(2026, 1, 1, tzinfo=india),
    )
    assert interval.start == datetime(2028, 2, 29, 18, 30, tzinfo=UTC)
    assert interval.end == datetime(2028, 3, 31, 18, 30, tzinfo=UTC)
    timing = (
        _service(CareerTimingAnalysisService(SwissEphemerisProvider()))
        .answer(
            DeterministicAnalysisRequest(
                birth_input=_MATCHING_BIRTH,
                as_of=datetime(2026, 1, 1, tzinfo=india),
                question="Will my career change in March 2028?",
            )
        )
        .answers[0]
        .timing
    )
    assert timing is not None
    assert timing.calendar_timezone_offset == "+0530"
    assert (timing.evaluated_start, timing.evaluated_end) == (interval.start, interval.end)
    assert all(
        interval.start <= window.effective_start < window.effective_end <= interval.end
        for window in timing.windows
    )


def test_calendar_year_in_non_career_domain_never_invokes_career_timing() -> None:
    service = Mock(spec=CareerTimingAnalysisService)
    result = _service(service).answer(_request(_MATCHING_BIRTH, "Will my wealth grow in 2027?"))
    assert result.answers[0].timing is None
    service.analyze.assert_not_called()


def test_bounded_provider_packet_has_no_question_or_timing_data() -> None:
    transport = _RecordingTransport()
    result = _service(
        CareerTimingAnalysisService(SwissEphemerisProvider()),
        composer=SeniorAstrologerComposer(transport),
    ).answer(_request(_MATCHING_BIRTH, "Will my private career change in March 2028?"))
    assert result.answers[0].timing is not None
    assert transport.request is not None
    packet = transport.request.user_payload_json
    for private in (
        "private career",
        "March 2028",
        "2028-03-01",
        "1978-01-01",
        "birth_date",
        "BROAD_PERIOD",
    ):
        assert private not in packet
