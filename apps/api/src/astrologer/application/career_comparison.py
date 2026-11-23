"""``comparison-view-v1``: a factual side-by-side of two calendar years, without ranking.

Each column is one complete, independently evaluated single-year Career answer (the same
pipeline that answers "How is my career in 2027?").  The view only places the two columns
next to each other and lists factual differences between them:

* the calculated MD/AD periods and their local dates;
* which reviewed timing indications apply, quoted verbatim in the columns; and
* co-reference links (``career-synthesis-v1``) present in one year only.

It never combines, weighs, counts, or ranks anything.  Every sentence is either built from
calculated facts, an admitted rule (verbatim text or its plain label), or one of the fixed
texts below.  No new doctrine is introduced: no polarity, dimension, or preference.
"""

from collections.abc import Sequence
from typing import Final

from astrologer.application.career_claims import (
    local_date_span,
    tenth_lord_phrase,
    year_periods_sentence,
)
from astrologer.application.career_synthesis import claim_labels
from astrologer.astrology.dasha_linkage import DASHA_LINKAGE_METHODOLOGY_ID
from astrologer.composition.career_claims import CareerClaim, ClaimKind
from astrologer.composition.models import (
    CareerAnswerPlan,
    CareerYearColumn,
    CareerYearComparison,
    ComparisonSentence,
    ComparisonTimingIndication,
    DetailedComposedAnswer,
    SynthesisLink,
    SynthesisSentence,
)
from astrologer.knowledge import ACTIVE_PRODUCTION_RELEASE

COMPARISON_VIEW_VERSION: Final = "comparison-view-v1"

# Fixed texts.  ``{a}``/``{b}`` are the earlier/later year and ``{year}`` a column year.
DIRECT_NO_RANKING: Final = (
    "I can't rank {a} against {b} for your career: JyotishAI has no reviewed method for "
    "ranking periods."
)
DIRECT_TIMING_ONE_SIDED: Final = (
    "A reviewed timing indication applies in {with_year} and none applies in {without_year}."
)
DIRECT_TIMING_BOTH_SAME: Final = "The same reviewed timing indication applies in both years."
DIRECT_TIMING_BOTH_DIFFERENT: Final = "Different reviewed timing indications apply in {a} and {b}."
DIRECT_TIMING_NEITHER: Final = "No reviewed timing indication applies in either year."
DIRECT_TIMING_NOT_SETTLED: Final = (
    "Reviewed timing could not be evaluated for both years, so the timing side is incomplete."
)
DIRECT_SIDE_BY_SIDE: Final = "Here is what was calculated for each year, side by side."
ABSENCE_NOT_AGAINST: Final = (
    "An indication not applying in a year is not evidence against that year."
)
TIMING_NONE_IN_YEAR: Final = "In {year}, no reviewed timing indication applies."
TIMING_NOT_EVALUATED_IN_YEAR: Final = "In {year}, reviewed Career timing was not evaluated."
TIMING_UNKNOWN_IN_YEAR: Final = (
    "In {year}, the reviewed Career timing rules could not be evaluated from available facts."
)
TIMING_UNSUPPORTED_IN_YEAR: Final = (
    "In {year}, reviewed Career timing was not evaluated: the year is outside the supported "
    "forward timing horizon."
)
COLUMN_NO_TIMING: Final = "No reviewed timing indication applies."
COLUMN_NO_LINKS: Final = "No co-reference link was found for this year."
COLUMN_NO_PERIODS: Final = "Calculated Dasha periods for {year} are unavailable for this profile."
COLUMN_NO_DASHA_MEANING: Final = (
    "No reviewed interpretation of these Dasha periods is admitted; the lord facts above are "
    "calculated relationships only."
)
NATAL_NONE: Final = "No reviewed natal Career indication matched your chart."
NATAL_SAME: Final = (
    "This natal context comes from the birth chart, so it is the same for {a} and {b} and "
    "does not tell the years apart."
)
LINKS_ONLY_IN: Final = "Only in {year}: {text}"
WHY_NOT_A_VERDICT: Final = (
    "This is a factual side-by-side, not a verdict. JyotishAI has no reviewed method for "
    "ranking one period above another, so it shows what was calculated and which reviewed "
    "indications apply in each, without ranking them."
)
WHY_CONTEXT_ONLY: Final = (
    "The reviewed rules describe context. None of them has an approved direction or an "
    "approved way to compare periods, so listing them side by side is as far as the evidence "
    "goes."
)
LIMITATION_NO_EVENT: Final = (
    "None of this establishes a specific event, promotion, income change, or date."
)

FIXED_TEMPLATES: Final[tuple[str, ...]] = (
    DIRECT_NO_RANKING,
    DIRECT_TIMING_ONE_SIDED,
    DIRECT_TIMING_BOTH_SAME,
    DIRECT_TIMING_BOTH_DIFFERENT,
    DIRECT_TIMING_NEITHER,
    DIRECT_TIMING_NOT_SETTLED,
    DIRECT_SIDE_BY_SIDE,
    ABSENCE_NOT_AGAINST,
    TIMING_NONE_IN_YEAR,
    TIMING_NOT_EVALUATED_IN_YEAR,
    TIMING_UNKNOWN_IN_YEAR,
    TIMING_UNSUPPORTED_IN_YEAR,
    COLUMN_NO_TIMING,
    COLUMN_NO_LINKS,
    COLUMN_NO_PERIODS,
    COLUMN_NO_DASHA_MEANING,
    NATAL_NONE,
    NATAL_SAME,
    WHY_NOT_A_VERDICT,
    WHY_CONTEXT_ONLY,
    LIMITATION_NO_EVENT,
)


def fixed_texts(years: tuple[int, int]) -> frozenset[str]:
    """Every fixed text the view may render for ``years`` (used by the guard tests)."""
    a, b = years
    values: set[str] = set()
    for template in FIXED_TEMPLATES:
        for year in years:
            values.add(
                template.format(
                    a=a,
                    b=b,
                    year=year,
                    with_year=year,
                    without_year=b if year == a else a,
                )
            )
    return frozenset(values)


class ComparisonUnavailable(ValueError):
    """A year column could not be built from a single-year Career answer."""


def build_career_year_comparison(
    years: tuple[int, int], answers: tuple[DetailedComposedAnswer, DetailedComposedAnswer]
) -> CareerYearComparison:
    """Place two independently built year answers side by side; never rank them."""
    a, b = sorted(years)
    if a == b:
        raise ComparisonUnavailable("a comparison needs two different years")
    by_year = dict(zip(years, answers, strict=True))
    if {r for c in _natal_claims(by_year[a]) for r in c.rule_ids} != {
        r for c in _natal_claims(by_year[b]) for r in c.rule_ids
    }:
        raise ComparisonUnavailable("natal evidence differs between the two year answers")
    first, second = _column(a, by_year[a]), _column(b, by_year[b])
    plan = _plan(by_year[a])
    return CareerYearComparison(
        years=(a, b),
        direct=_direct(a, b, first, second),
        differences=_differences(a, b, first, second, by_year[a], by_year[b]),
        natal_shared=_natal(a, b, by_year[a], plan),
        columns=(first, second),
        why_no_ranking=(_fixed(WHY_NOT_A_VERDICT), _fixed(WHY_CONTEXT_ONLY)),
        limitations=(_fixed(LIMITATION_NO_EVENT),),
    )


def _plan(answer: DetailedComposedAnswer) -> CareerAnswerPlan:
    plan = answer.career_answer_plan
    if plan is None or answer.claim_ledger is None:
        raise ComparisonUnavailable("a comparison column needs a planned Career year answer")
    return plan


def _fixed(text: str) -> ComparisonSentence:
    return ComparisonSentence(text=text, basis="fixed")


def _from_synthesis(sentence: SynthesisSentence) -> ComparisonSentence:
    return ComparisonSentence(
        text=sentence.text,
        basis="rule" if sentence.rule_ids else "fact",
        claim_ids=sentence.claim_ids,
        fact_ids=sentence.fact_ids,
        rule_ids=sentence.rule_ids,
        calc_method_ids=sentence.calc_method_ids,
    )


def _timing_claims(answer: DetailedComposedAnswer) -> tuple[CareerClaim, ...]:
    ledger = answer.claim_ledger
    return tuple(
        claim
        for claim in (ledger.claims if ledger else ())
        if claim.kind is ClaimKind.APPROVED_TIMING_INTERPRETATION
    )


def _natal_claims(answer: DetailedComposedAnswer) -> list[CareerClaim]:
    ledger = answer.claim_ledger
    return [
        claim
        for claim in (ledger.claims if ledger else ())
        if claim.kind is ClaimKind.APPROVED_INTERPRETATION
    ]


def _column(year: int, answer: DetailedComposedAnswer) -> CareerYearColumn:
    plan = _plan(answer)
    scope = plan.requested_time_scope
    if scope is None or scope.start_date.year != year or scope.end_date.year != year:
        raise ComparisonUnavailable("a comparison column must be one calendar year")
    periods = tuple(_from_synthesis(item) for item in year_periods_sentence(plan, year)) or (
        _fixed(COLUMN_NO_PERIODS.format(year=year)),
    )
    context = next(
        (section for section in answer.consultation_sections if section.kind == "dasha_context"),
        None,
    )
    lord_facts = tuple(
        ComparisonSentence(
            text=sentence.text,
            basis="fact",
            fact_ids=sentence.fact_ids,
            calc_method_ids=(DASHA_LINKAGE_METHODOLOGY_ID,),
        )
        for sentence in (context.fact_sentences if context else ())
    )
    timing = answer.timing
    status = timing.status if timing is not None else "NOT_EVALUATED"
    indications = _indications(answer, plan)
    labels = {item.claim_id: item for item in indications}
    timing_sentences: list[ComparisonSentence] = []
    for claim in _timing_claims(answer):
        item = labels[claim.claim_id]
        timing_sentences.append(
            ComparisonSentence(
                text=f"{item.label[0].upper()}{item.label[1:]} applies ({item.local_span}).",
                basis="rule",
                claim_ids=(claim.claim_id,),
                rule_ids=claim.rule_ids,
                fact_ids=claim.fact_ids,
            )
        )
        # Admitted text, byte-for-byte; never reworded.
        timing_sentences.append(
            ComparisonSentence(
                text=claim.permitted_wording,
                basis="rule",
                claim_ids=(claim.claim_id,),
                rule_ids=claim.rule_ids,
            )
        )
    if not timing_sentences:
        timing_sentences.append(_fixed(_status_text(year, status, column=True)))
    synthesis = plan.synthesis
    links = _unique_links(synthesis.links if synthesis else ())
    co_references = tuple(_link_sentence(link) for link in links) or (_fixed(COLUMN_NO_LINKS),)
    slot = plan.dasha_interpretation
    if slot is not None and slot.claims:
        interpretation = ComparisonSentence(
            text=" ".join(claim.permitted_wording for claim in slot.claims),
            basis="rule",
            rule_ids=tuple(dict.fromkeys(claim.rule_id for claim in slot.claims)),
        )
    else:
        interpretation = _fixed(COLUMN_NO_DASHA_MEANING)
    return CareerYearColumn(
        year=year,
        dasha_segments=plan.dasha_segments,
        periods=periods,
        lord_facts=lord_facts,
        timing_status=status,
        timing_indications=indications,
        timing=tuple(timing_sentences),
        co_references=co_references,
        dasha_interpretation=interpretation,
        manifest_id=answer.manifest_id,
        manifest_version=answer.manifest_version,
        methodology_version=(
            f"{ACTIVE_PRODUCTION_RELEASE.fact_contract.methodology_id}:"
            f"{ACTIVE_PRODUCTION_RELEASE.fact_contract.contract_version}"
        ),
        timing_release_id=timing.timing_release_id if timing else "",
        timing_release_version=timing.timing_release_version if timing else "",
        synthesis_version=synthesis.synthesis_version if synthesis else None,
        answer_plan_version=plan.plan_version,
    )


def _indications(
    answer: DetailedComposedAnswer, plan: CareerAnswerPlan
) -> tuple[ComparisonTimingIndication, ...]:
    claims = _timing_claims(answer)
    if not claims:
        return ()
    timing = answer.timing
    if timing is None:
        raise ComparisonUnavailable("a timing claim has no timing context")
    windows = {
        f"[{window.effective_start.isoformat()},{window.effective_end.isoformat()})": window
        for window in timing.windows
    }
    labels = claim_labels(claims)
    zone = plan.dasha_segments[0].local_start.tzinfo if plan.dasha_segments else None
    result = []
    for claim in claims:
        window = windows.get(claim.timing_reference or "")
        if window is None or zone is None or claim.authorized_precision is None:
            raise ComparisonUnavailable("a timing claim lacks its display window")
        result.append(
            ComparisonTimingIndication(
                claim_id=claim.claim_id,
                rule_id=claim.rule_ids[0],
                label=labels[claim.claim_id],
                reviewed_statement=claim.permitted_wording,
                source_reference=claim.source_reference,
                precision=window.precision,
                local_span=local_date_span(window.effective_start, window.effective_end, zone),
            )
        )
    return tuple(result)


def _status_text(year: int, status: str, *, column: bool = False) -> str:
    if status in {"NO_MATCH", "MATCH"}:
        return COLUMN_NO_TIMING if column else TIMING_NONE_IN_YEAR.format(year=year)
    if status == "UNKNOWN":
        return TIMING_UNKNOWN_IN_YEAR.format(year=year)
    if status == "UNSUPPORTED":
        return TIMING_UNSUPPORTED_IN_YEAR.format(year=year)
    return TIMING_NOT_EVALUATED_IN_YEAR.format(year=year)


def _unique_links(links: Sequence[SynthesisLink]) -> tuple[SynthesisLink, ...]:
    seen: dict[str, SynthesisLink] = {}
    for link in links:
        seen.setdefault(link.text, link)
    return tuple(seen.values())


def _link_sentence(link: SynthesisLink, prefix: str | None = None) -> ComparisonSentence:
    text = LINKS_ONLY_IN.format(year=prefix, text=link.text) if prefix else link.text
    return ComparisonSentence(
        text=text,
        basis="rule",
        claim_ids=(link.claim_id,),
        fact_ids=tuple(dict.fromkeys((*link.claim_fact_ids, *link.dasha_fact_ids))),
        rule_ids=tuple(dict.fromkeys((*link.claim_rule_ids, *link.dasha_rule_ids))),
        calc_method_ids=link.calc_method_ids,
    )


def _link_key(link: SynthesisLink) -> tuple[str, str, str, str]:
    """What a link connects, without its dates: a period interval always differs by year."""
    if link.link_type == "SAME_PERIOD":
        return (link.link_type, link.claim_label, "", "")
    return (
        link.link_type,
        link.claim_label,
        link.shared_reference,
        f"{link.period_role}:{link.period_lord}",
    )


def _rule_set(column: CareerYearColumn) -> frozenset[str]:
    return frozenset(item.rule_id for item in column.timing_indications)


def _settled(column: CareerYearColumn) -> bool:
    return column.timing_status in {"MATCH", "NO_MATCH"}


def _direct(
    a: int, b: int, first: CareerYearColumn, second: CareerYearColumn
) -> tuple[ComparisonSentence, ...]:
    lead = _fixed(DIRECT_NO_RANKING.format(a=a, b=b))
    rules_a, rules_b = _rule_set(first), _rule_set(second)
    if not (_settled(first) and _settled(second)):
        timing = _fixed(DIRECT_TIMING_NOT_SETTLED)
    elif rules_a and rules_b:
        timing = _fixed(
            DIRECT_TIMING_BOTH_SAME
            if rules_a == rules_b
            else DIRECT_TIMING_BOTH_DIFFERENT.format(a=a, b=b)
        )
    elif rules_a or rules_b:
        with_year, without_year = (a, b) if rules_a else (b, a)
        timing = _fixed(
            DIRECT_TIMING_ONE_SIDED.format(with_year=with_year, without_year=without_year)
        )
    else:
        timing = _fixed(DIRECT_TIMING_NEITHER)
    return (lead, timing, _fixed(DIRECT_SIDE_BY_SIDE))


def _year_timing_sentence(column: CareerYearColumn) -> ComparisonSentence:
    """'In 2027, <label> applies (Jan 1–Dec 31).' or the year's fixed status line."""
    if not column.timing_indications:
        return _fixed(_status_text(column.year, column.timing_status))
    parts = [f"{item.label} applies ({item.local_span})" for item in column.timing_indications]
    joined = parts[0] if len(parts) == 1 else "; ".join(parts[:-1]) + "; and " + parts[-1]
    return ComparisonSentence(
        text=f"In {column.year}, {joined}.",
        basis="rule",
        claim_ids=tuple(item.claim_id for item in column.timing_indications),
        rule_ids=tuple(dict.fromkeys(item.rule_id for item in column.timing_indications)),
    )


def _differences(
    a: int,
    b: int,
    first: CareerYearColumn,
    second: CareerYearColumn,
    answer_a: DetailedComposedAnswer,
    answer_b: DetailedComposedAnswer,
) -> tuple[ComparisonSentence, ...]:
    """Only factual differences: periods and dates, applying indications, one-year links."""
    sentences: list[ComparisonSentence] = [*first.periods, *second.periods]
    rules_a, rules_b = _rule_set(first), _rule_set(second)
    spans_differ = [item.local_span for item in first.timing_indications] != [
        item.local_span for item in second.timing_indications
    ]
    if rules_a != rules_b or first.timing_status != second.timing_status or spans_differ:
        sentences += [_year_timing_sentence(first), _year_timing_sentence(second)]
    if (rules_a - rules_b) or (rules_b - rules_a):
        sentences.append(_fixed(ABSENCE_NOT_AGAINST))
    links_a = _unique_links(_links(answer_a))
    links_b = _unique_links(_links(answer_b))
    keys_a = {_link_key(link) for link in links_a}
    keys_b = {_link_key(link) for link in links_b}
    sentences += [_link_sentence(link, str(a)) for link in links_a if _link_key(link) not in keys_b]
    sentences += [_link_sentence(link, str(b)) for link in links_b if _link_key(link) not in keys_a]
    return tuple(sentences)


def _links(answer: DetailedComposedAnswer) -> tuple[SynthesisLink, ...]:
    synthesis = _plan(answer).synthesis
    return synthesis.links if synthesis else ()


def _natal(
    a: int, b: int, answer: DetailedComposedAnswer, plan: CareerAnswerPlan
) -> tuple[ComparisonSentence, ...]:
    """The year-invariant natal context, shown once (E1: the 10th lord named first)."""
    natal = _natal_claims(answer)
    named = tenth_lord_phrase(plan)
    sentences: list[ComparisonSentence] = []
    if named is not None:
        sentences.append(ComparisonSentence(text=f"{named[0]}.", basis="fact", fact_ids=named[1]))
    if natal:
        labels = list(claim_labels(natal).values())
        joined = labels[0] if len(labels) == 1 else ", ".join(labels[:-1]) + " and " + labels[-1]
        sentences.append(
            ComparisonSentence(
                text=f"Your chart matches {joined}.",
                basis="rule",
                claim_ids=tuple(claim.claim_id for claim in natal),
                fact_ids=tuple(dict.fromkeys(f for claim in natal for f in claim.fact_ids)),
                rule_ids=tuple(dict.fromkeys(r for claim in natal for r in claim.rule_ids)),
            )
        )
    else:
        sentences.append(_fixed(NATAL_NONE))
    sentences.append(_fixed(NATAL_SAME.format(a=a, b=b)))
    return tuple(sentences)
