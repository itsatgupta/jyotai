"""Synthetic coverage for governed evidence and constrained composition."""

import json

import pytest

from astrologer.composition import (
    AnswerComposer,
    AnswerCompositionError,
    CompositionProviderResponse,
    DeterministicAnswerComposer,
)
from astrologer.evidence import (
    EvidenceSelectionResult,
    InterpretationEvidenceBuilder,
    InterpretationEvidenceBuildError,
)
from astrologer.evidence.models import EvidenceItem, ResolvedEvidenceFact
from astrologer.evidence.selection_models import (
    EXACT_DOMAIN_SELECTION_POLICY_V1,
    SelectionCapabilitySummary,
)
from astrologer.knowledge.business_pack_v1 import (
    ACTIVE_PRODUCTION_RELEASE,
)
from astrologer.knowledge.education_pack_v1 import (
    TENTH_LORD_FACT_ID as FACT_ID,
)
from astrologer.knowledge.evaluation import (
    FactEvaluationProvenance,
    GovernedRuleEvaluator,
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

_BUILDER = InterpretationEvidenceBuilder()
_GENERAL_FACT_ID = "jyotish.d1.house_lord.11.placement_house"


def _governed_items(facts: FactSet) -> tuple[EvidenceItem, ...]:
    provenance = FactEvaluationProvenance(
        methodology_id=ACTIVE_PRODUCTION_RELEASE.fact_contract.methodology_id,
        source_register_version=ACTIVE_PRODUCTION_RELEASE.registry.registry_version,
        derived_fact_provenance_sha256="0" * 64,
        fact_set_sha256=fact_set_sha256(facts),
    )
    results = GovernedRuleEvaluator().evaluate(
        ACTIVE_PRODUCTION_RELEASE.manifest,
        ACTIVE_PRODUCTION_RELEASE.envelopes,
        ACTIVE_PRODUCTION_RELEASE.registry,
        ACTIVE_PRODUCTION_RELEASE.fact_contract,
        facts,
        provenance,
    )
    values = facts.by_id()
    return tuple(
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
        for result in results
    )


def _selection(domain: QuestionDomain, items: tuple[EvidenceItem, ...], *, timing: bool = False):
    relevant = tuple(item for item in items if item.domain.value == domain.value)
    matched = tuple(item for item in relevant if item.evaluation_status is EvaluationStatus.TRUE)
    unmatched = tuple(item for item in relevant if item.evaluation_status is EvaluationStatus.FALSE)
    unknown = tuple(item for item in relevant if item.evaluation_status is EvaluationStatus.UNKNOWN)
    intent = QuestionIntent(
        intent_id="intent-1",
        domain=domain,
        shape=QuestionShape.TIMING if timing else QuestionShape.DESCRIPTIVE,
        temporal_intent=TemporalIntent.TIME_BOUND if timing else TemporalIntent.CURRENT,
        requires_timing=timing,
    )
    capability = SelectionCapabilitySummary(
        has_matched_evidence=bool(matched),
        has_supporting_match=False,
        has_challenging_match=False,
        has_contextual_match=bool(matched),
        timing_requested=timing,
        has_static_match=bool(matched),
        has_timing_required_match=False,
        has_corroboration_required_match=False,
        timing_answerability_established=False,
        corroboration_handling_deferred=False,
    )
    fields = dict(
        policy=EXACT_DOMAIN_SELECTION_POLICY_V1,
        question_intent=intent,
        evidence_package_content_sha256="1" * 64,
        manifest_id=ACTIVE_PRODUCTION_RELEASE.manifest.manifest_id,
        manifest_version=ACTIVE_PRODUCTION_RELEASE.manifest.manifest_version,
        manifest_content_sha256=ACTIVE_PRODUCTION_RELEASE.manifest.content_sha256(),
        selected_matched=matched,
        relevant_unmatched=unmatched,
        relevant_unknown=unknown,
        excluded=(),
        capability_summary=capability,
    )
    provisional = EvidenceSelectionResult.model_construct(
        **fields, selection_content_sha256="0" * 64
    )
    return EvidenceSelectionResult(**fields, selection_content_sha256=provisional.content_sha256())


def test_career_match_admits_only_selected_career_rules_and_preserves_provenance() -> None:
    items = _governed_items(
        FactSet(facts=(Fact(fact_id=FACT_ID, value=4), Fact(fact_id=_GENERAL_FACT_ID, value=9)))
    )

    contract = _BUILDER.build(_selection(QuestionDomain.CAREER, items))

    assert contract.selected_matched
    assert all(item.domain is JyotishDomain.CAREER for item in contract.selected_matched)
    item = contract.selected_matched[0]
    assert item.rule_id == "bphs.d1.house_lord.10.in_4_or_10.v1"
    assert item.governance_provenance.passage_id
    assert item.governance_provenance.manifest_id == "jyotish.production.cumulative"
    assert item.governance_provenance.manifest_version == "v6"
    assert item.governance_provenance.interpretation_version == "v2"
    assert item.resolved_fact_ids == (FACT_ID,)


def test_exact_domain_isolation_excludes_general_from_career_and_career_from_general() -> None:
    items = _governed_items(
        FactSet(facts=(Fact(fact_id=FACT_ID, value=4), Fact(fact_id=_GENERAL_FACT_ID, value=9)))
    )

    career = _BUILDER.build(_selection(QuestionDomain.CAREER, items))
    general = _BUILDER.build(_selection(QuestionDomain.GENERAL, items))

    assert all(
        item.domain is JyotishDomain.CAREER
        for item in career.selected_matched + career.relevant_unmatched
    )
    assert all(item.domain is JyotishDomain.GENERAL for item in general.selected_matched)
    assert not any(item.domain is JyotishDomain.CAREER for item in general.selected_matched)


def test_unknown_and_false_are_explicitly_distinct() -> None:
    unknown = _BUILDER.build(_selection(QuestionDomain.CAREER, _governed_items(FactSet())))
    false = _BUILDER.build(
        _selection(
            QuestionDomain.CAREER,
            _governed_items(FactSet(facts=(Fact(fact_id=FACT_ID, value=1),))),
        )
    )

    assert unknown.selected_matched == () and unknown.relevant_unmatched == ()
    assert all(
        item.evaluation_status is EvaluationStatus.UNKNOWN for item in unknown.relevant_unknown
    )
    assert all(item.unresolved_fact_ids == (FACT_ID,) for item in unknown.relevant_unknown)
    assert false.selected_matched == () and false.relevant_unknown == ()
    assert all(
        item.evaluation_status is EvaluationStatus.FALSE for item in false.relevant_unmatched
    )
    assert all(item.resolved_fact_ids == (FACT_ID,) for item in false.relevant_unmatched)


def test_time_bound_career_context_does_not_admit_timing_fields_or_answerability() -> None:
    items = _governed_items(FactSet(facts=(Fact(fact_id=FACT_ID, value=4),)))

    contract = _BUILDER.build(_selection(QuestionDomain.CAREER, items, timing=True))
    serialized = contract.model_dump(mode="json")

    assert contract.selected_matched
    assert contract.intent.timing_requested is True
    assert contract.timing_answerability_established is False
    assert "time_range" not in serialized
    assert "date" not in str(serialized) and "period" not in str(serialized)


@pytest.mark.parametrize("candidate_id", ["career-candidate-01", "career-candidate-05"])
def test_repeated_construction_is_equal_and_non_admitted_candidates_are_rejected(
    candidate_id: str,
) -> None:
    items = _governed_items(FactSet(facts=(Fact(fact_id=FACT_ID, value=4),)))
    selection = _selection(QuestionDomain.CAREER, items)

    assert _BUILDER.build(selection) == _BUILDER.build(selection)
    candidate = selection.selected_matched[0].model_copy(
        update={
            "rule_id": candidate_id,
            "rule_version": "v1",
            "governance_provenance": selection.selected_matched[0].governance_provenance.model_copy(
                update={"rule_id": candidate_id, "rule_version": "v1"}
            ),
        }
    )
    rejected = _selection(QuestionDomain.CAREER, (candidate,))
    with pytest.raises(InterpretationEvidenceBuildError, match="not admitted"):
        _BUILDER.build(rejected)


class _FakeTransport:
    def __init__(self, output_json: str) -> None:
        self.output_json = output_json
        self.requests = []

    def complete(self, request):  # type: ignore[no-untyped-def]
        self.requests.append(request)
        return CompositionProviderResponse(
            output_json=self.output_json,
            provider_id="test-provider",
            model_id="test-model",
        )


def test_composer_sends_only_governed_wording_and_safe_projection() -> None:
    items = _governed_items(FactSet(facts=(Fact(fact_id=FACT_ID, value=4),)))
    evidence = _BUILDER.build(_selection(QuestionDomain.CAREER, items))
    transport = _FakeTransport(
        '{"answer":"The reviewed contextual natal evidence is limited to its stated scope.",'
        '"timing_answered":false}'
    )

    answer = AnswerComposer(transport).compose("How is my career?", evidence)

    payload = transport.requests[0].user_payload_json
    assert answer.provider_id == "test-provider"
    assert evidence.selected_matched[0].reviewed_statement in payload
    assert '"resolved_fact_ids"' not in payload
    assert '"fact_provenance"' not in payload
    assert '"context_identity"' not in payload
    assert "birth_date" not in payload
    assert "referenced_evidence_item_ids" not in payload
    assert "Do not return evidence IDs" in transport.requests[0].system_instructions
    assert "application, not you, attaches deterministic supporting evidence IDs" in (
        transport.requests[0].system_instructions
    )
    assert answer.referenced_evidence_item_ids == tuple(
        item.evidence_item_id for item in evidence.selected_matched
    )
    assert answer.corpus_limitation is False


def test_composer_returns_deterministic_limit_without_calling_provider() -> None:
    items = _governed_items(FactSet(facts=(Fact(fact_id=FACT_ID, value=1),)))
    evidence = _BUILDER.build(_selection(QuestionDomain.CAREER, items, timing=True))
    transport = _FakeTransport("not used")

    answer = AnswerComposer(transport).compose("When will my career improve?", evidence)

    assert transport.requests == []
    assert answer.corpus_limitation is True
    assert "current governed corpus does not establish" in answer.answer
    assert "Timing is not established" in answer.answer


def test_wealth_corpus_limit_does_not_call_provider_when_no_wealth_rules_match() -> None:
    items = _governed_items(
        FactSet(
            facts=(
                Fact(fact_id=_GENERAL_FACT_ID, value=3),
                Fact(fact_id="jyotish.d1.house_lord.5.placement_house", value=3),
            )
        )
    )
    evidence = _BUILDER.build(_selection(QuestionDomain.WEALTH, items))
    transport = _FakeTransport("not used")

    answer = AnswerComposer(transport).compose("How is my wealth?", evidence)

    assert transport.requests == []
    assert answer.corpus_limitation is True


def test_disabled_composer_uses_only_selected_reviewed_wording() -> None:
    items = _governed_items(FactSet(facts=(Fact(fact_id=FACT_ID, value=4),)))
    evidence = _BUILDER.build(_selection(QuestionDomain.CAREER, items))

    answer = DeterministicAnswerComposer().compose("How is my career?", evidence)

    assert answer.answer == " ".join(item.reviewed_statement for item in evidence.selected_matched)
    assert answer.referenced_evidence_item_ids == tuple(
        item.evidence_item_id for item in evidence.selected_matched
    )
    assert answer.corpus_limitation is False


@pytest.mark.parametrize("placement_house", [4, 5, 6, 9])
def test_disabled_career_answers_use_plain_reviewed_wording_without_internal_phrases(
    placement_house: int,
) -> None:
    items = _governed_items(FactSet(facts=(Fact(fact_id=FACT_ID, value=placement_house),)))
    evidence = _BUILDER.build(_selection(QuestionDomain.CAREER, items))

    answer = DeterministicAnswerComposer().compose("How is my career?", evidence)

    assert answer.answer == " ".join(item.reviewed_statement for item in evidence.selected_matched)
    assert answer.corpus_limitation is False
    for phrase in (
        "selected edition",
        "adjacent Hindi rendering",
        "compound outcome cluster",
        "reviewed source passage",
        "probability",
        "career success",
    ):
        assert phrase not in answer.answer
    assert "will " not in answer.answer
    assert "do not by themselves establish a profession, promotion, income, or timing." in (
        answer.answer
    )


def test_disabled_composer_keeps_unknown_unresolved_in_corpus_limit_answer() -> None:
    evidence = _BUILDER.build(_selection(QuestionDomain.CAREER, _governed_items(FactSet())))

    answer = DeterministicAnswerComposer().compose("How is my career?", evidence)

    assert evidence.relevant_unknown
    assert answer.corpus_limitation is True
    assert "UNKNOWN" in answer.answer


def test_timing_question_returns_only_deterministic_static_context_and_limitation() -> None:
    items = _governed_items(FactSet(facts=(Fact(fact_id=FACT_ID, value=4),)))
    evidence = _BUILDER.build(_selection(QuestionDomain.CAREER, items, timing=True))
    matched = evidence.selected_matched[0]
    transport = _FakeTransport(
        '{"answer":"Static contextual explanation.","timing_answered":false}'
    )

    answer = AnswerComposer(transport).compose("When will my career improve?", evidence)

    payload = json.loads(transport.requests[0].user_payload_json)
    assert payload["composition_mode"] == "static_context_only"
    assert (
        payload["question"]
        == "Provide a static contextual explanation for the user's career topic."
    )
    assert "When will my career improve?" not in transport.requests[0].user_payload_json
    assert (
        "do not attempt to answer the user's timing question"
        in transport.requests[0].system_instructions
    )
    assert matched.reviewed_statement in answer.answer
    assert "Static contextual explanation." not in answer.answer
    assert answer.answer.endswith("Timing is not established by the current governed evidence.")
    assert answer.timing_answered is False


@pytest.mark.parametrize(
    ("output_json", "reason_code"),
    (
        (
            '{"timing_answered":false}',
            "invalid_output_shape",
        ),
        (
            '{"answer":"","timing_answered":false}',
            "invalid_output_shape",
        ),
        (
            '{"answer":123,"timing_answered":false}',
            "invalid_output_shape",
        ),
        (
            '{"answer":"Missing timing."}',
            "invalid_output_shape",
        ),
        (
            '{"answer":"Wrong timing type.","timing_answered":"false"}',
            "invalid_output_shape",
        ),
        (
            '{"answer":"This will happen in 2030.","timing_answered":false}',
            "unauthorized_timing_text",
        ),
        (
            '{"answer":"This will happen next month.","timing_answered":false}',
            "unauthorized_timing_text",
        ),
        (
            '{"answer":"Timing is established.","timing_answered":true}',
            "unauthorized_timing_flag",
        ),
        ("not json", "invalid_json"),
    ),
)
def test_composer_rejects_unsafe_or_invalid_provider_output(
    output_json: str, reason_code: str
) -> None:
    items = _governed_items(FactSet(facts=(Fact(fact_id=FACT_ID, value=4),)))
    evidence = _BUILDER.build(_selection(QuestionDomain.CAREER, items, timing=True))
    transport = _FakeTransport(output_json)

    with pytest.raises(AnswerCompositionError) as raised:
        AnswerComposer(transport).compose("When will my career improve?", evidence)

    assert raised.value.reason_code == reason_code


def test_composer_discards_obsolete_or_harmless_control_fields() -> None:
    items = _governed_items(FactSet(facts=(Fact(fact_id=FACT_ID, value=4),)))
    evidence = _BUILDER.build(_selection(QuestionDomain.CAREER, items))
    transport = _FakeTransport(
        '{"answer":"The reviewed evidence is limited to its stated scope.",'
        '"timing_answered":false,"corpus_limitation":"false",'
        '"referenced_evidence_item_ids":["obsolete"],"reason":"unused"}'
    )

    answer = AnswerComposer(transport).compose("How is my career?", evidence)

    assert answer.answer == "The reviewed evidence is limited to its stated scope."
    assert answer.referenced_evidence_item_ids == tuple(
        item.evidence_item_id for item in evidence.selected_matched
    )
    assert answer.corpus_limitation is False


def test_schema_diagnostics_contain_structure_but_not_provider_values() -> None:
    items = _governed_items(FactSet(facts=(Fact(fact_id=FACT_ID, value=4),)))
    evidence = _BUILDER.build(_selection(QuestionDomain.CAREER, items))
    transport = _FakeTransport(
        '{"answer":"private answer text","corpus_limitation":"private","reason":"private"}'
    )

    with pytest.raises(AnswerCompositionError) as raised:
        AnswerComposer(transport).compose("How is my career?", evidence)

    error = raised.value
    assert error.returned_fields == "answer,corpus_limitation,reason"
    assert error.missing_fields == "timing_answered"
    assert error.unexpected_fields == "corpus_limitation,reason"
    assert error.field_types == "answer=str,corpus_limitation=str,reason=str"
    assert error.validation_errors == "missing:timing_answered"
    for value in ("private answer text", "private"):
        assert value not in " ".join(
            (
                error.returned_fields,
                error.missing_fields,
                error.unexpected_fields,
                error.field_types,
                error.validation_errors,
            )
        )
