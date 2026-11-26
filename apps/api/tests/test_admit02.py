"""NEXT-ADMIT-02: the reviewer's Sitting 1 + 2 written verdicts.

Every decision comes from ``research/prereview/pandit-ji-verdicts-2026-11-24.md`` as
instructed by the project owner.  Synthetic facts and synthetic births only.
"""

import inspect
from datetime import UTC, datetime

import pytest
from test_year_glance import _answer, _birth

from astrologer.application.analyze import (
    DeterministicAnalysisRequest,
    DeterministicAnalysisService,
)
from astrologer.application.answer import AskJyotAIService
from astrologer.application.context import DeterministicAstrologyContextService
from astrologer.application.lord_dignity import DIGNITY_PREFIX, lord_dignity
from astrologer.astrology.dasha import DashaLord
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.birth.models import BirthInput
from astrologer.composition import DeterministicAnswerComposer
from astrologer.composition.evaluative_guard import EVALUATIVE_LANGUAGE
from astrologer.evidence import InterpretationEvidenceBuilder
from astrologer.knowledge import ACTIVE_PRODUCTION_RELEASE
from astrologer.knowledge.admit02_pack_v1 import (
    ADMIT02_CHANNEL,
    ADMIT02_NOTE,
    ADMIT02_REVIEWER,
    PASSAGE_IN_1_READING,
    REMOVED_FROM_MANIFEST,
    RULE_10_IN_4,
    RULE_10_IN_4_OR_10,
    RULE_10_IN_10,
    RULE_CHILDREN_10_IN_5_OR_11,
    RULE_IN_2_OR_3,
    RULE_IN_7,
    STATEMENT_10_IN_6_OR_12,
    STATEMENT_IN_7_PAUSED,
    WITHHELD_WORDING_RULE_IDS,
)
from astrologer.knowledge.career_part0_pack_v1 import (
    ACTIVE_PRODUCTION_RELEASE as RELEASE_V11,
)
from astrologer.knowledge.career_part0_pack_v1 import RULE_IN_2_3_OR_7, RULE_IN_8
from astrologer.knowledge.corpus import ProductionCorpusLoader
from astrologer.knowledge.evaluation import (
    FactEvaluationProvenance,
    GovernedRuleEvaluator,
    canonical_sha256,
    fact_set_sha256,
)
from astrologer.knowledge.reviewer_guard import ai_review_violation
from astrologer.knowledge.rule_weights import SECONDARY_RULES, primary_first, rule_weight
from astrologer.knowledge.signification_admit02_v1 import (
    ACTIVE_SIGNIFICATION_CORPUS,
    LORDSHIP_PRINCIPLE_V2,
    PERIOD_THEMES_CLOSING_V2,
    X18_BASIS_LABEL,
)
from astrologer.knowledge.signification_part0b_v1 import (
    PRODUCTION_SIGNIFICATION_MANIFEST as SIGNIFICATION_MANIFEST_V2,
)
from astrologer.rules.models import EvaluationStatus, Fact, FactSet
from astrologer.timing_rules.evaluator import CareerTimingRuleEvaluator
from astrologer.timing_rules.models import (
    V87_REVIEWED_INTERPRETATION_ADMIT02,
    V140_REVIEWED_INTERPRETATION_ADMIT02,
    CareerTimingRequest,
    CareerTimingRule,
    MahadashaTimingCondition,
    MoonVenusOwnExaltationTimingSourceRecord,
    NatalTimingCondition,
    TimingRuleStatus,
    TimingSourceRecord,
)
from astrologer.timing_rules.registry import (
    PRODUCTION_CAREER_TIMING_RELEASE_V2,
    PRODUCTION_CAREER_TIMING_RELEASE_V3,
    get_active_timing_release,
)
from astrologer.timing_rules.service import CareerTimingAnalysisService

_AS_OF = datetime(2026, 1, 1, tzinfo=UTC)
TENTH = "jyotish.d1.house_lord.10.placement_house"
# Synthetic births found by scanning dates at 12:00 UTC, 0°N 0°E.
TENTH_LORD_IN = {
    10: _birth("1985-01-01", "12:00:00"),
    7: _birth("1986-02-12", "12:00:00"),
    6: _birth("1986-04-27", "12:00:00"),
}
_V11_STATEMENTS = {
    e.rule.rule_id: next(
        i.statement
        for i in RELEASE_V11.registry.interpretations
        if i.interpretation_id == e.interpretation_id
    )
    for e in RELEASE_V11.envelopes
}


def _interpretation(rule_id: str):  # type: ignore[no-untyped-def]
    envelope = next(e for e in ACTIVE_PRODUCTION_RELEASE.envelopes if e.rule.rule_id == rule_id)
    return next(
        i
        for i in ACTIVE_PRODUCTION_RELEASE.registry.interpretations
        if i.interpretation_id == envelope.interpretation_id
    )


def _status(rule_id: str, house: int) -> EvaluationStatus:
    release = ACTIVE_PRODUCTION_RELEASE
    facts = FactSet(facts=(Fact(fact_id=TENTH, value=house),))
    results = GovernedRuleEvaluator().evaluate(
        release.manifest,
        release.envelopes,
        release.registry,
        release.fact_contract,
        facts,
        FactEvaluationProvenance(
            methodology_id=release.fact_contract.methodology_id,
            source_register_version=release.registry.registry_version,
            derived_fact_provenance_sha256="0" * 64,
            fact_set_sha256=fact_set_sha256(facts),
        ),
    )
    return next(r for r in results if r.evaluation.rule_id == rule_id).evaluation.status


# --- records ------------------------------------------------------------------------------


def test_v12_supersedes_v11_and_v11_is_unchanged() -> None:
    assert ACTIVE_PRODUCTION_RELEASE.release_version == "v12"
    assert RELEASE_V11.release_version == "v11"
    # The v11 manifest hash recorded in every v19 answer (``manifest_content_sha256``).
    assert (
        canonical_sha256(RELEASE_V11.manifest)
        == "e602fc4f5841ff0b3dbd918da35e1b76a9fe15a73a6b8e96b1925e5e34c31f24"
    )
    rules = ProductionCorpusLoader().load(
        ACTIVE_PRODUCTION_RELEASE.manifest,
        ACTIVE_PRODUCTION_RELEASE.envelopes,
        ACTIVE_PRODUCTION_RELEASE.registry,
        ACTIVE_PRODUCTION_RELEASE.fact_contract,
    )
    assert len(rules) == 26
    old = {e.rule.rule_id for e in RELEASE_V11.envelopes}
    new = {e.rule.rule_id for e in ACTIVE_PRODUCTION_RELEASE.envelopes}
    assert old - new == REMOVED_FROM_MANIFEST
    assert new - old == {RULE_10_IN_4, RULE_10_IN_10, RULE_IN_2_OR_3, RULE_IN_7}
    # Every v11 record is still in the v12 registry (superseding records only).
    assert set(RELEASE_V11.registry.interpretations) <= set(
        ACTIVE_PRODUCTION_RELEASE.registry.interpretations
    )
    assert set(RELEASE_V11.registry.passages) <= set(ACTIVE_PRODUCTION_RELEASE.registry.passages)


def test_every_new_record_names_the_reviewer_channel_and_owner_note() -> None:
    old = {i.interpretation_id for i in RELEASE_V11.registry.interpretations}
    new = [
        i
        for i in ACTIVE_PRODUCTION_RELEASE.registry.interpretations
        if i.interpretation_id not in old
    ]
    assert len(new) == 25  # 21 confirmed or changed + 4 split/paused
    records = [i.review for i in new] + [PRODUCTION_CAREER_TIMING_RELEASE_V3.review]
    records += [e.review for e in ACTIVE_SIGNIFICATION_CORPUS.entries if e.rule_version == "v2"]
    records.append(LORDSHIP_PRINCIPLE_V2.review)
    for review in records:
        assert review.reviewer == ADMIT02_REVIEWER == "Pandit ji (full name pending)"
        assert review.notes is not None
        assert "Acharya" in review.notes
        assert ADMIT02_CHANNEL == "written verdicts relayed by Atul, 2026-11-24"
        assert ADMIT02_CHANNEL in review.notes
        assert ADMIT02_NOTE in review.notes
        assert ai_review_violation(review) is None
    assert ADMIT02_NOTE == (
        "Admission instructed by the project owner; authorship of the written verdicts not "
        "independently confirmed."
    )


# --- Sitting 1 items 1–24 ---------------------------------------------------------------------


@pytest.mark.parametrize(
    "rule_id",
    [
        "bphs.d1.house_lord.11.in_9_or_10.v1",
        "bphs.d1.house_lord.11.in_1.wealth.v1",
        "bphs.d1.house_lord.11.in_2_or_5.wealth.v1",
        "bphs.d1.house_lord.11.in_9_or_10.wealth.v1",
        "bphs.d1.house_lord.5.in_11.wealth.v1",
        "bphs.d1.house_lord.4.in_1_or_7.education.v1",
        "bphs.d1.house_lord.5.in_11.education.v1",
        "bphs.d1.house_lord.5.in_11.children.v1",
        "bphs.d1.house_lord.11.in_2_or_5.children.v1",
        "bphs.d1.house_lord.10.in_4_or_10.spirituality.v1",
        "bphs.d1.house_lord.10.equals_9.spirituality.v1",
        "bphs.d1.house_lord.11.in_2_or_5.spirituality.v1",
        "bphs.d1.house_lord.11.in_9_or_10.spirituality.v1",
        "bphs.d1.house_lord.6.in_2_or_10.travel.v1",
        "bphs.d1.house_lord.10.equals_9.friends.v1",
        "bphs.d1.house_lord.10.equals_1.v1",
    ],
)
def test_confirmed_rules_keep_their_wording_byte_for_byte(rule_id: str) -> None:
    interpretation = _interpretation(rule_id)
    assert interpretation.statement == _V11_STATEMENTS[rule_id]
    assert interpretation.review.reviewer == ADMIT02_REVIEWER


def test_changed_wording_follows_the_verdicts() -> None:
    four = _interpretation(RULE_10_IN_4).statement
    ten = _interpretation(RULE_10_IN_10).statement
    assert "property, homeland, the institutional environment, public position" in four
    assert "strong connection with profession, status and public activity" in ten
    five = _interpretation("bphs.d1.house_lord.10.in_5_or_11.v1").statement
    assert "children" not in five  # item 5: only the career-relevant layer
    assert "intelligence, creativity, counsel, decision-making and merit" in five
    six = _interpretation("bphs.d1.house_lord.10.in_6_or_12.v1").statement
    assert six == STATEMENT_10_IN_6_OR_12
    assert "not by itself an adverse career indication" in six  # item 6: never "bad career"
    assert "adversarial difficulty" not in six
    nine = _interpretation("bphs.d1.house_lord.10.equals_9.v1").statement
    assert "dharma–karma relationship" in nine
    edu = _interpretation("bphs.d1.house_lord.11.in_11.education.v1").statement
    assert "poetic" not in edu and "intellectual accomplishment" in edu
    business = _interpretation("bphs.d1.house_lord.6.in_9.business.v1").statement
    assert "secondary commercial/trade-related indication" in business
    for text in (four, ten, five, six, nine):
        assert text.endswith(
            "These do not by themselves establish a specific profession, promotion, income, "
            "or timing."
        )


def test_item_4_splits_the_fourth_and_tenth_placements() -> None:
    assert _status(RULE_10_IN_4, 4) is EvaluationStatus.TRUE
    assert _status(RULE_10_IN_4, 10) is EvaluationStatus.FALSE
    assert _status(RULE_10_IN_10, 10) is EvaluationStatus.TRUE
    assert _status(RULE_10_IN_10, 4) is EvaluationStatus.FALSE
    assert RULE_10_IN_4_OR_10 not in {e.rule.rule_id for e in ACTIVE_PRODUCTION_RELEASE.envelopes}


def test_item_18_is_not_surfaced_but_stays_in_the_ledger() -> None:
    assert RULE_CHILDREN_10_IN_5_OR_11 in REMOVED_FROM_MANIFEST
    assert RULE_CHILDREN_10_IN_5_OR_11 not in {
        r.rule_id for r in ACTIVE_PRODUCTION_RELEASE.manifest.rules
    }
    ledger = {i.interpretation_id for i in ACTIVE_PRODUCTION_RELEASE.registry.interpretations}
    assert "bphs.karmeshas-phala.10th-lord.5-or-11.children.interpretation.v1" in ledger
    assert rule_weight(RULE_CHILDREN_10_IN_5_OR_11) == "secondary"
    service = _service()
    result = service.answer(
        DeterministicAnalysisRequest(
            birth_input=_birth("1985-01-01", "12:00:00"),
            as_of=_AS_OF,
            question="What does my chart say about children?",
        )
    )
    cited = {item.rule_id for s in result.selections for item in s.selected_matched}
    cited |= {item.rule_id for s in result.selections for item in s.relevant_unmatched}
    assert {r for r in cited if r.endswith(".children.v1")} == {
        "bphs.d1.house_lord.5.in_11.children.v1",
        "bphs.d1.house_lord.11.in_2_or_5.children.v1",
    }
    assert RULE_CHILDREN_10_IN_5_OR_11 not in cited


def test_item_23_relabels_the_travel_domain() -> None:
    from test_interpretation_evidence import _BUILDER, _governed_items, _selection

    from astrologer.application.detailed_answer import DetailedAnswerBuilder
    from astrologer.questions.models import QuestionDomain

    facts = FactSet(facts=(Fact(fact_id="jyotish.d1.house_lord.6.placement_house", value=10),))
    evidence = _BUILDER.build(_selection(QuestionDomain.TRAVEL, _governed_items(facts)))
    answer = DetailedAnswerBuilder().build(evidence)
    assert answer.evidence
    assert answer.answer == (
        "Your D1 chart contains reviewed contextual evidence relevant to Residence away from "
        "birthplace."
    )


def test_weights_are_display_order_only() -> None:
    assert set(SECONDARY_RULES.values()) and all(
        "Sitting 1 item" in v for v in SECONDARY_RULES.values()
    )
    for rule_id in SECONDARY_RULES:
        assert rule_weight(rule_id) == "secondary"
        assert rule_weight(f"{rule_id}@v1") == "secondary"
    assert rule_weight("bphs.d1.house_lord.10.equals_9.v1") == "primary"
    items = ["bphs.d1.house_lord.10.equals_9.friends.v1", "x.primary.a", "x.primary.b"]
    assert primary_first(items, lambda item: item) == ("x.primary.a", "x.primary.b", items[0])
    # Weight never enters a rule, a hash input or an evaluation.
    assert "weight" not in ACTIVE_PRODUCTION_RELEASE.envelopes[0].model_dump()


def test_secondary_rules_are_labelled_supporting_and_shown_after_primary_ones() -> None:
    # A synthetic chart whose 5th lord is in the 11th: Children (item 16, secondary).
    from test_interpretation_evidence import _BUILDER, _governed_items, _selection

    from astrologer.application.detailed_answer import DetailedAnswerBuilder
    from astrologer.questions.models import QuestionDomain

    facts = FactSet(
        facts=(
            Fact(fact_id="jyotish.d1.house_lord.5.placement_house", value=11),
            Fact(fact_id="jyotish.d1.house_lord.11.placement_house", value=2),
        )
    )
    evidence = _BUILDER.build(_selection(QuestionDomain.CHILDREN, _governed_items(facts)))
    answer = DetailedAnswerBuilder().build(evidence)
    assert [e.weight for e in answer.evidence] == ["secondary", "secondary"]
    assert all(why.startswith("Supporting: ") for why in answer.why_it_applies)
    # Reviewed statements are quoted unchanged.
    assert set(answer.reviewed_interpretations) == {
        item.reviewed_statement for item in evidence.selected_matched
    }


# --- Sitting 1 items 1 and 2: timing v3 --------------------------------------------------------


def test_timing_v3_carries_the_reviewer_wording_and_v2_is_unchanged() -> None:
    release = get_active_timing_release()
    assert release is PRODUCTION_CAREER_TIMING_RELEASE_V3
    v87, v140 = (source.reviewed_interpretation for source in release.sources)
    assert v87 == V87_REVIEWED_INTERPRETATION_ADMIT02
    assert v140 == V140_REVIEWED_INTERPRETATION_ADMIT02
    assert (
        "associated with authority, position, office or status-related results during the "
        "lord's Dasha, subject to the overall strength and condition of the 10th lord and the "
        "chart" in v87
    )
    assert "It does not guarantee employment, promotion, office, authority" in v87
    assert "rājya-lābha, gain or benefit connected with authority, position or status" in v140
    # v2 keeps its admitted wording; the rules and conditions are the same objects.
    assert PRODUCTION_CAREER_TIMING_RELEASE_V2.sources == (
        TimingSourceRecord(),
        MoonVenusOwnExaltationTimingSourceRecord(),
    )
    assert release.rules == PRODUCTION_CAREER_TIMING_RELEASE_V2.rules
    # v.140 stays conjunctive: Moon MD AND Venus AD AND Venus own/exalted (Sitting 1 item 2).
    assert release.sources[1].scope == (
        "Moon MD / Venus AD",
        "D1 Venus own-sign OR exaltation-sign only",
    )


def test_mahadasha_only_rule_is_never_applied_to_an_antardasha() -> None:
    # v.87 takes the Mahadasha only: the evaluator has no Antardasha input at all.
    assert "antardasha" not in inspect.signature(CareerTimingRuleEvaluator.evaluate).parameters
    natal = NatalTimingCondition(tenth_house_lord=DashaLord.JUPITER, placement_house=4)
    md = MahadashaTimingCondition(
        lord=DashaLord.SATURN, start=_AS_OF, end=datetime(2040, 1, 1, tzinfo=UTC)
    )
    rule = get_active_timing_release().rules[0]
    assert isinstance(rule, CareerTimingRule)
    assert CareerTimingRuleEvaluator().evaluate(rule, natal, md).status is TimingRuleStatus.FALSE
    # Over 35 years, the 10th lord's Antardashas inside other Mahadashas never give a v.87 window.
    birth = BirthInput(
        birth_date="1978-01-01", birth_time="12:00:00", timezone="UTC", latitude=0, longitude=0
    )
    result = CareerTimingAnalysisService(SwissEphemerisProvider()).analyze(
        CareerTimingRequest(
            birth_input=birth,
            domain="career",
            as_of=_AS_OF,
            horizon_end=datetime(2061, 1, 1, tzinfo=UTC),
        )
    )
    v87 = [w for w in result.windows if w.rule_id.endswith("10th_lord.in_4.md.v1")]
    assert v87 and all(w.antardasha_lord is None for w in v87)
    assert {w.mahadasha_lord for w in v87} == {DashaLord.JUPITER}


# --- Sitting 2 items 1–10, 17, 30; Sitting 1 items 26–28 ---------------------------------------


def test_signification_v3_glosses_keep_the_sanskrit() -> None:
    corpus = ACTIVE_SIGNIFICATION_CORPUS
    assert corpus.version == "jyotish.signification.production@v3"
    displays = {t.sanskrit: t.display for e in corpus.entries for t in e.terms}
    assert displays["राजकुमारः"] == "heir, successor or senior/deputy role"
    assert displays["सेना"] == "forces, personnel or organized workforce"
    assert displays["विक्रम"] == "courage, initiative or enterprise"
    assert displays["राजा"] == "head, authority or governing role"
    assert displays["राज्य"] == "authority or office"
    assert displays["भृत्य"] == "employees or staff"
    assert displays["शत्रु"] == "adversaries, opposition, competition"
    # Corpus v2 is unchanged (no 6th house, old glosses).
    assert SIGNIFICATION_MANIFEST_V2.manifest_version == "v2"
    v2 = {t.sanskrit: t.display for e in SIGNIFICATION_MANIFEST_V2.entries for t in e.terms}
    assert v2["सेना"] == "army or forces" and "शत्रु" not in v2


def test_x18_v2_is_a_labelled_convention_with_md_primary_ad_secondary() -> None:
    principle = ACTIVE_SIGNIFICATION_CORPUS.lordship_principle
    assert principle is LORDSHIP_PRINCIPLE_V2
    assert principle.approved_template_version == "period-themes-v2"
    assert principle.scope == "MAHADASHA_PRIMARY_ANTARDASHA_SECONDARY"
    assert X18_BASIS_LABEL == (
        "project interpretive convention, reviewer-approved; no source verse identified"
    )
    assert X18_BASIS_LABEL in principle.source_locator


def test_dignity_is_a_calculated_modifier_that_never_changes_a_result() -> None:
    facts: dict[str, object] = {
        "jyotish.d1.house.10.lord": "mars",
        "jyotish.d1.planet.mars.own_sign": True,
        "jyotish.d1.planet.mars.exaltation_sign": False,
        "jyotish.d1.planet.mars.debilitation_sign": False,
    }
    found = lord_dignity(facts, 10)
    assert found is not None
    assert found.text == f"{DIGNITY_PREFIX}: your 10th lord, Mars, is in its own sign."
    assert EVALUATIVE_LANGUAGE.search(found.text) is None
    debilitated = {**facts, "jyotish.d1.planet.mars.own_sign": False}
    debilitated["jyotish.d1.planet.mars.debilitation_sign"] = True
    assert lord_dignity(debilitated, 10).text.endswith("is in its debilitation sign.")  # type: ignore[union-attr]
    # UNKNOWN is never FALSE: a missing dignity fact gives no line at all.
    assert lord_dignity({k: v for k, v in facts.items() if "exaltation" not in k}, 10) is None
    # The reviewed natal statement is the same whatever the dignity (never inverted).
    answer = _answer(TENTH_LORD_IN[6], 2028)
    natal = next(s for s in answer.consultation_sections if s.kind == "natal")
    assert STATEMENT_10_IN_6_OR_12 in natal.text
    assert natal.text.count(DIGNITY_PREFIX) == 1
    assert natal.text.index(STATEMENT_10_IN_6_OR_12) < natal.text.index(DIGNITY_PREFIX)


def test_seventh_house_part_of_v72_is_paused() -> None:
    assert RULE_IN_2_3_OR_7 in REMOVED_FROM_MANIFEST
    assert WITHHELD_WORDING_RULE_IDS == {RULE_IN_8, RULE_IN_7}
    for house in (2, 3):
        assert _status(RULE_IN_2_OR_3, house) is EvaluationStatus.TRUE
    assert _status(RULE_IN_2_OR_3, 7) is EvaluationStatus.FALSE
    assert _status(RULE_IN_7, 7) is EvaluationStatus.TRUE
    assert "seventh" not in _interpretation(RULE_IN_2_OR_3).statement
    answer = _answer(TENTH_LORD_IN[7], 2028)
    sections = {s.kind: s.text for s in answer.consultation_sections}
    assert STATEMENT_IN_7_PAUSED in sections["natal"]
    assert "a reviewed indication exists; wording pending source verification" in sections["glance"]
    assert "high-minded" not in " ".join(sections.values())


def test_v71_printed_reading_is_recorded() -> None:
    passage = next(
        p
        for p in ACTIVE_PRODUCTION_RELEASE.registry.passages
        if p.passage_id == PASSAGE_IN_1_READING
    )
    assert passage.ambiguity_notes is not None
    assert "कर्मेशाधिपतौ" in passage.ambiguity_notes
    assert _interpretation("bphs.d1.house_lord.10.equals_1.v1").passage_id == PASSAGE_IN_1_READING


def test_period_themes_compact_form_with_one_closing() -> None:
    answer = _answer(TENTH_LORD_IN[6], 2028)
    themes = next(s for s in answer.consultation_sections if s.kind == "period_themes")
    assert themes.text.count(PERIOD_THEMES_CLOSING_V2) == 1
    assert themes.text.endswith(PERIOD_THEMES_CLOSING_V2)
    assert "This does not predict an event or an outcome." not in themes.text
    # NEXT-PROPERTY-01: every Mahadasha line is labelled primary.
    assert themes.text.startswith(
        "Moon Mahadasha (primary) (throughout 2028): reviewed themes — Moon: "
    )
    assert "Rahu Antardasha (secondary) (Jan 1–" in themes.text
    assert "6th house (adversaries, opposition, competition)" in themes.text


# --- held / paused -------------------------------------------------------------------------------


def test_held_items_are_not_admitted() -> None:
    # P1–P6 are held (P5 cannot meet the verdict with the packet's wording: see the record).
    timing_ids = {str(rule.rule_id) for rule in get_active_timing_release().rules}
    assert timing_ids == {
        "bphs.timing.vimshottari.career.10th_lord.in_4.md.v1",
        "bphs.timing.vimshottari.career.moon_md.venus_ad.own_or_exaltation.v1",
    }
    static_ids = " ".join(r.rule_id for r in ACTIVE_PRODUCTION_RELEASE.manifest.rules)
    for fragment in ("house_lord.9.", "exchange", "joined", "4_10", "dasha"):
        assert fragment not in static_ids


def _service() -> AskJyotAIService:
    provider = SwissEphemerisProvider()
    return AskJyotAIService(
        DeterministicAnalysisService(DeterministicAstrologyContextService(provider)),
        InterpretationEvidenceBuilder(),
        DeterministicAnswerComposer(),
        CareerTimingAnalysisService(provider),
    )
