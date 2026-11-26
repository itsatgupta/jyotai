"""NEXT-WEALTH-01: one answer pipeline for a domain without reviewed timing rules.

The NEXT-MARRIAGE-01/02 marriage answer, generalised.  A :class:`DomainConfig` names the
domain's houses (their lords are the domain lords), its kārakas, the signification tag the
answer may show, its fixed texts, its wording guard, its out-of-scope questions and, where
relevant, a divisional-chart fact builder.  The pipeline then states only:

* **calculated chart factors**: each domain lord and its house, each kāraka and its house,
  and each one's sign dignity as a calculated fact (X2 convention: a modifier only; it
  changes nothing and never calls a planet strong or weak);
* **reviewed natal context** (only when the governed evaluator matched reviewed rules for the
  domain): the rule's placement line and its admitted statement, quoted verbatim;
* for a timing or year question, the calculated Vimshottari **periods** of the domain lords
  and kārakas overlapping the asked range (Mahadasha primary, Antardasha "(secondary)"); a
  period that runs past the range is marked ``CONTINUES``; their reviewed **Period themes**
  from the domain's tagged terms, or the periods only with the domain's pending line;
* **divisional facts** where the domain has them (Marriage: D9), facts only;
* the **timing status** (no reviewed timing rule; no date; no ranking) and one **limit**.

Every section passes the domain wording guard and the ranking and evaluative guards;
admitted text (signification terms, the reviewer's closing, reviewed natal statements) is
quoted verbatim and excluded from those checks.  A failing section is dropped (fail closed).

Career has reviewed natal and timing rules, so its answer keeps the reviewed Career composer;
its :class:`DomainConfig` (``application.domains``) supplies the 10th house and the Career
signification tag that composer uses.
"""

import logging
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta, tzinfo
from typing import Final, Literal

from astrologer.application.career_synthesis import VIMSHOTTARI_METHODOLOGY_ID
from astrologer.application.lord_dignity import DIGNITY_PREFIX
from astrologer.astrology.chart import Chart
from astrologer.astrology.dasha import VimshottariDashaEngine
from astrologer.composition.comparison_guard import ranking_violation
from astrologer.composition.evaluative_guard import evaluative_violation
from astrologer.composition.models import (
    ConsultationSection,
    DetailedComposedAnswer,
    SynthesisSentence,
)
from astrologer.knowledge.models import JyotishDomain
from astrologer.knowledge.rule_weights import SUPPORTING_LABEL
from astrologer.knowledge.signification import SignificationCorpus, SignificationEntry
from astrologer.knowledge.signification_admit02_v1 import PERIOD_THEMES_CLOSING_V2
from astrologer.questions.models import (
    QuestionDomain,
    QuestionIntent,
    QuestionShape,
    TemporalIntent,
    TimeRangeKind,
)

DOMAIN_PIPELINE_VERSION: Final = "domain-pipeline-v1"
CONTINUES: Final = "(continues past the window)"
OUTLOOK: Final = "outlook"
TIMING: Final = "timing"
_DASHA_YEAR_DAYS: Final = 365.25
_LOGGER = logging.getLogger(__name__)
_ListKind = Literal["chart_factors", "periods", "period_themes", "dasha", "d9_factors", "natal"]
Guard = Callable[[str], str | None]
DivisionalFacts = Callable[[Chart, Mapping[str, object]], tuple[SynthesisSentence, ...]]


@dataclass(frozen=True)
class DomainTexts:
    """The fixed sentences of one domain's answers (template text, never admitted text)."""

    no_timing_rule: str
    timing_status: str
    timing_status_periods: str
    no_ranking: str
    limit_outlook: str
    limit_timing: str
    limit_timing_periods_only: str
    themes_pending: str
    # "<lead>: your 7th lord, Mercury, is in the 9th house and Venus is in the 2nd house."
    outlook_lead: str
    # Used instead of ``outlook_lead`` when reviewed natal rules matched for the domain.
    outlook_lead_reviewed: str | None = None


@dataclass(frozen=True)
class DomainConfig:
    """What a domain answer is built from (see module docstring)."""

    domain: QuestionDomain
    tag_domain: JyotishDomain
    answer_version: str
    houses: tuple[int, ...]
    karakas: tuple[str, ...]
    # "generic": this pipeline; "career": the reviewed Career composer.
    composer: Literal["generic", "career"]
    texts: DomainTexts | None = None
    timing_horizon_years: int = 20
    wording_guard: Guard | None = None
    # Checked in order, the first match decides; each pattern's reply is one polite line.
    out_of_scope: tuple[tuple[str, re.Pattern[str], str], ...] = ()
    divisional: DivisionalFacts | None = None

    def out_of_scope_reply(self, question: str) -> str | None:
        normalized = " ".join(question.lower().split())
        for _scope, pattern, reply in self.out_of_scope:
            if pattern.search(normalized):
                return reply
        return None

    def scope(self, question: str, intent: QuestionIntent) -> str:
        """``outlook``, ``timing`` or the name of an out-of-scope pattern (language only)."""
        normalized = " ".join(question.lower().split())
        for scope, pattern, _reply in self.out_of_scope:
            if pattern.search(normalized):
                return scope
        if intent.requires_timing or intent.time_range is not None:
            return TIMING
        return OUTLOOK


@dataclass(frozen=True)
class Window:
    start: datetime
    end: datetime
    phrase: str


@dataclass(frozen=True)
class _Listed:
    lord: str
    role: str
    sentence: SynthesisSentence


@dataclass(frozen=True)
class _Lords:
    """The domain lords (planet -> the domain houses it rules, in config order)."""

    ruled: dict[str, tuple[int, ...]]

    def role(self, planet: str) -> str:
        houses = self.ruled.get(planet)
        if not houses:
            return ""
        return f" (your {_house_list(houses)} lord)"

    def subject(self, planet: str) -> str:
        houses = self.ruled.get(planet)
        if not houses:
            return planet.title()
        return f"your {_house_list(houses)} lord, {planet.title()}"


def answer_domain(
    config: DomainConfig,
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
    """Rebuild a domain answer's text and consultation sections (see module docstring).

    ``corpus`` must already be the domain view of the reviewed signification corpus
    (``signification_tags.domain_view``): only terms tagged for the domain are shown.
    ``answer`` is the deterministic detailed answer; its matched reviewed rules (``evidence``)
    become the natal section, quoted verbatim.
    """
    texts = config.texts
    if texts is None:
        raise ValueError(f"{config.domain.value} is not answered by the generic pipeline")
    reply = config.out_of_scope_reply(question)
    if reply is not None:
        return _finish(config, answer, (ConsultationSection(kind="direct", text=reply),), ())
    lords = _domain_lords(config, facts)
    factors = _chart_factors(config, facts, lords)
    natal, admitted_natal = _natal_section(answer, config.domain.value)
    divisional = config.divisional(chart, facts) if config.divisional is not None else ()
    reviewed = bool(natal)
    window = (
        _window(intent, as_of, config.timing_horizon_years)
        if config.scope(question, intent) == TIMING
        else None
    )
    if window is None:
        direct = _outlook_direct(config, texts, facts, lords, reviewed)
        sections = [ConsultationSection(kind="direct", text=direct)]
        if config.scope(question, intent) == TIMING:  # an unbounded past question: no range
            sections[0] = ConsultationSection(
                kind="direct", text=f"{texts.no_timing_rule} {direct}"
            )
        sections += natal
        sections += _sentences_section("chart_factors", factors)
        sections += _sentences_section("d9_factors", divisional)
        sections.append(ConsultationSection(kind="limit", text=texts.limit_outlook))
        return _finish(config, answer, tuple(sections), admitted_natal)

    targets = tuple(dict.fromkeys((*lords.ruled, *config.karakas)))
    listed, running = _periods(chart, dasha_engine, window, targets, lords, as_of)
    themes, admitted_terms = _themes_section(texts, listed, facts, corpus, lords)
    sections = [
        ConsultationSection(
            kind="direct",
            text=_timing_direct(
                texts, config, window, lords, bool(listed), intent, bool(admitted_terms)
            ),
        )
    ]
    sections += _sentences_section("periods", tuple(item.sentence for item in listed))
    sections += themes
    sections += natal
    sections += _sentences_section("chart_factors", factors)
    sections += _sentences_section("d9_factors", divisional)
    status = texts.timing_status_periods if listed else texts.timing_status
    sections.append(ConsultationSection(kind="timing_status", text=status))
    if running:
        sections += _sentences_section("dasha", running)
    limit = texts.limit_timing if admitted_terms else texts.limit_timing_periods_only
    sections.append(ConsultationSection(kind="limit", text=limit))
    return _finish(config, answer, tuple(sections), (*admitted_terms, *admitted_natal))


def _finish(
    config: DomainConfig,
    answer: DetailedComposedAnswer,
    sections: tuple[ConsultationSection, ...],
    admitted: Sequence[str],
) -> DetailedComposedAnswer:
    clean = tuple(section for section in sections if _clean(config, section, admitted))
    return answer.model_copy(
        update={
            "answer": " ".join(section.text for section in clean),
            "consultation_sections": clean,
            "limitations": (),
            "corpus_limitation": not any(
                item.domain == config.domain.value for item in answer.evidence
            ),
            "timing_answered": False,
        }
    )


def _clean(config: DomainConfig, section: ConsultationSection, admitted: Sequence[str]) -> bool:
    """Guards on one section; admitted text (signification terms, the reviewer's closing,
    reviewed natal statements) is quoted verbatim and excluded from every check."""
    allowed = (*admitted, PERIOD_THEMES_CLOSING_V2)
    remaining = section.text
    for passage in sorted(set(allowed), key=len, reverse=True):
        remaining = remaining.replace(passage, " ")
    # The domain guard sees the full text, except reviewed natal statements (admitted text).
    guarded = section.text if section.kind != "natal" else remaining
    bad = (
        (config.wording_guard(guarded) if config.wording_guard is not None else None)
        or ranking_violation(remaining)
        or evaluative_violation(remaining)
    )
    if bad is not None:
        _LOGGER.warning(
            "%s section %s dropped by guard: %r", config.domain.value, section.kind, bad
        )
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


def _domain_lords(config: DomainConfig, facts: Mapping[str, object]) -> _Lords:
    ruled: dict[str, list[int]] = {}
    for house in config.houses:
        lord = _string(facts.get(f"jyotish.d1.house.{house}.lord"))
        if lord is not None:
            ruled.setdefault(lord, []).append(house)
    return _Lords({lord: tuple(houses) for lord, houses in ruled.items()})


def _natal_section(
    answer: DetailedComposedAnswer, domain: str
) -> tuple[list[ConsultationSection], list[str]]:
    """The matched reviewed rules of ``domain``: placement line (``Supporting`` for a
    secondary rule, then the lord's sign dignity) and the admitted statement, verbatim.

    The evidence selector is already exact-domain (``evidence.selector``); a rule of any
    other domain (e.g. the General 11th-lord-in-9/10 rule) is dropped here too."""
    sentences: list[SynthesisSentence] = []
    admitted: list[str] = []
    for item in answer.evidence:
        if item.domain != domain:
            continue
        line = item.placement_explanation
        if item.weight == "secondary":
            line = f"{SUPPORTING_LABEL}: {line}"
        if item.lord_dignity:
            line = f"{line} {item.lord_dignity}"
        sentences.append(SynthesisSentence(text=f"{line} {item.reviewed_statement}"))
        admitted.append(item.reviewed_statement)
    return _sentences_section("natal", sentences), admitted


def _chart_factors(
    config: DomainConfig, facts: Mapping[str, object], lords: _Lords
) -> tuple[SynthesisSentence, ...]:
    sentences: list[SynthesisSentence] = []
    for lord, houses in lords.ruled.items():
        house = houses[0]
        placed = _int(facts.get(f"jyotish.d1.house_lord.{house}.placement_house"))
        if placed is not None:
            sentences.append(
                SynthesisSentence(
                    text=(
                        f"Your {_house_list(houses)} lord is {lord.title()}, placed in the "
                        f"{_ordinal(placed)} house."
                    ),
                    fact_ids=(
                        *(f"jyotish.d1.house.{item}.lord" for item in houses),
                        *(f"jyotish.d1.house_lord.{item}.placement_house" for item in houses),
                    ),
                )
            )
        if dignity := planet_dignity(facts, lord, f"your {_house_list(houses)} lord"):
            sentences.append(dignity)
    for karaka in config.karakas:
        placed = _int(facts.get(f"jyotish.d1.planet.{karaka}.placement_house"))
        if placed is not None:
            karaka_houses = lords.ruled.get(karaka)
            role = f", your {_house_list(karaka_houses)} lord," if karaka_houses else ""
            sentences.append(
                SynthesisSentence(
                    text=f"{karaka.title()}{role} is placed in the {_ordinal(placed)} house.",
                    fact_ids=(f"jyotish.d1.planet.{karaka}.placement_house",),
                )
            )
        if karaka not in lords.ruled and (dignity := planet_dignity(facts, karaka, None)):
            sentences.append(dignity)
    return tuple(sentences)


def planet_dignity(
    facts: Mapping[str, object], planet: str, role: str | None
) -> SynthesisSentence | None:
    """'Calculated fact (sign dignity): Venus is in its own sign.' from the D1 dignity facts.

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


def _outlook_direct(
    config: DomainConfig,
    texts: DomainTexts,
    facts: Mapping[str, object],
    lords: _Lords,
    reviewed: bool,
) -> str:
    parts: list[str] = []
    for lord, houses in lords.ruled.items():
        placed = _int(facts.get(f"jyotish.d1.house_lord.{houses[0]}.placement_house"))
        if placed is not None:
            parts.append(f"{lords.subject(lord)}, is in the {_ordinal(placed)} house")
    for karaka in config.karakas:
        placed = _int(facts.get(f"jyotish.d1.planet.{karaka}.placement_house"))
        if placed is not None and karaka not in lords.ruled:
            parts.append(f"{karaka.title()} is in the {_ordinal(placed)} house")
    lead = texts.outlook_lead_reviewed if reviewed and texts.outlook_lead_reviewed else None
    lead = lead or texts.outlook_lead
    return f"{lead}: {_and_list(parts)}." if parts else f"{lead}."


def _timing_direct(
    texts: DomainTexts,
    config: DomainConfig,
    window: Window,
    lords: _Lords,
    found: bool,
    intent: QuestionIntent,
    themed: bool,
) -> str:
    subjects = [lords.subject(planet) for planet in lords.ruled]
    subjects += [karaka.title() for karaka in config.karakas if karaka not in lords.ruled]
    if found:
        themes = " with their reviewed Period themes" if themed else ""
        body = (
            f"{window.phrase}, the Mahadasha and Antardasha periods of "
            f"{_of_list(subjects)} are listed below{themes}."
        )
    elif len(subjects) == 1:
        body = f"{window.phrase}, {_with_comma(subjects[0])} has no Mahadasha or Antardasha period."
    elif len(subjects) == 2:
        body = (
            f"{window.phrase}, neither {_with_comma(subjects[0])} nor {subjects[1]} has a "
            "Mahadasha or Antardasha period."
        )
    else:
        body = (
            f"{window.phrase}, there is no Mahadasha or Antardasha period of {_of_list(subjects)}."
        )
    text = f"{texts.no_timing_rule} {body}"
    if intent.shape is QuestionShape.COMPARATIVE:
        text = f"{text} {texts.no_ranking}"
    return text


def _with_comma(subject: str) -> str:
    """'your 7th lord, Venus' -> 'your 7th lord, Venus,' (a bare planet name is unchanged)."""
    return f"{subject}," if subject.startswith("your ") else subject


def _of_list(subjects: Sequence[str]) -> str:
    """'A' / 'A, and of B' / 'A, of B, and of C' (A and B may carry their role)."""
    if len(subjects) == 1:
        return subjects[0]
    return ", of ".join(subjects[:-1]) + f", and of {subjects[-1]}"


def _and_list(parts: Sequence[str]) -> str:
    """'A' / 'A and B' / 'A, B and C'."""
    if len(parts) <= 2:
        return " and ".join(parts)
    return ", ".join(parts[:-1]) + f" and {parts[-1]}"


def _window(intent: QuestionIntent, as_of: datetime, horizon_years: int) -> Window | None:
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
        return Window(start.astimezone(UTC), end.astimezone(UTC), phrase)
    if intent.temporal_intent is TemporalIntent.HISTORICAL:
        return None
    start = as_of.astimezone(UTC)
    end = start + timedelta(days=_DASHA_YEAR_DAYS * horizon_years)
    phrase = f"In the next {horizon_years} years ({_date(as_of)} to {_date(end.astimezone(zone))})"
    return Window(start, end, phrase)


def _periods(
    chart: Chart,
    engine: VimshottariDashaEngine,
    window: Window,
    targets: tuple[str, ...],
    lords: _Lords,
    as_of: datetime,
) -> tuple[list[_Listed], tuple[SynthesisSentence, ...]]:
    """The target lords' MD/AD periods overlapping the window, in time order, and (for a
    window of at most a year) every MD/AD segment running in it.  A period that ends after
    the window is marked ``CONTINUES``."""
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
        name = major.lord.value
        if name in targets:
            listed.append(
                _Listed(
                    name,
                    "Mahadasha",
                    _period_sentence(
                        f"{name.title()}{lords.role(name)} Mahadasha",
                        major.start,
                        major.end,
                        zone,
                        window,
                    ),
                )
            )
        for minor in major.antardashas:
            if minor.end <= window.start or minor.start >= window.end:
                continue
            minor_name = minor.lord.value
            label = (
                f"{minor_name.title()}{lords.role(minor_name)} Antardasha "
                f"in the {name.title()} Mahadasha"
            )
            if minor_name in targets:
                listed.append(
                    _Listed(
                        minor_name,
                        "Antardasha",
                        _period_sentence(label, minor.start, minor.end, zone, window),
                    )
                )
            if short:
                running.append(
                    _period_sentence(
                        f"Running: {name.title()} Mahadasha / {minor_name.title()} Antardasha",
                        minor.start,
                        minor.end,
                        zone,
                        window,
                    )
                )
    return listed, tuple(running)


def _period_sentence(
    label: str, start: datetime, end: datetime, zone: tzinfo, window: Window
) -> SynthesisSentence:
    past = f" {CONTINUES}" if end > window.end else ""
    return SynthesisSentence(
        text=f"{label}: {_date(start.astimezone(zone))} to {_date(end.astimezone(zone))}{past}.",
        calc_method_ids=(VIMSHOTTARI_METHODOLOGY_ID,),
    )


def _themes_section(
    texts: DomainTexts,
    listed: Sequence[_Listed],
    facts: Mapping[str, object],
    corpus: SignificationCorpus,
    lords: _Lords,
) -> tuple[list[ConsultationSection], tuple[str, ...]]:
    """X18 compact Period-themes lines, one per listed lord, then the reviewer's closing;
    also the admitted terms quoted (excluded from the guards).  When no listed lord has a
    term tagged for the domain, the periods only (one line per lord) and the pending line."""
    principle = corpus.lordship_principle
    if not listed:
        return [], ()
    if principle is None:
        return _pending_section(texts, listed, lords), ()
    principle_id = f"{principle.rule_id}@{principle.rule_version}"
    template = principle.approved_template_version
    sentences: list[SynthesisSentence] = []
    terms: list[str] = []
    for lord in dict.fromkeys(item.lord for item in listed):
        roles = {item.role for item in listed if item.lord == lord}
        found = _theme_sentence(lord, roles, facts, corpus, lords, principle_id, template)
        if found is not None:
            sentences.append(found[0])
            terms.extend(found[1])
    if not sentences:
        return _pending_section(texts, listed, lords), ()
    sentences.append(SynthesisSentence(text=PERIOD_THEMES_CLOSING_V2))
    return _sentences_section("period_themes", sentences), tuple(terms)


def _pending_section(
    texts: DomainTexts, listed: Sequence[_Listed], lords: _Lords
) -> list[ConsultationSection]:
    sentences = [
        SynthesisSentence(
            text=f"{lord.title()}{lords.role(lord)} "
            f"{_role_label({item.role for item in listed if item.lord == lord})}.",
            calc_method_ids=(VIMSHOTTARI_METHODOLOGY_ID,),
        )
        for lord in dict.fromkeys(item.lord for item in listed)
    ]
    sentences.append(SynthesisSentence(text=texts.themes_pending))
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
    lords: _Lords,
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
    label = f"{name}{lords.role(lord)} {_role_label(roles)}"
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


def _house_list(houses: Sequence[int]) -> str:
    """(7,) -> '7th'; (2, 11) -> '2nd and 11th'."""
    return " and ".join(_ordinal(house) for house in houses)


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
