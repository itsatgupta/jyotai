"""Constrained, provider-neutral language composition over governed evidence."""

from astrologer.composition.composer import (
    AnswerComposer,
    AnswerCompositionError,
    DeterministicAnswerComposer,
)
from astrologer.composition.models import (
    DEFAULT_COMPOSITION_POLICY,
    AnswerCompositionPolicy,
    ComposedAnswer,
    CompositionProviderRequest,
    CompositionProviderResponse,
    DetailedComposedAnswer,
    DetailedEvidence,
    LanguageModelTransport,
    SeniorAstrologerNarrative,
)
from astrologer.composition.openai_compatible import (
    LanguageModelTransportError,
    OpenAICompatibleTransport,
)
from astrologer.composition.senior_composer import SeniorAstrologerComposer

__all__ = [
    "AnswerComposer",
    "AnswerCompositionError",
    "DeterministicAnswerComposer",
    "LanguageModelTransportError",
    "OpenAICompatibleTransport",
    "AnswerCompositionPolicy",
    "ComposedAnswer",
    "DetailedComposedAnswer",
    "DetailedEvidence",
    "CompositionProviderRequest",
    "CompositionProviderResponse",
    "DEFAULT_COMPOSITION_POLICY",
    "LanguageModelTransport",
    "SeniorAstrologerComposer",
    "SeniorAstrologerNarrative",
]
