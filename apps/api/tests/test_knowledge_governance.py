"""Synthetic tests for Task 09B governance; no Jyotish doctrine is asserted here."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from astrologer.knowledge.admission import AdmissionError, AdmissionValidator, can_transition
from astrologer.knowledge.corpus import (
    EMPTY_PRODUCTION_MANIFEST,
    ManifestRule,
    ProductionCorpusLoader,
    ProductionCorpusLoadError,
    ProductionCorpusManifest,
    envelope_sha256,
)
from astrologer.knowledge.models import (
    EMPTY_SOURCE_REGISTRY,
    ChartScope,
    DeclarativeClause,
    EvidenceDirection,
    FactContract,
    FactDependency,
    JyotishDomain,
    ProductionRuleEnvelope,
    ReviewCategory,
    ReviewedInterpretation,
    ReviewRecord,
    ReviewStatus,
    RightsStatus,
    RuleLifecycle,
    RulePosture,
    RuleTaxonomy,
    SourceKind,
    SourcePassage,
    SourceRecord,
    SourceRegistry,
    TranslationApplicability,
    TranslationRecord,
)
from astrologer.rules.evaluator import RuleEvaluator
from astrologer.rules.models import (
    ConditionDefinition,
    ConditionKind,
    ConditionOperation,
    EvaluationStatus,
    Fact,
    FactSet,
    RuleDefinition,
    RuleEffect,
)

_REVIEWED_AT = datetime(2026, 10, 2, tzinfo=UTC)


def _condition(fact_id: str = "test.fact") -> ConditionDefinition:
    return ConditionDefinition(
        kind=ConditionKind.LEAF,
        operation=ConditionOperation.EQUALS,
        fact_id=fact_id,
        expected_value=True,
    )


def _rule(*, synthetic: bool = False) -> RuleDefinition:
    return RuleDefinition(
        rule_id="SYNTHETIC_GOVERNANCE_RULE",
        rule_version="1",
        ruleset_version="synthetic-governance-v1",
        name="Synthetic governance rule",
        domain="test",
        is_synthetic_demo=synthetic,
        condition=_condition(),
        effect=RuleEffect(effect_key="test.effect", label="Synthetic only"),
    )


def _registry(*, reviewed: bool = True, include_translation: bool = True) -> SourceRegistry:
    status = ReviewStatus.REVIEWED if reviewed else ReviewStatus.DRAFT

    def review(category: ReviewCategory) -> ReviewRecord:
        return ReviewRecord(
            category=category,
            status=status,
            reviewer="synthetic-reviewer",
            reviewed_at=_REVIEWED_AT,
        )

    source = SourceRecord(
        source_id="synthetic.source",
        source_version="1",
        kind=SourceKind.PRIMARY,
        title="Synthetic source fixture",
        original_language="synthetic",
        rights_status=RightsStatus.REFERENCE_ONLY,
    )
    passage = SourcePassage(
        passage_id="synthetic.passage",
        source_id=source.source_id,
        locator="fixture 1",
        passage_reference="synthetic reference only",
        review=review(ReviewCategory.SOURCE_VERIFICATION),
    )
    translations = (
        (
            TranslationRecord(
                translation_id="synthetic.translation",
                translation_version="1",
                passage_id=passage.passage_id,
                language="English",
                text="Synthetic translation.",
                review=review(ReviewCategory.TRANSLATION_VERIFICATION),
            ),
        )
        if include_translation
        else ()
    )
    interpretation = ReviewedInterpretation(
        interpretation_id="synthetic.interpretation",
        interpretation_version="1",
        passage_id=passage.passage_id,
        translation_id="synthetic.translation" if include_translation else None,
        translation_applicability=(
            TranslationApplicability.REQUIRED
            if include_translation
            else TranslationApplicability.NOT_APPLICABLE
        ),
        statement="Synthetic reviewed interpretation, not astrology doctrine.",
        review=review(ReviewCategory.INTERPRETATION_REVIEW),
    )
    return SourceRegistry(
        registry_version="synthetic-registry-v1",
        sources=(source,),
        passages=(passage,),
        translations=translations,
        interpretations=(interpretation,),
    )


def _contract() -> FactContract:
    return FactContract(
        contract_id="synthetic.fact.contract",
        contract_version="1",
        chart_scope=ChartScope.D1_RASHI,
        methodology_id="synthetic-facts-v1",
        available_fact_ids=("test.fact",),
        available_fact_family_prefixes=("test.",),
    )


def _envelope(
    *,
    lifecycle: RuleLifecycle = RuleLifecycle.PRODUCTION_ACTIVE,
    synthetic: bool = False,
    fact_id: str = "test.fact",
) -> ProductionRuleEnvelope:
    return ProductionRuleEnvelope(
        rule=_rule(synthetic=synthetic).model_copy(update={"condition": _condition(fact_id)}),
        lifecycle=lifecycle,
        domain=JyotishDomain.CAREER,
        taxonomy=RuleTaxonomy.NATAL_STRUCTURAL,
        posture=RulePosture.STATIC,
        evidence_direction=EvidenceDirection.SUPPORTING,
        chart_scope=ChartScope.D1_RASHI,
        fact_contract_id="synthetic.fact.contract",
        fact_contract_version="1",
        fact_contract_methodology_id="synthetic-facts-v1",
        fact_dependencies=(FactDependency(fact_id=fact_id),),
        applicability=DeclarativeClause(
            label="Synthetic applicability", condition=_condition(fact_id)
        ),
        prerequisites=(
            DeclarativeClause(label="Synthetic prerequisite", condition=_condition(fact_id)),
        ),
        exceptions=(DeclarativeClause(label="Synthetic exception", condition=_condition(fact_id)),),
        interpretation_id="synthetic.interpretation",
        formalization_review=ReviewRecord(
            category=ReviewCategory.FORMALIZATION_REVIEW,
            status=ReviewStatus.REVIEWED,
            reviewer="synthetic-formalizer",
            reviewed_at=_REVIEWED_AT,
        ),
    )


def _manifest(envelope: ProductionRuleEnvelope) -> ProductionCorpusManifest:
    return ProductionCorpusManifest(
        manifest_id="synthetic.manifest",
        manifest_version="1",
        registry_version="synthetic-registry-v1",
        fact_contract_id="synthetic.fact.contract",
        fact_contract_version="1",
        rules=(
            ManifestRule(
                rule_id=envelope.rule.rule_id,
                rule_version=envelope.rule.rule_version,
                envelope_sha256=envelope_sha256(envelope),
            ),
        ),
    )


def test_source_registry_preserves_source_to_translation_to_interpretation_traceability() -> None:
    registry = _registry()
    assert registry.interpretations[0].passage_id == registry.passages[0].passage_id
    assert registry.interpretations[0].translation_id == registry.translations[0].translation_id
    assert registry.interpretations[0].statement != registry.translations[0].text


@pytest.mark.parametrize(
    "passage",
    [
        {"passage_id": "x", "source_id": "s", "locator": "p"},
        {
            "passage_id": "x",
            "source_id": "s",
            "locator": "p",
            "content_sha256": "bad",
            "excerpt": "x",
        },
    ],
)
def test_source_passage_requires_valid_locator_content(passage: dict[str, str]) -> None:
    with pytest.raises(ValidationError):
        SourcePassage.model_validate(passage)


def test_source_registry_rejects_unresolved_links_and_naive_review_time() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        ReviewRecord(
            category=ReviewCategory.INTERPRETATION_REVIEW,
            status=ReviewStatus.REVIEWED,
            reviewer="r",
            reviewed_at=datetime(2026, 1, 1),
        )
    with pytest.raises(ValidationError, match="unknown source"):
        SourceRegistry(
            registry_version="v1",
            passages=(
                SourcePassage(
                    passage_id="p", source_id="missing", locator="x", passage_reference="x"
                ),
            ),
        )


def test_lifecycle_transitions_are_explicit_and_invalid_transitions_fail() -> None:
    assert can_transition(RuleLifecycle.APPROVED, RuleLifecycle.PRODUCTION_ACTIVE)
    assert not can_transition(RuleLifecycle.DRAFT, RuleLifecycle.PRODUCTION_ACTIVE)
    with pytest.raises(AdmissionError, match="invalid lifecycle transition"):
        from astrologer.knowledge.admission import require_transition

        require_transition(RuleLifecycle.DRAFT, RuleLifecycle.PRODUCTION_ACTIVE)


def test_production_admission_requires_active_reviewed_non_synthetic_rule() -> None:
    validator = AdmissionValidator()
    with pytest.raises(AdmissionError, match="production_active"):
        validator.validate_production_active(
            _envelope(lifecycle=RuleLifecycle.APPROVED), _registry(), _contract()
        )
    with pytest.raises(AdmissionError, match="synthetic/demo"):
        validator.validate_production_active(_envelope(synthetic=True), _registry(), _contract())
    with pytest.raises(AdmissionError, match="reviewed interpretation"):
        validator.validate_production_active(_envelope(), _registry(reviewed=False), _contract())


def test_admission_requires_declared_compatible_deterministic_facts() -> None:
    with pytest.raises(AdmissionError, match="unsupported fact dependency"):
        AdmissionValidator().validate_production_active(
            _envelope(fact_id="unknown.fact"), _registry(), _contract()
        )
    incompatible = _envelope().model_copy(update={"chart_scope": ChartScope.D1_RASHI})
    wrong_contract = _contract().model_copy(update={"contract_version": "2"})
    with pytest.raises(AdmissionError, match="does not match"):
        AdmissionValidator().validate_production_active(incompatible, _registry(), wrong_contract)


def test_envelope_requires_dependencies_and_never_adds_executable_clauses() -> None:
    no_dependencies = _envelope().model_dump()
    no_dependencies["fact_dependencies"] = ()
    with pytest.raises(ValidationError, match="explicit fact dependencies"):
        ProductionRuleEnvelope.model_validate(no_dependencies)
    with pytest.raises(ValidationError):
        ProductionRuleEnvelope.model_validate({**_envelope().model_dump(), "script": "run"})


def test_empty_production_manifest_is_reproducible_and_loads_no_rules() -> None:
    registry = EMPTY_SOURCE_REGISTRY
    contract = FactContract(
        contract_id="jyotish.d1.structural",
        contract_version="v1",
        chart_scope=ChartScope.D1_RASHI,
        methodology_id="jyotish-derived-facts-v1",
    )
    assert (
        EMPTY_PRODUCTION_MANIFEST.content_sha256()
        == "f2b95924b75cf9d5abb4d644cb035199de447d7b666d226ae8b2ba9036b072ff"
    )
    assert ProductionCorpusLoader().load(EMPTY_PRODUCTION_MANIFEST, (), registry, contract) == ()


def test_manifest_rejects_approved_but_not_active_rules_and_mismatched_membership() -> None:
    envelope = _envelope(lifecycle=RuleLifecycle.APPROVED)
    with pytest.raises(ProductionCorpusLoadError, match="unadmitted"):
        ProductionCorpusLoader().load(_manifest(envelope), (envelope,), _registry(), _contract())
    with pytest.raises(ProductionCorpusLoadError, match="membership"):
        ProductionCorpusLoader().load(_manifest(_envelope()), (), _registry(), _contract())


def test_manifest_rejects_non_active_demo_and_hash_tampering() -> None:
    demo = _envelope(synthetic=True)
    with pytest.raises(ProductionCorpusLoadError, match="synthetic/demo"):
        ProductionCorpusLoader().load(_manifest(demo), (demo,), _registry(), _contract())
    envelope = _envelope()
    tampered = _manifest(envelope).model_copy(
        update={
            "rules": (
                ManifestRule(
                    rule_id=envelope.rule.rule_id,
                    rule_version=envelope.rule.rule_version,
                    envelope_sha256="0" * 64,
                ),
            )
        }
    )
    with pytest.raises(ProductionCorpusLoadError, match="hash"):
        ProductionCorpusLoader().load(tampered, (envelope,), _registry(), _contract())


def test_loader_rejects_unsafe_mapping_and_returns_stable_independent_rules() -> None:
    envelope = _envelope()
    unsafe = envelope.model_dump(mode="json")
    unsafe["rule"]["script"] = "not executable"
    with pytest.raises(ProductionCorpusLoadError, match="executable"):
        ProductionCorpusLoader().load(_manifest(envelope), (unsafe,), _registry(), _contract())
    loaded = ProductionCorpusLoader().load(
        _manifest(envelope), (envelope,), _registry(), _contract()
    )
    assert loaded == (envelope.rule,)


def test_supporting_and_challenging_results_remain_independent_without_aggregation() -> None:
    supporting = _rule()
    challenging = supporting.model_copy(update={"rule_id": "SYNTHETIC_CHALLENGING"})
    facts = FactSet(facts=(Fact(fact_id="test.fact", value=True),))
    results = RuleEvaluator().evaluate_rules((challenging, supporting), facts)
    assert tuple(result.status for result in results) == (
        EvaluationStatus.TRUE,
        EvaluationStatus.TRUE,
    )
    assert len(results) == 2


def test_missing_facts_preserve_task08_unknown_semantics() -> None:
    result = RuleEvaluator().evaluate_rule(_rule(), FactSet())
    assert result.status is EvaluationStatus.UNKNOWN
