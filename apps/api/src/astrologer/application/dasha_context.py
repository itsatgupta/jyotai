"""Build and render the calculated Dasha context for planned Career Dasha segments.

Every rendered sentence is generated from linkage fact ids, plus exactly one fixed framing
line.  No sentence evaluates, ranks, or interprets a lord or period; interpretation can
appear only when an admitted Dasha rule fills the review-gated slot.
"""

from collections.abc import Iterable, Sequence
from typing import Final

from astrologer.astrology.chart import Chart
from astrologer.astrology.dasha import DashaLord
from astrologer.astrology.dasha_linkage import (
    DashaLordLinkage,
    LinkageFactName,
    LinkageStatus,
    build_pair_linkage,
)
from astrologer.astrology.derived_facts import DerivedFactsEngine
from astrologer.composition.models import (
    ConsultationSection,
    DashaContextSentence,
    DashaInterpretationSlot,
    DashaSegmentLinkage,
    PlannedDashaSegment,
)
from astrologer.knowledge.dasha_interpretation import DashaInterpretationCorpus

DASHA_CONTEXT_FRAMING: Final = (
    "These are calculated chart relationships, counted from your D1 Lagna; a reviewed Career "
    "interpretation of this Dasha is not yet available."
)
DASHA_CONTEXT_REVIEWED_FRAMING: Final = (
    "These are calculated chart relationships, counted from your D1 Lagna. The following "
    "reviewed Career interpretation of this Dasha comes from an admitted rule:"
)

_ROLE_NAMES: Final = {"mahadasha": "Mahadasha", "antardasha": "Antardasha"}
_DIGNITY_WORDING: Final[tuple[tuple[LinkageFactName, str], ...]] = (
    ("own_sign", "its own sign"),
    ("exaltation_sign", "its exaltation sign"),
)
_TENTH_CLAUSES: Final[tuple[tuple[LinkageFactName, str, str], ...]] = (
    ("is_tenth_lord", "is your 10th lord", "is not your 10th lord"),
    ("occupies_tenth", "occupies your 10th house", "does not occupy your 10th house"),
    ("aspects_tenth_house", "aspects your 10th house", "does not aspect your 10th house"),
    ("aspects_tenth_lord", "aspects your 10th lord", "does not aspect your 10th lord"),
    (
        "same_sign_as_tenth_lord",
        "is in the same sign as your 10th lord",
        "is not in the same sign as your 10th lord",
    ),
)
_ASPECT_FACTS: Final[tuple[LinkageFactName, ...]] = ("aspects_tenth_house", "aspects_tenth_lord")


def build_dasha_context(
    chart: Chart,
    segments: Sequence[PlannedDashaSegment],
    corpus: DashaInterpretationCorpus,
) -> tuple[tuple[DashaSegmentLinkage, ...], DashaInterpretationSlot]:
    """Return per-segment linkage facts and the admitted-rule slot for those segments."""
    derived = DerivedFactsEngine().calculate(chart)
    linkages = tuple(
        DashaSegmentLinkage(
            segment_id=segment.segment_id,
            linkage=build_pair_linkage(
                chart,
                derived,
                DashaLord(segment.mahadasha_lord),
                DashaLord(segment.antardasha_lord),
            ),
        )
        for segment in segments
    )
    slot = corpus.evaluate((item.segment_id, item.linkage) for item in linkages)
    return linkages, slot


def dasha_context_section(
    linkages: Sequence[DashaSegmentLinkage], slot: DashaInterpretationSlot | None
) -> ConsultationSection | None:
    """Render fact-backed sentences, then one framing line (and admitted wording, if any)."""
    if not linkages:
        return None
    roles: dict[DashaLord, list[str]] = {}
    lords: dict[DashaLord, DashaLordLinkage] = {}
    for item in linkages:
        for role, lord_linkage in (
            ("mahadasha", item.linkage.mahadasha),
            ("antardasha", item.linkage.antardasha),
        ):
            lords.setdefault(lord_linkage.lord, lord_linkage)
            if role not in roles.setdefault(lord_linkage.lord, []):
                roles[lord_linkage.lord].append(role)
    sentences: list[DashaContextSentence] = []
    for lord, lord_linkage in lords.items():
        sentences.extend(_lord_sentences(lord_linkage, roles[lord]))
    seen_pairs: set[str] = set()
    for item in linkages:
        fact = item.linkage.ad_house_from_md
        if fact.fact_id in seen_pairs:
            continue
        seen_pairs.add(fact.fact_id)
        md = _name(item.linkage.mahadasha.lord)
        ad = _name(item.linkage.antardasha.lord)
        sentences.append(
            DashaContextSentence(
                text=(
                    f"{ad} is in the {_ordinal(_int(fact.value))} sign counted from {md}'s sign."
                ),
                fact_ids=(fact.fact_id,),
            )
        )
    claims = slot.claims if slot is not None else ()
    framing = DASHA_CONTEXT_REVIEWED_FRAMING if claims else DASHA_CONTEXT_FRAMING
    parts = [sentence.text for sentence in sentences] + [framing]
    parts.extend(
        f"{claim.mahadasha_lord.title()} Mahadasha, {claim.antardasha_lord.title()} "
        f"Antardasha: {claim.permitted_wording} [{claim.rule_id} v{claim.rule_version}; "
        f"{claim.source_locator}]"
        for claim in claims
    )
    return ConsultationSection(
        kind="dasha_context",
        text=" ".join(parts),
        fact_sentences=tuple(sentences),
        framing=framing,
        interpretation_rule_ids=tuple(
            dict.fromkeys(f"{claim.rule_id}@{claim.rule_version}" for claim in claims)
        ),
    )


def _lord_sentences(linkage: DashaLordLinkage, roles: list[str]) -> list[DashaContextSentence]:
    name = _name(linkage.lord)
    role = " and ".join(_ROLE_NAMES[item] for item in roles)
    sentences: list[DashaContextSentence] = []

    ruled = linkage.fact("ruled_houses")
    houses = ruled.value if isinstance(ruled.value, tuple) else ()
    if houses:
        noun = "house" if len(houses) == 1 else "houses"
        text = f"{name}, your {role} lord, rules your {_join(_ordinal(h) for h in houses)} {noun}."
    else:
        text = (
            f"{name}, your {role} lord, is not assigned sign rulership under the classical "
            "seven-planet lordship convention used here."
        )
    sentences.append(DashaContextSentence(text=text, fact_ids=(ruled.fact_id,)))

    placement = linkage.fact("placement_house")
    sign = linkage.fact("sign")
    placement_ids = [placement.fact_id, sign.fact_id]
    dignity = ""
    for fact_name, wording in _DIGNITY_WORDING:
        dignity_fact = linkage.fact(fact_name)
        if dignity_fact.status is LinkageStatus.KNOWN and dignity_fact.value is True:
            dignity = f", {wording}"
            placement_ids.append(dignity_fact.fact_id)
    sentences.append(
        DashaContextSentence(
            text=(
                f"{name} occupies your {_ordinal(_int(placement.value))} house, "
                f"{str(sign.value).title()}{dignity}."
            ),
            fact_ids=tuple(placement_ids),
        )
    )

    clauses: list[str] = []
    tenth_ids: list[str] = []
    for fact_name, yes, no in _TENTH_CLAUSES:
        fact = linkage.fact(fact_name)
        if fact.status is LinkageStatus.KNOWN:
            clauses.append(yes if fact.value is True else no)
            tenth_ids.append(fact.fact_id)
    sentences.append(
        DashaContextSentence(text=f"{name} {_join(clauses)}.", fact_ids=tuple(tenth_ids))
    )

    aspects = [linkage.fact(fact_name) for fact_name in _ASPECT_FACTS]
    unknown = [fact for fact in aspects if fact.status is LinkageStatus.UNKNOWN]
    if unknown:
        sentences.append(
            DashaContextSentence(
                text=(
                    f"Whether {name} aspects your 10th house or your 10th lord is unknown: "
                    "Rahu and Ketu aspects are not modeled under the seven-planet aspect "
                    "convention used here."
                ),
                fact_ids=tuple(fact.fact_id for fact in unknown),
            )
        )
    return sentences


def _name(lord: DashaLord) -> str:
    return lord.value.title()


def _int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("expected an integer linkage fact")
    return value


def _ordinal(number: int) -> str:
    suffix = (
        "th" if 10 <= number % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    )
    return f"{number}{suffix}"


def _join(items: Iterable[str]) -> str:
    values = list(items)
    if len(values) <= 1:
        return "".join(values)
    return ", ".join(values[:-1]) + " and " + values[-1]
