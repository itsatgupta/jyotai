"""Fail-closed senior-astrologer narrative composition over detailed evidence."""

import json
import logging
import re
from dataclasses import dataclass
from typing import TypedDict

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
    r"transit(?:s|ing)?|remed(?:y|ies)|gemstone(?:s)?|mantra(?:s)?|ritual(?:s)?"
    r")\b",
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
    r"may|june|july|august|september|october|november|december)\b|\bsoon\b",
    re.I,
)
_SOURCE_CLAIM = re.compile(r"\b(?:according to|source|bphs|brihat|parashara)\b", re.I)
_EMAIL = re.compile(r"\b[^\s@]+@[^\s@]+\.[^\s@]+\b")
_CURRENCY_AMOUNT = re.compile(r"([$₹€])\s?\d+(?:[,.]\d+)*")
_DATE_VALUE = re.compile(r"\b(?:19|20)\d{2}(?:[-/]\d{1,2}){0,2}\b")
_LONG_NUMBER = re.compile(r"\b\d{7,}\b")
_SENSITIVE_CONCEPTS = {
    "profession": re.compile(r"\bprofession\b", re.I),
    "promotion": re.compile(r"\bpromotion\b", re.I),
    "income": re.compile(r"\bincome\b", re.I),
    "profit": re.compile(r"\bprofit\b", re.I),
    "revenue": re.compile(r"\brevenue\b", re.I),
    "visa": re.compile(r"\bvisa\b", re.I),
    "citizenship": re.compile(r"\bcitizenship\b", re.I),
    "marriage": re.compile(r"\bmarriage\b", re.I),
    "pregnancy": re.compile(r"\bpregnan\w*\b", re.I),
    "health": re.compile(r"\bhealth\b", re.I),
    "diagnosis": re.compile(r"\bdiagnos\w*\b", re.I),
    "child_count": re.compile(r"\b(?:child[- ]count|number of children)\b", re.I),
    "friend_count": re.compile(r"\b(?:friend[- ]count|number of friends)\b", re.I),
    "popularity": re.compile(r"\bpopularity\b", re.I),
}
_OUTCOME_ASSERTION = re.compile(
    r"\b(?:will|likely|strongly indicates?|promises?|guarantees?|expected to|"
    r"should receive|will receive|destined|certain|definitely|very strong chance|"
    r"highly probable|assured|confirmed)\b",
    re.I,
)
_LIMITATION_POSTURE = re.compile(
    r"\b(?:does not|do not|cannot|can not|not establish(?:ed)?|not identify|"
    r"not determine|not conclude|not a guarantee|should not be read as)\b",
    re.I,
)
_QUANTIFICATION = re.compile(
    r"[$₹€]\s?\d+|\b\d+(?:\.\d+)?\s?%|\b(?:percentage|percent|probability|"
    r"confidence score)\b|\b(?:income|salary|profit|revenue)\s+(?:of\s+|is\s+|"
    r"will be\s+|at\s+)?\d+|\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+"
    r"(?:children|friends|matching rules|rules|matches)\b",
    re.I,
)
_HEALTH_HARD_BLOCK = re.compile(
    r"\b(?:diagnos\w*|prognos\w*|treat(?:ment|ing)?|disease|life expectancy)\b", re.I
)
_LOGGER = logging.getLogger(__name__)
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


@dataclass(frozen=True)
class _AuthorizedConcepts:
    """Sensitive concepts licensed by the closed packet, split by evidence posture."""

    supported: frozenset[str]
    limitation_only: frozenset[str]


class _ApprovedPhrases(TypedDict):
    summary: list[str]
    explanation: dict[str, list[str]]
    question_relevance: list[str]


class _NarrativeOutput(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    summary: str = Field(min_length=1, max_length=1600)
    explanation: str = Field(min_length=1, max_length=5000)
    question_relevance: str = Field(min_length=1, max_length=1600)
    limitations_text: str = Field(min_length=1, max_length=2000)
    follow_up: str | None = Field(default=None, max_length=600)
    supporting_evidence_item_ids: dict[str, list[str]]


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
            user_payload_json=json.dumps(self._packet(detailed, evidence), sort_keys=True),
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
                "limitations_text, follow_up, and supporting_evidence_item_ids. "
                "follow_up must be null. supporting_evidence_item_ids must map summary, "
                "explanation, and question_relevance to the supplied evidence_item_ids.",
                "Use only the exact approved phrases in approved_narrative_phrases. "
                "Do not create free-form sentences or combine phrases.",
                "limitations_text must reproduce the supplied deterministic limitations "
                "without additions.",
            )
        )

    @staticmethod
    def _packet(
        detailed: DetailedComposedAnswer, evidence: InterpretationEvidence
    ) -> dict[str, object]:
        return {
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
            "evidence_item_ids": list(detailed.referenced_evidence_item_ids),
            "approved_narrative_phrases": _approved_phrases(detailed, evidence.intent.domain.value),
        }

    @staticmethod
    def _validate(
        output: _NarrativeOutput,
        detailed: DetailedComposedAnswer,
        evidence: InterpretationEvidence,
        provider_id: str,
        model_id: str,
    ) -> None:
        if output.limitations_text == " ".join(detailed.limitations) and _supported_output(
            output, detailed, evidence.intent.domain.value
        ):
            return
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
        category = "not_applicable"
        pattern = "not_applicable"
        match: re.Match[str] | None = None
        authorized_concepts = _authorized_concepts(detailed)
        if output.limitations_text != " ".join(detailed.limitations):
            reason = "limitations_not_application_controlled"
            category = "application_controlled_limitations"
            pattern = "exact_limitations_text"
        elif match := _BANNED.search(text):
            reason = "unsupported_doctrine"
            category = "banned_astrology_or_safety_term"
            pattern = "banned_term"
        elif match := _PLANETS.search(text):
            reason = "unsupported_doctrine"
            category = "banned_astrology_or_safety_term"
            pattern = "planet_name"
        elif match := _HEALTH_HARD_BLOCK.search(text):
            reason = "unsupported_concept"
            category = "health_high_stakes"
            pattern = match.group().casefold()
        elif concept_match := _unauthorized_concept_match(text, authorized_concepts):
            reason = "unsupported_concept"
            category = "sensitive_concept_authorization"
            pattern, match = concept_match
        elif assertion_match := _unauthorized_assertion_match(text, authorized_concepts):
            reason = "unauthorized_outcome_assertion"
            category = "assertion_strength"
            pattern, match = assertion_match
        elif concept_match := _nonlimitation_use_of_limited_concept(text, authorized_concepts):
            reason = "unsupported_concept"
            category = "sensitive_concept_authorization"
            pattern, match = concept_match
        elif match := _QUANTIFICATION.search(text):
            reason = "unsupported_quantification"
            category = "quantification"
            pattern = _matched_quantification_pattern(match)
        elif not evidence.timing_answerability_established and (match := _DATES.search(text)):
            reason = "unsupported_timing_claim"
            category = "timing"
            pattern = "date_or_timing_phrase"
        elif (match := _HOUSE.search(text)) and not any(
            placement.casefold() in text.casefold() for placement in detailed.why_it_applies
        ):
            reason = "unsupported_placement_claim"
            category = "placement"
            pattern = "house_or_house_lord"
        elif match := _other_domain_match(text, evidence.intent.domain.value):
            reason = "outside_governed_domain"
            category = "domain_boundary"
            pattern = "other_governed_domain"
        elif (match := _SOURCE_CLAIM.search(text)) and not any(
            item.source_work.casefold() in text.casefold() for item in detailed.evidence
        ):
            reason = "invented_source"
            category = "source_attribution"
            pattern = "unapproved_source_claim"
        elif not _supported_output(output, detailed, evidence.intent.domain.value):
            reason = "unsupported_narrative_claim"
            category = "closed_phrase_and_evidence_support"
            pattern = "unapproved_phrase_or_reference"
        if reason:
            _LOGGER.warning(
                "senior_narrative_validation_rejected reason_code=%s "
                "validator_category=%s matched_pattern=%s excerpt=%r",
                reason,
                category,
                pattern,
                _sanitized_excerpt(text, match),
            )
            raise AnswerCompositionError(
                "senior_narrative_validation",
                reason_code=reason,
                provider_id=provider_id,
                model_id=model_id,
            )


def _other_domain_match(text: str, domain: str) -> re.Match[str] | None:
    """Return the first existing domain-boundary match without changing rule order."""
    for term in _OTHER_DOMAINS.get(domain, ()):
        if match := re.search(rf"\b{re.escape(term)}", text, re.I):
            return match
    return None


def _approved_phrases(detailed: DetailedComposedAnswer, domain: str) -> _ApprovedPhrases:
    """Build a closed phrase catalog from the deterministic display projection."""
    return {
        "summary": [
            detailed.answer.removesuffix(" " + _TIMING),
            "This is a contextual reading of the supplied governed evidence.",
        ],
        "explanation": {
            item_id: [
                item.placement_explanation,
                item.reviewed_statement,
                f"This reviewed D1 indication provides context for {domain} matters.",
            ]
            for item_id, item in zip(
                detailed.referenced_evidence_item_ids, detailed.evidence, strict=True
            )
        },
        "question_relevance": [item.question_framing for item in detailed.evidence],
    }


def _supported_output(
    output: _NarrativeOutput, detailed: DetailedComposedAnswer, domain: str
) -> bool:
    """Accept only whole approved phrases with the exact evidence links they require."""
    references = output.supporting_evidence_item_ids
    if set(references) != {"summary", "explanation", "question_relevance"}:
        return False
    all_ids = list(detailed.referenced_evidence_item_ids)
    if len(all_ids) != len(set(all_ids)) or len(all_ids) != len(detailed.evidence):
        return False
    if references["summary"] != all_ids or references["question_relevance"] != all_ids:
        return False
    explanation_ids = references["explanation"]
    if len(explanation_ids) != 1 or explanation_ids[0] not in all_ids:
        return False
    approved = _approved_phrases(detailed, domain)
    return (
        output.summary in approved["summary"]
        and output.explanation in approved["explanation"][explanation_ids[0]]
        and output.question_relevance in approved["question_relevance"]
        and output.follow_up is None
    )


def _authorized_concepts(detailed: DetailedComposedAnswer) -> _AuthorizedConcepts:
    """Derive sensitive-term authority only from the closed governed packet.

    The user question is deliberately absent: it supplies conversational context, never
    astrological authority. A term found exclusively in an application-owned limitation
    can be restated only as a limitation.
    """
    packet_fields = (
        detailed.answer,
        *detailed.why_it_applies,
        *detailed.reviewed_interpretations,
        *detailed.limitations,
        *(item.question_framing for item in detailed.evidence),
        *(item.source_work for item in detailed.evidence),
        *(item.source_section for item in detailed.evidence),
        *(item.source_reference or "" for item in detailed.evidence),
    )
    supported_set: set[str] = set()
    limited_set: set[str] = set()
    for field in packet_fields:
        for sentence in _sentences(field):
            for concept, pattern in _SENSITIVE_CONCEPTS.items():
                if not pattern.search(sentence):
                    continue
                if _LIMITATION_POSTURE.search(sentence):
                    limited_set.add(concept)
                else:
                    supported_set.add(concept)
    supported = frozenset(supported_set)
    limited = frozenset(limited_set)
    return _AuthorizedConcepts(
        supported=supported | limited,
        limitation_only=limited - supported,
    )


def _sentences(text: str) -> tuple[str, ...]:
    split_sentences = re.split(r"(?<=[.!?])\s+", text)
    return tuple(sentence.strip() for sentence in split_sentences if sentence.strip())


def _unauthorized_concept_match(
    text: str, authorized: _AuthorizedConcepts
) -> tuple[str, re.Match[str]] | None:
    """Return a sensitive concept that has no authority anywhere in the closed packet."""
    for sentence in _sentences(text):
        for concept, pattern in _SENSITIVE_CONCEPTS.items():
            if match := pattern.search(sentence):
                if concept not in authorized.supported:
                    return concept, match
    return None


def _nonlimitation_use_of_limited_concept(
    text: str, authorized: _AuthorizedConcepts
) -> tuple[str, re.Match[str]] | None:
    """Reject neutral or descriptive expansion of a term supplied only as a limitation."""
    for sentence in _sentences(text):
        if _LIMITATION_POSTURE.search(sentence):
            continue
        for concept in authorized.limitation_only:
            if match := _SENSITIVE_CONCEPTS[concept].search(sentence):
                return concept, match
    return None


def _unauthorized_assertion_match(
    text: str, authorized: _AuthorizedConcepts
) -> tuple[str, re.Match[str]] | None:
    """Reject strengthened outcomes while preserving explicit limitation restatements."""
    for sentence in _sentences(text):
        if _LIMITATION_POSTURE.search(sentence):
            continue
        if match := _OUTCOME_ASSERTION.search(sentence):
            sensitive = next(
                (
                    concept
                    for concept, pattern in _SENSITIVE_CONCEPTS.items()
                    if concept in authorized.supported and pattern.search(sentence)
                ),
                None,
            )
            if sensitive is not None:
                # Log the authorized concept rather than only the strengthening word so
                # diagnostics identify the governed boundary that was exceeded.
                return sensitive, _SENSITIVE_CONCEPTS[sensitive].search(text) or match
            # Certainty language is an unsupported outcome claim even where the
            # provider avoids a sensitive noun (for example, "this guarantees success").
            if match.group().casefold() in {
                "promises",
                "promise",
                "guarantees",
                "guarantee",
                "certain",
                "definitely",
                "very strong chance",
                "highly probable",
                "assured",
                "confirmed",
            }:
                return "assertive_language", match
    return None


def _matched_quantification_pattern(match: re.Match[str]) -> str:
    """Name a quantification branch without retaining a financial or count value."""
    if _CURRENCY_AMOUNT.fullmatch(match.group()):
        return "currency_amount"
    if "%" in match.group():
        return "percentage"
    return "unsupported_quantification"


def _sanitized_excerpt(text: str, match: re.Match[str] | None) -> str:
    """Return at most 96 characters around a rejected term, with sensitive values redacted."""
    if match is None:
        return "not_applicable"
    start = max(0, match.start() - 36)
    end = min(len(text), match.end() + 36)
    excerpt = re.sub(r"\s+", " ", text[start:end]).strip()
    excerpt = _EMAIL.sub("[redacted-email]", excerpt)
    excerpt = _CURRENCY_AMOUNT.sub(r"\1[redacted-amount]", excerpt)
    excerpt = _DATE_VALUE.sub("[redacted-date]", excerpt)
    excerpt = _LONG_NUMBER.sub("[redacted-number]", excerpt)
    return excerpt[:96]
