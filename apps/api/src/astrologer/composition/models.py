"""Typed contracts for the narrow LLM composition boundary.

These models deliberately contain no chart, birth, ephemeris, fact values, or
source text.  A transport implementation receives only ``CompositionProviderRequest``.
"""

from datetime import date, datetime
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

from astrologer.astrology.dasha_linkage import DashaPairLinkage
from astrologer.composition.career_claims import CareerClaimLedger
from astrologer.questions.models import QuestionIntent, ResolvedTimeRange


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class AnswerCompositionPolicy(_FrozenModel):
    """Versioned, non-overridable rules for composing governed evidence."""

    policy_id: Literal["governed-answer-composition"] = "governed-answer-composition"
    policy_version: Literal["v1"] = "v1"
    prompt_version: Literal["governed-answer-composition-prompt-v1"] = (
        "governed-answer-composition-prompt-v1"
    )
    require_evidence_references: Literal[True] = True
    prohibit_timing_without_answerability: Literal[True] = True

    def system_instructions(self, *, static_context_only: bool = False) -> str:
        """Return the complete fixed instruction set; callers cannot weaken it."""
        instructions: tuple[str, ...] = (
            "You are JyotAI's constrained language composer.",
            "Explain only the supplied governed evidence. Do not calculate astrology.",
            "Do not add or infer Jyotish doctrine, chart facts, houses, signs, aspects, ",
            "yogas, dashas, transits, strengths, dignities, outcomes, or timing.",
            "A TRUE item may be described only through its reviewed_statement and scope_notes.",
            "A FALSE item means that its governed rule did not match; it is not opposite evidence.",
            "An UNKNOWN item is unresolved; do not treat it as FALSE or repair it.",
            "Do not turn absent evidence into a negative astrological conclusion.",
            "Keep the supplied domain boundary. Do not mention excluded domains.",
            "timing_answerability_established is authoritative. When false, do not give a ",
            "date, period, forecast window, or answer to when; state that timing is "
            "not established.",
            "Do not present astrology as scientific certainty or guarantee health, legal, "
            "or financial outcomes.",
            "Return exactly one JSON object with only answer and timing_answered. Do not return "
            "evidence IDs, rule IDs, corpus_limitation, or any other control fields.",
            "The application, not you, attaches deterministic supporting evidence IDs and "
            "corpus limitation status.",
            "timing_answered must be false unless timing answerability is explicitly true.",
        )
        if static_context_only:
            instructions += (
                "This request is timing-unavailable. Explain static/contextual governed "
                "evidence only; do not attempt to answer the user's timing question.",
            )
        return "\n".join(instructions)


DEFAULT_COMPOSITION_POLICY = AnswerCompositionPolicy()


class CompositionProviderRequest(_FrozenModel):
    """The complete and only payload an LLM transport is allowed to receive."""

    system_instructions: str = Field(min_length=1)
    user_payload_json: str = Field(min_length=1)


class CompositionProviderResponse(_FrozenModel):
    """Raw structured text plus auditable provider/model identifiers."""

    output_json: str = Field(min_length=1)
    provider_id: str = Field(min_length=1, max_length=128)
    model_id: str = Field(min_length=1, max_length=256)


class LanguageModelTransport(Protocol):
    """Provider adapter seam; implementations must not receive domain objects."""

    def complete(self, request: CompositionProviderRequest) -> CompositionProviderResponse:
        """Return one JSON-only model completion."""


class ComposedAnswer(_FrozenModel):
    """Validated language output tied to one immutable evidence contract and policy."""

    answer: str = Field(min_length=1, max_length=8000)
    referenced_evidence_item_ids: tuple[str, ...] = ()
    timing_answered: bool = False
    corpus_limitation: bool
    policy_id: str
    policy_version: str
    prompt_version: str
    interpretation_contract_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    manifest_id: str
    manifest_version: str
    manifest_content_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    provider_id: str
    model_id: str


class DetailedEvidence(_FrozenModel):
    """A renderer-safe, deterministic explanation of one selected rule."""

    placement_explanation: str
    reviewed_statement: str
    question_framing: str
    source_work: str
    source_section: str
    source_reference: str | None = None
    chart_scope: Literal["D1/Rashi"] = "D1/Rashi"
    posture: Literal["static/contextual"] = "static/contextual"
    domain: str
    # NEXT-ADMIT-02: reviewer weight (display order only, never a score) and the lord's sign
    # dignity as a calculated fact (a modifier only; it never changes the rule's result).
    weight: Literal["primary", "secondary"] = "primary"
    lord_dignity: str | None = None


class SeniorAstrologerNarrative(_FrozenModel):
    """Validated prose that augments, but never replaces, detailed evidence."""

    summary: str = Field(min_length=1, max_length=1600)
    explanation: str = Field(min_length=1, max_length=5000)
    question_relevance: str = Field(min_length=1, max_length=1600)
    follow_up: str | None = Field(default=None, max_length=600)


class CareerTimingWindowDisplay(_FrozenModel):
    """Application-owned governed timing window; never generated by the language model."""

    rule_id: str
    precision: Literal["BROAD_PERIOD", "SUB_PERIOD"]
    source_start: datetime
    source_end: datetime
    effective_start: datetime
    effective_end: datetime
    mahadasha_lord: str | None = None
    antardasha_lord: str | None = None
    why_this_period_applies: str
    reviewed_statement: str
    limitations: tuple[str, ...]
    source: "CareerTimingProvenance"


class CareerTimingProvenance(_FrozenModel):
    """User-safe source context for one governed timing window."""

    source_work: str
    section: str
    verse: str
    chart_scope: Literal["D1/Rashi"]
    dasha_scope: str
    precision: Literal["BROAD_PERIOD", "SUB_PERIOD"]


class CareerTimingContext(_FrozenModel):
    """Separate Ask display contract for the governed production Career timing release."""

    domain: Literal["career"] = "career"
    timing_answerability_established: bool
    status: Literal["MATCH", "NO_MATCH", "UNKNOWN", "UNSUPPORTED"]
    scope: Literal[
        "requested_range",
        "default_40_year_horizon",
        "historical_unbounded",
        "precision_unsupported",
    ] = "default_40_year_horizon"
    requested_start_date: date | None = None
    requested_end_date: date | None = None
    calendar_timezone_offset: str | None = None
    evaluated_start: datetime | None = None
    evaluated_end: datetime | None = None
    partially_supported: bool = False
    timing_release_id: str
    timing_release_version: str
    windows: tuple[CareerTimingWindowDisplay, ...] = ()
    message: str
    # Deprecated v1 fields retained only for one-rule responses so existing clients remain safe.
    # Mixed windows must use their mandatory per-window fields instead.
    precision: Literal["BROAD_PERIOD", "SUB_PERIOD"] | None = None
    reviewed_statement: str | None = None
    why_this_period_applies: str | None = None
    limitations: tuple[str, ...] = ()


class PlannedDashaSegment(_FrozenModel):
    """Calculated chronology intersecting the requested local calendar year."""

    segment_id: str
    mahadasha_lord: str
    antardasha_lord: str
    mahadasha_start: datetime
    mahadasha_end: datetime
    antardasha_start: datetime
    antardasha_end: datetime
    effective_start: datetime
    effective_end: datetime
    local_start: datetime
    local_end: datetime


class D1FactReference(_FrozenModel):
    """The value of one existing D1 derived fact, cited by its fact id (not a new fact)."""

    fact_id: str = Field(min_length=1)
    value: str = Field(min_length=1)


class DashaSegmentLinkage(_FrozenModel):
    """Deterministic chart-linkage facts for the lords of one planned Dasha segment."""

    segment_id: str
    linkage: DashaPairLinkage
    # The existing ``jyotish.d1.house.10.lord`` fact, so prose can name the 10th lord.
    tenth_lord: D1FactReference | None = None


class DashaInterpretationClaim(_FrozenModel):
    """One admitted Dasha interpretation rule that matched one planned segment."""

    rule_id: str
    rule_version: str
    source_locator: str = Field(min_length=1)
    permitted_wording: str = Field(min_length=1)
    segment_id: str
    mahadasha_lord: str
    antardasha_lord: str
    matched_fact_ids: tuple[str, ...]


class DashaInterpretationSlot(_FrozenModel):
    """Review-gated slot; only rules admitted to the Dasha corpus release can fill it."""

    corpus_manifest_id: str
    corpus_manifest_version: str
    claims: tuple[DashaInterpretationClaim, ...] = ()


class DashaContextSentence(_FrozenModel):
    """One rendered sentence and the linkage fact ids it was generated from."""

    text: str = Field(min_length=1)
    fact_ids: tuple[str, ...] = Field(min_length=1)


SynthesisLinkType = Literal["SAME_PLANET", "SAME_HOUSE", "SAME_PERIOD"]


class SynthesisLink(_FrozenModel):
    """One deterministic co-reference between a reviewed Career claim and a Dasha period.

    The link states only the shared reference (a planet, a house, or a time interval).  It
    carries no polarity, weight, or causal meaning.  ``dasha_rule_ids`` lists admitted Dasha
    interpretation rules for the period and is empty when none exist.  ``calc_method_ids``
    names the calculation methodology that produced the Dasha-side facts; a calculation
    method is provenance, never a rule, so it never appears in ``dasha_rule_ids``.

    ``claim_label`` and ``claim_subject`` are plain-language display labels (no ids);
    ``period_span`` is the period's local date span and ``period_covers_year`` records whether
    that period spans the whole asked year.
    """

    link_type: SynthesisLinkType
    claim_id: str = Field(min_length=1)
    claim_label: str = Field(min_length=1)
    claim_subject: str | None = None
    claim_fact_ids: tuple[str, ...] = Field(min_length=1)
    claim_rule_ids: tuple[str, ...] = Field(min_length=1)
    dasha_fact_ids: tuple[str, ...] = Field(min_length=1)
    dasha_rule_ids: tuple[str, ...] = ()
    calc_method_ids: tuple[str, ...] = Field(min_length=1)
    segment_ids: tuple[str, ...] = Field(min_length=1)
    period_role: Literal["Mahadasha", "Antardasha"] | None = None
    period_lord: str | None = None
    period_span: str | None = None
    period_covers_year: bool = False
    shared_reference: str = Field(min_length=1)
    text: str = Field(min_length=1)


class SynthesisSentence(_FrozenModel):
    """One rendered sentence and every id it was generated from (sentence-to-fact mapping)."""

    text: str = Field(min_length=1)
    claim_ids: tuple[str, ...] = ()
    fact_ids: tuple[str, ...] = ()
    rule_ids: tuple[str, ...] = ()
    calc_method_ids: tuple[str, ...] = ()


class CareerSynthesis(_FrozenModel):
    """Structural co-references between reviewed Career claims and the asked year's Dasha.

    ``year_spanning_claim_ids`` lists reviewed timing claims whose window covers every
    planned Dasha segment of the asked year.  ``withheld_claim_ids`` lists matched reviewed
    claims whose wording is paused or withheld (v.72 7th house, v.76): they are never linked.
    """

    synthesis_version: Literal["career-synthesis-v1"] = "career-synthesis-v1"
    year: int
    reviewed_claim_ids: tuple[str, ...] = ()
    withheld_claim_ids: tuple[str, ...] = ()
    links: tuple[SynthesisLink, ...] = ()
    year_spanning_claim_ids: tuple[str, ...] = ()
    out_of_scope: tuple[str, ...] = ()

    @property
    def co_referenced_claim_ids(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(link.claim_id for link in self.links))


class CareerAnswerPlan(_FrozenModel):
    """Application-selected evidence and limits, before any prose is composed."""

    plan_version: Literal["career-answer-plan-v1"] = "career-answer-plan-v1"
    question_intent: QuestionIntent
    requested_time_scope: ResolvedTimeRange | None = None
    calculated_fact_ids: tuple[str, ...] = ()
    matched_claim_ids: tuple[str, ...] = ()
    timing_evidence_ids: tuple[str, ...] = ()
    timing_references: tuple[str, ...] = ()
    dasha_segments: tuple[PlannedDashaSegment, ...] = ()
    approved_source_locators: tuple[str, ...] = ()
    limitation_ids: tuple[str, ...] = ()
    answerability: Literal[
        "REVIEWED_TIMING_CONTEXT", "NATAL_CONTEXT_ONLY", "FACTS_ONLY", "UNKNOWN", "UNSUPPORTED"
    ]
    dasha_linkages: tuple[DashaSegmentLinkage, ...] = ()
    dasha_interpretation: DashaInterpretationSlot | None = None
    synthesis: CareerSynthesis | None = None
    # Existing D1 facts naming the 10th lord and its placement house (no meaning attached).
    tenth_lord_facts: tuple[D1FactReference, ...] = ()
    # NEXT-ADMIT-02 (X2): the 10th lord's sign dignity as a calculated fact, shown next to the
    # natal rule as a modifier only; it never changes a rule's result.
    tenth_lord_dignity: str | None = None
    tenth_lord_dignity_fact_ids: tuple[str, ...] = ()
    # NEXT-SIG-01: the signification corpus consulted ("<manifest_id>@<version>") and the
    # "Period themes" sentences it produced; empty unless 0b entries AND X18 are admitted.
    signification_corpus_version: str | None = None
    period_themes: tuple[SynthesisSentence, ...] = ()
    # NEXT-ADMIT-01: the one glance bullet summarising the Period-themes terms (None if none).
    period_themes_glance: SynthesisSentence | None = None


class ConsultationSection(_FrozenModel):
    """Deterministic, renderer-ready prose composed from a validated answer plan.

    A ``dasha_context`` section also carries its sentence -> fact-id mapping, the fixed
    framing line, and the ids of any admitted interpretation rules it quotes.  A ``glance``
    section (year answers) carries one ``synthesis_sentences`` entry per bullet.
    """

    kind: Literal[
        "direct",
        "glance",
        "why",
        "period_themes",
        "natal",
        "dasha",
        "dasha_context",
        "timing",
        "limit",
    ]
    text: str = Field(min_length=1)
    fact_sentences: tuple[DashaContextSentence, ...] = ()
    framing: str | None = None
    interpretation_rule_ids: tuple[str, ...] = ()
    synthesis_links: tuple[SynthesisLink, ...] = ()
    synthesis_sentences: tuple[SynthesisSentence, ...] = ()


ComparisonSentenceBasis = Literal["fact", "rule", "fixed"]


class ComparisonSentence(_FrozenModel):
    """One rendered comparison sentence and what backs it.

    ``fact``: built only from calculated facts (``fact_ids`` non-empty).
    ``rule``: admitted rule text quoted verbatim, or a plain label of an admitted rule
    (``rule_ids`` non-empty).  ``fixed``: one of the fixed comparison-view texts.
    """

    text: str = Field(min_length=1)
    basis: ComparisonSentenceBasis
    claim_ids: tuple[str, ...] = ()
    fact_ids: tuple[str, ...] = ()
    rule_ids: tuple[str, ...] = ()
    calc_method_ids: tuple[str, ...] = ()


class ComparisonTimingIndication(_FrozenModel):
    """One reviewed timing indication that applies in a year, quoted verbatim."""

    claim_id: str
    rule_id: str
    label: str
    reviewed_statement: str
    source_reference: str
    precision: Literal["BROAD_PERIOD", "SUB_PERIOD"]
    local_span: str


class CareerYearColumn(_FrozenModel):
    """One independently evaluated calendar year; never combined with the other column."""

    year: int
    dasha_segments: tuple[PlannedDashaSegment, ...] = ()
    periods: tuple[ComparisonSentence, ...] = ()
    lord_facts: tuple[ComparisonSentence, ...] = ()
    timing_status: Literal["MATCH", "NO_MATCH", "UNKNOWN", "UNSUPPORTED", "NOT_EVALUATED"]
    timing_indications: tuple[ComparisonTimingIndication, ...] = ()
    timing: tuple[ComparisonSentence, ...] = ()
    co_references: tuple[ComparisonSentence, ...] = ()
    dasha_interpretation: ComparisonSentence
    # Per-column provenance, as for a single-year answer.
    manifest_id: str
    manifest_version: str
    methodology_version: str
    timing_release_id: str
    timing_release_version: str
    synthesis_version: str | None = None
    answer_plan_version: str | None = None


class CareerYearComparison(_FrozenModel):
    """A factual side-by-side of two calendar years (``comparison-view-v1``).

    It has no ranking, score, or verdict field by design.  ``ranking_status`` is always
    ``unsupported`` while no reviewed comparison method exists.
    """

    view_version: Literal["comparison-view-v1"] = "comparison-view-v1"
    comparison_mode: Literal["SIDE_BY_SIDE"] = "SIDE_BY_SIDE"
    ranking_status: Literal["unsupported"] = "unsupported"
    unit: Literal["calendar_year"] = "calendar_year"
    years: tuple[int, int]
    direct: tuple[ComparisonSentence, ...] = Field(min_length=1)
    differences: tuple[ComparisonSentence, ...] = Field(min_length=1)
    natal_shared: tuple[ComparisonSentence, ...] = Field(min_length=1)
    columns: tuple[CareerYearColumn, CareerYearColumn]
    why_no_ranking: tuple[ComparisonSentence, ...] = Field(min_length=1)
    limitations: tuple[ComparisonSentence, ...] = Field(min_length=1)

    def sentences(self) -> tuple[ComparisonSentence, ...]:
        """Every rendered sentence, in display order."""
        column_sentences = tuple(
            sentence
            for column in self.columns
            for sentence in (
                *column.periods,
                *column.lord_facts,
                *column.timing,
                *column.co_references,
                column.dasha_interpretation,
            )
        )
        return (
            *self.direct,
            *self.differences,
            *self.natal_shared,
            *column_sentences,
            *self.why_no_ranking,
            *self.limitations,
        )

    def text(self) -> str:
        """Plain text in display order: direct, differences, natal, columns, why, limits."""
        return " ".join(sentence.text for sentence in self.sentences())


ReviewTypeLabel = Literal[
    "Independent reviewer (Pandit ji, Acharya)",
    "Project-owner review (not independently certified)",
    "Project interpretive convention, reviewer-approved; no source verse identified",
]


class RuleReviewType(_FrozenModel):
    """The review type of one cited rule, from its existing record (evidence disclosure only)."""

    rule_id: str
    review_type: ReviewTypeLabel


# NEXT-MARRIAGE-01: the badge names the author's own confidence in the reading.
ProvisionalBadge = Literal[
    "Provisional · high confidence",
    "Provisional · medium confidence",
    "Provisional · low confidence",
]


class ProvisionalJustificationView(_FrozenModel):
    """The full justification of a provisional rule, for its evidence disclosure."""

    source_work: str
    locator: str
    original_text: str
    draft_translation: str
    interpretive_reasoning: str
    conventions: tuple[str, ...]
    confidence: Literal["high", "medium", "low"]
    author: Literal[
        "project owner, provisional",
        "drafted_by: AI agent; adopted_by: project owner (pending)",
    ]
    status: Literal["provisional"]
    transcription_notes: str | None = None


class ProvisionalInterpretation(_FrozenModel):
    """NEXT-PROVISIONAL-01: one matched provisional rule, shown only on request.

    Never part of the reviewed answer text, the claim ledger, the evidence package or
    ``rule_review_types``; always rendered with ``badge``.
    """

    rule_id: str
    rule_version: str
    tier: Literal["provisional"] = "provisional"
    badge: ProvisionalBadge
    domain: str
    placement_explanation: str
    statement: str
    fact_ids: tuple[str, ...]
    corpus_release: str
    justification: ProvisionalJustificationView


class DetailedComposedAnswer(ComposedAnswer):
    """Ask-only deterministic explanation; dashboard keeps ``ComposedAnswer`` concise."""

    why_it_applies: tuple[str, ...] = ()
    reviewed_interpretations: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    evidence: tuple[DetailedEvidence, ...] = ()
    narrative: SeniorAstrologerNarrative | None = None
    timing: CareerTimingContext | None = None
    claim_ledger: CareerClaimLedger | None = None
    career_answer_plan: CareerAnswerPlan | None = None
    consultation_sections: tuple[ConsultationSection, ...] = ()
    career_comparison: CareerYearComparison | None = None
    # NEXT-THEMES-01: review type per cited rule; shown only in the evidence disclosure.
    rule_review_types: tuple[RuleReviewType, ...] = ()
    # NEXT-PROVISIONAL-01: present only when the request sets ``include_provisional``.
    provisional_interpretations: tuple[ProvisionalInterpretation, ...] = ()
