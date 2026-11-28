"""NEXT-CHILDREN-01: provisional corpus v6 (``jyotish.provisional@v6``) adds Children rules.

v6 = the v5 rules, unchanged, plus provisional Children rules for the D1 fifth-house lord, from
the BPHS Bhavesha-phala chapter, अथ सुतेशभावफलम् (Sutesha-phala), verses 35–42, PDF pp.
187–188 (printed pp. 189–190), read from the local PDF page images
(``bphs.selected-edition@v1``).  A verse is drafted only where it has a progeny clause that
passes the children guards (no child-sex hint beyond the पुत्र gloss, no childlessness, loss
or number of children: owner decision, NEXT-CHILDREN-GUARD-01).  All 12 placements:

* **Shown** (2): the 9th and the 10th (v.41, पुत्रो भूपसमो: children (the text says 'son')
  compared to a king), medium confidence.  Only that clause is displayed; the source verse is
  held in the app (its second line has कुलदीपक, an epithet that can hint at a child's sex).
* **Held** (5): the 2nd and the 8th (v.36: a number of children, in a word naming a child's
  sex); the 5th (v.38) and the 6th and 12th (v.39): their progeny clauses are of a kind the
  app never displays.  The app shows the held statement; the verse stays in the review pack.
* **Not drafted** (5): the 1st and 3rd (v.35), the 4th (v.37) and the 7th (v.40) have no
  progeny clause; the 11th (v.42) already has the reviewed Children rule the reviewer
  confirmed (Sitting 1 item 16), and its progeny clause gives a number of children.

Every rule is PROVISIONAL, drafted by an AI agent, pending the project owner's adoption and the
final expert review; none is REVIEWED.
"""

from datetime import UTC, datetime
from typing import Final

from astrologer.composition.children_guard import PUTRA_CONVENTION, PUTRA_GLOSS
from astrologer.knowledge.models import JyotishDomain
from astrologer.knowledge.provisional import (
    HELD_STATEMENT,
    PROVISIONAL_AUTHOR_AI_DRAFTED,
    ProvisionalConfidence,
    ProvisionalCorpus,
    ProvisionalJustification,
    ProvisionalRule,
)
from astrologer.knowledge.provisional_pack_v1 import _CONVENTIONS, _SOURCE_WORK, _placement_rule
from astrologer.knowledge.provisional_pack_v5 import NOT_DRAFTED as NOT_DRAFTED_V5
from astrologer.knowledge.provisional_pack_v5 import PROVISIONAL_CORPUS_V5
from astrologer.knowledge.provisional_pack_v5 import REVIEWER_QUESTIONS as REVIEWER_QUESTIONS_V5

_RECORDED_AT: Final = datetime(2026, 11, 28, tzinfo=UTC)
_SUTESHA: Final = "भावेशफलाध्यायः, अथ सुतेशभावफलम् (Sutesha-phala)"
_P187: Final = "PDF p. 187 (printed p. 189)"
_P188: Final = "PDF p. 188 (printed p. 190)"
_CHILDREN_CONVENTIONS: Final = (
    *_CONVENTIONS,
    f"The fifth lord is named सुतेश (lord of the house of {PUTRA_GLOSS}) and पंचमेश (Hindi) "
    "in these verses.",
    "Drafted only where the verse has a progeny clause that passes the children guards; only "
    "that clause is displayed, and the full translation stays in the review pack. A Children "
    "item never says whether, when or how many children there will be.",
    PUTRA_CONVENTION,
)
_HELD_NUMBER: Final = (
    "The verse's progeny clause gives a number of children, in a word that names a child's "
    "sex; JyotAI shows neither (owner decision, NEXT-CHILDREN-GUARD-01). The expert review "
    "decides the wording."
)
_HELD_KIND: Final = (
    "The verse's progeny clause is of a kind JyotAI never displays (children wording rule, "
    "owner decision NEXT-CHILDREN-GUARD-01). The expert review decides the wording."
)

_V35: Final = "सुतेशे लग्नसहजे मायावी पिशुनो महान् । लोष्ठं दत्तवान्नैव काचिद्द्रव्यस्य का कथा ॥ ३५ ॥"
_V36: Final = "सुतेशे चायुधि धने बहुपुत्री न संशयः । कासश्वाससुखी न स्यात्क्रोधयुक्तो धनान्वितः ॥ ३६ ॥"
_V38: Final = "सुतेशे पञ्चमे यस्य तस्य पुत्रो न जीवति । क्षणिकः क्रूरभाषी च धनिको मतिमान्भवेत् ॥ ३८ ॥"
_V39: Final = "सुतेशे षष्ठरिःफस्थे पुत्रः शत्रुत्वमाप्नुयात् । मृतापत्यो दत्तपुत्रो धनपुत्रोऽथवा भवेत् ॥ ३९ ॥"
_V41: Final = "सुतेशे नवमे कर्मे पुत्रो भूपसमो भवेत् । अथवा ग्रन्थकर्ता च विख्यातः कुलदीपकः ॥ ४१ ॥"
_V42: Final = "सुतेशे लाभभवने पण्डितो जनवल्लभः । ग्रन्थकर्ता महादक्षो बहुपुत्रधनान्वितः ॥ ४२ ॥"

_ORDINAL: Final = {
    2: "second",
    5: "fifth",
    6: "sixth",
    8: "eighth",
    9: "ninth",
    10: "tenth",
    12: "twelfth",
}


def _justification(
    *,
    verse: int,
    page: str,
    original: str,
    translation: str,
    reasoning: str,
    confidence: ProvisionalConfidence,
    notes: str,
) -> ProvisionalJustification:
    return ProvisionalJustification(
        source_work=_SOURCE_WORK,
        locator=f"{_SUTESHA}, verse {verse}; {page}.",
        original_text=original,
        draft_translation=translation,
        interpretive_reasoning=reasoning,
        conventions=_CHILDREN_CONVENTIONS,
        confidence=confidence,
        author=PROVISIONAL_AUTHOR_AI_DRAFTED,
        recorded_at=_RECORDED_AT,
        transcription_notes=notes,
    )


def _children_rule(
    house: int,
    justification: ProvisionalJustification,
    *,
    statement: str = HELD_STATEMENT,
    held_reason: str | None = None,
    translation_held_reason: str | None = None,
) -> ProvisionalRule:
    return ProvisionalRule(
        rule=_placement_rule(
            rule_id=f"provisional.bphs.d1.house_lord.5.equals_{house}.children.v1",
            name=f"D1 fifth-house lord in the {_ORDINAL[house]} house (provisional)",
            domain=JyotishDomain.CHILDREN,
            lord=5,
            house=house,
        ),
        domain=JyotishDomain.CHILDREN,
        fact_dependencies=("jyotish.d1.house_lord.5.placement_house",),
        statement=statement,
        justification=justification,
        wording="held" if held_reason is not None else "shown",
        held_reason=held_reason,
        translation_held_reason=translation_held_reason,
    )


# --- Shown: the 9th and the 10th (v.41) ---------------------------------------------------

_V41_TRANSLATION: Final = (
    "When the lord of the fifth is in the ninth or the tenth (कर्म), the son is like a king, or "
    "an author, renowned, the lamp of the family (कुलदीपक). [Hindi: सुतेश ९वें या १०वें भाव में "
    "हो तो जातक का पुत्र राजा के समान होता है अथवा प्रसिद्ध ग्रंथकर्त्ता होता है।]"
)
_V41_REASONING: Final = (
    "The verse names the fifth lord in the ninth (नवमे) or the tenth (कर्मे) house; the "
    f"edition's Hindi agrees. The progeny clause is पुत्रो भूपसमो, {PUTRA_GLOSS} compared to "
    "a king; it is the only clause displayed, with the gloss. The second line (an author, "
    "renowned, 'the lamp of the family') may describe the child, as the Hindi reads it, or the "
    "native; its last epithet can hint at a child's sex, so the line is not displayed and the "
    "source verse is held in the app (in full in the review pack). Confidence is medium for "
    "that reason and because the verse does not say whether children will come; the "
    "statement says so."
)
_V41_NOTES: Final = (
    "Read from the page image (PDF p. 188, printed p. 190). The PDF text layer misreads the "
    "vowel sign of the progeny word in line 1 (ौ for ो) and reads ग्रन्थकेतां for ग्रन्थकर्ता. "
    "The Sanskrit and the edition's Hindi agree; the Hindi omits the last epithet."
)
_V41_HELD_TRANSLATION: Final = (
    "The verse's second line (an author, renown and an epithet that can hint at a child's sex) "
    "is not displayed; the full translation is kept for the expert review."
)


def _v41_statement(house: int) -> str:
    return (
        f"With the D1 fifth-house lord in the {_ORDINAL[house]} house, the text compares "
        f"{PUTRA_GLOSS} to a king (पुत्रो भूपसमो). It does not say whether, when or how many "
        "children there will be."
    )


RULE_5_IN_9_CHILDREN: Final = _children_rule(
    9,
    _justification(
        verse=41,
        page=_P188,
        original=_V41,
        translation=_V41_TRANSLATION,
        reasoning=_V41_REASONING,
        confidence=ProvisionalConfidence.MEDIUM,
        notes=_V41_NOTES,
    ),
    statement=_v41_statement(9),
    translation_held_reason=_V41_HELD_TRANSLATION,
)
RULE_5_IN_10_CHILDREN: Final = _children_rule(
    10,
    _justification(
        verse=41,
        page=_P188,
        original=_V41,
        translation=_V41_TRANSLATION,
        reasoning=_V41_REASONING,
        confidence=ProvisionalConfidence.MEDIUM,
        notes=_V41_NOTES,
    ),
    statement=_v41_statement(10),
    translation_held_reason=_V41_HELD_TRANSLATION,
)

# --- Held: the 2nd and 8th (v.36), the 5th (v.38), the 6th and 12th (v.39) ----------------

_V36_TRANSLATION: Final = (
    "When the lord of the fifth is in the eighth (आयु) or the second (धन), the native has many "
    "sons, no doubt; he is not free of cough and asthma, is given to anger and is wealthy. "
    "[Hindi: पंचमेश ८वें वा दूसरे भाव में हो तो जातक अनेक पुत्रों से युक्त, कास-श्वासरोगी, "
    "क्रोधी और धनी होता है।]"
)
_V36_REASONING: Final = (
    "The verse names the fifth lord in the eighth (आयुधि, the house of longevity) or the second "
    "(धने) house; the edition's Hindi agrees. Its progeny clause is held (see the held reason). "
    "Its other clauses, a respiratory illness, anger and wealth, are not children themes; one "
    "is a health statement. Nothing of the verse is displayed; the full verse and translation "
    "are in the review pack."
)
_V36_NOTES: Final = (
    "Read from the page image (PDF p. 188, printed p. 190). The PDF text layer agrees on the "
    "first line. The Hindi has '८वें वा दूसरे' (eighth or second); the text layer reads रसरे."
)
_V38_TRANSLATION: Final = (
    "He whose fifth lord is in the fifth: his son does not live; he is fickle, harsh of speech, "
    "wealthy and intelligent. [Hindi: सुतेश ५वें भाव में हो तो जातक का पुत्र नहीं जीता है।]"
)
_V38_REASONING: Final = (
    "The verse names the fifth lord in the fifth house (पञ्चमे); the edition's Hindi agrees "
    "and renders only the progeny clause. That clause is held (see the held reason). The other "
    "clauses, fickle (क्षणिक), harsh of speech (क्रूरभाषी), wealthy (धनिक) and intelligent "
    "(मतिमान्), are not children themes; two are judgements of conduct. Nothing of the verse "
    "is displayed; the full verse and translation are in the review pack."
)
_V38_NOTES: Final = (
    "Read from the page image (PDF p. 188, printed p. 190). The PDF text layer agrees. The "
    "Hindi renders only the first line."
)
_V39_TRANSLATION: Final = (
    "When the lord of the fifth is in the sixth or the twelfth, the son becomes hostile; the "
    "native's children die, or he has an adopted son or a son acquired for wealth. [Hindi: "
    "सुतेश छठे, बारहवें भाव में हो तो जातक को पुत्र से शत्रुता होती है और उसके पुत्र मर जाते हैं। "
    "उसे दत्तक पुत्र या क्रीत पुत्र होता है।]"
)
_V39_REASONING: Final = (
    "The verse names the fifth lord in the sixth or the twelfth house (षष्ठरिःफस्थे); the "
    "edition's Hindi agrees. Every clause of the verse concerns progeny and is held (see the "
    "held reason). Nothing of the verse is displayed; the full verse and translation are in "
    "the review pack."
)
_V39_NOTES: Final = (
    "Read from the page image (PDF p. 188, printed p. 190). The PDF text layer reads "
    "शत्रत्वमाप्नुयात् for शत्रुत्वमाप्नुयात्. The Hindi renders the verse's last compound with "
    "क्रीत (acquired by purchase)."
)


def _held(
    house: int, verse: int, original: str, translation: str, reasoning: str, notes: str, why: str
) -> ProvisionalRule:
    return _children_rule(
        house,
        _justification(
            verse=verse,
            page=_P188,
            original=original,
            translation=translation,
            reasoning=reasoning,
            confidence=ProvisionalConfidence.LOW,
            notes=notes,
        ),
        held_reason=why,
    )


RULE_5_IN_2_CHILDREN: Final = _held(
    2, 36, _V36, _V36_TRANSLATION, _V36_REASONING, _V36_NOTES, _HELD_NUMBER
)
RULE_5_IN_8_CHILDREN: Final = _held(
    8, 36, _V36, _V36_TRANSLATION, _V36_REASONING, _V36_NOTES, _HELD_NUMBER
)
RULE_5_IN_5_CHILDREN: Final = _held(
    5, 38, _V38, _V38_TRANSLATION, _V38_REASONING, _V38_NOTES, _HELD_KIND
)
RULE_5_IN_6_CHILDREN: Final = _held(
    6, 39, _V39, _V39_TRANSLATION, _V39_REASONING, _V39_NOTES, _HELD_KIND
)
RULE_5_IN_12_CHILDREN: Final = _held(
    12, 39, _V39, _V39_TRANSLATION, _V39_REASONING, _V39_NOTES, _HELD_KIND
)

CHILDREN_RULES: Final = (
    RULE_5_IN_2_CHILDREN,
    RULE_5_IN_5_CHILDREN,
    RULE_5_IN_6_CHILDREN,
    RULE_5_IN_8_CHILDREN,
    RULE_5_IN_9_CHILDREN,
    RULE_5_IN_10_CHILDREN,
    RULE_5_IN_12_CHILDREN,
)

# Located verses that yield no Children rule, with the reason (shown in the review pack).
NOT_DRAFTED: Final[dict[str, tuple[str, ...]]] = {
    **NOT_DRAFTED_V5,
    JyotishDomain.CHILDREN.value: (
        f"Fifth lord in the 1st or 3rd house: verse 35 ({_V35}), {_P187}, located. No progeny "
        "clause (deceitful, a slanderer, miserly: judgements of conduct); no Children rule is "
        "proposed and nothing is shown.",
        "Fifth lord in the 4th house: verse 37, PDF p. 188, located. No progeny clause (the "
        "mother's happiness, prosperity, intelligence, an adviser or teacher); it is the "
        "provisional Education rule v.37. No Children rule is proposed.",
        "Fifth lord in the 7th house: verse 40, PDF p. 188, located. No progeny clause "
        "(honour, every dharma, devotion); it is the provisional Spirituality rule v.40. No "
        "Children rule is proposed.",
        f"Fifth lord in the 11th house: verse 42 ({_V42}), {_P188}, located. The reviewed "
        "Children rule for this placement (bphs.d1.house_lord.5.in_11.children.v1) was "
        "confirmed by the reviewer as supporting evidence (Sitting 1 item 16) and is shown "
        "instead; the verse's progeny clause (बहुपुत्र) also gives a number of children, which "
        "JyotAI does not show. No provisional rule is proposed.",
        "Mars as a Children kāraka: कारकाध्यायः, अथ सूर्यादिग्रहाणां कारकत्वमाह v.3, PDF p. 109: "
        "the compound सत्त्वसद्मभूमिपुत्रशील… can be read भूमि + पुत्र (as the Hindi does) or "
        "भूमिपुत्र, an epithet of Mars. Jupiter is named for children in four verses (vv. 5, 30, "
        "33, 37); Mars is not used and no Mars term is drafted.",
        "5th-house terms that are not progeny terms (द्वादशभावविचाराध्यायः v.5, PDF p. 147): "
        "यन्त्र, मन्त्र (amulets, mantras), प्रबन्ध (composition; uncertain reading) and "
        "राज्यापभ्रंश (a fall from royal position) are not drafted; विद्या and बुद्धि are "
        "drafted for Education (provisional), not for Children.",
        "D7 (Saptāṁśa): not calculated by JyotAI, so no D7 fact is shown (open item).",
    ),
}

REVIEWER_QUESTIONS: Final[tuple[tuple[str, str], ...]] = (
    *REVIEWER_QUESTIONS_V5,
    (
        "Which factors should a Children answer use?",
        "JyotAI's Children answer lists the D1 5th lord and Jupiter (calculated facts with sign "
        "dignity) and the two reviewed Children rules you confirmed (Sitting 1 items 16 and 17, "
        "both supporting). Jupiter is named for children in कारकत्वमाह v.5 (PDF p. 109), "
        "स्थिरकारक vv. 30 and 33 (PDF p. 107) and the bhāva-kāraka list v.37 (PDF p. 108). "
        "Mars's v.3 compound सत्त्वसद्मभूमिपुत्र… may be read भूमि + पुत्र or भूमिपुत्र; Mars is "
        "not used. Are these the right factors, and should the 5th house's occupants (v.36: a "
        "graha in the 5th is also its kāraka) be added?",
    ),
    (
        "Fifth lord in the 9th or 10th (v.41): may the progeny clause be shown, and is the "
        "source verse rightly held?",
        "Statement shown (medium confidence): 'the text compares children (the text says "
        "'son') to a king (पुत्रो भूपसमो)', with 'It does not say whether, when or how many "
        "children there will be.' The second line (ग्रन्थकर्ता, विख्यात, कुलदीपक) may describe "
        "the child or the native; कुलदीपक ('lamp of the family') is customarily said of a son, "
        "so the app holds the source verse. Please confirm, change or reject.",
    ),
    (
        "Fifth lord in the 2nd/8th (v.36), 5th (v.38), 6th/12th (v.39): held. What wording, if "
        "any, may the app show?",
        "v.36 gives a number of sons (बहुपुत्री); v.38 says the son does not live; v.39 says the "
        "son becomes hostile, the children die, or there is an adopted or purchased son. Owner "
        "decision: no child-sex prediction, no childlessness, loss or number of children; the "
        "app shows the held statement. The verses' other clauses (illness, anger, wealth, "
        "conduct, intelligence) are not children themes.",
    ),
    (
        "May the reviewed Career terms of the 5th house (विद्या 'learning', बुद्धि 'intellect') "
        "be tagged Education?",
        "They are admitted for Career and tagged Career only. JyotAI drafted the same two words "
        "as provisional Education significations (द्वादशभावविचाराध्यायः v.5, PDF p. 147), shown "
        "only with the provisional toggle. A reviewed Education tag would replace them.",
    ),
    (
        "Should D7 (Saptāṁśa) be calculated and shown for children, and by which method?",
        "Your Sitting 1 verdict lists 'possibly D7'. JyotAI calculates D1, D2, D9 and D10 only; "
        "no D7 is shown. A reviewer-approved D7 method (and whether any D7 reading belongs in a "
        "Children answer) is needed first.",
    ),
)

PROVISIONAL_CORPUS_V6: Final = ProvisionalCorpus(
    corpus_id="jyotish.provisional",
    corpus_version="v6",
    rules=tuple(
        sorted((*PROVISIONAL_CORPUS_V5.rules, *CHILDREN_RULES), key=lambda rule: rule.rule_id)
    ),
)
ACTIVE_PROVISIONAL_CORPUS: Final = PROVISIONAL_CORPUS_V6
