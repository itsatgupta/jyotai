"""Review-gated signification (kārakatva) corpus: graha/bhava → approved terms.

Governed like every other corpus: entries reach a corpus only through
``admit_signification_corpus``.  An entry needs a REVIEWED interpretation review by a named
reviewer, a governance-record reference, and a rule id and version.  The lordship principle
(review packet X18) is a separate record that approves one exact, versioned sentence template.

The production corpus lives in ``signification_admit02_v1`` (NEXT-ADMIT-02: the reviewer's
Sitting 2 glosses, 6th-house शत्रु restored, X18 v2); the NEXT-ADMIT-01 corpora (packet 0b
terms and X18 v1) stay in ``signification_part0b_v1``.  Any
change requires a review recorded on a governance record
(``research/next_dasha_01_review/governance-record-template.md``); an AI preparer is never a
reviewer.
"""

import re
from collections.abc import Iterable
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from astrologer.astrology.dasha import DashaLord
from astrologer.composition.comparison_guard import ranking_violation
from astrologer.composition.evaluative_guard import evaluative_violation
from astrologer.knowledge.models import ReviewCategory, ReviewRecord, ReviewStatus
from astrologer.knowledge.reviewer_guard import ai_review_violation

SIGNIFICATION_SCHEMA_VERSION: Final = "signification-corpus-v1"
# The sentence templates a lordship-principle (X18) record may approve: v1 (NEXT-ADMIT-01)
# and the compact form v2 (NEXT-ADMIT-02, Sitting 2 item 10).
PERIOD_THEMES_TEMPLATE_VERSION: Final = "period-themes-v1"
PERIOD_THEMES_COMPACT_TEMPLATE_VERSION: Final = "period-themes-v2"
APPROVED_PERIOD_THEMES_TEMPLATES: Final = frozenset(
    {PERIOD_THEMES_TEMPLATE_VERSION, PERIOD_THEMES_COMPACT_TEMPLATE_VERSION}
)

SubjectKind = Literal["graha", "bhava"]
# MAHADASHA_PRIMARY_ANTARDASHA_SECONDARY (NEXT-ADMIT-02, Sitting 1 item 27 / Sitting 2 item 17):
# both periods are described, and Antardasha lines are labelled "(secondary)".
LordshipScope = Literal[
    "MAHADASHA_ONLY", "MAHADASHA_AND_ANTARDASHA", "MAHADASHA_PRIMARY_ANTARDASHA_SECONDARY"
]

_GRAHAS: Final = frozenset(lord.value for lord in DashaLord)
_ID = r"^[A-Za-z][A-Za-z0-9_.@-]{0,127}$"
# Causal, evaluative or event words a signification term may never carry.
_FORBIDDEN_TERM_WORDS: Final = re.compile(
    r"\b(?:activates?|triggers?|therefore|because|strengthens?|delivers?|brings?|causes?|"
    r"leads to|results in|favou?rable|auspicious|good|bad|positive|negative|strong|strongest|"
    r"strength|weak|weakest|significant|guarantee[sd]?|will|promotion|success|failure)\b",
    re.IGNORECASE,
)


class SignificationCorpusError(ValueError):
    """Raised when a signification corpus fails admission."""


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ApprovedTerm(_Frozen):
    """One kept term: its source wording and the reviewer-approved English display."""

    sanskrit: str = Field(min_length=1, max_length=128)
    display: str = Field(min_length=1, max_length=64)


class SignificationEntry(_Frozen):
    """Approved significations of one graha or one bhava."""

    subject_kind: SubjectKind
    # A graha name ("jupiter") or a house number as text ("10").
    subject: str = Field(min_length=1, max_length=16)
    terms: tuple[ApprovedTerm, ...] = Field(min_length=1)
    rule_id: str = Field(pattern=_ID)
    rule_version: str = Field(min_length=1, max_length=32)
    source_locator: str = Field(min_length=1, max_length=512)
    governance_record_ref: str = Field(min_length=1, max_length=256)
    review: ReviewRecord

    @model_validator(mode="after")
    def subject_must_exist(self) -> "SignificationEntry":
        if self.subject_kind == "graha" and self.subject not in _GRAHAS:
            raise ValueError(f"unknown graha: {self.subject}")
        if self.subject_kind == "bhava" and self.subject not in {str(n) for n in range(1, 13)}:
            raise ValueError(f"unknown bhava: {self.subject}")
        return self


class LordshipPrincipleRecord(_Frozen):
    """Review packet X18: a Dasha lord may be described with the significations of the
    houses it rules and occupies, using exactly one approved, versioned template."""

    rule_id: str = Field(pattern=_ID)
    rule_version: str = Field(min_length=1, max_length=32)
    approved_template_version: str = Field(min_length=1)
    scope: LordshipScope
    source_locator: str = Field(min_length=1, max_length=512)
    governance_record_ref: str = Field(min_length=1, max_length=256)
    review: ReviewRecord


class SignificationCorpusManifest(_Frozen):
    schema_version: Literal["signification-corpus-v1"] = SIGNIFICATION_SCHEMA_VERSION
    manifest_id: str = Field(pattern=_ID)
    manifest_version: str = Field(min_length=1, max_length=32)
    entries: tuple[SignificationEntry, ...] = ()
    lordship_principle: LordshipPrincipleRecord | None = None


_ADMISSION_TOKEN: Final = object()


class SignificationCorpus:
    """Admitted significations only; construct through ``admit_signification_corpus``."""

    def __init__(self, *, token: object, manifest: SignificationCorpusManifest) -> None:
        if token is not _ADMISSION_TOKEN:
            raise TypeError("signification corpora are created only by admission")
        self._manifest = manifest
        self._by_subject = {(e.subject_kind, e.subject): e for e in manifest.entries}

    @property
    def version(self) -> str:
        return f"{self._manifest.manifest_id}@{self._manifest.manifest_version}"

    @property
    def entries(self) -> tuple[SignificationEntry, ...]:
        return self._manifest.entries

    @property
    def lordship_principle(self) -> LordshipPrincipleRecord | None:
        return self._manifest.lordship_principle

    def graha(self, lord: str) -> SignificationEntry | None:
        return self._by_subject.get(("graha", lord))

    def bhava(self, house: int) -> SignificationEntry | None:
        return self._by_subject.get(("bhava", str(house)))


def _check_review(review: ReviewRecord, what: str) -> None:
    if review.status is not ReviewStatus.REVIEWED:
        raise SignificationCorpusError(f"{what}: review is not REVIEWED")
    if review.category is not ReviewCategory.INTERPRETATION_REVIEW:
        raise SignificationCorpusError(f"{what}: needs an interpretation review")
    if (violation := ai_review_violation(review)) is not None:
        raise SignificationCorpusError(f"{what}: an AI preparer is never a reviewer: {violation}")


def term_violation(text: str) -> str | None:
    """The first ranking, causal, evaluative or event word in ``text``, else None."""
    match = _FORBIDDEN_TERM_WORDS.search(text)
    if match:
        return match.group()
    return ranking_violation(text) or evaluative_violation(text)


def admit_signification_corpus(manifest: SignificationCorpusManifest) -> SignificationCorpus:
    """Admit a manifest: every entry reviewed, unique, and free of forbidden words."""
    seen: set[tuple[str, str]] = set()
    for entry in manifest.entries:
        key = (entry.subject_kind, entry.subject)
        if key in seen:
            raise SignificationCorpusError(f"duplicate signification entry: {key}")
        seen.add(key)
        _check_review(entry.review, f"{entry.rule_id}")
        for term in entry.terms:
            if (bad := term_violation(term.display)) is not None:
                raise SignificationCorpusError(f"{entry.rule_id}: forbidden word {bad!r}")
    principle = manifest.lordship_principle
    if principle is not None:
        _check_review(principle.review, principle.rule_id)
        if principle.approved_template_version not in APPROVED_PERIOD_THEMES_TEMPLATES:
            raise SignificationCorpusError(
                f"{principle.rule_id}: approves template "
                f"{principle.approved_template_version!r}, not one of "
                f"{sorted(APPROVED_PERIOD_THEMES_TEMPLATES)!r}"
            )
    return SignificationCorpus(token=_ADMISSION_TOKEN, manifest=manifest)


EMPTY_SIGNIFICATION_MANIFEST: Final = SignificationCorpusManifest(
    manifest_id="jyotish.signification.production", manifest_version="v0-empty"
)

# The NEXT-SIG-01 release (no entry, no X18 record); kept for history and tests.
EMPTY_SIGNIFICATION_CORPUS: Final = admit_signification_corpus(EMPTY_SIGNIFICATION_MANIFEST)


def admit_entries(
    manifest_id: str,
    manifest_version: str,
    entries: Iterable[SignificationEntry],
    lordship_principle: LordshipPrincipleRecord | None = None,
) -> SignificationCorpus:
    """Convenience wrapper used by tests and future governed releases."""
    return admit_signification_corpus(
        SignificationCorpusManifest(
            manifest_id=manifest_id,
            manifest_version=manifest_version,
            entries=tuple(entries),
            lordship_principle=lordship_principle,
        )
    )
