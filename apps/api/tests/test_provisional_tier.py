"""NEXT-PROVISIONAL-01: the provisional rule tier is admitted, shown and promoted apart."""

import json
import re
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from astrologer.application.provisional import provisional_interpretations
from astrologer.common.config import Settings
from astrologer.knowledge import ACTIVE_PRODUCTION_RELEASE
from astrologer.knowledge.admission import AdmissionError, AdmissionValidator
from astrologer.knowledge.models import (
    ChartScope,
    FactContract,
    JyotishDomain,
    ReviewCategory,
    ReviewRecord,
    ReviewStatus,
    RightsStatus,
    SourceKind,
    SourceRecord,
)
from astrologer.knowledge.provisional import (
    PROVISIONAL_AUTHOR_AI_DRAFTED,
    PROVISIONAL_AUTHOR_OWNER,
    PromotionReviews,
    ProvisionalConfidence,
    ProvisionalCorpus,
    ProvisionalJustification,
    ProvisionalRule,
    evaluate_provisional,
    promote_to_reviewed,
    provisional_badge,
    require_disjoint,
)
from astrologer.knowledge.provisional_pack_v1 import (
    PROVISIONAL_CORPUS_V1,
    RULE_5_IN_7_SPIRITUALITY,
    RULE_7_IN_5_WEALTH,
)
from astrologer.main import create_app

# Synthetic profile P_MATCH of the frozen benchmark: its D1 fifth lord is in the seventh.
_BIRTH = {
    "birth_date": "1978-01-01",
    "birth_time": "12:00:00",
    "timezone": "UTC",
    "latitude": 0,
    "longitude": 0,
}
_AS_OF = "2026-01-01T00:00:00+00:00"
_SPIRITUALITY = "What does my chart say about spirituality?"
_REVIEWED_WORD = re.compile(r"\breviewed\b", re.IGNORECASE)


def _client() -> TestClient:
    return TestClient(create_app(Settings(llm_enabled=False)))


def _justification(**changes: object) -> dict[str, object]:
    data = RULE_7_IN_5_WEALTH.justification.model_dump()
    data.update(changes)
    return data


def _rule(**changes: object) -> dict[str, object]:
    data = RULE_7_IN_5_WEALTH.model_dump()
    data.update(changes)
    return data


# --- Admission: a complete justification record is required -------------------------------


@pytest.mark.parametrize(
    "field",
    [
        "source_work",
        "locator",
        "original_text",
        "draft_translation",
        "interpretive_reasoning",
        "conventions",
        "confidence",
        "author",
        "recorded_at",
    ],
)
def test_every_justification_field_is_required(field: str) -> None:
    data = _justification()
    del data[field]
    with pytest.raises(ValidationError):
        ProvisionalJustification.model_validate(data)


@pytest.mark.parametrize("field", ["original_text", "draft_translation", "interpretive_reasoning"])
def test_justification_text_may_not_be_empty(field: str) -> None:
    with pytest.raises(ValidationError):
        ProvisionalJustification.model_validate(_justification(**{field: ""}))


def test_conventions_must_be_listed() -> None:
    with pytest.raises(ValidationError):
        ProvisionalJustification.model_validate(_justification(conventions=()))
    with pytest.raises(ValidationError):
        ProvisionalJustification.model_validate(_justification(conventions=(" ",)))


def test_author_is_one_of_the_two_provisional_authors() -> None:
    for author in (
        "Pandit ji",
        "project owner",
        "Claude",
        "JyotAI project-owner review",
        "drafted_by: AI agent",
        "drafted_by: AI agent; adopted_by: project owner",
    ):
        with pytest.raises(ValidationError, match="provisional author"):
            ProvisionalJustification.model_validate(_justification(author=author))
    for author in (PROVISIONAL_AUTHOR_OWNER, PROVISIONAL_AUTHOR_AI_DRAFTED):
        assert ProvisionalJustification.model_validate(_justification(author=author)).author == (
            author
        )
    assert PROVISIONAL_AUTHOR_AI_DRAFTED == (
        "drafted_by: AI agent; adopted_by: project owner (pending)"
    )


def test_badge_names_the_authors_confidence() -> None:
    assert [provisional_badge(level) for level in ProvisionalConfidence] == [
        "Provisional · high confidence",
        "Provisional · medium confidence",
        "Provisional · low confidence",
    ]


def test_confidence_is_high_medium_or_low() -> None:
    with pytest.raises(ValidationError):
        ProvisionalJustification.model_validate(_justification(confidence="certain"))


def test_justification_status_is_provisional_and_never_reviewed() -> None:
    with pytest.raises(ValidationError):
        ProvisionalJustification.model_validate(_justification(status=ReviewStatus.REVIEWED))
    assert RULE_7_IN_5_WEALTH.justification.status is ReviewStatus.PROVISIONAL


@pytest.mark.parametrize(
    ("statement", "reason"),
    [
        ("With the D1 seventh lord in the fifth, the text gives better wealth.", "ranking"),
        ("With the D1 seventh lord in the fifth, the text gives favourable wealth.", "ranking"),
        ("With the D1 seventh lord in the fifth, the placement is auspicious.", "evaluative"),
        ("A reviewed indication about wealth.", "reviewed"),
        ("An approved indication about wealth.", "reviewed"),
    ],
)
def test_statement_passes_the_guards_at_admission(statement: str, reason: str) -> None:
    with pytest.raises(ValidationError, match=reason):
        ProvisionalRule.model_validate(_rule(statement=statement))


def test_rule_ids_ruleset_and_facts_are_constrained() -> None:
    rule = RULE_7_IN_5_WEALTH.rule.model_dump()
    with pytest.raises(ValidationError, match="must start with"):
        ProvisionalRule.model_validate(_rule(rule={**rule, "rule_id": "bphs.d1.x.v1"}))
    with pytest.raises(ValidationError, match="ruleset"):
        ProvisionalRule.model_validate(
            _rule(rule={**rule, "ruleset_version": "jyotish.production-rules-v1"})
        )
    with pytest.raises(ValidationError, match="placement facts"):
        ProvisionalRule.model_validate(_rule(fact_dependencies=("jyotish.d1.house.10.lord",)))
    with pytest.raises(ValidationError, match="domain"):
        ProvisionalRule.model_validate(_rule(domain=JyotishDomain.CAREER))


def test_provisional_ids_never_collide_with_reviewed_rules() -> None:
    reviewed = {envelope.rule.rule_id for envelope in ACTIVE_PRODUCTION_RELEASE.envelopes}
    require_disjoint(PROVISIONAL_CORPUS_V1, reviewed)
    with pytest.raises(AdmissionError, match="collide"):
        require_disjoint(PROVISIONAL_CORPUS_V1, {RULE_7_IN_5_WEALTH.rule_id})


def test_provisional_rules_are_absent_from_the_reviewed_release() -> None:
    reviewed_ids = {rule.rule_id for rule in ACTIVE_PRODUCTION_RELEASE.manifest.rules}
    registry_text = ACTIVE_PRODUCTION_RELEASE.model_dump_json()
    for rule in PROVISIONAL_CORPUS_V1.rules:
        assert rule.rule_id not in reviewed_ids
        assert rule.rule_id not in registry_text
        assert rule.statement not in registry_text


def test_seed_corpus_records() -> None:
    corpus = PROVISIONAL_CORPUS_V1
    assert corpus.release_id == "jyotish.provisional@v1"
    assert {rule.domain for rule in corpus.rules} == {
        JyotishDomain.EDUCATION,
        JyotishDomain.SPIRITUALITY,
        JyotishDomain.WEALTH,
    }
    for rule in corpus.rules:
        # Every seed rule was drafted by an AI agent; the owner's adoption is pending.
        assert rule.justification.author == PROVISIONAL_AUTHOR_AI_DRAFTED
        assert rule.justification.status is ReviewStatus.PROVISIONAL
        assert rule.chart_scope is ChartScope.D1_RASHI
        assert _REVIEWED_WORD.search(rule.model_dump_json()) is None
    with pytest.raises(ValidationError, match="unique"):
        ProvisionalCorpus(corpus_id="x", corpus_version="v1", rules=corpus.rules + corpus.rules[:1])


def test_a_provisional_review_status_is_never_accepted_as_reviewed() -> None:
    from astrologer.knowledge.admission import _require_review

    record = ReviewRecord(
        category=ReviewCategory.INTERPRETATION_REVIEW,
        status=ReviewStatus.PROVISIONAL,
        reviewer=PROVISIONAL_AUTHOR_OWNER,
        reviewed_at=datetime(2026, 11, 24, tzinfo=UTC),
    )
    with pytest.raises(AdmissionError):
        _require_review(record, ReviewCategory.INTERPRETATION_REVIEW, "needs review")


# --- Evaluation and display ------------------------------------------------------------------


def test_only_true_matches_are_returned() -> None:
    fact = "jyotish.d1.house_lord.7.placement_house"
    assert len(evaluate_provisional(PROVISIONAL_CORPUS_V1, {fact: 5}, "wealth")) == 1
    assert evaluate_provisional(PROVISIONAL_CORPUS_V1, {fact: 6}, "wealth") == ()
    assert evaluate_provisional(PROVISIONAL_CORPUS_V1, {}, "wealth") == ()
    assert evaluate_provisional(PROVISIONAL_CORPUS_V1, {fact: 5}, "career") == ()


def test_display_items_carry_the_badge_and_full_justification() -> None:
    (item,) = provisional_interpretations(
        PROVISIONAL_CORPUS_V1, {"jyotish.d1.house_lord.7.placement_house": 5}, "wealth"
    )
    assert item.tier == "provisional"
    assert item.badge == "Provisional · high confidence"  # v.54 is high confidence
    assert item.placement_explanation == "Your D1 seventh-house lord is placed in the fifth house."
    assert item.statement == RULE_7_IN_5_WEALTH.statement
    assert item.corpus_release == "jyotish.provisional@v1"
    justification = item.justification
    assert justification.author == "drafted_by: AI agent; adopted_by: project owner (pending)"
    assert justification.status == "provisional"
    assert justification.confidence == "high"
    assert justification.original_text == RULE_7_IN_5_WEALTH.justification.original_text
    assert justification.draft_translation and justification.interpretive_reasoning
    assert justification.conventions and "PDF p. 190" in justification.locator


def test_a_statement_that_fails_a_guard_at_runtime_is_dropped() -> None:
    bad = RULE_7_IN_5_WEALTH.model_construct(
        **{**dict(RULE_7_IN_5_WEALTH), "statement": "This placement is excellent for wealth."}
    )
    corpus = ProvisionalCorpus.model_construct(corpus_id="x", corpus_version="v1", rules=(bad,))
    facts = {"jyotish.d1.house_lord.7.placement_house": 5}
    assert provisional_interpretations(corpus, facts, "wealth") == ()


# --- API flag -------------------------------------------------------------------------------


def _analyze(client: TestClient, **extra: object) -> dict[str, object]:
    response = client.post(
        "/api/v1/analyze",
        json={"birth_input": _BIRTH, "as_of": _AS_OF, "question": _SPIRITUALITY, **extra},
    )
    assert response.status_code == 200
    payload: dict[str, object] = response.json()
    return payload


def _without_provisional(payload: dict[str, object]) -> dict[str, object]:
    copy = json.loads(json.dumps(payload))
    for answer in copy["answers"]:
        answer.pop("provisional_interpretations")
    return copy  # type: ignore[no-any-return]


def test_flag_defaults_to_off_and_changes_nothing() -> None:
    client = _client()
    default = _analyze(client)
    off = _analyze(client, include_provisional=False)
    on = _analyze(client, include_provisional=True)
    assert default == off
    assert all(answer["provisional_interpretations"] == [] for answer in default["answers"])  # type: ignore[index, union-attr]
    # Every reviewed part of the answer is identical with the flag on.
    assert _without_provisional(on) == _without_provisional(off)


def test_flag_on_returns_the_matched_provisional_rule_kept_apart() -> None:
    on = _analyze(_client(), include_provisional=True)
    (answer,) = on["answers"]  # type: ignore[misc]
    (item,) = answer["provisional_interpretations"]
    assert item["rule_id"] == RULE_5_IN_7_SPIRITUALITY.rule_id
    assert item["badge"] == "Provisional · low confidence"  # v.40 is low confidence
    assert item["justification"]["author"] == PROVISIONAL_AUTHOR_AI_DRAFTED
    # Never in the reviewed answer text, review types or evidence.
    reviewed_parts = json.dumps(
        {k: v for k, v in answer.items() if k != "provisional_interpretations"}
    )
    assert RULE_5_IN_7_SPIRITUALITY.rule_id not in reviewed_parts
    assert RULE_5_IN_7_SPIRITUALITY.statement not in reviewed_parts
    assert RULE_5_IN_7_SPIRITUALITY.rule_id not in json.dumps(on["evidence_package"])
    assert _REVIEWED_WORD.search(json.dumps(item, ensure_ascii=False)) is None


def test_consultation_passes_the_flag_through() -> None:
    client = _client()
    base = {"birth_input": _BIRTH, "as_of": _AS_OF, "question": _SPIRITUALITY}
    off = client.post("/api/v1/consultation", json=base).json()
    on = client.post("/api/v1/consultation", json={**base, "include_provisional": True}).json()
    assert off["analysis"]["answers"][0]["provisional_interpretations"] == []
    (item,) = on["analysis"]["answers"][0]["provisional_interpretations"]
    assert item["tier"] == "provisional"


def test_flag_must_be_a_boolean() -> None:
    response = _client().post(
        "/api/v1/analyze",
        json={
            "birth_input": _BIRTH,
            "as_of": _AS_OF,
            "question": _SPIRITUALITY,
            "include_provisional": "maybe",
        },
    )
    assert response.status_code == 422


# --- Promotion: provisional → reviewed only with a review record -----------------------------

_SOURCE = SourceRecord(
    source_id="bphs.selected-edition",
    source_version="v1",
    kind=SourceKind.PRIMARY,
    title="Brihat Parashara Hora Shastra / Brihat Parashara Hora Shastram",
    original_language="Sanskrit",
    rights_status=RightsStatus.REFERENCE_ONLY,
)
_CONTRACT = FactContract(
    contract_id="jyotish.d1.structural.provisional-promotion-test",
    contract_version="v1",
    chart_scope=ChartScope.D1_RASHI,
    methodology_id="jyotish-derived-facts-v1",
    available_fact_ids=("jyotish.d1.house_lord.7.placement_house",),
)


def _review(
    category: ReviewCategory, reviewer: str = "Synthetic Reviewer (Acharya)"
) -> ReviewRecord:
    return ReviewRecord(
        category=category,
        status=ReviewStatus.REVIEWED,
        reviewer=reviewer,
        reviewed_at=datetime(2026, 12, 1, tzinfo=UTC),
        notes="Synthetic test record.",
    )


def _reviews(**changes: ReviewRecord) -> PromotionReviews:
    data = {
        "source_verification": _review(ReviewCategory.SOURCE_VERIFICATION),
        "translation_verification": _review(ReviewCategory.TRANSLATION_VERIFICATION),
        "interpretation_review": _review(ReviewCategory.INTERPRETATION_REVIEW),
        "formalization_review": _review(ReviewCategory.FORMALIZATION_REVIEW),
    }
    data.update(changes)
    return PromotionReviews(**data)


def _promote(reviews: PromotionReviews | None) -> object:
    return promote_to_reviewed(
        RULE_7_IN_5_WEALTH,
        reviews,
        source=_SOURCE,
        fact_contract=_CONTRACT,
        registry_version="jyotish-source-registry-promotion-test",
    )


def test_promotion_requires_a_review_record() -> None:
    with pytest.raises(AdmissionError, match="requires a review record"):
        _promote(None)


def test_promotion_requires_every_review_category() -> None:
    with pytest.raises(ValidationError):
        PromotionReviews(  # type: ignore[call-arg]
            source_verification=_review(ReviewCategory.SOURCE_VERIFICATION),
            translation_verification=_review(ReviewCategory.TRANSLATION_VERIFICATION),
            interpretation_review=_review(ReviewCategory.INTERPRETATION_REVIEW),
        )
    with pytest.raises(AdmissionError, match="formalization_review"):
        _promote(_reviews(formalization_review=_review(ReviewCategory.INTERPRETATION_REVIEW)))


def test_promotion_rejects_drafts_the_provisional_author_and_ai_reviewers() -> None:
    draft = ReviewRecord(
        category=ReviewCategory.INTERPRETATION_REVIEW,
        status=ReviewStatus.DRAFT,
        reviewer="Synthetic Reviewer",
        reviewed_at=datetime(2026, 12, 1, tzinfo=UTC),
    )
    provisional = ReviewRecord(
        category=ReviewCategory.INTERPRETATION_REVIEW,
        status=ReviewStatus.PROVISIONAL,
        reviewer="Synthetic Reviewer",
        reviewed_at=datetime(2026, 12, 1, tzinfo=UTC),
    )
    with pytest.raises(AdmissionError, match="completed"):
        _promote(_reviews(interpretation_review=draft))
    with pytest.raises(AdmissionError, match="completed"):
        _promote(_reviews(interpretation_review=provisional))
    for author in (PROVISIONAL_AUTHOR_OWNER, PROVISIONAL_AUTHOR_AI_DRAFTED, "AI agent"):
        with pytest.raises(AdmissionError, match="provisional author"):
            review = _review(ReviewCategory.INTERPRETATION_REVIEW, author)
            _promote(_reviews(interpretation_review=review))
    with pytest.raises(AdmissionError, match="AI agent"):
        _promote(
            _reviews(interpretation_review=_review(ReviewCategory.INTERPRETATION_REVIEW, "Claude"))
        )


def test_promotion_with_a_review_record_yields_a_reviewed_production_rule() -> None:
    result = _promote(_reviews())
    envelope = result.envelope  # type: ignore[attr-defined]
    registry = result.registry  # type: ignore[attr-defined]
    assert envelope.rule.rule_id == "bphs.d1.house_lord.7.equals_5.wealth.v1"
    assert envelope.lifecycle.value == "production_active"
    assert envelope.rule.ruleset_version == "jyotish.production-rules-v1"
    (interpretation,) = registry.interpretations
    assert interpretation.review.status is ReviewStatus.REVIEWED
    assert interpretation.statement == RULE_7_IN_5_WEALTH.statement
    (passage,) = registry.passages
    assert passage.excerpt == RULE_7_IN_5_WEALTH.justification.original_text
    # The same validator the production corpus loader uses accepts it.
    AdmissionValidator().validate_production_active(envelope, registry, _CONTRACT)
