"""Synthetic deterministic coverage for the reviewed Education Pack v1 release."""

import pytest

from astrologer.composition import DeterministicAnswerComposer
from astrologer.evidence import EvidenceSelector, InterpretationEvidenceBuilder
from astrologer.evidence.models import EvidenceItem, EvidencePackage, ResolvedEvidenceFact
from astrologer.knowledge.education_pack_v1 import (
    ACTIVE_PRODUCTION_RELEASE,
    EDUCATION_RULE_ENVELOPES,
    ELEVENTH_LORD_FACT_ID,
    FACT_CONTRACT,
    FIFTH_LORD_FACT_ID,
    FOURTH_LORD_FACT_ID,
    PRODUCTION_MANIFEST,
    SOURCE_REGISTRY,
)
from astrologer.knowledge.evaluation import (
    FactEvaluationProvenance,
    GovernedRuleEvaluator,
    canonical_sha256,
    fact_set_sha256,
)
from astrologer.knowledge.models import JyotishDomain
from astrologer.knowledge.wealth_pack_v1 import ACTIVE_PRODUCTION_RELEASE as RELEASE_V4
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
        ("bphs.d1.house_lord.4.in_1_or_7.education.v1", FOURTH_LORD_FACT_ID, (1, 7), 2),
        ("bphs.d1.house_lord.5.in_11.education.v1", FIFTH_LORD_FACT_ID, (11,), 3),
        ("bphs.d1.house_lord.11.in_11.education.v1", ELEVENTH_LORD_FACT_ID, (11,), 3),
    ),
)
def test_education_rules_have_exact_true_false_and_unknown_semantics(
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


def test_v5_explicitly_admits_education_and_preserves_v4() -> None:
    ids = tuple(item.rule.rule_id for item in ACTIVE_PRODUCTION_RELEASE.envelopes)
    assert ACTIVE_PRODUCTION_RELEASE.release_version == "v5"
    assert FACT_CONTRACT.contract_version == "v4"
    assert len(ids) == len(set(ids)) == 12
    assert set(ids) == {item.rule.rule_id for item in RELEASE_V4.envelopes} | {
        item.rule.rule_id for item in EDUCATION_RULE_ENVELOPES
    }
    assert len(EDUCATION_RULE_ENVELOPES) == 3
    assert all(item.domain is JyotishDomain.EDUCATION for item in EDUCATION_RULE_ENVELOPES)
    assert (
        RELEASE_V4.manifest.content_sha256()
        == "2ad0f17f15633a484df9dc39a6bc9e280c2aca6fea4d78b50421b60efa2aa139"
    )
    assert (
        canonical_sha256(RELEASE_V4)
        == "f91ac25636f8bca3f31265cda3647417eee8945a466c4a69ba42197521074796"
    )
    assert (
        PRODUCTION_MANIFEST.content_sha256()
        == "1324230f41b502e551b0edd4eecddc188eef5f79d4ac31baf0a27514fb61f05d"
    )
    assert (
        canonical_sha256(ACTIVE_PRODUCTION_RELEASE)
        == "ac8880f444888ffa72e63f6a21fe33d86e12ba25c8f9241eb33af6cdc1664d0e"
    )


def test_shared_fifth_lord_source_has_distinct_education_and_wealth_identities() -> None:
    education = next(
        item
        for item in EDUCATION_RULE_ENVELOPES
        if item.rule.rule_id.endswith("5.in_11.education.v1")
    )
    wealth = next(
        item for item in RELEASE_V4.envelopes if item.rule.rule_id.endswith("5.in_11.wealth.v1")
    )
    interpretations = {item.interpretation_id: item for item in SOURCE_REGISTRY.interpretations}
    assert education.rule.rule_id != wealth.rule.rule_id
    assert education.interpretation_id != wealth.interpretation_id
    assert (
        interpretations[education.interpretation_id].passage_id
        == interpretations[wealth.interpretation_id].passage_id
    )


def test_exact_domain_selection_isolates_education_and_wealth_shared_condition() -> None:
    package = _package(Fact(fact_id=FIFTH_LORD_FACT_ID, value=11))
    selector = EvidenceSelector()
    education = selector.select(_intent(QuestionDomain.EDUCATION), package)
    wealth = selector.select(_intent(QuestionDomain.WEALTH), package)
    assert [item.rule_id for item in education.selected_matched] == [
        "bphs.d1.house_lord.5.in_11.education.v1"
    ]
    assert [item.rule_id for item in wealth.selected_matched] == [
        "bphs.d1.house_lord.5.in_11.wealth.v1"
    ]
    assert {item.domain for item in education.excluded} == {
        JyotishDomain.GENERAL,
        JyotishDomain.CAREER,
        JyotishDomain.WEALTH,
    }
    assert any(
        item.rule_id == "bphs.d1.house_lord.5.in_11.wealth.v1" for item in education.excluded
    )
    assert any(
        item.rule_id == "bphs.d1.house_lord.5.in_11.education.v1" for item in wealth.excluded
    )


def test_disabled_composer_renders_education_wording_and_timing_limit() -> None:
    package = _package(Fact(fact_id=FOURTH_LORD_FACT_ID, value=1))
    selection = EvidenceSelector().select(_intent(QuestionDomain.EDUCATION, timing=True), package)
    evidence = InterpretationEvidenceBuilder().build(selection)
    answer = DeterministicAnswerComposer().compose("When will my studies improve?", evidence)
    assert answer.corpus_limitation is False
    assert answer.timing_answered is False
    assert answer.answer.endswith("Timing is not established by the current governed evidence.")


def test_disabled_composer_returns_education_corpus_limit_without_match() -> None:
    package = _package(Fact(fact_id=FOURTH_LORD_FACT_ID, value=2))
    evidence = InterpretationEvidenceBuilder().build(
        EvidenceSelector().select(_intent(QuestionDomain.EDUCATION), package)
    )
    answer = DeterministicAnswerComposer().compose("How are my studies?", evidence)
    assert answer.corpus_limitation is True
