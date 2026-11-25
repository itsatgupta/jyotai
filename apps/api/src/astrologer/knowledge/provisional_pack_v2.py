"""NEXT-MARRIAGE-01: provisional corpus v2 (``jyotish.provisional@v2``) adds Marriage.

v2 = the three v1 rules, unchanged, plus provisional Marriage rules for the D1 seventh-house
lord, one per house, from the same BPHS Bhavesha-phala chapter as the 10th-lord rules:
अथ सप्तमेशभावफलम् (Saptamesha-phala), verses 50–56, PDF pp. 190–191 (printed pp. 192–193).
Every rule is PROVISIONAL, drafted by an AI agent, pending the project owner's adoption and
the final expert review.

The original text was read from the local PDF page images (the selected edition,
``bphs.selected-edition@v1``).  The seven verses cover all twelve houses (most verses name
two houses).  What each verse says about marriage decides how it is used:

* **Shown** (12th house, v.56): the marriage clause can be stated without fear-based or
  accusatory wording.
* **Held** (1st, 2nd, 4th, 6th, 7th, 8th, 9th, 10th): the verse is located and recorded in
  full, but its marriage clause is accusatory, a judgement of conduct or a health statement.
  The app shows only ``HELD_STATEMENT``; the expert review decides the wording.
* **Not drafted** (3rd, 11th: v.52; 5th: v.54): the verse has no marriage clause, so no
  Marriage rule is proposed (``NOT_DRAFTED``).  v.54 is already the provisional Wealth rule.

Nothing is invented: a clause that is not displayed is named in the reasoning.
"""

from datetime import UTC, datetime
from typing import Final

from astrologer.knowledge.models import JyotishDomain
from astrologer.knowledge.provisional import (
    HELD_STATEMENT,
    PROVISIONAL_AUTHOR_AI_DRAFTED,
    ProvisionalConfidence,
    ProvisionalCorpus,
    ProvisionalJustification,
    ProvisionalRule,
)
from astrologer.knowledge.provisional_pack_v1 import (
    _CONVENTIONS,
    _SOURCE_WORK,
    PROVISIONAL_CORPUS_V1,
    _placement_rule,
)

_RECORDED_AT: Final = datetime(2026, 11, 25, tzinfo=UTC)
_CHAPTER: Final = "भावेशफलाध्यायः, अथ सप्तमेशभावफलम् (Saptamesha-phala)"
_P190: Final = "PDF p. 190 (printed p. 192)"
_P191: Final = "PDF p. 191 (printed p. 193)"
_MARRIAGE_CONVENTIONS: Final = (
    *_CONVENTIONS,
    "The verses address a male native (भार्या, जाया, कामिनी: wife); a displayed statement "
    "says 'spouse'. Whether a verse applies unchanged to every chart is for the expert review.",
    "The seventh lord is named by its synonyms: सप्तमेश, द्यूनेश (द्यून = seventh house), "
    "जायेश (lord of the house of the wife).",
)
_HELD_ACCUSATORY: Final = (
    "The verse's marriage clause is a judgement about a person's conduct or fidelity; stated "
    "to a user it would be accusatory. Wording is for the expert review."
)
_HELD_HEALTH: Final = (
    "The verse's marriage clause is a health statement about the spouse and the verse is "
    "phrased in absolute terms. Health is a high-stakes topic; wording is for the expert review."
)

_V50: Final = "सप्तमेशे तनौ चास्ते परजायासु लम्पटः । दुष्टो विचक्षणो धीरो वातरुक् स्थीयते हृदि ॥ ५० ॥"
_V50_TRANSLATION: Final = (
    "When the lord of the seventh is in the first house (and, reading चास्ते as च अस्ते, in "
    "the seventh), the native is drawn to the wives of others, wicked, discerning and steady, "
    "and a vāta (wind) ailment settles in the heart. [Hindi: सप्तमेश लग्न या सप्तम में हो तो "
    "जातक परस्त्री में आसक्त, दुष्ट, पंडित, वातरोगी होता है।]"
)
_V50_NOTES: Final = (
    "Read from the page image. चास्ते is read as च + अस्ते (अस्त, a name of the seventh "
    "house); the edition's Hindi confirms 'लग्न या सप्तम'."
)
_V51: Final = "द्यूनेशे नवमे वित्ते नानास्त्रीभिः समागमः । आरम्भी दीर्घसूत्री च स्त्रीषु चित्तं हि केवलम् ॥ ५१ ॥"
_V51_TRANSLATION: Final = (
    "When the lord of the seventh is in the ninth or the second (वित्त), there is union with "
    "many women; the native starts undertakings, is slow to finish them, and his mind is on "
    "women alone. [Hindi: सप्तमेश नवम और दूसरे भाव में हो तो अनेक स्त्रियों में आसक्त, कार्य "
    "को आरंभ करने वाला, दीर्घसूत्री और केवल स्त्री में चित्त को लगाने वाला होता है।]"
)
_V51_REASONING: Final = (
    "द्यूनेश is the seventh lord; नवमे वित्ते names the ninth and the second (वित्त, the house "
    "of wealth); the edition's Hindi agrees. The marriage clauses (नानास्त्रीभिः समागमः, "
    "स्त्रीषु चित्तं हि केवलम्) are judgements about the person's conduct, so the wording is "
    "held. आरम्भी and दीर्घसूत्री (starts undertakings, slow to finish) are not marriage themes "
    "and are not used."
)
_V53: Final = "द्यूनेशे दशमे तुर्ये नास्य जाया पतिव्रता । धर्मात्मा सत्यसंयुक्तः केवलं दन्तरोगवान् ॥ ५३ ॥"
_V53_TRANSLATION: Final = (
    "When the lord of the seventh is in the tenth or the fourth, his wife is not "
    "pativratā (devoted to her husband); the native is righteous and truthful, and has only "
    "a dental ailment. [Hindi: सप्तमेश दशम या चतुर्थ भाव में हो तो जातक की स्त्री पतिव्रता "
    "नहीं होती है।]"
)
_V53_REASONING: Final = (
    "द्यूनेश is the seventh lord; दशमे तुर्ये names the tenth and the fourth. The marriage "
    "clause नास्य जाया पतिव्रता is a judgement about the spouse's fidelity, so the wording is "
    "held. धर्मात्मा and सत्यसंयुक्त (righteous, truthful) describe the person, not the "
    "marriage; the dental clause is a health statement. Neither is used."
)
_V53_NOTES: Final = (
    "Read from the page image. The Hindi agrees on the first clause, but its second sentence "
    "(सर्वगुणसम्पन्न, मानी, सर्व सम्पत्तिमान्) matches v.54, not the printed Sanskrit of v.53 "
    "(धर्मात्मा सत्यसंयुक्तः केवलं दन्तरोगवान्). The Sanskrit is followed; the Hindi second "
    "sentence is treated as a carry-over."
)
_V55: Final = "जायेशे चाष्टमे षष्ठे रोगिणी कामिनी लभेत् । क्रोधयुक्तो भवेद्वापि न सुखं लभते क्वचित् ॥ ५५ ॥"
_V55_TRANSLATION: Final = (
    "When the lord of the seventh is in the eighth or the sixth, the native obtains a sickly "
    "wife; he is given to anger and finds no happiness anywhere. [Hindi: सप्तमेश ६ या ८ भाव "
    "में हो तो जातक की स्त्री रोगिणी होती है। जातक क्रोधी होता है और सुखी नहीं रहता है।]"
)
_V55_REASONING: Final = (
    "जायेश (lord of the house of the wife) is the seventh lord; अष्टमे षष्ठे names the eighth "
    "and the sixth; the edition's Hindi agrees. The marriage clause रोगिणी कामिनी लभेत् is a "
    "health statement about the spouse, and the rest of the verse is phrased in absolute terms "
    "(न सुखं लभते क्वचित्). The wording is held."
)
_V56: Final = "द्वादशस्थे सप्तमेशे दरिद्रः कृपणो महान् । चारुकन्या भवेद्भार्या वस्त्राज्जीवी च निर्धनी ॥ ५६ ॥"


def _justification(
    *,
    verse: int,
    page: str,
    original: str,
    translation: str,
    reasoning: str,
    confidence: ProvisionalConfidence,
    notes: str = "Read from the page image; the Sanskrit and the edition's Hindi agree.",
) -> ProvisionalJustification:
    return ProvisionalJustification(
        source_work=_SOURCE_WORK,
        locator=f"{_CHAPTER}, verse {verse}; {page}.",
        original_text=original,
        draft_translation=translation,
        interpretive_reasoning=reasoning,
        conventions=_MARRIAGE_CONVENTIONS,
        confidence=confidence,
        author=PROVISIONAL_AUTHOR_AI_DRAFTED,
        recorded_at=_RECORDED_AT,
        transcription_notes=notes,
    )


_ORDINAL: Final = {
    1: "first",
    2: "second",
    4: "fourth",
    6: "sixth",
    7: "seventh",
    8: "eighth",
    9: "ninth",
    10: "tenth",
    12: "twelfth",
}


def _marriage_rule(
    house: int,
    justification: ProvisionalJustification,
    *,
    statement: str = HELD_STATEMENT,
    held_reason: str | None = None,
) -> ProvisionalRule:
    rule_id = f"provisional.bphs.d1.house_lord.7.equals_{house}.marriage.v1"
    return ProvisionalRule(
        rule=_placement_rule(
            rule_id=rule_id,
            name=f"D1 seventh-house lord in the {_ORDINAL[house]} house (provisional)",
            domain=JyotishDomain.MARRIAGE,
            lord=7,
            house=house,
        ),
        domain=JyotishDomain.MARRIAGE,
        fact_dependencies=("jyotish.d1.house_lord.7.placement_house",),
        statement=statement,
        justification=justification,
        wording="held" if held_reason is not None else "shown",
        held_reason=held_reason,
    )


RULE_7_IN_1_MARRIAGE: Final = _marriage_rule(
    1,
    _justification(
        verse=50,
        page=_P190,
        original=_V50,
        translation=_V50_TRANSLATION,
        reasoning=(
            "तनौ is the first house. The verse's only marriage clause, परजायासु लम्पटः "
            "(drawn to the wives of others), is a judgement about the person's conduct, so the "
            "wording is held. दुष्ट, विचक्षण, धीर (character) are not marriage themes; the "
            "vāta clause is a health statement. Neither is used."
        ),
        confidence=ProvisionalConfidence.HIGH,
        notes=_V50_NOTES,
    ),
    held_reason=_HELD_ACCUSATORY,
)
RULE_7_IN_7_MARRIAGE: Final = _marriage_rule(
    7,
    _justification(
        verse=50,
        page=_P190,
        original=_V50,
        translation=_V50_TRANSLATION,
        reasoning=(
            "The seventh house is read from चास्ते as च अस्ते (अस्त, a name of the seventh "
            "house); the edition's Hindi says 'लग्न या सप्तम'. Confidence is medium because "
            "the seventh-house condition rests on that reading. The verse's only marriage "
            "clause, परजायासु लम्पटः, is a judgement about the person's conduct, so the wording "
            "is held. The character and vāta clauses are not used."
        ),
        confidence=ProvisionalConfidence.MEDIUM,
        notes=_V50_NOTES,
    ),
    held_reason=_HELD_ACCUSATORY,
)
RULE_7_IN_2_MARRIAGE: Final = _marriage_rule(
    2,
    _justification(
        verse=51,
        page=_P190,
        original=_V51,
        translation=_V51_TRANSLATION,
        reasoning=_V51_REASONING,
        confidence=ProvisionalConfidence.HIGH,
    ),
    held_reason=_HELD_ACCUSATORY,
)
RULE_7_IN_9_MARRIAGE: Final = _marriage_rule(
    9,
    _justification(
        verse=51,
        page=_P190,
        original=_V51,
        translation=_V51_TRANSLATION,
        reasoning=_V51_REASONING,
        confidence=ProvisionalConfidence.HIGH,
    ),
    held_reason=_HELD_ACCUSATORY,
)
RULE_7_IN_4_MARRIAGE: Final = _marriage_rule(
    4,
    _justification(
        verse=53,
        page=_P190,
        original=_V53,
        translation=_V53_TRANSLATION,
        reasoning=_V53_REASONING,
        confidence=ProvisionalConfidence.HIGH,
        notes=_V53_NOTES,
    ),
    held_reason=_HELD_ACCUSATORY,
)
RULE_7_IN_10_MARRIAGE: Final = _marriage_rule(
    10,
    _justification(
        verse=53,
        page=_P190,
        original=_V53,
        translation=_V53_TRANSLATION,
        reasoning=_V53_REASONING,
        confidence=ProvisionalConfidence.HIGH,
        notes=_V53_NOTES,
    ),
    held_reason=_HELD_ACCUSATORY,
)
RULE_7_IN_6_MARRIAGE: Final = _marriage_rule(
    6,
    _justification(
        verse=55,
        page=_P190,
        original=_V55,
        translation=_V55_TRANSLATION,
        reasoning=_V55_REASONING,
        confidence=ProvisionalConfidence.HIGH,
    ),
    held_reason=_HELD_HEALTH,
)
RULE_7_IN_8_MARRIAGE: Final = _marriage_rule(
    8,
    _justification(
        verse=55,
        page=_P190,
        original=_V55,
        translation=_V55_TRANSLATION,
        reasoning=_V55_REASONING,
        confidence=ProvisionalConfidence.HIGH,
    ),
    held_reason=_HELD_HEALTH,
)
RULE_7_IN_12_MARRIAGE: Final = _marriage_rule(
    12,
    _justification(
        verse=56,
        page=_P191,
        original=_V56,
        translation=(
            "When the lord of the seventh is in the twelfth, the native is without means and "
            "very miserly; his wife is a beautiful maiden; he lives by cloth and is without "
            "wealth. [Hindi: सप्तमेश १२वें भाव में हो तो जातक दरिद्र, अत्यंत कृपण, स्त्री "
            "सुंदरी, और वस्त्र से जीविका करने वाला निर्धन होता है।]"
        ),
        reasoning=(
            "The marriage clause is चारुकन्या भवेद्भार्या (the wife is a beautiful maiden); it "
            "is the only clause displayed. दरिद्र, कृपण, वस्त्राज्जीवी and निर्धनी (without "
            "means, miserly, living by cloth, without wealth) are wealth and livelihood "
            "themes, not marriage themes, and are not displayed under Marriage; they are named "
            "here so that nothing is left out silently. Confidence is medium: निर्धनी has a "
            "feminine-looking form, so the last words may describe the wife rather than the "
            "native; the edition's Hindi applies them to the native."
        ),
        confidence=ProvisionalConfidence.MEDIUM,
        notes=(
            "Read from the page image (PDF p. 191, printed p. 193). The Sanskrit and the "
            "edition's Hindi agree; the Hindi renders चारुकन्या भार्या as 'स्त्री सुंदरी'."
        ),
    ),
    statement=(
        "With the D1 seventh-house lord in the twelfth house, the text describes the spouse "
        "as beautiful (चारु)."
    ),
)

MARRIAGE_RULES: Final = (
    RULE_7_IN_1_MARRIAGE,
    RULE_7_IN_2_MARRIAGE,
    RULE_7_IN_4_MARRIAGE,
    RULE_7_IN_6_MARRIAGE,
    RULE_7_IN_7_MARRIAGE,
    RULE_7_IN_8_MARRIAGE,
    RULE_7_IN_9_MARRIAGE,
    RULE_7_IN_10_MARRIAGE,
    RULE_7_IN_12_MARRIAGE,
)

# Located verses that yield no Marriage rule, with the reason (shown in the review pack).
NOT_DRAFTED: Final[dict[str, tuple[str, ...]]] = {
    JyotishDomain.MARRIAGE.value: (
        "Seventh lord in the 3rd or the 11th house: verse 52 (द्यूनेशे सहजे लाभे …), "
        f"{_P190}, located. Its clauses concern children only; it has no marriage clause, so "
        "no Marriage rule is proposed.",
        "Seventh lord in the 5th house: verse 54 (सर्वगुणयुतो मानी …), "
        f"{_P190}, located. It has no marriage clause (virtues, honour, wealth, joy); it is "
        "already the provisional Wealth rule, so no Marriage rule is proposed.",
    ),
}

PROVISIONAL_CORPUS_V2: Final = ProvisionalCorpus(
    corpus_id="jyotish.provisional",
    corpus_version="v2",
    rules=tuple(
        sorted((*PROVISIONAL_CORPUS_V1.rules, *MARRIAGE_RULES), key=lambda rule: rule.rule_id)
    ),
)
ACTIVE_PROVISIONAL_CORPUS: Final = PROVISIONAL_CORPUS_V2
