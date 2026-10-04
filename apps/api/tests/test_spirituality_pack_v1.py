"""Synthetic deterministic coverage for the reviewed Spirituality / Dharma Pack v1."""

import pytest

from astrologer.composition import DeterministicAnswerComposer
from astrologer.evidence import EvidenceSelector, InterpretationEvidenceBuilder
from astrologer.evidence.models import EvidenceItem, EvidencePackage, ResolvedEvidenceFact
from astrologer.knowledge.children_pack_v1 import ACTIVE_PRODUCTION_RELEASE as RELEASE_V7
from astrologer.knowledge.evaluation import (
    FactEvaluationProvenance,
    GovernedRuleEvaluator,
    canonical_sha256,
    fact_set_sha256,
)
from astrologer.knowledge.models import JyotishDomain
from astrologer.knowledge.spirituality_pack_v1 import (
    ACTIVE_PRODUCTION_RELEASE,
    ELEVENTH_LORD_FACT_ID,
    FACT_CONTRACT,
    PRODUCTION_MANIFEST,
    SOURCE_REGISTRY,
    SPIRITUALITY_INTERPRETATION_IDS,
    SPIRITUALITY_RULE_ENVELOPES,
    SPIRITUALITY_RULE_IDS,
    TENTH_LORD_FACT_ID,
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


@pytest.mark.parametrize(
    ("rule_id", "fact_id", "matches", "non_match"),
    (
        (SPIRITUALITY_RULE_IDS[0], TENTH_LORD_FACT_ID, (4, 10), 3),
        (SPIRITUALITY_RULE_IDS[1], TENTH_LORD_FACT_ID, (9,), 8),
        (SPIRITUALITY_RULE_IDS[2], ELEVENTH_LORD_FACT_ID, (2, 5), 3),
        (SPIRITUALITY_RULE_IDS[3], ELEVENTH_LORD_FACT_ID, (9, 10), 8),
    ),
)
def test_spirituality_rules_have_exact_true_false_and_unknown_semantics(
    rule_id: str, fact_id: str, matches: tuple[int, ...], non_match: int
) -> None:
    for value in matches:
        result = next(
            item
            for item in _evaluate(Fact(fact_id=fact_id, value=value))
            if item.evaluation.rule_id == rule_id
        )
        assert result.evaluation.status is EvaluationStatus.TRUE
    result = next(
        item
        for item in _evaluate(Fact(fact_id=fact_id, value=non_match))
        if item.evaluation.rule_id == rule_id
    )
    assert result.evaluation.status is EvaluationStatus.FALSE
    result = next(item for item in _evaluate() if item.evaluation.rule_id == rule_id)
    assert result.evaluation.status is EvaluationStatus.UNKNOWN
    assert result.evaluation.condition.referenced_fact_ids == (fact_id,)


def test_v8_explicitly_admits_four_spirituality_rules_and_preserves_v7() -> None:
    ids = tuple(item.rule.rule_id for item in ACTIVE_PRODUCTION_RELEASE.envelopes)
    assert ACTIVE_PRODUCTION_RELEASE.release_version == "v8"
    assert FACT_CONTRACT.contract_version == "v5"
    assert FACT_CONTRACT is RELEASE_V7.fact_contract
    assert len(ids) == len(set(ids)) == 20
    assert set(ids) == {item.rule.rule_id for item in RELEASE_V7.envelopes} | set(
        SPIRITUALITY_RULE_IDS
    )
    assert tuple(item.rule.rule_id for item in SPIRITUALITY_RULE_ENVELOPES) == SPIRITUALITY_RULE_IDS
    assert all(item.domain is JyotishDomain.SPIRITUALITY for item in SPIRITUALITY_RULE_ENVELOPES)
    assert (
        RELEASE_V7.manifest.content_sha256()
        == "1f158a37959f2b38e7e8b65ff54b412d644ce6a86aaaba6f41e5c8e8ca443b48"
    )
    assert (
        canonical_sha256(RELEASE_V7)
        == "a50bb352734a902bae11be02fcf7589e52c6705390627f425490a46e1595b9b9"
    )
    assert (
        PRODUCTION_MANIFEST.content_sha256()
        == "d7e8e065626d931137e21f16d6dd5e258ef9513c4cbe298eba4cbbfe43ca5a6a"
    )


def test_shared_sources_keep_distinct_spirituality_rule_and_interpretation_identities() -> None:
    interpretations = {item.interpretation_id: item for item in SOURCE_REGISTRY.interpretations}
    envelopes = {item.rule.rule_id: item for item in ACTIVE_PRODUCTION_RELEASE.envelopes}
    overlaps = (
        (SPIRITUALITY_RULE_IDS[0], "bphs.d1.house_lord.10.in_4_or_10.v1"),
        (SPIRITUALITY_RULE_IDS[1], "bphs.d1.house_lord.10.equals_9.v1"),
        (
            SPIRITUALITY_RULE_IDS[2],
            "bphs.d1.house_lord.11.in_2_or_5.wealth.v1",
            "bphs.d1.house_lord.11.in_2_or_5.children.v1",
        ),
        (
            SPIRITUALITY_RULE_IDS[3],
            "bphs.d1.house_lord.11.in_9_or_10.v1",
            "bphs.d1.house_lord.11.in_9_or_10.wealth.v1",
        ),
    )
    for spirituality_id, *existing_ids in overlaps:
        spirituality = envelopes[spirituality_id]
        for existing_id in existing_ids:
            existing = envelopes[existing_id]
            assert spirituality.interpretation_id != existing.interpretation_id
            assert (
                interpretations[spirituality.interpretation_id].passage_id
                == interpretations[existing.interpretation_id].passage_id
            )
    assert (
        tuple(item.interpretation_id for item in SPIRITUALITY_RULE_ENVELOPES)
        == SPIRITUALITY_INTERPRETATION_IDS
    )


def test_exact_domain_selection_separates_spirituality_from_all_existing_domains() -> None:
    package = _package(
        Fact(fact_id=TENTH_LORD_FACT_ID, value=4), Fact(fact_id=ELEVENTH_LORD_FACT_ID, value=2)
    )
    selector = EvidenceSelector()
    spirituality = selector.select(_intent(QuestionDomain.SPIRITUALITY), package)
    assert {item.rule_id for item in spirituality.selected_matched} == {
        SPIRITUALITY_RULE_IDS[0],
        SPIRITUALITY_RULE_IDS[2],
    }
    assert all(item.exclusion_reason.value == "domain_mismatch" for item in spirituality.excluded)
    for domain in (
        QuestionDomain.GENERAL,
        QuestionDomain.CAREER,
        QuestionDomain.WEALTH,
        QuestionDomain.EDUCATION,
        QuestionDomain.BUSINESS,
        QuestionDomain.CHILDREN,
    ):
        selection = selector.select(_intent(domain), package)
        assert all(
            item.domain is not JyotishDomain.SPIRITUALITY for item in selection.selected_matched
        )
        assert all(item.exclusion_reason.value == "domain_mismatch" for item in selection.excluded)
        assert any(item.rule_id in SPIRITUALITY_RULE_IDS for item in selection.excluded)


def test_router_and_disabled_composer_handle_spirituality_without_provider_or_timing() -> None:
    routing = QuestionIntentRouter().route(
        QuestionRequest(question="When will my spiritual life improve?")
    )
    assert routing.intents[0].domain is QuestionDomain.SPIRITUALITY
    selection = EvidenceSelector().select(
        _intent(QuestionDomain.SPIRITUALITY, timing=True),
        _package(Fact(fact_id=TENTH_LORD_FACT_ID, value=4)),
    )
    answer = DeterministicAnswerComposer().compose(
        "When will my spiritual life improve?", InterpretationEvidenceBuilder().build(selection)
    )
    assert answer.corpus_limitation is False
    assert answer.timing_answered is False
    assert answer.provider_id == "deterministic-governed-composer"
    assert answer.answer.endswith("Timing is not established by the current governed evidence.")
    assert "religious identity, moral standing, timing, or certainty." in answer.answer


def test_disabled_composer_returns_spirituality_corpus_limit_without_match() -> None:
    evidence = InterpretationEvidenceBuilder().build(
        EvidenceSelector().select(
            _intent(QuestionDomain.SPIRITUALITY),
            _package(Fact(fact_id=TENTH_LORD_FACT_ID, value=3)),
        )
    )
    answer = DeterministicAnswerComposer().compose("Will I be spiritual?", evidence)
    assert answer.corpus_limitation is True
    assert answer.provider_id == "deterministic-corpus-limit"
