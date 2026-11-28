"""NEXT-CHILDREN-GUARD-01: no child-sex hint and no childlessness or loss wording, anywhere.

Owner decision (a product decision, not legal advice; see ``questions.children_scope``):

* **Child sex.**  No answer text may name or hint at the sex of a child: no "son",
  "daughter", "boy", "girl", "male child" and the like, in English, Hinglish or Devanagari.
* **पुत्र and सुत.**  Where the text says पुत्र or सुत, the term is shown as written with the
  gloss :data:`PUTRA_GLOSS`, "children (the text says 'son')".  It is a quoted term, never a
  prediction about the user.  The gloss itself is the one allowed place for "son".  (सुत also
  names the fifth house, सुतभाव; the gloss applies there too.)
* **Source verses.**  A quoted source verse (Sanskrit, or the edition's Hindi) with a clause
  that names a child's sex beyond the glossed term, or a childlessness or loss clause
  (:func:`source_child_clause`), is not displayed: the app shows
  :data:`SOURCE_HELD_NOTICE` and the review pack keeps the verse in full.
* **Childlessness and loss.**  No "childless", "without children", "barren", "miscarriage",
  "loss of a child" and the like, in any domain.

Quoted source text (a Sanskrit original kept verbatim for the evidence disclosure) is passed
as ``quoted`` and removed first, as in the other wording guards.  The guards apply to every
template sentence, every provisional display field and every language-model narrative.

Text the guard holds is replaced by a notice, never silently dropped: a held source verse by
:data:`SOURCE_HELD_NOTICE`, a held provisional statement by the provisional held statement, and
any other held text (an answer section, a reviewed statement, a justification field) by
:data:`CHILD_HELD_NOTICE`.
"""

import re
from collections.abc import Iterable
from typing import Final

PUTRA_GLOSS: Final = "children (the text says 'son')"
"""The only rendering of पुत्र and सुत in displayed text."""
PUTRA: Final = "पुत्र"
SUTA: Final = "सुत"
CHILD_TERMS: Final = (PUTRA, SUTA)
"""The source terms shown only with :data:`PUTRA_GLOSS` and a recorded :data:`PUTRA_CONVENTION`."""
PUTRA_CONVENTION: Final = (
    "Where the text says पुत्र or सुत, the term is shown as written with the gloss "
    f'"{PUTRA_GLOSS}"; it is a quoted term, never a prediction about the user. A source verse '
    "whose clause names a child's sex or denies children is held in the app and kept in full in "
    "the review pack. JyotAI never predicts or hints at the sex of a child (owner decision, "
    "NEXT-CHILDREN-GUARD-01)."
)
"""The justification-record convention for every record whose displayed text has पुत्र or सुत."""

SOURCE_HELD_NOTICE: Final = (
    "The source verse is held for the expert review under JyotAI's children wording rule; the "
    "full verse is in the final review pack."
)
"""Shown in place of a source verse with a child-sex or childlessness clause."""
CHILD_HELD_NOTICE: Final = (
    "This text is held for the expert review under JyotAI's children wording rule."
)
"""Shown in place of any other text the children guard holds."""

CHILD_SEX_LANGUAGE: Final = re.compile(
    r"\b(?:sons?|daughters?|boys?|girls?|(?:male|female|boy|girl)\s+(?:child|children|baby|"
    r"babies|kids?|issue|heirs?|offspring|progeny)|male\s+heirs?|beta|bete|beti|betiyan|"
    r"ladk[aei]|ladkiyan|putra|putri|putron)\b"
    r"|(?<![ऀ-ॿ])(?:बेटा|बेटी|बेटे|लड़का|लड़की|लड़के|लडका|लडकी)",
    re.IGNORECASE,
)
"""Words naming a child's sex, barred outside quoted text and the पुत्र gloss."""

CHILD_LOSS_LANGUAGE: Final = re.compile(
    r"\b(?:childless\w*|child-less|issueless|barren\w*|infertil\w*|steril(?:e|ity)|"
    r"miscarr\w*|stillb(?:irth|orn)\w*|abortions?|aborted|"
    r"(?:no|without|lack\s+of|absence\s+of|denial\s+of)\s+(?:any\s+)?(?:children|child|kids|"
    r"sons?|daughters?|issue|progeny|offspring|santan)|"
    r"(?:never|not|won't|will\s+not|cannot|can't|unable\s+to)\s+(?:have|bear|conceive|get|"
    r"be\s+blessed\s+with)\s+(?:any\s+|a\s+)?(?:children|child|kids|sons?|daughters?|baby|"
    r"babies|issue|progeny|offspring)|"
    r"(?:loss|losses|lose|loses|losing|lost|death|deaths|die|dies|died|dying|dead|mortality)\s+"
    r"of\s+(?:a\s+|the\s+|one's\s+|his\s+|her\s+|their\s+)?(?:child|children|kids|sons?|"
    r"daughters?|baby|babies|infants?|progeny|offspring|pregnanc\w*)|"
    r"(?:child|children|infant|baby|pregnancy|progeny)\s+(?:loss|losses|death|deaths|"
    r"mortality)|santaa?n\s*(?:heen|hin|nash|kasht)|nis+antaa?n\w*|baa?njh\w*)\b"
    r"|पुत्रहीन|सुतहीन|अनपत्य|निःसंतान|निःसन्तान|संतानहीन|सन्तानहीन|बांझ|बाँझ|वन्ध्या|गर्भपात|"
    r"गर्भस्राव|पुत्रनाश|सुतनाश",
    re.IGNORECASE,
)
"""Childlessness and loss wording barred from every answer outside quoted text."""

_DEVANAGARI: Final = "[\u0900-\u097f]"
SOURCE_CHILD_CLAUSE: Final = re.compile(
    # Childlessness, denial or loss of children (पुत्रहीनः, सुतहीनो, "no joy of the eldest son").
    "पुत्रहीन|सुतहीन|अपुत्र|निष्पुत्र|अनपत्य|निःसंतान|निःसन्तान|संतानहीन|सन्तानहीन|बांझ|बाँझ|"
    "वन्ध्या|गर्भपात|गर्भस्राव|पुत्रनाश|सुतनाश|पुत्रशोक|सुतशोक|"
    f"(?:पुत्र|सुत)सुख{_DEVANAGARI}*\\s+न(?!{_DEVANAGARI})|"
    # A clause naming a child's sex beyond the glossed term: "has sons" (पुत्री, पुत्रवान्),
    # a daughter (सुता, दुहिता, Hindi बेटी / लड़की), the eldest or youngest son.
    f"पुत्री|पुत्रिका|पुत्रव(?:ान|ती|न्त)|सुतव(?:ान|ती)|सुता(?!{_DEVANAGARI})|दुहित|"
    "ज्येष्ठपुत्र|कनिष्ठपुत्र|ज्येष्ठसुत|बेटा|बेटी|बेटे|लड़का|लड़की|लड़के|लडका|लडकी"
)
"""A source-verse clause the app never displays (the verse stays in the review pack)."""


def _remaining(text: str, quoted: Iterable[str]) -> str:
    remaining = text
    for passage in sorted({item for item in quoted if item}, key=len, reverse=True):
        remaining = remaining.replace(passage, " ")
    return remaining


def child_sex_violation(text: str, quoted: Iterable[str] = ()) -> str | None:
    """The first child-sex word in ``text`` outside ``quoted`` and the पुत्र gloss, else
    None.  पुत्र and सुत are allowed only next to the gloss in the same text."""
    remaining = _remaining(text, quoted)
    glossed = PUTRA_GLOSS in remaining
    match = CHILD_SEX_LANGUAGE.search(remaining.replace(PUTRA_GLOSS, " "))
    if match is not None:
        return match.group()
    if not glossed:
        return next((term for term in CHILD_TERMS if term in remaining), None)
    return None


def child_loss_violation(text: str, quoted: Iterable[str] = ()) -> str | None:
    """The first childlessness or loss phrase in ``text`` outside ``quoted``, else None."""
    match = CHILD_LOSS_LANGUAGE.search(_remaining(text, quoted))
    return match.group() if match else None


def child_wording_violation(text: str, quoted: Iterable[str] = ()) -> str | None:
    """Either guard's first violation (child sex first), else None."""
    return child_sex_violation(text, quoted) or child_loss_violation(text, quoted)


def source_child_clause(text: str) -> str | None:
    """The first child-sex or childlessness clause in a quoted source text, else None."""
    match = SOURCE_CHILD_CLAUSE.search(text)
    return match.group() if match else None


def has_child_term(text: str) -> bool:
    """True when ``text`` has पुत्र or सुत (shown only with the recorded gloss convention)."""
    return any(term in text for term in CHILD_TERMS)
