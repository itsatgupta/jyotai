"""NEXT-MARRIAGE-02: domain tags on signification terms.

Every signification term carries domain tags (Career, Marriage, Wealth, …), each with a
status: ``reviewed`` or ``provisional``.  An answer shows only the terms tagged for the asked
domain, so a Marriage answer never shows a Career term ("trade or business", "adviser or
counsellor") unless that term is tagged Marriage.

* **Reviewed terms** (the admitted corpora in ``signification_part0b_v1`` and
  ``signification_admit02_v1``) are tagged here, in a separate versioned tag record keyed by
  ``(subject_kind, subject, sanskrit)``.  The admitted manifests are not touched (their hashes
  stay pinned).  Tag set v1 tags every reviewed term **Career (reviewed)**: the terms were
  the review packet's "Proposed for Career" column and were admitted for Career; no term has
  been reviewed for any other domain.  A reviewed tag set carries reviewed tags only.
* **Provisional terms** carry their tags on their own record
  (``knowledge.provisional_signification``), always with status ``provisional``.

``domain_view`` gives the reviewed corpus an answer for one domain may use: only terms with a
reviewed tag for that domain; an entry left without terms is dropped; the X18 record is kept.
In a corpus the tag set covers, an untagged term is shown in no domain (fail closed).  A
corpus the tag set does not cover (a test fixture) predates tagging: every one admitted so far
was a Career packet, so its terms are treated as Career only (``UNTAGGED_CORPUS_DOMAIN``).
"""

from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from astrologer.knowledge.models import JyotishDomain
from astrologer.knowledge.signification import (
    SignificationCorpus,
    SignificationEntry,
    SubjectKind,
    admit_signification_corpus,
)
from astrologer.knowledge.signification_admit02_v1 import PRODUCTION_SIGNIFICATION_MANIFEST_V3
from astrologer.knowledge.signification_part0b_v1 import (
    PRODUCTION_SIGNIFICATION_MANIFEST,
    SIGNIFICATION_MANIFEST_V1,
)

TagStatus = Literal["reviewed", "provisional"]
# Terms of a corpus admitted before tagging (fixtures) are Career only; see module docstring.
UNTAGGED_CORPUS_DOMAIN: Final = JyotishDomain.CAREER

TermKey = tuple[str, str, str]


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class DomainTag(_Frozen):
    """One domain a term may be shown for, and whether that use is reviewed or provisional."""

    domain: JyotishDomain
    status: TagStatus


class TermTags(_Frozen):
    """The domain tags of one admitted term, keyed by its subject and Sanskrit word."""

    subject_kind: SubjectKind
    subject: str = Field(min_length=1, max_length=16)
    sanskrit: str = Field(min_length=1, max_length=128)
    tags: tuple[DomainTag, ...] = Field(min_length=1)

    @property
    def key(self) -> TermKey:
        return (self.subject_kind, self.subject, self.sanskrit)

    @model_validator(mode="after")
    def domains_are_unique(self) -> "TermTags":
        domains = [tag.domain for tag in self.tags]
        if len(domains) != len(set(domains)):
            raise ValueError(f"duplicate domain tag on {self.key}")
        return self


class SignificationTagSet(_Frozen):
    """Versioned domain tags for the terms of the reviewed corpora it names."""

    tag_set_id: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$")
    tag_set_version: str = Field(min_length=1, max_length=32)
    covers_corpora: tuple[str, ...] = Field(min_length=1)
    basis: str = Field(min_length=1, max_length=2000)
    terms: tuple[TermTags, ...]

    @model_validator(mode="after")
    def keys_are_unique_and_reviewed(self) -> "SignificationTagSet":
        keys = [term.key for term in self.terms]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate term in tag set")
        for term in self.terms:
            if any(tag.status != "reviewed" for tag in term.tags):
                raise ValueError(f"a reviewed tag set carries reviewed tags only: {term.key}")
        return self

    @property
    def version(self) -> str:
        return f"{self.tag_set_id}@{self.tag_set_version}"

    def reviewed_domains(self, key: TermKey) -> frozenset[JyotishDomain]:
        for term in self.terms:
            if term.key == key:
                return frozenset(tag.domain for tag in term.tags if tag.status == "reviewed")
        return frozenset()


def domain_view(
    corpus: SignificationCorpus, domain: JyotishDomain, tag_set: "SignificationTagSet"
) -> SignificationCorpus:
    """The reviewed terms of ``corpus`` tagged for ``domain`` (see module docstring).

    Returns ``corpus`` itself when every term is tagged for the domain, so a Career answer is
    unchanged; otherwise a filtered corpus versioned ``<version>+<domain>``.
    """
    covered = corpus.version in tag_set.covers_corpora

    def shown(entry: SignificationEntry, sanskrit: str) -> bool:
        if not covered:
            return domain is UNTAGGED_CORPUS_DOMAIN
        return domain in tag_set.reviewed_domains((entry.subject_kind, entry.subject, sanskrit))

    entries: list[SignificationEntry] = []
    for entry in corpus.entries:
        terms = tuple(term for term in entry.terms if shown(entry, term.sanskrit))
        if terms == entry.terms:
            entries.append(entry)
        elif terms:
            entries.append(entry.model_copy(update={"terms": terms}))
    if tuple(entries) == corpus.entries:
        return corpus
    manifest = corpus.manifest
    return admit_signification_corpus(
        manifest.model_copy(
            update={
                "manifest_version": f"{manifest.manifest_version}+{domain.value}",
                "entries": tuple(entries),
            }
        )
    )


def _career_reviewed(*manifests_entries: tuple[SignificationEntry, ...]) -> tuple[TermTags, ...]:
    keys: dict[TermKey, None] = {}
    for entries in manifests_entries:
        for entry in entries:
            for term in entry.terms:
                keys.setdefault((entry.subject_kind, entry.subject, term.sanskrit), None)
    return tuple(
        TermTags(
            subject_kind=kind,  # type: ignore[arg-type]
            subject=subject,
            sanskrit=sanskrit,
            tags=(DomainTag(domain=JyotishDomain.CAREER, status="reviewed"),),
        )
        for kind, subject, sanskrit in keys
    )


def _corpus_version(manifest_id: str, manifest_version: str) -> str:
    return f"{manifest_id}@{manifest_version}"


SIGNIFICATION_TAG_SET_V1: Final = SignificationTagSet(
    tag_set_id="jyotish.signification.domain-tags",
    tag_set_version="v1",
    covers_corpora=tuple(
        _corpus_version(m.manifest_id, m.manifest_version)
        for m in (
            SIGNIFICATION_MANIFEST_V1,
            PRODUCTION_SIGNIFICATION_MANIFEST,
            PRODUCTION_SIGNIFICATION_MANIFEST_V3,
        )
    ),
    basis=(
        "Every reviewed term was the review packet's 'Proposed for Career' column (packet 0b) "
        "and was admitted for Career (docs/admissions/jyotish.signification.part0b."
        "admission.v1.md; the Sitting 2 glosses: docs/admissions/jyotish.admit02.sitting-1-2."
        "admission.v1.md). No reviewed term has been reviewed for another domain, so each "
        "carries Career (reviewed) only. Tagging adds no term and changes no wording."
    ),
    terms=_career_reviewed(
        SIGNIFICATION_MANIFEST_V1.entries,
        PRODUCTION_SIGNIFICATION_MANIFEST.entries,
        PRODUCTION_SIGNIFICATION_MANIFEST_V3.entries,
    ),
)
ACTIVE_SIGNIFICATION_TAG_SET: Final = SIGNIFICATION_TAG_SET_V1
