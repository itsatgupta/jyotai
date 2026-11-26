"""NEXT-PROPERTY-01: provisional corpus v4 (``jyotish.provisional@v4``) adds Property rules.

v4 = the v3 rules, plus:

* **Property** rules for the D1 fourth-house lord, from the BPHS Bhavesha-phala chapter,
  अथ सुखेशभावफलम् (Sukhesha-phala), verses 26–34, PDF pp. 186–187 (printed pp. 188–189),
  read from the local PDF page images (``bphs.selected-edition@v1``).  A verse is drafted only
  where it has a property clause (land, a house, vehicles or possessions).  Of the 12
  placements, one is drafted and shown (the 2nd, v.27: सर्वसम्पद्युत, "endowed with all
  possessions", low confidence); none is held; eleven are not drafted (``NOT_DRAFTED``): their
  verses have no property clause (conduct, the father, learning, wealth earned by effort),
  and two of them (6th, v.31; 8th/12th, v.33) are also accusatory or fear-based.
* **Carry-over (A4):** the NEXT-PROVISIONAL-01 Wealth rule v.54 (7th lord in the 5th) gets a
  new record version, v2: the statement and justification are unchanged, and the full
  translation now stays in the review pack (``translation_held_reason``), like every other
  Wealth item.

Every rule is PROVISIONAL, drafted by an AI agent, pending the project owner's adoption and the
final expert review.
"""

from datetime import UTC, datetime
from typing import Final

from astrologer.knowledge.models import JyotishDomain
from astrologer.knowledge.provisional import (
    PROVISIONAL_AUTHOR_AI_DRAFTED,
    ProvisionalConfidence,
    ProvisionalCorpus,
    ProvisionalJustification,
    ProvisionalRule,
)
from astrologer.knowledge.provisional_pack_v1 import (
    _CONVENTIONS,
    _SOURCE_WORK,
    RULE_7_IN_5_WEALTH,
    _placement_rule,
)
from astrologer.knowledge.provisional_pack_v3 import NOT_DRAFTED as NOT_DRAFTED_V3
from astrologer.knowledge.provisional_pack_v3 import PROVISIONAL_CORPUS_V3
from astrologer.knowledge.provisional_pack_v3 import REVIEWER_QUESTIONS as REVIEWER_QUESTIONS_V3

_RECORDED_AT: Final = datetime(2026, 11, 26, 18, tzinfo=UTC)
_SUKHESHA: Final = "भावेशफलाध्यायः, अथ सुखेशभावफलम् (Sukhesha-phala)"
_PROPERTY_CONVENTIONS: Final = (
    *_CONVENTIONS,
    "The fourth lord is named सुखेश (lord of the house of happiness) and तुर्येश in these verses.",
    "Drafted only where the verse has a property clause (land, a house, vehicles or "
    "possessions); only that clause is displayed, and the full translation stays in the "
    "review pack.",
)

_V27: Final = "सर्वसम्पद्युतो मानी साहसी कुहकान्वितः । कुटुम्बसंयुतो भोगी सुखेशे च धनस्थिते ॥ २७ ॥"

RULE_4_IN_2_PROPERTY: Final = ProvisionalRule(
    rule=_placement_rule(
        rule_id="provisional.bphs.d1.house_lord.4.equals_2.property.v1",
        name="D1 fourth-house lord in the second house (provisional)",
        domain=JyotishDomain.PROPERTY,
        lord=4,
        house=2,
    ),
    domain=JyotishDomain.PROPERTY,
    fact_dependencies=("jyotish.d1.house_lord.4.placement_house",),
    statement=(
        "With the D1 fourth-house lord in the second house, the text describes the native as "
        "endowed with all kinds of possessions (सर्वसम्पद्युत)."
    ),
    justification=ProvisionalJustification(
        source_work=_SOURCE_WORK,
        locator=f"{_SUKHESHA}, verse 27; PDF p. 186 (printed p. 188).",
        original_text=_V27,
        draft_translation=(
            "When the lord of the fourth is in the second (धन), the native is endowed with all "
            "kinds of possessions, honoured, daring, given to trickery, has his family with "
            "him and enjoys pleasures. [Hindi: सुखेश धनभाव में हो तो जातक सभी सम्पत्तियों से "
            "युक्त, मानी, साहसी, इन्द्रजाल करने वाला, कुटुम्ब से युक्त और भोगी होता है।]"
        ),
        interpretive_reasoning=(
            "सुखेश is the fourth lord; धनस्थिते is the second house; the edition's Hindi "
            "agrees. The only clause that touches property is सर्वसम्पद्युत (endowed with all "
            "सम्पद्), which the Hindi renders 'सभी सम्पत्तियों से युक्त' (with all "
            "properties). सम्पद् also means prosperity or riches, and the verse names no land, "
            "house or vehicle, so confidence is low; the expert review decides whether it is a "
            "Property or a Wealth clause. मानी (honoured), साहसी (daring), कुहकान्वित (given "
            "to trickery; Hindi: इन्द्रजाल करने वाला), कुटुम्बसंयुत (with his family) and भोगी "
            "(enjoying pleasures) are not property themes; one is a judgement of conduct. "
            "None of them is displayed."
        ),
        conventions=_PROPERTY_CONVENTIONS,
        confidence=ProvisionalConfidence.LOW,
        author=PROVISIONAL_AUTHOR_AI_DRAFTED,
        recorded_at=_RECORDED_AT,
        transcription_notes=(
            "Read from the page image (PDF p. 186, printed p. 188). The PDF text layer agrees. "
            "The Sanskrit and the edition's Hindi agree."
        ),
    ),
    translation_held_reason=(
        "The verse's other clauses (honour, daring, trickery, the family, pleasures) are not "
        "property themes; only the property clause is shown, and the full translation is kept "
        "for the expert review."
    ),
)

# Carry-over A4: the same rule and wording; the translation is now held like every Wealth item.
RULE_7_IN_5_WEALTH_V2: Final = ProvisionalRule.model_validate(
    {
        **RULE_7_IN_5_WEALTH.model_dump(),
        "rule": RULE_7_IN_5_WEALTH.rule.model_copy(update={"rule_version": "v2"}),
        "translation_held_reason": (
            "Every Wealth item keeps its full translation in the review pack (NEXT-PROPERTY-01). "
            "The statement shown already names each clause of the verse."
        ),
    }
)

PROPERTY_RULES: Final = (RULE_4_IN_2_PROPERTY,)

# Located verses that yield no Property rule, with the reason (shown in the review pack).
NOT_DRAFTED: Final[dict[str, tuple[str, ...]]] = {
    **NOT_DRAFTED_V3,
    JyotishDomain.PROPERTY.value: (
        "Fourth lord in the 1st house: verse 26 (सुखेशे लग्नगे …), PDF p. 186, located (verse "
        "32 also names लग्ने). No property clause (affection of father and son, enmity from the "
        "father's side, fame by the father's name); no Property rule is proposed.",
        "Fourth lord in the 3rd or 11th house: verse 28 (सुखेशे सहजे लाभे …), PDF p. 186, "
        "located. स्वभुजार्जितवित्तवान् (wealth earned by one's own effort) is a wealth "
        "clause, not a property clause; नित्यरोगी (always ill) is a health statement. No "
        "Property rule is proposed.",
        "Fourth lord in the 4th house: verse 29 (तुर्येशे तुर्यगे …), PDF pp. 186–187, located. "
        "सर्वधनाधिप (master of all wealth) and धनाढ्य (rich) are wealth (धन) clauses; the "
        "edition's Hindi renders सर्वधनाधिप as 'सभी प्रकार की संपत्ति'. No Property rule is "
        "proposed; the question is in the reviewer questions.",
        "Fourth lord in the 5th or 9th house: verse 30 (तुर्येशे पञ्चमे भाग्ये …), PDF p. 187, "
        "located. No property clause (happiness, popularity, devotion, honour, wealth earned by "
        "effort); no Property rule is proposed.",
        "Fourth lord in the 6th house: verse 31 (सुखेशे शत्रुगेहस्थे …), PDF p. 187, located. "
        "No property clause; its clauses are accusatory judgements (anger, theft, sorcery). "
        "Not drafted and nothing is shown.",
        "Fourth lord in the 7th house: verse 32 (सुखेशे सप्तमे लग्ने …), PDF p. 187, located. "
        "No property clause (learning, giving up the father's wealth, silence in an assembly); "
        "no Property rule is proposed.",
        "Fourth lord in the 8th or 12th house: verse 33 (सुखेशे व्ययरन्ध्रस्थे …), PDF p. 187, "
        "located. No property clause; it predicts a lack of happiness and makes accusatory "
        "statements about the native's birth. Not drafted and nothing is shown.",
        "Fourth lord in the 10th house: verse 34 (सुखेशे कर्मगेहस्थे …), PDF p. 187, located. No "
        "property clause (royal honour, alchemy, delight, happiness); no Property rule is "
        "proposed.",
        "4th-house terms that are not property terms (द्वादशभावविचाराध्यायः v.4, PDF p. 147): "
        "बन्धु (relatives) and मातृसौख्य (the mother's happiness) belong to a relatives, mother "
        "or happiness domain, which JyotAI does not have, so they are neither tagged Property "
        "nor drafted; निधि (treasure; Hindi: गड़े धन, buried wealth) is a wealth matter, not "
        "land, a house or a vehicle, and is not drafted.",
    ),
}

REVIEWER_QUESTIONS: Final[tuple[tuple[str, str], ...]] = (
    *REVIEWER_QUESTIONS_V3,
    (
        "Which kārakas should a Property answer use?",
        "कारकाध्यायः, अथ सूर्यादिग्रहाणां कारकत्वमाह, PDF p. 109 (printed p. 111): Mars is "
        "the kāraka of भूमि (land) and सद्म (dwelling; the Hindi omits सद्म), v.3; Jupiter of "
        "गृह (house), v.5; Venus of यान (vehicles), v.6; the Sun of क्षेत्र (field or region), "
        "v.1. The bhāva-kāraka list (v.37, PDF p. 108) gives the 4th house to सोमः (Moon) in "
        "the Sanskrit and to Mercury in the Hindi, without naming property. JyotAI's Property "
        "answer lists Mars, Jupiter and Venus (each has a high-confidence property term); the "
        "Sun's क्षेत्र is a provisional signification (medium) only. Which kārakas are right, "
        "and how does v.37 fit?",
    ),
    (
        "Are सम्पद् (v.27) and the Hindi संपत्ति for सर्वधनाधिप (v.29) property or wealth?",
        "Fourth lord in the 2nd (v.27): सर्वसम्पद्युत, Hindi 'सभी सम्पत्तियों से युक्त', drafted "
        "for Property at low confidence. Fourth lord in the 4th (v.29): सर्वधनाधिप, धनाढ्य "
        "(wealth), which the Hindi renders 'सभी प्रकार की संपत्ति'; not drafted. Should either "
        "be a Property item, a Wealth item, or neither?",
    ),
    (
        "Should D4 (Chaturthāṁśa) be calculated and shown for property, and by which method?",
        "JyotAI calculates D1, D2, D9 and D10 only; no D4 is shown. A reviewer-approved D4 "
        "method (and whether any D4 reading belongs in a Property answer) is needed first.",
    ),
)

PROVISIONAL_CORPUS_V4: Final = ProvisionalCorpus(
    corpus_id="jyotish.provisional",
    corpus_version="v4",
    rules=tuple(
        sorted(
            (
                *(
                    RULE_7_IN_5_WEALTH_V2 if rule.rule_id == RULE_7_IN_5_WEALTH.rule_id else rule
                    for rule in PROVISIONAL_CORPUS_V3.rules
                ),
                *PROPERTY_RULES,
            ),
            key=lambda rule: rule.rule_id,
        )
    ),
)
ACTIVE_PROVISIONAL_CORPUS: Final = PROVISIONAL_CORPUS_V4
