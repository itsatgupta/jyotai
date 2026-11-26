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
"""

import re
from datetime import UTC, datetime
from typing import Final

from pydantic import BaseModel, ConfigDict, Field, model_validator

from astrologer.composition.comparison_guard import ranking_violation
from astrologer.composition.evaluative_guard import evaluative_violation
from astrologer.composition.marriage_guard import marriage_wording_violation
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
ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS: Final = PROVISIONAL_SIGNIFICATION_CORPUS_V2
