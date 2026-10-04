"""Synthetic deterministic coverage for Friends / Social Network Pack v1."""

from astrologer.composition import DeterministicAnswerComposer
from astrologer.evidence import EvidenceSelector, InterpretationEvidenceBuilder
from astrologer.evidence.models import EvidenceItem, EvidencePackage, ResolvedEvidenceFact
from astrologer.knowledge.evaluation import (
    FactEvaluationProvenance,
    GovernedRuleEvaluator,
    canonical_sha256,
    fact_set_sha256,
)
from astrologer.knowledge.friends_pack_v1 import (
    ACTIVE_PRODUCTION_RELEASE,
    FACT_CONTRACT,
    FRIENDS_INTERPRETATION_ID,
    FRIENDS_RULE_ENVELOPE,
    FRIENDS_RULE_ID,
    PRODUCTION_MANIFEST,
    SOURCE_REGISTRY,
    TENTH_LORD_FACT_ID,
)
from astrologer.knowledge.models import JyotishDomain
from astrologer.knowledge.travel_pack_v1 import ACTIVE_PRODUCTION_RELEASE as RELEASE_V9
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


def _friends_result(*facts: Fact):
    return next(item for item in _evaluate(*facts) if item.evaluation.rule_id == FRIENDS_RULE_ID)


def test_friends_rule_has_exact_true_false_and_unknown_semantics() -> None:
    assert (
        _friends_result(Fact(fact_id=TENTH_LORD_FACT_ID, value=9)).evaluation.status
        is EvaluationStatus.TRUE
    )
    assert (
        _friends_result(Fact(fact_id=TENTH_LORD_FACT_ID, value=8)).evaluation.status
        is EvaluationStatus.FALSE
    )
    unknown = _friends_result()
    assert unknown.evaluation.status is EvaluationStatus.UNKNOWN
    assert unknown.evaluation.condition.referenced_fact_ids == (TENTH_LORD_FACT_ID,)


def test_v10_explicitly_admits_one_friends_rule_and_preserves_v9() -> None:
    ids = tuple(item.rule.rule_id for item in ACTIVE_PRODUCTION_RELEASE.envelopes)
    friends = tuple(
        item for item in ACTIVE_PRODUCTION_RELEASE.envelopes if item.domain is JyotishDomain.FRIENDS
    )
    assert ACTIVE_PRODUCTION_RELEASE.release_version == "v10"
    assert FACT_CONTRACT is RELEASE_V9.fact_contract
    assert FACT_CONTRACT.contract_version == "v5"
    assert len(ids) == len(set(ids)) == 22
    assert set(ids) == {item.rule.rule_id for item in RELEASE_V9.envelopes} | {FRIENDS_RULE_ID}
    assert friends == (FRIENDS_RULE_ENVELOPE,)
    assert FRIENDS_RULE_ENVELOPE.interpretation_id == FRIENDS_INTERPRETATION_ID
    assert not any(
        candidate in rule_id
        for rule_id in ids
        for candidate in ("avastha", "sabha", "gamana", "agamana")
    )
    assert (
        RELEASE_V9.manifest.content_sha256()
        == "6bce7e766f52f192524e57e58c62054478ab94f431c6c227e8e728ebac0e2878"
    )
    assert (
        canonical_sha256(RELEASE_V9)
        == "a9fb137f27778c7a5b98b7f6c2e8da50f512f01971632635aced84c75abdb093"
    )


def test_exact_domain_selection_separates_friends_career_and_spirituality() -> None:
    package = _package(Fact(fact_id=TENTH_LORD_FACT_ID, value=9))
    selector = EvidenceSelector()
    friends = selector.select(_intent(QuestionDomain.FRIENDS), package)
    career = selector.select(_intent(QuestionDomain.CAREER), package)
    spirituality = selector.select(_intent(QuestionDomain.SPIRITUALITY), package)
    assert [item.rule_id for item in friends.selected_matched] == [FRIENDS_RULE_ID]
    assert {
        item.rule_id
        for item in friends.excluded
        if item.rule_id
        in {
            "bphs.d1.house_lord.10.equals_9.v1",
            "bphs.d1.house_lord.10.equals_9.spirituality.v1",
        }
    } == {
        "bphs.d1.house_lord.10.equals_9.v1",
        "bphs.d1.house_lord.10.equals_9.spirituality.v1",
    }
    assert all(item.exclusion_reason.value == "domain_mismatch" for item in friends.excluded)
    assert FRIENDS_RULE_ID in {item.rule_id for item in career.excluded}
    assert FRIENDS_RULE_ID in {item.rule_id for item in spirituality.excluded}
    assert all(item.exclusion_reason.value == "domain_mismatch" for item in career.excluded)
    assert all(item.exclusion_reason.value == "domain_mismatch" for item in spirituality.excluded)


def test_router_and_disabled_composer_handle_friends_without_provider_or_timing() -> None:
    routing = QuestionIntentRouter().route(
        QuestionRequest(question="When will I make good friends?")
    )
    assert routing.intents[0].domain is QuestionDomain.FRIENDS
    selection = EvidenceSelector().select(
        _intent(QuestionDomain.FRIENDS, timing=True),
        _package(Fact(fact_id=TENTH_LORD_FACT_ID, value=9)),
    )
    answer = DeterministicAnswerComposer().compose(
        "When will I make good friends?",
        InterpretationEvidenceBuilder(PRODUCTION_MANIFEST).build(selection),
    )
    assert answer.corpus_limitation is False
    assert answer.timing_answered is False
    assert answer.provider_id == "deterministic-governed-composer"
    assert answer.answer.endswith("Timing is not established by the current governed evidence.")


def test_disabled_composer_returns_friends_corpus_limit_without_match() -> None:
    evidence = InterpretationEvidenceBuilder(PRODUCTION_MANIFEST).build(
        EvidenceSelector().select(
            _intent(QuestionDomain.FRIENDS),
            _package(Fact(fact_id=TENTH_LORD_FACT_ID, value=8)),
        )
    )
    answer = DeterministicAnswerComposer().compose("Will I make good friends?", evidence)
    assert answer.corpus_limitation is True
    assert answer.provider_id == "deterministic-corpus-limit"
