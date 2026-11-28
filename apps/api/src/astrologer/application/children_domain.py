"""NEXT-CHILDREN-01: children answers (outlook, timing, year) in the consultation layout,
built by the generic domain pipeline (``application.domain_pipeline``).

The NEXT-CHILDREN-GUARD-01 hard guards come first and are unchanged: a child-sex question
("Will I have a son?") gets "JyotAI does not predict a child's sex.", and fertility,
pregnancy, "will I have children at all" and counts get one out-of-scope line, before this
pipeline runs (``questions.children_scope``, ``application.children``).  Every section of a
children answer passes the children wording guard first (``children_guard``), then this
domain's guard (``children_domain_guard``: no medical, fatalistic or promising wording).

Domain configuration (:data:`CHILDREN_DOMAIN`): the D1 5th house, its lord, and Jupiter, the
kāraka the text names for children (BPHS, selected edition):

* अथ सूर्यादिग्रहाणां कारकत्वमाह v.5, PDF p. 109: Jupiter is the kāraka of पुत्र, among
  other matters;
* अथ स्थिरकारकमाह v.30, PDF p. 107 (गुरुणा … पुत्र…) and v.33, PDF p. 107 (देवेज्यात्पञ्चमे
  पुत्रो: from Jupiter, the 5th for children);
* अथ भावकारकमाह v.37, PDF p. 108: Jupiter is the bhāva-kāraka of the 5th house.

Where the text says पुत्र, JyotAI shows "children (the text says 'son')" (owner decision).
The reviewer's Sitting 1 verdict names the same factors: "5th house, 5th lord, Jupiter, putra
karaka".  Mars's list (v.3) also has पुत्र inside the compound सत्त्वसद्मभूमिपुत्र…, which can
also be read भूमिपुत्र (an epithet of Mars, "son of the earth"); Mars is not used (a question
in the review pack).

A children answer states only:

* calculated chart factors: the 5th lord and its house, Jupiter and its house, and each
  one's sign dignity as a calculated fact (a modifier only);
* the reviewed natal Children context, when the governed evaluator matched reviewed Children
  rules: only the two the reviewer confirmed in Sitting 1 (item 16, 5th lord in the 11th;
  item 17, 11th lord in the 2nd or 5th; both "Supporting"), quoted verbatim.  The 10th lord in
  the 5th/11th (item 18) is not a Children rule and never shows (it left the manifest);
* for a timing or year question, the calculated Vimshottari Mahadasha/Antardasha periods of
  the 5th lord and Jupiter in the asked range.  No reviewed children timing rule exists, so
  the periods are listed only (no date, no ranking).  No reviewed signification term is tagged
  Children, so Period themes list the periods only, then ``THEMES_PENDING``.

D7 (Saptāṁśa) is not calculated by JyotAI, so no divisional fact is shown (open item).  Out of
scope, one polite line each: a child's health; fatalistic questions (doshas, curses).
Provisional Children rules and significations are attached separately, only on request
(``application.provisional``).
"""

import re
from typing import Final

from astrologer.application.domain_pipeline import DomainConfig, DomainTexts
from astrologer.composition.children_domain_guard import children_domain_violation
from astrologer.knowledge.models import JyotishDomain
from astrologer.questions.models import QuestionDomain

CHILDREN_ANSWER_VERSION: Final = "children-answer-v1"
CHILDREN_TIMING_HORIZON_YEARS: Final = 20
CHILDREN_KARAKAS: Final = ("jupiter",)
NO_TIMING_RULE: Final = (
    "No reviewed timing rule exists for children, so JyotAI gives no date or period for children."
)
TIMING_STATUS: Final = "Timing rules for children: none reviewed yet."
TIMING_STATUS_PERIODS: Final = (
    f"{TIMING_STATUS} The periods above are calculated facts and are not read as the time of a "
    "birth."
)
NO_RANKING: Final = "JyotAI has no approved way to compare periods, so the years are not ranked."
LIMIT_OUTLOOK: Final = (
    "These are calculated chart facts; they do not predict whether or when children will "
    "come, how many, or any medical matter."
)
LIMIT_TIMING: Final = (
    "These are calculated periods and chart facts; they do not predict whether or when "
    "children will come, how many, or any medical matter."
)
THEMES_PENDING: Final = "Reviewed children meanings for these periods are pending expert review."
OUTLOOK_LEAD: Final = (
    "No reviewed Children interpretation is shown for your chart, so JyotAI shows the "
    "calculated children factors in your D1 chart without reading meaning into them"
)
OUTLOOK_LEAD_REVIEWED: Final = (
    "Your D1 chart has reviewed natal Children context, shown below; JyotAI also shows the "
    "calculated children factors in your D1 chart without reading meaning into them"
)

OUT_OF_SCOPE_REPLIES: Final[dict[str, str]] = {
    "health": (
        "JyotAI doesn't comment on a child's health; for medical matters, please consult a doctor."
    ),
    "fatalistic": (
        "JyotAI doesn't make fixed pronouncements about children; ask \"What does my chart say "
        'about children?" to see the calculated children factors in your chart.'
    ),
}
# Checked in this order; the first match decides.  (Child-sex, fertility, pregnancy,
# "whether" and count questions never reach this list: ``questions.children_scope``.)
_SCOPE_PATTERNS: Final[tuple[tuple[str, re.Pattern[str]], ...]] = (
    (
        "health",
        re.compile(
            r"\b(?:health\w*|ill|illness\w*|sick\w*|diseases?|disabilit\w*|disabled|"
            r"bimar\w*|beemar\w*|swasthya)\b"
        ),
    ),
    (
        "fatalistic",
        re.compile(
            r"\b(?:dosh\w*|curse\w*|shraap|shrap|shaap|destin\w*|fate|fated|doom\w*|"
            r"punish\w*)\b"
        ),
    ),
)

CHILDREN_DOMAIN: Final = DomainConfig(
    domain=QuestionDomain.CHILDREN,
    tag_domain=JyotishDomain.CHILDREN,
    answer_version=CHILDREN_ANSWER_VERSION,
    houses=(5,),
    karakas=CHILDREN_KARAKAS,
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
    timing_horizon_years=CHILDREN_TIMING_HORIZON_YEARS,
    wording_guard=children_domain_violation,
    out_of_scope=tuple(
        (scope, pattern, OUT_OF_SCOPE_REPLIES[scope]) for scope, pattern in _SCOPE_PATTERNS
    ),
)
