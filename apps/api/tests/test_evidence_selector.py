"""Task 13 deterministic, status-preserving evidence-selection tests."""

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
from astrologer.evidence import EvidenceBuilder, EvidenceSelector
from astrologer.evidence.models import EvidenceEvaluationSummary, EvidenceItem, EvidencePackage
from astrologer.evidence.selector import SELECTOR_VERSION
from astrologer.knowledge.evaluation import (
    FactEvaluationProvenance,
    GovernedRuleEvaluator,
    fact_set_sha256,
)
from astrologer.knowledge.models import EvidenceDirection, JyotishDomain, RulePosture
from astrologer.knowledge.production import (
    FACT_CONTRACT,
    FACT_ID,
    PRODUCTION_MANIFEST,
    RULE_ENVELOPE,
    SOURCE_REGISTRY,
)
from astrologer.questions import QuestionIntentRouter, QuestionRequest
from astrologer.rules.models import EvaluationStatus

_AS_OF = datetime(2026, 10, 2, 12, 0, tzinfo=UTC)
_BIRTH = BirthInput(
    birth_date=date(1990, 1, 15),
    birth_time=time(9, 30),
    timezone="Asia/Kolkata",
    latitude=19.076,
    longitude=72.8777,
)
_SELECTOR = EvidenceSelector()
_ROUTER = QuestionIntentRouter()


@pytest.fixture(scope="module")
def context() -> DeterministicAstrologyContext:
    return DeterministicAstrologyContextService(SwissEphemerisProvider()).build(
        DeterministicContextRequest(birth_input=_BIRTH, as_of=_AS_OF)
    )


def _package(context: DeterministicAstrologyContext, value: int | None = 9) -> EvidencePackage:
    facts = tuple(
        fact for fact in context.derived_facts.facts if fact.fact_id != FACT_ID or value is not None
    )
    if value is not None:
        facts = tuple(
            DerivedFact(fact_id=fact.fact_id, value=value) if fact.fact_id == FACT_ID else fact
            for fact in facts
        )
    adjusted = context.model_copy(
        update={
            "derived_facts": DerivedFactBundle(
                provenance=context.derived_facts.provenance, facts=facts
            )
        }
    )
    supplied = to_fact_set(adjusted.derived_facts)
    provenance = FactEvaluationProvenance.from_derived_fact_bundle(
        adjusted.derived_facts
    ).model_copy(update={"fact_set_sha256": fact_set_sha256(supplied)})
    result = GovernedRuleEvaluator().evaluate(
        PRODUCTION_MANIFEST,
        (RULE_ENVELOPE,),
        SOURCE_REGISTRY,
        FACT_CONTRACT,
        supplied,
        provenance,
    )
    return EvidenceBuilder().build(adjusted, PRODUCTION_MANIFEST, result)


def _intent(question: str):
    return _ROUTER.route(QuestionRequest(question=question)).intents[0]


def _synthetic_item(
    item: EvidenceItem,
    index: int,
    status: EvaluationStatus,
    direction: EvidenceDirection,
    domain: JyotishDomain,
    posture: RulePosture,
) -> EvidenceItem:
    rule_id = f"synthetic.rule.{index}"
    return item.model_copy(
        update={
            "evidence_item_id": f"{rule_id}@v1",
            "rule_id": rule_id,
            "rule_version": "v1",
            "evaluation_status": status,
            "evidence_direction": direction,
            "domain": domain,
            "posture": posture,
            "governance_provenance": item.governance_provenance.model_copy(
                update={
                    "rule_id": rule_id,
                    "rule_version": "v1",
                    "domain": domain,
                    "posture": posture,
                }
            ),
        }
    )


def _repackage(template: EvidencePackage, items: tuple[EvidenceItem, ...]) -> EvidencePackage:
    ordered = tuple(sorted(items, key=lambda item: (item.rule_id, item.rule_version)))
    matched = tuple(item for item in ordered if item.evaluation_status is EvaluationStatus.TRUE)
    unmatched = tuple(item for item in ordered if item.evaluation_status is EvaluationStatus.FALSE)
    unknown = tuple(item for item in ordered if item.evaluation_status is EvaluationStatus.UNKNOWN)
    summary = EvidenceEvaluationSummary(
        total_evaluations=len(ordered),
        matched_count=len(matched),
        unmatched_count=len(unmatched),
        unknown_count=len(unknown),
    )
    provisional = EvidencePackage.model_construct(
        context_identity=template.context_identity,
        corpus_release=template.corpus_release,
        manifest_content_sha256=template.manifest_content_sha256,
        matched_evidence=matched,
        unmatched_evaluations=unmatched,
        unknown_evaluations=unknown,
        evaluation_summary=summary,
        package_content_sha256="0" * 64,
    )
    return EvidencePackage(
        context_identity=template.context_identity,
        corpus_release=template.corpus_release,
        manifest_content_sha256=template.manifest_content_sha256,
        matched_evidence=matched,
        unmatched_evaluations=unmatched,
        unknown_evaluations=unknown,
        evaluation_summary=summary,
        package_content_sha256=provisional.content_sha256(),
    )


def test_exact_domain_true_false_unknown_and_mismatch_are_partitioned(
    context: DeterministicAstrologyContext,
) -> None:
    base = _package(context).matched_evidence[0]
    package = _repackage(
        _package(context),
        (
            _synthetic_item(
                base,
                3,
                EvaluationStatus.UNKNOWN,
                EvidenceDirection.CONTEXTUAL,
                JyotishDomain.CAREER,
                RulePosture.STATIC,
            ),
            _synthetic_item(
                base,
                2,
                EvaluationStatus.FALSE,
                EvidenceDirection.CHALLENGING,
                JyotishDomain.CAREER,
                RulePosture.STATIC,
            ),
            _synthetic_item(
                base,
                1,
                EvaluationStatus.TRUE,
                EvidenceDirection.SUPPORTING,
                JyotishDomain.CAREER,
                RulePosture.STATIC,
            ),
            _synthetic_item(
                base,
                4,
                EvaluationStatus.TRUE,
                EvidenceDirection.CONTEXTUAL,
                JyotishDomain.GENERAL,
                RulePosture.STATIC,
            ),
        ),
    )

    result = _SELECTOR.select(_intent("How is my career?"), package)

    assert [item.evaluation_status for item in result.selected_matched] == [EvaluationStatus.TRUE]
    assert [item.evaluation_status for item in result.relevant_unmatched] == [
        EvaluationStatus.FALSE
    ]
    assert [item.evaluation_status for item in result.relevant_unknown] == [
        EvaluationStatus.UNKNOWN
    ]
    assert result.selected_matched[0].evidence_direction is EvidenceDirection.SUPPORTING
    assert result.relevant_unmatched[0].evidence_direction is EvidenceDirection.CHALLENGING
    assert result.excluded[0].domain is JyotishDomain.GENERAL
    assert result.excluded[0].exclusion_reason.value == "domain_mismatch"


def test_all_matched_directions_are_preserved_without_ranking_or_resolution(
    context: DeterministicAstrologyContext,
) -> None:
    base = _package(context).matched_evidence[0]
    package = _repackage(
        _package(context),
        tuple(
            _synthetic_item(
                base,
                index,
                EvaluationStatus.TRUE,
                direction,
                JyotishDomain.CAREER,
                RulePosture.STATIC,
            )
            for index, direction in enumerate(
                (
                    EvidenceDirection.CHALLENGING,
                    EvidenceDirection.CONTEXTUAL,
                    EvidenceDirection.SUPPORTING,
                ),
                start=1,
            )
        ),
    )

    result = _SELECTOR.select(_intent("How is my career?"), package)

    assert [item.evidence_direction for item in result.selected_matched] == [
        EvidenceDirection.CHALLENGING,
        EvidenceDirection.CONTEXTUAL,
        EvidenceDirection.SUPPORTING,
    ]
    assert result.capability_summary.has_supporting_match is True
    assert result.capability_summary.has_challenging_match is True
    assert result.capability_summary.has_contextual_match is True


def test_current_rule_one_general_and_other_domain_behavior(
    context: DeterministicAstrologyContext,
) -> None:
    package = _package(context)

    general = _SELECTOR.select(_intent("How is my overall reading?"), package)
    career = _SELECTOR.select(_intent("How is my career?"), package)
    wealth = _SELECTOR.select(_intent("How is my wealth?"), package)

    assert general.selected_matched[0].domain is JyotishDomain.GENERAL
    assert general.selected_matched[0].evidence_direction is EvidenceDirection.CONTEXTUAL
    assert career.selected_matched == wealth.selected_matched == ()
    assert career.excluded[0].exclusion_reason.value == "domain_mismatch"
    assert wealth.excluded[0].exclusion_reason.value == "domain_mismatch"


def test_current_rule_one_timing_requests_preserve_static_evidence_without_answerability(
    context: DeterministicAstrologyContext,
) -> None:
    package = _package(context)

    property_result = _SELECTOR.select(_intent("When will I buy property?"), package)
    general_result = _SELECTOR.select(_intent("When will I have an overall reading?"), package)

    assert property_result.selected_matched == ()
    assert property_result.capability_summary.timing_requested is True
    assert property_result.capability_summary.timing_answerability_established is False
    assert general_result.selected_matched[0].posture is RulePosture.STATIC
    assert general_result.capability_summary.has_static_match is True
    assert general_result.capability_summary.timing_answerability_established is False


def test_timing_and_corroboration_postures_remain_unmet_requirements(
    context: DeterministicAstrologyContext,
) -> None:
    base = _package(context).matched_evidence[0]
    package = _repackage(
        _package(context),
        (
            _synthetic_item(
                base,
                1,
                EvaluationStatus.TRUE,
                EvidenceDirection.CONTEXTUAL,
                JyotishDomain.CAREER,
                RulePosture.TIMING_REQUIRED,
            ),
            _synthetic_item(
                base,
                2,
                EvaluationStatus.TRUE,
                EvidenceDirection.CONTEXTUAL,
                JyotishDomain.CAREER,
                RulePosture.CORROBORATION_REQUIRED,
            ),
        ),
    )

    result = _SELECTOR.select(_intent("When will I change my job?"), package)

    assert len(result.selected_matched) == 2
    assert result.capability_summary.has_timing_required_match is True
    assert result.capability_summary.has_corroboration_required_match is True
    assert result.capability_summary.corroboration_handling_deferred is True
    assert result.capability_summary.timing_answerability_established is False


def test_empty_eligible_selection_and_hash_provenance_are_deterministic(
    context: DeterministicAstrologyContext,
) -> None:
    package = _package(context)
    intent = _intent("How is my marriage?")

    first = _SELECTOR.select(intent, package)
    second = _SELECTOR.select(intent, package)

    assert first == second
    assert first.selected_matched == first.relevant_unmatched == first.relevant_unknown == ()
    assert first.selection_content_sha256 == first.content_sha256()
    assert first.evidence_package_content_sha256 == package.package_content_sha256
    assert first.manifest_id == package.corpus_release.manifest_id
    assert first.policy.policy_id == "exact-domain-selection"
    assert first.excluded[0].evidence_item_id == package.matched_evidence[0].evidence_item_id
    serialized = first.model_dump_json()
    assert SOURCE_REGISTRY.passages[0].passage_reference not in serialized
    assert SOURCE_REGISTRY.translations[0].text not in serialized
    assert SOURCE_REGISTRY.interpretations[0].statement not in serialized


def test_selector_has_no_calculator_evaluator_loader_source_or_llm_dependencies() -> None:
    source = getsource(EvidenceSelector)

    for prohibited in (
        "GovernedRuleEvaluator",
        "RuleEvaluator",
        "ProductionCorpusLoader",
        "LLM",
        "Dasha",
        "Transit",
        "ChartEngine",
        "SwissEphemeris",
        "score",
        "weight",
        "probability",
        "confidence",
        "source",
        "bphs",
    ):
        assert prohibited not in source
    assert SELECTOR_VERSION == "evidence-selector-v1"
