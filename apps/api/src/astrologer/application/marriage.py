"""NEXT-MARRIAGE-01: marriage answers (outlook, timing, year) in the consultation layout.

No reviewed natal or timing rule exists for marriage, so a marriage answer states only:

* calculated chart factors: the 7th lord and its house, Venus and its house, and each one's
  sign dignity as a calculated modifier fact (X2 convention; it changes nothing);
* for a timing or year question, the calculated Vimshottari Mahadasha/Antardasha periods of
  the 7th lord and of Venus in the asked range, with the reviewed Period themes of those
  lords (the X18 lordship principle and the signification terms tagged Marriage (reviewed);
  the 7th lord's line carries the 7th house), and the fact that no reviewed timing rule
  exists for marriage.  No date is predicted and no period is ranked.  NEXT-MARRIAGE-02: no
  reviewed term is tagged Marriage yet, so Period themes list the periods only, then
  ``THEMES_PENDING``;
* NEXT-MARRIAGE-02: calculated D9 (Navamsa) factors (``application.marriage_d9``), facts only.

Out of scope, each with one polite line: compatibility / guna milan (it needs the partner's
chart), Mangal checks, predictions of a marriage ending, and fatalistic questions.

NEXT-WEALTH-01: the answer is built by the generic domain pipeline
(``application.domain_pipeline``) from :data:`MARRIAGE_DOMAIN`; this module keeps the
marriage configuration, texts and scope patterns.  Provisional interpretations are attached
separately, only on request (``application.provisional``).
"""

import re
from collections.abc import Mapping
from datetime import datetime
from enum import StrEnum
from typing import Final

from astrologer.application.domain_pipeline import (
    DomainConfig,
    DomainTexts,
    answer_domain,
    planet_dignity,
)
from astrologer.application.lord_dignity import DIGNITY_PREFIX
from astrologer.application.marriage_d9 import d9_marriage_factors
from astrologer.astrology.chart import Chart
from astrologer.astrology.dasha import VimshottariDashaEngine
from astrologer.composition.marriage_guard import marriage_wording_violation
from astrologer.composition.models import DetailedComposedAnswer
from astrologer.knowledge.models import JyotishDomain
from astrologer.knowledge.signification import SignificationCorpus
from astrologer.questions.models import QuestionDomain, QuestionIntent

__all__ = ["DIGNITY_PREFIX", "planet_dignity"]

MARRIAGE_ANSWER_VERSION: Final = "marriage-answer-v1"
# A "When will I get married?" question with no range lists the next 20 years of periods.
MARRIAGE_TIMING_HORIZON_YEARS: Final = 20
NO_TIMING_RULE: Final = (
    "No reviewed timing rule exists for marriage, so JyotAI gives no date for a marriage."
)
TIMING_STATUS: Final = "Timing rules for marriage: none reviewed yet."
TIMING_STATUS_PERIODS: Final = (
    f"{TIMING_STATUS} The periods above are calculated facts and are not read as a time of "
    "marriage."
)
NO_RANKING: Final = "JyotAI has no approved way to compare periods, so the years are not ranked."
LIMIT_OUTLOOK: Final = (
    "These are calculated chart facts; they do not predict whether or when a marriage will happen."
)
LIMIT_TIMING: Final = (
    "These are calculated periods and reviewed themes; they do not predict whether or when a "
    "marriage will happen."
)
# NEXT-MARRIAGE-02: no reviewed term is tagged Marriage, so Period themes list the periods only.
LIMIT_TIMING_PERIODS_ONLY: Final = (
    "These are calculated periods; they do not predict whether or when a marriage will happen."
)
THEMES_PENDING: Final = "Reviewed marriage meanings for these periods are pending expert review."


class MarriageScope(StrEnum):
    OUTLOOK = "outlook"
    TIMING = "timing"
    COMPATIBILITY = "compatibility"
    MANGAL = "mangal"
    SEPARATION = "separation"
    FATALISTIC = "fatalistic"


OUT_OF_SCOPE_REPLIES: Final[dict[MarriageScope, str]] = {
    MarriageScope.COMPATIBILITY: (
        "Compatibility and guna milan need both partners' charts, and JyotAI reads one chart "
        "only, so it can't assess a match."
    ),
    MarriageScope.MANGAL: (
        "JyotAI doesn't offer Mangal (Mars) checks for marriage; no reviewed method for them "
        "is in the app."
    ),
    MarriageScope.SEPARATION: (
        "JyotAI doesn't make predictions about a marriage ending or a couple separating."
    ),
    MarriageScope.FATALISTIC: (
        "JyotAI doesn't make fixed statements about whether a marriage will or won't happen; "
        'ask "What does my chart say about marriage?" to see the calculated marriage factors '
        "in your chart."
    ),
}
# Checked in this order; the first match decides.
_SCOPE_PATTERNS: Final[tuple[tuple[MarriageScope, re.Pattern[str]], ...]] = (
    (
        MarriageScope.COMPATIBILITY,
        re.compile(
            r"\b(?:compatib\w*|gun(?:a)?\s*milan|ashta\s*koota?|ashtakoot\w*|"
            r"(?:kundli|kundali|horoscope|chart)s?\s+match\w*|match\w*\s+(?:our|my|the|two)\s+"
            r"(?:charts?|kundlis?|kundalis?|horoscopes?)|partner'?s\s+chart|"
            r"(?:his|her|their)\s+(?:chart|kundli|kundali|horoscope)|our\s+charts?)\b"
        ),
    ),
    (
        MarriageScope.MANGAL,
        re.compile(r"\b(?:mangal\w*|manglik|kuja\s+dosh\w*|mars\s+dosh\w*|chevvai\s+dosh\w*)\b"),
    ),
    (
        MarriageScope.SEPARATION,
        re.compile(
            r"\b(?:divorc\w*|separat\w*|break\s*up|broke\s+up|split\s+up|"
            r"end\s+(?:of\s+)?(?:my|our|the)\s+marriage|marriage\s+(?:end|fail)\w*|"
            r"leave\s+my\s+(?:husband|wife|spouse))\b"
        ),
    ),
    (
        MarriageScope.FATALISTIC,
        re.compile(
            r"\b(?:ever\s+(?:get\s+|be\s+)?marr\w*|never\s+(?:get\s+|be\s+)?marr\w*|destin\w*|"
            r"fate|fated|doom\w*|curse\w*|unhapp\w*|(?:stay|remain|always\s+be)\s+single|"
            r"deni\w*|deny|delay\w*|dosh\w*)\b"
        ),
    ),
)


def marriage_scope(question: str, intent: QuestionIntent) -> MarriageScope:
    """Which kind of marriage answer ``question`` gets (language only; no astrology)."""
    normalized = " ".join(question.lower().split())
    for scope, pattern in _SCOPE_PATTERNS:
        if pattern.search(normalized):
            return scope
    if intent.requires_timing or intent.time_range is not None:
        return MarriageScope.TIMING
    return MarriageScope.OUTLOOK


OUTLOOK_LEAD: Final = (
    "No reviewed interpretation for marriage exists yet, so JyotAI shows the calculated "
    "marriage factors in your D1 chart without reading meaning into them"
)
MARRIAGE_DOMAIN: Final = DomainConfig(
    domain=QuestionDomain.MARRIAGE,
    tag_domain=JyotishDomain.MARRIAGE,
    answer_version=MARRIAGE_ANSWER_VERSION,
    houses=(7,),
    karakas=("venus",),
    composer="generic",
    texts=DomainTexts(
        no_timing_rule=NO_TIMING_RULE,
        timing_status=TIMING_STATUS,
        timing_status_periods=TIMING_STATUS_PERIODS,
        no_ranking=NO_RANKING,
        limit_outlook=LIMIT_OUTLOOK,
        limit_timing=LIMIT_TIMING,
        limit_timing_periods_only=LIMIT_TIMING_PERIODS_ONLY,
        themes_pending=THEMES_PENDING,
        outlook_lead=OUTLOOK_LEAD,
    ),
    timing_horizon_years=MARRIAGE_TIMING_HORIZON_YEARS,
    wording_guard=marriage_wording_violation,
    out_of_scope=tuple(
        (scope.value, pattern, OUT_OF_SCOPE_REPLIES[scope]) for scope, pattern in _SCOPE_PATTERNS
    ),
    divisional=d9_marriage_factors,
)


def answer_marriage(
    answer: DetailedComposedAnswer,
    *,
    question: str,
    intent: QuestionIntent,
    chart: Chart,
    facts: Mapping[str, object],
    as_of: datetime,
    dasha_engine: VimshottariDashaEngine,
    corpus: SignificationCorpus,
) -> DetailedComposedAnswer:
    """A marriage answer (see module docstring), built from :data:`MARRIAGE_DOMAIN`.

    ``corpus`` must already be the Marriage view of the reviewed signification corpus
    (``signification_tags.domain_view``): only terms tagged Marriage (reviewed) are shown.
    """
    return answer_domain(
        MARRIAGE_DOMAIN,
        answer,
        question=question,
        intent=intent,
        chart=chart,
        facts=facts,
        as_of=as_of,
        dasha_engine=dasha_engine,
        corpus=corpus,
    )
