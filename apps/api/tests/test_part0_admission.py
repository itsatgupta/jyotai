"""NEXT-ADMIT-01: review packet Part 0 admitted under a general expert approval.

Covers the v11 natal release (0a: 10th lord in 1, 2/3/7, 8), the production signification
corpus (0b) and the X18 lordship principle.  Synthetic facts and synthetic births only.
"""

import pytest
from test_period_themes import _AS_OF, RAHU_MERCURY

from astrologer.application.analyze import (
    DeterministicAnalysisRequest,
    DeterministicAnalysisService,
)
from astrologer.application.answer import AskJyotAIService
from astrologer.application.context import DeterministicAstrologyContextService
from astrologer.application.period_themes import PERIOD_THEMES_CLOSING
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.composition import DeterministicAnswerComposer
from astrologer.evidence import InterpretationEvidenceBuilder
from astrologer.knowledge import ACTIVE_PRODUCTION_RELEASE as RUNTIME_RELEASE
from astrologer.knowledge.career_part0_pack_v1 import (
    ACTIVE_PRODUCTION_RELEASE,
    EXPERT_REVIEW_NOTES,
    EXPERT_REVIEWER,
    EXPERT_STATEMENT,
    FACT_CONTRACT,
    PART0_RULE_ENVELOPES,
    PRODUCTION_MANIFEST,
    RULE_IN_1,
    RULE_IN_2_3_OR_7,
    RULE_IN_8,
    SOURCE_REGISTRY,
    TENTH_LORD_FACT_ID,
    WITHHELD_STATEMENT,
)
from astrologer.knowledge.corpus import ProductionCorpusLoader
from astrologer.knowledge.evaluation import (
    FactEvaluationProvenance,
    GovernedRuleEvaluator,
    canonical_sha256,
    fact_set_sha256,
)
from astrologer.knowledge.friends_pack_v1 import ACTIVE_PRODUCTION_RELEASE as RELEASE_V10
from astrologer.knowledge.models import JyotishDomain, ReviewCategory
from astrologer.knowledge.signification import PERIOD_THEMES_TEMPLATE_VERSION
from astrologer.knowledge.signification_part0b_v1 import (
    ACTIVE_SIGNIFICATION_CORPUS,
    LORDSHIP_PRINCIPLE,
    PRODUCTION_SIGNIFICATION_MANIFEST,
)
from astrologer.rules.models import EvaluationStatus, Fact, FactSet
from astrologer.timing_rules.service import CareerTimingAnalysisService

PART0 = (RULE_IN_1, RULE_IN_2_3_OR_7, RULE_IN_8)
GENERAL_APPROVAL = (
    "Approved as proposed; no item-level readings, OCR issues or translations individually "
    "addressed."
)


def _evaluate(*facts: Fact):  # type: ignore[no-untyped-def]
    fact_set = FactSet(facts=facts)
    return GovernedRuleEvaluator().evaluate(
        PRODUCTION_MANIFEST,
        ACTIVE_PRODUCTION_RELEASE.envelopes,
        SOURCE_REGISTRY,
        FACT_CONTRACT,
        fact_set,
        FactEvaluationProvenance(
            methodology_id=FACT_CONTRACT.methodology_id,
            source_register_version=SOURCE_REGISTRY.registry_version,
            derived_fact_provenance_sha256="0" * 64,
            fact_set_sha256=fact_set_sha256(fact_set),
        ),
    )


def _status(rule_id: str, *facts: Fact) -> EvaluationStatus:
    return next(r for r in _evaluate(*facts) if r.evaluation.rule_id == rule_id).evaluation.status


# --- 0a: release v11 ---------------------------------------------------------------------------


def test_v11_adds_exactly_the_three_part0_rules_and_keeps_v10_immutable() -> None:
    assert RUNTIME_RELEASE is ACTIVE_PRODUCTION_RELEASE
    assert ACTIVE_PRODUCTION_RELEASE.release_version == "v11"
    ids = [item.rule.rule_id for item in ACTIVE_PRODUCTION_RELEASE.envelopes]
    assert len(ids) == len(set(ids)) == 25
    assert set(ids) == {item.rule.rule_id for item in RELEASE_V10.envelopes} | set(PART0)
    assert all(item.domain is JyotishDomain.CAREER for item in PART0_RULE_ENVELOPES)
    assert (
        RELEASE_V10.manifest.content_sha256()
        == "f9827c92375485aaae453ebf0e9f06cdfa28424580834d8421b1c4c5b9f5f4fb"
    )
    assert (
        canonical_sha256(RELEASE_V10)
        == "965f8e31e31f33b44214132048701329b340b64704fc4b621e08ea494a4344b5"
    )


def test_v11_loads_through_the_admission_validator() -> None:
    loaded = ProductionCorpusLoader().load(
        PRODUCTION_MANIFEST, ACTIVE_PRODUCTION_RELEASE.envelopes, SOURCE_REGISTRY, FACT_CONTRACT
    )
    assert {rule.rule_id for rule in loaded} >= set(PART0)


@pytest.mark.parametrize(
    ("rule_id", "house", "expected"),
    [
        # Packet test cases T0a.1.1–T0a.3.2 (Aries Lagna, 10th lord Saturn).
        (RULE_IN_1, 1, EvaluationStatus.TRUE),
        (RULE_IN_1, 10, EvaluationStatus.FALSE),
        (RULE_IN_2_3_OR_7, 2, EvaluationStatus.TRUE),
        (RULE_IN_2_3_OR_7, 3, EvaluationStatus.TRUE),
        (RULE_IN_2_3_OR_7, 7, EvaluationStatus.TRUE),
        (RULE_IN_2_3_OR_7, 5, EvaluationStatus.FALSE),
        (RULE_IN_8, 8, EvaluationStatus.TRUE),
        (RULE_IN_8, 9, EvaluationStatus.FALSE),
    ],
)
def test_packet_test_cases(rule_id: str, house: int, expected: EvaluationStatus) -> None:
    assert _status(rule_id, Fact(fact_id=TENTH_LORD_FACT_ID, value=house)) is expected


@pytest.mark.parametrize("rule_id", PART0)
def test_unresolved_placement_is_unknown(rule_id: str) -> None:
    assert _status(rule_id) is EvaluationStatus.UNKNOWN


@pytest.mark.parametrize("house", range(1, 13))
def test_every_resolvable_placement_has_exactly_one_natal_career_rule(house: int) -> None:
    matched = [
        r.evaluation.rule_id
        for r in _evaluate(Fact(fact_id=TENTH_LORD_FACT_ID, value=house))
        if r.evaluation.status is EvaluationStatus.TRUE
        and r.governance_provenance.domain is JyotishDomain.CAREER
    ]
    assert len(matched) == 1, matched


# --- The expert record on every review -------------------------------------------------------


def _part0_reviews():  # type: ignore[no-untyped-def]
    interpretation_ids = {e.interpretation_id for e in PART0_RULE_ENVELOPES}
    interpretations = [
        i for i in SOURCE_REGISTRY.interpretations if i.interpretation_id in interpretation_ids
    ]
    passage_ids = {i.passage_id for i in interpretations}
    yield from (e.formalization_review for e in PART0_RULE_ENVELOPES)
    yield from (i.review for i in interpretations)
    yield from (p.review for p in SOURCE_REGISTRY.passages if p.passage_id in passage_ids)
    yield from (t.review for t in SOURCE_REGISTRY.translations if t.passage_id in passage_ids)
    yield from (e.review for e in PRODUCTION_SIGNIFICATION_MANIFEST.entries)
    yield LORDSHIP_PRINCIPLE.review


def test_every_review_records_the_general_approval_verbatim() -> None:
    reviews = list(_part0_reviews())
    categories = {review.category for review in reviews}
    assert categories == {
        ReviewCategory.FORMALIZATION_REVIEW,
        ReviewCategory.INTERPRETATION_REVIEW,
        ReviewCategory.SOURCE_VERIFICATION,
        ReviewCategory.TRANSLATION_VERIFICATION,
    }
    assert len(reviews) == 3 * 4 + len(PRODUCTION_SIGNIFICATION_MANIFEST.entries) + 1
    for review in reviews:
        assert review.reviewer == EXPERT_REVIEWER == "Pandit ji"
        assert review.reviewed_at.date().isoformat() == "2026-11-23"
        assert review.notes == EXPERT_REVIEW_NOTES
    assert f'"{EXPERT_STATEMENT}"' in EXPERT_REVIEW_NOTES
    assert EXPERT_STATEMENT == (
        "All data points look good. The app is giving good calculation results. Mahadasha and "
        "Antardasha are both good, including their calculations and results. Proceed."
    )
    for fragment in (
        "GENERAL approval",
        "full name pending",
        "qualification: Acharya",
        "independence: not recorded",
        "verbal, relayed by Atul, 2026-11-23",
        "Reviewer has seen the review packet PDF",
        GENERAL_APPROVAL,
    ):
        assert fragment in EXPERT_REVIEW_NOTES, fragment


# --- v.76: calculated match only, wording withheld -------------------------------------------


def test_v76_shows_only_the_withheld_notice() -> None:
    envelope = next(e for e in PART0_RULE_ENVELOPES if e.rule.rule_id == RULE_IN_8)
    interpretation = next(
        i
        for i in SOURCE_REGISTRY.interpretations
        if i.interpretation_id == envelope.interpretation_id
    )
    assert interpretation.statement == WITHHELD_STATEMENT
    assert "wording is withheld pending further review" in WITHHELD_STATEMENT
    passage_ids = {interpretation.passage_id}
    texts = [
        interpretation.statement,
        interpretation.scope_notes or "",
        *(t.text for t in SOURCE_REGISTRY.translations if t.passage_id in passage_ids),
        *(
            p.locator + p.passage_reference
            for p in SOURCE_REGISTRY.passages
            if p.passage_id in passage_ids
        ),
    ]
    for text in texts:
        lowered = text.lower()
        for word in ("lifespan", "short life", "short-lived", "alpāyu", "अल्पायु", "cruel", "thief"):
            assert word not in lowered, (word, text)


def test_v71_and_v72_use_the_packet_proposed_wording_verbatim() -> None:
    statements = {i.interpretation_id: i.statement for i in SOURCE_REGISTRY.interpretations}
    v71 = statements["bphs.bhavesha-phala.10th-lord.1.interpretation.v1"]
    v72 = statements["bphs.bhavesha-phala.10th-lord.2-3-or-7.interpretation.v1"]
    assert v71.startswith("With the D1 tenth-house lord in the first house")
    assert "childhood" not in v71 and "sick" not in v71  # health clause left out, as proposed
    assert v72.startswith("With the D1 tenth-house lord in the second, third or seventh house")


# --- 0b and X18 --------------------------------------------------------------------------------


def test_production_signification_terms_are_the_proposed_column_minus_exclusions() -> None:
    corpus = ACTIVE_SIGNIFICATION_CORPUS
    assert corpus.version == "jyotish.signification.production@v1"
    sanskrit = {
        term.sanskrit for entry in PRODUCTION_SIGNIFICATION_MANIFEST.entries for term in entry.terms
    }
    for excluded in (
        "बालत्वधीमतः",
        "ऐश्वर्यदायकः",
        "मृत्युजाल",
        "अङ्कुरादि",
        "गत्यनूक",
        "फलमन्त्यादिक",
        "आकाशवृत्ति",
        "वर्ण",
        "राज्यापभ्रंश",
        "क्रोधः",
        "वीर्यम्",
        "दुःखम्",
    ):
        assert excluded not in sanskrit, excluded
    assert corpus.bhava(4) is None and corpus.bhava(8) is None
    assert [t.display for t in corpus.bhava(6).terms] == ["adversaries"]  # type: ignore[union-attr]
    assert [t.display for t in corpus.bhava(7).terms] == ["trade or business"]  # type: ignore[union-attr]
    assert [t.display for t in corpus.bhava(11).terms] == ["gain", "increase"]  # type: ignore[union-attr]
    assert all(
        corpus.graha(g) is not None
        for g in ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu")
    )


def test_x18_approves_the_v1_template_for_mahadasha_and_antardasha() -> None:
    principle = ACTIVE_SIGNIFICATION_CORPUS.lordship_principle
    assert principle is LORDSHIP_PRINCIPLE
    assert principle.scope == "MAHADASHA_AND_ANTARDASHA"
    assert (
        principle.approved_template_version == PERIOD_THEMES_TEMPLATE_VERSION == "period-themes-v1"
    )


def test_production_period_themes_for_a_rahu_mercury_year() -> None:
    provider = SwissEphemerisProvider()
    service = AskJyotAIService(
        DeterministicAnalysisService(DeterministicAstrologyContextService(provider)),
        InterpretationEvidenceBuilder(),
        DeterministicAnswerComposer(),
        CareerTimingAnalysisService(provider),
    )
    answer = service.answer(
        DeterministicAnalysisRequest(
            birth_input=RAHU_MERCURY, as_of=_AS_OF, question="How is my career in 2028?"
        )
    ).answers[0]
    kinds = [s.kind for s in answer.consultation_sections]
    assert kinds[:3] == ["direct", "glance", "period_themes"]
    section = answer.consultation_sections[2]
    texts = [s.text for s in section.synthesis_sentences]
    # Rahu rules no sign: only its occupied house (the 11th).
    assert texts[0] == (
        "During your Rahu Mahadasha throughout 2028, the reviewed significations associated "
        "with Rahu (army or forces) and with the house it occupies (11th house: gain, "
        "increase) are the themes the texts associate with this period."
    )
    assert texts[-1] == PERIOD_THEMES_CLOSING
    assert len(texts) == 4  # Rahu MD, Saturn AD, Mercury AD, closing
    for sentence in section.synthesis_sentences[:-1]:
        assert "jyotish.lordship-principle.x18@v1" in sentence.rule_ids
        assert PERIOD_THEMES_TEMPLATE_VERSION in sentence.calc_method_ids
    plan = answer.career_answer_plan
    assert plan is not None
    assert plan.signification_corpus_version == "jyotish.signification.production@v1"
