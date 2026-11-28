"""NEXT-CHILDREN-GUARD-01: provisional corpus v5 (``jyotish.provisional@v5``).

v5 = the v4 rules, with new record versions (v2) of the six second-lord Wealth rules whose
displayed text named a son or had पुत्र without a gloss (BPHS, अथ धनेशभावफलम्, vv. 9, 10, 12,
13, 17, 18).  Owner decision: JyotAI never predicts or hints at the sex of a child, and never
uses childlessness or loss wording; where the text says पुत्र the term is shown as written
with the gloss "children (the text says 'son')", a quoted term, never a prediction about the
user.  Each v2 record states that choice in its conventions (``PUTRA_CONVENTION``).

What changed in each v2 record (the rule, the condition, the original text, the draft
translation kept for the review pack, the confidence and held/shown status are unchanged):

* v.12 (2nd lord in the 5th): the statement says "wealth through children (the text says
  'son'): पुत्रतो धनवान्" instead of "wealth through a son".
* vv. 9, 10, 12, 17: the reasoning and the translation-held reason name the verse's clause
  about children with the gloss; "has sons" and "without sons" are no longer displayed.
* v.13 (held): the transcription note glosses the Hindi's पुत्र.
* v.18 (held): the convention only (its original text has पुत्र).

The gloss also applies to सुत (owner decision, review pack Q7): v.12's reasoning glosses
सुतभाव, and three more records whose original text has सुत (naming the fifth house: v.37
Education सुतेशे, v.40 Spirituality सुतेशे, v.54 Wealth सुते) record the convention only, with
no other change (v.37 and v.40 record v2, v.54 record v3).

Source verses with a child-sex or childlessness clause (vv. 9 पुत्री, 10 पुत्रहीनः, 12
पुत्रवान्, 17 सुतहीनो, 18 ज्येष्ठपुत्रसुखं न) are not changed here: the records keep them
verbatim for the review pack, and the app shows the held notice in their place
(``application.provisional``, ``children_guard.source_child_clause``).

None of these records is REVIEWED: every one is a provisional record (tier "provisional",
status PROVISIONAL), so no admitted text is reworded.
"""

from datetime import UTC, datetime
from typing import Final

from astrologer.composition.children_guard import PUTRA_CONVENTION, PUTRA_GLOSS
from astrologer.knowledge.provisional import (
    ProvisionalCorpus,
    ProvisionalJustification,
    ProvisionalRule,
)
from astrologer.knowledge.provisional_pack_v1 import (
    RULE_5_IN_4_EDUCATION,
    RULE_5_IN_7_SPIRITUALITY,
)
from astrologer.knowledge.provisional_pack_v3 import (
    RULE_2_IN_1_WEALTH,
    RULE_2_IN_2_WEALTH,
    RULE_2_IN_5_WEALTH,
    RULE_2_IN_6_WEALTH,
    RULE_2_IN_10_WEALTH,
    RULE_2_IN_12_WEALTH,
)
from astrologer.knowledge.provisional_pack_v4 import NOT_DRAFTED as NOT_DRAFTED_V4
from astrologer.knowledge.provisional_pack_v4 import (
    PROVISIONAL_CORPUS_V4,
    RULE_7_IN_5_WEALTH_V2,
)
from astrologer.knowledge.provisional_pack_v4 import REVIEWER_QUESTIONS as REVIEWER_QUESTIONS_V4

_RECORDED_AT: Final = datetime(2026, 11, 27, tzinfo=UTC)
_HELD: Final = (
    "The verse's other clauses, about {clauses}, are not wealth themes; only the wealth clause "
    "is shown, and the full translation is kept for the expert review."
)


def _v2(
    rule: ProvisionalRule,
    *,
    statement: str | None = None,
    reasoning: str | None = None,
    notes: str | None = None,
    held_clauses: str | None = None,
    version: str = "v2",
) -> ProvisionalRule:
    """A new record version: the gloss convention, and only the named fields reworded."""
    old = rule.justification
    justification = ProvisionalJustification.model_validate(
        {
            **old.model_dump(),
            "conventions": (*old.conventions, PUTRA_CONVENTION),
            "recorded_at": _RECORDED_AT,
            "interpretive_reasoning": reasoning or old.interpretive_reasoning,
            "transcription_notes": notes or old.transcription_notes,
        }
    )
    return ProvisionalRule.model_validate(
        {
            **rule.model_dump(),
            "rule": rule.rule.model_copy(update={"rule_version": version}),
            "statement": statement or rule.statement,
            "justification": justification,
            "translation_held_reason": (
                _HELD.format(clauses=held_clauses) if held_clauses else rule.translation_held_reason
            ),
        }
    )


RULE_2_IN_1_WEALTH_V2: Final = _v2(
    RULE_2_IN_1_WEALTH,
    reasoning=(
        "धनेश is the second lord; तनौ is the first house; the edition's Hindi agrees. The "
        "wealth clause is धनवान् (wealthy); it is the only clause displayed. The clauses about "
        f"{PUTRA_GLOSS}, स्वकुटुम्बस्य कण्टकः (a thorn to his family), निष्ठुर (harsh), कामी "
        "(lustful) and परकार्येषु तत्परः (busy with others' affairs) are not wealth themes; "
        "several are judgements of conduct and are not displayed."
    ),
    held_clauses=f"{PUTRA_GLOSS}, the family and conduct",
)
RULE_2_IN_2_WEALTH_V2: Final = _v2(
    RULE_2_IN_2_WEALTH,
    reasoning=(
        "धनगे (in the house of wealth) is the second house. The wealth clause is धनवान् "
        "(wealthy); it is the only clause displayed. गर्वसंयुत (proud), the number of wives "
        f"and the clause about {PUTRA_GLOSS} are not wealth themes and are not displayed."
    ),
    held_clauses=f"pride, wives and {PUTRA_GLOSS}",
)
RULE_2_IN_5_WEALTH_V2: Final = _v2(
    RULE_2_IN_5_WEALTH,
    statement=(
        "With the D1 second-house lord in the fifth house, the text describes wealth through "
        f"{PUTRA_GLOSS}: पुत्रतो धनवान्."
    ),
    reasoning=(
        f"सुतभाव, the house of {PUTRA_GLOSS}, is the fifth house. The wealth clause is "
        f"पुत्रतो धनवान्, wealthy through {PUTRA_GLOSS}; it is the only clause displayed. "
        "कृपण (miserly), दुःखभाक् (sharing in sorrow), यशस्वी (famous) "
        "and the verse's further clause about children are not wealth themes and are not "
        "displayed."
    ),
    held_clauses=f"miserliness, sorrow, fame and {PUTRA_GLOSS}",
)
RULE_2_IN_6_WEALTH_V2: Final = _v2(
    RULE_2_IN_6_WEALTH,
    notes=(
        "Read from the page image (PDF p. 184). The Sanskrit has शत्रुतो वित्तनाशः (loss of "
        f"wealth through an enemy); the Hindi reads पुत्र, {PUTRA_GLOSS}, in place of the "
        "enemy, probably a misprint; the Sanskrit is followed."
    ),
)
RULE_2_IN_10_WEALTH_V2: Final = _v2(
    RULE_2_IN_10_WEALTH,
    reasoning=(
        "दशमे is the tenth house. The wealth clause is in the compound बहुदारधनैर्युक्तः "
        "(endowed with many wives and wealth); only 'wealth (धन)' is displayed. Confidence "
        "is medium: बहु may qualify both wives and wealth ('much wealth'); the statement "
        "claims no amount. कामी, मानी, पण्डित (lustful, honoured, learned), the wives and the "
        f"clause about {PUTRA_GLOSS} are not wealth themes and are not displayed."
    ),
    held_clauses=f"conduct, wives and {PUTRA_GLOSS}",
)
RULE_2_IN_12_WEALTH_V2: Final = _v2(RULE_2_IN_12_WEALTH)

CHILDREN_GUARD_REVISIONS: Final = (
    RULE_2_IN_1_WEALTH_V2,
    RULE_2_IN_2_WEALTH_V2,
    RULE_2_IN_5_WEALTH_V2,
    RULE_2_IN_6_WEALTH_V2,
    RULE_2_IN_10_WEALTH_V2,
    RULE_2_IN_12_WEALTH_V2,
)
# सुत names the fifth house in these verses; the convention is recorded, nothing else changes.
SUTA_CONVENTION_REVISIONS: Final = (
    _v2(RULE_5_IN_4_EDUCATION),
    _v2(RULE_5_IN_7_SPIRITUALITY),
    _v2(RULE_7_IN_5_WEALTH_V2, version="v3"),
)
_REVISED: Final = {
    rule.rule_id: rule for rule in (*CHILDREN_GUARD_REVISIONS, *SUTA_CONVENTION_REVISIONS)
}

NOT_DRAFTED: Final = NOT_DRAFTED_V4
REVIEWER_QUESTIONS: Final[tuple[tuple[str, str], ...]] = (
    *REVIEWER_QUESTIONS_V4,
    (
        f'Is "{PUTRA_GLOSS}" the right display for पुत्र and for सुत?',
        "Owner decision (NEXT-CHILDREN-GUARD-01): JyotAI never predicts or hints at the sex of "
        "a child, so where the text says पुत्र or सुत the app shows the term as written with "
        f'the gloss "{PUTRA_GLOSS}" (second-lord verses 9, 10, 12, 13, 17, 18; the kāraka '
        "lists of Mars and Jupiter; the 11th-house verse; Venus's v.33; सुत also where it "
        "names the fifth house: सुतभाव v.12, सुतेशे vv. 37 and 40, सुते v.54). The app does "
        "not display a source verse whose clause names a child's sex or denies children "
        "(vv. 9 पुत्री, 10 पुत्रहीनः, 12 पुत्रवान्, 17 सुतहीनो, 18 ज्येष्ठपुत्रसुखं न हि): "
        "it shows a held notice, and the verses are in full in this pack. Please confirm the "
        "gloss for both terms, or give the wording to use.",
    ),
)

PROVISIONAL_CORPUS_V5: Final = ProvisionalCorpus(
    corpus_id="jyotish.provisional",
    corpus_version="v5",
    rules=tuple(_REVISED.get(rule.rule_id, rule) for rule in PROVISIONAL_CORPUS_V4.rules),
)
ACTIVE_PROVISIONAL_CORPUS: Final = PROVISIONAL_CORPUS_V5
