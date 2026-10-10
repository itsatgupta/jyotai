"""Focused candidate-only coverage for the independently scoped BPHS v.89 clause."""

from datetime import UTC, datetime, timedelta
from inspect import getsource

from astrologer.astrology.dasha import DashaLord
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.birth.models import BirthInput
from astrologer.timing_rules.evaluator import CareerTimingRuleEvaluator
from astrologer.timing_rules.models import (
    CareerTimingRequest,
    MahadashaTimingCondition,
    NinthLordTenthPlacementTimingCondition,
    TimingPrecision,
    TimingRuleStatus,
)
from astrologer.timing_rules.registry import (
    ACTIVE_TIMING_RELEASE_POINTER,
    CANDIDATE_CAREER_TIMING_RELEASE_V89,
    NINTH_LORD_IN_TENTH_TIMING_RULE,
    NINTH_LORD_IN_TENTH_TIMING_SOURCE,
    PRODUCTION_CAREER_TIMING_RELEASE_V2,
)
from astrologer.timing_rules.service import CareerTimingAnalysisService

_BIRTH = BirthInput(
    birth_date="1952-05-01",
    birth_time="12:00:00",
    timezone="UTC",
    latitude=0,
    longitude=0,
)
_AS_OF = datetime(2026, 1, 1, tzinfo=UTC)
_HORIZON = datetime(2090, 1, 1, tzinfo=UTC)
_MD = MahadashaTimingCondition(
    lord=DashaLord.JUPITER,
    start=datetime(2045, 1, 1, tzinfo=UTC),
    end=datetime(2061, 1, 1, tzinfo=UTC),
)


def _service() -> CareerTimingAnalysisService:
    return CareerTimingAnalysisService(
        SwissEphemerisProvider(), timing_release=CANDIDATE_CAREER_TIMING_RELEASE_V89
    )


def _request(as_of: datetime = _AS_OF, horizon_end: datetime = _HORIZON) -> CareerTimingRequest:
    return CareerTimingRequest(
        birth_input=_BIRTH, domain="career", as_of=as_of, horizon_end=horizon_end
    )


def test_v89_evaluator_preserves_positive_false_and_unknown_facts() -> None:
    evaluator = CareerTimingRuleEvaluator()
    matching = NinthLordTenthPlacementTimingCondition(
        ninth_house_lord=DashaLord.JUPITER, placement_house=10
    )
    assert (
        evaluator.evaluate_ninth_lord_in_tenth_mahadasha(
            NINTH_LORD_IN_TENTH_TIMING_RULE, matching, _MD
        ).status
        is TimingRuleStatus.MATCH
    )
    assert (
        evaluator.evaluate_ninth_lord_in_tenth_mahadasha(
            NINTH_LORD_IN_TENTH_TIMING_RULE,
            matching.model_copy(update={"placement_house": 9}),
            _MD,
        ).status
        is TimingRuleStatus.FALSE
    )
    assert (
        evaluator.evaluate_ninth_lord_in_tenth_mahadasha(
            NINTH_LORD_IN_TENTH_TIMING_RULE,
            matching,
            _MD.model_copy(update={"lord": DashaLord.SATURN}),
        ).status
        is TimingRuleStatus.FALSE
    )
    assert (
        evaluator.evaluate_ninth_lord_in_tenth_mahadasha(
            NINTH_LORD_IN_TENTH_TIMING_RULE,
            matching.model_copy(update={"ninth_house_lord": None}),
            _MD,
        ).status
        is TimingRuleStatus.UNKNOWN
    )
    assert (
        evaluator.evaluate_ninth_lord_in_tenth_mahadasha(
            NINTH_LORD_IN_TENTH_TIMING_RULE,
            matching.model_copy(update={"placement_house": None}),
            _MD,
        ).status
        is TimingRuleStatus.UNKNOWN
    )
    assert (
        evaluator.evaluate_ninth_lord_in_tenth_mahadasha(
            NINTH_LORD_IN_TENTH_TIMING_RULE,
            matching,
            _MD.model_copy(update={"start": None}),
        ).status
        is TimingRuleStatus.UNKNOWN
    )


def test_v89_candidate_uses_deterministic_d1_fixture_and_canonical_md_interval() -> None:
    result = _service().analyze(_request())
    match = next(item for item in result.evidence if item.status is TimingRuleStatus.MATCH)
    window = result.windows[0]

    assert result.timing_release_id == "jyotish.timing.career.candidate.v89"
    assert result.timing_release_status.value == "candidate_admitted"
    assert match.natal_condition.ninth_house_lord is DashaLord.JUPITER
    assert match.natal_condition.placement_house == 10
    assert match.mahadasha.lord is DashaLord.JUPITER
    assert match.source_interval == window.source_interval
    assert match.effective_window == window.effective_window == match.source_interval
    assert window.precision is TimingPrecision.BROAD_PERIOD


def test_v89_candidate_clips_only_effective_window() -> None:
    full = _service().analyze(_request())
    canonical = next(
        item for item in full.evidence if item.status is TimingRuleStatus.MATCH
    ).source_interval
    assert canonical is not None
    clipped = _service().analyze(
        _request(canonical.start + timedelta(days=10), canonical.end - timedelta(days=10))
    )
    match = next(item for item in clipped.evidence if item.status is TimingRuleStatus.MATCH)
    assert match.source_interval == canonical
    assert match.effective_window is not None
    assert match.effective_window.start == canonical.start + timedelta(days=10)
    assert match.effective_window.end == canonical.end - timedelta(days=10)


def test_v89_source_provenance_wording_and_adjacent_verse_limitations_are_bounded() -> None:
    source = NINTH_LORD_IN_TENTH_TIMING_SOURCE
    assert source.verse == "89"
    assert source.page_locator == "printed p. 440; local artifact PDF p. 438"
    assert "दशमस्थ धर्मेशदशा राज्यप्रदायिनी" in source.sanskrit
    assert "ninth-house lord placed in the tenth house" in source.reviewed_translation
    assert "employment" in source.reviewed_interpretation
    assert "promotion" in source.reviewed_interpretation
    assert "government position" in source.reviewed_interpretation
    assert "salary or wealth increase" in source.reviewed_interpretation
    assert "authority acquisition" in source.reviewed_interpretation
    assert "predictive certainty" in source.reviewed_interpretation
    assert any("v.88" in item for item in source.adjacent_verse_limitations)
    assert any("vv.90–95" in item for item in source.adjacent_verse_limitations)


def test_v89_candidate_neither_mutates_production_v2_nor_enters_ask_path() -> None:
    assert CANDIDATE_CAREER_TIMING_RELEASE_V89.activated_at is None
    assert CANDIDATE_CAREER_TIMING_RELEASE_V89.rules == (NINTH_LORD_IN_TENTH_TIMING_RULE,)
    assert ACTIVE_TIMING_RELEASE_POINTER.release_id == "jyotish.timing.production.career@v2"
    assert NINTH_LORD_IN_TENTH_TIMING_RULE not in PRODUCTION_CAREER_TIMING_RELEASE_V2.rules
    assert "CANDIDATE_CAREER_TIMING_RELEASE_V89" not in getsource(
        CareerTimingAnalysisService.__init__
    )
