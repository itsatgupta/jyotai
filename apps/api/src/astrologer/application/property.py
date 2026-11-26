"""NEXT-PROPERTY-01: property answers (outlook, timing, year), provisional, in the consultation
layout, built by the generic domain pipeline (``application.domain_pipeline``).

Domain configuration (:data:`PROPERTY_DOMAIN`): the D1 4th house, its lord, and the kārakas the
text itself names for land, a house or vehicles, each with a high-confidence reading (BPHS,
कारकाध्यायः, अथ सूर्यादिग्रहाणां कारकत्वमाह, PDF p. 109):

* **Mars**: भूमि (land) and सद्म (dwelling), v.3;
* **Jupiter**: गृह (house), v.5;
* **Venus**: यान (vehicles), v.6.

The Sun's list (v.1) also names क्षेत्र (field); that reading is medium confidence (the word
stands among राज्य, वन, पर्वत and may mean a region), so the Sun is a provisional signification
only and not a Property kāraka of the answer.  The bhāva-kāraka list (v.37) gives the 4th house
as a whole to the Moon (Sanskrit सोमः; the Hindi has Mercury) and names no property matter;
it is a question for the reviewer and is not used.

A property answer states only:

* calculated chart factors: the 4th lord and its house, Mars, Jupiter and Venus and their
  houses, and each one's sign dignity as a calculated fact (a modifier only);
* for a timing or year question, the calculated Vimshottari Mahadasha/Antardasha periods of
  the 4th lord, Mars, Jupiter and Venus in the asked range.  No reviewed property timing rule
  exists, so the periods are listed only (no date, no ranking).  No reviewed signification
  term is tagged Property, so Period themes list the periods only, then ``THEMES_PENDING``;
  a Property answer never shows a Career, Marriage or Wealth term.

No reviewed natal Property rule exists.  No divisional chart is shown: D4 (Chaturthāṁśa) is
not calculated by JyotAI (open item).  Out of scope, one polite line each: prices and values;
advice to buy, sell or invest; legal matters; fatalistic questions (losing a home, accidents,
"will I ever own a house").  Provisional Property rules and significations are attached
separately, only on request (``application.provisional``).
"""

import re
from typing import Final

from astrologer.application.domain_pipeline import DomainConfig, DomainTexts
from astrologer.composition.property_guard import property_wording_violation
from astrologer.knowledge.models import JyotishDomain
from astrologer.questions.models import QuestionDomain

PROPERTY_ANSWER_VERSION: Final = "property-answer-v1"
PROPERTY_TIMING_HORIZON_YEARS: Final = 20
PROPERTY_KARAKAS: Final = ("mars", "jupiter", "venus")
NO_TIMING_RULE: Final = (
    "No reviewed timing rule exists for property, so JyotAI gives no date or period for property."
)
TIMING_STATUS: Final = "Timing rules for property: none reviewed yet."
TIMING_STATUS_PERIODS: Final = (
    f"{TIMING_STATUS} The periods above are calculated facts and are not read as a time to "
    "acquire a home, land or a vehicle."
)
NO_RANKING: Final = "JyotAI has no approved way to compare periods, so the years are not ranked."
LIMIT_OUTLOOK: Final = (
    "These are calculated chart facts; they do not predict a purchase, a sale, a price or a "
    "legal outcome."
)
LIMIT_TIMING: Final = (
    "These are calculated periods and chart facts; they do not predict a purchase, a sale, a "
    "price or a legal outcome."
)
THEMES_PENDING: Final = "Reviewed property meanings for these periods are pending expert review."
OUTLOOK_LEAD: Final = (
    "No reviewed Property interpretation is shown for your chart, so JyotAI shows the "
    "calculated property factors in your D1 chart without reading meaning into them"
)

OUT_OF_SCOPE_REPLIES: Final[dict[str, str]] = {
    "price": (
        "JyotAI doesn't predict property prices, values or costs; ask \"What does my chart say "
        'about property?" to see the calculated property factors in your chart.'
    ),
    "advice": (
        "JyotAI doesn't advise whether to buy, sell or invest in property; for that decision, "
        "please consult a qualified property or financial adviser."
    ),
    "legal": (
        "JyotAI doesn't comment on legal matters or court cases about property; for those, "
        "please consult a qualified lawyer."
    ),
    "fatalistic": (
        "JyotAI doesn't make fixed statements about whether someone will or won't have a home, "
        'land or a vehicle; ask "What does my chart say about property?" to see the '
        "calculated property factors in your chart."
    ),
}
# Checked in this order; the first match decides.
_SCOPE_PATTERNS: Final[tuple[tuple[str, re.Pattern[str]], ...]] = (
    (
        "price",
        re.compile(
            r"\b(?:prices?|pricing|priced|costs?|costly|rates?|values?|valuation|worth|"
            r"apprecia\w*|depreciat\w*|how\s+much|kitn[aei]|lakhs?|crores?)\b"
        ),
    ),
    (
        "advice",
        re.compile(
            r"\b(?:should\s+i\s+(?:buy|sell|purchase|invest|rent)|"
            r"(?:good|right|best|auspicious|lucky)\s+(?:time|year|month|day)\s+to\s+"
            r"(?:buy|sell|purchase|invest)|good\s+idea\s+to\s+(?:buy|sell|purchase|invest)|"
            r"(?:buy|sell)\s+or\s+(?:rent|wait|sell|buy|not)|invest\w*|nivesh|"
            r"(?:kharid|bech)\w*\s.*\bchahiye)\b"
        ),
    ),
    (
        "legal",
        re.compile(
            r"\b(?:legal\w*|court|courts|lawsuits?|litigation|disputes?|disputed|lawyers?|"
            r"advocates?|title\s+deeds?|encroach\w*|evict\w*|mukadma\w*|kanooni)\b"
        ),
    ),
    (
        "fatalistic",
        re.compile(
            r"\b(?:lose|losing|lost|loss(?:es)?|(?:ever|never)\s+(?:own|have|get|buy)|"
            r"destin\w*|fate|fated|curse\w*|dosh\w*|accidents?|stolen|theft)\b"
        ),
    ),
)

PROPERTY_DOMAIN: Final = DomainConfig(
    domain=QuestionDomain.PROPERTY,
    tag_domain=JyotishDomain.PROPERTY,
    answer_version=PROPERTY_ANSWER_VERSION,
    houses=(4,),
    karakas=PROPERTY_KARAKAS,
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
    ),
    timing_horizon_years=PROPERTY_TIMING_HORIZON_YEARS,
    wording_guard=property_wording_violation,
    out_of_scope=tuple(
        (scope, pattern, OUT_OF_SCOPE_REPLIES[scope]) for scope, pattern in _SCOPE_PATTERNS
    ),
)
