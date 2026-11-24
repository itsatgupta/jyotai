"""'<Year> at a glance': a short, templated summary at the top of a Career year answer.

Presentation only.  Every bullet is a template over facts and labels the year answer already
carries (planned Dasha segments, ``jyotish.dasha_linkage.v1`` facts, the D1 10th-lord facts,
synthesis links, and plain labels of admitted claims).  No bullet quotes or rewords admitted
rule text, and none adds a fact, rule, or meaning.

Bullets, in order:

1. the calculated periods covering the year (one line);
2. the 10th lord (named here, once) and the reviewed natal indication, in one plain clause;
3. one calculated link between a period lord and the 10th lord / 10th house, chosen by the
   fixed display precedence ``GLANCE_LINK_PRECEDENCE`` (omitted when no link is found); a
   period lord that is the 10th lord is then referred to by role ("your 10th lord is also
   your Mahadasha lord throughout 2027");
4. the Period-themes terms of the year's period lords (``plan.period_themes_glance``; omitted
   when no Period-themes sentence exists);
5. the timing status (the matched rule's label, or "no reviewed timing rule applies").

A natal rule whose reviewed wording is withheld (v.76, 10th lord in the 8th) is stated as "a
reviewed indication exists … its wording is withheld pending further review"; the paused
7th-house part of v.72 (NEXT-ADMIT-02) as "a reviewed indication exists; wording pending
source verification".

The precedence orders links for display only.  It is a presentation convention, not a
strength model: the bullet never calls a link strong, weak, or significant.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Final, Literal

from astrologer.application.career_synthesis import (
    VIMSHOTTARI_METHODOLOGY_ID,
    claim_labels,
)
from astrologer.astrology.dasha_linkage import (
    DASHA_LINKAGE_METHODOLOGY_ID,
    DashaLordLinkage,
    LinkageStatus,
)
from astrologer.composition.career_claims import CareerClaim
from astrologer.composition.models import (
    CareerAnswerPlan,
    CareerTimingContext,
    ConsultationSection,
    PlannedDashaSegment,
    SynthesisLink,
    SynthesisSentence,
)
from astrologer.knowledge.admit02_pack_v1 import (
    WITHHELD_WORDING_CLAUSES,
    WITHHELD_WORDING_RULE_IDS,
)

GLANCE_VERSION: Final = "year-glance-v1"

GlanceLinkKind = Literal[
    "is_tenth_lord",
    "same_sign_as_tenth_lord",
    "occupies_tenth",
    "aspects_tenth_house",
    "aspects_tenth_lord",
    "SAME_HOUSE",
]
# Fixed display precedence (first match wins).  Display order only, never strength.
GLANCE_LINK_PRECEDENCE: Final[tuple[GlanceLinkKind, ...]] = (
    "is_tenth_lord",
    "same_sign_as_tenth_lord",
    "occupies_tenth",
    "aspects_tenth_house",
    "aspects_tenth_lord",
    "SAME_HOUSE",
)
_CLAUSES: Final[dict[GlanceLinkKind, str]] = {
    "is_tenth_lord": "is your 10th lord",
    "same_sign_as_tenth_lord": "is in the same sign as your 10th lord",
    "occupies_tenth": "occupies your 10th house",
    "aspects_tenth_house": "aspects your 10th house",
    "aspects_tenth_lord": "aspects your 10th lord",
}
_TENTH_LORD_FACT_ID: Final = "jyotish.d1.house.10.lord"
_TENTH_PLACEMENT_FACT_ID: Final = "jyotish.d1.house_lord.10.placement_house"


@dataclass(frozen=True)
class _Period:
    role: Literal["Mahadasha", "Antardasha"]
    linkage: DashaLordLinkage
    segments: tuple[PlannedDashaSegment, ...]


@dataclass(frozen=True)
class GlanceLink:
    """The link chosen for the glance, and its place in the fixed precedence."""

    kind: GlanceLinkKind
    period_role: Literal["Mahadasha", "Antardasha"]
    period_lord: str
    sentence: SynthesisSentence
    # "your Mahadasha lord throughout 2027" / "your Antardasha lord (Jan 22–Dec 31)"
    role_phrase: str = ""


def year_glance_section(
    plan: CareerAnswerPlan,
    year: int,
    natal: Sequence[CareerClaim],
    timed: Sequence[CareerClaim],
    timing: CareerTimingContext | None,
) -> ConsultationSection | None:
    """Return the glance section, or None when the year has no planned Dasha segments."""
    if not plan.dasha_segments:
        return None
    periods = _periods(plan)
    if periods is None:
        return None
    natal_bullet, named = _natal_bullet(plan, natal)
    bullets = [periods, natal_bullet]
    link = select_glance_link(plan, year)
    if link is not None:
        sentence = link.sentence
        if named and link.kind == "is_tenth_lord":
            # The natal bullet already names the 10th lord; refer to it by role only.
            sentence = sentence.model_copy(
                update={"text": f"Calculated link: your 10th lord is also {link.role_phrase}."}
            )
        bullets.append(sentence)
    if plan.period_themes and plan.period_themes_glance is not None:
        bullets.append(plan.period_themes_glance)
    bullets.append(_timing_bullet(year, timed, timing))
    return ConsultationSection(
        kind="glance",
        text=" ".join(bullet.text for bullet in bullets),
        synthesis_sentences=tuple(bullets),
    )


def select_glance_link(plan: CareerAnswerPlan, year: int) -> GlanceLink | None:
    """The first link by ``GLANCE_LINK_PRECEDENCE``; ties go to the Mahadasha, then the
    earlier period.  UNKNOWN linkage facts (e.g. Rahu/Ketu aspects) never count as a link.
    """
    periods = _year_periods(plan)
    for kind in GLANCE_LINK_PRECEDENCE:
        for period in periods:
            sentence = _link_sentence(kind, period, plan, year)
            if sentence is not None:
                return GlanceLink(
                    kind=kind,
                    period_role=period.role,
                    period_lord=period.linkage.lord.value,
                    sentence=sentence,
                    role_phrase=f"your {period.role} lord {_span_phrase(period, plan, year)}",
                )
    return None


def _year_periods(plan: CareerAnswerPlan) -> list[_Period]:
    """Distinct MD and AD periods of the year: all Mahadashas first, then Antardashas,
    each in chronological order."""
    by_segment = {item.segment_id: item for item in plan.dasha_linkages}
    majors: dict[tuple[str, str], list[PlannedDashaSegment]] = {}
    minors: dict[tuple[str, str, str], list[PlannedDashaSegment]] = {}
    lords: dict[tuple[str, ...], DashaLordLinkage] = {}
    for segment in plan.dasha_segments:
        item = by_segment.get(segment.segment_id)
        if item is None:
            continue
        md_key = (segment.mahadasha_lord, segment.mahadasha_start.isoformat())
        ad_key = (*md_key, segment.antardasha_start.isoformat())
        majors.setdefault(md_key, []).append(segment)
        minors.setdefault(ad_key, []).append(segment)
        lords.setdefault(md_key, item.linkage.mahadasha)
        lords.setdefault(ad_key, item.linkage.antardasha)
    return [
        *(_Period("Mahadasha", lords[key], tuple(items)) for key, items in majors.items()),
        *(_Period("Antardasha", lords[key], tuple(items)) for key, items in minors.items()),
    ]


def _link_sentence(
    kind: GlanceLinkKind, period: _Period, plan: CareerAnswerPlan, year: int
) -> SynthesisSentence | None:
    name = period.linkage.lord.value.title()
    subject = f"{name}, your {period.role} lord {_span_phrase(period, plan, year)},"
    segment_ids = tuple(segment.segment_id for segment in period.segments)
    if kind == "SAME_HOUSE":
        link = _same_house_link(plan, period)
        if link is None:
            return None
        verbs = _house_verbs(link, period.linkage)
        return SynthesisSentence(
            text=(
                f"Calculated link: {subject} {verbs} {link.claim_subject}, which "
                f"{link.claim_label} concerns."
            ),
            claim_ids=(link.claim_id,),
            fact_ids=tuple(
                dict.fromkeys((*segment_ids, *link.dasha_fact_ids, *link.claim_fact_ids))
            ),
            rule_ids=link.claim_rule_ids,
            calc_method_ids=(VIMSHOTTARI_METHODOLOGY_ID, DASHA_LINKAGE_METHODOLOGY_ID),
        )
    fact = period.linkage.fact(kind)
    if fact.status is not LinkageStatus.KNOWN or fact.value is not True:
        return None
    tenth_ids = tuple(
        item.fact_id for item in plan.tenth_lord_facts if item.fact_id == _TENTH_LORD_FACT_ID
    )
    return SynthesisSentence(
        text=f"Calculated link: {subject} {_CLAUSES[kind]}.",
        fact_ids=tuple(dict.fromkeys((*segment_ids, fact.fact_id, *tenth_ids))),
        calc_method_ids=(VIMSHOTTARI_METHODOLOGY_ID, DASHA_LINKAGE_METHODOLOGY_ID),
    )


def _same_house_link(plan: CareerAnswerPlan, period: _Period) -> SynthesisLink | None:
    if plan.synthesis is None:
        return None
    ids = {segment.segment_id for segment in period.segments}
    name = period.linkage.lord.value.title()
    return next(
        (
            link
            for link in plan.synthesis.links
            if link.link_type == "SAME_HOUSE"
            and link.period_role == period.role
            and link.period_lord == name
            and link.claim_subject is not None
            and ids & set(link.segment_ids)
        ),
        None,
    )


def _house_verbs(link: SynthesisLink, linkage: DashaLordLinkage) -> str:
    verbs = []
    if linkage.fact("ruled_houses").fact_id in link.dasha_fact_ids:
        verbs.append("rules")
    if linkage.fact("placement_house").fact_id in link.dasha_fact_ids:
        verbs.append("occupies")
    return " and ".join(verbs)


def _span_phrase(period: _Period, plan: CareerAnswerPlan, year: int) -> str:
    if _covers_year(period.segments, plan):
        return f"throughout {year}"
    return f"({_local_span(period.segments[0].local_start, period.segments[-1].local_end)})"


def _covers_year(segments: Sequence[PlannedDashaSegment], plan: CareerAnswerPlan) -> bool:
    return (
        segments[0].effective_start == plan.dasha_segments[0].effective_start
        and segments[-1].effective_end == plan.dasha_segments[-1].effective_end
    )


def _periods(plan: CareerAnswerPlan) -> SynthesisSentence | None:
    """'Periods: Rahu Mahadasha throughout 2028, with Saturn Antardasha (Jan 1–Jan 22),
    then Mercury Antardasha (Jan 22–Dec 31).'"""
    scope = plan.requested_time_scope
    if scope is None:
        return None
    year = scope.start_date.year
    groups: dict[tuple[str, str], list[PlannedDashaSegment]] = {}
    for segment in plan.dasha_segments:
        groups.setdefault((segment.mahadasha_lord, segment.mahadasha_start.isoformat()), []).append(
            segment
        )
    parts = []
    for (md, _), segments in groups.items():
        whole = _covers_year(segments, plan)
        head = f"{md.title()} Mahadasha " + (
            f"throughout {year}"
            if whole
            else f"({_local_span(segments[0].local_start, segments[-1].local_end)})"
        )
        if len(segments) == 1:
            parts.append(f"{head}, with {segments[0].antardasha_lord.title()} Antardasha")
            continue
        ads = [
            f"{segment.antardasha_lord.title()} Antardasha "
            f"({_local_span(segment.local_start, segment.local_end)})"
            for segment in segments
        ]
        parts.append(f"{head}, with {', then '.join(ads)}")
    return SynthesisSentence(
        text=f"Periods: {'; then '.join(parts)}.",
        fact_ids=tuple(segment.segment_id for segment in plan.dasha_segments),
        calc_method_ids=(VIMSHOTTARI_METHODOLOGY_ID,),
    )


def _natal_bullet(
    plan: CareerAnswerPlan, natal: Sequence[CareerClaim]
) -> tuple[SynthesisSentence, bool]:
    """The single statement of the 10th lord, then the reviewed natal indication by its
    plain label.  Also returns whether the 10th lord was named."""
    facts = {fact.fact_id: fact for fact in plan.tenth_lord_facts}
    lord = facts.get(_TENTH_LORD_FACT_ID)
    house = facts.get(_TENTH_PLACEMENT_FACT_ID)
    lead: str | None = None
    lead_ids: tuple[str, ...] = ()
    if lord is not None and house is not None and house.value.isdigit():
        placement = f"in your {_ordinal(int(house.value))} house"
        lead = f"your 10th lord is {lord.value.title()}, {placement}"
        lead_ids = (lord.fact_id, house.fact_id)
    withheld = [claim for claim in natal if _wording_withheld(claim)]
    shown = [claim for claim in natal if not _wording_withheld(claim)]
    if natal:
        clauses = []
        if shown:
            labels = list(claim_labels(shown).values())
            joined = (
                labels[0] if len(labels) == 1 else ", ".join(labels[:-1]) + " and " + labels[-1]
            )
            clauses.append(f"your chart matches {joined}")
        clauses.extend(
            dict.fromkeys(
                WITHHELD_WORDING_CLAUSES[rule.split("@")[0]]
                for claim in withheld
                for rule in claim.rule_ids
                if rule.split("@")[0] in WITHHELD_WORDING_CLAUSES
            )
        )
        clause = "; ".join(clauses)
    else:
        clause = "no reviewed natal Career indication matched your chart"
    text = f"Natal: {lead}; {clause}." if lead else f"Natal: {clause}."
    sentence = SynthesisSentence(
        text=text,
        claim_ids=tuple(claim.claim_id for claim in natal),
        fact_ids=tuple(dict.fromkeys((*lead_ids, *(f for c in natal for f in c.fact_ids)))),
        rule_ids=tuple(dict.fromkeys(r for claim in natal for r in claim.rule_ids)),
    )
    return sentence, lead is not None


def _wording_withheld(claim: CareerClaim) -> bool:
    return any(rule.split("@")[0] in WITHHELD_WORDING_RULE_IDS for rule in claim.rule_ids)


def _timing_bullet(
    year: int, timed: Sequence[CareerClaim], timing: CareerTimingContext | None
) -> SynthesisSentence:
    if timed:
        labels = list(claim_labels(timed).values())
        joined = labels[0] if len(labels) == 1 else ", ".join(labels[:-1]) + " and " + labels[-1]
        verb = "applies" if len(labels) == 1 else "apply"
        return SynthesisSentence(
            text=f"Timing: {joined} {verb}.",
            claim_ids=tuple(claim.claim_id for claim in timed),
            rule_ids=tuple(dict.fromkeys(r for claim in timed for r in claim.rule_ids)),
        )
    if timing is None:
        text = f"Timing: reviewed Career timing was not evaluated for {year}."
    elif timing.status == "UNKNOWN":
        text = f"Timing: the reviewed timing rules could not be evaluated for {year}."
    else:
        text = f"Timing: no reviewed timing rule applies to {year}."
    return SynthesisSentence(text=text)


def _local_span(start: datetime, end: datetime) -> str:
    """'Jan 22–Dec 31' from local segment bounds (end exclusive), as in the year answer."""
    last = end - timedelta(microseconds=1)
    return f"{start.strftime('%b')} {start.day}–{last.strftime('%b')} {last.day}"


def _ordinal(number: int) -> str:
    suffix = (
        "th" if 10 <= number % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    )
    return f"{number}{suffix}"


__all__ = [
    "GLANCE_LINK_PRECEDENCE",
    "GLANCE_VERSION",
    "GlanceLink",
    "select_glance_link",
    "year_glance_section",
]
