"""Deterministic preparation and validation around a constrained LLM transport."""

import json
import re

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from astrologer.composition.models import (
    DEFAULT_COMPOSITION_POLICY,
    AnswerCompositionPolicy,
    ComposedAnswer,
    CompositionProviderRequest,
    LanguageModelTransport,
)
from astrologer.evidence import InterpretationEvidence, InterpretationEvidenceItem

_TIMING_VALUE_PATTERN = re.compile(
    r"\b(?:19|20)\d{2}\b|\b\d{1,2}\s+(?:day|week|month|year)s?\b|"
    r"\bnext\s+(?:week|month|year)\b|\bsoon\b|\bby\s+"
    r"(?:january|february|march|april|may|june|july|august|september|october|november|december)\b",
    re.I,
)


class AnswerCompositionError(ValueError):
    """Raised when a provider response is not a safe governed composition."""

    def __init__(
        self,
        category: str = "provider_output_validation",
        *,
        provider_id: str | None = None,
        model_id: str | None = None,
    ) -> None:
        super().__init__("provider response is not a safe governed composition")
        self.category = category
        self.provider_id = provider_id
        self.model_id = model_id


class _ModelOutput(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    answer: str = Field(min_length=1, max_length=8000)
    referenced_evidence_item_ids: tuple[str, ...] = ()
    timing_answered: bool
    corpus_limitation: bool


class AnswerComposer:
    """Compose user-facing language from one validated evidence contract only."""

    def __init__(
        self,
        transport: LanguageModelTransport,
        policy: AnswerCompositionPolicy = DEFAULT_COMPOSITION_POLICY,
    ) -> None:
        self._transport = transport
        self._policy = policy

    def compose(self, question: str, evidence: InterpretationEvidence) -> ComposedAnswer:
        """Return a validated answer, never exposing raw astrology inputs to a transport."""
        if not question.strip():
            raise ValueError("question must not be blank")
        if not evidence.selected_matched:
            return self._corpus_limit_answer(evidence)

        timing_unavailable = (
            evidence.intent.timing_requested and not evidence.timing_answerability_established
        )
        request = CompositionProviderRequest(
            system_instructions=self._policy.system_instructions(
                static_context_only=timing_unavailable
            ),
            user_payload_json=json.dumps(
                self._safe_model_payload(
                    question,
                    evidence,
                    static_context_only=timing_unavailable,
                ),
                sort_keys=True,
                separators=(",", ":"),
            ),
        )
        response = self._transport.complete(request)
        output = self._parse_and_validate_output(
            response.output_json, evidence, response.provider_id, response.model_id
        )
        if timing_unavailable:
            # Generated prose cannot be proven free of all timing claims. Do not return it.
            # The static governed wording and the timing limitation are application-owned.
            return self._timing_unavailable_answer(
                evidence, response.provider_id, response.model_id
            )
        return ComposedAnswer(
            answer=output.answer,
            referenced_evidence_item_ids=output.referenced_evidence_item_ids,
            timing_answered=False,
            corpus_limitation=output.corpus_limitation,
            policy_id=self._policy.policy_id,
            policy_version=self._policy.policy_version,
            prompt_version=self._policy.prompt_version,
            interpretation_contract_sha256=evidence.contract_content_sha256,
            manifest_id=evidence.manifest_id,
            manifest_version=evidence.manifest_version,
            manifest_content_sha256=evidence.manifest_content_sha256,
            provider_id=response.provider_id,
            model_id=response.model_id,
        )

    def _safe_model_payload(
        self,
        question: str,
        evidence: InterpretationEvidence,
        *,
        static_context_only: bool,
    ) -> dict[str, object]:
        """Project a deliberately small allowlist; never serialize the full contract."""
        return {
            "question": (
                "Provide a static contextual explanation for the user's "
                f"{evidence.intent.domain.value} topic."
                if static_context_only
                else question
            ),
            "composition_mode": "static_context_only" if static_context_only else "direct_answer",
            "composition_policy": {
                "policy_id": self._policy.policy_id,
                "policy_version": self._policy.policy_version,
                "prompt_version": self._policy.prompt_version,
            },
            "intent": evidence.intent.model_dump(mode="json"),
            "timing_answerability_established": evidence.timing_answerability_established,
            "provenance": {
                "manifest_id": evidence.manifest_id,
                "manifest_version": evidence.manifest_version,
                "manifest_content_sha256": evidence.manifest_content_sha256,
                "interpretation_contract_sha256": evidence.contract_content_sha256,
            },
            "selected_matched": [self._safe_item(item) for item in evidence.selected_matched],
            "relevant_unmatched": [self._safe_item(item) for item in evidence.relevant_unmatched],
            "relevant_unknown": [self._safe_item(item) for item in evidence.relevant_unknown],
        }

    @staticmethod
    def _safe_item(item: InterpretationEvidenceItem) -> dict[str, object]:
        return {
            "evidence_item_id": item.evidence_item_id,
            "rule_id": item.rule_id,
            "rule_version": item.rule_version,
            "evaluation_status": item.evaluation_status.value,
            "evidence_direction": item.evidence_direction.value,
            "domain": item.domain.value,
            "taxonomy": item.taxonomy.value,
            "posture": item.posture.value,
            "chart_scope": item.chart_scope.value,
            "interpretation_id": item.interpretation_id,
            "interpretation_version": item.interpretation_version,
            "reviewed_statement": item.reviewed_statement,
            "scope_notes": item.scope_notes,
        }

    def _parse_and_validate_output(
        self,
        output_json: str,
        evidence: InterpretationEvidence,
        provider_id: str,
        model_id: str,
    ) -> _ModelOutput:
        try:
            output = _ModelOutput.model_validate_json(output_json)
        except ValidationError as error:
            category = (
                "provider_output_parse"
                if any(item["type"] == "json_invalid" for item in error.errors())
                else "provider_output_validation"
            )
            raise AnswerCompositionError(
                category, provider_id=provider_id, model_id=model_id
            ) from error
        allowed_ids = {
            item.evidence_item_id
            for item in (
                evidence.selected_matched + evidence.relevant_unmatched + evidence.relevant_unknown
            )
        }
        references = output.referenced_evidence_item_ids
        if len(references) != len(set(references)) or not set(references).issubset(allowed_ids):
            raise AnswerCompositionError(
                "provider_output_evidence_reference", provider_id=provider_id, model_id=model_id
            )
        if not references:
            raise AnswerCompositionError(
                "provider_output_evidence_reference", provider_id=provider_id, model_id=model_id
            )
        if output.timing_answered or _TIMING_VALUE_PATTERN.search(output.answer):
            raise AnswerCompositionError(
                "provider_output_timing_safety", provider_id=provider_id, model_id=model_id
            )
        return output

    def _timing_unavailable_answer(
        self, evidence: InterpretationEvidence, provider_id: str, model_id: str
    ) -> ComposedAnswer:
        """Return only pre-reviewed static wording plus an application-owned timing limit."""
        static_context = " ".join(item.reviewed_statement for item in evidence.selected_matched)
        return ComposedAnswer(
            answer=(
                f"{static_context} Timing is not established by the current governed evidence."
            ),
            referenced_evidence_item_ids=tuple(
                item.evidence_item_id for item in evidence.selected_matched
            ),
            corpus_limitation=False,
            policy_id=self._policy.policy_id,
            policy_version=self._policy.policy_version,
            prompt_version=self._policy.prompt_version,
            interpretation_contract_sha256=evidence.contract_content_sha256,
            manifest_id=evidence.manifest_id,
            manifest_version=evidence.manifest_version,
            manifest_content_sha256=evidence.manifest_content_sha256,
            provider_id=provider_id,
            model_id=model_id,
        )

    def _corpus_limit_answer(self, evidence: InterpretationEvidence) -> ComposedAnswer:
        unknown_note = (
            " Some relevant governed evidence is unresolved (UNKNOWN), so it is not treated "
            "as false."
            if evidence.relevant_unknown
            else ""
        )
        timing_note = (
            " Timing is not established by the current evidence."
            if evidence.intent.timing_requested
            else ""
        )
        return ComposedAnswer(
            answer=(
                "The current governed corpus does not establish the requested "
                f"{evidence.intent.domain.value} "
                f"interpretation from the supplied evidence.{unknown_note}{timing_note}"
            ),
            corpus_limitation=True,
            policy_id=self._policy.policy_id,
            policy_version=self._policy.policy_version,
            prompt_version=self._policy.prompt_version,
            interpretation_contract_sha256=evidence.contract_content_sha256,
            manifest_id=evidence.manifest_id,
            manifest_version=evidence.manifest_version,
            manifest_content_sha256=evidence.manifest_content_sha256,
            provider_id="deterministic-corpus-limit",
            model_id="none",
        )
