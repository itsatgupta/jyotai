"""Task 12 deterministic, language-only question-routing tests."""

from datetime import UTC, date, datetime, timedelta, timezone
from inspect import getsource

import pytest
from pydantic import ValidationError

from astrologer.questions import (
    QuestionDomain,
    QuestionIntent,
    QuestionIntentRouter,
    QuestionRequest,
    QuestionShape,
    RelativeTimeExpression,
    RoutingIssue,
    RoutingStatus,
    TemporalIntent,
    TimeRangeKind,
    TimeRangeSource,
)

_ROUTER = QuestionIntentRouter()
_REFERENCE = datetime(2026, 10, 2, 12, 0, tzinfo=UTC)


def _route(question: str, reference_instant: datetime | None = None):
    return _ROUTER.route(QuestionRequest(question=question, reference_instant=reference_instant))


@pytest.mark.parametrize(
    ("question", "domain", "shape", "temporal", "requires_timing"),
    [
        (
            "How is my career?",
            QuestionDomain.CAREER,
            QuestionShape.DESCRIPTIVE,
            TemporalIntent.TIMELESS,
            False,
        ),
        (
            "When will I change my job?",
            QuestionDomain.CAREER,
            QuestionShape.TIMING,
            TemporalIntent.TIME_BOUND,
            True,
        ),
        (
            "How will my business grow?",
            QuestionDomain.BUSINESS,
            QuestionShape.DESCRIPTIVE,
            TemporalIntent.FUTURE_GENERAL,
            False,
        ),
        (
            "How is my wealth?",
            QuestionDomain.WEALTH,
            QuestionShape.DESCRIPTIVE,
            TemporalIntent.TIMELESS,
            False,
        ),
        (
            "When will I buy my own house?",
            QuestionDomain.PROPERTY,
            QuestionShape.TIMING,
            TemporalIntent.TIME_BOUND,
            True,
        ),
        (
            "How is my marriage?",
            QuestionDomain.MARRIAGE,
            QuestionShape.DESCRIPTIVE,
            TemporalIntent.TIMELESS,
            False,
        ),
        (
            "When will I get married?",
            QuestionDomain.MARRIAGE,
            QuestionShape.TIMING,
            TemporalIntent.TIME_BOUND,
            True,
        ),
        (
            "How is my health?",
            QuestionDomain.HEALTH,
            QuestionShape.DESCRIPTIVE,
            TemporalIntent.TIMELESS,
            False,
        ),
        (
            "Should I change my business?",
            QuestionDomain.BUSINESS,
            QuestionShape.DECISION,
            TemporalIntent.TIMELESS,
            False,
        ),
        (
            "Will this property investment be good?",
            QuestionDomain.PROPERTY,
            QuestionShape.POTENTIAL,
            TemporalIntent.TIMELESS,
            False,
        ),
        (
            "Give me an overall reading.",
            QuestionDomain.GENERAL,
            QuestionShape.DESCRIPTIVE,
            TemporalIntent.TIMELESS,
            False,
        ),
        (
            "Will I get a promotion?",
            QuestionDomain.CAREER,
            QuestionShape.POTENTIAL,
            TemporalIntent.FUTURE_GENERAL,
            False,
        ),
    ],
)
def test_single_domain_examples_route_as_approved(
    question: str,
    domain: QuestionDomain,
    shape: QuestionShape,
    temporal: TemporalIntent,
    requires_timing: bool,
) -> None:
    result = _route(question)

    assert result.status is RoutingStatus.ROUTABLE
    assert result.issues == ()
    assert len(result.intents) == 1
    intent = result.intents[0]
    assert (intent.domain, intent.shape, intent.temporal_intent, intent.requires_timing) == (
        domain,
        shape,
        temporal,
        requires_timing,
    )


def test_absolute_year_routes_as_time_bound_potential() -> None:
    result = _route("Will I get a promotion in 2027?")

    intent = result.intents[0]
    assert intent.shape is QuestionShape.POTENTIAL
    assert intent.temporal_intent is TemporalIntent.TIME_BOUND
    assert intent.requires_timing is True
    assert intent.time_range is not None
    assert intent.time_range.start_date == date(2027, 1, 1)
    assert intent.time_range.end_date == date(2027, 12, 31)
    assert intent.time_range.range_kind is TimeRangeKind.CALENDAR_YEAR
    assert intent.time_range.source is TimeRangeSource.ABSOLUTE


def test_explicit_multi_domain_question_returns_atomic_intents_in_textual_order() -> None:
    result = _route("How will my career and finances be in 2028?")

    assert result.status is RoutingStatus.ROUTABLE
    assert [intent.intent_id for intent in result.intents] == ["intent-1", "intent-2"]
    assert [intent.domain for intent in result.intents] == [
        QuestionDomain.CAREER,
        QuestionDomain.WEALTH,
    ]
    assert all(intent.shape is QuestionShape.DESCRIPTIVE for intent in result.intents)
    assert all(intent.temporal_intent is TemporalIntent.TIME_BOUND for intent in result.intents)
    assert all(intent.requires_timing for intent in result.intents)
    assert all(intent.time_range is not None for intent in result.intents)
    assert result.intents[0].time_range == result.intents[1].time_range


def test_business_and_profits_route_to_business_and_wealth_as_separate_domains() -> None:
    result = _route("How will my business and profits grow?")

    assert [intent.domain for intent in result.intents] == [
        QuestionDomain.BUSINESS,
        QuestionDomain.WEALTH,
    ]
    assert {domain.value for domain in QuestionDomain} == {
        "general",
        "career",
        "business",
        "education",
        "wealth",
        "marriage",
        "health",
        "property",
    }


def test_ambiguous_domain_is_not_silently_routed_to_general() -> None:
    result = _route("How will things be next year?")

    assert result.status is RoutingStatus.NEEDS_CLARIFICATION
    assert result.intents == ()
    assert result.issues == (
        RoutingIssue.AMBIGUOUS_DOMAIN,
        RoutingIssue.REFERENCE_INSTANT_REQUIRED,
    )


def test_relative_time_without_reference_retains_identified_domain_intent() -> None:
    result = _route("How will my career be next year?")

    assert result.status is RoutingStatus.NEEDS_CLARIFICATION
    assert result.issues == (RoutingIssue.REFERENCE_INSTANT_REQUIRED,)
    intent = result.intents[0]
    assert intent.domain is QuestionDomain.CAREER
    assert intent.temporal_intent is TemporalIntent.TIME_BOUND
    assert intent.requires_timing is True
    assert intent.time_range is None
    assert intent.unresolved_relative_time is RelativeTimeExpression.NEXT_YEAR


def test_relative_time_resolves_only_against_explicit_reference_instant() -> None:
    result = _route("What happened with my career last year?", _REFERENCE)

    assert result.status is RoutingStatus.ROUTABLE
    intent = result.intents[0]
    assert intent.shape is QuestionShape.RETROSPECTIVE
    assert intent.temporal_intent is TemporalIntent.HISTORICAL
    assert intent.requires_timing is True
    assert intent.unresolved_relative_time is None
    assert intent.time_range is not None
    assert intent.time_range.start_date == date(2025, 1, 1)
    assert intent.time_range.end_date == date(2025, 12, 31)
    assert intent.time_range.source is TimeRangeSource.RELATIVE_RESOLVED


def test_relative_month_resolution_uses_the_supplied_timezone_aware_reference() -> None:
    india = timezone(timedelta(hours=5, minutes=30))
    reference = datetime(2026, 1, 1, 0, 15, tzinfo=india)
    result = _route("How is my health this month?", reference)

    intent = result.intents[0]
    assert intent.temporal_intent is TemporalIntent.TIME_BOUND
    assert intent.time_range is not None
    assert intent.time_range.range_kind is TimeRangeKind.CALENDAR_MONTH
    assert intent.time_range.start_date == date(2026, 1, 1)
    assert intent.time_range.end_date == date(2026, 1, 31)


def test_absolute_year_span_is_an_inclusive_date_range() -> None:
    result = _route("How will my wealth be between 2028 and 2030?")

    time_range = result.intents[0].time_range
    assert time_range is not None
    assert time_range.range_kind is TimeRangeKind.DATE_RANGE
    assert time_range.start_date == date(2028, 1, 1)
    assert time_range.end_date == date(2030, 12, 31)


def test_current_and_future_general_remain_distinct_from_question_shape() -> None:
    current = _route("How is my career currently?").intents[0]
    future = _route("How will my career be?").intents[0]

    assert current.shape is future.shape is QuestionShape.DESCRIPTIVE
    assert current.temporal_intent is TemporalIntent.CURRENT
    assert future.temporal_intent is TemporalIntent.FUTURE_GENERAL
    assert current.requires_timing is future.requires_timing is False


@pytest.mark.parametrize(
    ("question", "shape"),
    [
        ("Why is my career changing?", QuestionShape.EXPLANATORY),
        ("Compare my career and wealth.", QuestionShape.COMPARATIVE),
    ],
)
def test_additional_question_shapes_are_preserved_without_interpretation(
    question: str, shape: QuestionShape
) -> None:
    result = _route(question)

    assert result.status is RoutingStatus.ROUTABLE
    assert all(intent.shape is shape for intent in result.intents)


def test_unknown_language_is_explicitly_unsupported() -> None:
    result = _route("Tell me my lucky number.")

    assert result.status is RoutingStatus.UNSUPPORTED
    assert result.intents == ()
    assert result.issues == (RoutingIssue.UNSUPPORTED_LANGUAGE,)


def test_domain_aliases_are_bounded_terms_not_substrings() -> None:
    result = _route("How will this object change?")

    assert result.status is RoutingStatus.NEEDS_CLARIFICATION
    assert result.intents == ()
    assert result.issues == (RoutingIssue.AMBIGUOUS_DOMAIN,)


def test_request_preserves_exact_original_question_and_repeated_routing_is_deterministic() -> None:
    question = "  How will my career be in 2028?  "
    request = QuestionRequest(question=question)

    assert request.question == question
    assert _ROUTER.route(request) == _ROUTER.route(request)


def test_models_are_immutable_and_reject_extra_fields_and_unknown_values() -> None:
    request = QuestionRequest(question="How is my career?")
    with pytest.raises(ValidationError):
        request.question = "Changed"
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        QuestionRequest(question="How is my career?", extra="no")
    assert (
        QuestionIntent(
            intent_id="intent-1",
            domain="business",
            shape=QuestionShape.DESCRIPTIVE,
            temporal_intent=TemporalIntent.TIMELESS,
            requires_timing=False,
        ).domain
        is QuestionDomain.BUSINESS
    )
    with pytest.raises(ValidationError, match="timezone-aware"):
        QuestionRequest(question="How is my career?", reference_instant=datetime(2026, 1, 1))


def test_router_has_no_implicit_clock_or_forbidden_runtime_dependencies() -> None:
    source = getsource(QuestionIntentRouter)

    for forbidden in (
        "datetime.now",
        "date.today",
        "EvidencePackage",
        "EvidenceBuilder",
        "GovernedRuleEvaluator",
        "ProductionCorpus",
        "RuleLoader",
        "ChartEngine",
        "Dasha",
        "Transit",
        "Varga",
        "LLM",
    ):
        assert forbidden not in source
