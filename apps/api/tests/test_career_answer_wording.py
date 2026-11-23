"""NEXT-CAREER-02b: plain wording of the Career year answer (deterministic templates only).

The wording pass adds no facts, rules, or doctrine: every sentence is a template over the
existing synthesis links or a verbatim sentence of admitted rule wording.  Ids stay in the
evidence disclosure (links, ledger) and in the sentence-to-fact mapping, never in prose.

All birth inputs are synthetic (lat/long 0, UTC); none describes a real person.
"""

import re
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest

from astrologer.application.analyze import (
    DeterministicAnalysisRequest,
    DeterministicAnalysisService,
)
from astrologer.application.answer import AskJyotAIService
from astrologer.application.career_claims import timing_meaning_and_limit
from astrologer.application.career_synthesis import (
    VIMSHOTTARI_METHODOLOGY_ID,
    WHY_FRAMING,
    _dasha_rule_ids,
    claim_label,
    claim_labels,
    why_sentences,
)
from astrologer.application.consultation import (
    ConsultationRequest,
    ConsultationResponse,
    ConsultationService,
    ConsultationStore,
)
from astrologer.application.context import DeterministicAstrologyContextService
from astrologer.astrology.dasha_linkage import DASHA_LINKAGE_METHODOLOGY_ID
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.birth.models import BirthInput
from astrologer.composition import DeterministicAnswerComposer
from astrologer.composition.career_claims import CareerClaim, ClaimKind, ClaimStatus
from astrologer.composition.models import (
    CareerSynthesis,
    DashaInterpretationClaim,
    DashaInterpretationSlot,
    DetailedComposedAnswer,
    SynthesisLink,
)
from astrologer.evidence import InterpretationEvidenceBuilder
from astrologer.questions.models import CareerQuestionFocus
from astrologer.timing_rules.models import (
    MoonVenusOwnExaltationTimingSourceRecord,
    NinthLordInTenthTimingSourceRecord,
    TimingSourceRecord,
)
from astrologer.timing_rules.service import CareerTimingAnalysisService

_AS_OF = datetime(2026, 1, 1, tzinfo=ZoneInfo("Asia/Kolkata"))
_QUESTION = "How will my career be in 2027?"


def _birth(date: str, time: str) -> BirthInput:
    return BirthInput(birth_date=date, birth_time=time, timezone="UTC", latitude=0, longitude=0)


PROFILES = {
    # 10th lord Jupiter is the 2027 Mahadasha lord; the v1 timing rule matches.
    "period_lord": _birth("1978-01-01", "12:00:00"),
    # No timing match; Jupiter Antardasha rules the 11th, where the 10th lord sits.
    "shared_house": _birth("1988-02-28", "06:00:00"),
    # No 2027 period lord shares a planet, house, or period.
    "none": _birth("1995-11-05", "18:00:00"),
    # Rahu is both the Mahadasha and the Antardasha lord for all of 2027.
    "rahu_rahu": _birth("1990-03-10", "18:00:00"),
}
METHOD_IDS = {
    DASHA_LINKAGE_METHODOLOGY_ID,
    VIMSHOTTARI_METHODOLOGY_ID,
    "career-synthesis-v1",
    # The Period-themes template version is cited as a method, never as a rule (NEXT-SIG-01).
    "period-themes-v1",
}
# Dotted rule/fact ids, ledger claim ids, and methodology ids.
ID_PATTERN = re.compile(
    r"\b[a-z][a-z0-9_]*(?:\.[a-z0-9_@-]+){2,}"
    r"|\bcareer-(?:timing|approved|calculated|insufficient|synthesis)[\w.@-]*"
    r"|\bvimshottari-v\d"
)
_SENTENCES = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")


def _ask() -> AskJyotAIService:
    provider = SwissEphemerisProvider()
    return AskJyotAIService(
        DeterministicAnalysisService(DeterministicAstrologyContextService(provider)),
        InterpretationEvidenceBuilder(),
        DeterministicAnswerComposer(),
        CareerTimingAnalysisService(provider),
    )


@pytest.fixture(scope="module")
def answers() -> dict[str, DetailedComposedAnswer]:
    service = _ask()
    return {
        name: service.answer(
            DeterministicAnalysisRequest(birth_input=birth, as_of=_AS_OF, question=_QUESTION)
        ).answers[0]
        for name, birth in PROFILES.items()
    }


@pytest.fixture
def consultation() -> ConsultationService:
    return ConsultationService(_ask(), ConsultationStore())


def _respond(
    service: ConsultationService,
    birth: BirthInput,
    question: str,
    consultation_id: str | None = None,
    **update: object,
) -> ConsultationResponse:
    request = ConsultationRequest(
        birth_input=birth,
        as_of=datetime(2026, 1, 1, tzinfo=UTC),
        question=question,
        consultation_id=consultation_id,
    )
    return service.respond(request.model_copy(update=update))


def _known_ids(answer: DetailedComposedAnswer) -> set[str]:
    ledger = answer.claim_ledger
    assert ledger is not None
    ids = {claim.claim_id for claim in ledger.claims}
    ids |= {rule_id for claim in ledger.claims for rule_id in claim.rule_ids}
    plan = answer.career_answer_plan
    if plan is not None and plan.synthesis is not None:
        for link in plan.synthesis.links:
            ids |= {*link.claim_rule_ids, *link.dasha_rule_ids, *link.calc_method_ids}
    return ids | METHOD_IDS


def _assert_no_ids(text: str, ids: set[str]) -> None:
    assert ID_PATTERN.search(text) is None, text
    assert not [item for item in ids if item in text], text


def _section(answer: DetailedComposedAnswer, kind: str):  # type: ignore[no-untyped-def]
    return next(section for section in answer.consultation_sections if section.kind == kind)


# --- (a) Direct line --------------------------------------------------------------------------


def test_direct_line_is_two_or_three_plain_sentences(
    answers: dict[str, DetailedComposedAnswer],
) -> None:
    for name, answer in answers.items():
        direct = answer.consultation_sections[0]
        assert direct.kind == "direct"
        assert 2 <= len(direct.synthesis_sentences) <= 3, name
        assert direct.text == " ".join(sentence.text for sentence in direct.synthesis_sentences)
        assert 2 <= len(_SENTENCES.split(direct.text)) <= 3, (name, direct.text)


def test_matched_timing_rule_leads_with_framing_then_verbatim_meaning_and_limit(
    answers: dict[str, DetailedComposedAnswer],
) -> None:
    answer = answers["period_lord"]
    timed = next(
        claim
        for claim in answer.claim_ledger.claims  # type: ignore[union-attr]
        if claim.kind is ClaimKind.APPROVED_TIMING_INTERPRETATION
    )
    meaning, guarantee = timing_meaning_and_limit(timed.permitted_wording)
    sentences = answer.consultation_sections[0].synthesis_sentences
    # NEXT-UX-SUMMARY: the 10th lordship and placement moved to the glance (stated once).
    assert [sentence.text for sentence in sentences] == [
        "Your current Jupiter Mahadasha matches a reviewed BPHS timing rule.",
        meaning,
        guarantee,
    ]
    assert meaning.startswith("In the reviewed BPHS Dasha-phala passage")
    assert guarantee is not None and guarantee.startswith("It does not guarantee")
    # Both are verbatim admitted text and cite their rule in the sentence mapping.
    assert meaning in timed.permitted_wording and guarantee in timed.permitted_wording
    assert sentences[1].rule_ids == sentences[2].rule_ids == timed.rule_ids
    # The full admitted wording still appears exactly once, in the timing section.
    assert answer.answer.count(timed.permitted_wording) == 1
    assert timed.permitted_wording in _section(answer, "timing").text


def test_timing_framing_is_backed_by_calculated_facts_and_admitted_text_is_byte_identical(
    answers: dict[str, DetailedComposedAnswer],
) -> None:
    answer = answers["period_lord"]
    plan = answer.career_answer_plan
    assert plan is not None
    timed = next(
        claim
        for claim in answer.claim_ledger.claims  # type: ignore[union-attr]
        if claim.kind is ClaimKind.APPROVED_TIMING_INTERPRETATION
    )
    framing, meaning, guarantee = answer.consultation_sections[0].synthesis_sentences
    # Byte-identical admitted text: each quoted sentence is a whole sentence of the admitted
    # wording, byte for byte (the first and the non-guarantee sentence).
    admitted = _SENTENCES.split(timed.permitted_wording)
    assert meaning.text.encode() == admitted[0].encode()
    assert guarantee.text.encode() == admitted[-1].encode()
    assert guarantee.text.startswith("It does not guarantee")
    # The framing cites the period's segments; the lordship and placement it used to state
    # are now stated once, in the glance, each backed by its calculated fact.
    lord = next(
        item.linkage.mahadasha
        for item in plan.dasha_linkages
        if item.segment_id in framing.fact_ids
    )
    assert set(framing.fact_ids) == {item.segment_id for item in plan.dasha_linkages}
    tenth = lord.fact("is_tenth_lord")
    assert tenth.value is True
    natal, link = _section(answer, "glance").synthesis_sentences[1:3]
    assert natal.text.startswith(
        "Natal: your 10th lord is Jupiter, in your 4th house; your chart matches "
    )
    assert link.text == (
        "Calculated link: your 10th lord is also your Mahadasha lord throughout 2027."
    )
    assert tenth.fact_id in link.fact_ids
    assert "jyotish.d1.house_lord.10.placement_house" in natal.fact_ids
    assert lord.lord.value.title() == "Jupiter"
    assert all(segment.mahadasha_lord == "jupiter" for segment in plan.dasha_segments)
    assert framing.claim_ids == (timed.claim_id,)
    assert framing.rule_ids == timed.rule_ids
    assert framing.text.startswith("Your current Jupiter Mahadasha ")


def test_framing_does_not_say_current_for_a_period_that_has_not_started() -> None:
    answer = (
        _ask()
        .answer(
            DeterministicAnalysisRequest(
                birth_input=PROFILES["period_lord"],
                as_of=datetime(2010, 1, 1, tzinfo=UTC),
                question=_QUESTION,
            )
        )
        .answers[0]
    )
    framing = answer.consultation_sections[0].synthesis_sentences[0]
    assert framing.text.startswith("Your Jupiter Mahadasha in 2027 matches a reviewed BPHS")
    assert "current" not in framing.text


def test_without_timing_match_the_direct_line_states_periods_natal_label_and_status(
    answers: dict[str, DetailedComposedAnswer],
) -> None:
    # NEXT-UX-SUMMARY: the 10th lord (E1) is named once, in the glance, not here.
    assert answers["shared_house"].consultation_sections[0].text == (
        "In 2027 your calculated Vimshottari periods are the Mercury Mahadasha with the "
        "Jupiter Antardasha (Jan 1–Dec 31). Your chart matches the reviewed indication about "
        "your 10th lord's placement. No reviewed timing rule applies to 2027, so no specific "
        "Career event is established for this year."
    )
    assert answers["rahu_rahu"].consultation_sections[0].text == (
        "In 2027 your calculated Vimshottari periods are the Rahu Mahadasha with the Rahu "
        "Antardasha (Jan 1–Dec 31). Your chart matches the reviewed indication about your "
        "10th lord's placement. No reviewed timing rule applies to 2027, so no specific "
        "Career event is established for this year."
    )
    assert "Natal: your 10th lord is Venus, in your 6th house; your chart matches" in (
        _section(answers["rahu_rahu"], "glance").text
    )


def test_no_co_reference_sentence_in_the_direct_line_without_a_timing_match(
    answers: dict[str, DetailedComposedAnswer],
) -> None:
    for name in ("shared_house", "rahu_rahu", "none"):
        answer = answers[name]
        plan = answer.career_answer_plan
        assert plan is not None and plan.synthesis is not None
        direct = answer.consultation_sections[0]
        why = _section(answer, "why")
        for sentence in why.synthesis_sentences:
            assert sentence.text not in direct.text, name
        for link in plan.synthesis.links:
            assert link.text not in direct.text, name
        for phrase in (" concerns ", " lord throughout ", "shares a calculated", "Shared "):
            assert phrase not in direct.text, (name, phrase)
        assert direct.text.endswith(
            "No reviewed timing rule applies to 2027, so no specific Career event is "
            "established for this year."
        )
    # The co-reference lines are still in the Why section.
    assert "rules your 11th house" in _section(answers["shared_house"], "why").text


@pytest.mark.parametrize(
    "wording",
    [
        TimingSourceRecord().reviewed_interpretation,
        MoonVenusOwnExaltationTimingSourceRecord().reviewed_interpretation,
        NinthLordInTenthTimingSourceRecord().reviewed_interpretation,
    ],
)
def test_every_admitted_timing_wording_splits_into_verbatim_meaning_and_limit(
    wording: str,
) -> None:
    meaning, limit = timing_meaning_and_limit(wording)
    assert wording.startswith(meaning) and meaning.endswith(".")
    assert limit is not None and wording.endswith(limit)
    assert limit.startswith("It does not")


def test_timing_wording_without_a_non_guarantee_clause_is_not_invented() -> None:
    assert timing_meaning_and_limit("Only one sentence.") == ("Only one sentence.", None)


def test_natal_context_has_its_own_section_after_why(
    answers: dict[str, DetailedComposedAnswer],
) -> None:
    for answer in answers.values():
        kinds = [section.kind for section in answer.consultation_sections]
        assert kinds == [
            "direct",
            "glance",
            "period_themes",
            "why",
            "natal",
            "dasha",
            "dasha_context",
            "timing",
            "limit",
        ]
        natal = _section(answer, "natal")
        direct = answer.consultation_sections[0]
        for claim in answer.claim_ledger.claims:  # type: ignore[union-attr]
            if claim.kind is ClaimKind.APPROVED_INTERPRETATION:
                assert claim.permitted_wording in natal.text
                assert claim.permitted_wording not in direct.text
        assert "natal Career context" not in direct.text
        assert answer.answer == " ".join(s.text for s in answer.consultation_sections)


# --- (b) No ids in prose ----------------------------------------------------------------------


def test_answer_prose_contains_no_rule_claim_or_method_ids(
    answers: dict[str, DetailedComposedAnswer],
) -> None:
    for answer in answers.values():
        ids = _known_ids(answer)
        _assert_no_ids(answer.answer, ids)
        for section in answer.consultation_sections:
            _assert_no_ids(section.text, ids)
            for sentence in section.synthesis_sentences:
                _assert_no_ids(sentence.text, ids)
        plan = answer.career_answer_plan
        assert plan is not None and plan.synthesis is not None
        for link in plan.synthesis.links:
            _assert_no_ids(link.text, ids)
            _assert_no_ids(link.claim_label, ids)


def test_ids_stay_in_the_disclosure_and_sentence_mapping(
    answers: dict[str, DetailedComposedAnswer],
) -> None:
    answer = answers["period_lord"]
    plan = answer.career_answer_plan
    assert plan is not None and plan.synthesis is not None
    why = _section(answer, "why")
    assert why.synthesis_links == plan.synthesis.links
    for sentence in why.synthesis_sentences:
        assert sentence.claim_ids and sentence.fact_ids and sentence.rule_ids
        assert sentence.calc_method_ids
    mapped = {fid for sentence in why.synthesis_sentences for fid in sentence.fact_ids}
    for link in plan.synthesis.links:
        assert set(link.claim_fact_ids) | set(link.dasha_fact_ids) <= mapped


def test_follow_up_replies_contain_no_ids(consultation: ConsultationService) -> None:
    for birth in PROFILES.values():
        first = _respond(consultation, birth, _QUESTION)
        assert first.analysis is not None
        ids = _known_ids(first.analysis.answers[0])
        for question in (
            "Why?",
            "Explain this particular claim",
            "What are the limitations?",
            "Which planetary placement supports this?",
        ):
            reply = _respond(consultation, birth, question, first.state.consultation_id)
            _assert_no_ids(reply.reply or "", ids)
            for choice in reply.choices:
                _assert_no_ids(choice.label, ids)
                _assert_no_ids(choice.question, ids)


def test_claim_labels_are_derived_from_fact_ids() -> None:
    def claim(kind: ClaimKind, *fact_ids: str, claim_id: str = "c") -> CareerClaim:
        return CareerClaim(
            claim_id=claim_id,
            kind=kind,
            requested_question_shape=CareerQuestionFocus.PERIOD,
            fact_ids=fact_ids,
            rule_ids=("r",),
            evidence_item_ids=("e",),
            calculation_version="x",
            methodology_version="x",
            source_reference="s",
            evaluation_status=ClaimStatus.MATCH,
            permitted_wording="w",
            timing_reference="[2027-01-01T00:00:00+00:00,2028-01-01T00:00:00+00:00)"
            if kind is ClaimKind.APPROVED_TIMING_INTERPRETATION
            else None,
            authorized_precision="BROAD_PERIOD"
            if kind is ClaimKind.APPROVED_TIMING_INTERPRETATION
            else None,
        )

    natal = ClaimKind.APPROVED_INTERPRETATION
    timed = ClaimKind.APPROVED_TIMING_INTERPRETATION
    assert claim_label(claim(natal, "jyotish.d1.house_lord.10.placement_house")) == (
        "the reviewed indication about your 10th lord's placement"
    )
    assert claim_label(
        claim(
            timed,
            "jyotish.d1.house.10.lord",
            "jyotish.d1.house_lord.10.placement_house",
            "jyotish.timing.vimshottari.mahadasha.lord",
        )
    ) == ("the reviewed timing indication about your 10th lord's Mahadasha")
    assert claim_label(
        claim(
            timed,
            "jyotish.timing.vimshottari.antardasha.lord",
            "jyotish.d1.planet.venus.own_sign",
            "jyotish.d1.planet.venus.exaltation_sign",
        )
    ) == ("the reviewed timing indication about Venus's own or exaltation sign")
    # NEXT-COMPARE-02b: with calculated window lords, the label names the period.
    lorded = claim(timed, "jyotish.timing.vimshottari.mahadasha.lord")
    assert claim_label(lorded.model_copy(update={"period_lords": ("jupiter",)})) == (
        "the reviewed timing indication for Jupiter Mahadasha"
    )
    assert claim_label(lorded.model_copy(update={"period_lords": ("moon", "venus")})) == (
        "the reviewed timing indication for Moon Mahadasha with Venus Antardasha"
    )
    assert claim_label(claim(natal, "jyotish.d1.planet.saturn.placement_house")) == (
        "the reviewed indication about Saturn's placement"
    )
    assert claim_label(claim(natal, "unrecognised.fact")) == "the reviewed natal Career indication"
    twins = claim_labels(
        (
            claim(natal, "jyotish.d1.house.10.sign", claim_id="a"),
            claim(natal, "jyotish.d1.house.10.kendra", claim_id="b"),
        )
    )
    assert twins == {
        "a": "the reviewed indication about your 10th house (1 of 2)",
        "b": "the reviewed indication about your 10th house (2 of 2)",
    }


# --- (c) Why section --------------------------------------------------------------------------


def test_why_merges_same_planet_lines_and_replaces_year_spanning_period_lines(
    answers: dict[str, DetailedComposedAnswer],
) -> None:
    answer = answers["period_lord"]
    why = _section(answer, "why")
    assert [sentence.text for sentence in why.synthesis_sentences] == [
        "Both reviewed indications concern your 10th lord, Jupiter, and Jupiter is the "
        "Mahadasha lord (18 Mar 2015 to 18 Mar 2031).",
        "The window of the reviewed timing indication for Jupiter Mahadasha spans all of 2027.",
    ]
    assert why.text.endswith(WHY_FRAMING)
    assert "Shared period" not in why.text
    # The links themselves are unchanged: two SAME_PLANET and two SAME_PERIOD.
    plan = answer.career_answer_plan
    assert plan is not None and plan.synthesis is not None
    assert [link.link_type for link in plan.synthesis.links] == [
        "SAME_PLANET",
        "SAME_PLANET",
        "SAME_PERIOD",
        "SAME_PERIOD",
    ]
    assert plan.synthesis.year_spanning_claim_ids == tuple(
        link.claim_id for link in plan.synthesis.links[2:3]
    )


def test_same_planet_as_mahadasha_and_antardasha_lord_is_one_line(
    answers: dict[str, DetailedComposedAnswer],
) -> None:
    why = _section(answers["rahu_rahu"], "why")
    assert [sentence.text for sentence in why.synthesis_sentences] == [
        "The reviewed indication about your 10th lord's placement concerns your 6th house, and "
        "Rahu, both the Mahadasha lord (28 Feb 2026 to 28 Feb 2044) and the Antardasha lord "
        "(28 Feb 2026 to 10 Nov 2028), occupies your 6th house."
    ]
    assert len(why.synthesis_links) == 2


def _link(claim_id: str, label: str, **values: object) -> SynthesisLink:
    base: dict[str, object] = {
        "link_type": "SAME_PLANET",
        "claim_id": claim_id,
        "claim_label": label,
        "claim_subject": "your 10th lord, Saturn",
        "claim_fact_ids": (f"{claim_id}.fact",),
        "claim_rule_ids": (f"{claim_id}.rule",),
        "dasha_fact_ids": ("jyotish.dasha_linkage.v1.lord.saturn.is_tenth_lord",),
        "calc_method_ids": (DASHA_LINKAGE_METHODOLOGY_ID,),
        "segment_ids": ("s1",),
        "period_role": "Antardasha",
        "period_lord": "Saturn",
        "period_span": "1 Mar 2027 to 1 Jun 2029",
        "shared_reference": "planet:saturn",
        "text": "t",
    }
    return SynthesisLink.model_validate({**base, **values})


def test_partial_merge_names_each_indication_and_keeps_partial_period_lines() -> None:
    period = _link(
        "c",
        "the reviewed timing indication about your 10th lord's Mahadasha",
        link_type="SAME_PERIOD",
        claim_subject=None,
        period_role=None,
        period_lord=None,
        period_span=None,
        shared_reference="interval:[a,b)",
        calc_method_ids=(VIMSHOTTARI_METHODOLOGY_ID,),
        text="Shared period, 1 Mar 2027 to 31 Dec 2027: the window overlaps one segment.",
    )
    synthesis = CareerSynthesis(
        year=2027,
        reviewed_claim_ids=("a", "b", "c"),
        links=(
            _link("a", "the reviewed indication about your 10th lord's placement"),
            _link("b", "the reviewed indication about your 10th house"),
            period,
        ),
    )
    texts = [sentence.text for sentence in why_sentences(synthesis)]
    assert texts == [
        "The reviewed indication about your 10th lord's placement and the reviewed indication "
        "about your 10th house both concern your 10th lord, Saturn, and Saturn is the "
        "Antardasha lord (1 Mar 2027 to 1 Jun 2029).",
        # The window does not span the whole year, so its period line is kept.
        period.text,
    ]


# --- (d) Calculation-method provenance -------------------------------------------------------


def test_calculation_methods_are_never_rule_ids(
    answers: dict[str, DetailedComposedAnswer],
) -> None:
    for answer in answers.values():
        plan = answer.career_answer_plan
        assert plan is not None and plan.synthesis is not None
        for link in plan.synthesis.links:
            assert not set(link.dasha_rule_ids) & METHOD_IDS
            assert not set(link.claim_rule_ids) & METHOD_IDS
            expected = (
                VIMSHOTTARI_METHODOLOGY_ID
                if link.link_type == "SAME_PERIOD"
                else DASHA_LINKAGE_METHODOLOGY_ID
            )
            assert link.calc_method_ids == (expected,)
        for section in answer.consultation_sections:
            for sentence in section.synthesis_sentences:
                assert not set(sentence.rule_ids) & METHOD_IDS
                assert set(sentence.calc_method_ids) <= METHOD_IDS


def test_admitted_dasha_rules_are_the_only_dasha_rule_ids() -> None:
    slot = DashaInterpretationSlot(
        corpus_manifest_id="m",
        corpus_manifest_version="1",
        claims=(
            DashaInterpretationClaim(
                rule_id="synthetic.dasha.rule",
                rule_version="v1",
                source_locator="synthetic",
                permitted_wording="synthetic",
                segment_id="s1",
                mahadasha_lord="jupiter",
                antardasha_lord="moon",
                matched_fact_ids=("f",),
            ),
        ),
    )
    assert _dasha_rule_ids(slot, ("s1",)) == ("synthetic.dasha.rule@v1",)
    assert _dasha_rule_ids(slot, ("s2",)) == ()
    assert _dasha_rule_ids(None, ("s1",)) == ()


# --- (e) Plain-language choices --------------------------------------------------------------


def test_why_reply_offers_plain_choices(consultation: ConsultationService) -> None:
    birth = PROFILES["period_lord"]
    first = _respond(consultation, birth, _QUESTION)
    reply = _respond(consultation, birth, "Why?", first.state.consultation_id)
    assert [choice.label for choice in reply.choices] == [
        "The reviewed indication about your 10th lord's placement",
        "The reviewed timing indication for Jupiter Mahadasha",
    ]
    assert (
        "To go deeper, choose the reviewed indication about your 10th lord's placement or "
        "the reviewed timing indication for Jupiter Mahadasha"
    ) in (reply.reply or "")


def test_which_claim_prompt_offers_plain_choices_that_resolve(
    consultation: ConsultationService,
) -> None:
    birth = PROFILES["period_lord"]
    first = _respond(consultation, birth, _QUESTION)
    assert first.analysis is not None
    ids = _known_ids(first.analysis.answers[0])
    prompt = _respond(
        consultation, birth, "Explain this particular claim", first.state.consultation_id
    )
    assert prompt.status == "clarification"
    assert prompt.reply == (
        "Which reviewed indication do you mean: the reviewed indication about your 10th lord's "
        "placement or the reviewed timing indication for Jupiter Mahadasha?"
    )
    natal = prompt.choices[0]
    picked = _respond(
        consultation,
        birth,
        natal.question,
        first.state.consultation_id,
        claim_ids=natal.claim_ids,
        reference_turn_id=first.state.turn_id,
    )
    assert picked.status == "answered"
    assert picked.resolved_claim_ids == natal.claim_ids
    assert "Approved rule: the reviewed indication about your 10th lord's placement." in (
        picked.reply or ""
    )
    _assert_no_ids(picked.reply or "", ids)
    # The rule id is still disclosed through the resolved claim and its source reference.
    assert picked.source_references


def test_typed_plain_label_resolves_the_claim(consultation: ConsultationService) -> None:
    birth = PROFILES["period_lord"]
    first = _respond(consultation, birth, _QUESTION)
    reply = _respond(
        consultation,
        birth,
        "Explain the reviewed timing indication for Jupiter Mahadasha",
        first.state.consultation_id,
    )
    assert reply.status == "answered"
    assert reply.resolved_claim_ids == ("career-timing-1",)


def test_no_match_prompt_offers_natal_and_timing_choices(
    consultation: ConsultationService,
) -> None:
    birth = PROFILES["shared_house"]
    first = _respond(consultation, birth, _QUESTION)
    prompt = _respond(
        consultation, birth, "Explain this particular claim", first.state.consultation_id
    )
    assert prompt.status == "clarification"
    assert [choice.label for choice in prompt.choices] == [
        "The reviewed indication about your 10th lord's placement",
        "Why no reviewed Career timing rule matched 2027",
    ]
    timing = prompt.choices[1]
    reply = _respond(
        consultation,
        birth,
        timing.question,
        first.state.consultation_id,
        claim_ids=timing.claim_ids,
        reference_turn_id=first.state.turn_id,
    )
    assert reply.resolved_claim_ids == ("career-timing-status",)
    assert (reply.reply or "").startswith("For 2027: ")


def test_which_claim_prompt_names_each_option_by_its_button_label(
    consultation: ConsultationService,
) -> None:
    birth = PROFILES["shared_house"]
    first = _respond(consultation, birth, _QUESTION)
    prompt = _respond(
        consultation, birth, "Explain this particular claim", first.state.consultation_id
    )
    text = prompt.reply or ""
    assert text == (
        "Would you like me to explain the reviewed indication about your 10th lord's "
        "placement, or why no reviewed Career timing rule matched 2027?"
    )
    for choice in prompt.choices:
        assert choice.label[0].lower() + choice.label[1:] in text
    assert "eleventh-house" not in text and "Career interpretation" not in text
