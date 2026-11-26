"""NEXT-WEALTH-01: wealth answers (outlook, timing, year), provisional, in the consultation
layout, built by the generic domain pipeline (``application.domain_pipeline``).

Domain configuration (:data:`WEALTH_DOMAIN`): the D1 2nd house (धन) and 11th house (लाभ),
their lords, and Jupiter as kāraka.  A wealth answer states only:

* calculated chart factors: the 2nd lord and the 11th lord with their houses, Jupiter and
  its house, and each one's sign dignity as a calculated fact (a modifier only);
* the reviewed natal Wealth context, when the governed evaluator matched reviewed Wealth
  rules (``jyotish.production.cumulative``), quoted verbatim;
* for a timing or year question, the calculated Vimshottari Mahadasha/Antardasha periods of
  the 2nd lord, the 11th lord and Jupiter in the asked range.  No reviewed wealth timing rule
  exists, so the periods are listed only (no date, no ranking).  No reviewed signification
  term is tagged Wealth, so Period themes list the periods only, then ``THEMES_PENDING``;
  a Wealth answer never shows a Career or Marriage term.

No divisional chart is shown for wealth (no reviewed method; D2 is calculated but not used).
Out of scope, one polite line each: investment, trading or gambling advice; amounts of money;
fatalistic questions (poverty, losses, debt, "will I ever be rich").  Provisional Wealth
rules and significations are attached separately, only on request
(``application.provisional``).
"""

import re
from typing import Final

from astrologer.application.domain_pipeline import DomainConfig, DomainTexts
from astrologer.composition.wealth_guard import wealth_wording_violation
from astrologer.knowledge.models import JyotishDomain
from astrologer.questions.models import QuestionDomain

WEALTH_ANSWER_VERSION: Final = "wealth-answer-v1"
WEALTH_TIMING_HORIZON_YEARS: Final = 20
NO_TIMING_RULE: Final = (
    "No reviewed timing rule exists for wealth, so JyotAI gives no date or period for wealth."
)
TIMING_STATUS: Final = "Timing rules for wealth: none reviewed yet."
TIMING_STATUS_PERIODS: Final = (
    f"{TIMING_STATUS} The periods above are calculated facts and are not read as a time of "
    "financial gain."
)
NO_RANKING: Final = "JyotAI has no approved way to compare periods, so the years are not ranked."
LIMIT_OUTLOOK: Final = (
    "These are calculated chart facts; they do not predict income, an amount of money or a "
    "financial outcome."
)
LIMIT_TIMING: Final = (
    "These are calculated periods and chart facts; they do not predict income, an amount of "
    "money or a financial outcome."
)
THEMES_PENDING: Final = "Reviewed wealth meanings for these periods are pending expert review."
OUTLOOK_LEAD: Final = (
    "No reviewed Wealth interpretation is shown for your chart, so JyotAI shows the calculated "
    "wealth factors in your D1 chart without reading meaning into them"
)
OUTLOOK_LEAD_REVIEWED: Final = (
    "Your D1 chart has reviewed natal Wealth context, shown below; JyotAI also shows the "
    "calculated wealth factors in your D1 chart without reading meaning into them"
)

OUT_OF_SCOPE_REPLIES: Final[dict[str, str]] = {
    "investment": (
        "JyotAI doesn't give investment, trading or gambling advice; for financial decisions, "
        "please consult a qualified financial adviser."
    ),
    "amount": (
        "JyotAI doesn't predict amounts of money or income; ask \"What does my chart say about "
        'wealth?" to see the calculated wealth factors in your chart.'
    ),
    "fatalistic": (
        "JyotAI doesn't make fixed statements about whether someone will or won't have wealth; "
        'ask "What does my chart say about wealth?" to see the calculated wealth factors in '
        "your chart."
    ),
}
# Checked in this order; the first match decides.
_SCOPE_PATTERNS: Final[tuple[tuple[str, re.Pattern[str]], ...]] = (
    (
        "investment",
        re.compile(
            r"\b(?:invest\w*|stocks?|shares?|share\s+market|crypto\w*|bitcoin|lotter(?:y|ies)|"
            r"gambl\w*|betting|bets?|trading|speculat\w*|mutual\s+funds?)\b"
        ),
    ),
    (
        "amount",
        re.compile(
            r"\b(?:how\s+much|exact\s+amount|net\s+worth|millionaire|billionaire|crores?|"
            r"lakhs?)\b"
        ),
    ),
    (
        "fatalistic",
        re.compile(
            r"\b(?:poor|poverty|bankrupt\w*|broke|debts?|lose|losing|loss(?:es)?|lost|ruin\w*|"
            r"(?:ever|never)\s+(?:be|become|get)\s+(?:rich|wealthy)|destin\w*|fate|fated|"
            r"curse\w*|dosh\w*)\b"
        ),
    ),
)

WEALTH_DOMAIN: Final = DomainConfig(
    domain=QuestionDomain.WEALTH,
    tag_domain=JyotishDomain.WEALTH,
    answer_version=WEALTH_ANSWER_VERSION,
    houses=(2, 11),
    karakas=("jupiter",),
    composer="generic",
    texts=DomainTexts(
        no_timing_rule=NO_TIMING_RULE,
        timing_status=TIMING_STATUS,
        timing_status_periods=TIMING_STATUS_PERIODS,
        no_ranking=NO_RANKING,
        limit_outlook=LIMIT_OUTLOOK,
        limit_timing=LIMIT_TIMING,
        limit_timing_periods_only=LIMIT_TIMING,
        themes_pending=THEMES_PENDING,
        outlook_lead=OUTLOOK_LEAD,
        outlook_lead_reviewed=OUTLOOK_LEAD_REVIEWED,
    ),
    timing_horizon_years=WEALTH_TIMING_HORIZON_YEARS,
    wording_guard=wealth_wording_violation,
    out_of_scope=tuple(
        (scope, pattern, OUT_OF_SCOPE_REPLIES[scope]) for scope, pattern in _SCOPE_PATTERNS
    ),
)
