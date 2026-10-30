"""Short-lived, evidence-linked Ask consultation state and deterministic follow-ups."""

import hashlib
import json
import re
import time
from dataclasses import dataclass
from threading import Lock
from typing import Annotated, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from astrologer.application.analyze import DeterministicAnalysisRequest
from astrologer.application.answer import AskJyotAIResult, AskJyotAIService
from astrologer.composition.career_claims import CareerClaim, ClaimKind
from astrologer.composition.models import DetailedComposedAnswer
from astrologer.knowledge import ACTIVE_PRODUCTION_RELEASE
from astrologer.questions.models import QuestionDomain, QuestionIntent
from astrologer.timing_rules.registry import get_active_timing_release


class ConsultationError(ValueError):
    """A stale, cross-profile, or forged consultation reference."""


class ConsultationRequest(DeterministicAnalysisRequest):
    consultation_id: str | None = Field(default=None, max_length=64)
    reference_turn_id: str | None = Field(default=None, max_length=64)
    claim_ids: tuple[Annotated[str, Field(min_length=1, max_length=256)], ...] = Field(
        default=(), max_length=20
    )
    evidence_item_ids: tuple[Annotated[str, Field(min_length=1, max_length=256)], ...] = Field(
        default=(), max_length=20
    )
    timing_references: tuple[Annotated[str, Field(min_length=1, max_length=256)], ...] = Field(
        default=(), max_length=20
    )


class ConsultationTurn(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    consultation_id: str
    turn_id: str
    domain: QuestionDomain | None = None
    intent: QuestionIntent | None = None
    claim_ids: tuple[str, ...] = ()
    evidence_item_ids: tuple[str, ...] = ()
    timing_references: tuple[str, ...] = ()
    manifest_id: str
    manifest_version: str
    methodology_version: str
    timing_release_id: str
    timing_release_version: str
    limitation: bool = False


class ConsultationResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    state: ConsultationTurn
    analysis: AskJyotAIResult | None = None
    reply: str | None = None
    status: Literal["answered", "clarification", "unsupported"] = "answered"
    source_references: tuple[str, ...] = ()
    resolved_claim_ids: tuple[str, ...] = ()
    resolved_evidence_item_ids: tuple[str, ...] = ()
    resolved_timing_references: tuple[str, ...] = ()


@dataclass(frozen=True)
class _Anchor:
    intent: QuestionIntent
    answer: DetailedComposedAnswer


@dataclass(frozen=True)
class _Record:
    profile_hash: str
    as_of: str
    anchor: _Anchor | None
    anchor_turn_id: str
    domains: tuple[QuestionDomain, ...]
    release: tuple[str, ...]
    expires_at: float


class ConsultationStore:
    """Process-local bounded state; holds no birth input, chart, or question transcript."""

    def __init__(self) -> None:
        self._records: dict[str, _Record] = {}
        self._lock = Lock()

    def _evict_expired(self, now: float) -> None:
        self._records = {
            key: value for key, value in self._records.items() if value.expires_at > now
        }

    def put(self, consultation_id: str, record: _Record) -> None:
        with self._lock:
            now = time.monotonic()
            self._evict_expired(now)
            if len(self._records) >= 500:
                oldest = min(self._records, key=lambda key: self._records[key].expires_at)
                del self._records[oldest]
            self._records[consultation_id] = record

    def replace(self, consultation_id: str, expected: _Record, record: _Record) -> None:
        with self._lock:
            self._evict_expired(time.monotonic())
            if self._records.get(consultation_id) is not expected:
                raise ConsultationError(
                    "Previous consultation is no longer available. Start a new consultation."
                )
            self._records[consultation_id] = record

    def get(self, consultation_id: str) -> _Record:
        with self._lock:
            self._evict_expired(time.monotonic())
            record = self._records.get(consultation_id)
            if record is None:
                raise ConsultationError(
                    "Previous consultation is no longer available. Start a new consultation."
                )
            return record


def _profile_hash(request: ConsultationRequest) -> str:
    # Keep the chart binding independent of a display-name edit.
    fields = request.birth_input.model_dump(exclude={"display_name", "place_name"}, mode="json")
    return hashlib.sha256(json.dumps(fields, sort_keys=True).encode()).hexdigest()


def _anchor(result: AskJyotAIResult) -> _Anchor | None:
    if len(result.answers) != 1 or len(result.routing.intents) != 1:
        return None
    return _Anchor(result.routing.intents[0], result.answers[0])


def _active_release() -> tuple[str, ...]:
    timing = get_active_timing_release()
    return (
        ACTIVE_PRODUCTION_RELEASE.manifest.manifest_id,
        ACTIVE_PRODUCTION_RELEASE.manifest.manifest_version,
        ACTIVE_PRODUCTION_RELEASE.fact_contract.methodology_id,
        ACTIVE_PRODUCTION_RELEASE.fact_contract.contract_version,
        timing.release_id,
        timing.release_version,
    )


def _state(
    consultation_id: str, anchor: _Anchor | None, turn_id: str | None = None
) -> ConsultationTurn:
    timing = anchor.answer.timing if anchor else None
    answer = anchor.answer if anchor else None
    claims = answer.claim_ledger.claims if answer and answer.claim_ledger else ()
    release = get_active_timing_release()
    return ConsultationTurn(
        consultation_id=consultation_id,
        turn_id=turn_id or uuid4().hex,
        domain=anchor.intent.domain if anchor else None,
        intent=anchor.intent if anchor else None,
        claim_ids=tuple(claim.claim_id for claim in claims),
        evidence_item_ids=answer.referenced_evidence_item_ids if answer else (),
        timing_references=tuple(
            claim.timing_reference for claim in claims if claim.timing_reference
        ),
        manifest_id=answer.manifest_id
        if answer
        else ACTIVE_PRODUCTION_RELEASE.manifest.manifest_id,
        manifest_version=answer.manifest_version
        if answer
        else ACTIVE_PRODUCTION_RELEASE.manifest.manifest_version,
        methodology_version=(
            f"{ACTIVE_PRODUCTION_RELEASE.fact_contract.methodology_id}:"
            f"{ACTIVE_PRODUCTION_RELEASE.fact_contract.contract_version}"
        ),
        timing_release_id=timing.timing_release_id if timing else release.release_id,
        timing_release_version=timing.timing_release_version if timing else release.release_version,
        limitation=bool(
            answer and (answer.corpus_limitation or (timing and timing.status != "MATCH"))
        ),
    )


class ConsultationService:
    def __init__(self, ask: AskJyotAIService, store: ConsultationStore) -> None:
        self._ask = ask
        self._store = store

    def respond(self, request: ConsultationRequest) -> ConsultationResponse:
        if request.consultation_id is None:
            if (
                request.reference_turn_id
                or request.claim_ids
                or request.evidence_item_ids
                or request.timing_references
            ):
                raise ConsultationError("Evidence references require an active consultation.")
            return self._analyze(request, uuid4().hex)
        record = self._store.get(request.consultation_id)
        if (
            record.profile_hash != _profile_hash(request)
            or record.as_of != request.as_of.isoformat()
        ):
            raise ConsultationError(
                "Previous consultation is no longer available. Start a new consultation."
            )
        if record.release != _active_release():
            raise ConsultationError(
                "Previous consultation is no longer available. Start a new consultation."
            )
        has_references = bool(
            request.claim_ids or request.evidence_item_ids or request.timing_references
        )
        if (has_references or request.reference_turn_id is not None) and (
            request.reference_turn_id != record.anchor_turn_id
        ):
            raise ConsultationError("The supplied evidence reference is no longer current.")
        anchor = record.anchor
        if anchor is None:
            if request.claim_ids or request.evidence_item_ids or request.timing_references:
                raise ConsultationError("This consultation has no approved references to resolve.")
            domains = ", ".join(domain.value for domain in record.domains)
            return ConsultationResponse(
                state=_state(request.consultation_id, None).model_copy(update={"limitation": True}),
                reply=(
                    f"Which earlier domain do you mean ({domains})? "
                    "Ask a specific question about that domain."
                    if domains
                    else "Ask a specific supported domain question before a follow-up."
                ),
                status="clarification",
            )
        state = _state(request.consultation_id, anchor)
        if (
            anchor.answer.manifest_id != ACTIVE_PRODUCTION_RELEASE.manifest.manifest_id
            or anchor.answer.manifest_version != ACTIVE_PRODUCTION_RELEASE.manifest.manifest_version
            or (
                anchor.answer.timing is not None
                and (
                    anchor.answer.timing.timing_release_id != get_active_timing_release().release_id
                    or anchor.answer.timing.timing_release_version
                    != get_active_timing_release().release_version
                )
            )
        ):
            raise ConsultationError(
                "The approved evidence release changed. Start a new consultation."
            )
        if (
            not set(request.claim_ids) <= set(state.claim_ids)
            or not set(request.evidence_item_ids) <= set(state.evidence_item_ids)
            or not set(request.timing_references) <= set(state.timing_references)
        ):
            raise ConsultationError(
                "The supplied claim or evidence reference is not in this consultation."
            )
        question = " ".join(request.question.lower().split())
        years = tuple(
            dict.fromkeys(int(year) for year in re.findall(r"\b(?:19|20)\d{2}\b", question))
        )
        previous_year = (
            anchor.intent.time_range.start_date.year
            if anchor.intent.time_range
            and anchor.intent.time_range.start_date.year == anchor.intent.time_range.end_date.year
            else None
        )
        comparison = bool(re.search(r"\b(compare|better|versus|vs\.?|worse)\b", question))
        if comparison:
            if anchor.intent.domain is not QuestionDomain.CAREER:
                return self._reply(
                    request.consultation_id,
                    anchor,
                    "No approved comparison method is active for this domain.",
                    "unsupported",
                )
            if len(years) == 1 and previous_year is not None:
                years = (previous_year, years[0])
            if len(set(years)) < 2:
                return self._reply(
                    request.consultation_id,
                    anchor,
                    "Which two years would you like to compare?",
                    "clarification",
                )
            return self._compare(request, anchor, years[:2])
        if (
            re.fullmatch(r"(?:and )?what about (?:in )?(?:19|20)\d{2}\??", question)
            and len(years) == 1
        ):
            domain = anchor.intent.domain.value
            return self._analyze(
                request.model_copy(update={"question": f"What about {domain} in {years[0]}?"}),
                request.consultation_id,
                record,
            )
        if years and (previous_year is None or any(year != previous_year for year in years)):
            return self._reply(
                request.consultation_id,
                anchor,
                "Which earlier claim and year do you mean?",
                "clarification",
            )
        return self._explain(request, anchor)

    def _compare(
        self, request: ConsultationRequest, anchor: _Anchor, years: tuple[int, ...]
    ) -> ConsultationResponse:
        """Show two independently evaluated timing facts without a relative judgment."""
        years = tuple(sorted(years))
        periods: list[str] = []
        for year in years:
            analysis = self._ask.answer(
                DeterministicAnalysisRequest(
                    birth_input=request.birth_input,
                    as_of=request.as_of,
                    question=f"How is my career in {year}?",
                )
            )
            timing = analysis.answers[0].timing if analysis.answers else None
            if timing is None:
                periods.append(f"{year}: Career timing was not evaluated.")
            elif not timing.windows:
                periods.append(f"{year}: {timing.status} — {timing.message}")
            else:
                for window in timing.windows:
                    lords = (
                        f"{window.mahadasha_lord.title()} Mahadasha"
                        if window.mahadasha_lord
                        else window.source.dasha_scope
                    )
                    if window.antardasha_lord:
                        lords += f", {window.antardasha_lord.title()} Antardasha"
                    periods.append(
                        f"{year}: {lords}; {window.effective_start.isoformat()} to "
                        f"{window.effective_end.isoformat()} (end exclusive); "
                        f"{window.precision}; rule {window.rule_id}; "
                        f"source {window.source.source_work}, {window.source.section}, "
                        f"verse {window.source.verse}."
                    )
        return self._reply(
            request.consultation_id or "",
            anchor,
            f"I cannot rank Career outcomes for {years[0]} and {years[1]}. "
            "No approved two-period comparison methodology is active. "
            "Separately evaluated governed timing context: "
            + " ".join(periods)
            + " These periods do not establish events or relative outcomes.",
            "unsupported",
        )

    def _analyze(
        self,
        request: ConsultationRequest,
        consultation_id: str,
        previous: _Record | None = None,
    ) -> ConsultationResponse:
        result = self._ask.answer(
            DeterministicAnalysisRequest.model_validate(
                request.model_dump(include={"birth_input", "as_of", "question"})
            )
        )
        anchor = _anchor(result)
        anchor_turn_id = uuid4().hex
        record = _Record(
            _profile_hash(request),
            request.as_of.isoformat(),
            anchor,
            anchor_turn_id,
            tuple(intent.domain for intent in result.routing.intents),
            _active_release(),
            time.monotonic() + 1800,
        )
        if anchor and len(anchor.answer.model_dump_json()) > 131_072:
            raise ConsultationError(
                "Consultation state exceeds the available limit. Start a new consultation."
            )
        if previous is None:
            self._store.put(consultation_id, record)
        else:
            self._store.replace(consultation_id, previous, record)
        return ConsultationResponse(
            state=_state(consultation_id, anchor, anchor_turn_id), analysis=result
        )

    def _reply(
        self,
        consultation_id: str,
        anchor: _Anchor,
        reply: str,
        status: Literal["answered", "clarification", "unsupported"] = "answered",
        claims: tuple[CareerClaim, ...] = (),
    ) -> ConsultationResponse:
        state = _state(consultation_id, anchor)
        return ConsultationResponse(
            state=state.model_copy(update={"limitation": status != "answered" or state.limitation}),
            reply=reply,
            status=status,
            source_references=tuple(
                dict.fromkeys(
                    claim.source_reference
                    for claim in claims
                    if claim.kind
                    in {
                        ClaimKind.APPROVED_INTERPRETATION,
                        ClaimKind.APPROVED_TIMING_INTERPRETATION,
                    }
                )
            ),
            resolved_claim_ids=tuple(claim.claim_id for claim in claims),
            resolved_evidence_item_ids=tuple(
                dict.fromkeys(
                    evidence_id for claim in claims for evidence_id in claim.evidence_item_ids
                )
            ),
            resolved_timing_references=tuple(
                claim.timing_reference for claim in claims if claim.timing_reference
            ),
        )

    def _explain(self, request: ConsultationRequest, anchor: _Anchor) -> ConsultationResponse:
        question = request.question.lower()
        answer = anchor.answer
        ledger = answer.claim_ledger
        claims = ledger.claims if ledger else ()
        if not claims:
            if re.search(r"\b(dasha|antardasha|period|timing)\b", question):
                return self._reply(
                    request.consultation_id or "",
                    anchor,
                    "No approved timing evidence is available for this domain. "
                    "A Dasha cannot be interpreted for that request.",
                    "unsupported",
                )
            return self._reply(
                request.consultation_id or "",
                anchor,
                "The prior answer has no Career claim ledger to resolve. "
                "Ask a specific supported domain question.",
                "unsupported",
            )
        timing = answer.timing
        if re.search(r"\b(dasha|antardasha|period)\b", question):
            chosen = tuple(
                claim for claim in claims if claim.kind is ClaimKind.APPROVED_TIMING_INTERPRETATION
            )
            if request.timing_references:
                chosen = tuple(
                    claim for claim in chosen if claim.timing_reference in request.timing_references
                )
            if timing is None or not chosen:
                return self._reply(
                    request.consultation_id or "",
                    anchor,
                    timing.message
                    if timing
                    else "No approved timing evidence was established for that answer.",
                    "unsupported",
                )
            if len(chosen) != 1:
                return self._reply(
                    request.consultation_id or "",
                    anchor,
                    "Which displayed timing window do you mean?",
                    "clarification",
                )
            claim = chosen[0]
            window = next(
                (
                    item
                    for item in timing.windows
                    if f"[{item.effective_start.isoformat()},{item.effective_end.isoformat()})"
                    == claim.timing_reference
                ),
                None,
            )
            if window is None:
                raise ConsultationError(
                    "The timing reference no longer matches its approved window."
                )
            if window.mahadasha_lord is None:
                return self._reply(
                    request.consultation_id or "",
                    anchor,
                    "The approved window does not supply a calculated Mahadasha lord.",
                    "unsupported",
                )
            dasha_label = f"{window.mahadasha_lord.title()} Mahadasha"
            if window.antardasha_lord:
                dasha_label += f", {window.antardasha_lord.title()} Antardasha"
            return self._reply(
                request.consultation_id or "",
                anchor,
                (
                    f"Calculated period: {window.source.dasha_scope} ({dasha_label}), "
                    f"{window.source_start.isoformat()} to {window.source_end.isoformat()} "
                    "(end exclusive). The requested-date intersection is "
                    f"{window.effective_start.isoformat()} to {window.effective_end.isoformat()} "
                    f"(end exclusive). Approved interpretation: {window.reviewed_statement} "
                    f"Condition: {window.why_this_period_applies} Precision: {window.precision}. "
                    "This does not establish an event or exact date."
                ),
                claims=(claim,),
            )
        if re.search(
            r"\b(not establish|doesn't establish|cannot establish|limit|unsupported)\b", question
        ):
            limits = list(answer.limitations)
            if timing:
                limits.extend(item for window in timing.windows for item in window.limitations)
            limits.extend(
                claim.missing_evidence[0]
                for claim in claims
                if claim.kind is ClaimKind.UNSUPPORTED_REQUEST and claim.missing_evidence
            )
            return self._reply(
                request.consultation_id or "",
                anchor,
                "This interpretation does not establish: " + "; ".join(dict.fromkeys(limits))
                if limits
                else "The available evidence does not establish an exact outcome or event date.",
            )
        if re.search(r"\b(placement|planetary)\b", question):
            chosen = tuple(claim for claim in claims if claim.kind is ClaimKind.CALCULATED_FACT)
            interpreted = tuple(
                claim for claim in claims if claim.kind is ClaimKind.APPROVED_INTERPRETATION
            )
            if len(chosen) != 1 or len(interpreted) != 1:
                return self._reply(
                    request.consultation_id or "",
                    anchor,
                    "Which Career placement claim do you mean?",
                    "clarification",
                )
            fact, interpretation = chosen[0], interpreted[0]
            if not set(fact.evidence_item_ids) & set(interpretation.evidence_item_ids):
                raise ConsultationError("The placement claim is not linked to that interpretation.")
            return self._reply(
                request.consultation_id or "",
                anchor,
                (
                    f"Calculated placement: {fact.permitted_wording} "
                    f"Approved rule: {interpretation.rule_ids[0]}. "
                    f"The reviewed source permits: {interpretation.permitted_wording} "
                    "The placement matched that rule's required chart fact. "
                    "It does not establish a profession, promotion, or event date."
                ),
                claims=(fact, interpretation),
            )
        if re.search(r"\b(why|explain|detail|more)\b", question):
            if anchor.intent.requires_timing and timing and timing.status != "MATCH":
                return self._reply(
                    request.consultation_id or "", anchor, timing.message, "unsupported"
                )
            mentioned_ids = tuple(
                claim.claim_id
                for claim in claims
                if re.search(rf"(?<![\w.-]){re.escape(claim.claim_id)}(?![\w.-])", question)
            )
            explicit_ids = request.claim_ids or mentioned_ids
            approved = tuple(
                claim
                for claim in claims
                if claim.kind
                in {ClaimKind.APPROVED_INTERPRETATION, ClaimKind.APPROVED_TIMING_INTERPRETATION}
            )
            if explicit_ids:
                chosen = tuple(claim for claim in claims if claim.claim_id in explicit_ids)
            elif anchor.intent.requires_timing and re.search(r"\b(?:19|20)\d{2}\b", question):
                chosen = tuple(
                    claim
                    for claim in approved
                    if claim.kind is ClaimKind.APPROVED_TIMING_INTERPRETATION
                )
            else:
                chosen = approved
            if len(chosen) != 1:
                options = ", ".join(claim.claim_id for claim in chosen[:4])
                return self._reply(
                    request.consultation_id or "",
                    anchor,
                    "Which approved claim do you mean? "
                    + (
                        f"Choose a displayed claim ID: {options}."
                        if options
                        else "Please choose a displayed evidence reference."
                    ),
                    "clarification",
                )
            claim = chosen[0]
            if claim.kind is ClaimKind.CALCULATED_FACT:
                return self._reply(
                    request.consultation_id or "",
                    anchor,
                    f"Calculated placement: {claim.permitted_wording} "
                    "This fact alone does not establish an outcome or event date.",
                    claims=(claim,),
                )
            if claim.kind in {ClaimKind.UNSUPPORTED_REQUEST, ClaimKind.INSUFFICIENT_EVIDENCE}:
                return self._reply(
                    request.consultation_id or "",
                    anchor,
                    claim.permitted_wording
                    + (
                        " Missing: " + ", ".join(claim.missing_evidence)
                        if claim.missing_evidence
                        else ""
                    ),
                    "unsupported",
                    (claim,),
                )
            if claim.kind is ClaimKind.APPROVED_TIMING_INTERPRETATION and timing:
                matched_window = next(
                    (
                        item
                        for item in timing.windows
                        if f"[{item.effective_start.isoformat()},{item.effective_end.isoformat()})"
                        == claim.timing_reference
                    ),
                    None,
                )
                if matched_window is None:
                    raise ConsultationError(
                        "The timing reference no longer matches its approved window."
                    )
                reply = (
                    f"{claim.permitted_wording} The condition matched because "
                    f"{matched_window.why_this_period_applies} The authorized intersection is "
                    f"{matched_window.effective_start.isoformat()} to "
                    f"{matched_window.effective_end.isoformat()} (end exclusive); "
                    f"the complete source period is {matched_window.source_start.isoformat()} "
                    f"to {matched_window.source_end.isoformat()} (end exclusive). "
                    f"Precision: {matched_window.precision}. "
                    "This does not establish an event date or promotion."
                )
            else:
                matched_fact = next(
                    (
                        item
                        for item in claims
                        if item.kind is ClaimKind.CALCULATED_FACT
                        and set(item.evidence_item_ids) & set(claim.evidence_item_ids)
                    ),
                    None,
                )
                placement = (
                    f"Calculated placement: {matched_fact.permitted_wording} "
                    if matched_fact
                    else ""
                )
                if not placement:
                    display_placement = next(
                        (
                            item.placement_explanation
                            for evidence_id, item in zip(
                                answer.referenced_evidence_item_ids, answer.evidence, strict=True
                            )
                            if evidence_id in claim.evidence_item_ids
                        ),
                        None,
                    )
                    if display_placement:
                        placement = f"Calculated placement: {display_placement} "
                reply = (
                    f"{placement}Approved rule: {claim.rule_ids[0]}. "
                    f"The reviewed source permits: {claim.permitted_wording} "
                    "This matched the rule's required chart fact. "
                    "It does not establish a profession, promotion, or event date."
                )
            return self._reply(request.consultation_id or "", anchor, reply, claims=(claim,))
        return self._reply(
            request.consultation_id or "",
            anchor,
            "Please ask which placement, Dasha, limitation, or approved claim you want explained.",
            "clarification",
        )
