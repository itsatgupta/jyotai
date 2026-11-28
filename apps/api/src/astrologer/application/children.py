"""NEXT-CHILDREN-GUARD-01: the one-line replies for child-sex and medical questions.

A question matched by :func:`~astrologer.questions.children_scope.child_question_scope` (in
any domain and any wording) is routed to the Children domain only, and its answer is the
scope's one line: no chart factors, no evidence, no provisional items, no language model.
Owner decision; a product decision, not legal advice (see ``questions.children_scope``).
"""

import logging
from collections.abc import Sequence
from typing import Final

from astrologer.composition.children_guard import CHILD_HELD_NOTICE, child_wording_violation
from astrologer.composition.models import ConsultationSection, DetailedComposedAnswer
from astrologer.questions.children_scope import ChildQuestionScope

CHILD_SEX_REPLY: Final = "JyotAI does not predict a child's sex."
CHILD_SCOPE_REPLIES: Final[dict[ChildQuestionScope, str]] = {
    ChildQuestionScope.CHILD_SEX: CHILD_SEX_REPLY,
    ChildQuestionScope.MEDICAL: (
        "Questions about fertility and pregnancy are out of scope for JyotAI; for medical "
        "matters, please consult a doctor."
    ),
    ChildQuestionScope.WHETHER_OR_COUNT: (
        "Whether or how many children someone will have is out of scope for JyotAI; for "
        "medical matters, please consult a doctor."
    ),
}
_LOGGER = logging.getLogger(__name__)


def child_scope_answer(
    answer: DetailedComposedAnswer, scope: ChildQuestionScope
) -> DetailedComposedAnswer:
    """``answer`` reduced to the scope's one line (provenance fields kept)."""
    reply = CHILD_SCOPE_REPLIES[scope]
    return answer.model_copy(
        update={
            "answer": reply,
            "consultation_sections": (ConsultationSection(kind="direct", text=reply),),
            "referenced_evidence_item_ids": (),
            "why_it_applies": (),
            "reviewed_interpretations": (),
            "limitations": (),
            "evidence": (),
            "narrative": None,
            "timing": None,
            "claim_ledger": None,
            "career_answer_plan": None,
            "career_comparison": None,
            "rule_review_types": (),
            "provisional_interpretations": (),
            # A policy line, not a corpus limit: nothing reviewed would change it.
            "corpus_limitation": False,
            "timing_answered": False,
        }
    )


def child_held_section(section: ConsultationSection, domain: str) -> ConsultationSection:
    """``section``, or the held notice in its place when any of its text has child-sex,
    childlessness or loss wording (fail closed; the section is never silently dropped)."""
    texts = (
        section.text,
        section.framing or "",
        *(sentence.text for sentence in section.synthesis_sentences),
    )
    bad = next((hit for text in texts if (hit := child_wording_violation(text))), None)
    if bad is None:
        return section
    _LOGGER.warning("%s section %s held by children guard: %r", domain, section.kind, bad)
    return ConsultationSection(kind=section.kind, text=CHILD_HELD_NOTICE)


def child_clean_sections(
    sections: Sequence[ConsultationSection], domain: str
) -> tuple[ConsultationSection, ...]:
    """Every section, with the held notice in place of one the children guard holds."""
    return tuple(child_held_section(section, domain) for section in sections)


def child_clean_answer(answer: DetailedComposedAnswer, domain: str) -> DetailedComposedAnswer:
    """The answer with every section and the answer line passed through the children guard;
    held text shows :data:`CHILD_HELD_NOTICE` (reviewed statements: ``DetailedAnswerBuilder``)."""
    update: dict[str, object] = {
        "consultation_sections": child_clean_sections(answer.consultation_sections, domain)
    }
    if (bad := child_wording_violation(answer.answer)) is not None:
        _LOGGER.warning("%s answer line held by children guard: %r", domain, bad)
        update["answer"] = CHILD_HELD_NOTICE
    return answer.model_copy(update=update)
