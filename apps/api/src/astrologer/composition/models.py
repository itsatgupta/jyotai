"""Typed contracts for the narrow LLM composition boundary.

These models deliberately contain no chart, birth, ephemeris, fact values, or
source text.  A transport implementation receives only ``CompositionProviderRequest``.
"""

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
