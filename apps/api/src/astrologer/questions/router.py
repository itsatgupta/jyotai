"""Bounded deterministic routing of user language into question intents."""

import re
from calendar import monthrange
from datetime import date

from pydantic import ValidationError

from astrologer.questions.models import (
    CareerQuestionFocus,
    QuestionDomain,
    QuestionIntent,
    QuestionRequest,
    QuestionRoutingResult,
    QuestionShape,
    RelativeTimeExpression,
    RequestedTimingPrecision,
    ResolvedTimeRange,
    RoutingIssue,
    RoutingStatus,
    TemporalIntent,
    TimeRangeKind,
    TimeRangeSource,
)

ROUTER_VERSION = "question-intent-router-v1"

_DOMAIN_PATTERNS: tuple[tuple[QuestionDomain, tuple[str, ...]], ...] = (
    (
        QuestionDomain.CAREER,
        ("career", "job", "promotion", "promoted", "profession", "occupation", "professional"),
    ),
    (QuestionDomain.BUSINESS, ("business",)),
    (
        QuestionDomain.EDUCATION,
        ("education", "study", "studies", "academic", "exam", "school", "college"),
    ),
    (QuestionDomain.WEALTH, ("wealth", "finance", "financial", "finances", "profit", "profits")),
    (QuestionDomain.CHILDREN, ("children", "child", "progeny")),
    (
        QuestionDomain.SPIRITUALITY,
        ("spirituality", "spiritual", "dharma", "dharmic", "devotional", "worship"),
    ),
    (
        QuestionDomain.TRAVEL,
        ("travel", "foreign", "abroad", "relocate", "relocation", "move abroad"),
    ),
    (
        QuestionDomain.FRIENDS,
        ("friends", "friend", "friendship", "friendships", "social network"),
    ),
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
        domain_text = re.sub(
            r"\b(?:first|second|third|fourth|fifth|sixth|"
            r"seventh|eighth|ninth|tenth|eleventh|twelfth|"
            r"\d+(?:st|nd|rd|th))[- ]house[- ]lord\b",
            "lord",
            normalized,
        )
        domains = self._domains(domain_text)
        comparison_years = self._comparison_years(normalized)
        shape = QuestionShape.COMPARATIVE if comparison_years else self._shape(normalized)
        try:
            temporal, time_range, unresolved_relative = self._temporal(normalized, request)
        except (ValueError, ValidationError):
            return QuestionRoutingResult(
                request=request,
                status=RoutingStatus.NEEDS_CLARIFICATION,
                issues=(RoutingIssue.INVALID_TIME_RANGE,),
            )
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
                career_focus=self._career_focus(normalized, comparison_years)
                if domain is QuestionDomain.CAREER
                else None,
                requested_timing_precision=self._requested_precision(normalized)
                if domain is QuestionDomain.CAREER
                else None,
                comparison_years=comparison_years if domain is QuestionDomain.CAREER else (),
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
        if re.search(r"\b(when|which (?:exact )?month|what (?:exact )?date)\b", question):
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
        if re.search(r"\b(when|which (?:exact )?month|what (?:exact )?date)\b", question):
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
        dates = re.search(
            r"\b(?:between|from) (\d{4}-\d{2}-\d{2}) (?:and|to) (\d{4}-\d{2}-\d{2})\b",
            question,
        )
        if dates:
            return ResolvedTimeRange(
                range_kind=TimeRangeKind.DATE_RANGE,
                start_date=date.fromisoformat(dates.group(1)),
                end_date=date.fromisoformat(dates.group(2)),
                source=TimeRangeSource.ABSOLUTE,
            )
        span = re.search(r"\b(?:between|from) (\d{4}) (?:and|to) (\d{4})\b", question)
        if span:
            first, last = (int(value) for value in span.groups())
            return ResolvedTimeRange(
                range_kind=TimeRangeKind.DATE_RANGE,
                start_date=date(first, 1, 1),
                end_date=date(last, 12, 31),
                source=TimeRangeSource.ABSOLUTE,
            )
        comparison = QuestionIntentRouter._comparison_years(question)
        if comparison:
            return ResolvedTimeRange(
                range_kind=TimeRangeKind.DATE_RANGE,
                start_date=date(min(comparison), 1, 1),
                end_date=date(max(comparison), 12, 31),
                source=TimeRangeSource.ABSOLUTE,
            )
        month_names = (
            "january|february|march|april|may|june|july|august|september|october|november|december"
        )
        month = re.search(rf"\bin ({month_names}) (\d{{4}})\b", question)
        if month:
            value = int(month.group(2))
            month_number = (
                "january",
                "february",
                "march",
                "april",
                "may",
                "june",
                "july",
                "august",
                "september",
                "october",
                "november",
                "december",
            ).index(month.group(1)) + 1
            return ResolvedTimeRange(
                range_kind=TimeRangeKind.CALENDAR_MONTH,
                start_date=date(value, month_number, 1),
                end_date=date(value, month_number, monthrange(value, month_number)[1]),
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
    def _comparison_years(question: str) -> tuple[int, ...]:
        if re.search(r"\b\d{4}-\d{2}-\d{2}\b", question):
            return ()
        if re.search(r"\b(?:between|from) \d{4} (?:and|to) \d{4}\b", question):
            return ()
        if not (
            re.search(r"\b(compare|versus|vs\.?|better|or)\b", question)
            or re.search(r"\b(?:19|20)\d{2} and (?:19|20)\d{2}\b", question)
        ):
            return ()
        years = tuple(
            dict.fromkeys(int(year) for year in re.findall(r"\b(?:19|20)\d{2}\b", question))
        )
        return years if len(years) >= 2 else ()

    @staticmethod
    def _requested_precision(question: str) -> RequestedTimingPrecision | None:
        if re.search(r"\b(exact|specific|precise)\s+(day|date)\b", question):
            return RequestedTimingPrecision.EXACT_DATE
        if re.search(r"\b(exact|specific|precise)\s+month\b", question):
            return RequestedTimingPrecision.EXACT_MONTH
        if re.search(r"\b(which|what)\s+month\b", question):
            return RequestedTimingPrecision.MONTH
        return RequestedTimingPrecision.BROAD

    @staticmethod
    def _career_focus(question: str, years: tuple[int, ...]) -> CareerQuestionFocus:
        if years:
            return CareerQuestionFocus.COMPARISON
        if re.search(r"\b(promotion|promoted)\b", question):
            return CareerQuestionFocus.PROMOTION
        if re.search(r"\b(profession|occupation|career path|which job|what job)\b", question):
            return CareerQuestionFocus.PROFESSION
        if re.search(r"\b(strength|strengths|talent|talents)\b", question):
            return CareerQuestionFocus.STRENGTHS
        if re.search(r"\b(develop|development|progress|trajectory|grow|growth)\b", question):
            return CareerQuestionFocus.DEVELOPMENT
        if re.search(
            r"\b(when|timing|period|which (?:exact )?month|in (?:19|20)\d{2})\b", question
        ):
            return CareerQuestionFocus.PERIOD
        return CareerQuestionFocus.PLACEMENT

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
