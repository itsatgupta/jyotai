"""Deterministic Ask JyotishAI justification from selected governed evidence only."""
# ruff: noqa: E501

import re
from collections.abc import Mapping

from astrologer.application.lord_dignity import lord_dignity
from astrologer.composition import DetailedComposedAnswer, DetailedEvidence
from astrologer.composition.models import DEFAULT_COMPOSITION_POLICY
from astrologer.evidence import InterpretationEvidence, InterpretationEvidenceItem
from astrologer.knowledge import ACTIVE_PRODUCTION_RELEASE
from astrologer.knowledge.rule_weights import SUPPORTING_LABEL, primary_first, rule_weight

_PLACEMENT_FACT = re.compile(r"^jyotish\.d1\.house_lord\.(?P<lord>[1-9]|1[0-2])\.placement_house$")
_ORDINALS = {
    1: "first",
    2: "second",
    3: "third",
    4: "fourth",
    5: "fifth",
    6: "sixth",
    7: "seventh",
    8: "eighth",
    9: "ninth",
    10: "tenth",
    11: "eleventh",
    12: "twelfth",
}
_DOMAIN_FRAMING = {
    "general": "This placement is being considered only as contextual natal evidence for an overall reading.",
    "career": "This placement is being considered only as contextual natal evidence for career matters.",
    "wealth": "This placement is being considered only as contextual natal evidence for wealth matters.",
    "education": "This placement is being considered only as contextual natal evidence for learning and education.",
    "business": "This placement is being considered only as contextual natal evidence for business matters.",
    "children": "This placement is being considered only as contextual natal evidence for children-related matters.",
    "spirituality": "This placement is being considered only as contextual natal evidence for spirituality-related matters.",
    "travel": "This placement is being considered only as contextual natal evidence for travel or residence-away-from-native-place matters.",
    "friends": "This placement is being considered only as contextual natal evidence for friendships and supportive associations.",
}
_DOMAIN_LIMITATIONS = {
    "general": ("This evidence does not establish a specific outcome, certainty, or timing.",),
    "career": (
        "This evidence does not establish a specific profession, promotion, income, certainty, or timing.",
    ),
    "wealth": ("This evidence does not establish an exact amount, income, certainty, or timing.",),
    "education": (
        "This evidence does not establish a specific course, admission result, exam score, certainty, or timing.",
    ),
    "business": (
        "This evidence does not establish a specific business result, profit, certainty, or timing.",
    ),
    "children": (
        "This evidence does not establish the number of children, a specific outcome, certainty, or timing.",
    ),
    "spirituality": (
        "This evidence does not establish a specific spiritual outcome, certainty, or timing.",
    ),
    "travel": (
        "This evidence does not establish visa or citizenship outcomes, a specific destination, certainty, or timing.",
    ),
    "friends": (
        "This evidence does not establish popularity, friend count, loyalty, certainty, or timing.",
    ),
}
# Display name of a domain in the answer's summary line.  NEXT-ADMIT-02, Sitting 1 item 23:
# the Travel rule is labelled "Residence away from birthplace" (routing still uses "travel").
_DOMAIN_LABELS = {"travel": "Residence away from birthplace"}
_NO_MATCH = "No reviewed interpretation is currently available for this area from the active governed corpus."
_UNKNOWN = "Some reviewed rules for this area could not be evaluated because the required chart facts were not available."
_TIMING = "Timing is not established by the current governed evidence."
# NEXT-CLEANUP-01: outside Career (whose answer is rebuilt by ``answer_career``) a timing
# question gets this factual line instead of a second non-prediction sentence; the domain
# limitation stays the answer's one template non-prediction sentence, at the end.
_NO_TIMING_RULE = "No reviewed timing rule is available for this area."


class DetailedAnswerBuilder:
    """Create an Ask-only display model; it neither evaluates nor interprets rules."""

    def build(
        self, evidence: InterpretationEvidence, facts: Mapping[str, object] | None = None
    ) -> DetailedComposedAnswer:
        """``facts`` (the chart's D1 derived facts) add each rule lord's sign dignity as a
        calculated fact; without them no dignity line is shown."""
        items = primary_first(evidence.selected_matched, lambda item: item.rule_id)
        domain = evidence.intent.domain.value
        timing_note = ""
        if evidence.intent.timing_requested:
            timing_note = " " + (_TIMING if domain == "career" else _NO_TIMING_RULE)
        if not items:
            limitations = (_UNKNOWN,) if evidence.relevant_unknown else ()
            return self._answer(
                evidence,
                answer=_NO_MATCH + timing_note,
                corpus_limitation=True,
                limitations=limitations,
            )

        display_evidence = tuple(self._display_item(item, domain, facts) for item in items)
        label = _DOMAIN_LABELS.get(domain, domain.title())
        summary = (
            f"Your D1 chart contains multiple reviewed indications relevant to {label}."
            if len(items) > 1
            else f"Your D1 chart contains reviewed contextual evidence relevant to {label}."
        )
        answer = summary + timing_note
        return self._answer(
            evidence,
            answer=answer,
            corpus_limitation=False,
            why_it_applies=tuple(_why(item) for item in display_evidence),
            reviewed_interpretations=tuple(item.reviewed_statement for item in display_evidence),
            limitations=_DOMAIN_LIMITATIONS[domain],
            display_evidence=display_evidence,
        )

    def _display_item(
        self,
        item: InterpretationEvidenceItem,
        domain: str,
        facts: Mapping[str, object] | None = None,
    ) -> DetailedEvidence:
        placement = self._placement(item)
        dignity = None
        house = _placement_lord(item)
        if facts is not None and house is not None:
            found = lord_dignity(facts, house)
            dignity = found.text if found is not None else None
        interpretations = {
            interpretation.interpretation_id: interpretation
            for interpretation in ACTIVE_PRODUCTION_RELEASE.registry.interpretations
        }
        passages = {
            passage.passage_id: passage for passage in ACTIVE_PRODUCTION_RELEASE.registry.passages
        }
        sources = {
            source.source_id: source for source in ACTIVE_PRODUCTION_RELEASE.registry.sources
        }
        interpretation = interpretations.get(item.interpretation_id)
        if interpretation is None:
            raise ValueError("selected governed interpretation is missing from the active registry")
        passage = passages.get(interpretation.passage_id)
        if passage is None or passage.source_id not in sources:
            raise ValueError("selected governed interpretation has insufficient source provenance")
        return DetailedEvidence(
            placement_explanation=placement,
            reviewed_statement=item.reviewed_statement,
            question_framing=_DOMAIN_FRAMING[domain],
            source_work=sources[passage.source_id].title,
            source_section=passage.locator,
            source_reference=passage.passage_reference,
            domain=domain,
            weight=rule_weight(item.rule_id),
            lord_dignity=dignity,
        )

    @staticmethod
    def _placement(item: InterpretationEvidenceItem) -> str:
        facts = item.resolved_facts
        if len(facts) != 1:
            raise ValueError("selected rule lacks one safely displayable placement fact")
        fact = facts[0]
        match = _PLACEMENT_FACT.fullmatch(fact.fact_id)
        if match is None or not isinstance(fact.value, int) or fact.value not in _ORDINALS:
            raise ValueError("selected rule lacks a safely displayable placement fact")
        return (
            f"Your D1 {_ORDINALS[int(match.group('lord'))]}-house lord is placed in the "
            f"{_ORDINALS[fact.value]} house."
        )

    @staticmethod
    def _answer(
        evidence: InterpretationEvidence,
        *,
        answer: str,
        corpus_limitation: bool,
        why_it_applies: tuple[str, ...] = (),
        reviewed_interpretations: tuple[str, ...] = (),
        limitations: tuple[str, ...] = (),
        display_evidence: tuple[DetailedEvidence, ...] = (),
    ) -> DetailedComposedAnswer:
        policy = DEFAULT_COMPOSITION_POLICY
        return DetailedComposedAnswer(
            answer=answer,
            referenced_evidence_item_ids=tuple(
                item.evidence_item_id for item in evidence.selected_matched
            ),
            timing_answered=False,
            corpus_limitation=corpus_limitation,
            policy_id=policy.policy_id,
            policy_version=policy.policy_version,
            prompt_version=policy.prompt_version,
            interpretation_contract_sha256=evidence.contract_content_sha256,
            manifest_id=evidence.manifest_id,
            manifest_version=evidence.manifest_version,
            manifest_content_sha256=evidence.manifest_content_sha256,
            provider_id="deterministic-detailed-answer-builder",
            model_id="none",
            why_it_applies=why_it_applies,
            reviewed_interpretations=reviewed_interpretations,
            limitations=limitations,
            evidence=display_evidence,
        )


def _placement_lord(item: InterpretationEvidenceItem) -> int | None:
    """The house whose lord the rule's single placement fact is about."""
    facts = item.resolved_facts
    if len(facts) != 1:
        return None
    match = _PLACEMENT_FACT.fullmatch(facts[0].fact_id)
    return int(match.group("lord")) if match else None


def _why(item: DetailedEvidence) -> str:
    """The placement line; a secondary rule is labelled "Supporting", and the lord's sign
    dignity follows as a calculated fact.  The reviewed statement itself is never changed."""
    text = item.placement_explanation
    if item.weight == "secondary":
        text = f"{SUPPORTING_LABEL}: {text}"
    if item.lord_dignity:
        text = f"{text} {item.lord_dignity}"
    return text
