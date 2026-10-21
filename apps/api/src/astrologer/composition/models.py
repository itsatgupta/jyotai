"""Typed contracts for the narrow LLM composition boundary.

These models deliberately contain no chart, birth, ephemeris, fact values, or
source text.  A transport implementation receives only ``CompositionProviderRequest``.
"""

from datetime import date, datetime
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field


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
    timing_answered: Literal[False] = False
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
    scope: Literal["requested_range", "default_40_year_horizon", "historical_unbounded"] = (
        "default_40_year_horizon"
    )
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


class DetailedComposedAnswer(ComposedAnswer):
    """Ask-only deterministic explanation; dashboard keeps ``ComposedAnswer`` concise."""

    why_it_applies: tuple[str, ...] = ()
    reviewed_interpretations: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    evidence: tuple[DetailedEvidence, ...] = ()
    narrative: SeniorAstrologerNarrative | None = None
    timing: CareerTimingContext | None = None
