"""NEXT-PROVISIONAL-01: the first provisional corpus (``jyotish.provisional@v1``).

Every rule here is PROVISIONAL: authored as "project owner, provisional", pending the
final expert review (``research/final-review/review-pack.md``).  None of it is reviewed,
none of it is in the production release, and it is shown only when a request sets
``include_provisional`` (web: "Show provisional interpretations (beta)").

Source text: the selected BPHS edition already cited by the reviewed packs
(``bphs.selected-edition@v1``), Bhavesha-phala chapter (भावेशफलाध्यायः).  The original
text was read from the local PDF page images; OCR noise in the PDF's text layer was
corrected by eye, and every such reading is listed in ``transcription_notes``.  The
draft translations follow the edition's adjacent Hindi rendering.

Each compound passage is recorded whole in the justification; the displayed statement
leaves out no clause silently: a clause not displayed is named in the reasoning.
"""

from datetime import UTC, datetime
from typing import Final

from astrologer.knowledge.models import JyotishDomain
from astrologer.knowledge.provisional import (
    PROVISIONAL_AUTHOR,
    PROVISIONAL_RULESET_VERSION,
    ProvisionalConfidence,
    ProvisionalCorpus,
    ProvisionalJustification,
    ProvisionalRule,
)
from astrologer.rules.models import (
    ConditionDefinition,
    ConditionKind,
    ConditionOperation,
    RuleDefinition,
    RuleEffect,
)

_RECORDED_AT: Final = datetime(2026, 11, 24, tzinfo=UTC)
_SOURCE_WORK: Final = "Brihat Parashara Hora Shastra (selected edition, bphs.selected-edition@v1)"
_CONVENTIONS: Final = (
    "Houses counted from the D1 Lagna, Whole Sign (reviewer convention, Sitting 2 item 18).",
    "Classical seven-planet sign lordship; the house lord's placement is a deterministic "
    "D1 fact (jyotish-derived-facts-v1).",
    "Static, contextual natal evidence only: no polarity, weight, timing or prediction.",
    "Sanskrit term kept, controlled English gloss displayed (reviewer convention, Sitting 2 "
    "item 20).",
)


def _placement_rule(
    *, rule_id: str, name: str, domain: JyotishDomain, lord: int, house: int
) -> RuleDefinition:
    return RuleDefinition(
        rule_id=rule_id,
        rule_version="v1",
        ruleset_version=PROVISIONAL_RULESET_VERSION,
        name=name,
        domain=domain.value,
        condition=ConditionDefinition(
            kind=ConditionKind.LEAF,
            operation=ConditionOperation.EQUALS,
            fact_id=f"jyotish.d1.house_lord.{lord}.placement_house",
            expected_value=house,
        ),
        effect=RuleEffect(effect_key=f"{rule_id}.contextual", label="Provisional natal context"),
    )


RULE_5_IN_4_EDUCATION: Final = ProvisionalRule(
    rule=_placement_rule(
        rule_id="provisional.bphs.d1.house_lord.5.equals_4.education.v1",
        name="D1 fifth-house lord in the fourth house (provisional)",
        domain=JyotishDomain.EDUCATION,
        lord=5,
        house=4,
    ),
    domain=JyotishDomain.EDUCATION,
    fact_dependencies=("jyotish.d1.house_lord.5.placement_house",),
    statement=(
        "With the D1 fifth-house lord in the fourth house, the text associates the placement "
        "with intelligence (सुबुद्धि) and with an adviser's or teacher's role (सचिव, गुरु). "
        "The same verse also names lasting comfort from the mother and prosperity (लक्ष्मी)."
    ),
    justification=ProvisionalJustification(
        source_work=_SOURCE_WORK,
        locator=(
            "भावेशफलाध्यायः, अथ सुतेशभावफलम् (Sutesha-phala), verse 37; PDF p. 188 (printed p. 190)."
        ),
        original_text=("सुतेशे मातृभवने चिरं मातृसुखं भवेत् । लक्ष्मीयुक्तः सुबुद्धिश्च सचिवोऽप्यथवा गुरुः ॥ ३७ ॥"),
        draft_translation=(
            "When the lord of the fifth is in the fourth (the house of the mother), there is "
            "long-lasting happiness from the mother; the native is endowed with prosperity "
            "(Lakshmi), of sound intelligence, and a minister/adviser or else a teacher (guru)."
        ),
        interpretive_reasoning=(
            "The fifth house is read for intelligence and learning; the verse names सुबुद्धि "
            "(sound intelligence) and two roles that rest on learning, सचिव (adviser) and गुरु "
            "(teacher). That is why the rule is proposed for Education rather than Career. "
            "The mother-comfort and prosperity clauses are kept in the displayed statement, "
            "not dropped. The edition's Hindi rendering continues with qualities (knowing "
            "muhurta, crooked speech, wealthy) that are not in the Sanskrit of v.37; they are "
            "treated as a carry-over and not used."
        ),
        conventions=_CONVENTIONS,
        confidence=ProvisionalConfidence.MEDIUM,
        author=PROVISIONAL_AUTHOR,
        recorded_at=_RECORDED_AT,
        transcription_notes=(
            "Read from the page image; the PDF text layer drops the first line. The Hindi "
            "rendering's second sentence (मुहूर्त को जानने वाला, टेढ़ा बोलने वाला, धनी और "
            "बुद्धिमान्) has no counterpart in the printed Sanskrit."
        ),
    ),
)

RULE_5_IN_7_SPIRITUALITY: Final = ProvisionalRule(
    rule=_placement_rule(
        rule_id="provisional.bphs.d1.house_lord.5.equals_7.spirituality.v1",
        name="D1 fifth-house lord in the seventh house (provisional)",
        domain=JyotishDomain.SPIRITUALITY,
        lord=5,
        house=7,
    ),
    domain=JyotishDomain.SPIRITUALITY,
    fact_dependencies=("jyotish.d1.house_lord.5.placement_house",),
    statement=(
        "With the D1 fifth-house lord in the seventh house, the text associates the placement "
        "with adherence to every dharma (सर्वधर्मसमन्वित), single-minded devotion (भक्ति) "
        "and being held in honour (मानी)."
    ),
    justification=ProvisionalJustification(
        source_work=_SOURCE_WORK,
        locator=(
            "भावेशफलाध्यायः, अथ सुतेशभावफलम् (Sutesha-phala), verse 40; PDF p. 188 (printed p. 190)."
        ),
        original_text=("सुतेशे कामगे मानी सर्वधर्मसमन्वितः । तुंगबष्टिस्तनुस्वामी भक्तियुक्तैकचेतसा ॥ ४० ॥"),
        draft_translation=(
            "When the lord of the fifth is in the seventh, the native is proud/honoured, endowed "
            "with all dharmas, [tall-nosed (per the Hindi)], and devoted with a single-pointed "
            "mind."
        ),
        interpretive_reasoning=(
            "सर्वधर्मसमन्वित (endowed with every dharma) and भक्तियुक्तैकचेतसा (single-minded "
            "devotion) are religious and devotional qualities, so the rule is proposed for "
            "Spirituality. The physical description (ऊँचे नाक वाला in the Hindi) is not a "
            "spirituality theme and is not displayed. Confidence is low because line 2 is "
            "uncertain: the printed तुंगबष्टि looks like a misprint, and तनुस्वामी could be read "
            "as a second condition involving the Lagna lord. If it is a condition, this "
            "formalization (fifth lord in the seventh only) is incomplete."
        ),
        conventions=_CONVENTIONS,
        confidence=ProvisionalConfidence.LOW,
        author=PROVISIONAL_AUTHOR,
        recorded_at=_RECORDED_AT,
        transcription_notes=(
            "Printed तुंगबष्टिस्तनुस्वामी kept as printed (likely misprint; the Hindi reads "
            "'ऊँचे नाक वाला', tall-nosed). The PDF text layer reads तुंगबष्टिस्तनुस्वाधी and "
            "भर्तियुक्तैकचेतसा; the page image shows स्वामी and भक्ति."
        ),
    ),
)

RULE_7_IN_5_WEALTH: Final = ProvisionalRule(
    rule=_placement_rule(
        rule_id="provisional.bphs.d1.house_lord.7.equals_5.wealth.v1",
        name="D1 seventh-house lord in the fifth house (provisional)",
        domain=JyotishDomain.WEALTH,
        lord=7,
        house=5,
    ),
    domain=JyotishDomain.WEALTH,
    fact_dependencies=("jyotish.d1.house_lord.7.placement_house",),
    statement=(
        "With the D1 seventh-house lord in the fifth house, the text associates the placement "
        "with possessing wealth of every kind (सर्वधनाधिप), with being held in honour (मानी), "
        "with many qualities, and with constant cheerfulness."
    ),
    justification=ProvisionalJustification(
        source_work=_SOURCE_WORK,
        locator=(
            "भावेशफलाध्यायः, अथ सप्तमेशभावफलम् (Saptamesha-phala), verse 54; PDF p. 190 "
            "(printed p. 192)."
        ),
        original_text=("सर्वगुणयुतो मानी भवेत्सर्वधनाधिपः । सदैव हर्षसंयुक्तः सप्तमेशे सुते स्थिते ॥ ५४ ॥"),
        draft_translation=(
            "When the lord of the seventh is placed in the fifth, the native is endowed with all "
            "virtues, honoured, master of all kinds of wealth, and always joyful."
        ),
        interpretive_reasoning=(
            "The central term is सर्वधनाधिप (master of every kind of wealth), so the rule is "
            "proposed for Wealth. The other clauses (virtues, honour, joy) are kept in the "
            "displayed statement. The verse gives no amount, source or timing of wealth, and "
            "the rule claims none."
        ),
        conventions=_CONVENTIONS,
        confidence=ProvisionalConfidence.HIGH,
        author=PROVISIONAL_AUTHOR,
        recorded_at=_RECORDED_AT,
        transcription_notes=(
            "Read from the page image; the PDF text layer reads भानी for मानी. Sanskrit and "
            "Hindi agree."
        ),
    ),
)

PROVISIONAL_CORPUS_V1: Final = ProvisionalCorpus(
    corpus_id="jyotish.provisional",
    corpus_version="v1",
    rules=tuple(
        sorted(
            (RULE_5_IN_4_EDUCATION, RULE_5_IN_7_SPIRITUALITY, RULE_7_IN_5_WEALTH),
            key=lambda rule: rule.rule_id,
        )
    ),
)
ACTIVE_PROVISIONAL_CORPUS: Final = PROVISIONAL_CORPUS_V1
