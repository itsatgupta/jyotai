"""Synthetic deterministic coverage for Travel / Foreign Residence Pack v1."""

from astrologer.composition import DeterministicAnswerComposer
from astrologer.evidence import EvidenceSelector, InterpretationEvidenceBuilder
from astrologer.evidence.models import EvidenceItem, EvidencePackage, ResolvedEvidenceFact
from astrologer.knowledge.evaluation import (
    FactEvaluationProvenance,
    GovernedRuleEvaluator,
    canonical_sha256,
    fact_set_sha256,
)
from astrologer.knowledge.models import JyotishDomain
from astrologer.knowledge.spirituality_pack_v1 import ACTIVE_PRODUCTION_RELEASE as RELEASE_V8
from astrologer.knowledge.travel_pack_v1 import (
    ACTIVE_PRODUCTION_RELEASE,
    FACT_CONTRACT,
    PRODUCTION_MANIFEST,
    SIXTH_LORD_FACT_ID,
    SOURCE_REGISTRY,
    TRAVEL_INTERPRETATION_ID,
    TRAVEL_RULE_ENVELOPE,
    TRAVEL_RULE_ID,
)
from astrologer.questions.models import (
    QuestionDomain,
    QuestionIntent,
    QuestionRequest,
    QuestionShape,
    TemporalIntent,
)
from astrologer.questions.router import QuestionIntentRouter
from astrologer.rules.models import EvaluationStatus, Fact, FactSet


def _evaluate(*facts: Fact):
    fact_set = FactSet(facts=facts)
    provenance = FactEvaluationProvenance(
        methodology_id=FACT_CONTRACT.methodology_id,
        source_register_version=SOURCE_REGISTRY.registry_version,
        derived_fact_provenance_sha256="0" * 64,
        fact_set_sha256=fact_set_sha256(fact_set),
    )
    return GovernedRuleEvaluator().evaluate(
        PRODUCTION_MANIFEST,
        ACTIVE_PRODUCTION_RELEASE.envelopes,
        SOURCE_REGISTRY,
        FACT_CONTRACT,
        fact_set,
        provenance,
    )


def _package(*facts: Fact) -> EvidencePackage:
    fact_set = FactSet(facts=facts)
    values = fact_set.by_id()
    items = tuple(
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
        for result in _evaluate(*facts)
    )
    return EvidencePackage.model_construct(
        matched_evidence=tuple(
            item for item in items if item.evaluation_status is EvaluationStatus.TRUE
        ),
        unmatched_evaluations=tuple(
            item for item in items if item.evaluation_status is EvaluationStatus.FALSE
        ),
        unknown_evaluations=tuple(
            item for item in items if item.evaluation_status is EvaluationStatus.UNKNOWN
        ),
        corpus_release=PRODUCTION_MANIFEST,
        manifest_content_sha256=PRODUCTION_MANIFEST.content_sha256(),
        package_content_sha256="0" * 64,
    )


def _intent(domain: QuestionDomain, *, timing: bool = False) -> QuestionIntent:
    return QuestionIntent(
        intent_id="intent-1",
        domain=domain,
        shape=QuestionShape.TIMING if timing else QuestionShape.DESCRIPTIVE,
        temporal_intent=TemporalIntent.TIME_BOUND if timing else TemporalIntent.CURRENT,
        requires_timing=timing,
    )


def _travel_result(*facts: Fact):
    return next(item for item in _evaluate(*facts) if item.evaluation.rule_id == TRAVEL_RULE_ID)


def test_travel_rule_has_exact_true_false_and_unknown_semantics() -> None:
    for value in (2, 10):
        assert _travel_result(Fact(fact_id=SIXTH_LORD_FACT_ID, value=value)).evaluation.status is (
            EvaluationStatus.TRUE
        )
    assert _travel_result(Fact(fact_id=SIXTH_LORD_FACT_ID, value=9)).evaluation.status is (
        EvaluationStatus.FALSE
    )
    unknown = _travel_result()
    assert unknown.evaluation.status is EvaluationStatus.UNKNOWN
    assert unknown.evaluation.condition.referenced_fact_ids == (SIXTH_LORD_FACT_ID,)


def test_v9_explicitly_admits_one_travel_rule_and_preserves_v8() -> None:
    ids = tuple(item.rule.rule_id for item in ACTIVE_PRODUCTION_RELEASE.envelopes)
    travel = tuple(
        item for item in ACTIVE_PRODUCTION_RELEASE.envelopes if item.domain is JyotishDomain.TRAVEL
    )
    assert ACTIVE_PRODUCTION_RELEASE.release_version == "v9"
    assert FACT_CONTRACT is RELEASE_V8.fact_contract
    assert FACT_CONTRACT.contract_version == "v5"
    assert len(ids) == len(set(ids)) == 21
    assert set(ids) == {item.rule.rule_id for item in RELEASE_V8.envelopes} | {TRAVEL_RULE_ID}
    assert travel == (TRAVEL_RULE_ENVELOPE,)
    assert TRAVEL_RULE_ENVELOPE.interpretation_id == TRAVEL_INTERPRETATION_ID
    assert not any("malefic" in rule_id or "benefic" in rule_id for rule_id in ids)
    assert (
        RELEASE_V8.manifest.content_sha256()
        == "d7e8e065626d931137e21f16d6dd5e258ef9513c4cbe298eba4cbbfe43ca5a6a"
    )
    assert (
        canonical_sha256(RELEASE_V8)
        == "6c3f973b4f0a4f742d34d5b87e2b25a5ae1992b3f247a7b4668ab88bb56735da"
    )


def test_exact_domain_selection_separates_travel_and_business() -> None:
    package = _package(Fact(fact_id=SIXTH_LORD_FACT_ID, value=10))
    selector = EvidenceSelector()
    travel = selector.select(_intent(QuestionDomain.TRAVEL), package)
    business = selector.select(_intent(QuestionDomain.BUSINESS), package)
    assert [item.rule_id for item in travel.selected_matched] == [TRAVEL_RULE_ID]
    assert any(item.rule_id == "bphs.d1.house_lord.6.in_9.business.v1" for item in travel.excluded)
    assert all(item.exclusion_reason.value == "domain_mismatch" for item in travel.excluded)
    assert business.selected_matched == ()
    assert any(item.rule_id == TRAVEL_RULE_ID for item in business.excluded)


def test_router_and_disabled_composer_handle_travel_without_provider_or_timing() -> None:
    routing = QuestionIntentRouter().route(QuestionRequest(question="When will I move abroad?"))
    assert routing.intents[0].domain is QuestionDomain.TRAVEL
    selection = EvidenceSelector().select(
        _intent(QuestionDomain.TRAVEL, timing=True),
        _package(Fact(fact_id=SIXTH_LORD_FACT_ID, value=2)),
    )
    answer = DeterministicAnswerComposer().compose(
        "When will I move abroad?",
        InterpretationEvidenceBuilder(PRODUCTION_MANIFEST).build(selection),
    )
    assert answer.corpus_limitation is False
    assert answer.timing_answered is False
    assert answer.provider_id == "deterministic-governed-composer"
    assert (
        answer.answer
        == "This is contextual natal evidence related to travel or residence away from the native "
        "place. In the selected BPHS passage, the D1 sixth-house lord in the second or tenth "
        "house is associated with being comfortable in a foreign place. It does not establish "
        "relocation timing, permanent foreign settlement, immigration status, visa or "
        "citizenship outcomes, or a specific destination. Timing is not established by the "
        "current governed evidence."
    )


def test_disabled_composer_returns_travel_corpus_limit_without_match() -> None:
    evidence = InterpretationEvidenceBuilder(PRODUCTION_MANIFEST).build(
        EvidenceSelector().select(
            _intent(QuestionDomain.TRAVEL),
            _package(Fact(fact_id=SIXTH_LORD_FACT_ID, value=9)),
        )
    )
    answer = DeterministicAnswerComposer().compose("Will I travel abroad?", evidence)
    assert answer.corpus_limitation is True
    assert answer.provider_id == "deterministic-corpus-limit"
