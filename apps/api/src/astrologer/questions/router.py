"""Bounded deterministic routing of user language into question intents."""

import re
from calendar import monthrange
from datetime import date

from astrologer.questions.models import (
    QuestionDomain,
    QuestionIntent,
    QuestionRequest,
    QuestionRoutingResult,
    QuestionShape,
    RelativeTimeExpression,
    ResolvedTimeRange,
    RoutingIssue,
    RoutingStatus,
    TemporalIntent,
    TimeRangeKind,
    TimeRangeSource,
)

ROUTER_VERSION = "question-intent-router-v1"

_DOMAIN_PATTERNS: tuple[tuple[QuestionDomain, tuple[str, ...]], ...] = (
    (QuestionDomain.CAREER, ("career", "job", "promotion", "professional")),
    (QuestionDomain.BUSINESS, ("business",)),
    (
        QuestionDomain.EDUCATION,
        ("education", "study", "studies", "academic", "exam", "school", "college"),
    ),
    (QuestionDomain.WEALTH, ("wealth", "finance", "financial", "finances", "profit", "profits")),
    (QuestionDomain.CHILDREN, ("children", "child", "progeny")),
    (QuestionDomain.MARRIAGE, ("marriage", "married", "marry")),
    (QuestionDomain.HEALTH, ("health",)),
    (QuestionDomain.PROPERTY, ("property", "house", "home", "real estate")),
)
_GENERAL_PATTERNS = ("overall reading", "general reading", "overall life")
_RELATIVE_PATTERNS: tuple[tuple[RelativeTimeExpression, str], ...] = (
    (RelativeTimeExpression.THIS_YEAR, r"\bthis year\b"),
    (RelativeTimeExpression.NEXT_YEAR, r"\bnext year\b"),
    (RelativeTimeExpression.LAST_YEAR, r"\blast year\b"),
    (RelativeTimeExpression.THIS_MONTH, r"\bthis month\b"),
    (RelativeTimeExpression.NEXT_MONTH, r"\bnext month\b"),
    (RelativeTimeExpression.LAST_MONTH, r"\blast month\b"),
)


class QuestionIntentRouter:
    """Classify bounded user-language patterns without astrology dependencies."""

    router_version = ROUTER_VERSION

    def route(self, request: QuestionRequest) -> QuestionRoutingResult:
        normalized = " ".join(request.question.lower().split())
        domains = self._domains(normalized)
        shape = self._shape(normalized)
        temporal, time_range, unresolved_relative = self._temporal(normalized, request)
        issues: list[RoutingIssue] = []

        if not domains:
            if self._is_explicitly_general(normalized):
                domains = (QuestionDomain.GENERAL,)
            elif self._looks_like_supported_question(normalized):
                issues.append(RoutingIssue.AMBIGUOUS_DOMAIN)
            else:
                return QuestionRoutingResult(
                    request=request,
                    status=RoutingStatus.UNSUPPORTED,
                    issues=(RoutingIssue.UNSUPPORTED_LANGUAGE,),
                )

        if unresolved_relative is not None:
            issues.append(RoutingIssue.REFERENCE_INSTANT_REQUIRED)

        intents = tuple(
            QuestionIntent(
                intent_id=f"intent-{index}",
                domain=domain,
                shape=shape,
                temporal_intent=temporal,
                requires_timing=temporal
                in {TemporalIntent.TIME_BOUND, TemporalIntent.HISTORICAL, TemporalIntent.MIXED},
                time_range=time_range,
                unresolved_relative_time=unresolved_relative,
            )
            for index, domain in enumerate(domains, start=1)
        )
        return QuestionRoutingResult(
            request=request,
            status=RoutingStatus.NEEDS_CLARIFICATION if issues else RoutingStatus.ROUTABLE,
            intents=intents,
            issues=tuple(issues),
        )

    @staticmethod
    def _domains(question: str) -> tuple[QuestionDomain, ...]:
        found: list[tuple[int, QuestionDomain]] = []
        for domain, phrases in _DOMAIN_PATTERNS:
            positions = [
                match.start()
                for phrase in phrases
                if (match := re.search(rf"\b{re.escape(phrase)}\b", question)) is not None
            ]
            if positions:
                found.append((min(positions), domain))
        return tuple(domain for _, domain in sorted(found))

    @staticmethod
    def _is_explicitly_general(question: str) -> bool:
        return any(phrase in question for phrase in _GENERAL_PATTERNS)

    @staticmethod
    def _looks_like_supported_question(question: str) -> bool:
        return any(
            marker in question
            for marker in ("how", "when", "will", "what", "should", "why", "compare")
        )

    @staticmethod
    def _shape(question: str) -> QuestionShape:
        if re.search(r"\bwhen\b", question):
            return QuestionShape.TIMING
        if re.search(r"\bshould\b", question):
            return QuestionShape.DECISION
        if re.search(r"\bwhat happened\b", question):
            return QuestionShape.RETROSPECTIVE
        if re.search(r"\bwhy\b", question):
            return QuestionShape.EXPLANATORY
        if re.search(r"\b(compare|versus|vs\.?|better)\b", question):
            return QuestionShape.COMPARATIVE
        if re.search(r"\bhow will\b", question):
            return QuestionShape.DESCRIPTIVE
        if re.search(r"(^|\s)(will|can i|do i have|is there)\b", question):
            return QuestionShape.POTENTIAL
        return QuestionShape.DESCRIPTIVE

    def _temporal(
        self, question: str, request: QuestionRequest
    ) -> tuple[TemporalIntent, ResolvedTimeRange | None, RelativeTimeExpression | None]:
        absolute = self._absolute_time_range(question)
        if absolute is not None:
            return TemporalIntent.TIME_BOUND, absolute, None
        for expression, pattern in _RELATIVE_PATTERNS:
            if re.search(pattern, question):
                if request.reference_instant is None:
                    intent = (
                        TemporalIntent.HISTORICAL
                        if expression
                        in {
                            RelativeTimeExpression.LAST_YEAR,
                            RelativeTimeExpression.LAST_MONTH,
                        }
                        else TemporalIntent.TIME_BOUND
                    )
                    return intent, None, expression
                resolved_temporal, resolved_range = self._resolve_relative(
                    expression, request.reference_instant.date()
                )
                return resolved_temporal, resolved_range, None
        if re.search(r"\bwhen\b", question):
            return TemporalIntent.TIME_BOUND, None, None
        if re.search(r"\b(currently|current|now|at present)\b", question):
            return TemporalIntent.CURRENT, None, None
        if re.search(r"\b(how will|will i|future|grow)\b", question):
            return TemporalIntent.FUTURE_GENERAL, None, None
        if re.search(r"\b(happened|previously|past)\b", question):
            return TemporalIntent.HISTORICAL, None, None
        return TemporalIntent.TIMELESS, None, None

    @staticmethod
    def _absolute_time_range(question: str) -> ResolvedTimeRange | None:
        span = re.search(r"\bbetween (\d{4}) and (\d{4})\b", question)
        if span:
            first, last = (int(value) for value in span.groups())
            return ResolvedTimeRange(
                range_kind=TimeRangeKind.DATE_RANGE,
                start_date=date(first, 1, 1),
                end_date=date(last, 12, 31),
                source=TimeRangeSource.ABSOLUTE,
            )
        year = re.search(r"\bin (\d{4})\b", question)
        if year:
            value = int(year.group(1))
            return ResolvedTimeRange(
                range_kind=TimeRangeKind.CALENDAR_YEAR,
                start_date=date(value, 1, 1),
                end_date=date(value, 12, 31),
                source=TimeRangeSource.ABSOLUTE,
            )
        return None

    @staticmethod
    def _resolve_relative(
        expression: RelativeTimeExpression, reference_date: date
    ) -> tuple[TemporalIntent, ResolvedTimeRange]:
        if expression in {
            RelativeTimeExpression.THIS_YEAR,
            RelativeTimeExpression.NEXT_YEAR,
            RelativeTimeExpression.LAST_YEAR,
        }:
            year_offset = {
                RelativeTimeExpression.THIS_YEAR: 0,
                RelativeTimeExpression.NEXT_YEAR: 1,
                RelativeTimeExpression.LAST_YEAR: -1,
            }[expression]
            year = reference_date.year + year_offset
            temporal = TemporalIntent.HISTORICAL if year_offset < 0 else TemporalIntent.TIME_BOUND
            return temporal, ResolvedTimeRange(
                range_kind=TimeRangeKind.CALENDAR_YEAR,
                start_date=date(year, 1, 1),
                end_date=date(year, 12, 31),
                source=TimeRangeSource.RELATIVE_RESOLVED,
            )
        month_offset = {
            RelativeTimeExpression.THIS_MONTH: 0,
            RelativeTimeExpression.NEXT_MONTH: 1,
            RelativeTimeExpression.LAST_MONTH: -1,
        }[expression]
        month_index = reference_date.year * 12 + reference_date.month - 1 + month_offset
        year, month_zero_based = divmod(month_index, 12)
        month = month_zero_based + 1
        temporal = TemporalIntent.HISTORICAL if month_offset < 0 else TemporalIntent.TIME_BOUND
        return temporal, ResolvedTimeRange(
            range_kind=TimeRangeKind.CALENDAR_MONTH,
            start_date=date(year, month, 1),
            end_date=date(year, month, monthrange(year, month)[1]),
            source=TimeRangeSource.RELATIVE_RESOLVED,
        )
