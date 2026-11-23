"""career-synthesis-v1: deterministic co-references between reviewed claims and Dasha periods.

All birth inputs are synthetic (lat/long 0, UTC); none describes a real person.
"""

import re
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from astrologer.application.analyze import (
    DeterministicAnalysisRequest,
    DeterministicAnalysisService,
)
from astrologer.application.answer import AskJyotAIService
from astrologer.application.career_synthesis import (
    OUT_OF_SCOPE,
    WHY_FRAMING,
    co_reference_sentence,
    why_section,
    year_limit_sentence,
)
from astrologer.application.context import DeterministicAstrologyContextService
from astrologer.astrology.derived_facts import DerivedFactsEngine
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.birth.models import BirthInput
from astrologer.composition import DeterministicAnswerComposer
from astrologer.composition.career_claims import ClaimKind
from astrologer.composition.models import CareerSynthesis, DetailedComposedAnswer, SynthesisLink
from astrologer.evidence import InterpretationEvidenceBuilder
from astrologer.timing_rules.service import CareerTimingAnalysisService

_AS_OF = datetime(2026, 1, 1, tzinfo=ZoneInfo("Asia/Kolkata"))
_QUESTION = "How will my career be in 2027?"

# 10th lord Jupiter is also the 2027 Mahadasha lord.
TENTH_LORD_IS_PERIOD_LORD = BirthInput(
    birth_date="1978-01-01", birth_time="12:00:00", timezone="UTC", latitude=0, longitude=0
)
# 10th lord Mars (in the 11th) is not a period lord; Jupiter Antardasha rules the 11th.
SHARED_HOUSE_ONLY = BirthInput(
    birth_date="1988-02-28", birth_time="06:00:00", timezone="UTC", latitude=0, longitude=0
)
# 10th lord Saturn (in the 11th); no 2027 period lord shares a planet, house, or period.
NO_CO_REFERENCE = BirthInput(
    birth_date="1995-11-05", birth_time="18:00:00", timezone="UTC", latitude=0, longitude=0
)

# Causal or evaluative connectives that must never appear in synthesis prose.
FORBIDDEN_CONNECTIVES: tuple[str, ...] = (
    "activates",
    "activate",
    "activation",
    "triggers",
    "trigger",
    "therefore",
    "thus",
    "hence",
    "because of the dasha",
    "because",
    "due to",
    "strengthens",
    "strengthen",
    "weakens",
    "delivers",
    "deliver",
    "brings",
    "bring",
    "results in",
    "leads to",
    "causes",
    "boosts",
    "enhances",
    "supports",
    "confirms",
    "favorable",
    "favourable",
    "unfavorable",
    "auspicious",
    "inauspicious",
    "good",
    "bad",
    "positive",
    "negative",
    "strong",
    "weak",
    "promising",
    "fruitful",
)


def _forbidden_in(text: str) -> list[str]:
    lowered = text.lower()
    return [word for word in FORBIDDEN_CONNECTIVES if re.search(rf"\b{re.escape(word)}\b", lowered)]


def _service() -> AskJyotAIService:
    provider = SwissEphemerisProvider()
    return AskJyotAIService(
        DeterministicAnalysisService(DeterministicAstrologyContextService(provider)),
        InterpretationEvidenceBuilder(),
        DeterministicAnswerComposer(),
        CareerTimingAnalysisService(provider),
    )


def _answer(birth: BirthInput) -> DetailedComposedAnswer:
    request = DeterministicAnalysisRequest(birth_input=birth, as_of=_AS_OF, question=_QUESTION)
    return _service().answer(request).answers[0]


def _synthesis(answer: DetailedComposedAnswer) -> CareerSynthesis:
    plan = answer.career_answer_plan
    assert plan is not None and plan.synthesis is not None
    return plan.synthesis


@pytest.fixture(scope="module")
def answers() -> dict[str, DetailedComposedAnswer]:
    return {
        "period_lord": _answer(TENTH_LORD_IS_PERIOD_LORD),
        "shared_house": _answer(SHARED_HOUSE_ONLY),
        "none": _answer(NO_CO_REFERENCE),
    }


def test_tenth_lord_as_mahadasha_lord_is_a_same_planet_link(
    answers: dict[str, DetailedComposedAnswer],
) -> None:
    answer = answers["period_lord"]
    synthesis = _synthesis(answer)
    planet = [link for link in synthesis.links if link.link_type == "SAME_PLANET"]
    assert {link.claim_id for link in planet} == set(synthesis.reviewed_claim_ids)
    for link in planet:
        assert link.shared_reference == "planet:jupiter"
        assert (link.period_role, link.period_lord) == ("Mahadasha", "Jupiter")
        assert "jyotish.d1.house.10.lord" in link.claim_fact_ids
        assert link.dasha_fact_ids == (
            "jyotish.dasha_linkage.v1.lord.jupiter.ruled_houses",
            "jyotish.dasha_linkage.v1.lord.jupiter.is_tenth_lord",
        )
        # The production Dasha corpus admits no rules: the calculation method is provenance.
        assert link.dasha_rule_ids == ()
        assert link.calc_method_ids == ("jyotish.dasha_linkage.v1",)
        # The Mahadasha spans both 2027 segments; the link names both.
        assert len(link.segment_ids) == 2
    # Jupiter is already a SAME_PLANET link, so its 10th/4th houses are not repeated.
    assert not [link for link in synthesis.links if link.link_type == "SAME_HOUSE"]


def test_timing_window_overlapping_each_segment_is_a_same_period_link(
    answers: dict[str, DetailedComposedAnswer],
) -> None:
    answer = answers["period_lord"]
    synthesis = _synthesis(answer)
    plan = answer.career_answer_plan
    assert plan is not None
    period = [link for link in synthesis.links if link.link_type == "SAME_PERIOD"]
    timing_claims = {
        claim.claim_id
        for claim in answer.claim_ledger.claims  # type: ignore[union-attr]
        if claim.kind is ClaimKind.APPROVED_TIMING_INTERPRETATION
    }
    assert {link.claim_id for link in period} == timing_claims
    assert [link.segment_ids[0] for link in period] == [
        segment.segment_id for segment in plan.dasha_segments
    ]
    assert all(link.dasha_rule_ids == () for link in period)
    assert all(link.calc_method_ids == ("vimshottari-v1",) for link in period)
    # Natal claims carry no window, so they never form SAME_PERIOD links.
    natal_ids = set(synthesis.reviewed_claim_ids) - timing_claims
    assert not [link for link in period if link.claim_id in natal_ids]


def test_tenth_lord_not_a_period_lord_can_still_share_a_house(
    answers: dict[str, DetailedComposedAnswer],
) -> None:
    synthesis = _synthesis(answers["shared_house"])
    assert [link.link_type for link in synthesis.links] == ["SAME_HOUSE"]
    link = synthesis.links[0]
    assert link.shared_reference == "house:11"
    assert (link.period_role, link.period_lord) == ("Antardasha", "Jupiter")
    assert link.dasha_fact_ids == ("jyotish.dasha_linkage.v1.lord.jupiter.ruled_houses",)
    assert link.claim_fact_ids == ("jyotish.d1.house_lord.10.placement_house",)


def test_no_co_reference_is_stated_as_absence_not_as_negative_evidence(
    answers: dict[str, DetailedComposedAnswer],
) -> None:
    answer = answers["none"]
    synthesis = _synthesis(answer)
    assert synthesis.reviewed_claim_ids and not synthesis.links
    section = next(s for s in answer.consultation_sections if s.kind == "why")
    assert "No shared planet, house, or period was found" in section.text
    assert "among the calculated links" in section.text
    assert "not evidence for or against any indication" in section.text
    assert answer.consultation_sections[0].text == (
        "For 2027, no reviewed Career timing rule matched. No 2027 period lord shares a "
        "calculated planet or house with the reviewed indication about your 10th lord's "
        "placement. No reviewed rule establishes a specific Career event in 2027."
    )


def test_every_link_cites_both_sides_and_only_existing_ids(
    answers: dict[str, DetailedComposedAnswer],
) -> None:
    for answer in answers.values():
        plan = answer.career_answer_plan
        assert plan is not None and plan.synthesis is not None
        claims = {c.claim_id: c for c in answer.claim_ledger.claims}  # type: ignore[union-attr]
        linkage_ids = {
            fact.fact_id
            for item in plan.dasha_linkages
            for lord in (item.linkage.mahadasha, item.linkage.antardasha)
            for fact in lord.facts
        }
        segment_ids = {segment.segment_id for segment in plan.dasha_segments}
        for link in plan.synthesis.links:
            claim = claims[link.claim_id]
            assert claim.claim_id in plan.matched_claim_ids
            assert link.claim_rule_ids == claim.rule_ids
            assert set(claim.fact_ids) <= set(link.claim_fact_ids)
            assert all(rule_id not in link.text for rule_id in link.claim_rule_ids)
            assert link.claim_id not in link.text
            assert set(link.dasha_fact_ids) <= linkage_ids | segment_ids
            assert set(link.segment_ids) <= segment_ids
            assert link.calc_method_ids


def test_synthesis_adds_no_facts_or_rules(answers: dict[str, DetailedComposedAnswer]) -> None:
    """Structural synthesis cites existing facts and rules; it never introduces new ones."""
    for birth, answer in zip(
        (TENTH_LORD_IS_PERIOD_LORD, SHARED_HOUSE_ONLY, NO_CO_REFERENCE),
        answers.values(),
        strict=True,
    ):
        plan = answer.career_answer_plan
        assert plan is not None and plan.synthesis is not None
        chart = _service()._analysis_service.d1_chart(
            DeterministicAnalysisRequest(birth_input=birth, as_of=_AS_OF, question=_QUESTION)
        )
        derived = {fact.fact_id for fact in DerivedFactsEngine().calculate(chart).facts}
        ledger = answer.claim_ledger
        assert ledger is not None
        ledger_facts = {fid for claim in ledger.claims for fid in claim.fact_ids}
        ledger_rules = {rid for claim in ledger.claims for rid in claim.rule_ids}
        for link in plan.synthesis.links:
            assert set(link.claim_fact_ids) <= ledger_facts | derived
            assert set(link.claim_rule_ids) <= ledger_rules


def test_synthesis_is_deterministic() -> None:
    assert _synthesis(_answer(TENTH_LORD_IS_PERIOD_LORD)) == _synthesis(
        _answer(TENTH_LORD_IS_PERIOD_LORD)
    )


def test_out_of_scope_records_missing_polarity(
    answers: dict[str, DetailedComposedAnswer],
) -> None:
    for answer in answers.values():
        synthesis = _synthesis(answer)
        assert synthesis.out_of_scope == OUT_OF_SCOPE
        assert any("polarity" in item for item in synthesis.out_of_scope)


def test_why_section_follows_direct_and_carries_its_links(
    answers: dict[str, DetailedComposedAnswer],
) -> None:
    answer = answers["period_lord"]
    kinds = [section.kind for section in answer.consultation_sections]
    assert kinds[:2] == ["direct", "why"]
    section = answer.consultation_sections[1]
    assert section.synthesis_links == _synthesis(answer).links
    assert section.framing == WHY_FRAMING
    assert section.text.endswith(WHY_FRAMING)


def test_year_limit_sentence_only_when_plan_carries_it() -> None:
    assert year_limit_sentence(2027, ()) is None
    assert year_limit_sentence(2027, ("career-year-outcome-unestablished",)) == (
        "No reviewed rule establishes a specific Career event in 2027."
    )


def test_empty_synthesis_says_nothing_to_compare() -> None:
    synthesis = CareerSynthesis(year=2027, out_of_scope=OUT_OF_SCOPE)
    section = why_section(synthesis)
    assert "No reviewed Career indication applies to 2027" in section.text
    assert section.synthesis_sentences == ()
    assert co_reference_sentence(synthesis).text == "No reviewed Career indication applies."


@pytest.mark.parametrize("word", ["activates", "triggers", "therefore", "brings"])
def test_blocklist_detects_forbidden_connectives(word: str) -> None:
    assert _forbidden_in(f"Jupiter {word} the indication.") == [word]
    assert _forbidden_in("Saturn is also the Antardasha lord.") == []


def test_synthesis_prose_uses_no_causal_or_evaluative_connectives(
    answers: dict[str, DetailedComposedAnswer],
) -> None:
    texts: list[str] = [WHY_FRAMING]
    for answer in answers.values():
        synthesis = _synthesis(answer)
        claims = answer.claim_ledger.claims  # type: ignore[union-attr]
        plan = answer.career_answer_plan
        assert plan is not None
        texts.append(answer.consultation_sections[0].text)
        texts.append(co_reference_sentence(synthesis, claims).text)
        texts.append(why_section(synthesis).text)
        texts.extend(link.text for link in synthesis.links)
    texts.append(why_section(CareerSynthesis(year=2027)).text)
    for text in texts:
        assert _forbidden_in(text) == [], text


def test_link_model_rejects_a_one_sided_citation() -> None:
    with pytest.raises(ValueError):
        SynthesisLink(
            link_type="SAME_PLANET",
            claim_id="c",
            claim_label="the reviewed indication about your 10th lord's placement",
            claim_fact_ids=("f",),
            claim_rule_ids=("r",),
            dasha_fact_ids=(),
            calc_method_ids=("jyotish.dasha_linkage.v1",),
            segment_ids=("s",),
            shared_reference="planet:jupiter",
            text="t",
        )


def test_node_period_lord_links_only_through_calculated_placement() -> None:
    """Rahu has no sign rulership under the convention; only its KNOWN placement can link."""
    birth = BirthInput(
        birth_date="1990-03-10", birth_time="18:00:00", timezone="UTC", latitude=0, longitude=0
    )
    synthesis = _synthesis(_answer(birth))
    assert synthesis.links
    for link in synthesis.links:
        assert link.period_lord == "Rahu"
        assert link.link_type == "SAME_HOUSE"
        assert link.dasha_fact_ids == ("jyotish.dasha_linkage.v1.lord.rahu.placement_house",)
        assert "occupies your 6th house" in link.text
