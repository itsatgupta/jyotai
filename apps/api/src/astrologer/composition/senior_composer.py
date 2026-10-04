"""Fail-closed senior-astrologer narrative composition over detailed evidence."""

import json
import re

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from astrologer.composition.composer import AnswerCompositionError
from astrologer.composition.models import (
    CompositionProviderRequest,
    DetailedComposedAnswer,
    LanguageModelTransport,
    SeniorAstrologerNarrative,
)
from astrologer.evidence import InterpretationEvidence

_TIMING = "Timing is not established by the current governed evidence."
_BANNED = re.compile(
    r"\b(?:aspect(?:s|ed|ing)?|conjunction|conjunct|exalt(?:ed|ation)?|debilitat(?:ed|ion)?|"
    r"retrograde|combust(?:ion|ed)?|yoga|dosha|nakshatra|mahadasha|antardasha|dasha|"
    r"transit(?:s|ing)?|remed(?:y|ies)|gemstone(?:s)?|mantra(?:s)?|ritual(?:s)?|"
    r"guarantee(?:d)?|certain(?:ty)?|definitely|probability|percentage|percent)\b",
    re.I,
)
_PLANETS = re.compile(r"\b(?:sun|moon|mars|mercury|jupiter|venus|saturn|rahu|ketu)\b", re.I)
_HOUSE = re.compile(
    r"\b(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|"
    r"eleventh|twelfth|[1-9]|1[0-2])(?:-?house)?\s+house\b|\b(?:first|second|"
    r"third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth)-house\s+lord\b",
    re.I,
)
_DATES = re.compile(
    r"\b(?:19|20)\d{2}\b|\b\d{1,2}\s+(?:days?|weeks?|months?|years?)\b|"
    r"\b(?:next|within|by|during)\s+(?:week|month|year|january|february|march|april|"
    r"may|june|july|august|september|october|november|december)\b",
    re.I,
)
_HIGH_STAKES_OR_OUTCOME = re.compile(
    r"\b(?:profession|promotion|income|profit|revenue|visa|citizenship|marriage|pregnan\w*|"
    r"health|diagnos\w*|child[- ]count|friend[- ]count|popularity)\b|[$₹€]\s?\d",
    re.I,
)
_SOURCE_CLAIM = re.compile(r"\b(?:according to|source|bphs|brihat|parashara)\b", re.I)
_OTHER_DOMAINS = {
    "career": ("wealth", "education", "business", "children", "spiritual", "travel", "friend"),
    "wealth": ("career", "education", "business", "children", "spiritual", "travel", "friend"),
    "education": ("career", "wealth", "business", "children", "spiritual", "travel", "friend"),
    "business": ("career", "wealth", "education", "children", "spiritual", "travel", "friend"),
    "children": ("career", "wealth", "education", "business", "spiritual", "travel", "friend"),
    "spirituality": ("career", "wealth", "education", "business", "children", "travel", "friend"),
    "travel": ("career", "wealth", "education", "business", "children", "spiritual", "friend"),
    "friends": ("career", "wealth", "education", "business", "children", "spiritual", "travel"),
}


class _NarrativeOutput(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    summary: str = Field(min_length=1, max_length=1600)
    explanation: str = Field(min_length=1, max_length=5000)
    question_relevance: str = Field(min_length=1, max_length=1600)
    limitations_text: str = Field(min_length=1, max_length=2000)
    follow_up: str | None = Field(default=None, max_length=600)


class SeniorAstrologerComposer:
    """An optional prose layer with a closed packet and deterministic claim barrier."""

    def __init__(self, transport: LanguageModelTransport) -> None:
        self._transport = transport

    def compose(
        self,
        question: str,
        detailed: DetailedComposedAnswer,
        evidence: InterpretationEvidence,
    ) -> SeniorAstrologerNarrative | None:
        """Return validated prose, or skip corpus-limit/UNKNOWN answers entirely."""
        if detailed.corpus_limitation or evidence.relevant_unknown or not detailed.evidence:
            return None
        request = CompositionProviderRequest(
            system_instructions=self._instructions(evidence.timing_answerability_established),
            user_payload_json=json.dumps(
                self._packet(question, detailed, evidence), sort_keys=True
            ),
        )
        response = self._transport.complete(request)
        try:
            output = _NarrativeOutput.model_validate_json(response.output_json)
        except ValidationError as error:
            raise AnswerCompositionError(
                "senior_narrative_schema",
                reason_code="invalid_structured_narrative",
                provider_id=response.provider_id,
                model_id=response.model_id,
            ) from error
        self._validate(output, detailed, evidence, response.provider_id, response.model_id)
        return SeniorAstrologerNarrative(
            summary=output.summary,
            explanation=output.explanation,
            question_relevance=output.question_relevance,
            follow_up=output.follow_up,
        )

    @staticmethod
    def _instructions(timing_answerable: bool) -> str:
        timing = (
            "Timing is not authorized. Do not give dates, periods, forecasts, or timing "
            "predictions."
        )
        return "\n".join(
            (
                "You are JyotishAI Senior Vedic Astrology Explanation Specialist.",
                "You are not an astrology calculator and not an independent doctrine source.",
                "Explain only the supplied governed evidence, facts, interpretations, and "
                "source metadata.",
                "Do not introduce doctrine from memory or new placements, planets, houses, "
                "yogas, aspects, conjunctions, dignities, divisional charts, dasha or transit "
                "claims.",
                "Do not provide remedies, gemstones, mantras, rituals, probabilities, scores, "
                "guarantees, financial amounts, health claims, marriage predictions, child counts, "
                "visas, citizenship, or invented sources.",
                "Do not say multiple items reinforce, confirm, rank, score, or increase certainty. "
                "Describe each supplied item separately where needed.",
                timing
                if not timing_answerable
                else "Use only explicitly supplied timing authorization.",
                "Return exactly one JSON object with summary, explanation, question_relevance, "
                "limitations_text, and follow_up. follow_up may be null.",
                "limitations_text must reproduce the supplied deterministic limitations "
                "without additions.",
            )
        )

    @staticmethod
    def _packet(
        question: str, detailed: DetailedComposedAnswer, evidence: InterpretationEvidence
    ) -> dict[str, object]:
        return {
            "original_question": question,
            "governed_domain": evidence.intent.domain.value,
            "deterministic_direct_summary": detailed.answer.removesuffix(" " + _TIMING),
            "why_it_applies": list(detailed.why_it_applies),
            "reviewed_interpretations": list(detailed.reviewed_interpretations),
            "domain_framing": [item.question_framing for item in detailed.evidence],
            "deterministic_limitations": list(detailed.limitations),
            "timing_answerability_established": evidence.timing_answerability_established,
            "corpus_limitation": detailed.corpus_limitation,
            "safe_chart_scope": [item.chart_scope for item in detailed.evidence],
            "safe_source_metadata": [
                {
                    "work": item.source_work,
                    "section": item.source_section,
                    "reference": item.source_reference,
                }
                for item in detailed.evidence
            ],
        }

    @staticmethod
    def _validate(
        output: _NarrativeOutput,
        detailed: DetailedComposedAnswer,
        evidence: InterpretationEvidence,
        provider_id: str,
        model_id: str,
    ) -> None:
        text = " ".join(
            value
            for value in (
                output.summary,
                output.explanation,
                output.question_relevance,
                output.follow_up or "",
            )
            if value
        ).strip()
        reason = None
        if output.limitations_text != " ".join(detailed.limitations):
            reason = "limitations_not_application_controlled"
        elif _BANNED.search(text) or _PLANETS.search(text):
            reason = "unsupported_astrology_or_safety_claim"
        elif _HIGH_STAKES_OR_OUTCOME.search(text):
            reason = "unsupported_outcome_or_high_stakes_claim"
        elif not evidence.timing_answerability_established and _DATES.search(text):
            reason = "unsupported_timing_claim"
        elif _HOUSE.search(text) and not any(
            placement.casefold() in text.casefold() for placement in detailed.why_it_applies
        ):
            reason = "unsupported_placement_claim"
        elif any(
            re.search(rf"\b{re.escape(term)}", text, re.I)
            for term in _OTHER_DOMAINS.get(evidence.intent.domain.value, ())
        ):
            reason = "outside_governed_domain"
        elif _SOURCE_CLAIM.search(text) and not any(
            item.source_work.casefold() in text.casefold() for item in detailed.evidence
        ):
            reason = "unsupported_source_claim"
        if reason:
            raise AnswerCompositionError(
                "senior_narrative_validation",
                reason_code=reason,
                provider_id=provider_id,
                model_id=model_id,
            )
