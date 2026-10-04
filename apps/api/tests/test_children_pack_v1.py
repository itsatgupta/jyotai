"""Synthetic deterministic coverage for the reviewed Children / Progeny Pack v1."""

import pytest

from astrologer.composition import DeterministicAnswerComposer
from astrologer.evidence import EvidenceSelector, InterpretationEvidenceBuilder
from astrologer.evidence.models import EvidenceItem, EvidencePackage, ResolvedEvidenceFact
from astrologer.knowledge.business_pack_v1 import ACTIVE_PRODUCTION_RELEASE as RELEASE_V6
from astrologer.knowledge.children_pack_v1 import (
    ACTIVE_PRODUCTION_RELEASE,
    CHILDREN_INTERPRETATION_IDS,
    CHILDREN_RULE_ENVELOPES,
    CHILDREN_RULE_IDS,
    ELEVENTH_LORD_FACT_ID,
    FACT_CONTRACT,
    FIFTH_LORD_FACT_ID,
    PRODUCTION_MANIFEST,
    SOURCE_REGISTRY,
    TENTH_LORD_FACT_ID,
)
from astrologer.knowledge.evaluation import (
    FactEvaluationProvenance,
    GovernedRuleEvaluator,
    canonical_sha256,
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
        (CHILDREN_RULE_IDS[0], FIFTH_LORD_FACT_ID, (11,), 10),
        (CHILDREN_RULE_IDS[1], ELEVENTH_LORD_FACT_ID, (2, 5), 3),
        (CHILDREN_RULE_IDS[2], TENTH_LORD_FACT_ID, (5, 11), 9),
    ),
)
def test_children_rules_have_exact_true_false_and_unknown_semantics(
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


def test_v7_explicitly_admits_three_children_rules_and_preserves_v6() -> None:
    ids = tuple(item.rule.rule_id for item in ACTIVE_PRODUCTION_RELEASE.envelopes)
    assert ACTIVE_PRODUCTION_RELEASE.release_version == "v7"
    assert FACT_CONTRACT.contract_version == "v5"
    assert FACT_CONTRACT is RELEASE_V6.fact_contract
    assert len(ids) == len(set(ids)) == 16
    assert set(ids) == {item.rule.rule_id for item in RELEASE_V6.envelopes} | set(CHILDREN_RULE_IDS)
    assert tuple(item.rule.rule_id for item in CHILDREN_RULE_ENVELOPES) == CHILDREN_RULE_IDS
    assert all(item.domain is JyotishDomain.CHILDREN for item in CHILDREN_RULE_ENVELOPES)
    assert not any(
        "in_9_or_10.children" in rule_id or "house_lord.2.in_5.children" in rule_id
        for rule_id in ids
    )
    assert RELEASE_V6.manifest.content_sha256() == (
        "e84af683c345b5d4c89ba4a7acdeac55260505a25fa7b2058f9868102133d882"
    )
    assert canonical_sha256(RELEASE_V6) == (
        "5469d12786c2ddcc367062484c715c102f8f98cc97589fb3036a415934b0fd7c"
    )
    assert PRODUCTION_MANIFEST.content_sha256() == (
        "1f158a37959f2b38e7e8b65ff54b412d644ce6a86aaaba6f41e5c8e8ca443b48"
    )
    assert canonical_sha256(ACTIVE_PRODUCTION_RELEASE) == (
        "a50bb352734a902bae11be02fcf7589e52c6705390627f425490a46e1595b9b9"
    )


def test_shared_source_provenance_uses_distinct_children_rule_and_interpretation_identities() -> (
    None
):
    interpretations = {item.interpretation_id: item for item in SOURCE_REGISTRY.interpretations}
    overlaps = (
        (
            CHILDREN_RULE_IDS[0],
            "bphs.d1.house_lord.5.in_11.wealth.v1",
            "bphs.d1.house_lord.5.in_11.education.v1",
        ),
        (CHILDREN_RULE_IDS[1], "bphs.d1.house_lord.11.in_2_or_5.wealth.v1"),
        (CHILDREN_RULE_IDS[2], "bphs.d1.house_lord.10.in_5_or_11.v1"),
    )
    envelopes = {item.rule.rule_id: item for item in ACTIVE_PRODUCTION_RELEASE.envelopes}
    for children_id, *existing_ids in overlaps:
        children = envelopes[children_id]
        for existing_id in existing_ids:
            existing = envelopes[existing_id]
            assert children.rule.rule_id != existing.rule.rule_id
            assert children.interpretation_id != existing.interpretation_id
            assert (
                interpretations[children.interpretation_id].passage_id
                == interpretations[existing.interpretation_id].passage_id
            )
    assert (
        tuple(item.interpretation_id for item in CHILDREN_RULE_ENVELOPES)
        == CHILDREN_INTERPRETATION_IDS
    )
    assert all(
        item.interpretation_id
        not in {entry.interpretation_id for entry in RELEASE_V6.registry.interpretations}
        for item in CHILDREN_RULE_ENVELOPES
    )


def test_exact_domain_selection_keeps_children_and_shared_domains_separate() -> None:
    package = _package(
        Fact(fact_id=FIFTH_LORD_FACT_ID, value=11),
        Fact(fact_id=ELEVENTH_LORD_FACT_ID, value=2),
        Fact(fact_id=TENTH_LORD_FACT_ID, value=5),
    )
    selector = EvidenceSelector()
    children = selector.select(_intent(QuestionDomain.CHILDREN), package)
    assert {item.rule_id for item in children.selected_matched} == set(CHILDREN_RULE_IDS)
    assert all(item.exclusion_reason.value == "domain_mismatch" for item in children.excluded)
    for rule_id in (
        "bphs.d1.house_lord.5.in_11.wealth.v1",
        "bphs.d1.house_lord.5.in_11.education.v1",
        "bphs.d1.house_lord.11.in_2_or_5.wealth.v1",
        "bphs.d1.house_lord.10.in_5_or_11.v1",
    ):
        assert any(item.rule_id == rule_id for item in children.excluded)
    expected_existing_matches = {
        QuestionDomain.GENERAL: set(),
        QuestionDomain.CAREER: {"bphs.d1.house_lord.10.in_5_or_11.v1"},
        QuestionDomain.WEALTH: {
            "bphs.d1.house_lord.11.in_2_or_5.wealth.v1",
            "bphs.d1.house_lord.5.in_11.wealth.v1",
        },
        QuestionDomain.EDUCATION: {"bphs.d1.house_lord.5.in_11.education.v1"},
        QuestionDomain.BUSINESS: set(),
    }
    for domain, expected_matches in expected_existing_matches.items():
        selection = selector.select(_intent(domain), package)
        assert {item.rule_id for item in selection.selected_matched} == expected_matches
        assert all(item.domain is not JyotishDomain.CHILDREN for item in selection.selected_matched)
        assert all(item.exclusion_reason.value == "domain_mismatch" for item in selection.excluded)
        assert any(item.rule_id in CHILDREN_RULE_IDS for item in selection.excluded)


def test_disabled_composer_renders_children_wording_and_timing_limit() -> None:
    selection = EvidenceSelector().select(
        _intent(QuestionDomain.CHILDREN, timing=True),
        _package(Fact(fact_id=FIFTH_LORD_FACT_ID, value=11)),
    )
    evidence = InterpretationEvidenceBuilder(PRODUCTION_MANIFEST).build(selection)
    answer = DeterministicAnswerComposer().compose("When will I have children?", evidence)
    assert answer.corpus_limitation is False
    assert answer.timing_answered is False
    assert answer.provider_id == "deterministic-governed-composer"
    assert answer.answer == (
        "With the D1 fifth-house lord in the eleventh house, this is contextual natal evidence "
        "related to children/progeny. The selected BPHS passage also associates the placement "
        "with scholarship, authorship, skill, and wealth. It does not guarantee children, "
        "establish their number, or provide timing. Timing is not established by the current "
        "governed evidence."
    )


def test_disabled_composer_returns_children_corpus_limit_without_match() -> None:
    evidence = InterpretationEvidenceBuilder(PRODUCTION_MANIFEST).build(
        EvidenceSelector().select(
            _intent(QuestionDomain.CHILDREN),
            _package(Fact(fact_id=FIFTH_LORD_FACT_ID, value=10)),
        )
    )
    answer = DeterministicAnswerComposer().compose("Will I have children?", evidence)
    assert answer.corpus_limitation is True
    assert answer.provider_id == "deterministic-corpus-limit"
