"""Synthetic tests for the Task 09C1 governed evaluation provenance bridge."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from astrologer.knowledge.corpus import (
    EMPTY_PRODUCTION_MANIFEST,
    ManifestRule,
    ProductionCorpusLoadError,
    ProductionCorpusManifest,
    envelope_sha256,
)
from astrologer.knowledge.evaluation import (
    FactEvaluationProvenance,
    GovernedEvaluationError,
    GovernedRuleEvaluator,
    fact_set_sha256,
)
from astrologer.knowledge.models import (
    ChartScope,
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


def _review(category: ReviewCategory, status: ReviewStatus = ReviewStatus.REVIEWED) -> ReviewRecord:
    return ReviewRecord(
        category=category,
        status=status,
        reviewer="synthetic-reviewer",
        reviewed_at=_REVIEWED_AT,
    )


def _condition() -> ConditionDefinition:
    return ConditionDefinition(
        kind=ConditionKind.LEAF,
        operation=ConditionOperation.EQUALS,
        fact_id="test.flag",
        expected_value=True,
    )


def _registry(*, translation_applicable: bool = True) -> SourceRegistry:
    source = SourceRecord(
        source_id="synthetic.source",
        source_version="v1",
        kind=SourceKind.PRIMARY,
        title="Synthetic source fixture",
        original_language="English",
        rights_status=RightsStatus.REFERENCE_ONLY,
    )
    passage = SourcePassage(
        passage_id="synthetic.passage",
        source_id=source.source_id,
        locator="fixture 1",
        passage_reference="synthetic reference only",
        review=_review(ReviewCategory.SOURCE_VERIFICATION),
    )
    translation = TranslationRecord(
        translation_id="synthetic.translation",
        translation_version="v1",
        passage_id=passage.passage_id,
        language="English",
        text="Synthetic translation only.",
        review=_review(ReviewCategory.TRANSLATION_VERIFICATION),
    )
    interpretation = ReviewedInterpretation(
        interpretation_id="synthetic.interpretation",
        interpretation_version="v1",
        passage_id=passage.passage_id,
        translation_id=translation.translation_id if translation_applicable else None,
        translation_applicability=(
            TranslationApplicability.REQUIRED
            if translation_applicable
            else TranslationApplicability.NOT_APPLICABLE
        ),
        statement="Synthetic reviewed interpretation, not Jyotish doctrine.",
        review=_review(ReviewCategory.INTERPRETATION_REVIEW),
    )
    return SourceRegistry(
        registry_version="synthetic-registry-v1",
        sources=(source,),
        passages=(passage,),
        translations=(translation,) if translation_applicable else (),
        interpretations=(interpretation,),
    )


def _contract() -> FactContract:
    return FactContract(
        contract_id="synthetic.contract",
        contract_version="v1",
        chart_scope=ChartScope.D1_RASHI,
        methodology_id="synthetic-facts-v1",
        available_fact_ids=("test.flag",),
    )


def _envelope(*, rule_id: str = "SYNTHETIC_RULE") -> ProductionRuleEnvelope:
    rule = RuleDefinition(
        rule_id=rule_id,
        rule_version="v1",
        ruleset_version="synthetic-rules-v1",
        name="Synthetic governed rule",
        domain="test",
        condition=_condition(),
        effect=RuleEffect(effect_key="test.effect", label="Synthetic effect"),
    )
    return ProductionRuleEnvelope(
        rule=rule,
        lifecycle=RuleLifecycle.PRODUCTION_ACTIVE,
        domain=JyotishDomain.GENERAL,
        taxonomy=RuleTaxonomy.NATAL_STRUCTURAL,
        posture=RulePosture.STATIC,
        evidence_direction=EvidenceDirection.CONTEXTUAL,
        chart_scope=ChartScope.D1_RASHI,
        fact_contract_id="synthetic.contract",
        fact_contract_version="v1",
        fact_contract_methodology_id="synthetic-facts-v1",
        fact_dependencies=(FactDependency(fact_id="test.flag"),),
        interpretation_id="synthetic.interpretation",
        formalization_review=_review(ReviewCategory.FORMALIZATION_REVIEW),
    )


def _manifest(envelopes: tuple[ProductionRuleEnvelope, ...]) -> ProductionCorpusManifest:
    return ProductionCorpusManifest(
        manifest_id="synthetic.manifest",
        manifest_version="v1",
        registry_version="synthetic-registry-v1",
        fact_contract_id="synthetic.contract",
        fact_contract_version="v1",
        rules=tuple(
            ManifestRule(
                rule_id=envelope.rule.rule_id,
                rule_version=envelope.rule.rule_version,
                envelope_sha256=envelope_sha256(envelope),
            )
            for envelope in envelopes
        ),
    )


def _fact_provenance(facts: FactSet) -> FactEvaluationProvenance:
    return FactEvaluationProvenance(
        methodology_id="synthetic-facts-v1",
        source_register_version="synthetic-fact-register-v1",
        derived_fact_provenance_sha256="a" * 64,
        fact_set_sha256=fact_set_sha256(facts),
    )


@pytest.mark.parametrize(
    ("facts", "expected"),
    [
        (FactSet(facts=(Fact(fact_id="test.flag", value=True),)), EvaluationStatus.TRUE),
        (FactSet(facts=(Fact(fact_id="test.flag", value=False),)), EvaluationStatus.FALSE),
        (FactSet(), EvaluationStatus.UNKNOWN),
    ],
)
def test_governed_evaluation_preserves_task08_status_and_trace(
    facts: FactSet, expected: EvaluationStatus
) -> None:
    envelope = _envelope()
    result = GovernedRuleEvaluator().evaluate(
        _manifest((envelope,)),
        (envelope,),
        _registry(),
        _contract(),
        facts,
        _fact_provenance(facts),
    )[0]

    assert result.evaluation.status is expected
    assert result.evaluation.condition == result.evaluation.condition
    assert result.evaluation.referenced_fact_ids == ("test.flag",)
    assert result.evaluation.resolved_fact_ids == (("test.flag",) if facts.facts else ())
    assert result.evidence_direction is EvidenceDirection.CONTEXTUAL


def test_governed_result_resolves_compact_provenance_without_source_text() -> None:
    envelope = _envelope()
    facts = FactSet(facts=(Fact(fact_id="test.flag", value=True),))
    result = GovernedRuleEvaluator().evaluate(
        _manifest((envelope,)),
        (envelope,),
        _registry(),
        _contract(),
        facts,
        _fact_provenance(facts),
    )[0]

    provenance = result.governance_provenance
    assert (provenance.rule_id, provenance.rule_version) == ("SYNTHETIC_RULE", "v1")
    assert provenance.source_id == "synthetic.source"
    assert provenance.source_version == "v1"
    assert provenance.passage_id == "synthetic.passage"
    assert (provenance.translation_id, provenance.translation_version) == (
        "synthetic.translation",
        "v1",
    )
    assert (provenance.interpretation_id, provenance.interpretation_version) == (
        "synthetic.interpretation",
        "v1",
    )
    assert provenance.envelope_sha256 == envelope_sha256(envelope)
    assert provenance.manifest_content_sha256 == _manifest((envelope,)).content_sha256()
    assert "Synthetic translation" not in result.model_dump_json()
    assert "Synthetic reviewed interpretation" not in result.model_dump_json()


def test_translation_not_applicable_requires_no_fake_translation() -> None:
    envelope = _envelope()
    facts = FactSet(facts=(Fact(fact_id="test.flag", value=True),))
    result = GovernedRuleEvaluator().evaluate(
        _manifest((envelope,)),
        (envelope,),
        _registry(translation_applicable=False),
        _contract(),
        facts,
        _fact_provenance(facts),
    )[0]

    assert result.governance_provenance.translation_id is None
    assert result.governance_provenance.translation_version is None


def test_result_order_and_hashes_are_deterministic() -> None:
    first = _envelope(rule_id="SYNTHETIC_A")
    second = _envelope(rule_id="SYNTHETIC_B")
    facts = FactSet(facts=(Fact(fact_id="test.flag", value=True),))
    manifest = _manifest((first, second))
    results = GovernedRuleEvaluator().evaluate(
        manifest, (second, first), _registry(), _contract(), facts, _fact_provenance(facts)
    )

    assert tuple(result.evaluation.rule_id for result in results) == ("SYNTHETIC_A", "SYNTHETIC_B")
    assert envelope_sha256(first) == envelope_sha256(first)
    assert manifest.content_sha256() == manifest.content_sha256()
    assert fact_set_sha256(facts) == fact_set_sha256(facts)


def test_bridge_rejects_mismatched_fact_provenance_and_unadmitted_inputs() -> None:
    envelope = _envelope()
    facts = FactSet(facts=(Fact(fact_id="test.flag", value=True),))
    bad_provenance = _fact_provenance(facts).model_copy(update={"fact_set_sha256": "0" * 64})
    with pytest.raises(GovernedEvaluationError, match="does not match"):
        GovernedRuleEvaluator().evaluate(
            _manifest((envelope,)),
            (envelope,),
            _registry(),
            _contract(),
            facts,
            bad_provenance,
        )
    with pytest.raises(ProductionCorpusLoadError, match="hash"):
        bad_manifest = _manifest((envelope,)).model_copy(
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
        GovernedRuleEvaluator().evaluate(
            bad_manifest, (envelope,), _registry(), _contract(), facts, _fact_provenance(facts)
        )
    tampered_envelope = envelope.model_copy(
        update={"evidence_direction": EvidenceDirection.SUPPORTING}
    )
    with pytest.raises(ProductionCorpusLoadError, match="hash"):
        GovernedRuleEvaluator().evaluate(
            _manifest((envelope,)),
            (tampered_envelope,),
            _registry(),
            _contract(),
            facts,
            _fact_provenance(facts),
        )
    with pytest.raises(ProductionCorpusLoadError, match="fact contract"):
        GovernedRuleEvaluator().evaluate(
            _manifest((envelope,)),
            (envelope,),
            _registry(),
            _contract().model_copy(update={"contract_version": "v2"}),
            facts,
            _fact_provenance(facts),
        )


@pytest.mark.parametrize(
    ("field", "review"),
    [
        ("passage", _review(ReviewCategory.INTERPRETATION_REVIEW)),
        ("formalization", _review(ReviewCategory.SOURCE_VERIFICATION)),
    ],
)
def test_wrong_source_or_formalization_review_category_is_rejected(
    field: str, review: ReviewRecord
) -> None:
    envelope = _envelope()
    registry = _registry()
    if field == "passage":
        passage = registry.passages[0].model_copy(update={"review": review})
        registry = registry.model_copy(update={"passages": (passage,)})
    else:
        envelope = envelope.model_copy(update={"formalization_review": review})
    facts = FactSet(facts=(Fact(fact_id="test.flag", value=True),))
    with pytest.raises(ProductionCorpusLoadError, match="wrong review category"):
        GovernedRuleEvaluator().evaluate(
            _manifest((envelope,)),
            (envelope,),
            registry,
            _contract(),
            facts,
            _fact_provenance(facts),
        )


def test_missing_required_reviews_and_wrong_translation_interpretation_categories_fail() -> None:
    with pytest.raises(ValidationError, match="translation review category"):
        TranslationRecord(
            translation_id="bad.translation",
            translation_version="v1",
            passage_id="synthetic.passage",
            language="English",
            text="Synthetic.",
            review=_review(ReviewCategory.INTERPRETATION_REVIEW),
        )
    with pytest.raises(ValidationError, match="interpretation review category"):
        ReviewedInterpretation(
            interpretation_id="bad.interpretation",
            interpretation_version="v1",
            passage_id="synthetic.passage",
            translation_applicability=TranslationApplicability.NOT_APPLICABLE,
            statement="Synthetic.",
            review=_review(ReviewCategory.TRANSLATION_VERIFICATION),
        )
    envelope = _envelope().model_copy(update={"formalization_review": None})
    facts = FactSet(facts=(Fact(fact_id="test.flag", value=True),))
    with pytest.raises(ProductionCorpusLoadError, match="reviewed formalization"):
        GovernedRuleEvaluator().evaluate(
            _manifest((envelope,)),
            (envelope,),
            _registry(),
            _contract(),
            facts,
            _fact_provenance(facts),
        )
    registry = _registry()
    passage = registry.passages[0].model_copy(update={"review": None})
    with pytest.raises(ProductionCorpusLoadError, match="verified source passage"):
        GovernedRuleEvaluator().evaluate(
            _manifest((_envelope(),)),
            (_envelope(),),
            registry.model_copy(update={"passages": (passage,)}),
            _contract(),
            facts,
            _fact_provenance(facts),
        )


def test_empty_historical_manifest_remains_unchanged_and_evaluates_nothing() -> None:
    facts = FactSet()
    provenance = FactEvaluationProvenance(
        methodology_id="jyotish-derived-facts-v1",
        source_register_version="task09a-v1-approved-conventions",
        derived_fact_provenance_sha256="b" * 64,
        fact_set_sha256=fact_set_sha256(facts),
    )
    registry = SourceRegistry(registry_version="jyotish-source-registry-v1")
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
    assert (
        GovernedRuleEvaluator().evaluate(
            EMPTY_PRODUCTION_MANIFEST, (), registry, contract, facts, provenance
        )
        == ()
    )
