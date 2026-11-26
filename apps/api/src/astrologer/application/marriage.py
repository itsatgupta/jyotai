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

Every sentence passes the marriage wording guard (no fear-based or fatalistic wording) and
the ranking and evaluative guards; admitted signification terms are quoted verbatim and
excluded from those checks.  A failing sentence is dropped (fail closed).  Provisional
interpretations are attached separately, only on request (``application.provisional``).
"""

import logging
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta, tzinfo
from enum import StrEnum
from typing import Final, Literal

from astrologer.application.career_synthesis import VIMSHOTTARI_METHODOLOGY_ID
from astrologer.application.marriage_d9 import d9_marriage_factors
from astrologer.astrology.chart import Chart
from astrologer.astrology.dasha import VimshottariDashaEngine
from astrologer.composition.comparison_guard import ranking_violation
from astrologer.composition.evaluative_guard import evaluative_violation
from astrologer.composition.marriage_guard import marriage_wording_violation
from astrologer.composition.models import (
    ConsultationSection,
    DetailedComposedAnswer,
    SynthesisSentence,
)
from astrologer.knowledge.signification import SignificationCorpus, SignificationEntry
from astrologer.knowledge.signification_admit02_v1 import PERIOD_THEMES_CLOSING_V2
from astrologer.questions.models import (
    QuestionIntent,
    QuestionShape,
    TemporalIntent,
    TimeRangeKind,
)

MARRIAGE_ANSWER_VERSION: Final = "marriage-answer-v1"
# A "When will I get married?" question with no range lists the next 20 years of periods.
MARRIAGE_TIMING_HORIZON_YEARS: Final = 20
_DASHA_YEAR_DAYS: Final = 365.25
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
DIGNITY_PREFIX: Final = "Calculated fact (sign dignity, shown as a modifier only)"
_LOGGER = logging.getLogger(__name__)
_ListKind = Literal["chart_factors", "periods", "period_themes", "dasha", "d9_factors"]


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


@dataclass(frozen=True)
class _Window:
    start: datetime
    end: datetime
    phrase: str


@dataclass(frozen=True)
class _Listed:
    lord: str
    role: str
    sentence: SynthesisSentence


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
    """Rebuild a marriage answer's text and consultation sections (see module docstring).

    ``corpus`` must already be the Marriage view of the reviewed signification corpus
    (``signification_tags.domain_view``): only terms tagged Marriage (reviewed) are shown.
    """
    scope = marriage_scope(question, intent)
    if scope in OUT_OF_SCOPE_REPLIES:
        line = OUT_OF_SCOPE_REPLIES[scope]
        return _finish(answer, (ConsultationSection(kind="direct", text=line),), ())
    seventh = _string(facts.get("jyotish.d1.house.7.lord"))
    factors = _chart_factors(facts, seventh)
    window = _window(intent, as_of) if scope is MarriageScope.TIMING else None
    if window is None:
        direct = _outlook_direct(facts, seventh)
        sections = [ConsultationSection(kind="direct", text=direct)]
        if scope is MarriageScope.TIMING:  # an unbounded past question: no range to list
            sections[0] = ConsultationSection(kind="direct", text=f"{NO_TIMING_RULE} {direct}")
        sections += _sentences_section("chart_factors", factors)
        sections += _sentences_section("d9_factors", d9_marriage_factors(chart, facts))
        sections.append(ConsultationSection(kind="limit", text=LIMIT_OUTLOOK))
        return _finish(answer, tuple(sections), ())

    targets = tuple(dict.fromkeys(lord for lord in (seventh, "venus") if lord is not None))
    listed, running = _periods(chart, dasha_engine, window, targets, seventh, as_of)
    themes, admitted_terms = _themes_section(listed, facts, corpus, seventh)
    sections = [
        ConsultationSection(
            kind="direct",
            text=_timing_direct(window, seventh, bool(listed), intent, bool(admitted_terms)),
        )
    ]
    sections += _sentences_section("periods", tuple(item.sentence for item in listed))
    sections += themes
    sections += _sentences_section("chart_factors", factors)
    sections += _sentences_section("d9_factors", d9_marriage_factors(chart, facts))
    status = TIMING_STATUS_PERIODS if listed else TIMING_STATUS
    sections.append(ConsultationSection(kind="timing_status", text=status))
    if running:
        sections += _sentences_section("dasha", running)
    limit = LIMIT_TIMING if admitted_terms else LIMIT_TIMING_PERIODS_ONLY
    sections.append(ConsultationSection(kind="limit", text=limit))
    return _finish(answer, tuple(sections), admitted_terms)


def _finish(
    answer: DetailedComposedAnswer,
    sections: tuple[ConsultationSection, ...],
    admitted_terms: Sequence[str],
) -> DetailedComposedAnswer:
    clean = tuple(section for section in sections if _clean(section, admitted_terms))
    return answer.model_copy(
        update={
            "answer": " ".join(section.text for section in clean),
            "consultation_sections": clean,
            "limitations": (),
            "corpus_limitation": True,
            "timing_answered": False,
        }
    )


def _clean(section: ConsultationSection, admitted_terms: Sequence[str]) -> bool:
    """Guards on one section; admitted signification terms (and the reviewer's closing) are
    quoted verbatim and excluded from the ranking and evaluative checks."""
    allowed = (*admitted_terms, PERIOD_THEMES_CLOSING_V2)
    remaining = section.text
    for passage in sorted(set(allowed), key=len, reverse=True):
        remaining = remaining.replace(passage, " ")
    bad = (
        marriage_wording_violation(section.text)
        or ranking_violation(remaining)
        or evaluative_violation(remaining)
    )
    if bad is not None:
        _LOGGER.warning("marriage section %s dropped by guard: %r", section.kind, bad)
        return False
    return True


def _sentences_section(
    kind: _ListKind, sentences: Sequence[SynthesisSentence]
) -> list[ConsultationSection]:
    if not sentences:
        return []
    return [
        ConsultationSection(
            kind=kind,
            text=" ".join(sentence.text for sentence in sentences),
            synthesis_sentences=tuple(sentences),
        )
    ]


def _chart_factors(
    facts: Mapping[str, object], seventh: str | None
) -> tuple[SynthesisSentence, ...]:
    sentences: list[SynthesisSentence] = []
    house = _int(facts.get("jyotish.d1.house_lord.7.placement_house"))
    if seventh is not None and house is not None:
        sentences.append(
            SynthesisSentence(
                text=f"Your 7th lord is {seventh.title()}, placed in the {_ordinal(house)} house.",
                fact_ids=("jyotish.d1.house.7.lord", "jyotish.d1.house_lord.7.placement_house"),
            )
        )
    if seventh is not None and (dignity := planet_dignity(facts, seventh, "your 7th lord")):
        sentences.append(dignity)
    venus_house = _int(facts.get("jyotish.d1.planet.venus.placement_house"))
    if venus_house is not None:
        role = ", your 7th lord," if seventh == "venus" else ""
        sentences.append(
            SynthesisSentence(
                text=f"Venus{role} is placed in the {_ordinal(venus_house)} house.",
                fact_ids=("jyotish.d1.planet.venus.placement_house",),
            )
        )
    if seventh != "venus" and (dignity := planet_dignity(facts, "venus", None)):
        sentences.append(dignity)
    return tuple(sentences)


def planet_dignity(
    facts: Mapping[str, object], planet: str, role: str | None
) -> SynthesisSentence | None:
    """'Calculated fact (…): Venus is in its own sign.' from the existing D1 dignity facts.

    X2 convention: sign dignity is a modifier only; the sentence never calls a planet strong
    or weak.  None when any of the three facts is unavailable (UNKNOWN is never FALSE).
    """
    held: list[str] = []
    fact_ids: list[str] = []
    for kind, phrase in (
        ("own_sign", "its own sign"),
        ("exaltation_sign", "its exaltation sign"),
        ("debilitation_sign", "its debilitation sign"),
    ):
        fact_id = f"jyotish.d1.planet.{planet}.{kind}"
        value = facts.get(fact_id)
        if not isinstance(value, bool):
            return None
        fact_ids.append(fact_id)
        if value:
            held.append(phrase)
    state = (
        "is in " + " and ".join(held)
        if held
        else "is in none of its own, exaltation or debilitation signs"
    )
    subject = f"{role}, {planet.title()}," if role else planet.title()
    return SynthesisSentence(text=f"{DIGNITY_PREFIX}: {subject} {state}.", fact_ids=tuple(fact_ids))


def _outlook_direct(facts: Mapping[str, object], seventh: str | None) -> str:
    parts: list[str] = []
    house = _int(facts.get("jyotish.d1.house_lord.7.placement_house"))
    if seventh is not None and house is not None:
        parts.append(f"your 7th lord, {seventh.title()}, is in the {_ordinal(house)} house")
    venus_house = _int(facts.get("jyotish.d1.planet.venus.placement_house"))
    if venus_house is not None and seventh != "venus":
        parts.append(f"Venus is in the {_ordinal(venus_house)} house")
    lead = (
        "No reviewed interpretation for marriage exists yet, so JyotAI shows the calculated "
        "marriage factors in your D1 chart without reading meaning into them"
    )
    return f"{lead}: {' and '.join(parts)}." if parts else f"{lead}."


def _timing_direct(
    window: _Window, seventh: str | None, found: bool, intent: QuestionIntent, themed: bool
) -> str:
    if seventh is None:  # the 7th lord fact is unavailable: Venus only (UNKNOWN is not FALSE)
        who, absent = "Venus", "Venus has no"
    elif seventh == "venus":
        who, absent = "your 7th lord, Venus", "your 7th lord, Venus, has no"
    else:
        name = seventh.title()
        who = f"your 7th lord, {name}, and of Venus"
        absent = f"neither your 7th lord, {name}, nor Venus has a"
    if found:
        themes = " with their reviewed Period themes" if themed else ""
        body = (
            f"{window.phrase}, the Mahadasha and Antardasha periods of {who} are listed "
            f"below{themes}."
        )
    else:
        body = f"{window.phrase}, {absent} Mahadasha or Antardasha period."
    text = f"{NO_TIMING_RULE} {body}"
    if intent.shape is QuestionShape.COMPARATIVE:
        text = f"{text} {NO_RANKING}"
    return text


def _window(intent: QuestionIntent, as_of: datetime) -> _Window | None:
    zone = as_of.tzinfo
    assert zone is not None  # validated by the request model
    scope = intent.time_range
    if scope is not None:
        start = datetime.combine(scope.start_date, datetime.min.time(), tzinfo=zone)
        end = datetime.combine(scope.end_date + timedelta(days=1), datetime.min.time(), tzinfo=zone)
        if scope.range_kind is TimeRangeKind.CALENDAR_YEAR:
            phrase = f"In {scope.start_date.year}"
        elif scope.range_kind is TimeRangeKind.CALENDAR_MONTH:
            phrase = f"In {scope.start_date.strftime('%B %Y')}"
        else:
            phrase = f"From {_date(start)} to {_date(end - timedelta(days=1))}"
        return _Window(start.astimezone(UTC), end.astimezone(UTC), phrase)
    if intent.temporal_intent is TemporalIntent.HISTORICAL:
        return None
    start = as_of.astimezone(UTC)
    end = start + timedelta(days=_DASHA_YEAR_DAYS * MARRIAGE_TIMING_HORIZON_YEARS)
    phrase = (
        f"In the next {MARRIAGE_TIMING_HORIZON_YEARS} years "
        f"({_date(as_of)} to {_date(end.astimezone(zone))})"
    )
    return _Window(start, end, phrase)


def _periods(
    chart: Chart,
    engine: VimshottariDashaEngine,
    window: _Window,
    targets: tuple[str, ...],
    seventh: str | None,
    as_of: datetime,
) -> tuple[list[_Listed], tuple[SynthesisSentence, ...]]:
    """The 7th lord's and Venus's MD/AD periods overlapping the window, in time order, and
    (for a window of at most a year) every MD/AD segment running in it."""
    if window.end <= chart.birth_input.utc_datetime:
        return [], ()
    timeline = engine.calculate(chart, window.end)
    zone = as_of.tzinfo
    assert zone is not None  # validated by the request model
    listed: list[_Listed] = []
    running: list[SynthesisSentence] = []
    short = window.end - window.start <= timedelta(days=367)
    for major in timeline.mahadashas:
        if major.end <= window.start or major.start >= window.end:
            continue
        if major.lord.value in targets:
            listed.append(
                _Listed(
                    major.lord.value,
                    "Mahadasha",
                    _period_sentence(
                        f"{major.lord.value.title()}{_role(major.lord.value, seventh)} Mahadasha",
                        major.start,
                        major.end,
                        zone,
                    ),
                )
            )
        for minor in major.antardashas:
            if minor.end <= window.start or minor.start >= window.end:
                continue
            label = (
                f"{minor.lord.value.title()}{_role(minor.lord.value, seventh)} Antardasha "
                f"in the {major.lord.value.title()} Mahadasha"
            )
            if minor.lord.value in targets:
                listed.append(
                    _Listed(
                        minor.lord.value,
                        "Antardasha",
                        _period_sentence(label, minor.start, minor.end, zone),
                    )
                )
            if short:
                running.append(
                    _period_sentence(
                        f"Running: {major.lord.value.title()} Mahadasha / "
                        f"{minor.lord.value.title()} Antardasha",
                        minor.start,
                        minor.end,
                        zone,
                    )
                )
    return listed, tuple(running)


def _period_sentence(label: str, start: datetime, end: datetime, zone: tzinfo) -> SynthesisSentence:
    return SynthesisSentence(
        text=f"{label}: {_date(start.astimezone(zone))} to {_date(end.astimezone(zone))}.",
        calc_method_ids=(VIMSHOTTARI_METHODOLOGY_ID,),
    )


def _role(lord: str, seventh: str | None) -> str:
    return " (your 7th lord)" if lord == seventh else ""


def _themes_section(
    listed: Sequence[_Listed],
    facts: Mapping[str, object],
    corpus: SignificationCorpus,
    seventh: str | None,
) -> tuple[list[ConsultationSection], tuple[str, ...]]:
    """X18 compact Period-themes lines, one per listed lord, then the reviewer's closing;
    also the admitted terms quoted (excluded from the guards).

    NEXT-MARRIAGE-02: when no listed lord has a Marriage-tagged reviewed term, the section
    lists the periods only (one line per lord, no terms) and ``THEMES_PENDING``.
    """
    principle = corpus.lordship_principle
    if not listed:
        return [], ()
    if principle is None:
        return _pending_section(listed, seventh), ()
    principle_id = f"{principle.rule_id}@{principle.rule_version}"
    template = principle.approved_template_version
    sentences: list[SynthesisSentence] = []
    terms: list[str] = []
    for lord in dict.fromkeys(item.lord for item in listed):
        roles = {item.role for item in listed if item.lord == lord}
        found = _theme_sentence(lord, roles, facts, corpus, seventh, principle_id, template)
        if found is not None:
            sentences.append(found[0])
            terms.extend(found[1])
    if not sentences:
        return _pending_section(listed, seventh), ()
    sentences.append(SynthesisSentence(text=PERIOD_THEMES_CLOSING_V2))
    return _sentences_section("period_themes", sentences), tuple(terms)


def _pending_section(listed: Sequence[_Listed], seventh: str | None) -> list[ConsultationSection]:
    """The periods only, one line per listed lord, then ``THEMES_PENDING``."""
    sentences = [
        SynthesisSentence(
            text=f"{lord.title()}{_role(lord, seventh)} "
            f"{_role_label({item.role for item in listed if item.lord == lord})}.",
            calc_method_ids=(VIMSHOTTARI_METHODOLOGY_ID,),
        )
        for lord in dict.fromkeys(item.lord for item in listed)
    ]
    sentences.append(SynthesisSentence(text=THEMES_PENDING))
    return _sentences_section("period_themes", sentences)


def _role_label(roles: set[str]) -> str:
    if roles == {"Mahadasha", "Antardasha"}:
        return "Mahadasha and Antardasha"
    if roles == {"Antardasha"}:
        return "Antardasha (secondary)"
    return "Mahadasha"


def _theme_sentence(
    lord: str,
    roles: set[str],
    facts: Mapping[str, object],
    corpus: SignificationCorpus,
    seventh: str | None,
    principle_id: str,
    template: str,
) -> tuple[SynthesisSentence, tuple[str, ...]] | None:
    ruled = [house for house in range(1, 13) if facts.get(f"jyotish.d1.house.{house}.lord") == lord]
    placed = _int(facts.get(f"jyotish.d1.planet.{lord}.placement_house"))
    houses: list[tuple[int, SignificationEntry]] = []
    for house in dict.fromkeys((*ruled, *((placed,) if placed is not None else ()))):
        entry = corpus.bhava(house)
        if entry is not None:
            houses.append((house, entry))
    own = corpus.graha(lord)
    if own is None and not houses:
        return None
    name = lord.title()
    parts: list[str] = []
    if own is not None:
        parts.append(f"{name}: {_terms(own)}")
    if houses:
        used_ruled = any(house in ruled for house, _ in houses)
        used_placed = any(house == placed for house, _ in houses)
        verb = (
            "rules and occupies"
            if used_ruled and used_placed
            else ("rules" if used_ruled else "occupies")
        )
        noun = "houses" if len(houses) > 1 else "house"
        listed = "; ".join(f"{_ordinal(house)} house ({_terms(entry)})" for house, entry in houses)
        parts.append(f"{noun} it {verb}: {listed}")
    label = f"{name}{_role(lord, seventh)} {_role_label(roles)}"
    entries = [*((own,) if own is not None else ()), *(entry for _, entry in houses)]
    fact_ids = [f"jyotish.d1.house.{house}.lord" for house in ruled]
    if placed is not None:
        fact_ids.append(f"jyotish.d1.planet.{lord}.placement_house")
    sentence = SynthesisSentence(
        text=f"{label}: reviewed themes — {'; '.join(parts)}.",
        fact_ids=tuple(fact_ids),
        rule_ids=(
            *dict.fromkeys(f"{entry.rule_id}@{entry.rule_version}" for entry in entries),
            principle_id,
        ),
        calc_method_ids=(VIMSHOTTARI_METHODOLOGY_ID, template),
    )
    return sentence, tuple(term.display for entry in entries for term in entry.terms)


def _terms(entry: SignificationEntry) -> str:
    return ", ".join(term.display for term in entry.terms)


def _string(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _int(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _date(value: datetime) -> str:
    return f"{value.day} {value.strftime('%b %Y')}"


def _ordinal(number: int) -> str:
    suffix = (
        "th" if 10 <= number % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    )
    return f"{number}{suffix}"
