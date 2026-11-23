"""NEXT-DASHA-01: Dasha context section, review-gated slot, and follow-up path.

All profiles are synthetic (noon UTC at 0, 0); expected values are read from the engine and
derived facts in-test, never hand-typed.
"""

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from test_dasha_linkage import blocklisted_terms

from astrologer.application.analyze import (
    DeterministicAnalysisRequest,
    DeterministicAnalysisService,
)
from astrologer.application.answer import AskJyotAIService
from astrologer.application.context import DeterministicAstrologyContextService
from astrologer.application.dasha_context import (
    DASHA_CONTEXT_FRAMING,
    DASHA_CONTEXT_REVIEWED_FRAMING,
)
from astrologer.astrology.chart import ChartEngine
from astrologer.astrology.dasha import DashaLord, VimshottariDashaEngine
from astrologer.astrology.dasha_linkage import LinkageStatus, to_segment_fact_set
from astrologer.astrology.derived_facts import DerivedFactsEngine
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.birth.models import BirthInput
from astrologer.composition import DeterministicAnswerComposer
from astrologer.composition.models import (
    CareerAnswerPlan,
    ConsultationSection,
    DetailedComposedAnswer,
)
from astrologer.evidence import InterpretationEvidenceBuilder
from astrologer.knowledge.corpus import (
    ManifestRule,
    ProductionCorpusLoadError,
    ProductionCorpusManifest,
    envelope_sha256,
)
from astrologer.knowledge.dasha_interpretation import (
    ACTIVE_DASHA_INTERPRETATION_CORPUS,
    DASHA_INTERPRETATION_FACT_CONTRACT,
    EMPTY_DASHA_INTERPRETATION_MANIFEST,
    DashaInterpretationCorpus,
    admit_dasha_interpretation_corpus,
)
from astrologer.knowledge.models import (
    ChartScope,
    EvidenceDirection,
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
)
from astrologer.rules.models import (
    ConditionDefinition,
    ConditionKind,
    ConditionOperation,
    RuleDefinition,
    RuleEffect,
)
from astrologer.timing_rules.service import CareerTimingAnalysisService

_ZONE = ZoneInfo("Asia/Kolkata")
_AS_OF = datetime(2026, 1, 1, tzinfo=_ZONE)
_QUESTION = "How will my career be in 2027?"
# Synthetic: shared with test_career_consultation.py (Jupiter MD in 2027).
_REFERENCE = BirthInput(
    birth_date="1978-01-01", birth_time="12:00:00", timezone="UTC", latitude=0, longitude=0
)
# Synthetic: chosen because the engine places it in Rahu MD throughout 2027.
_RAHU = BirthInput(
    birth_date="1965-01-01", birth_time="12:00:00", timezone="UTC", latitude=0, longitude=0
)
_NO_SIGNIFICANCE = (
    "no significance",
    "not significant",
    "insignificant",
    "no effect",
    "irrelevant",
    "does not matter",
    "meaningless",
)
_REVIEWED_AT = datetime(2026, 11, 1, tzinfo=UTC)
_FIXTURE_WORDING = "Synthetic reviewed Dasha interpretation fixture, not astrology doctrine."


def _service(corpus: DashaInterpretationCorpus | None = None) -> AskJyotAIService:
    provider = SwissEphemerisProvider()
    return AskJyotAIService(
        DeterministicAnalysisService(DeterministicAstrologyContextService(provider)),
        InterpretationEvidenceBuilder(),
        DeterministicAnswerComposer(),
        CareerTimingAnalysisService(provider),
        dasha_interpretation_corpus=corpus,
    )


def _answer(
    birth: BirthInput = _REFERENCE, corpus: DashaInterpretationCorpus | None = None
) -> tuple[DetailedComposedAnswer, CareerAnswerPlan, ConsultationSection]:
    answer = (
        _service(corpus)
        .answer(DeterministicAnalysisRequest(birth_input=birth, as_of=_AS_OF, question=_QUESTION))
        .answers[0]
    )
    plan = answer.career_answer_plan
    assert plan is not None
    sections = [s for s in answer.consultation_sections if s.kind == "dasha_context"]
    assert len(sections) == 1
    return answer, plan, sections[0]


def _linkage_fact_ids(plan: CareerAnswerPlan) -> set[str]:
    """Linkage fact ids, plus the existing D1 10th-lord fact id the linkage is sourced from."""
    known = {fact_id for item in plan.dasha_linkages for fact_id in item.linkage.fact_ids()}
    for item in plan.dasha_linkages:
        if item.tenth_lord is None:
            continue
        for lord in (item.linkage.mahadasha, item.linkage.antardasha):
            assert item.tenth_lord.fact_id in lord.fact("is_tenth_lord").source_fact_ids
        known.add(item.tenth_lord.fact_id)
    return known


def section_is_fact_backed(section: ConsultationSection, known_fact_ids: set[str]) -> bool:
    """True only if the section is fact-backed sentences plus framing and admitted wording."""
    if section.framing not in (DASHA_CONTEXT_FRAMING, DASHA_CONTEXT_REVIEWED_FRAMING):
        return False
    if not section.fact_sentences:
        return False
    for sentence in section.fact_sentences:
        if not sentence.fact_ids or not set(sentence.fact_ids) <= known_fact_ids:
            return False
    head = " ".join([*(s.text for s in section.fact_sentences), section.framing])
    if section.framing == DASHA_CONTEXT_FRAMING:
        return section.text == head and not section.interpretation_rule_ids
    return section.text.startswith(head + " ") and bool(section.interpretation_rule_ids)


# --- Reference 2027 case -------------------------------------------------------------------


def test_reference_2027_segments_come_from_the_engine() -> None:
    _, plan, _ = _answer()
    chart = ChartEngine(SwissEphemerisProvider()).calculate(_REFERENCE)
    end = datetime(2028, 1, 1, tzinfo=_ZONE)
    start = datetime(2027, 1, 1, tzinfo=_ZONE)
    expected = [
        (major.lord.value, minor.lord.value)
        for major in VimshottariDashaEngine().calculate(chart, end).mahadashas
        for minor in major.antardashas
        if minor.start < end and minor.end > start
    ]
    assert [(s.mahadasha_lord, s.antardasha_lord) for s in plan.dasha_segments] == expected
    assert [item.segment_id for item in plan.dasha_linkages] == [
        s.segment_id for s in plan.dasha_segments
    ]
    # The spec's stated reference periods, confirmed from the engine rather than trusted.
    assert expected == [("jupiter", "moon"), ("jupiter", "mars")]


def test_reference_linkage_values_match_in_test_derived_facts() -> None:
    _, plan, section = _answer()
    chart = ChartEngine(SwissEphemerisProvider()).calculate(_REFERENCE)
    facts = {f.fact_id: f.value for f in DerivedFactsEngine().calculate(chart).facts}
    for item in plan.dasha_linkages:
        for lord_linkage in (item.linkage.mahadasha, item.linkage.antardasha):
            lord = lord_linkage.lord.value
            placement = facts[f"jyotish.d1.planet.{lord}.placement_house"]
            ruled = tuple(h for h in range(1, 13) if facts[f"jyotish.d1.house.{h}.lord"] == lord)
            assert lord_linkage.fact("ruled_houses").value == ruled
            assert lord_linkage.fact("placement_house").value == placement
            assert lord_linkage.fact("is_tenth_lord").value is (
                facts["jyotish.d1.house.10.lord"] == lord
            )
            assert (
                lord_linkage.fact("aspects_tenth_house").value
                is (facts[f"jyotish.d1.aspect.{lord}.house.10"])
            )
            # Each lord's ruled houses and placement are named in the section.
            for house in ruled:
                assert f"{house}" in section.text
        assert isinstance(item.linkage.ad_house_from_md.value, int)
    assert section_is_fact_backed(section, _linkage_fact_ids(plan))


def test_section_follows_chronology_and_appears_once_in_the_answer() -> None:
    answer, _, section = _answer()
    kinds = [s.kind for s in answer.consultation_sections]
    assert kinds == ["direct", "dasha", "dasha_context", "timing", "limit"]
    assert answer.answer.count(section.text) == 1
    assert answer.answer == " ".join(s.text for s in answer.consultation_sections)


# --- Rahu MD case ----------------------------------------------------------------------------


def test_rahu_mahadasha_keeps_aspects_unknown_end_to_end() -> None:
    _, plan, section = _answer(_RAHU)
    assert plan.dasha_segments and all(s.mahadasha_lord == "rahu" for s in plan.dasha_segments)
    rahu = plan.dasha_linkages[0].linkage.mahadasha
    assert rahu.lord is DashaLord.RAHU
    for name in ("aspects_tenth_house", "aspects_tenth_lord"):
        assert rahu.fact(name).status is LinkageStatus.UNKNOWN  # type: ignore[arg-type]
    assert rahu.fact("ruled_houses").value == ()
    assert "Whether Rahu aspects your 10th house or your 10th lord is unknown" in section.text
    assert "Rahu does not aspect" not in section.text
    assert "Rahu aspects your" not in section.text.replace("Whether Rahu aspects your", "")
    assert "no lordship" not in section.text.lower()
    assert section_is_fact_backed(section, _linkage_fact_ids(plan))


# --- Framing, empty slot, structure, blocklist ----------------------------------------------


@pytest.mark.parametrize("birth", [_REFERENCE, _RAHU])
def test_empty_corpus_gives_one_framing_line_and_an_empty_slot(birth: BirthInput) -> None:
    answer, plan, section = _answer(birth)
    assert ACTIVE_DASHA_INTERPRETATION_CORPUS.rule_keys == ()
    assert plan.dasha_interpretation is not None
    assert plan.dasha_interpretation.claims == ()
    assert plan.dasha_interpretation.corpus_manifest_id == "jyotish.dasha_interpretation.career"
    assert section.framing == DASHA_CONTEXT_FRAMING
    assert answer.answer.count(DASHA_CONTEXT_FRAMING) == 1
    assert section.text.endswith(DASHA_CONTEXT_FRAMING)
    assert "counted from your D1 Lagna" in DASHA_CONTEXT_FRAMING
    assert not section.interpretation_rule_ids
    lowered = section.text.lower()
    assert not [phrase for phrase in _NO_SIGNIFICANCE if phrase in lowered]


def test_structural_check_rejects_any_unbacked_sentence() -> None:
    _, plan, section = _answer()
    known = _linkage_fact_ids(plan)
    assert section_is_fact_backed(section, known)
    extra = section.model_copy(update={"text": section.text + " This period looks promising."})
    assert not section_is_fact_backed(extra, known)
    unknown_id = section.model_copy(
        update={
            "fact_sentences": (
                section.fact_sentences[0].model_copy(update={"fact_ids": ("invented.fact",)}),
                *section.fact_sentences[1:],
            )
        }
    )
    assert not section_is_fact_backed(unknown_id, known)
    no_framing = section.model_copy(update={"framing": "Some other line."})
    assert not section_is_fact_backed(no_framing, known)


@pytest.mark.parametrize("birth", [_REFERENCE, _RAHU])
def test_section_and_linkage_strings_avoid_blocklisted_terms(birth: BirthInput) -> None:
    _, plan, section = _answer(birth)
    assert blocklisted_terms(section.text) == []
    assert blocklisted_terms(" ".join(s.text for s in section.fact_sentences)) == []
    for item in plan.dasha_linkages:
        assert blocklisted_terms(item.linkage.model_dump_json()) == []
    assert blocklisted_terms(DASHA_CONTEXT_FRAMING + DASHA_CONTEXT_REVIEWED_FRAMING) == []


# --- Review-gated slot -----------------------------------------------------------------------


def _review(category: ReviewCategory) -> ReviewRecord:
    return ReviewRecord(
        category=category,
        status=ReviewStatus.REVIEWED,
        reviewer="synthetic-reviewer",
        reviewed_at=_REVIEWED_AT,
    )


def _registry() -> SourceRegistry:
    return SourceRegistry(
        registry_version="synthetic-dasha-registry-v1",
        sources=(
            SourceRecord(
                source_id="synthetic.dasha.source",
                source_version="1",
                kind=SourceKind.PRIMARY,
                title="Synthetic Dasha source fixture",
                original_language="synthetic",
                rights_status=RightsStatus.REFERENCE_ONLY,
            ),
        ),
        passages=(
            SourcePassage(
                passage_id="synthetic.dasha.passage",
                source_id="synthetic.dasha.source",
                locator="fixture 1",
                passage_reference="synthetic reference only",
                review=_review(ReviewCategory.SOURCE_VERIFICATION),
            ),
        ),
        interpretations=(
            ReviewedInterpretation(
                interpretation_id="synthetic.dasha.interpretation",
                interpretation_version="1",
                passage_id="synthetic.dasha.passage",
                translation_applicability=TranslationApplicability.NOT_APPLICABLE,
                statement=_FIXTURE_WORDING,
                review=_review(ReviewCategory.INTERPRETATION_REVIEW),
            ),
        ),
    )


def _envelope(lifecycle: RuleLifecycle = RuleLifecycle.PRODUCTION_ACTIVE) -> ProductionRuleEnvelope:
    fact_id = "jyotish.dasha_linkage.v1.segment.mahadasha.is_tenth_lord"
    condition = ConditionDefinition(
        kind=ConditionKind.LEAF,
        operation=ConditionOperation.EQUALS,
        fact_id=fact_id,
        expected_value=True,
    )
    return ProductionRuleEnvelope(
        rule=RuleDefinition(
            rule_id="synthetic.dasha.md_is_tenth_lord",
            rule_version="1",
            ruleset_version="synthetic-dasha-v1",
            name="Synthetic Dasha fixture rule",
            domain="career",
            condition=condition,
            effect=RuleEffect(effect_key="synthetic.dasha", label="Synthetic fixture only"),
        ),
        lifecycle=lifecycle,
        domain=JyotishDomain.CAREER,
        taxonomy=RuleTaxonomy.NATAL_STRUCTURAL,
        posture=RulePosture.TIMING_REQUIRED,
        evidence_direction=EvidenceDirection.CONTEXTUAL,
        chart_scope=ChartScope.D1_RASHI,
        fact_contract_id=DASHA_INTERPRETATION_FACT_CONTRACT.contract_id,
        fact_contract_version=DASHA_INTERPRETATION_FACT_CONTRACT.contract_version,
        fact_contract_methodology_id=DASHA_INTERPRETATION_FACT_CONTRACT.methodology_id,
        fact_dependencies=(FactDependency(fact_id=fact_id),),
        interpretation_id="synthetic.dasha.interpretation",
        formalization_review=_review(ReviewCategory.FORMALIZATION_REVIEW),
    )


def _manifest(*envelopes: ProductionRuleEnvelope) -> ProductionCorpusManifest:
    return ProductionCorpusManifest(
        manifest_id="synthetic.dasha.manifest",
        manifest_version="1",
        registry_version="synthetic-dasha-registry-v1",
        fact_contract_id=DASHA_INTERPRETATION_FACT_CONTRACT.contract_id,
        fact_contract_version=DASHA_INTERPRETATION_FACT_CONTRACT.contract_version,
        rules=tuple(
            ManifestRule(
                rule_id=item.rule.rule_id,
                rule_version=item.rule.rule_version,
                envelope_sha256=envelope_sha256(item),
            )
            for item in envelopes
        ),
    )


def test_admitted_fixture_rule_fills_the_slot_and_is_stored_on_the_answer() -> None:
    envelope = _envelope()
    corpus = admit_dasha_interpretation_corpus(_manifest(envelope), (envelope,), _registry())
    answer, plan, section = _answer(corpus=corpus)
    # Jupiter (MD in both 2027 segments) is this synthetic chart's 10th lord.
    assert plan.dasha_linkages[0].linkage.mahadasha.fact("is_tenth_lord").value is True
    slot = plan.dasha_interpretation
    assert slot is not None and slot.corpus_manifest_id == "synthetic.dasha.manifest"
    assert [(c.rule_id, c.rule_version) for c in slot.claims] == [
        ("synthetic.dasha.md_is_tenth_lord", "1")
    ] * len(plan.dasha_segments)
    assert {c.segment_id for c in slot.claims} == {s.segment_id for s in plan.dasha_segments}
    assert all(c.permitted_wording == _FIXTURE_WORDING for c in slot.claims)
    assert section.framing == DASHA_CONTEXT_REVIEWED_FRAMING
    assert DASHA_CONTEXT_FRAMING not in answer.answer
    assert answer.answer.count(DASHA_CONTEXT_REVIEWED_FRAMING) == 1
    assert section.interpretation_rule_ids == ("synthetic.dasha.md_is_tenth_lord@1",)
    assert "synthetic.dasha.md_is_tenth_lord v1" in section.text
    assert section_is_fact_backed(section, _linkage_fact_ids(plan))


def test_admitted_rule_that_does_not_match_leaves_the_slot_empty() -> None:
    envelope = _envelope()
    corpus = admit_dasha_interpretation_corpus(_manifest(envelope), (envelope,), _registry())
    _, plan, section = _answer(_RAHU, corpus=corpus)
    assert plan.dasha_interpretation is not None and plan.dasha_interpretation.claims == ()
    assert section.framing == DASHA_CONTEXT_FRAMING


def test_the_same_rule_not_admitted_cannot_fill_the_slot() -> None:
    approved_only = _envelope(RuleLifecycle.APPROVED)
    with pytest.raises(ProductionCorpusLoadError):
        admit_dasha_interpretation_corpus(_manifest(approved_only), (approved_only,), _registry())
    envelope = _envelope()
    with pytest.raises(ProductionCorpusLoadError):  # not on the manifest allowlist
        admit_dasha_interpretation_corpus(_manifest(), (envelope,), _registry())
    with pytest.raises(TypeError):
        DashaInterpretationCorpus(token=object(), manifest=_manifest(), rules=())
    empty = admit_dasha_interpretation_corpus(
        EMPTY_DASHA_INTERPRETATION_MANIFEST.model_copy(
            update={"registry_version": "synthetic-dasha-registry-v1"}
        ),
        (),
        _registry(),
    )
    _, plan, section = _answer(corpus=empty)
    assert plan.dasha_interpretation is not None and plan.dasha_interpretation.claims == ()
    assert section.framing == DASHA_CONTEXT_FRAMING


def test_segment_rule_inputs_are_exactly_the_contract_fact_ids() -> None:
    _, plan, _ = _answer()
    contract = set(DASHA_INTERPRETATION_FACT_CONTRACT.available_fact_ids)
    for item in plan.dasha_linkages:
        produced = {fact.fact_id for fact in to_segment_fact_set(item.linkage).facts}
        assert produced <= contract
    assert not DASHA_INTERPRETATION_FACT_CONTRACT.available_fact_family_prefixes


# --- Period grouping, 10th lord naming, FALSE collapse, UNKNOWN kept separate -------------

_TENTH_FACT_NAMES = (
    "is_tenth_lord",
    "occupies_tenth",
    "aspects_tenth_house",
    "aspects_tenth_lord",
    "same_sign_as_tenth_lord",
)


def _local_date(value: datetime) -> str:
    return f"{value.day} {value.strftime('%b %Y')}"


@pytest.mark.parametrize("birth", [_REFERENCE, _RAHU])
def test_section_is_grouped_by_period_with_dates(birth: BirthInput) -> None:
    _, plan, section = _answer(birth)
    texts = [sentence.text for sentence in section.fact_sentences]
    zone = plan.dasha_segments[0].local_start.tzinfo
    headings = []
    for segment in plan.dasha_segments:
        md_end = (segment.mahadasha_end - timedelta(microseconds=1)).astimezone(zone)
        ad_end = (segment.antardasha_end - timedelta(microseconds=1)).astimezone(zone)
        md = (
            f"{segment.mahadasha_lord.title()} Mahadasha "
            f"({_local_date(segment.mahadasha_start.astimezone(zone))} to {_local_date(md_end)}): "
        )
        if md not in headings:
            headings.append(md)
        headings.append(
            f"{segment.antardasha_lord.title()} Antardasha "
            f"({_local_date(segment.antardasha_start.astimezone(zone))} to {_local_date(ad_end)}): "
        )
    # Exactly one block per Mahadasha and one per Antardasha, in chronological order.
    opened = [text for text in texts if " Mahadasha (" in text or " Antardasha (" in text]
    assert len(opened) == len(headings)
    for heading, text in zip(headings, opened, strict=True):
        assert text.startswith(heading)
    # Each block opens with its lord's ruled-houses sentence.
    for text, sentence in zip(texts, section.fact_sentences, strict=True):
        if text in opened:
            assert sentence.fact_ids[0].endswith(".ruled_houses")


@pytest.mark.parametrize("birth", [_REFERENCE, _RAHU])
def test_tenth_lord_is_named_from_the_existing_d1_house_lord_fact(birth: BirthInput) -> None:
    _, plan, section = _answer(birth)
    chart = ChartEngine(SwissEphemerisProvider()).calculate(birth)
    facts = {f.fact_id: f.value for f in DerivedFactsEngine().calculate(chart).facts}
    tenth = facts["jyotish.d1.house.10.lord"]
    assert all(
        item.tenth_lord is not None
        and item.tenth_lord.fact_id == "jyotish.d1.house.10.lord"
        and item.tenth_lord.value == tenth
        for item in plan.dasha_linkages
    )
    naming = [s for s in section.fact_sentences if s.text.startswith("Your 10th lord is")]
    assert len(naming) == 1
    assert naming[0].text == f"Your 10th lord is {str(tenth).title()}."
    assert naming[0].fact_ids[0] == "jyotish.d1.house.10.lord"
    # An operating lord that IS the 10th lord is stated once, by the naming sentence, which
    # carries its is_tenth_lord citation; its own block does not repeat the clause.
    self_ids = set()
    for item in plan.dasha_linkages:
        for lord in (item.linkage.mahadasha, item.linkage.antardasha):
            fact = lord.fact("is_tenth_lord")
            if fact.value is True:
                self_ids.add(fact.fact_id)
            assert not [
                s
                for s in section.fact_sentences
                if s.text.startswith(f"{lord.lord.value.title()} is your 10th lord")
            ]
            citing = [s for s in section.fact_sentences if fact.fact_id in s.fact_ids]
            assert len({s.text for s in citing}) == 1
    assert set(naming[0].fact_ids[1:]) == self_ids
    assert bool(self_ids) is (birth is _REFERENCE)  # Jupiter MD is the reference 10th lord


@pytest.mark.parametrize("birth", [_REFERENCE, _RAHU])
def test_false_tenth_relationships_collapse_into_one_sentence_citing_every_fact(
    birth: BirthInput,
) -> None:
    _, plan, section = _answer(birth)
    checked = 0
    for item in plan.dasha_linkages:
        for lord in (item.linkage.mahadasha, item.linkage.antardasha):
            false_ids = {
                lord.fact(name).fact_id  # type: ignore[arg-type]
                for name in _TENTH_FACT_NAMES
                if lord.fact(name).status is LinkageStatus.KNOWN  # type: ignore[arg-type]
                and lord.fact(name).value is False  # type: ignore[arg-type]
            }
            if not false_ids:
                continue
            checked += 1
            citing = [s for s in section.fact_sentences if set(s.fact_ids) & false_ids]
            # One summary sentence per block cites them all, and nothing else cites them.
            assert citing
            assert all(set(s.fact_ids) == false_ids for s in citing)
            assert len({s.text for s in citing}) == 1
            assert " not " in citing[0].text or " no " in citing[0].text
    assert checked
    # The Antardasha lords of the reference case are calculated FALSE on all five facts.
    if birth is _REFERENCE:
        assert (
            "Moon is not your 10th lord, does not occupy or aspect your 10th house and has no "
            "aspect or same-sign relationship with Jupiter." in section.text
        )


def test_unknown_facts_are_never_folded_into_the_negative_summary() -> None:
    _, plan, section = _answer(_RAHU)
    rahu = plan.dasha_linkages[0].linkage.mahadasha
    unknown_ids = {
        rahu.fact(name).fact_id  # type: ignore[arg-type]
        for name in _TENTH_FACT_NAMES
        if rahu.fact(name).status is LinkageStatus.UNKNOWN  # type: ignore[arg-type]
    }
    assert unknown_ids == {
        rahu.fact("aspects_tenth_house").fact_id,
        rahu.fact("aspects_tenth_lord").fact_id,
    }
    citing = [s for s in section.fact_sentences if set(s.fact_ids) & unknown_ids]
    assert len(citing) == 1
    assert set(citing[0].fact_ids) == unknown_ids
    assert citing[0].text.startswith("Whether Rahu aspects your 10th house or your 10th lord")
    assert "is unknown" in citing[0].text
    negative = [
        s
        for s in section.fact_sentences
        if s.text.startswith("Rahu ") and "10th" in s.text and "unknown" not in s.text
    ]
    assert len(negative) == 1
    assert not set(negative[0].fact_ids) & unknown_ids
    assert "aspect" not in negative[0].text
