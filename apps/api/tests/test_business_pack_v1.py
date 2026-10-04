"""Synthetic deterministic coverage for the reviewed Business Pack v1 release."""

from astrologer.composition import DeterministicAnswerComposer
from astrologer.evidence import EvidenceSelector, InterpretationEvidenceBuilder
from astrologer.evidence.models import EvidenceItem, EvidencePackage, ResolvedEvidenceFact
from astrologer.knowledge.business_pack_v1 import (
    ACTIVE_PRODUCTION_RELEASE,
    BUSINESS_INTERPRETATION_ID,
    BUSINESS_RULE_ENVELOPE,
    BUSINESS_RULE_ID,
    FACT_CONTRACT,
    PRODUCTION_MANIFEST,
    SIXTH_LORD_FACT_ID,
    SOURCE_REGISTRY,
)
from astrologer.knowledge.education_pack_v1 import ACTIVE_PRODUCTION_RELEASE as RELEASE_V5
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


def _business_result(*facts: Fact):
    return next(item for item in _evaluate(*facts) if item.evaluation.rule_id == BUSINESS_RULE_ID)


def test_business_rule_has_exact_true_false_and_unknown_semantics() -> None:
    assert _business_result(Fact(fact_id=SIXTH_LORD_FACT_ID, value=9)).evaluation.status is (
        EvaluationStatus.TRUE
    )
    assert _business_result(Fact(fact_id=SIXTH_LORD_FACT_ID, value=8)).evaluation.status is (
        EvaluationStatus.FALSE
    )
    unknown = _business_result()
    assert unknown.evaluation.status is EvaluationStatus.UNKNOWN
    assert unknown.evaluation.condition.referenced_fact_ids == (SIXTH_LORD_FACT_ID,)


def test_v6_explicitly_admits_only_one_business_rule_and_preserves_v5() -> None:
    ids = tuple(item.rule.rule_id for item in ACTIVE_PRODUCTION_RELEASE.envelopes)
    business = tuple(
        item
        for item in ACTIVE_PRODUCTION_RELEASE.envelopes
        if item.domain is JyotishDomain.BUSINESS
    )
    assert ACTIVE_PRODUCTION_RELEASE.release_version == "v6"
    assert FACT_CONTRACT.contract_version == "v5"
    assert FACT_CONTRACT.available_fact_ids == RELEASE_V5.fact_contract.available_fact_ids + (
        SIXTH_LORD_FACT_ID,
    )
    assert len(ids) == len(set(ids)) == 13
    assert {item.rule.rule_id for item in RELEASE_V5.envelopes} | {BUSINESS_RULE_ID} == set(ids)
    assert business == (BUSINESS_RULE_ENVELOPE,)
    assert not any(
        candidate in ids
        for candidate in ("candidate.2", "candidate.3", "candidate.4", "candidate.5")
    )
    assert (
        RELEASE_V5.manifest.content_sha256()
        == "1324230f41b502e551b0edd4eecddc188eef5f79d4ac31baf0a27514fb61f05d"
    )
    assert (
        canonical_sha256(RELEASE_V5)
        == "ac8880f444888ffa72e63f6a21fe33d86e12ba25c8f9241eb33af6cdc1664d0e"
    )


def test_exact_domain_selection_excludes_all_non_business_domains() -> None:
    package = _package(Fact(fact_id=SIXTH_LORD_FACT_ID, value=9))
    selector = EvidenceSelector()
    business = selector.select(_intent(QuestionDomain.BUSINESS), package)
    career = selector.select(_intent(QuestionDomain.CAREER), package)
    wealth = selector.select(_intent(QuestionDomain.WEALTH), package)
    education = selector.select(_intent(QuestionDomain.EDUCATION), package)
    general = selector.select(_intent(QuestionDomain.GENERAL), package)
    assert [item.rule_id for item in business.selected_matched] == [BUSINESS_RULE_ID]
    assert all(item.exclusion_reason.value == "domain_mismatch" for item in business.excluded)
    assert {item.domain for item in business.excluded} == {
        JyotishDomain.GENERAL,
        JyotishDomain.CAREER,
        JyotishDomain.WEALTH,
        JyotishDomain.EDUCATION,
    }
    for selection in (career, wealth, education, general):
        assert selection.selected_matched == ()
        assert any(item.rule_id == BUSINESS_RULE_ID for item in selection.excluded)


def test_disabled_composer_renders_business_wording_and_timing_limit() -> None:
    selection = EvidenceSelector().select(
        _intent(QuestionDomain.BUSINESS, timing=True),
        _package(Fact(fact_id=SIXTH_LORD_FACT_ID, value=9)),
    )
    evidence = InterpretationEvidenceBuilder().build(selection)
    answer = DeterministicAnswerComposer().compose("When will my business improve?", evidence)
    assert answer.corpus_limitation is False
    assert answer.timing_answered is False
    assert answer.provider_id == "deterministic-governed-composer"
    assert answer.answer == (
        "With the D1 sixth-house lord in the ninth house, this is contextual natal evidence for "
        "commercial activity. The selected BPHS rendering associates this placement with selling "
        "goods such as wood or stone and with trade. It does not establish business success, "
        "profit or loss, livelihood, self-employment, timing, or certainty. Timing is not "
        "established by the current governed evidence."
    )


def test_disabled_composer_returns_business_corpus_limit_without_match() -> None:
    evidence = InterpretationEvidenceBuilder().build(
        EvidenceSelector().select(
            _intent(QuestionDomain.BUSINESS),
            _package(Fact(fact_id=SIXTH_LORD_FACT_ID, value=8)),
        )
    )
    answer = DeterministicAnswerComposer().compose("How is my business?", evidence)
    assert answer.corpus_limitation is True
    assert answer.provider_id == "deterministic-corpus-limit"


def test_business_interpretation_identity_is_distinct_and_immutable() -> None:
    interpretation = next(
        item
        for item in SOURCE_REGISTRY.interpretations
        if item.interpretation_id == BUSINESS_INTERPRETATION_ID
    )
    assert interpretation.interpretation_version == "v1"
    assert interpretation.passage_id == "bphs.bhavesha-phala.6th-lord.9"
    assert all(
        item.interpretation_id != BUSINESS_INTERPRETATION_ID
        for item in RELEASE_V5.registry.interpretations
    )
