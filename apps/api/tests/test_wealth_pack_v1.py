"""Synthetic deterministic coverage for the reviewed Wealth Pack v1 release."""

import pytest

from astrologer.evidence import EvidenceSelector
from astrologer.evidence.models import EvidenceItem, EvidencePackage, ResolvedEvidenceFact
from astrologer.knowledge.career_pack_v1 import ACTIVE_PRODUCTION_RELEASE as RELEASE_V3
from astrologer.knowledge.evaluation import (
    FactEvaluationProvenance,
    GovernedRuleEvaluator,
    canonical_sha256,
    fact_set_sha256,
)
from astrologer.knowledge.models import JyotishDomain
from astrologer.knowledge.wealth_pack_v1 import (
    ACTIVE_PRODUCTION_RELEASE,
    ELEVENTH_LORD_FACT_ID,
    FACT_CONTRACT,
    FIFTH_LORD_FACT_ID,
    PRODUCTION_MANIFEST,
    SOURCE_REGISTRY,
    WEALTH_RULE_ENVELOPES,
)
from astrologer.questions.models import (
    QuestionDomain,
    QuestionIntent,
    QuestionShape,
    TemporalIntent,
)
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


@pytest.mark.parametrize(
    ("rule_id", "fact_id", "matches", "non_match"),
    (
        ("bphs.d1.house_lord.11.in_1.wealth.v1", ELEVENTH_LORD_FACT_ID, (1,), 3),
        ("bphs.d1.house_lord.11.in_2_or_5.wealth.v1", ELEVENTH_LORD_FACT_ID, (2, 5), 3),
        ("bphs.d1.house_lord.11.in_9_or_10.wealth.v1", ELEVENTH_LORD_FACT_ID, (9, 10), 3),
        ("bphs.d1.house_lord.5.in_11.wealth.v1", FIFTH_LORD_FACT_ID, (11,), 3),
    ),
)
def test_wealth_rules_have_exact_true_false_and_unknown_semantics(
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


def test_v4_is_explicit_cumulative_admission_and_v3_is_unchanged() -> None:
    v4_ids = tuple(item.rule.rule_id for item in ACTIVE_PRODUCTION_RELEASE.envelopes)
    wealth_ids = tuple(item.rule.rule_id for item in WEALTH_RULE_ENVELOPES)
    assert ACTIVE_PRODUCTION_RELEASE.release_version == "v4"
    assert len(v4_ids) == len(set(v4_ids)) == 9
    assert set(v4_ids) == {item.rule.rule_id for item in RELEASE_V3.envelopes} | set(wealth_ids)
    assert len(wealth_ids) == 4
    assert all(item.domain is JyotishDomain.WEALTH for item in WEALTH_RULE_ENVELOPES)
    assert all(
        item.fact_dependencies[0].fact_id in {ELEVENTH_LORD_FACT_ID, FIFTH_LORD_FACT_ID}
        for item in WEALTH_RULE_ENVELOPES
    )
    assert not any("candidate-0" in rule_id for rule_id in v4_ids)
    assert (
        RELEASE_V3.manifest.content_sha256()
        == "88b1650b62f4f05719707b8911d2cb2e748d11a5b9f924ca9fa481e97f0e0749"
    )
    assert (
        PRODUCTION_MANIFEST.content_sha256()
        == "2ad0f17f15633a484df9dc39a6bc9e280c2aca6fea4d78b50421b60efa2aa139"
    )
    assert (
        canonical_sha256(ACTIVE_PRODUCTION_RELEASE)
        == "f91ac25636f8bca3f31265cda3647417eee8945a466c4a69ba42197521074796"
    )


def test_candidate_three_has_shared_passage_but_distinct_general_and_wealth_identities() -> None:
    general = next(item for item in RELEASE_V3.envelopes if item.domain is JyotishDomain.GENERAL)
    wealth = next(
        item
        for item in WEALTH_RULE_ENVELOPES
        if item.rule.rule_id.endswith("11.in_9_or_10.wealth.v1")
    )
    interpretations = {item.interpretation_id: item for item in SOURCE_REGISTRY.interpretations}
    assert general.rule.rule_id != wealth.rule.rule_id
    assert general.interpretation_id != wealth.interpretation_id
    assert (
        interpretations[general.interpretation_id].passage_id
        == interpretations[wealth.interpretation_id].passage_id
    )


def test_exact_domain_selection_keeps_shared_candidate_three_separate() -> None:
    facts = FactSet(facts=(Fact(fact_id=ELEVENTH_LORD_FACT_ID, value=9),))
    evaluations = _evaluate(*facts.facts)
    values = facts.by_id()
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
        for result in evaluations
    )
    package = EvidencePackage.model_construct(
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
    selector = EvidenceSelector()

    def intent(domain: QuestionDomain) -> QuestionIntent:
        return QuestionIntent(
            intent_id="intent-1",
            domain=domain,
            shape=QuestionShape.DESCRIPTIVE,
            temporal_intent=TemporalIntent.CURRENT,
            requires_timing=False,
        )

    wealth = selector.select(intent(QuestionDomain.WEALTH), package)
    general = selector.select(intent(QuestionDomain.GENERAL), package)
    assert [item.rule_id for item in wealth.selected_matched] == [
        "bphs.d1.house_lord.11.in_9_or_10.wealth.v1"
    ]
    assert [item.rule_id for item in general.selected_matched] == [
        "bphs.d1.house_lord.11.in_9_or_10.v1"
    ]
    assert any(item.rule_id == "bphs.d1.house_lord.11.in_9_or_10.v1" for item in wealth.excluded)
    assert any(
        item.rule_id == "bphs.d1.house_lord.11.in_9_or_10.wealth.v1" for item in general.excluded
    )
