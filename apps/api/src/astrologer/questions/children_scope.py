"""NEXT-CHILDREN-GUARD-01: questions JyotAI answers with one fixed line, in any domain.

Owner decision (a product decision, not legal advice): JyotAI never predicts or hints at the
sex of an unborn or future child, in any wording.  The PCPNDT Act (s.22) bans advertising
sex determination "by any means whatsoever, scientific or otherwise", which may reach a
public app.  Fertility, pregnancy, miscarriage, IVF, "will I have children at all" and the
number of children are out of scope too (consult a doctor for medical matters).

:func:`child_question_scope` classifies the question's language only (English, Hinglish and
Devanagari wordings); it reads no chart and no evidence.  The order is fixed: a question
about a child's sex is always :attr:`ChildQuestionScope.CHILD_SEX`, even when it also names
pregnancy or a number ("How many sons will I have?").  The router sends a matched question to
the Children domain only, and the answer layer replaces the answer with the scope's line.
"""

import re
from enum import StrEnum
from typing import Final


class ChildQuestionScope(StrEnum):
    """Why a question gets a one-line reply instead of an answer."""

    CHILD_SEX = "child_sex"
    MEDICAL = "medical"
    WHETHER_OR_COUNT = "whether_or_count"


# A word naming a child's sex: English, Hinglish (Latin script).
_SEXED: Final = (
    r"(?:sons?|daughters?|boys?(?!\s*friends?\b)|girls?(?!\s*friends?\b)|baby\s+(?:boy|girl)s?|"
    r"(?:male|female|boy|girl)\s+(?:child|children|baby|babies|kids?|issue|heirs?|offspring|"
    r"progeny)|male\s+heirs?|beta|bete|beti|betiyan|betiyaan|ladka|ladke|ladki|ladkiyan|"
    r"putra|putr|putri|putron)"
)
_CHILD: Final = (
    r"(?:children|child|kids?|bab(?:y|ies)|infants?|offspring|progeny|issue|heirs?|santan\w*|"
    r"santaan\w*|santati|bachch\w*|bacch\w*|aulaa?d\w*|aolad\w*)"
)
_GET: Final = (
    r"(?:have|having|has|had|get|gets|getting|bear|bearing|deliver|delivering|conceive|"
    r"conceiving|expect|expecting|carry|carrying|birth\s+to|give\s+birth\s+to|"
    r"blessed\s+with|bless\s+(?:me|us)\s+with|pregnant\s+with|father|fathering|adopt)"
)
_DETERMINER: Final = (
    r"(?:(?:a|an|my|our|any|the|one|two|three|four|five|more|another|only\s+one|\d+)\s+)?"
    r"(?:(?:first|second|third|next|healthy|baby|male|female|own)\s+)?"
)
_DEVANAGARI_SEXED: Final = r"(?<![ऀ-ॿ])(?:पुत्र|पुत्री|बेटा|बेटी|बेटे|लड़का|लड़की|लड़के|लडका|लडकी)"

_CHILD_SEX_PATTERNS: Final = (
    # "boy or girl", "son or daughter", "beta ya beti" (either order).
    re.compile(
        r"\b(?:boy|son|male|beta|ladka|putra)\s+(?:or|ya|aur)\s+(?:a\s+)?"
        r"(?:girl|daughter|female|beti|ladki|putri)\b"
        r"|\b(?:girl|daughter|female|beti|ladki|putri)\s+(?:or|ya|aur)\s+(?:a\s+)?"
        r"(?:boy|son|male|beta|ladka|putra)\b"
    ),
    # "the gender of my baby", "baby's sex", "what sex will the child be".
    re.compile(
        rf"\b(?:sex|gender|ling)\b.*\b(?:{_CHILD}|unborn|fetus|foetus|pregnan\w*|womb|"
        r"conceiv\w*|garbh\w*)"
        rf"|\b(?:{_CHILD}|unborn|fetus|foetus|pregnan\w*|womb|garbh\w*)\b.*\b(?:sex|gender)\b"
    ),
    # "have a son", "get a baby girl", "expecting a boy", "blessed with daughters".
    re.compile(rf"\b{_GET}\s+{_DETERMINER}{_SEXED}\b"),
    # "son likely", "a boy is indicated", "daughter in my chart".
    re.compile(
        rf"\b{_SEXED}\s+(?:is\s+|are\s+)?(?:likely|possible|probable|indicated|predicted|"
        r"promised|destined|coming|due|on\s+the\s+way|in\s+(?:my|our)\s+(?:chart|kundli|"
        r"kundali|horoscope|destiny|fate|future|luck|stars))\b"
    ),
    # "chances of a son", "odds of a girl", "signs of a baby boy".
    re.compile(
        r"\b(?:chances?|odds|probabilit(?:y|ies)|possibilit(?:y|ies)|likelihood|prospects?|"
        r"signs?|indications?|yogas?|yog|timing|time)\s+(?:of|for)\s+(?:a\s+|an\s+|getting\s+"
        rf"(?:a\s+)?|having\s+(?:a\s+)?)?{_SEXED}\b"
    ),
    # "will it be a boy", "is the baby a girl", "first child be a son".
    re.compile(
        r"\b(?:it|baby|child|kid|fetus|foetus|pregnancy|first\s+(?:child|baby)|"
        r"next\s+(?:child|baby)|second\s+(?:child|baby))\s+(?:will\s+be|would\s+be|"
        r"is\s+going\s+to\s+be|going\s+to\s+be|be|is)\s+(?:a\s+)?(?:boy|girl|son|daughter|male|"
        r"female)\b"
    ),
    # Inverted wordings: "is my pregnancy a boy?", "will the baby be a girl?".
    re.compile(
        r"\b(?:bab(?:y|ies)|pregnan\w*|fetus|foetus|womb|unborn|garbh\w*)\b.*\b(?:a|an)\s+"
        r"(?:boy|girl|son|daughter|male|female)\b"
    ),
    # A hypothetical child of one sex: "wealth through a son", "any daughter", "more sons".
    # ("my son" is an existing child and is not matched; a bare "a boy/girl" is too vague.)
    re.compile(
        r"\b(?:a|an|any|more|another|some|future)\s+(?:sons?|daughters?|baby\s+(?:boy|girl)s?|"
        r"(?:male|female|boy|girl)\s+(?:child|children|baby|heir)|male\s+heirs?)\b"
        r"|\b(?:through|from|by|via)\s+(?:sons|daughters)\b"
    ),
    # "when will my son be born", "a daughter to be born".
    re.compile(rf"\b{_SEXED}\s+(?:will\s+be|be|to\s+be|going\s+to\s+be)\s+born\b"),
    # "how many sons", "number of daughters".
    re.compile(rf"\b(?:how\s+many|number\s+of|kitn[aei]|kitne)\s+{_SEXED}\b"),
    # Hinglish: "beta hoga?", "putra prapti", "putra yog", "ladka kab hoga".
    re.compile(
        r"\b(?:putra|putr|putri|beta|bete|beti|betiyan|ladka|ladke|ladki)\s*(?:ka\s+|ki\s+)?"
        r"(?:hog[aie]|honge|hongi|hoyega|milega|milegi|mil\s+sakt\w*|paida|janm\w*|kab|yog|"
        r"yoga|prapti|praapti|sukh|santan|santaan|dosh\w*|sambhavna|chance)\b"
    ),
    # Devanagari: "बेटा होगा", "पुत्र प्राप्ति", "लड़का या लड़की".
    re.compile(
        _DEVANAGARI_SEXED
        + r"\s*(?:का\s*|की\s*)?(?:होगा|होगी|होंगे|होगें|प्राप्ति|योग|मिलेगा|मिलेगी|जन्म|कब|या|"
        r"सुख|संतान|सन्तान)"
    ),
    # Any पुत्र / putra wording at all: the word itself names a son.
    re.compile(r"(?<![ऀ-ॿ])(?:पुत्र|पुत्री)|\b(?:putra|putri|putron)\b"),
)

_MEDICAL_PATTERNS: Final = (
    re.compile(
        r"\b(?:fertil\w*|infertil\w*|pregnan\w*|conceiv\w*|conception|ivf|iui|icsi|"
        r"in[\s-]vitro|test[\s-]tube\s+bab\w*|surrogac\w*|surrogate|miscarr\w*|abortions?|"
        r"aborted|stillb\w*|ectopic|gyn(?:a)?ec\w*|obstetric\w*|ovulat\w*|embryos?|fetus|"
        r"foetus|f(?:o)?etal|womb|uterus|sperm\w*|egg\s+freez\w*|due\s+date|c[\s-]?section|"
        r"ca?esarean|labou?r\s+pains?|garbh\w*|godh\s+bharai|trying\s+to\s+conceive|ttc)\b"
    ),
    re.compile(
        r"\b(?:lose|losing|lost|loss\s+of)\s+(?:the\s+|my\s+|our\s+|a\s+)?"
        r"(?:baby|pregnancy|child)\b|\b(?:baby|pregnancy|child)\s+loss\b"
    ),
    re.compile(r"(?:गर्भ|गर्भपात|गर्भधारण|प्रजनन|आईवीएफ|बांझ|बाँझ)"),
)

_WHETHER_PATTERNS: Final = (
    # "Will I have children?", "Can we have kids?", "Will I ever have a child?".
    re.compile(
        r"\b(?:will|would|can|could|shall|may|might|do|does|did|am|is|are)\s+"
        r"(?:i|we|my\s+wife|my\s+husband|my\s+partner|my\s+spouse|she|he|us)\s+"
        r"(?:ever\s+)?(?:be\s+)?(?:able\s+to\s+)?(?:ever\s+)?"
        rf"{_GET}\s+{_DETERMINER}{_CHILD}\b"
    ),
    # "Am I going to have children?", "Is there any chance of children?".
    re.compile(rf"\b(?:going|gonna)\s+to\s+{_GET}\s+{_DETERMINER}{_CHILD}\b"),
    re.compile(
        r"\b(?:chances?|odds|probabilit(?:y|ies)|possibilit(?:y|ies)|likelihood|prospects?|"
        r"hope)\s+(?:of|for)\s+(?:having\s+|getting\s+)?(?:any\s+)?(?:a\s+)?"
        rf"{_CHILD}\b"
    ),
    # Childlessness wordings: "will I be childless", "no children in my chart".
    re.compile(
        r"\b(?:childless\w*|child-less|issueless|barren\w*|nis+antaa?n\w*|baa?njh\w*|"
        r"santaa?n\s*(?:heen|hin|hinta)|(?:no|without|never\s+(?:have|get))\s+(?:any\s+)?"
        r"(?:children|child|kids|issue|progeny|offspring|a\s+child|a\s+baby|babies))\b"
    ),
    # "How many children", "number of kids", "kitne bachche".
    re.compile(rf"\b(?:how\s+many|number\s+of|kitn[aei]|kitne)\s+{_CHILD}\b"),
    # Hinglish / Devanagari: "santan hogi?", "bachche honge?", "santan yog hai?".
    re.compile(
        r"\b(?:santaa?n\w*|santati|bachch\w*|bacch\w*|aulaa?d\w*|aolad\w*)\s+(?:ka\s+|ki\s+)?"
        r"(?:sukh\s+)?(?:hog[aie]|honge|hongi|milega|milegi|mil\s+payega|prapti|praapti|yog|"
        r"yoga|hai\s+(?:ki|ya)\s+nahi)\b"
        r"|\b(?:children|child|progeny)\s+yogas?\b"
    ),
    re.compile(
        r"(?:संतान|सन्तान|बच्चे|बच्चा|औलाद)\s*(?:का\s*|की\s*)?(?:सुख\s*)?"
        r"(?:होगी|होगा|होंगे|मिलेगा|मिलेगी|प्राप्ति|योग)|कितने\s*(?:बच्चे|संतान)|निःसंतान|निःसन्तान"
    ),
)
# A plain timing question ("When will I have children?") keeps the Children answer; it is a
# "whether" question only when it also says "ever", "at all" or "any".
_TIMING: Final = re.compile(r"\b(?:when|kab|which\s+year|what\s+year|what\s+age|at\s+what\s+age)\b")
_WHETHER_EVEN_IF_TIMING: Final = re.compile(r"\b(?:ever|at\s+all|any|whether|if)\b")


def _normalized(question: str) -> str:
    return " ".join(question.lower().replace("’", "'").split())


def child_question_scope(question: str) -> ChildQuestionScope | None:
    """The scope whose one-line reply replaces the answer, or None (language only)."""
    text = _normalized(question)
    if any(pattern.search(text) for pattern in _CHILD_SEX_PATTERNS):
        return ChildQuestionScope.CHILD_SEX
    if any(pattern.search(text) for pattern in _MEDICAL_PATTERNS):
        return ChildQuestionScope.MEDICAL
    for index, pattern in enumerate(_WHETHER_PATTERNS):
        if not pattern.search(text):
            continue
        # Only the plain "will I have children" wordings (the first two patterns) give way
        # to a timing question; childlessness and counts never do.
        if index < 2 and _TIMING.search(text) and not _WHETHER_EVEN_IF_TIMING.search(text):
            continue
        return ChildQuestionScope.WHETHER_OR_COUNT
    return None
