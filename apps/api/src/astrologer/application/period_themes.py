"""'Period themes' for a Career year answer (template ``period-themes-v1``).

For each period lord of the asked year (scope set by the admitted X18 record), one sentence
names the lord's own approved significations and the approved significations of the houses
it rules and occupies (calculated ``jyotish.dasha_linkage.v1`` facts, counted from the D1
Lagna).  Nothing is produced unless BOTH the X18 lordship-principle record AND at least one
relevant signification entry are admitted; otherwise the result is empty (UNKNOWN, no text).

The template states only which reviewed significations are associated with the period.  It
never predicts, weighs, ranks or causes anything; every rendered sentence is checked against
the ranking, causal and evaluative guards and is dropped (fail closed) if one fires.
"""

import logging
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import timedelta
from typing import Final, Literal

from astrologer.application.career_synthesis import VIMSHOTTARI_METHODOLOGY_ID
from astrologer.astrology.dasha_linkage import (
    DASHA_LINKAGE_METHODOLOGY_ID,
    DashaLordLinkage,
    LinkageStatus,
)
from astrologer.composition.models import (
    DashaSegmentLinkage,
    PlannedDashaSegment,
    SynthesisSentence,
)
from astrologer.knowledge.signification import (
    PERIOD_THEMES_TEMPLATE_VERSION,
    SignificationCorpus,
    SignificationEntry,
    term_violation,
)

PERIOD_THEMES_CLOSING: Final = "This does not predict an event or an outcome."
_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class _Period:
    role: Literal["Mahadasha", "Antardasha"]
    linkage: DashaLordLinkage
    segments: tuple[PlannedDashaSegment, ...]


def build_period_themes(
    linkages: Sequence[DashaSegmentLinkage],
    segments: Sequence[PlannedDashaSegment],
    corpus: SignificationCorpus,
    year: int,
) -> tuple[SynthesisSentence, ...]:
    """One sentence per period lord with admitted significations, then the fixed closing.

    Empty when X18 is not admitted, or when no period lord and none of its houses has an
    admitted entry.
    """
    principle = corpus.lordship_principle
    if principle is None or not segments:
        return ()
    sentences: list[SynthesisSentence] = []
    for period in _periods(linkages, segments, principle.scope == "MAHADASHA_AND_ANTARDASHA"):
        sentence = _sentence(
            period, corpus, segments, year, f"{principle.rule_id}@{principle.rule_version}"
        )
        if sentence is None:
            continue
        if (bad := term_violation(sentence.text)) is not None:
            _LOGGER.warning("period theme dropped by guard: %r", bad)
            continue
        sentences.append(sentence)
    if not sentences:
        return ()
    return (*sentences, SynthesisSentence(text=PERIOD_THEMES_CLOSING))


def _periods(
    linkages: Sequence[DashaSegmentLinkage],
    segments: Sequence[PlannedDashaSegment],
    with_antardasha: bool,
) -> list[_Period]:
    by_segment = {item.segment_id: item for item in linkages}
    majors: dict[tuple[str, str], list[PlannedDashaSegment]] = {}
    minors: dict[tuple[str, str, str], list[PlannedDashaSegment]] = {}
    lords: dict[tuple[str, ...], DashaLordLinkage] = {}
    for segment in segments:
        item = by_segment.get(segment.segment_id)
        if item is None:
            continue
        md_key = (segment.mahadasha_lord, segment.mahadasha_start.isoformat())
        ad_key = (*md_key, segment.antardasha_start.isoformat())
        majors.setdefault(md_key, []).append(segment)
        minors.setdefault(ad_key, []).append(segment)
        lords.setdefault(md_key, item.linkage.mahadasha)
        lords.setdefault(ad_key, item.linkage.antardasha)
    periods = [_Period("Mahadasha", lords[k], tuple(v)) for k, v in majors.items()]
    if with_antardasha:
        periods += [_Period("Antardasha", lords[k], tuple(v)) for k, v in minors.items()]
    return periods


@dataclass(frozen=True)
class _Themes:
    own: SignificationEntry | None
    houses: tuple[tuple[int, SignificationEntry], ...]
    ruled: tuple[int, ...]
    placed: int | None
    ruled_fact_id: str
    placed_fact_id: str


def _themes(linkage: DashaLordLinkage, corpus: SignificationCorpus) -> _Themes | None:
    """The lord's admitted entry and the admitted entries of the houses it rules and occupies
    (Rahu/Ketu rule no sign, so only their occupied house), or None when there is none."""
    own = corpus.graha(linkage.lord.value)
    ruled_fact = linkage.fact("ruled_houses")
    placed_fact = linkage.fact("placement_house")
    ruled = (
        tuple(ruled_fact.value)
        if ruled_fact.status is LinkageStatus.KNOWN and isinstance(ruled_fact.value, tuple)
        else ()
    )
    placed = (
        placed_fact.value
        if placed_fact.status is LinkageStatus.KNOWN
        and isinstance(placed_fact.value, int)
        and not isinstance(placed_fact.value, bool)
        else None
    )
    houses: list[tuple[int, SignificationEntry]] = []
    for house in dict.fromkeys((*ruled, *((placed,) if placed is not None else ()))):
        entry = corpus.bhava(house)
        if entry is not None:
            houses.append((house, entry))
    if own is None and not houses:
        return None
    return _Themes(own, tuple(houses), ruled, placed, ruled_fact.fact_id, placed_fact.fact_id)


def _sentence(
    period: _Period,
    corpus: SignificationCorpus,
    all_segments: Sequence[PlannedDashaSegment],
    year: int,
    principle_rule_id: str,
) -> SynthesisSentence | None:
    themes = _themes(period.linkage, corpus)
    if themes is None:
        return None
    name = period.linkage.lord.value.title()
    own, houses, ruled, placed = themes.own, themes.houses, themes.ruled, themes.placed
    parts: list[str] = []
    if own is not None:
        parts.append(f"{name} ({_terms(own)})")
    if houses:
        used_ruled = any(h in ruled for h, _ in houses)
        used_placed = any(h == placed for h, _ in houses)
        noun = "houses" if len(houses) > 1 else "house"
        verb = (
            "rules and occupies"
            if used_ruled and used_placed
            else ("rules" if used_ruled else "occupies")
        )
        listed = "; ".join(f"{_ordinal(h)} house: {_terms(e)}" for h, e in houses)
        parts.append(f"the {noun} it {verb} ({listed})")
    text = (
        f"During your {name} {period.role} {_span(period, all_segments, year)}, the reviewed "
        f"significations associated with {' and with '.join(parts)} are the themes the texts "
        "associate with this period."
    )
    return SynthesisSentence(
        text=text,
        fact_ids=_fact_ids(period, themes),
        rule_ids=(*_rule_ids(themes), principle_rule_id),
        calc_method_ids=(
            VIMSHOTTARI_METHODOLOGY_ID,
            DASHA_LINKAGE_METHODOLOGY_ID,
            PERIOD_THEMES_TEMPLATE_VERSION,
        ),
    )


def _fact_ids(period: _Period, themes: _Themes) -> tuple[str, ...]:
    fact_ids = [segment.segment_id for segment in period.segments]
    if any(h in themes.ruled for h, _ in themes.houses):
        fact_ids.append(themes.ruled_fact_id)
    if any(h == themes.placed for h, _ in themes.houses):
        fact_ids.append(themes.placed_fact_id)
    return tuple(dict.fromkeys(fact_ids))


def _rule_ids(themes: _Themes) -> tuple[str, ...]:
    entries = [*((themes.own,) if themes.own is not None else ()), *(e for _, e in themes.houses)]
    return tuple(dict.fromkeys(f"{e.rule_id}@{e.rule_version}" for e in entries))


def build_period_themes_glance(
    linkages: Sequence[DashaSegmentLinkage],
    segments: Sequence[PlannedDashaSegment],
    corpus: SignificationCorpus,
    year: int,
) -> SynthesisSentence | None:
    """One glance bullet listing each period's admitted terms, for exactly the periods that
    have a Period-themes sentence ('Period themes: Rahu Mahadasha (army or forces, gain,
    increase); Mercury Antardasha (speech, …).').  None when there is no such sentence."""
    principle = corpus.lordship_principle
    if principle is None or not segments:
        return None
    principle_rule_id = f"{principle.rule_id}@{principle.rule_version}"
    parts: list[str] = []
    fact_ids: list[str] = []
    rule_ids: list[str] = []
    for period in _periods(linkages, segments, principle.scope == "MAHADASHA_AND_ANTARDASHA"):
        sentence = _sentence(period, corpus, segments, year, principle_rule_id)
        themes = _themes(period.linkage, corpus)
        if sentence is None or themes is None or term_violation(sentence.text) is not None:
            continue
        entries = [
            *((themes.own,) if themes.own is not None else ()),
            *(e for _, e in themes.houses),
        ]
        terms = dict.fromkeys(term.display for entry in entries for term in entry.terms)
        label = f"{period.linkage.lord.value.title()} {period.role}"
        part = f"{label} ({', '.join(terms)})"
        if part not in parts:
            parts.append(part)
        fact_ids.extend(sentence.fact_ids)
        rule_ids.extend(sentence.rule_ids)
    if not parts:
        return None
    text = f"Period themes: {'; '.join(parts)}."
    if term_violation(text) is not None:
        return None
    return SynthesisSentence(
        text=text,
        fact_ids=tuple(dict.fromkeys(fact_ids)),
        rule_ids=tuple(dict.fromkeys(rule_ids)),
        calc_method_ids=(
            VIMSHOTTARI_METHODOLOGY_ID,
            DASHA_LINKAGE_METHODOLOGY_ID,
            PERIOD_THEMES_TEMPLATE_VERSION,
        ),
    )


def _terms(entry: SignificationEntry) -> str:
    return ", ".join(term.display for term in entry.terms)


def _span(period: _Period, all_segments: Sequence[PlannedDashaSegment], year: int) -> str:
    first, last = period.segments[0], period.segments[-1]
    if (
        first.effective_start == all_segments[0].effective_start
        and last.effective_end == all_segments[-1].effective_end
    ):
        return f"throughout {year}"
    end = last.local_end - timedelta(microseconds=1)
    start = first.local_start
    return f"({start.strftime('%b')} {start.day}–{end.strftime('%b')} {end.day})"


def _ordinal(number: int) -> str:
    suffix = (
        "th" if 10 <= number % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    )
    return f"{number}{suffix}"
