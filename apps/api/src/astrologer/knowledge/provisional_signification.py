"""NEXT-MARRIAGE-02: provisional signification terms (corpus ``jyotish.provisional.signification``).

A provisional signification is one graha or bhava term drafted from the text for a domain,
with the same justification record as a provisional rule (source, locator, original text read
from the page image, draft translation, reasoning, conventions, confidence, author).  It is
never part of a reviewed signification corpus, never quoted in reviewed answer text, and is
shown only with ``include_provisional`` (the "Show provisional interpretations (beta)"
toggle), badged with the author's confidence.  Its domain tags are on its own record and are
always ``provisional``; it becomes reviewed only through a future reviewed signification
corpus admitted with a human review record (an AI agent is never the reviewer).

Corpus v1: three Marriage terms, drafted by an AI agent, owner adoption pending.  Source: the
selected BPHS edition (``bphs.selected-edition@v1``), read from the local page images.  Only
terms the text gives are used; "marriage" and "partnership" are not drafted because the
verses do not name them.

* 7th house: जाया ("spouse"), द्वादशभावविचाराध्यायः v.7, PDF p. 147; high.
* Venus: कलत्र ("spouse"), Venus as its kāraka, सूर्यादिग्रहाणां कारकत्वम् v.6, PDF p. 109;
  corroborated by the bhāva-kāraka list (v.37, PDF p. 108: सितः for the 7th) and v.33
  (PDF p. 107: from Venus, the 7th for the wife); high.
* 2nd house: कुटुम्ब ("family"), द्वादशभावविचाराध्यायः v.2, PDF p. 146; low (the verse names
  family but no marriage clause; reading it for marriage questions is the author's step).

Corpus v2 (NEXT-WEALTH-01): the 7th-house and Venus terms unchanged; कुटुम्ब is no longer a
Marriage term (term v2, tag Wealth (provisional): the verse is the 2nd house, the house of
wealth, and names no spouse; the v.35/v.36 conflict is a question in the review pack); and
three Wealth terms, drafted only where the verse names wealth or gain:

* 2nd house: धन ("wealth"), द्वादशभावविचाराध्यायः v.2, PDF p. 146; high.
* 11th house: लाभ ("gain"), द्वादशभावविचाराध्यायः v.11, PDF p. 148; high.
* Jupiter: धन ("wealth (kāraka)"), सूर्यादिग्रहाणां कारकत्वम् v.5, PDF p. 109; corroborated by
  the bhāva-kāraka list (v.37, PDF p. 108: गुरुः for the 2nd and the 11th); high.

The reviewed Career terms of the same houses (धन; लाभ, वृद्धि) stay Career only (a reviewer
may tag them Wealth; the review pack asks).  A Wealth term's verse also lists matters of other
domains or death, so its translation stays in the review pack (``translation_held_reason``).

Corpus v4 (NEXT-CHILDREN-GUARD-01): the v3 terms, with record v2 of the six terms whose
displayed record named sons or quoted पुत्र (Venus कलत्र, 11th-house लाभ, Jupiter धन and गृह,
Mars भूमि and सद्म): the पुत्र gloss "children (the text says 'son')" and its convention.

Corpus v5 (NEXT-CHILDREN-01): the v4 terms unchanged, plus progeny terms for Children (each
shown with the पुत्र gloss "children (the text says 'son')") and the 5th house's learning and
intellect terms for Education; every translation stays in the review pack:

* 5th house: पुत्र (Children), द्वादशभावविचाराध्यायः v.5, PDF p. 147, corroborated by
  अथ भावकारकमाह v.36 (PDF p. 108); high.
* Jupiter: पुत्र kāraka (Children), सूर्यादिग्रहाणां कारकत्वम् v.5, PDF p. 109, corroborated by
  the fixed-kāraka verses vv. 30 and 33 (PDF p. 107) and the bhāva-kāraka list v.37 (PDF
  p. 108); high.
* 5th house: विद्या "learning" and बुद्धि "intellect" (Education), v.5, PDF p. 147; high.  The
  reviewed Career terms of the same words stay Career only (a reviewer may tag them Education).

Corpus v3 (NEXT-PROPERTY-01): the v2 terms unchanged, plus eight Property terms, drafted only
where the verse names land, a house or vehicles; every translation stays in the review pack:

* 4th house: गृह ("house or home"), क्षेत्र ("fields or land"), वाहन ("vehicles"),
  द्वादशभावविचाराध्यायः v.4, PDF p. 147; high.  बन्धु, मातृसौख्य and निधि (relatives, the
  mother's happiness, treasure) are not property terms and are not drafted.
* Mars: भूमि ("land (kāraka)"), high, and सद्म ("dwelling (kāraka)"), medium (the Hindi does
  not render it), सूर्यादिग्रहाणां कारकत्वम् v.3, PDF p. 109.
* Jupiter: गृह ("house (kāraka)"), v.5, PDF p. 109; high.
* Venus: यान ("vehicles (kāraka)"), v.6, PDF p. 109; high.
* Sun: क्षेत्र ("fields or land (kāraka)"), v.1, PDF p. 109; medium (may mean a region).
"""

import re
from datetime import UTC, datetime
from typing import Final

from pydantic import BaseModel, ConfigDict, Field, model_validator

from astrologer.composition.children_domain_guard import children_domain_violation
from astrologer.composition.children_guard import (
    PUTRA_CONVENTION,
    PUTRA_GLOSS,
    child_wording_violation,
)
from astrologer.composition.comparison_guard import ranking_violation
from astrologer.composition.evaluative_guard import evaluative_violation
from astrologer.composition.marriage_guard import marriage_wording_violation
from astrologer.composition.property_guard import property_wording_violation
from astrologer.composition.wealth_guard import wealth_wording_violation
from astrologer.knowledge.models import JyotishDomain
from astrologer.knowledge.provisional import (
    PROVISIONAL_AUTHOR_AI_DRAFTED,
    ProvisionalConfidence,
    ProvisionalJustification,
)
from astrologer.knowledge.provisional_pack_v1 import _SOURCE_WORK
from astrologer.knowledge.signification import SubjectKind, term_violation
from astrologer.knowledge.signification_tags import DomainTag

PROVISIONAL_SIGNIFICATION_PREFIX: Final = "provisional.signification."
_REVIEWED_LABEL: Final = re.compile(
    r"\b(?:reviewed|approved|admitted|certified|verified)\b", re.IGNORECASE
)
_GRAHAS: Final = frozenset(
    {"sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"}
)


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ProvisionalSignification(_Frozen):
    """One provisional term of one graha or bhava, with its justification and tags."""

    tier: str = Field(default="provisional", pattern=r"^provisional$")
    term_id: str = Field(pattern=r"^[a-z][a-z0-9_.-]{0,127}$")
    term_version: str = Field(min_length=1, max_length=32)
    subject_kind: SubjectKind
    subject: str = Field(min_length=1, max_length=16)
    sanskrit: str = Field(min_length=1, max_length=128)
    display: str = Field(min_length=1, max_length=64)
    tags: tuple[DomainTag, ...] = Field(min_length=1)
    statement: str = Field(min_length=1, max_length=1000)
    justification: ProvisionalJustification
    # Set when the verse's other clauses (e.g. death) should not reach a marriage answer: the
    # app then shows the held notice for the translation; the review pack keeps it in full.
    translation_held_reason: str | None = Field(default=None, min_length=1, max_length=1000)

    @model_validator(mode="after")
    def term_is_admissible(self) -> "ProvisionalSignification":
        if (violation := provisional_signification_violation(self)) is not None:
            raise ValueError(violation)
        return self

    @property
    def domains(self) -> frozenset[JyotishDomain]:
        return frozenset(tag.domain for tag in self.tags)


def provisional_signification_violation(term: ProvisionalSignification) -> str | None:
    """Why ``term`` cannot enter a provisional signification corpus, or None."""
    if not term.term_id.startswith(PROVISIONAL_SIGNIFICATION_PREFIX):
        return f"provisional signification ids start with {PROVISIONAL_SIGNIFICATION_PREFIX!r}"
    if term.subject_kind == "graha" and term.subject not in _GRAHAS:
        return f"unknown graha: {term.subject}"
    if term.subject_kind == "bhava" and term.subject not in {str(n) for n in range(1, 13)}:
        return f"unknown bhava: {term.subject}"
    if any(tag.status != "provisional" for tag in term.tags):
        return "a provisional signification carries provisional tags only"
    if len({tag.domain for tag in term.tags}) != len(term.tags):
        return "duplicate domain tag"
    if (bad := term_violation(term.display)) is not None:
        return f"display has a forbidden word: {bad!r}"
    for text in (term.statement, term.display):
        if (bad := ranking_violation(text) or evaluative_violation(text)) is not None:
            return f"fails the ranking/evaluative guard: {bad!r}"
        if (bad := marriage_wording_violation(text)) is not None:
            return f"fails the marriage wording guard: {bad!r}"
        if (bad := wealth_wording_violation(text)) is not None:
            return f"fails the wealth wording guard: {bad!r}"
        if (bad := property_wording_violation(text)) is not None:
            return f"fails the property wording guard: {bad!r}"
        if (bad := children_domain_violation(text)) is not None:
            return f"fails the children domain guard: {bad!r}"
        # NEXT-CHILDREN-GUARD-01: no child-sex hint, no childlessness or loss wording.
        if (bad := child_wording_violation(text)) is not None:
            return f"fails the children wording guard: {bad!r}"
        if (label := _REVIEWED_LABEL.search(text)) is not None:
            return f"may not present itself as reviewed: {label.group()!r}"
    if term.sanskrit not in term.statement:
        return "the statement quotes the Sanskrit term"
    return None


class ProvisionalSignificationCorpus(_Frozen):
    corpus_id: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$")
    corpus_version: str = Field(min_length=1, max_length=64)
    terms: tuple[ProvisionalSignification, ...] = ()

    @model_validator(mode="after")
    def ids_are_unique(self) -> "ProvisionalSignificationCorpus":
        ids = [term.term_id for term in self.terms]
        if len(ids) != len(set(ids)):
            raise ValueError("provisional signification ids must be unique")
        return self

    @property
    def release_id(self) -> str:
        return f"{self.corpus_id}@{self.corpus_version}"

    def for_domain(self, domain: str) -> tuple[ProvisionalSignification, ...]:
        return tuple(term for term in self.terms if domain in {d.value for d in term.domains})


_RECORDED_AT: Final = datetime(2026, 11, 26, tzinfo=UTC)
_HELD_OTHER_CLAUSES: Final = (
    "The verse's other clauses include death, which is not a marriage term; the full "
    "translation is kept for the expert review and is not shown in a marriage answer."
)
_MARRIAGE_TAG: Final = (DomainTag(domain=JyotishDomain.MARRIAGE, status="provisional"),)
_CH12: Final = "द्वादशभावविचाराध्यायः (अथ द्वादशभावेषु विचार्यत्वमाह)"
_KARAKA: Final = "कारकाध्यायः, अथ सूर्यादिग्रहाणां कारकत्वमाह"
_CONVENTIONS: Final = (
    "Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).",
    "Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 "
    "item 20).",
    "The verses address a male native (जाया, कलत्र, स्त्री: wife); the display says 'spouse'. "
    "Whether the term applies unchanged to every chart is for the expert review.",
    "A signification term names a theme only: no polarity, weight, timing or prediction. "
    "Domain tag: Marriage (provisional).",
)

SEVENTH_HOUSE_SPOUSE: Final = ProvisionalSignification(
    term_id="provisional.signification.bhava.7.jaya",
    term_version="v1",
    subject_kind="bhava",
    subject="7",
    sanskrit="जाया",
    display="spouse",
    tags=_MARRIAGE_TAG,
    statement="The text lists the spouse (जाया) among the matters judged from the 7th house.",
    justification=ProvisionalJustification(
        source_work=_SOURCE_WORK,
        locator=f"{_CH12}, verse 7; PDF p. 147 (printed p. 149).",
        original_text=("जायामध्वप्रयाणं च व्यापारं हतवीक्षणम् । मरणं च स्वदेहस्य जायाभावान्निरीक्षयेत् ॥ ७ ॥"),
        draft_translation=(
            "From the house of the wife (the seventh), one should examine the wife, journeys "
            "on the road, trade, lost things, and the death of one's own body. [Hindi: सप्तम "
            "भाव से स्त्री, मार्ग, यात्रा, व्यापार, नष्ट वस्तु और मृत्यु का विचार करना चाहिए।]"
        ),
        interpretive_reasoning=(
            "The verse names जाया (wife) first among the seventh house's matters and calls the "
            "seventh 'the house of the wife' (जायाभाव). Only that term is drafted for Marriage. "
            "व्यापार (trade) is already a Career signification term and stays Career only; "
            "journeys, lost things and death are not marriage terms and are not drafted. "
            "'Marriage' and "
            "'partnership' are not in the verse and are not used. Corroboration: the kāraka "
            "chapter v.36 (PDF p. 108) gives दारा (wife) from the seventh house."
        ),
        conventions=_CONVENTIONS,
        confidence=ProvisionalConfidence.HIGH,
        author=PROVISIONAL_AUTHOR_AI_DRAFTED,
        recorded_at=_RECORDED_AT,
        transcription_notes=(
            "Read from the page image. The PDF text layer agrees on the first line and reads "
            "जायाभावात्निरीक्षयेत् for the printed जायाभावान्निरीक्षयेत्. The Sanskrit and the "
            "edition's Hindi agree."
        ),
    ),
    translation_held_reason=_HELD_OTHER_CLAUSES,
)

VENUS_KARAKA_SPOUSE: Final = ProvisionalSignification(
    term_id="provisional.signification.graha.venus.kalatra",
    term_version="v1",
    subject_kind="graha",
    subject="venus",
    sanskrit="कलत्र",
    display="spouse (kāraka)",
    tags=_MARRIAGE_TAG,
    statement="The text names Venus the kāraka (significator) of the spouse (कलत्र).",
    justification=ProvisionalJustification(
        source_work=_SOURCE_WORK,
        locator=(
            f"{_KARAKA}, verse 6; PDF p. 109 (printed p. 111). Corroboration: अथ भावकारकमाह "
            "v.37, PDF p. 108 (printed p. 110); अथ स्थिरकारकमाह v.33, PDF p. 107 (printed p. 109)."
        ),
        original_text=(
            "कलत्रकार्मुकसुखगीतशास्त्रकाव्यपुष्पसुकुमारयौवनाभरणरजतयानस्वर्गलोकमौक्तिक"
            "विभवकवितारसादिकारको भृगुः ॥ ६ ॥ | v.37: सूर्यो गुरुः कुजः सोमो गुरुर्भौमः सितः "
            "शनिः । गुरुश्चन्द्रसुतो जीवो मन्दश्च भावकारकः ॥ ३७ ॥ | v.33: देवेज्यात्पञ्चमे पुत्रो "
            "दैत्येज्याद्द्यूनभे स्त्रियः । मन्दादष्टमतो मृत्युस्तातादीनां विचिन्तयेत् ॥ ३३ ॥"
        ),
        draft_translation=(
            "v.6: Bhṛgu (Venus) is the kāraka of the wife (कलत्र), the bow, happiness, music, "
            "poetry, flowers, youth, ornaments, silver, vehicles, … [Hindi: स्त्री, धनुष, सुख, "
            "गीतशास्त्र … के कारक शुक्र हैं।] v.37: the kārakas of the houses from the Lagna "
            "are, in order, Sun, Jupiter, Mars, Moon (Hindi: Mercury), Jupiter, Mars, Venus "
            "(सितः, the seventh), Saturn, Jupiter, Mercury, Jupiter, Saturn. v.33: from Venus "
            "(दैत्येज्य), the seventh house is examined for the wife."
        ),
        interpretive_reasoning=(
            "Three verses agree that Venus signifies the wife: it is named कलत्रकारक in its own "
            "kāraka list (v.6), it is the bhāva-kāraka of the seventh house (v.37), and the "
            "seventh from Venus is examined for the wife (v.33). Only कलत्र is drafted for "
            "Marriage; the other Venus terms of v.6 are not marriage terms. The Career "
            "signification term of Venus (सचिवः, 'adviser or counsellor') stays Career only."
        ),
        conventions=_CONVENTIONS,
        confidence=ProvisionalConfidence.HIGH,
        author=PROVISIONAL_AUTHOR_AI_DRAFTED,
        recorded_at=_RECORDED_AT,
        transcription_notes=(
            "Read from the page images. The PDF text layer garbles v.6 (कामुक for कार्मुक, भगः "
            "for भृगुः) and v.37 (सूयां गृरुः for सूर्यो गुरुः). In v.37 the Sanskrit's fourth "
            "kāraka is सोमः (Moon) while the Hindi gives बुध (Mercury); this does not affect the "
            "seventh (सितः, Venus), on which both agree."
        ),
    ),
)

SECOND_HOUSE_FAMILY: Final = ProvisionalSignification(
    term_id="provisional.signification.bhava.2.kutumba",
    term_version="v1",
    subject_kind="bhava",
    subject="2",
    sanskrit="कुटुम्ब",
    display="family",
    tags=_MARRIAGE_TAG,
    statement=(
        "The text lists family (कुटुम्ब) among the matters judged from the 2nd house; the "
        "verse does not mention a spouse, so its use for marriage questions is tentative."
    ),
    justification=ProvisionalJustification(
        source_work=_SOURCE_WORK,
        locator=f"{_CH12}, verse 2; PDF p. 146 (printed p. 148).",
        original_text=("धनं धान्यं कुटुम्बं च मृत्युजालममित्रकम् । धातुरत्नादिकं सर्वं धनस्थानाद्विचारयेत् ॥ २ ॥"),
        draft_translation=(
            "From the house of wealth (the second), one should consider wealth, grain, family, "
            "the net of death, enemies, and metals, gems and the like. [Hindi (PDF p. 147): "
            "दूसरे भाव में धन, धान्य, कुटुंब, मृत्यु, शत्रु का और धातु, रत्न आदि का विचार करना "
            "चाहिए।]"
        ),
        interpretive_reasoning=(
            "The verse gives कुटुम्ब (family, household) as a second-house matter. It does not "
            "mention marriage or a spouse; reading 'family' for a marriage question is the "
            "author's step, hence low confidence. The kāraka chapter v.35 (PDF p. 108) calls "
            "the second house दारकारक (kāraka of the wife), but v.36 on the same page takes "
            "दारा from the seventh house; that conflict is not resolved here and v.35 is not "
            "used. Only कुटुम्ब is drafted; धन (wealth) is already a Career signification term."
        ),
        conventions=_CONVENTIONS,
        confidence=ProvisionalConfidence.LOW,
        author=PROVISIONAL_AUTHOR_AI_DRAFTED,
        recorded_at=_RECORDED_AT,
        transcription_notes=(
            "Read from the page image (Sanskrit at the foot of PDF p. 146, Hindi at the top of "
            "PDF p. 147). The PDF text layer agrees. The Sanskrit and the Hindi agree."
        ),
    ),
    translation_held_reason=_HELD_OTHER_CLAUSES,
)

PROVISIONAL_SIGNIFICATION_CORPUS_V1: Final = ProvisionalSignificationCorpus(
    corpus_id="jyotish.provisional.signification",
    corpus_version="v1",
    terms=(SEVENTH_HOUSE_SPOUSE, VENUS_KARAKA_SPOUSE, SECOND_HOUSE_FAMILY),
)

# --- Corpus v2 (NEXT-WEALTH-01) -----------------------------------------------------------

_RECORDED_AT_V2: Final = datetime(2026, 11, 26, 12, tzinfo=UTC)
_WEALTH_TAG: Final = (DomainTag(domain=JyotishDomain.WEALTH, status="provisional"),)
_WEALTH_CONVENTIONS: Final = (
    "Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).",
    "Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 "
    "item 20).",
    "A signification term names a theme only: no polarity, weight, timing, amount or "
    "prediction. Domain tag: Wealth (provisional).",
    "Drafted only where the verse names wealth or gain (धन, लाभ); a Career-tagged term of "
    "the same word stays Career only until a reviewer tags it.",
)
_WEALTH_HELD_OTHER: Final = (
    "The verse's other matters are not wealth terms (they include {matters}); the full "
    "translation is kept for the expert review and is not shown in a wealth answer."
)
_V2_ORIGINAL: Final = SECOND_HOUSE_FAMILY.justification.original_text
_V2_TRANSLATION: Final = SECOND_HOUSE_FAMILY.justification.draft_translation
_V2_LOCATOR: Final = SECOND_HOUSE_FAMILY.justification.locator
_V2_NOTES: Final = SECOND_HOUSE_FAMILY.justification.transcription_notes

SECOND_HOUSE_FAMILY_V2: Final = ProvisionalSignification(
    term_id="provisional.signification.bhava.2.kutumba",
    term_version="v2",
    subject_kind="bhava",
    subject="2",
    sanskrit="कुटुम्ब",
    display="family",
    tags=_WEALTH_TAG,
    statement=(
        "The text lists family (कुटुम्ब) among the matters judged from the 2nd house, which "
        "it calls the house of wealth (धनस्थान)."
    ),
    justification=ProvisionalJustification(
        source_work=_SOURCE_WORK,
        locator=_V2_LOCATOR,
        original_text=_V2_ORIGINAL,
        draft_translation=_V2_TRANSLATION,
        interpretive_reasoning=(
            "Owner instruction (NEXT-WEALTH-01): कुटुम्ब is no longer drafted for Marriage; the "
            "verse names no spouse. It is tagged Wealth (provisional) because the verse judges "
            "it from धनस्थान, the house of wealth, next to धन and धान्य. कुटुम्ब (family, "
            "household) is not itself wealth, so confidence stays low; the expert review "
            "decides whether it belongs to Wealth, to another domain, or to none. The kāraka "
            "chapter v.35 (PDF p. 108) calls the second house दारकारक (kāraka of the wife) while "
            "v.36 on the same page takes दारा from the seventh house; that conflict is a "
            "question for the reviewer in the review pack and is not used here."
        ),
        conventions=_WEALTH_CONVENTIONS,
        confidence=ProvisionalConfidence.LOW,
        author=PROVISIONAL_AUTHOR_AI_DRAFTED,
        recorded_at=_RECORDED_AT_V2,
        transcription_notes=_V2_NOTES,
    ),
    translation_held_reason=_WEALTH_HELD_OTHER.format(matters="death and enemies"),
)

SECOND_HOUSE_WEALTH: Final = ProvisionalSignification(
    term_id="provisional.signification.bhava.2.dhana",
    term_version="v1",
    subject_kind="bhava",
    subject="2",
    sanskrit="धन",
    display="wealth",
    tags=_WEALTH_TAG,
    statement=(
        "The text lists wealth (धन) first among the matters judged from the 2nd house, which "
        "it calls the house of wealth (धनस्थान)."
    ),
    justification=ProvisionalJustification(
        source_work=_SOURCE_WORK,
        locator=_V2_LOCATOR,
        original_text=_V2_ORIGINAL,
        draft_translation=_V2_TRANSLATION,
        interpretive_reasoning=(
            "The verse opens with धनं (wealth) and closes with धनस्थानाद्विचारयेत् (judge from "
            "the house of wealth), so the second house's wealth term is explicit. Only धन is "
            "drafted. धान्य (grain) and धातुरत्नादि (metals, gems and the like) are possessions "
            "the expert review may add; कुटुम्ब is drafted separately (low). मृत्युजाल (the net "
            "of death) and अमित्र (enemies) are not wealth terms and are not drafted. The "
            "Career-tagged signification term of the second house is also धन ('wealth'), "
            "tagged for Career only; this provisional Wealth record does not change it."
        ),
        conventions=_WEALTH_CONVENTIONS,
        confidence=ProvisionalConfidence.HIGH,
        author=PROVISIONAL_AUTHOR_AI_DRAFTED,
        recorded_at=_RECORDED_AT_V2,
        transcription_notes=_V2_NOTES,
    ),
    translation_held_reason=_WEALTH_HELD_OTHER.format(matters="death and enemies"),
)

ELEVENTH_HOUSE_GAIN: Final = ProvisionalSignification(
    term_id="provisional.signification.bhava.11.labha",
    term_version="v1",
    subject_kind="bhava",
    subject="11",
    sanskrit="लाभ",
    display="gain",
    tags=_WEALTH_TAG,
    statement="The text lists gain (लाभ) among the matters judged from the 11th house.",
    justification=ProvisionalJustification(
        source_work=_SOURCE_WORK,
        locator=f"{_CH12}, verse 11; PDF p. 148 (printed p. 150).",
        original_text=("नानावस्तुभवस्यापि पुत्रजायादिकस्य च । लाभवृद्धिपशूनां च भवस्थानाद्विचारयेत् ॥ ११ ॥"),
        draft_translation=(
            "From the house of gains (भव, the eleventh), one should consider the acquisition "
            "of various things, sons, wife and the like, gain, and the increase of livestock. "
            "[Hindi: एकादश भाव से अनेक वस्तुओं की प्राप्ति, पुत्र, स्त्री, पशुओं की वृद्धि तथा "
            "लाभ आदि का विचार करना चाहिए।]"
        ),
        interpretive_reasoning=(
            "The verse names लाभ (gain) among the eleventh house's matters; नानावस्तुभव (the "
            "acquisition of various things) points the same way and is left for the expert "
            "review. Only लाभ is drafted. वृद्धि is read with पशूनां (the increase of livestock), "
            "as the edition's Hindi does, and is not drafted. पुत्र and जाया (sons, wife) are "
            "Children and Marriage matters, not wealth terms. The Career-tagged terms of the "
            "eleventh house (लाभ 'gain', वृद्धि 'increase') stay Career only."
        ),
        conventions=_WEALTH_CONVENTIONS,
        confidence=ProvisionalConfidence.HIGH,
        author=PROVISIONAL_AUTHOR_AI_DRAFTED,
        recorded_at=_RECORDED_AT_V2,
        transcription_notes=(
            "Read from the page image (PDF p. 148, printed p. 150). The PDF text layer agrees "
            "except for the verse number (९९ for ११). The Sanskrit and the Hindi agree."
        ),
    ),
    translation_held_reason=_WEALTH_HELD_OTHER.format(matters="sons, wife and livestock"),
)

JUPITER_KARAKA_WEALTH: Final = ProvisionalSignification(
    term_id="provisional.signification.graha.jupiter.dhana",
    term_version="v1",
    subject_kind="graha",
    subject="jupiter",
    sanskrit="धन",
    display="wealth (kāraka)",
    tags=_WEALTH_TAG,
    statement="The text names Jupiter a kāraka (significator) of wealth (धन).",
    justification=ProvisionalJustification(
        source_work=_SOURCE_WORK,
        locator=(
            f"{_KARAKA}, verse 5; PDF p. 109 (printed p. 111). Corroboration: अथ भावकारकमाह "
            "v.37, PDF p. 108 (printed p. 110)."
        ),
        original_text=(
            "स्वकर्मयजनदेवब्राह्मणधनगृहकाञ्चनवस्त्रपुत्रमित्रान्दोलनादिकारको गुरुः ॥ ५ ॥ | v.37: "
            "सूर्यो गुरुः कुजः सोमो गुरुर्भौमः सितः शनिः । गुरुश्चन्द्रसुतो जीवो मन्दश्च "
            "भावकारकः ॥ ३७ ॥"
        ),
        draft_translation=(
            "v.5: Guru (Jupiter) is the kāraka of one's own work, sacrifice, the gods, "
            "brāhmaṇas, wealth (धन), house, gold, cloth, sons, friends, swings and the like. "
            "[Hindi: अपने कार्य, यज्ञ, देवता, ब्राह्मण, धन, गृह, सुवर्ण, वस्त्र, पुत्र, मित्र, "
            "आंदोलन आदि के कारक गुरु हैं।] v.37: the kārakas of the houses from the Lagna are, "
            "in order, Sun, Jupiter (the second), Mars, Moon (Hindi: Mercury), Jupiter, Mars, "
            "Venus, Saturn, Jupiter, Mercury, Jupiter (the eleventh), Saturn."
        ),
        interpretive_reasoning=(
            "Jupiter's own kāraka list (v.5) names धन (wealth) and काञ्चन (gold); the "
            "bhāva-kāraka list (v.37) makes Jupiter the kāraka of the second and the eleventh "
            "houses, the two Wealth houses. Only धन is drafted. स्वकर्म (one's own work) is "
            "closer to Career, पुत्र to Children; they are not drafted for Wealth. The Career-tagged "
            "Career terms of Jupiter (ज्ञानम्, सचिवः) stay Career only."
        ),
        conventions=_WEALTH_CONVENTIONS,
        confidence=ProvisionalConfidence.HIGH,
        author=PROVISIONAL_AUTHOR_AI_DRAFTED,
        recorded_at=_RECORDED_AT_V2,
        transcription_notes=(
            "Read from the page images. The PDF text layer breaks v.5 at काञ्चन (a line break, "
            "no letter lost) and garbles v.37 (सूयां गृरुः for सूर्यो गुरुः). In v.37 the "
            "Sanskrit's fourth kāraka is सोमः (Moon) while the Hindi gives बुध (Mercury); the "
            "second and eleventh (गुरुः) agree in both."
        ),
    ),
    translation_held_reason=_WEALTH_HELD_OTHER.format(matters="one's own work, sons and friends"),
)

PROVISIONAL_SIGNIFICATION_CORPUS_V2: Final = ProvisionalSignificationCorpus(
    corpus_id="jyotish.provisional.signification",
    corpus_version="v2",
    terms=(
        SEVENTH_HOUSE_SPOUSE,
        VENUS_KARAKA_SPOUSE,
        SECOND_HOUSE_WEALTH,
        SECOND_HOUSE_FAMILY_V2,
        ELEVENTH_HOUSE_GAIN,
        JUPITER_KARAKA_WEALTH,
    ),
)

# --- Corpus v3 (NEXT-PROPERTY-01) ---------------------------------------------------------

_RECORDED_AT_V3: Final = datetime(2026, 11, 26, 18, tzinfo=UTC)
_PROPERTY_TAG: Final = (DomainTag(domain=JyotishDomain.PROPERTY, status="provisional"),)
_PROPERTY_CONVENTIONS: Final = (
    "Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).",
    "Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 "
    "item 20).",
    "A signification term names a theme only: no polarity, weight, timing, price or "
    "prediction. Domain tag: Property (provisional).",
    "Drafted only where the verse names land, a house or vehicles (भूमि, क्षेत्र, गृह, सद्म, "
    "वाहन, यान); the verse's other matters are not drafted for Property.",
)
_PROPERTY_HELD_OTHER: Final = (
    "The verse's other matters are not property terms (they include {matters}); the full "
    "translation is kept for the expert review and is not shown in a property answer."
)
_V4_LOCATOR: Final = f"{_CH12}, verse 4; PDF p. 147 (printed p. 149)."
_V4_ORIGINAL: Final = "वाहनस्याथ बन्धूनां मातृसौख्यादिकानपि । निधिक्षेत्रं गृहं चापि पातालाच्च निरीक्षयेत् ॥ ४ ॥"
_V4_TRANSLATION: Final = (
    "From the fourth house (पाताल), one should examine vehicles, relatives, the happiness of "
    "the mother and the like, treasure, fields (land) and the house. [Hindi: चौथे भाव से वाहन "
    "(सवारी) का, बंधुओं का, मातृसुख का, निधि (गड़े धन) का, क्षेत्र (खेत) तथा गृह का विचार करना "
    "चाहिए।]"
)
_V4_NOTES: Final = (
    "Read from the page image (PDF p. 147, printed p. 149). The PDF text layer agrees. The "
    "Sanskrit and the edition's Hindi agree."
)
_V4_HELD: Final = _PROPERTY_HELD_OTHER.format(
    matters="relatives, the mother's happiness and treasure"
)
_V4_NOT_DRAFTED: Final = (
    " बन्धु (relatives) and मातृसौख्य (the mother's happiness) are not property terms and "
    "are not tagged Property (JyotAI has no relatives, mother or happiness domain); निधि "
    "(treasure; Hindi: buried wealth) is a wealth matter and is not drafted."
)


def _fourth_house_term(
    sanskrit: str, slug: str, display: str, statement: str, reasoning: str
) -> ProvisionalSignification:
    return ProvisionalSignification(
        term_id=f"provisional.signification.bhava.4.{slug}",
        term_version="v1",
        subject_kind="bhava",
        subject="4",
        sanskrit=sanskrit,
        display=display,
        tags=_PROPERTY_TAG,
        statement=statement,
        justification=ProvisionalJustification(
            source_work=_SOURCE_WORK,
            locator=_V4_LOCATOR,
            original_text=_V4_ORIGINAL,
            draft_translation=_V4_TRANSLATION,
            interpretive_reasoning=reasoning + _V4_NOT_DRAFTED,
            conventions=_PROPERTY_CONVENTIONS,
            confidence=ProvisionalConfidence.HIGH,
            author=PROVISIONAL_AUTHOR_AI_DRAFTED,
            recorded_at=_RECORDED_AT_V3,
            transcription_notes=_V4_NOTES,
        ),
        translation_held_reason=_V4_HELD,
    )


FOURTH_HOUSE_HOUSE: Final = _fourth_house_term(
    "गृह",
    "griha",
    "house or home",
    "The text lists the house or home (गृह) among the matters judged from the 4th house.",
    "The verse names गृह (house, home) among the fourth house's matters, and the edition's "
    "Hindi keeps गृह. Only that term is drafted here.",
)
FOURTH_HOUSE_LAND: Final = _fourth_house_term(
    "क्षेत्र",
    "kshetra",
    "fields or land",
    "The text lists fields or land (क्षेत्र) among the matters judged from the 4th house.",
    "The verse names क्षेत्र (in the compound निधिक्षेत्रं), which the edition's Hindi glosses "
    "as खेत (field, farmland); 'fields or land' is displayed.",
)
FOURTH_HOUSE_VEHICLES: Final = _fourth_house_term(
    "वाहन",
    "vahana",
    "vehicles",
    "The text lists vehicles (वाहन) first among the matters judged from the 4th house.",
    "The verse opens with वाहन (vehicle, conveyance), which the edition's Hindi glosses as "
    "सवारी (a ride, conveyance); 'vehicles' is displayed.",
)

_V3_MARS_ORIGINAL: Final = "सत्त्वसद्मभूमिपुत्रशीलचौर्यरोगब्रह्मभ्रातृपराक्रमाग्निसाहसराजशत्रुकारकः कुजः ॥ ३ ॥"
_V3_MARS_TRANSLATION: Final = (
    "Kuja (Mars) is the kāraka of strength, the dwelling (सद्म), land (भूमि), sons, conduct, "
    "theft, disease, ब्रह्म (left untranslated; the Hindi keeps ब्रह्म), brothers, valour, "
    "fire, daring and the king's enemies. "
    "[Hindi: ओज, भूमि, पुत्र, शील, चोर, रोग, ब्रह्म, भाई, पराक्रम, अग्नि, साहस और राजशत्रु के "
    "कारक भौम हैं।]"
)
_V3_MARS_NOTES: Final = (
    "Read from the page image (PDF p. 109, printed p. 111). The PDF text layer reads "
    "सत्वसद्म… चौयरोगत्रर्मश्रात् for सत्त्वसद्म… चौर्यरोगब्रह्मभ्रातृ. The edition's Hindi renders "
    "सत्त्व as ओज and does not render सद्म; it keeps भूमि."
)
_MARS_HELD: Final = _PROPERTY_HELD_OTHER.format(
    matters="disease, theft, sons, brothers and the king's enemies"
)

MARS_KARAKA_LAND: Final = ProvisionalSignification(
    term_id="provisional.signification.graha.mars.bhumi",
    term_version="v1",
    subject_kind="graha",
    subject="mars",
    sanskrit="भूमि",
    display="land (kāraka)",
    tags=_PROPERTY_TAG,
    statement="The text names Mars a kāraka (significator) of land (भूमि).",
    justification=ProvisionalJustification(
        source_work=_SOURCE_WORK,
        locator=f"{_KARAKA}, verse 3; PDF p. 109 (printed p. 111).",
        original_text=_V3_MARS_ORIGINAL,
        draft_translation=_V3_MARS_TRANSLATION,
        interpretive_reasoning=(
            "Mars's own kāraka list names भूमि (land), and the edition's Hindi keeps भूमि. Only "
            "भूमि is drafted in this record; सद्म (dwelling) is a separate record. The other "
            "Mars terms (strength, sons, conduct, theft, disease, brothers, valour, fire, "
            "daring, the king's enemies) are not property terms and are not drafted."
        ),
        conventions=_PROPERTY_CONVENTIONS,
        confidence=ProvisionalConfidence.HIGH,
        author=PROVISIONAL_AUTHOR_AI_DRAFTED,
        recorded_at=_RECORDED_AT_V3,
        transcription_notes=_V3_MARS_NOTES,
    ),
    translation_held_reason=_MARS_HELD,
)

MARS_KARAKA_DWELLING: Final = ProvisionalSignification(
    term_id="provisional.signification.graha.mars.sadma",
    term_version="v1",
    subject_kind="graha",
    subject="mars",
    sanskrit="सद्म",
    display="dwelling (kāraka)",
    tags=_PROPERTY_TAG,
    statement=(
        "The text names Mars a kāraka (significator) of the dwelling (सद्म); the edition's "
        "Hindi does not render the word, so the reading is tentative."
    ),
    justification=ProvisionalJustification(
        source_work=_SOURCE_WORK,
        locator=f"{_KARAKA}, verse 3; PDF p. 109 (printed p. 111).",
        original_text=_V3_MARS_ORIGINAL,
        draft_translation=_V3_MARS_TRANSLATION,
        interpretive_reasoning=(
            "The list opens सत्त्वसद्म…; read as separate members of the compound, सद्म is a "
            "dwelling or house. Confidence is medium: the edition's Hindi renders सत्त्व as ओज "
            "and gives no word for सद्म, and सत्त्वसद्म could also be read together ('abode of "
            "strength'). Only सद्म is drafted in this record."
        ),
        conventions=_PROPERTY_CONVENTIONS,
        confidence=ProvisionalConfidence.MEDIUM,
        author=PROVISIONAL_AUTHOR_AI_DRAFTED,
        recorded_at=_RECORDED_AT_V3,
        transcription_notes=_V3_MARS_NOTES,
    ),
    translation_held_reason=_MARS_HELD,
)

JUPITER_KARAKA_HOUSE: Final = ProvisionalSignification(
    term_id="provisional.signification.graha.jupiter.griha",
    term_version="v1",
    subject_kind="graha",
    subject="jupiter",
    sanskrit="गृह",
    display="house (kāraka)",
    tags=_PROPERTY_TAG,
    statement="The text names Jupiter a kāraka (significator) of the house (गृह).",
    justification=ProvisionalJustification(
        source_work=_SOURCE_WORK,
        locator=f"{_KARAKA}, verse 5; PDF p. 109 (printed p. 111).",
        original_text=JUPITER_KARAKA_WEALTH.justification.original_text,
        draft_translation=JUPITER_KARAKA_WEALTH.justification.draft_translation,
        interpretive_reasoning=(
            "Jupiter's own kāraka list (v.5) names गृह (house) next to धन (wealth), and the "
            "edition's Hindi keeps गृह. Only गृह is drafted for Property; धन is the separate "
            "provisional Wealth record. The other Jupiter terms (one's own work, sacrifice, the "
            "gods, sons, friends) are not property terms. v.37 (Jupiter as bhāva-kāraka of the "
            "2nd, 5th, 9th and 11th) does not name the 4th house and is not used here."
        ),
        conventions=_PROPERTY_CONVENTIONS,
        confidence=ProvisionalConfidence.HIGH,
        author=PROVISIONAL_AUTHOR_AI_DRAFTED,
        recorded_at=_RECORDED_AT_V3,
        transcription_notes=JUPITER_KARAKA_WEALTH.justification.transcription_notes,
    ),
    translation_held_reason=_PROPERTY_HELD_OTHER.format(
        matters="one's own work, wealth, sons and friends"
    ),
)

VENUS_KARAKA_VEHICLES: Final = ProvisionalSignification(
    term_id="provisional.signification.graha.venus.yana",
    term_version="v1",
    subject_kind="graha",
    subject="venus",
    sanskrit="यान",
    display="vehicles (kāraka)",
    tags=_PROPERTY_TAG,
    statement="The text names Venus a kāraka (significator) of vehicles (यान).",
    justification=ProvisionalJustification(
        source_work=_SOURCE_WORK,
        locator=f"{_KARAKA}, verse 6; PDF p. 109 (printed p. 111).",
        original_text=VENUS_KARAKA_SPOUSE.justification.original_text.split(" | ")[0],
        draft_translation=(
            "Bhṛgu (Venus) is the kāraka of the wife, the bow, happiness, music, poetry, "
            "flowers, youth, ornaments, silver, vehicles (यान), heaven, pearls, splendour, "
            "verse, taste and the like. [Hindi: स्त्री, धनुष, सुख, गीतशास्त्र, काव्यशास्त्र, पुष्प, "
            "यौवन, आभूषण, चाँदी, सवारी, स्वर्गलोक, मोती, वैभव, कविता, रस आदि के कारक शुक्र हैं।]"
        ),
        interpretive_reasoning=(
            "Venus's own kāraka list names यान (vehicle, conveyance), which the edition's Hindi "
            "renders सवारी. Only यान is drafted for Property; कलत्र is the separate provisional "
            "Marriage record. The other Venus terms are not property terms."
        ),
        conventions=_PROPERTY_CONVENTIONS,
        confidence=ProvisionalConfidence.HIGH,
        author=PROVISIONAL_AUTHOR_AI_DRAFTED,
        recorded_at=_RECORDED_AT_V3,
        transcription_notes=(
            "Read from the page image (PDF p. 109, printed p. 111). The PDF text layer garbles "
            "v.6 (कामुक for कार्मुक, भगः for भृगुः) but reads यान correctly. The Sanskrit and the "
            "Hindi agree on यान/सवारी."
        ),
    ),
    translation_held_reason=_PROPERTY_HELD_OTHER.format(
        matters="the wife, happiness, music and ornaments"
    ),
)

SUN_KARAKA_FIELDS: Final = ProvisionalSignification(
    term_id="provisional.signification.graha.sun.kshetra",
    term_version="v1",
    subject_kind="graha",
    subject="sun",
    sanskrit="क्षेत्र",
    display="fields or land (kāraka)",
    tags=_PROPERTY_TAG,
    statement=(
        "The text names the Sun a kāraka (significator) of क्षेत्र, read here as fields or "
        "land; the word may also mean a region, so the reading is tentative."
    ),
    justification=ProvisionalJustification(
        source_work=_SOURCE_WORK,
        locator=f"{_KARAKA}, verse 1; PDF p. 109 (printed p. 111).",
        original_text="राज्यविद्रुमरक्तवस्त्रमाणिक्यराजवनपर्वतक्षेत्रपितृकारको रविः ॥ १ ॥",
        draft_translation=(
            "Ravi (the Sun) is the kāraka of kingship, coral, red cloth, rubies, the king, "
            "forests, mountains, क्षेत्र (fields or regions) and the father. [Hindi: राज्य, मूँगा, "
            "रक्तवस्त्र, मानिक, राज, वन, पर्वत, क्षेत्र और पिता का कारक सूर्य होता है।]"
        ),
        interpretive_reasoning=(
            "The Sun's list names क्षेत्र; the edition's Hindi keeps क्षेत्र without a gloss. "
            "Standing next to वन and पर्वत (forests, mountains), it may mean fields or land, or "
            "a region or sacred place, so confidence is medium. Only क्षेत्र is drafted. "
            "Because the reading is medium, the Sun is not one of the kārakas a Property answer "
            "lists (Mars, Jupiter and Venus each have a high-confidence term); the reviewer is "
            "asked."
        ),
        conventions=_PROPERTY_CONVENTIONS,
        confidence=ProvisionalConfidence.MEDIUM,
        author=PROVISIONAL_AUTHOR_AI_DRAFTED,
        recorded_at=_RECORDED_AT_V3,
        transcription_notes=(
            "Read from the page image (PDF p. 109, printed p. 111). The PDF text layer reads "
            "राज्यविदुम… for राज्यविद्रुम…; क्षेत्र is read the same in both."
        ),
    ),
    translation_held_reason=_PROPERTY_HELD_OTHER.format(
        matters="kingship, gems, the king and the father"
    ),
)

PROPERTY_SIGNIFICATIONS: Final = (
    FOURTH_HOUSE_HOUSE,
    FOURTH_HOUSE_LAND,
    FOURTH_HOUSE_VEHICLES,
    MARS_KARAKA_LAND,
    MARS_KARAKA_DWELLING,
    JUPITER_KARAKA_HOUSE,
    VENUS_KARAKA_VEHICLES,
    SUN_KARAKA_FIELDS,
)
PROVISIONAL_SIGNIFICATION_CORPUS_V3: Final = ProvisionalSignificationCorpus(
    corpus_id="jyotish.provisional.signification",
    corpus_version="v3",
    terms=(*PROVISIONAL_SIGNIFICATION_CORPUS_V2.terms, *PROPERTY_SIGNIFICATIONS),
)

# --- Corpus v4 (NEXT-CHILDREN-GUARD-01) ---------------------------------------------------
# Owner decision: JyotAI never predicts or hints at the sex of a child.  Where the text says
# पुत्र, the term is shown as written with the gloss "children (the text says 'son')".  Six
# terms whose displayed record named "sons" or had पुत्र (in the original text) get a new
# record version (v2): the gloss convention, and the reasoning / translation-held reason
# reworded with the gloss.  Terms, statements, tags, originals and translations are unchanged.

_RECORDED_AT_V4: Final = datetime(2026, 11, 27, tzinfo=UTC)


def _glossed(
    term: ProvisionalSignification,
    *,
    reasoning: str | None = None,
    translation_held_reason: str | None = None,
) -> ProvisionalSignification:
    old = term.justification
    justification = ProvisionalJustification.model_validate(
        {
            **old.model_dump(),
            "conventions": (*old.conventions, PUTRA_CONVENTION),
            "recorded_at": _RECORDED_AT_V4,
            "interpretive_reasoning": reasoning or old.interpretive_reasoning,
        }
    )
    return ProvisionalSignification.model_validate(
        {
            **term.model_dump(),
            "term_version": "v2",
            "justification": justification,
            "translation_held_reason": translation_held_reason or term.translation_held_reason,
        }
    )


VENUS_KARAKA_SPOUSE_V2: Final = _glossed(VENUS_KARAKA_SPOUSE)
ELEVENTH_HOUSE_GAIN_V2: Final = _glossed(
    ELEVENTH_HOUSE_GAIN,
    reasoning=ELEVENTH_HOUSE_GAIN.justification.interpretive_reasoning.replace(
        "पुत्र and जाया (sons, wife) are", f"पुत्र and जाया ({PUTRA_GLOSS}; the wife) are"
    ),
    translation_held_reason=_WEALTH_HELD_OTHER.format(
        matters=f"{PUTRA_GLOSS}, the wife and livestock"
    ),
)
JUPITER_KARAKA_WEALTH_V2: Final = _glossed(
    JUPITER_KARAKA_WEALTH,
    reasoning=JUPITER_KARAKA_WEALTH.justification.interpretive_reasoning.replace(
        "पुत्र to Children;", f"पुत्र ({PUTRA_GLOSS}) to Children;"
    ),
    translation_held_reason=_WEALTH_HELD_OTHER.format(
        matters=f"one's own work, {PUTRA_GLOSS} and friends"
    ),
)
_MARS_HELD_V2: Final = _PROPERTY_HELD_OTHER.format(
    matters=f"disease, theft, {PUTRA_GLOSS}, brothers and the king's enemies"
)
MARS_KARAKA_LAND_V2: Final = _glossed(
    MARS_KARAKA_LAND,
    reasoning=MARS_KARAKA_LAND.justification.interpretive_reasoning.replace(
        "(strength, sons, conduct,", f"(strength, {PUTRA_GLOSS}, conduct,"
    ),
    translation_held_reason=_MARS_HELD_V2,
)
MARS_KARAKA_DWELLING_V2: Final = _glossed(
    MARS_KARAKA_DWELLING, translation_held_reason=_MARS_HELD_V2
)
JUPITER_KARAKA_HOUSE_V2: Final = _glossed(
    JUPITER_KARAKA_HOUSE,
    reasoning=JUPITER_KARAKA_HOUSE.justification.interpretive_reasoning.replace(
        "the gods, sons, friends)", f"the gods, {PUTRA_GLOSS}, friends)"
    ),
    translation_held_reason=_PROPERTY_HELD_OTHER.format(
        matters=f"one's own work, wealth, {PUTRA_GLOSS} and friends"
    ),
)
CHILDREN_GUARD_SIGNIFICATION_REVISIONS: Final = (
    VENUS_KARAKA_SPOUSE_V2,
    ELEVENTH_HOUSE_GAIN_V2,
    JUPITER_KARAKA_WEALTH_V2,
    MARS_KARAKA_LAND_V2,
    MARS_KARAKA_DWELLING_V2,
    JUPITER_KARAKA_HOUSE_V2,
)
_REVISED_V4: Final = {term.term_id: term for term in CHILDREN_GUARD_SIGNIFICATION_REVISIONS}
PROVISIONAL_SIGNIFICATION_CORPUS_V4: Final = ProvisionalSignificationCorpus(
    corpus_id="jyotish.provisional.signification",
    corpus_version="v4",
    terms=tuple(
        _REVISED_V4.get(term.term_id, term) for term in PROVISIONAL_SIGNIFICATION_CORPUS_V3.terms
    ),
)

# --- Corpus v5 (NEXT-CHILDREN-01) ----------------------------------------------------------
# Children: progeny terms only, each shown with the पुत्र gloss.  Education: the 5th house's
# learning and intellect terms (the reviewed Career terms of the same words stay Career only).

_RECORDED_AT_V5: Final = datetime(2026, 11, 28, tzinfo=UTC)
_CHILDREN_TAG: Final = (DomainTag(domain=JyotishDomain.CHILDREN, status="provisional"),)
_EDUCATION_TAG: Final = (DomainTag(domain=JyotishDomain.EDUCATION, status="provisional"),)
_CHILDREN_CONVENTIONS: Final = (
    "Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).",
    "Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 "
    "item 20).",
    "A signification term names a theme only: no polarity, weight, timing, number or "
    "prediction; it never says whether or when children will come. Domain tag: Children "
    "(provisional).",
    "Drafted only where the verse names progeny (पुत्र); the verse's other matters are not "
    f"drafted for Children. पुत्र is shown as {PUTRA_GLOSS!r}.",
    PUTRA_CONVENTION,
)
_EDUCATION_CONVENTIONS: Final = (
    "Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).",
    "Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 "
    "item 20); the gloss is the admitted Career gloss of the same word.",
    "A signification term names a theme only: no polarity, weight, timing or prediction. "
    "Domain tag: Education (provisional).",
    PUTRA_CONVENTION,
)
_CHILDREN_HELD_OTHER: Final = (
    "The verse's other matters are not children terms (they include {matters}); the full "
    "translation is kept for the expert review and is not shown in a children answer."
)
_EDUCATION_HELD_OTHER: Final = (
    "The verse's other matters are not education terms (they include {matters}); the full "
    "translation is kept for the expert review and is not shown in an education answer."
)
_V5_LOCATOR: Final = f"{_CH12}, verse 5; PDF p. 147 (printed p. 149)."
_V5_ORIGINAL: Final = "यन्त्रमन्त्रौ तथा विद्या बुद्धेश्चैव प्रबन्धकम् । पुत्रराज्यापभ्रंशादि पश्येत्पुत्रालयाद् बुधः ॥ ५ ॥"
_V5_TRANSLATION: Final = (
    "From the fifth house, the house of sons (पुत्रालय), the wise should examine amulets "
    "(यन्त्र), mantras, learning (विद्या), intelligence (बुद्धि), composition (प्रबन्ध), sons "
    "(पुत्र) and the fall from royal position (राज्यापभ्रंश). [Hindi: पाँचवें भाव से यंत्र, "
    "मंत्र, विद्या, बुद्धि, प्रबंध, पुत्र और राज्य के स्खलन का विचार करना चाहिए।]"
)
_V5_NOTES: Final = (
    "Read from the page image (PDF p. 147, printed p. 149). The PDF text layer reads प्रनन्धकम् "
    "for the printed प्रबन्धकम्; the rest agrees. The Sanskrit and the edition's Hindi agree."
)

FIFTH_HOUSE_CHILDREN: Final = ProvisionalSignification(
    term_id="provisional.signification.bhava.5.progeny",
    term_version="v1",
    subject_kind="bhava",
    subject="5",
    sanskrit="पुत्र",
    display=PUTRA_GLOSS,
    tags=_CHILDREN_TAG,
    statement=(
        f"The text lists {PUTRA_GLOSS} (पुत्र) among the matters judged from the 5th house, "
        "which it calls पुत्रालय."
    ),
    justification=ProvisionalJustification(
        source_work=_SOURCE_WORK,
        locator=(f"{_V5_LOCATOR} Corroboration: अथ भावकारकमाह v.36, PDF p. 108 (printed p. 110)."),
        original_text=(
            f"{_V5_ORIGINAL} | v.36: सुते सुतं विजानीयाद्दारा सप्तमभावतः । सुतस्थाने "
            "ग्रहस्तिष्ठेत्सोऽपि कारक उच्यते ॥ ३६ ॥"
        ),
        draft_translation=(
            f"v.5: {_V5_TRANSLATION} v.36: from the fifth, sons (सुत); from the seventh house, "
            "the wife; a graha placed in the fifth is also called its kāraka. [Hindi: पंचम भाव "
            "पुत्र का और सातवाँ स्त्री का कारक होता है।]"
        ),
        interpretive_reasoning=(
            f"The verse names पुत्र, {PUTRA_GLOSS}, among the fifth house's matters and calls "
            "the fifth पुत्रालय; the kāraka chapter v.36 gives the fifth for the same matter "
            "(सुत). Only that term is drafted for Children, shown with the gloss. विद्या "
            "(learning) and बुद्धि (intelligence) are drafted separately for Education "
            "(provisional); यन्त्र, मन्त्र and प्रबन्ध (amulets, mantras, composition) and "
            "राज्यापभ्रंश (a fall from royal position) are not children themes and are not "
            "drafted. The term names a theme only; it never says whether or when children will "
            "come."
        ),
        conventions=_CHILDREN_CONVENTIONS,
        confidence=ProvisionalConfidence.HIGH,
        author=PROVISIONAL_AUTHOR_AI_DRAFTED,
        recorded_at=_RECORDED_AT_V5,
        transcription_notes=(
            f"{_V5_NOTES} v.36 read from the page image (PDF p. 108, printed p. 110); the PDF "
            "text layer reads विजानीयादारा for विजानीयाद्दारा."
        ),
    ),
    translation_held_reason=_CHILDREN_HELD_OTHER.format(
        matters="amulets, mantras, learning, composition and a fall from royal position"
    ),
)

_V30_ORIGINAL: Final = "बुधान्मातुलमाख्यातो मातृतुल्यानपि द्विज । गुरुणा चात्र विज्ञेया पुत्रस्वामिपितामहाः ॥ ३० ॥"
_V33_ORIGINAL: Final = VENUS_KARAKA_SPOUSE.justification.original_text.split(" | v.33: ")[1]
_V37_ORIGINAL: Final = "सूर्यो गुरुः कुजः सोमो गुरुर्भौमः सितः शनिः । गुरुश्चन्द्रसुतो जीवो मन्दश्च भावकारकः ॥ ३७ ॥"

JUPITER_KARAKA_CHILDREN: Final = ProvisionalSignification(
    term_id="provisional.signification.graha.jupiter.progeny",
    term_version="v1",
    subject_kind="graha",
    subject="jupiter",
    sanskrit="पुत्र",
    display=f"{PUTRA_GLOSS}, kāraka",
    tags=_CHILDREN_TAG,
    statement=f"The text names Jupiter a kāraka (significator) of {PUTRA_GLOSS} (पुत्र).",
    justification=ProvisionalJustification(
        source_work=_SOURCE_WORK,
        locator=(
            f"{_KARAKA}, verse 5; PDF p. 109 (printed p. 111). Corroboration: अथ स्थिरकारकमाह "
            "vv. 30 and 33, PDF p. 107 (printed p. 109); अथ भावकारकमाह v.37, PDF p. 108 "
            "(printed p. 110)."
        ),
        original_text=(
            f"{JUPITER_KARAKA_WEALTH.justification.original_text.split(' | ')[0]} | v.30: "
            f"{_V30_ORIGINAL} | v.33: {_V33_ORIGINAL} | v.37: {_V37_ORIGINAL}"
        ),
        draft_translation=(
            "v.5: Guru (Jupiter) is the kāraka of one's own work, sacrifice, the gods, "
            "brāhmaṇas, wealth, house, gold, cloth, sons (पुत्र), friends, swings and the like. "
            "[Hindi: अपने कार्य, यज्ञ, देवता, ब्राह्मण, धन, गृह, सुवर्ण, वस्त्र, पुत्र, मित्र, "
            "आंदोलन आदि के कारक गुरु हैं।] v.30: from Mercury the maternal uncle and those like "
            "the mother; from Jupiter, sons, the husband and the paternal grandfather. [Hindi: "
            "गुरु से पुत्र और पितामह आदि का विचार होता है।] v.33: from Jupiter (देवेज्य), the "
            "fifth for sons; from Venus the seventh for the wife; from Saturn the eighth for "
            "death. v.37: the kārakas of the houses from the Lagna are, in order, Sun, Jupiter, "
            "Mars, Moon (Hindi: Mercury), Jupiter (the fifth), Mars, Venus, Saturn, Jupiter, "
            "Mercury, Jupiter, Saturn."
        ),
        interpretive_reasoning=(
            f"Four verses agree that Jupiter signifies पुत्र, {PUTRA_GLOSS}: Jupiter's own "
            "kāraka list (v.5); the fixed-kāraka verses, which judge it from Jupiter (v.30) and "
            "from the fifth from Jupiter (v.33, देवेज्यात्पञ्चमे); and the bhāva-kāraka list "
            "(v.37), which makes Jupiter the kāraka of the fifth house. The reviewer's Sitting 1 "
            "verdict (item 16) also names Jupiter and the kāraka of children. Only this term is "
            "drafted for Children, shown with the gloss; धन and गृह are the separate provisional "
            "Wealth and Property records, and the other Jupiter terms are not children themes. "
            "Mars's list (v.3) also has the word inside the compound सत्त्वसद्मभूमिपुत्र…, "
            "which can also be read भूमिपुत्र, an epithet of Mars ('of the earth'); Mars is "
            "not used (a review-pack question)."
        ),
        conventions=_CHILDREN_CONVENTIONS,
        confidence=ProvisionalConfidence.HIGH,
        author=PROVISIONAL_AUTHOR_AI_DRAFTED,
        recorded_at=_RECORDED_AT_V5,
        transcription_notes=(
            "Read from the page images. v.5: the PDF text layer breaks the line at काञ्चन (no "
            "letter lost). v.30: the text layer reads पित्तामरः for पितामहाः. v.33: the text "
            "layer reads दैत्येज्यादयूनभे च्त्रियः. v.37: the text layer garbles सूर्यो गुरुः; in "
            "v.37 the Sanskrit's fourth kāraka is सोमः (Moon) while the Hindi gives बुध "
            "(Mercury); both give गुरु (Jupiter) for the fifth."
        ),
    ),
    translation_held_reason=_CHILDREN_HELD_OTHER.format(
        matters="one's own work, wealth, the house, friends, the husband and death"
    ),
)


def _education_term(
    *, term_id: str, sanskrit: str, display: str, statement: str, reasoning: str
) -> ProvisionalSignification:
    return ProvisionalSignification(
        term_id=term_id,
        term_version="v1",
        subject_kind="bhava",
        subject="5",
        sanskrit=sanskrit,
        display=display,
        tags=_EDUCATION_TAG,
        statement=statement,
        justification=ProvisionalJustification(
            source_work=_SOURCE_WORK,
            locator=_V5_LOCATOR,
            original_text=_V5_ORIGINAL,
            draft_translation=_V5_TRANSLATION,
            interpretive_reasoning=reasoning,
            conventions=_EDUCATION_CONVENTIONS,
            confidence=ProvisionalConfidence.HIGH,
            author=PROVISIONAL_AUTHOR_AI_DRAFTED,
            recorded_at=_RECORDED_AT_V5,
            transcription_notes=_V5_NOTES,
        ),
        translation_held_reason=_EDUCATION_HELD_OTHER.format(
            matters=f"amulets, mantras, {PUTRA_GLOSS} and a fall from royal position"
        ),
    )


_EDUCATION_REVIEWED_NOTE: Final = (
    "The admitted signification corpus has the same word for the 5th house with the same "
    "gloss, admitted for Career and tagged Career only; this provisional record lets an "
    "Education answer show it (with the flag) until the expert decides whether the admitted "
    "term may be tagged Education (review-pack question)."
)
FIFTH_HOUSE_LEARNING: Final = _education_term(
    term_id="provisional.signification.bhava.5.vidya",
    sanskrit="विद्या",
    display="learning",
    statement="The text lists learning (विद्या) among the matters judged from the 5th house.",
    reasoning=(
        "The verse names विद्या (learning) among the fifth house's matters; the edition's Hindi "
        "keeps विद्या. Only learning and intelligence are drafted for Education; the progeny "
        "term is the separate provisional Children record, and amulets, mantras, composition "
        f"and a fall from royal position are not drafted. {_EDUCATION_REVIEWED_NOTE}"
    ),
)
FIFTH_HOUSE_INTELLECT: Final = _education_term(
    term_id="provisional.signification.bhava.5.buddhi",
    sanskrit="बुद्धि",
    display="intellect",
    statement=(
        "The text lists intellect (बुद्धि; the verse has the form बुद्धेः) among the matters "
        "judged from the 5th house."
    ),
    reasoning=(
        "The verse names बुद्धि (in the form बुद्धेः) among the fifth house's matters; the "
        "edition's Hindi renders बुद्धि. Only learning and intelligence are drafted for "
        "Education; प्रबन्ध (composition; it may also mean an arrangement or management) is "
        "not drafted because its reading is uncertain. "
        f"{_EDUCATION_REVIEWED_NOTE}"
    ),
)

CHILDREN_SIGNIFICATIONS: Final = (FIFTH_HOUSE_CHILDREN, JUPITER_KARAKA_CHILDREN)
EDUCATION_SIGNIFICATIONS: Final = (FIFTH_HOUSE_LEARNING, FIFTH_HOUSE_INTELLECT)
PROVISIONAL_SIGNIFICATION_CORPUS_V5: Final = ProvisionalSignificationCorpus(
    corpus_id="jyotish.provisional.signification",
    corpus_version="v5",
    terms=(
        *PROVISIONAL_SIGNIFICATION_CORPUS_V4.terms,
        *CHILDREN_SIGNIFICATIONS,
        *EDUCATION_SIGNIFICATIONS,
    ),
)
ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS: Final = PROVISIONAL_SIGNIFICATION_CORPUS_V5
