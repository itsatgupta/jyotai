"""NEXT-WEALTH-01: provisional corpus v3 (``jyotish.provisional@v3``) adds Wealth rules.

v3 = the v2 rules, unchanged, plus provisional Wealth rules for the D1 second-house lord from
the BPHS Bhavesha-phala chapter, अथ धनेशभावफलम् (Dhanesha-phala), verses 9–18, PDF pp. 183–185
(printed pp. 185–187).  The eleventh-lord verses (अथ लाभेशभावफलम्, vv. 78–85, PDF pp. 194–195)
were read too.  Every rule is PROVISIONAL, drafted by an AI agent, pending the project owner's
adoption and the final expert review.  The original text was read from the local PDF page
images (``bphs.selected-edition@v1``).

A verse is drafted only where it names wealth or gain (धन, धनवान्, द्रव्य, लभेत्):

* **Shown** (2nd lord in the 1st, 2nd, 5th, 8th, 9th, 10th, 11th): the wealth clause alone is
  stated.  Each verse's other clauses (conduct, spouses, sons, illness) are not wealth themes,
  so its translation stays in the review pack (``translation_held_reason``).
* **Held** (2nd lord in the 6th, v.13: a loss of wealth, वित्तनाश; in the 12th, v.18: without
  wealth, धनवर्जित): owner rule, a verse that predicts poverty or loss is held, not shown.
* **Not drafted**: the verses with no wealth clause, and the eleventh-lord placements that
  already have a reviewed Wealth rule (``NOT_DRAFTED``).
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
from astrologer.knowledge.provisional_pack_v1 import _CONVENTIONS, _SOURCE_WORK, _placement_rule
from astrologer.knowledge.provisional_pack_v2 import NOT_DRAFTED as NOT_DRAFTED_V2
from astrologer.knowledge.provisional_pack_v2 import PROVISIONAL_CORPUS_V2

_RECORDED_AT: Final = datetime(2026, 11, 26, 12, tzinfo=UTC)
_CHAPTER: Final = "भावेशफलाध्यायः, अथ धनेशभावफलम् (Dhanesha-phala)"
_LABHESHA: Final = "भावेशफलाध्यायः, अथ लाभेशभावफलम् (Labhesha-phala)"
_P183: Final = "PDF p. 183 (printed p. 185); Hindi PDF p. 184"
_P184: Final = "PDF p. 184 (printed p. 186)"
_P184_185: Final = "PDF p. 184 (printed p. 186); Hindi PDF p. 185"
_P185: Final = "PDF p. 185 (printed p. 187)"
_WEALTH_CONVENTIONS: Final = (
    *_CONVENTIONS,
    "The second lord is named धनेश (lord of the house of wealth) and वित्तेश in these verses.",
    "Only the verse's wealth clause is displayed; its other clauses are named in the "
    "reasoning and kept, with the full translation, in the review pack.",
)
_HELD_LOSS: Final = (
    "The verse predicts a loss of wealth. Owner rule: a verse that predicts poverty or loss is "
    "held, not shown; the expert review decides the wording."
)
_HELD_POVERTY: Final = (
    "The verse predicts being without wealth. Owner rule: a verse that predicts poverty or "
    "loss is held, not shown; the expert review decides the wording."
)
_TRANSLATION_HELD: Final = (
    "The verse's other clauses ({clauses}) are not wealth themes; only the wealth clause is "
    "shown, and the full translation is kept for the expert review."
)

_V9: Final = "धनेशे च तनौ पुत्री स्वकुटुम्बस्य कण्टकः । धनवान्निष्ठुरः कामी परकार्येषु तत्परः ॥ ९ ॥"
_V10: Final = "धनेशे धनगे मर्त्यः धनवान् गर्वसंयुतः । भार्याद्वयं त्रयं वापि पुत्रहीनः प्रजायते ॥ १० ॥"
_V12: Final = "धनेशे सुतभावस्थे पुत्रतो धनवान् भवेत् । कृपणो दुःखभाग्जातो यशस्वी पुत्रवान् भवेत् ॥ १२ ॥"
_V13: Final = "धनेशे शत्रुगे शत्रोर्धनं प्राप्नोति निश्चितम् । शत्रुतो वित्तनाशः स्याज्जंघोर्वोर्भवेच्च रुक् ॥ १३ ॥"
_V15: Final = "धनेशे मृत्युगेहस्थे भूमिद्रव्यं लभेद् ध्रुवम् । जायासौख्यं भवेत्स्वल्पं ज्येष्ठभ्रातृसुखं न हि ॥ १५ ॥"
_V16: Final = "धनेशे नवमे लाभे धनवानुद्यमी पटुः । बाल्ये रोगी सुखी पश्चाद्यावदायुः समाप्यते ॥ १६ ॥"
_V17: Final = "धनेशो दशमे यस्य कामी मानी च पण्डितः । बहुदारधनैर्युक्तः सुतहीनो प्रजायते ॥ १७ ॥"
_V18: Final = "धनेशे व्ययगे ज्ञानी साहसी धनवर्जितः । जीविका नृपगेहाच्च ज्येष्ठपुत्रसुखं न हि ॥ १८ ॥"

_V16_TRANSLATION: Final = (
    "When the lord of the second is in the ninth or the eleventh (लाभ), the native is wealthy, "
    "enterprising and skilful; ill in childhood, he is happy afterwards for the rest of his "
    "life. [Hindi: धनेश नवम भाव वा लाभभाव में हो तो जातक धनी, उद्यमी, विद्वान् होता है। "
    "बाल्य अवस्था में रोगी और पीछे आयु पर्यंत सुखी होता है।]"
)
_V16_REASONING: Final = (
    "धनेश is the second lord; नवमे लाभे names the ninth and the eleventh; the edition's Hindi "
    "agrees. The wealth clause is धनवान् (wealthy), with उद्यमी (enterprising); both are "
    "displayed. पटु (skilful; the Hindi has विद्वान्, learned) is a quality of the person, and "
    "बाल्ये रोगी (ill in childhood) is a health statement; neither is displayed."
)
_V16_NOTES: Final = (
    "Read from the page images (Sanskrit at the foot of PDF p. 184, Hindi at the top of PDF "
    "p. 185). The Hindi renders पटु as विद्वान् (learned)."
)


def _justification(
    *,
    verse: int,
    page: str,
    original: str,
    translation: str,
    reasoning: str,
    confidence: ProvisionalConfidence,
    notes: str = "Read from the page image; the Sanskrit and the edition's Hindi agree.",
    chapter: str = _CHAPTER,
) -> ProvisionalJustification:
    return ProvisionalJustification(
        source_work=_SOURCE_WORK,
        locator=f"{chapter}, verse {verse}; {page}.",
        original_text=original,
        draft_translation=translation,
        interpretive_reasoning=reasoning,
        conventions=_WEALTH_CONVENTIONS,
        confidence=confidence,
        author=PROVISIONAL_AUTHOR_AI_DRAFTED,
        recorded_at=_RECORDED_AT,
        transcription_notes=notes,
    )


_ORDINAL: Final = {
    1: "first",
    2: "second",
    5: "fifth",
    6: "sixth",
    8: "eighth",
    9: "ninth",
    10: "tenth",
    11: "eleventh",
    12: "twelfth",
}


def _wealth_rule(
    house: int,
    justification: ProvisionalJustification,
    *,
    statement: str = HELD_STATEMENT,
    held_reason: str | None = None,
    translation_held: str | None = None,
) -> ProvisionalRule:
    rule_id = f"provisional.bphs.d1.house_lord.2.equals_{house}.wealth.v1"
    return ProvisionalRule(
        rule=_placement_rule(
            rule_id=rule_id,
            name=f"D1 second-house lord in the {_ORDINAL[house]} house (provisional)",
            domain=JyotishDomain.WEALTH,
            lord=2,
            house=house,
        ),
        domain=JyotishDomain.WEALTH,
        fact_dependencies=("jyotish.d1.house_lord.2.placement_house",),
        statement=statement,
        justification=justification,
        wording="held" if held_reason is not None else "shown",
        held_reason=held_reason,
        translation_held_reason=(
            _TRANSLATION_HELD.format(clauses=translation_held) if translation_held else None
        ),
    )


def _shown(house: int, clause: str) -> str:
    return f"With the D1 second-house lord in the {_ORDINAL[house]} house, the text {clause}."


RULE_2_IN_1_WEALTH: Final = _wealth_rule(
    1,
    _justification(
        verse=9,
        page=_P183,
        original=_V9,
        translation=(
            "When the lord of the second is in the first (तनु), the native has sons, is a thorn "
            "to his own family, wealthy, harsh, lustful and busy with others' affairs. [Hindi: "
            "धनेश लग्न में हो तो जातक पुत्रवान्, अपने कुटुम्ब का कंटक, धनी, निष्ठुर, कामी और "
            "दूसरे के कार्य में तत्पर होता है।]"
        ),
        reasoning=(
            "धनेश is the second lord; तनौ is the first house; the edition's Hindi agrees. The "
            "wealth clause is धनवान् (wealthy); it is the only clause displayed. पुत्री (has "
            "sons), स्वकुटुम्बस्य कण्टकः (a thorn to his family), निष्ठुर (harsh), कामी "
            "(lustful) and परकार्येषु तत्परः (busy with others' affairs) are not wealth themes; "
            "several are judgements of conduct and are not displayed."
        ),
        confidence=ProvisionalConfidence.HIGH,
        notes=(
            "Read from the page images (Sanskrit at the foot of PDF p. 183, Hindi at the top "
            "of PDF p. 184). The PDF text layer reads धनवातरिष्ठुरः for धनवान्निष्ठुरः."
        ),
    ),
    statement=_shown(1, "describes the native as wealthy (धनवान्)"),
    translation_held="sons, the family, conduct",
)
RULE_2_IN_2_WEALTH: Final = _wealth_rule(
    2,
    _justification(
        verse=10,
        page=_P184,
        original=_V10,
        translation=(
            "When the lord of the second is in the second, the person is wealthy and proud; he "
            "has two or three wives and is without sons. [Hindi: धनेश धनभाव में हो जातक धनी, "
            "धर्म से युक्त होता है। उसे २ या ३ स्त्रियाँ होती है और पुत्रहीन होता है।]"
        ),
        reasoning=(
            "धनगे (in the house of wealth) is the second house. The wealth clause is धनवान् "
            "(wealthy); it is the only clause displayed. गर्वसंयुत (proud), the number of wives "
            "and पुत्रहीन (without sons) are not wealth themes and are not displayed."
        ),
        confidence=ProvisionalConfidence.HIGH,
        notes=(
            "Read from the page image (PDF p. 184, printed p. 186). The Hindi renders "
            "गर्वसंयुतः (proud) as 'धर्म से युक्त' (righteous); the Sanskrit is followed. The "
            "wealth clause is the same in both."
        ),
    ),
    statement=_shown(2, "describes the native as wealthy (धनवान्)"),
    translation_held="pride, wives, sons",
)
RULE_2_IN_5_WEALTH: Final = _wealth_rule(
    5,
    _justification(
        verse=12,
        page=_P184,
        original=_V12,
        translation=(
            "When the lord of the second is in the fifth, the native becomes wealthy through a "
            "son; he is miserly, has his share of sorrow, is famous and has sons. [Hindi: धनेश "
            "पाँचवें भाव में हो तो पुत्र से धनी, कृपण, दुःख भोगने वाला, यशस्वी और पुत्रवान् "
            "होता है।]"
        ),
        reasoning=(
            "सुतभाव is the fifth house. The wealth clause is पुत्रतो धनवान् (wealthy through a "
            "son); it is the only clause displayed. कृपण (miserly), दुःखभाक् (sharing in "
            "sorrow), यशस्वी (famous) and पुत्रवान् (has sons) are not wealth themes and are "
            "not displayed."
        ),
        confidence=ProvisionalConfidence.HIGH,
    ),
    statement=_shown(5, "describes wealth through a son (पुत्रतो धनवान्)"),
    translation_held="miserliness, sorrow, fame, sons",
)
RULE_2_IN_6_WEALTH: Final = _wealth_rule(
    6,
    _justification(
        verse=13,
        page=_P184,
        original=_V13,
        translation=(
            "When the lord of the second is in the sixth, the native certainly obtains wealth "
            "from an enemy; through an enemy there is a loss of wealth, and an ailment of the "
            "shanks and thighs. [Hindi: धनेश छठे भाव में हो तो शत्रु से धन प्राप्त करने वाला, "
            "पुत्र द्वारा धन नाश वाला और जंघा तथा उरु प्रदेश में रोग युक्त होता है।]"
        ),
        reasoning=(
            "शत्रुगे is the sixth house. The verse pairs wealth from an enemy (शत्रोर्धनं "
            "प्राप्नोति) with a loss of wealth (वित्तनाशः) and an illness, stated as certain "
            "(निश्चितम्). Owner rule: a verse that predicts loss is held; nothing is displayed."
        ),
        confidence=ProvisionalConfidence.HIGH,
        notes=(
            "Read from the page image (PDF p. 184). The Sanskrit has शत्रुतो वित्तनाशः (loss "
            "of wealth through an enemy); the Hindi has 'पुत्र द्वारा धन नाश' (through a son), "
            "probably a misprint; the Sanskrit is followed."
        ),
    ),
    held_reason=_HELD_LOSS,
)
RULE_2_IN_8_WEALTH: Final = _wealth_rule(
    8,
    _justification(
        verse=15,
        page=_P184,
        original=_V15,
        translation=(
            "When the lord of the second is in the eighth, the native surely gains wealth from "
            "the ground (or land and goods); there is little happiness from the wife and no "
            "happiness from an elder brother. [Hindi: धनेश आठवें भाव में हो तो जातक को भूमिगत "
            "द्रव्य का लाभ, स्त्री का सुख अल्प और ज्येष्ठ भाई का सुख नहीं होता है।]"
        ),
        reasoning=(
            "मृत्युगेह is the eighth house. The wealth clause is भूमिद्रव्यं लभेत् (gains "
            "भूमिद्रव्य); it is the only clause displayed, without the verse's ध्रुवम् "
            "(surely), which would state a certainty. Confidence is medium: भूमिद्रव्य may be "
            "'land and goods' or 'wealth from the ground'; the edition's Hindi reads भूमिगत "
            "द्रव्य (buried wealth). The clauses about the wife and an elder brother are not "
            "wealth themes and are not displayed."
        ),
        confidence=ProvisionalConfidence.MEDIUM,
    ),
    statement=_shown(8, "describes a gain of wealth connected with land (भूमिद्रव्य)"),
    translation_held="the wife, an elder brother",
)
RULE_2_IN_9_WEALTH: Final = _wealth_rule(
    9,
    _justification(
        verse=16,
        page=_P184_185,
        original=_V16,
        translation=_V16_TRANSLATION,
        reasoning=_V16_REASONING,
        confidence=ProvisionalConfidence.HIGH,
        notes=_V16_NOTES,
    ),
    statement=_shown(9, "describes the native as wealthy (धनवान्) and enterprising (उद्यमी)"),
    translation_held="childhood illness, later happiness",
)
RULE_2_IN_11_WEALTH: Final = _wealth_rule(
    11,
    _justification(
        verse=16,
        page=_P184_185,
        original=_V16,
        translation=_V16_TRANSLATION,
        reasoning=_V16_REASONING,
        confidence=ProvisionalConfidence.HIGH,
        notes=_V16_NOTES,
    ),
    statement=_shown(11, "describes the native as wealthy (धनवान्) and enterprising (उद्यमी)"),
    translation_held="childhood illness, later happiness",
)
RULE_2_IN_10_WEALTH: Final = _wealth_rule(
    10,
    _justification(
        verse=17,
        page=_P185,
        original=_V17,
        translation=(
            "He whose second lord is in the tenth is lustful, honoured and learned; he is "
            "endowed with many wives and wealth, and is without sons. [Hindi: धनेश दशम भाव में "
            "हो तो जातक कामी, मानी, पंडित, अनेक स्त्री तथा धन से युक्त और पुत्रहीन होता है।]"
        ),
        reasoning=(
            "दशमे is the tenth house. The wealth clause is in the compound बहुदारधनैर्युक्तः "
            "(endowed with many wives and wealth); only 'wealth (धन)' is displayed. Confidence "
            "is medium: बहु may qualify both wives and wealth ('much wealth'); the statement "
            "claims no amount. कामी, मानी, पण्डित (lustful, honoured, learned), the wives and "
            "सुतहीन (without sons) are not wealth themes and are not displayed."
        ),
        confidence=ProvisionalConfidence.MEDIUM,
    ),
    statement=_shown(10, "associates the placement with wealth (धन)"),
    translation_held="conduct, wives, sons",
)
RULE_2_IN_12_WEALTH: Final = _wealth_rule(
    12,
    _justification(
        verse=18,
        page=_P185,
        original=_V18,
        translation=(
            "When the lord of the second is in the twelfth, the native is wise and daring but "
            "without wealth; his livelihood comes from the king's house, and there is no "
            "happiness from the eldest son. [Hindi: धनेश बारहवें भाव में हो तो जातक ज्ञानी, "
            "साहसी, धनहीन, राजगृह से जीविकावाला और ज्येष्ठ पुत्र के सुख से हीन होता है।]"
        ),
        reasoning=(
            "व्ययगे is the twelfth house. The wealth clause is धनवर्जितः (without wealth). "
            "Owner rule: a verse that predicts poverty is held; nothing is displayed."
        ),
        confidence=ProvisionalConfidence.HIGH,
    ),
    held_reason=_HELD_POVERTY,
)

WEALTH_RULES: Final = (
    RULE_2_IN_1_WEALTH,
    RULE_2_IN_2_WEALTH,
    RULE_2_IN_5_WEALTH,
    RULE_2_IN_6_WEALTH,
    RULE_2_IN_8_WEALTH,
    RULE_2_IN_9_WEALTH,
    RULE_2_IN_10_WEALTH,
    RULE_2_IN_11_WEALTH,
    RULE_2_IN_12_WEALTH,
)

# Located verses that yield no Wealth rule, with the reason (shown in the review pack).
NOT_DRAFTED: Final[dict[str, tuple[str, ...]]] = {
    **NOT_DRAFTED_V2,
    JyotishDomain.WEALTH.value: (
        "Second lord in the 3rd or the 4th house: verse 11 (धनेशे सहजे तुर्ये …), PDF p. 184, "
        "located. It has no wealth clause (valour, intelligence, conduct; लोभी, greedy, is "
        "not wealth), so no Wealth rule is proposed.",
        "Second lord in the 7th house: verse 14 (धनेशे सप्तमे …), PDF p. 184, located. It has "
        "no wealth clause; its clauses are accusatory judgements about the native's family. "
        "No Wealth rule is proposed and nothing is shown.",
        "Eleventh lord in the 1st (v.78), the 2nd or 5th (v.79) and the 9th or 10th (v.83), "
        f"{_LABHESHA}, PDF p. 194: these placements already have reviewed Wealth rules "
        "(jyotish.production.cumulative); no provisional rule duplicates them.",
        "Eleventh lord in the 3rd or 4th (v.80), the 6th (v.81), the 11th (v.84) and the 12th "
        f"(v.85), {_LABHESHA}, PDF pp. 194–195, located: no wealth clause (pilgrimage, "
        "illness, eloquence, conduct), so no Wealth rule is proposed.",
        "Eleventh lord in the 7th or 8th: verse 82 (लाभेशे सप्तमे रन्ध्रे भार्या तस्य न "
        f"जीवति …), {_LABHESHA}, PDF p. 194, located. It has no wealth clause and predicts the "
        "loss of the wife; it is not drafted and nothing is shown.",
    ),
}

# Open questions for the final expert review (printed at the end of the review pack).
REVIEWER_QUESTIONS: Final[tuple[tuple[str, str], ...]] = (
    (
        "Which house is the kāraka of the wife: the 2nd (v.35) or the 7th (v.36)?",
        "कारकाध्याय, अथ भावकारकमाह, PDF p. 108 (printed p. 110). v.35: धनभावं "
        "विजानीयाद्दारकारकमेव च (the house of wealth, the 2nd, is also the kāraka of the wife; "
        "Hindi: धनभाव स्त्रीकारक). v.36: सुते सुतं विजानीयाद्दारा सप्तमभावतः (sons from the 5th, "
        "the wife from the 7th; Hindi: सातवाँ स्त्री का कारक). JyotAI drafted no Marriage term "
        "from v.35: the 2nd-house term कुटुम्ब (family) was first proposed for Marriage (low) "
        "and is now proposed for Wealth only, and the 7th house carries जाया. Should the 2nd "
        "house carry any Marriage term, and how do v.35 and v.36 fit together?",
    ),
    (
        "May the reviewed Career terms of the 2nd and 11th houses also be tagged Wealth?",
        "The reviewed signification terms धन ('wealth', 2nd house) and लाभ ('gain'), वृद्धि "
        "('increase', 11th house) were reviewed for Career only, so a Wealth answer does not "
        "show them. The provisional Wealth terms धन (2nd house), लाभ (11th house) and Jupiter "
        "as kāraka of धन are drafted separately. If the reviewed terms may be tagged Wealth "
        "(reviewed), the matching provisional terms would be withdrawn.",
    ),
    (
        "Wording for the held 2nd-lord verses (6th: v.13; 12th: v.18)",
        "Both verses are recorded in full above but held in the app (owner rule: no verse "
        "predicting poverty or loss is shown). Should either be shown, and with what wording?",
    ),
)

PROVISIONAL_CORPUS_V3: Final = ProvisionalCorpus(
    corpus_id="jyotish.provisional",
    corpus_version="v3",
    rules=tuple(
        sorted((*PROVISIONAL_CORPUS_V2.rules, *WEALTH_RULES), key=lambda rule: rule.rule_id)
    ),
)
ACTIVE_PROVISIONAL_CORPUS: Final = PROVISIONAL_CORPUS_V3
