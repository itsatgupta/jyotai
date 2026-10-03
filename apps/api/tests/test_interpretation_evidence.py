"""Synthetic coverage for the Task 17C internal interpretation-evidence boundary."""

import pytest

from astrologer.evidence import (
    EvidenceSelectionResult,
    InterpretationEvidenceBuilder,
    InterpretationEvidenceBuildError,
)
from astrologer.evidence.models import EvidenceItem, ResolvedEvidenceFact
from astrologer.evidence.selection_models import (
    EXACT_DOMAIN_SELECTION_POLICY_V1,
    SelectionCapabilitySummary,
)
from astrologer.knowledge.career_pack_v1 import ACTIVE_PRODUCTION_RELEASE, FACT_ID
from astrologer.knowledge.evaluation import (
    FactEvaluationProvenance,
    GovernedRuleEvaluator,
    fact_set_sha256,
)
from astrologer.knowledge.models import JyotishDomain
from astrologer.questions.models import (
    QuestionDomain,
    QuestionIntent,
    QuestionShape,
    TemporalIntent,
)
from astrologer.rules.models import EvaluationStatus, Fact, FactSet

_BUILDER = InterpretationEvidenceBuilder()
_GENERAL_FACT_ID = "jyotish.d1.house_lord.11.placement_house"


def _governed_items(facts: FactSet) -> tuple[EvidenceItem, ...]:
    provenance = FactEvaluationProvenance(
        methodology_id=ACTIVE_PRODUCTION_RELEASE.fact_contract.methodology_id,
        source_register_version=ACTIVE_PRODUCTION_RELEASE.registry.registry_version,
        derived_fact_provenance_sha256="0" * 64,
        fact_set_sha256=fact_set_sha256(facts),
    )
    results = GovernedRuleEvaluator().evaluate(
        ACTIVE_PRODUCTION_RELEASE.manifest,
        ACTIVE_PRODUCTION_RELEASE.envelopes,
        ACTIVE_PRODUCTION_RELEASE.registry,
        ACTIVE_PRODUCTION_RELEASE.fact_contract,
        facts,
        provenance,
    )
    values = facts.by_id()
    return tuple(
        EvidenceItem(
            evidence_item_id=f"{result.evaluation.rule_id}@{result.evaluation.rule_version}",
            evaluation_status=result.evaluation.status,
            evidence_direction=result.evidence_direction,
            rule_id=result.evaluation.rule_id,
            rule_version=result.evaluation.rule_version,
            effect_key=result.evaluation.effect.effect_key,
            domain=result.governance_provenance.domain,
            taxonomy=result.governance_provenance.taxonomy,
            posture=result.governance_provenance.posture,
            chart_scope=result.governance_provenance.chart_scope,
            referenced_fact_ids=result.evaluation.condition.referenced_fact_ids,
            resolved_facts=tuple(
                ResolvedEvidenceFact(fact_id=fact_id, value=values[fact_id].value)
                for fact_id in result.evaluation.condition.resolved_fact_ids
            ),
            unresolved_fact_ids=tuple(
                fact_id
                for fact_id in result.evaluation.condition.referenced_fact_ids
                if fact_id not in result.evaluation.condition.resolved_fact_ids
            ),
            condition_trace=result.evaluation.condition,
            governance_provenance=result.governance_provenance,
            fact_provenance=result.fact_provenance,
        )
        for result in results
    )


def _selection(domain: QuestionDomain, items: tuple[EvidenceItem, ...], *, timing: bool = False):
    relevant = tuple(item for item in items if item.domain.value == domain.value)
    matched = tuple(item for item in relevant if item.evaluation_status is EvaluationStatus.TRUE)
    unmatched = tuple(item for item in relevant if item.evaluation_status is EvaluationStatus.FALSE)
    unknown = tuple(item for item in relevant if item.evaluation_status is EvaluationStatus.UNKNOWN)
    intent = QuestionIntent(
        intent_id="intent-1",
        domain=domain,
        shape=QuestionShape.TIMING if timing else QuestionShape.DESCRIPTIVE,
        temporal_intent=TemporalIntent.TIME_BOUND if timing else TemporalIntent.CURRENT,
        requires_timing=timing,
    )
    capability = SelectionCapabilitySummary(
        has_matched_evidence=bool(matched),
        has_supporting_match=False,
        has_challenging_match=False,
        has_contextual_match=bool(matched),
        timing_requested=timing,
        has_static_match=bool(matched),
        has_timing_required_match=False,
        has_corroboration_required_match=False,
        timing_answerability_established=False,
        corroboration_handling_deferred=False,
    )
    fields = dict(
        policy=EXACT_DOMAIN_SELECTION_POLICY_V1,
        question_intent=intent,
        evidence_package_content_sha256="1" * 64,
        manifest_id=ACTIVE_PRODUCTION_RELEASE.manifest.manifest_id,
        manifest_version=ACTIVE_PRODUCTION_RELEASE.manifest.manifest_version,
        manifest_content_sha256=ACTIVE_PRODUCTION_RELEASE.manifest.content_sha256(),
        selected_matched=matched,
        relevant_unmatched=unmatched,
        relevant_unknown=unknown,
        excluded=(),
        capability_summary=capability,
    )
    provisional = EvidenceSelectionResult.model_construct(
        **fields, selection_content_sha256="0" * 64
    )
    return EvidenceSelectionResult(**fields, selection_content_sha256=provisional.content_sha256())


def test_career_match_admits_only_selected_career_rules_and_preserves_provenance() -> None:
    items = _governed_items(
        FactSet(facts=(Fact(fact_id=FACT_ID, value=4), Fact(fact_id=_GENERAL_FACT_ID, value=9)))
    )

    contract = _BUILDER.build(_selection(QuestionDomain.CAREER, items))

    assert contract.selected_matched
    assert all(item.domain is JyotishDomain.CAREER for item in contract.selected_matched)
    item = contract.selected_matched[0]
    assert item.rule_id == "bphs.d1.house_lord.10.in_4_or_10.v1"
    assert item.governance_provenance.passage_id
    assert item.governance_provenance.manifest_id == "jyotish.production.cumulative"
    assert item.resolved_fact_ids == (FACT_ID,)


def test_exact_domain_isolation_excludes_general_from_career_and_career_from_general() -> None:
    items = _governed_items(
        FactSet(facts=(Fact(fact_id=FACT_ID, value=4), Fact(fact_id=_GENERAL_FACT_ID, value=9)))
    )

    career = _BUILDER.build(_selection(QuestionDomain.CAREER, items))
    general = _BUILDER.build(_selection(QuestionDomain.GENERAL, items))

    assert all(
        item.domain is JyotishDomain.CAREER
        for item in career.selected_matched + career.relevant_unmatched
    )
    assert all(item.domain is JyotishDomain.GENERAL for item in general.selected_matched)
    assert not any(item.domain is JyotishDomain.CAREER for item in general.selected_matched)


def test_unknown_and_false_are_explicitly_distinct() -> None:
    unknown = _BUILDER.build(_selection(QuestionDomain.CAREER, _governed_items(FactSet())))
    false = _BUILDER.build(
        _selection(
            QuestionDomain.CAREER,
            _governed_items(FactSet(facts=(Fact(fact_id=FACT_ID, value=1),))),
        )
    )

    assert unknown.selected_matched == () and unknown.relevant_unmatched == ()
    assert all(
        item.evaluation_status is EvaluationStatus.UNKNOWN for item in unknown.relevant_unknown
    )
    assert all(item.unresolved_fact_ids == (FACT_ID,) for item in unknown.relevant_unknown)
    assert false.selected_matched == () and false.relevant_unknown == ()
    assert all(
        item.evaluation_status is EvaluationStatus.FALSE for item in false.relevant_unmatched
    )
    assert all(item.resolved_fact_ids == (FACT_ID,) for item in false.relevant_unmatched)


def test_time_bound_career_context_does_not_admit_timing_fields_or_answerability() -> None:
    items = _governed_items(FactSet(facts=(Fact(fact_id=FACT_ID, value=4),)))

    contract = _BUILDER.build(_selection(QuestionDomain.CAREER, items, timing=True))
    serialized = contract.model_dump(mode="json")

    assert contract.selected_matched
    assert contract.intent.timing_requested is True
    assert contract.timing_answerability_established is False
    assert "time_range" not in serialized
    assert "date" not in str(serialized) and "period" not in str(serialized)


@pytest.mark.parametrize("candidate_id", ["career-candidate-01", "career-candidate-05"])
def test_repeated_construction_is_equal_and_non_admitted_candidates_are_rejected(
    candidate_id: str,
) -> None:
    items = _governed_items(FactSet(facts=(Fact(fact_id=FACT_ID, value=4),)))
    selection = _selection(QuestionDomain.CAREER, items)

    assert _BUILDER.build(selection) == _BUILDER.build(selection)
    candidate = selection.selected_matched[0].model_copy(
        update={
            "rule_id": candidate_id,
            "rule_version": "v1",
            "governance_provenance": selection.selected_matched[0].governance_provenance.model_copy(
                update={"rule_id": candidate_id, "rule_version": "v1"}
            ),
        }
    )
    rejected = _selection(QuestionDomain.CAREER, (candidate,))
    with pytest.raises(InterpretationEvidenceBuildError, match="not admitted"):
        _BUILDER.build(rejected)
