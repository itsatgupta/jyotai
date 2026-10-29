"""Typed, status-preserving Career answer claim ledger."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, model_validator

from astrologer.questions.models import CareerQuestionFocus, QuestionDomain, QuestionShape


class ClaimKind(StrEnum):
    CALCULATED_FACT = "CALCULATED_FACT"
    APPROVED_INTERPRETATION = "APPROVED_INTERPRETATION"
    APPROVED_TIMING_INTERPRETATION = "APPROVED_TIMING_INTERPRETATION"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    UNSUPPORTED_REQUEST = "UNSUPPORTED_REQUEST"


class ClaimStatus(StrEnum):
    MATCH = "MATCH"
    NO_MATCH = "NO_MATCH"
    UNKNOWN = "UNKNOWN"
    NOT_EVALUATED = "NOT_EVALUATED"
    UNSUPPORTED = "UNSUPPORTED"


class CareerClaim(BaseModel):
    """One independently supported statement; there is no synthesis operation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    claim_id: str
    kind: ClaimKind
    domain: QuestionDomain = QuestionDomain.CAREER
    requested_question_shape: CareerQuestionFocus
    fact_ids: tuple[str, ...] = ()
    rule_ids: tuple[str, ...] = ()
    evidence_item_ids: tuple[str, ...] = ()
    calculation_version: str
    methodology_version: str
    source_reference: str
    evaluation_status: ClaimStatus
    permitted_wording: str
    timing_reference: str | None = None
    authorized_precision: str | None = None
    missing_evidence: tuple[str, ...] = ()

    @model_validator(mode="after")
    def supported_claim_has_reference(self) -> "CareerClaim":
        if self.kind in {
            ClaimKind.APPROVED_INTERPRETATION,
            ClaimKind.APPROVED_TIMING_INTERPRETATION,
        }:
            if self.evaluation_status is not ClaimStatus.MATCH or not self.rule_ids:
                raise ValueError("approved interpretations require a matching rule")
        if self.kind is ClaimKind.APPROVED_INTERPRETATION and not self.evidence_item_ids:
            raise ValueError("static interpretation requires selected evidence")
        if self.kind is ClaimKind.APPROVED_TIMING_INTERPRETATION:
            if not self.timing_reference or not self.authorized_precision:
                raise ValueError("timing interpretation requires a window and precision")
        if self.kind is ClaimKind.CALCULATED_FACT and not self.fact_ids:
            raise ValueError("calculated fact requires a fact ID")
        return self


class CareerClaimLedger(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    ledger_version: str = "career-claim-ledger-v1"
    domain: QuestionDomain = QuestionDomain.CAREER
    question_shape: QuestionShape
    requested_question_shape: CareerQuestionFocus
    claims: tuple[CareerClaim, ...]
