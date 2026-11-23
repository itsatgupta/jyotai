"""Small, renderer-safe ledger for the active Career evidence and direct answer."""

import re
from datetime import datetime, timedelta, tzinfo

from astrologer.application.career_synthesis import (
    VIMSHOTTARI_METHODOLOGY_ID,
    claim_labels,
    co_reference_sentence,
    why_section,
    year_limit_sentence,
)
from astrologer.application.dasha_context import dasha_context_section
from astrologer.application.detailed_answer import DetailedAnswerBuilder
from astrologer.astrology.dasha_linkage import (
    DASHA_LINKAGE_METHODOLOGY_ID,
    DashaLordLinkage,
    LinkageStatus,
)
from astrologer.composition.career_claims import (
    CareerClaim,
    CareerClaimLedger,
    ClaimKind,
    ClaimStatus,
)
from astrologer.composition.models import (
    CareerAnswerPlan,
    CareerTimingContext,
    ConsultationSection,
    DetailedComposedAnswer,
    PlannedDashaSegment,
    SynthesisSentence,
)
from astrologer.evidence.interpretation import InterpretationEvidence, InterpretationEvidenceItem
from astrologer.knowledge import ACTIVE_PRODUCTION_RELEASE
from astrologer.questions.models import (
    CareerQuestionFocus,
    QuestionDomain,
    QuestionIntent,
    RequestedTimingPrecision,
)
from astrologer.timing_rules.registry import get_active_timing_release


def build_career_ledger(
    evidence: InterpretationEvidence, intent: QuestionIntent, timing: CareerTimingContext | None
) -> CareerClaimLedger:
    """Project only selected active-release evidence and attached governed timing windows."""
    if (
        intent.domain is not QuestionDomain.CAREER
        or evidence.intent.domain is not QuestionDomain.CAREER
    ):
        raise ValueError("Career ledger requires Career evidence")
    focus = intent.career_focus or CareerQuestionFocus.PLACEMENT
    claims: list[CareerClaim] = []
    all_items = evidence.selected_matched + evidence.relevant_unmatched + evidence.relevant_unknown
    first_fact = next((fact for item in all_items for fact in item.resolved_facts), None)
    first_item = next((item for item in all_items if item.resolved_facts), None)
    if first_fact is not None and first_item is not None:
        claims.append(
            _static_claim(
                first_item,
                focus,
                ClaimKind.CALCULATED_FACT,
                ClaimStatus.MATCH,
                DetailedAnswerBuilder._placement(first_item),
                first_fact.fact_id,
                first_fact.fact_id,
            )
        )
    passages = {
        passage.passage_id: passage for passage in ACTIVE_PRODUCTION_RELEASE.registry.passages
    }
    for item in evidence.selected_matched:
        passage_id = item.governance_provenance.passage_id
        passage = passages.get(passage_id)
        if passage is None:
            raise ValueError("selected Career source passage is absent")
        claims.append(
            _static_claim(
                item,
                focus,
                ClaimKind.APPROVED_INTERPRETATION,
                ClaimStatus.MATCH,
                item.reviewed_statement,
                f"{passage_id}: {passage.locator}",
                item.evidence_item_id,
            )
        )
    for kind, items, status in (
        (ClaimKind.INSUFFICIENT_EVIDENCE, evidence.relevant_unmatched, ClaimStatus.NO_MATCH),
        (ClaimKind.INSUFFICIENT_EVIDENCE, evidence.relevant_unknown, ClaimStatus.UNKNOWN),
    ):
        for item in items:
            claims.append(
                _static_claim(
                    item,
                    focus,
                    kind,
                    status,
                    "This reviewed Career rule did not match."
                    if status is ClaimStatus.NO_MATCH
                    else "This reviewed Career rule could not be evaluated.",
                    item.governance_provenance.passage_id,
                    item.evidence_item_id,
                    missing=item.unresolved_fact_ids,
                )
            )
    if timing is not None:
        active_timing = get_active_timing_release()
        if (timing.timing_release_id, timing.timing_release_version) != (
            active_timing.release_id,
            active_timing.release_version,
        ):
            raise ValueError("Career timing context is not from the active release")
        admitted_rules = {str(rule.rule_id): rule for rule in active_timing.rules}
        admitted_sources = (
            active_timing.sources if hasattr(active_timing, "sources") else (active_timing.source,)
        )
        for index, window in enumerate(timing.windows, start=1):
            rule = admitted_rules.get(window.rule_id)
            if rule is None or rule.precision.value != window.precision:
                raise ValueError("Career timing window is not an admitted rule")
            if not any(
                (source.source_work, source.section, source.verse)
                == (window.source.source_work, window.source.section, window.source.verse)
                for source in admitted_sources
            ):
                raise ValueError("Career timing source is not admitted")
            claims.append(
                CareerClaim(
                    claim_id=f"career-timing-{index}",
                    kind=ClaimKind.APPROVED_TIMING_INTERPRETATION,
                    requested_question_shape=focus,
                    fact_ids=rule.required_fact_ids,
                    rule_ids=(window.rule_id,),
                    calculation_version="vimshottari-v1",
                    methodology_version=(
                        f"{timing.timing_release_id}:{timing.timing_release_version}"
                    ),
                    source_reference=(
                        f"{window.source.source_work}, {window.source.section}, "
                        f"verse {window.source.verse}"
                    ),
                    evaluation_status=ClaimStatus.MATCH,
                    permitted_wording=window.reviewed_statement,
                    timing_reference=(
                        f"[{window.effective_start.isoformat()},{window.effective_end.isoformat()})"
                    ),
                    authorized_precision=window.precision,
                )
            )
        if timing.status != "MATCH":
            status = ClaimStatus(timing.status)
            claims.append(
                CareerClaim(
                    claim_id="career-timing-status",
                    kind=(
                        ClaimKind.UNSUPPORTED_REQUEST
                        if status is ClaimStatus.UNSUPPORTED
                        else ClaimKind.INSUFFICIENT_EVIDENCE
                    ),
                    requested_question_shape=focus,
                    rule_ids=tuple(admitted_rules),
                    calculation_version="vimshottari-v1",
                    methodology_version=(
                        f"{timing.timing_release_id}:{timing.timing_release_version}"
                    ),
                    source_reference=timing.timing_release_id,
                    evaluation_status=status,
                    permitted_wording=timing.message,
                    missing_evidence=(
                        ("requested timing method",)
                        if status is ClaimStatus.UNSUPPORTED
                        else ("resolved timing rule facts",)
                        if status is ClaimStatus.UNKNOWN
                        else ()
                    ),
                )
            )
    if focus in {
        CareerQuestionFocus.PROFESSION,
        CareerQuestionFocus.PROMOTION,
        CareerQuestionFocus.COMPARISON,
    } or (
        intent.requested_timing_precision is not None
        and intent.requested_timing_precision.value in {"month", "exact_month", "exact_date"}
    ):
        missing = (
            "two-period comparison method"
            if focus is CareerQuestionFocus.COMPARISON
            else "exact-event Career methodology"
            if focus in {CareerQuestionFocus.PROMOTION, CareerQuestionFocus.PROFESSION}
            else "requested timing precision"
        )
        claims.append(
            CareerClaim(
                claim_id="career-request-limit",
                kind=ClaimKind.UNSUPPORTED_REQUEST,
                requested_question_shape=focus,
                calculation_version=ACTIVE_PRODUCTION_RELEASE.fact_contract.contract_version,
                methodology_version=ACTIVE_PRODUCTION_RELEASE.fact_contract.methodology_id,
                source_reference=evidence.manifest_id,
                evaluation_status=ClaimStatus.UNSUPPORTED,
                permitted_wording="The active Career release does not establish this request.",
                missing_evidence=(missing,),
            )
        )
    if timing is None and intent.requires_timing:
        claims.append(
            CareerClaim(
                claim_id="career-timing-not-evaluated",
                kind=ClaimKind.INSUFFICIENT_EVIDENCE,
                requested_question_shape=focus,
                calculation_version=ACTIVE_PRODUCTION_RELEASE.fact_contract.contract_version,
                methodology_version=ACTIVE_PRODUCTION_RELEASE.fact_contract.methodology_id,
                source_reference=evidence.manifest_id,
                evaluation_status=ClaimStatus.NOT_EVALUATED,
                permitted_wording="Career timing was not evaluated for this request.",
                missing_evidence=("evaluated timing window",),
            )
        )
    return CareerClaimLedger(
        question_shape=intent.shape, requested_question_shape=focus, claims=tuple(claims)
    )


def _static_claim(
    item: InterpretationEvidenceItem,
    focus: CareerQuestionFocus,
    kind: ClaimKind,
    status: ClaimStatus,
    wording: str,
    source: str,
    claim_suffix: str,
    *,
    missing: tuple[str, ...] = (),
) -> CareerClaim:
    return CareerClaim(
        claim_id=f"career-{kind.value.lower()}-{claim_suffix}",
        kind=kind,
        requested_question_shape=focus,
        fact_ids=item.referenced_fact_ids,
        rule_ids=() if kind is ClaimKind.CALCULATED_FACT else (item.rule_id,),
        evidence_item_ids=(item.evidence_item_id,),
        calculation_version=item.fact_provenance.source_register_version,
        methodology_version=item.fact_provenance.methodology_id,
        source_reference=source,
        evaluation_status=status,
        permitted_wording=wording,
        missing_evidence=missing,
    )


def answer_career(
    answer: DetailedComposedAnswer,
    ledger: CareerClaimLedger,
    intent: QuestionIntent,
    plan: CareerAnswerPlan,
    as_of: datetime | None = None,
) -> DetailedComposedAnswer:
    """Use each approved claim independently, without scoring or combining meanings."""
    focus = ledger.requested_question_shape
    facts = [claim for claim in ledger.claims if claim.kind is ClaimKind.CALCULATED_FACT]
    interpretations = [
        claim for claim in ledger.claims if claim.kind is ClaimKind.APPROVED_INTERPRETATION
    ]
    timing = [
        claim for claim in ledger.claims if claim.kind is ClaimKind.APPROVED_TIMING_INTERPRETATION
    ]
    placement = facts[0].permitted_wording if facts else ""
    reviewed = " ".join(claim.permitted_wording for claim in interpretations)
    static_context = reviewed or "No matching reviewed Career interpretation is available."
    sections: tuple[ConsultationSection, ...] = ()
    if focus is CareerQuestionFocus.PERIOD and plan.dasha_segments:
        sections = _year_consultation(plan, ledger, answer.timing, as_of)
        direct = " ".join(section.text for section in sections)
    elif focus is CareerQuestionFocus.STRENGTHS:
        direct = (
            "The reviewed Career evidence gives contextual placement themes, but does not "
            f"rank personal career strengths. {static_context}"
        )
    elif focus is CareerQuestionFocus.DEVELOPMENT:
        direct = (
            "The current reviewed Career rules do not establish a future career trajectory: "
            f"they cover static D1 placement context. {static_context}"
        )
    elif focus is CareerQuestionFocus.COMPARISON:
        years = " and ".join(str(year) for year in intent.comparison_years)
        direct = (
            f"I cannot compare Career outcomes for {years}: no approved two-period comparison "
            "method is active, and the requested comparison was not evaluated. "
            f"The available static context is: {static_context}"
        )
    elif focus is CareerQuestionFocus.PROFESSION:
        direct = (
            f"No approved Career rule identifies a profession from this chart. {static_context}"
        )
    elif focus is CareerQuestionFocus.PROMOTION:
        precision = intent.requested_timing_precision
        if precision is not None and precision.value in {"month", "exact_month"}:
            direct = (
                "No approved exact-month promotion methodology is available, so I cannot "
                "identify a promotion month."
            )
        elif precision is not None and precision.value == "exact_date":
            direct = (
                "No approved exact-date promotion methodology is available, so I cannot "
                "identify a promotion date."
            )
        else:
            direct = "No approved Career rule establishes whether or when a promotion will occur."
        if timing:
            direct += (
                " A reviewed Career timing window is present at its authorized precision, "
                "but it does not establish a promotion event or month."
            )
    elif focus is CareerQuestionFocus.PERIOD:
        if timing:
            period = intent.time_range
            label = (
                str(period.start_date.year)
                if period and period.start_date.year == period.end_date.year
                else "the requested period"
            )
            direct = (
                f"A reviewed Career timing window overlaps {label} at its authorized precision: "
                + " ".join(claim.permitted_wording for claim in timing)
            )
        elif answer.timing is None:
            direct = f"Career timing was not evaluated for this request. {static_context}"
        elif answer.timing.status == "NO_MATCH":
            direct = (
                f"No reviewed Career timing rule matched the requested period. {static_context}"
            )
        elif answer.timing.status == "UNKNOWN":
            direct = (
                f"Career timing could not be evaluated from the available facts. {static_context}"
            )
        else:
            direct = f"The requested Career timing period is unsupported. {static_context}"
    else:
        direct = static_context
    if focus not in {CareerQuestionFocus.PROMOTION, CareerQuestionFocus.COMPARISON} and (
        intent.requested_timing_precision is not None
        and intent.requested_timing_precision.value in {"month", "exact_month", "exact_date"}
    ):
        direct = (
            "The requested timing precision is unsupported by the active Career methods. " + direct
        )
    if placement and not (focus is CareerQuestionFocus.PERIOD and plan.dasha_segments):
        direct = f"{placement} {direct}"
    return answer.model_copy(
        update={
            "answer": direct,
            "claim_ledger": ledger,
            "career_answer_plan": plan,
            "consultation_sections": sections,
            "timing_answered": (
                focus is CareerQuestionFocus.PERIOD
                and intent.requested_timing_precision in (None, RequestedTimingPrecision.BROAD)
                and bool(timing)
            ),
            "corpus_limitation": not bool(interpretations),
        }
    )


def _year_consultation(
    plan: CareerAnswerPlan,
    ledger: CareerClaimLedger,
    timing: CareerTimingContext | None,
    as_of: datetime | None = None,
) -> tuple[ConsultationSection, ...]:
    """Compose the requested year from explicit evidence, without Dasha interpretation."""
    scope = plan.requested_time_scope
    assert scope is not None and scope.start_date.year == scope.end_date.year
    year = scope.start_date.year
    facts = [claim for claim in ledger.claims if claim.kind is ClaimKind.CALCULATED_FACT]
    natal = [
        claim
        for claim in ledger.claims
        if claim.kind is ClaimKind.APPROVED_INTERPRETATION
        and claim.claim_id in plan.matched_claim_ids
    ]
    timed = [
        claim
        for claim in ledger.claims
        if claim.kind is ClaimKind.APPROVED_TIMING_INTERPRETATION
        and claim.claim_id in plan.matched_claim_ids
    ]
    if natal:
        natal_text = (
            "The available reviewed natal Career context is: "
            + (facts[0].permitted_wording + " " if facts else "")
            + " ".join(claim.permitted_wording for claim in natal)
        )
    elif facts:
        natal_text = (
            f"The calculated chart shows {facts[0].permitted_wording} "
            "No reviewed natal Career interpretation matched this placement."
        )
    else:
        natal_text = "No reviewed natal Career interpretation is available."
    chronology = "; ".join(_dasha_phrase(segment) for segment in plan.dasha_segments)
    sections = [_year_direct_section(plan, year, timed, timing, ledger.claims, natal, as_of)]
    if plan.synthesis is not None:
        sections.append(why_section(plan.synthesis))
    sections.append(ConsultationSection(kind="natal", text=natal_text))
    sections += [
        ConsultationSection(
            kind="dasha",
            text=f"Calculated Vimshottari periods in {year} (local dates): {chronology}.",
        ),
    ]
    context = dasha_context_section(
        plan.dasha_linkages, plan.dasha_interpretation, plan.dasha_segments
    )
    if context is not None:
        sections.append(context)
    if timed:
        assert timing is not None
        zone = plan.dasha_segments[0].local_start.tzinfo
        assert zone is not None
        windows = {
            f"[{window.effective_start.isoformat()},{window.effective_end.isoformat()})": window
            for window in timing.windows
        }
        descriptions = []
        for claim in timed:
            if claim.timing_reference is None:
                raise ValueError("approved Career timing claim lacks its interval reference")
            window = windows.get(claim.timing_reference)
            if window is None:
                raise ValueError("approved Career timing claim lacks its display window")
            precision = (
                "broad period" if claim.authorized_precision == "BROAD_PERIOD" else "sub-period"
            )
            dates = _local_date_span(window.effective_start, window.effective_end, zone)
            descriptions.append(f"{precision} {dates}: {claim.permitted_wording}")
        sections.append(
            ConsultationSection(
                kind="timing",
                text="Reviewed Career timing context: " + " ".join(descriptions),
            )
        )
    elif timing is None:
        sections.append(
            ConsultationSection(
                kind="timing", text="Reviewed Career timing was not evaluated for this request."
            )
        )
    elif timing.status == "NO_MATCH":
        sections.append(
            ConsultationSection(
                kind="timing", text=f"No reviewed Career timing rule matched {year}."
            )
        )
    elif timing.status == "UNKNOWN":
        sections.append(
            ConsultationSection(
                kind="timing",
                text=(
                    "The reviewed Career timing rules could not be evaluated from available facts."
                ),
            )
        )
    else:
        sections.append(ConsultationSection(kind="timing", text=timing.message))
    sections.append(
        ConsultationSection(
            kind="limit",
            text="The available reviewed timing evidence does not establish a specific "
            f"Career outcome for {year}.",
        )
    )
    return tuple(sections)


_SENTENCE_BREAK = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")
_NON_GUARANTEE = re.compile(r"^It does not (?:guarantee|establish)\b")


def timing_meaning_and_limit(wording: str) -> tuple[str, str | None]:
    """Split admitted timing wording into its meaning sentence and its non-guarantee clause.

    Both parts are verbatim sentences of the admitted wording; nothing is rephrased.
    """
    sentences = _SENTENCE_BREAK.split(wording.strip())
    limit = next((item for item in sentences[1:] if _NON_GUARANTEE.match(item)), None)
    return sentences[0], limit


# Short display names for admitted source works; an unknown work is shown in full.
_SOURCE_SHORT_NAMES = {"Brihat Parāśara Horā Śāstra": "BPHS"}


def _year_direct_section(
    plan: CareerAnswerPlan,
    year: int,
    timed: list[CareerClaim],
    timing: CareerTimingContext | None,
    claims: tuple[CareerClaim, ...],
    natal: list[CareerClaim],
    as_of: datetime | None = None,
) -> ConsultationSection:
    """Two or three plain sentences built only from calculated facts and admitted text.

    * One matched timing rule: a personal framing sentence (period lord, its calculated
      houses), then the admitted meaning and its non-guarantee sentence, verbatim.
    * No matched timing rule: the year's MD/AD periods, the reviewed natal indication by
      its plain label, then the timing status.  Co-references stay in the Why section.
    * Several matched timing rules: their status, the co-reference, then the limit.
    """
    synthesis = plan.synthesis
    limit = year_limit_sentence(year, plan.limitation_ids)
    sentences: tuple[SynthesisSentence, ...]
    if len(timed) == 1:
        meaning, guarantee = timing_meaning_and_limit(timed[0].permitted_wording)
        framing = _timing_framing_sentence(plan, timed[0], timing, as_of)
        lead = [framing] if framing is not None else []
        lead.append(
            SynthesisSentence(
                text=meaning, claim_ids=(timed[0].claim_id,), rule_ids=timed[0].rule_ids
            )
        )
        closing = guarantee or limit
        if closing is not None:
            lead.append(
                SynthesisSentence(
                    text=closing,
                    claim_ids=(timed[0].claim_id,) if guarantee else (),
                    rule_ids=timed[0].rule_ids if guarantee else (),
                )
            )
        sentences = tuple(lead)
    elif not timed:
        sentences = (
            *_periods_sentence(plan, year),
            _natal_sentence(natal),
            _no_timing_sentence(year, timing, limit),
        )
    else:
        status = SynthesisSentence(
            text=(
                f"For {year}, {len(timed)} reviewed Career timing indications apply; each is "
                "quoted in full in the timing section."
            ),
            claim_ids=tuple(c.claim_id for c in timed),
        )
        middle = [co_reference_sentence(synthesis, claims)] if synthesis is not None else []
        tail = [SynthesisSentence(text=limit)] if limit is not None else []
        sentences = (status, *middle, *tail)
    return ConsultationSection(
        kind="direct",
        text=" ".join(sentence.text for sentence in sentences),
        synthesis_sentences=sentences,
    )


def _timing_framing_sentence(
    plan: CareerAnswerPlan,
    claim: CareerClaim,
    timing: CareerTimingContext | None,
    as_of: datetime | None,
) -> SynthesisSentence | None:
    """'Your current <Planet> Mahadasha matches a reviewed <source> timing rule: ...'.

    Every word comes from calculated facts: the window's period lords, the source work of
    the matched rule, and the period lord's calculated linkage facts (10th lordship and
    placement house).  Returns None when the window or the lord's linkage is not found.
    """
    if timing is None or claim.timing_reference is None:
        return None
    window = next(
        (
            item
            for item in timing.windows
            if f"[{item.effective_start.isoformat()},{item.effective_end.isoformat()})"
            == claim.timing_reference
        ),
        None,
    )
    if window is None or window.mahadasha_lord is None:
        return None
    md = window.mahadasha_lord.lower()
    ad = window.antardasha_lord.lower() if window.antardasha_lord else None
    lord: DashaLordLinkage | None = None
    segment_ids: list[str] = []
    for item in plan.dasha_linkages:
        pair = item.linkage
        if pair.mahadasha.lord.value != md or (ad is not None and pair.antardasha.lord.value != ad):
            continue
        lord = lord or (pair.antardasha if ad is not None else pair.mahadasha)
        segment_ids.append(item.segment_id)
    if lord is None:
        return None
    current = as_of is not None and window.source_start <= as_of < window.source_end
    period = f"{md.title()} Mahadasha" + (f", {ad.title()} Antardasha" if ad else "")
    year = plan.requested_time_scope.start_date.year if plan.requested_time_scope else None
    opening = f"Your current {period}" if current or year is None else f"Your {period} in {year}"
    source = _SOURCE_SHORT_NAMES.get(window.source.source_work, window.source.source_work)
    name = lord.lord.value.title()
    tenth = lord.fact("is_tenth_lord")
    placement = lord.fact("placement_house")
    details: list[str] = []
    fact_ids: list[str] = []
    if tenth.status is LinkageStatus.KNOWN and tenth.value is True:
        details.append("is your 10th lord")
        fact_ids.append(tenth.fact_id)
    if (
        placement.status is LinkageStatus.KNOWN
        and isinstance(placement.value, int)
        and not isinstance(placement.value, bool)
    ):
        details.append(f"sits in your {_ordinal(placement.value)} house")
        fact_ids.append(placement.fact_id)
    text = f"{opening} matches a reviewed {source} timing rule"
    text += f": {name} {' and '.join(details)}." if details else "."
    return SynthesisSentence(
        text=text,
        claim_ids=(claim.claim_id,),
        fact_ids=(*segment_ids, *fact_ids),
        rule_ids=claim.rule_ids,
        calc_method_ids=(VIMSHOTTARI_METHODOLOGY_ID, DASHA_LINKAGE_METHODOLOGY_ID),
    )


def _periods_sentence(plan: CareerAnswerPlan, year: int) -> tuple[SynthesisSentence, ...]:
    """The asked year's calculated MD/AD periods, grouped by Mahadasha, in local dates."""
    if not plan.dasha_segments:
        return ()
    groups: dict[str, list[PlannedDashaSegment]] = {}
    for segment in plan.dasha_segments:
        groups.setdefault(segment.mahadasha_lord, []).append(segment)
    parts = []
    for md, segments in groups.items():
        ads = [
            f"the {segment.antardasha_lord.title()} Antardasha ({_segment_dates(segment)})"
            for segment in segments
        ]
        joined = ads[0] if len(ads) == 1 else ", ".join(ads[:-1]) + " and " + ads[-1]
        parts.append(f"the {md.title()} Mahadasha with {joined}")
    return (
        SynthesisSentence(
            text=f"In {year} your calculated Vimshottari periods are {', then '.join(parts)}.",
            fact_ids=tuple(segment.segment_id for segment in plan.dasha_segments),
            calc_method_ids=(VIMSHOTTARI_METHODOLOGY_ID,),
        ),
    )


def _segment_dates(segment: PlannedDashaSegment) -> str:
    zone = segment.local_start.tzinfo
    assert zone is not None
    return _local_date_span(segment.local_start, segment.local_end, zone)


def _natal_sentence(natal: list[CareerClaim]) -> SynthesisSentence:
    """The reviewed natal indication(s) by plain label; no co-reference to the periods."""
    if not natal:
        return SynthesisSentence(text="No reviewed natal Career indication matched your chart.")
    labels = list(claim_labels(natal).values())
    joined = labels[0] if len(labels) == 1 else ", ".join(labels[:-1]) + " and " + labels[-1]
    return SynthesisSentence(
        text=f"Your chart matches {joined}.",
        claim_ids=tuple(claim.claim_id for claim in natal),
        fact_ids=tuple(dict.fromkeys(f for claim in natal for f in claim.fact_ids)),
        rule_ids=tuple(dict.fromkeys(r for claim in natal for r in claim.rule_ids)),
    )


def _no_timing_sentence(
    year: int, timing: CareerTimingContext | None, limit: str | None
) -> SynthesisSentence:
    if timing is None:
        status = f"Reviewed Career timing was not evaluated for {year}"
    elif timing.status == "UNKNOWN":
        status = (
            f"The reviewed Career timing rules could not be evaluated for {year} from "
            "available facts"
        )
    else:
        status = f"No reviewed timing rule applies to {year}"
    if limit is not None:
        return SynthesisSentence(
            text=f"{status}, so no specific Career event is established for this year."
        )
    return SynthesisSentence(text=f"{status}.")


def _ordinal(number: int) -> str:
    suffix = (
        "th" if 10 <= number % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    )
    return f"{number}{suffix}"


def _dasha_phrase(segment: PlannedDashaSegment) -> str:
    start = segment.local_start
    end_inclusive = segment.local_end - timedelta(microseconds=1)
    start_label = _date_label(start)
    end_label = _date_label(end_inclusive)
    return (
        f"{start_label}–{end_label}: {segment.mahadasha_lord.title()} Mahadasha, "
        f"{segment.antardasha_lord.title()} Antardasha"
    )


def _local_date_span(start: datetime, end: datetime, zone: tzinfo) -> str:
    local_start = start.astimezone(zone)
    local_end = (end - timedelta(microseconds=1)).astimezone(zone)
    return f"{_date_label(local_start)}–{_date_label(local_end)}"


def _date_label(value: datetime) -> str:
    return f"{value.strftime('%b')} {value.day}"
