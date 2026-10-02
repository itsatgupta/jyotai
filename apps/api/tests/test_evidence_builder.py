"""Task 11 governed deterministic evidence-package tests."""

from datetime import UTC, date, datetime, time
from inspect import getsource

import pytest

from astrologer.application.context import (
    DeterministicAstrologyContext,
    DeterministicAstrologyContextService,
    DeterministicContextRequest,
)
from astrologer.astrology.derived_facts import DerivedFact, DerivedFactBundle, to_fact_set
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.birth.models import BirthInput
from astrologer.evidence import EvidenceBuilder, EvidenceBuildError
from astrologer.knowledge.corpus import (
    EMPTY_PRODUCTION_MANIFEST,
    ManifestRule,
    ProductionCorpusManifest,
)
from astrologer.knowledge.evaluation import (
    FactEvaluationProvenance,
    GovernedEvaluationResult,
    GovernedRuleEvaluator,
    fact_set_sha256,
)
from astrologer.knowledge.models import EvidenceDirection
from astrologer.knowledge.production import (
    FACT_CONTRACT,
    FACT_ID,
    PRODUCTION_MANIFEST,
    RULE_ENVELOPE,
    SOURCE_REGISTRY,
)
from astrologer.rules.models import EvaluationStatus, FactSet

_AS_OF = datetime(2026, 10, 2, 12, 0, tzinfo=UTC)
_BIRTH = BirthInput(
    birth_date=date(1990, 1, 15),
    birth_time=time(9, 30),
    timezone="Asia/Kolkata",
    latitude=19.076,
    longitude=72.8777,
)


@pytest.fixture(scope="module")
def context() -> DeterministicAstrologyContext:
    return DeterministicAstrologyContextService(SwissEphemerisProvider()).build(
        DeterministicContextRequest(birth_input=_BIRTH, as_of=_AS_OF)
    )


def _context_with_fact(
    context: DeterministicAstrologyContext, value: int | None
) -> DeterministicAstrologyContext:
    facts = tuple(
        fact for fact in context.derived_facts.facts if fact.fact_id != FACT_ID or value is not None
    )
    if value is not None:
        facts = tuple(
            DerivedFact(fact_id=fact.fact_id, value=value) if fact.fact_id == FACT_ID else fact
            for fact in facts
        )
    bundle = DerivedFactBundle(provenance=context.derived_facts.provenance, facts=facts)
    return context.model_copy(update={"derived_facts": bundle})


def _production_result(context: DeterministicAstrologyContext, facts: FactSet | None = None):
    supplied = facts or to_fact_set(context.derived_facts)
    provenance = FactEvaluationProvenance.from_derived_fact_bundle(
        context.derived_facts
    ).model_copy(update={"fact_set_sha256": fact_set_sha256(supplied)})
    return GovernedRuleEvaluator().evaluate(
        PRODUCTION_MANIFEST,
        (RULE_ENVELOPE,),
        SOURCE_REGISTRY,
        FACT_CONTRACT,
        supplied,
        provenance,
    )[0]


def _synthetic_release(
    result: GovernedEvaluationResult, directions: tuple[EvidenceDirection, ...]
) -> tuple[ProductionCorpusManifest, tuple[GovernedEvaluationResult, ...]]:
    rules = tuple(
        ManifestRule(
            rule_id=f"SYNTHETIC_{index}",
            rule_version="v1",
            envelope_sha256=f"{index + 1:064x}",
        )
        for index in range(len(directions))
    )
    manifest = ProductionCorpusManifest(
        manifest_id="synthetic.evidence",
        manifest_version="v1",
        registry_version=SOURCE_REGISTRY.registry_version,
        fact_contract_id=FACT_CONTRACT.contract_id,
        fact_contract_version=FACT_CONTRACT.contract_version,
        rules=rules,
    )
    synthetic = []
    for index, (member, direction) in enumerate(zip(rules, directions, strict=True)):
        evaluation = result.evaluation.model_copy(
            update={
                "rule_id": member.rule_id,
                "rule_version": member.rule_version,
                "effect": result.evaluation.effect.model_copy(
                    update={"effect_key": f"synthetic.effect.{index}"}
                ),
            }
        )
        governance = result.governance_provenance.model_copy(
            update={
                "rule_id": member.rule_id,
                "rule_version": member.rule_version,
                "envelope_sha256": member.envelope_sha256,
                "manifest_id": manifest.manifest_id,
                "manifest_version": manifest.manifest_version,
                "manifest_content_sha256": manifest.content_sha256(),
            }
        )
        synthetic.append(
            result.model_copy(
                update={
                    "evaluation": evaluation,
                    "evidence_direction": direction,
                    "governance_provenance": governance,
                }
            )
        )
    return manifest, tuple(reversed(synthetic))


def test_true_supporting_challenging_and_contextual_are_preserved(
    context: DeterministicAstrologyContext,
) -> None:
    true_context = _context_with_fact(context, 9)
    result = _production_result(true_context)
    manifest, results = _synthetic_release(
        result,
        (
            EvidenceDirection.SUPPORTING,
            EvidenceDirection.CHALLENGING,
            EvidenceDirection.CONTEXTUAL,
        ),
    )

    package = EvidenceBuilder().build(true_context, manifest, results)

    assert [item.rule_id for item in package.matched_evidence] == [
        "SYNTHETIC_0",
        "SYNTHETIC_1",
        "SYNTHETIC_2",
    ]
    assert [item.evidence_direction for item in package.matched_evidence] == [
        EvidenceDirection.SUPPORTING,
        EvidenceDirection.CHALLENGING,
        EvidenceDirection.CONTEXTUAL,
    ]
    assert package.unmatched_evaluations == ()
    assert package.unknown_evaluations == ()


def test_false_is_unmatched_not_opposite_evidence(context: DeterministicAstrologyContext) -> None:
    false_context = _context_with_fact(context, 8)
    package = EvidenceBuilder().build(
        false_context, PRODUCTION_MANIFEST, (_production_result(false_context),)
    )

    assert package.matched_evidence == ()
    assert package.unknown_evaluations == ()
    assert package.unmatched_evaluations[0].evaluation_status is EvaluationStatus.FALSE
    assert package.unmatched_evaluations[0].evidence_direction is EvidenceDirection.CONTEXTUAL


def test_unknown_remains_unresolved_even_when_context_has_the_fact(
    context: DeterministicAstrologyContext,
) -> None:
    result = _production_result(context, FactSet())
    package = EvidenceBuilder().build(context, PRODUCTION_MANIFEST, (result,))

    assert package.matched_evidence == ()
    assert package.unmatched_evaluations == ()
    item = package.unknown_evaluations[0]
    assert item.evaluation_status is EvaluationStatus.UNKNOWN
    assert item.resolved_facts == ()
    assert item.unresolved_fact_ids == (FACT_ID,)
    assert FACT_ID in {fact.fact_id for fact in context.derived_facts.facts}


def test_current_rule_one_true_false_and_unknown_behavior(
    context: DeterministicAstrologyContext,
) -> None:
    true_context = _context_with_fact(context, 10)
    false_context = _context_with_fact(context, 8)
    unknown_context = _context_with_fact(context, None)
    true = EvidenceBuilder().build(
        true_context, PRODUCTION_MANIFEST, (_production_result(true_context),)
    )
    false = EvidenceBuilder().build(
        false_context, PRODUCTION_MANIFEST, (_production_result(false_context),)
    )
    unknown = EvidenceBuilder().build(
        unknown_context,
        PRODUCTION_MANIFEST,
        (_production_result(unknown_context, FactSet()),),
    )

    assert len(true.matched_evidence) == 1
    assert true.matched_evidence[0].evidence_direction is EvidenceDirection.CONTEXTUAL
    assert len(false.unmatched_evaluations) == 1
    assert len(unknown.unknown_evaluations) == 1


def test_empty_manifest_is_valid_and_reproducible(context: DeterministicAstrologyContext) -> None:
    first = EvidenceBuilder().build(context, EMPTY_PRODUCTION_MANIFEST, ())
    second = EvidenceBuilder().build(context, EMPTY_PRODUCTION_MANIFEST, ())

    assert first == second
    assert first.matched_evidence == ()
    assert first.unmatched_evaluations == ()
    assert first.unknown_evaluations == ()
    assert first.evaluation_summary.total_evaluations == 0
    assert first.manifest_content_sha256 == EMPTY_PRODUCTION_MANIFEST.content_sha256()


def test_hashes_and_provenance_are_deterministic_and_compact(
    context: DeterministicAstrologyContext,
) -> None:
    true_context = _context_with_fact(context, 9)
    result = _production_result(true_context)
    first = EvidenceBuilder().build(true_context, PRODUCTION_MANIFEST, (result,))
    second = EvidenceBuilder().build(true_context, PRODUCTION_MANIFEST, (result,))
    item = first.matched_evidence[0]
    serialized = first.model_dump_json()

    assert first == second
    assert first.package_content_sha256 == first.content_sha256()
    assert item.governance_provenance == result.governance_provenance
    assert item.fact_provenance == result.fact_provenance
    assert first.context_identity.context_provenance == true_context.provenance
    assert SOURCE_REGISTRY.passages[0].passage_reference not in serialized
    assert SOURCE_REGISTRY.translations[0].text not in serialized
    assert SOURCE_REGISTRY.interpretations[0].statement not in serialized


@pytest.mark.parametrize("mutation", ["missing", "extra", "duplicate", "envelope", "manifest"])
def test_manifest_compatibility_rejections(
    context: DeterministicAstrologyContext, mutation: str
) -> None:
    result = _production_result(_context_with_fact(context, 9))
    if mutation == "missing":
        results: tuple[GovernedEvaluationResult, ...] = ()
    elif mutation == "extra":
        extra_manifest, extra_results = _synthetic_release(result, (EvidenceDirection.CONTEXTUAL,))
        results = extra_results
        with pytest.raises(EvidenceBuildError, match="membership"):
            EvidenceBuilder().build(context, PRODUCTION_MANIFEST, results)
        return
    elif mutation == "duplicate":
        results = (result, result)
    elif mutation == "envelope":
        results = (
            result.model_copy(
                update={
                    "governance_provenance": result.governance_provenance.model_copy(
                        update={"envelope_sha256": "0" * 64}
                    )
                }
            ),
        )
    else:
        results = (
            result.model_copy(
                update={
                    "governance_provenance": result.governance_provenance.model_copy(
                        update={"manifest_id": "wrong.manifest"}
                    )
                }
            ),
        )
    with pytest.raises(EvidenceBuildError):
        EvidenceBuilder().build(context, PRODUCTION_MANIFEST, results)


def test_builder_has_no_evaluator_llm_or_interpretation_dependencies() -> None:
    source = getsource(EvidenceBuilder)

    assert "GovernedRuleEvaluator" not in source
    assert "RuleEvaluator" not in source
    assert "LLM" not in source
    assert "Dasha" not in source
    assert "Transit" not in source
    assert "d9" not in source.lower()
    assert "d10" not in source.lower()
    assert "score" not in source.lower()
    assert "probability" not in source.lower()
    assert "confidence" not in source.lower()
