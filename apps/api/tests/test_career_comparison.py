"""NEXT-COMPARE-02: factual side-by-side Career comparison (comparison-view-v1), no ranking.

Synthetic births only:

* ``ONE_SIDED`` (1979-06-10 12:00 UTC, 0°/0°): a reviewed timing indication in 2027 only.
* ``NEITHER`` (1980-06-15): no reviewed timing indication in 2027 or 2028.
* ``BOTH`` (1978-01-01): the same reviewed timing indication in both years.
"""

import json
from datetime import UTC, datetime

import pytest

from astrologer.application.analyze import (
    DeterministicAnalysisRequest,
    DeterministicAnalysisService,
)
from astrologer.application.answer import AskJyotAIService
from astrologer.application.career_claims import year_periods_sentence
from astrologer.application.career_comparison import (
    ABSENCE_NOT_AGAINST,
    DIRECT_SIDE_BY_SIDE,
    FIXED_TEMPLATES,
    WHY_NOT_A_VERDICT,
    fixed_texts,
)
from astrologer.application.consultation import (
    COMPARISON_RANKING_PRECONDITIONS_REPLY,
    COMPARISON_WHY_REPLY,
    ConsultationRequest,
    ConsultationService,
    ConsultationStore,
)
from astrologer.application.context import DeterministicAstrologyContextService
from astrologer.application.detailed_answer import DetailedAnswerBuilder
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.birth.models import BirthInput
from astrologer.composition import DeterministicAnswerComposer, SeniorAstrologerComposer
from astrologer.composition.comparison_guard import ranking_violation
from astrologer.composition.composer import AnswerCompositionError
from astrologer.composition.models import (
    CareerYearComparison,
    CompositionProviderRequest,
    CompositionProviderResponse,
)
from astrologer.evidence import InterpretationEvidenceBuilder
from astrologer.timing_rules.models import (
    MoonVenusOwnExaltationTimingSourceRecord,
    TimingSourceRecord,
)
from astrologer.timing_rules.service import CareerTimingAnalysisService

_AS_OF = datetime(2026, 1, 1, tzinfo=UTC)
_BIRTHS = {
    "ONE_SIDED": BirthInput(
        birth_date="1979-06-10", birth_time="12:00:00", timezone="UTC", latitude=0, longitude=0
    ),
    "NEITHER": BirthInput(
        birth_date="1980-06-15", birth_time="12:00:00", timezone="UTC", latitude=0, longitude=0
    ),
    "BOTH": BirthInput(
        birth_date="1978-01-01", birth_time="12:00:00", timezone="UTC", latitude=0, longitude=0
    ),
}
_QUESTION = "Which is better for my career, 2027 or 2028?"
_ADMITTED_TEXTS = {
    TimingSourceRecord().reviewed_interpretation,
    MoonVenusOwnExaltationTimingSourceRecord().reviewed_interpretation,
}


def _ask(composer: object | None = None) -> AskJyotAIService:
    provider = SwissEphemerisProvider()
    return AskJyotAIService(
        DeterministicAnalysisService(DeterministicAstrologyContextService(provider)),
        InterpretationEvidenceBuilder(),
        composer or DeterministicAnswerComposer(),  # type: ignore[arg-type]
        CareerTimingAnalysisService(provider),
    )


def _request(profile: str, question: str = _QUESTION) -> DeterministicAnalysisRequest:
    return DeterministicAnalysisRequest(
        birth_input=_BIRTHS[profile], as_of=_AS_OF, question=question
    )


@pytest.fixture(scope="module")
def comparisons() -> dict[str, CareerYearComparison]:
    ask = _ask()
    result: dict[str, CareerYearComparison] = {}
    for profile in _BIRTHS:
        answer = ask.answer(_request(profile)).answers[0]
        assert answer.career_comparison is not None
        assert answer.answer == answer.career_comparison.text()
        result[profile] = answer.career_comparison
    return result


def _texts(comparison: CareerYearComparison) -> list[str]:
    return [sentence.text for sentence in comparison.sentences()]


# --- E2/E3: model and routing -------------------------------------------------------------


def test_comparison_is_side_by_side_with_no_ranking_fields(
    comparisons: dict[str, CareerYearComparison],
) -> None:
    fields = set(CareerYearComparison.model_fields)
    named = {name for name in fields if any(w in name for w in ("rank", "score", "winner"))}
    assert named == {"ranking_status", "why_no_ranking"}
    for comparison in comparisons.values():
        assert comparison.view_version == "comparison-view-v1"
        assert comparison.comparison_mode == "SIDE_BY_SIDE"
        assert comparison.ranking_status == "unsupported"
        assert comparison.unit == "calendar_year"
        assert comparison.years == (2027, 2028)
        assert [column.year for column in comparison.columns] == [2027, 2028]


def test_response_order_direct_differs_natal_columns_why_limits(
    comparisons: dict[str, CareerYearComparison],
) -> None:
    comparison = comparisons["ONE_SIDED"]
    text = comparison.text()
    direct = comparison.direct[0].text
    assert direct == (
        "I can't rank 2027 against 2028 for your career: JyotishAI has no reviewed method for "
        "ranking periods."
    )
    assert comparison.direct[-1].text == DIRECT_SIDE_BY_SIDE
    order = [
        text.index(direct),
        text.index(comparison.differences[0].text),
        text.index(comparison.natal_shared[0].text),
        text.index(comparison.columns[0].lord_facts[0].text),
        text.index(WHY_NOT_A_VERDICT),
        text.index(comparison.limitations[0].text),
    ]
    assert order == sorted(order)


def test_columns_are_the_independent_single_year_answers(
    comparisons: dict[str, CareerYearComparison],
) -> None:
    ask = _ask()
    for column in comparisons["ONE_SIDED"].columns:
        year_answer = ask.career_year_answer(_request("ONE_SIDED"), column.year)
        assert year_answer is not None and year_answer.career_answer_plan is not None
        expected = year_periods_sentence(year_answer.career_answer_plan, column.year)
        assert [sentence.text for sentence in column.periods] == [s.text for s in expected]
        assert column.dasha_segments == year_answer.career_answer_plan.dasha_segments
        assert year_answer.timing is not None
        assert column.timing_status == year_answer.timing.status
        assert column.synthesis_version == "career-synthesis-v1"
        assert column.timing_release_id and column.manifest_id


def test_calendar_year_unit_shows_md_ad_boundaries_inside_the_year(
    comparisons: dict[str, CareerYearComparison],
) -> None:
    periods = comparisons["ONE_SIDED"].columns[1].periods[0].text
    # 2028 crosses a Mahadasha boundary: both Mahadashas and the dates are shown.
    assert "the Moon Mahadasha with the Sun Antardasha (Jan 1–Mar 7)" in periods
    assert "then the Mars Mahadasha with the Mars Antardasha (Mar 7–Aug 4)" in periods


# --- Amendment (a): the "differs" block --------------------------------------------------


def test_differs_block_lists_periods_timing_and_one_year_links(
    comparisons: dict[str, CareerYearComparison],
) -> None:
    differences = [sentence.text for sentence in comparisons["ONE_SIDED"].differences]
    assert differences[1].startswith("In 2027 your calculated Vimshottari periods are")
    assert differences[2].startswith("In 2028 your calculated Vimshottari periods are")
    assert (
        "In 2027, the reviewed timing indication for Moon Mahadasha with Venus Antardasha "
        "applies (Jan 1–Sep 7)." in differences
    )
    assert "In 2028, no reviewed timing indication applies." in differences
    only = [text for text in differences if text.startswith("Only in ")]
    assert only and all(text.startswith("Only in 2027: Shared ") for text in only)
    # Links present in both years are not listed as differences.
    both = "Sun, the Antardasha lord (7 Sep 2027 to 7 Mar 2028), occupies your 10th house"
    assert not any(both in text for text in differences)


def test_differs_block_omits_timing_when_neither_year_has_an_indication(
    comparisons: dict[str, CareerYearComparison],
) -> None:
    differences = [sentence.text for sentence in comparisons["NEITHER"].differences]
    assert len(differences) == 3
    assert all("your calculated Vimshottari periods are" in text for text in differences[1:])
    assert comparisons["NEITHER"].direct[1].text == (
        "No reviewed timing indication applies in either year."
    )
    assert comparisons["BOTH"].direct[1].text == (
        "The same reviewed timing indication applies in both years."
    )


def test_natal_context_is_shown_once_as_same_for_both_years(
    comparisons: dict[str, CareerYearComparison],
) -> None:
    natal = [sentence.text for sentence in comparisons["NEITHER"].natal_shared]
    assert natal == [
        "Your 10th lord is Venus, in your 11th house.",
        "Your chart matches the reviewed indication about your 10th lord's placement.",
        "This natal context comes from the birth chart, so it is the same for 2027 and 2028 "
        "and does not tell the years apart.",
    ]
    assert comparisons["NEITHER"].natal_shared[0].fact_ids == (
        "jyotish.d1.house.10.lord",
        "jyotish.d1.house_lord.10.placement_house",
    )


# --- Amendment (b): absence is not evidence against a year -------------------------------


def test_absence_sentence_appears_exactly_when_an_indication_applies_in_one_year_only(
    comparisons: dict[str, CareerYearComparison],
) -> None:
    assert ABSENCE_NOT_AGAINST == (
        "An indication not applying in a year is not evidence against that year."
    )
    one_sided = _texts(comparisons["ONE_SIDED"])
    assert one_sided.count(ABSENCE_NOT_AGAINST) == 1
    # NEXT-COMPARE-02b: it sits in the direct line, immediately after the statement it
    # qualifies, and is not repeated in the "What differs" block.
    direct = [sentence.text for sentence in comparisons["ONE_SIDED"].direct]
    index = direct.index(ABSENCE_NOT_AGAINST)
    assert direct[index - 1] == (
        "A reviewed timing indication applies in 2027 and none applies in 2028."
    )
    assert ABSENCE_NOT_AGAINST not in [s.text for s in comparisons["ONE_SIDED"].differences]
    assert comparisons["ONE_SIDED"].text().count(ABSENCE_NOT_AGAINST) == 1
    assert ABSENCE_NOT_AGAINST not in _texts(comparisons["NEITHER"])
    assert ABSENCE_NOT_AGAINST not in _texts(comparisons["BOTH"])


# --- NEXT-COMPARE-02b: period changes open the "What differs" block --------------------


def test_differs_block_opens_with_a_mahadasha_change(
    comparisons: dict[str, CareerYearComparison],
) -> None:
    first = comparisons["ONE_SIDED"].differences[0]
    assert first.text == "Your Mahadasha changes from Moon to Mars on 7 Mar 2028."
    assert first.basis == "fact" and len(first.fact_ids) == 2
    segments = comparisons["ONE_SIDED"].columns[1].dasha_segments
    assert set(first.fact_ids) <= {segment.segment_id for segment in segments}
    # With a Mahadasha change, Antardasha changes are not listed as openers.
    assert not any(
        s.text.startswith("Your Antardasha changes") for s in comparisons["ONE_SIDED"].differences
    )


def test_differs_block_opens_with_antardasha_changes_without_a_mahadasha_change(
    comparisons: dict[str, CareerYearComparison],
) -> None:
    assert comparisons["NEITHER"].differences[0].text == (
        "Your Antardasha changes from Moon to Mars on 2 Jun 2028."
    )
    both = [s.text for s in comparisons["BOTH"].differences]
    assert both[:2] == [
        "Your Antardasha changes from Moon to Mars on 16 Nov 2027.",
        "Your Antardasha changes from Mars to Rahu on 22 Oct 2028.",
    ]


def test_timing_labels_name_the_periods_everywhere(
    comparisons: dict[str, CareerYearComparison],
) -> None:
    (indication,) = comparisons["ONE_SIDED"].columns[0].timing_indications
    assert indication.label == (
        "the reviewed timing indication for Moon Mahadasha with Venus Antardasha"
    )
    (both,) = comparisons["BOTH"].columns[0].timing_indications
    assert both.label == "the reviewed timing indication for Jupiter Mahadasha"
    assert "about Venus's own or exaltation sign" not in comparisons["ONE_SIDED"].text()


def test_a_label_naming_an_antardasha_still_resolves_its_claim_from_a_button() -> None:
    service = _consultation()
    first = service.respond(_turn("ONE_SIDED", "How will my career be in 2027?"))
    cid = first.state.consultation_id
    why = service.respond(_turn("ONE_SIDED", "Why?", cid))
    label = "The reviewed timing indication for Moon Mahadasha with Venus Antardasha"
    choice = next(choice for choice in why.choices if choice.label == label)
    picked = service.respond(
        _turn("ONE_SIDED", choice.question, cid).model_copy(
            update={"reference_turn_id": first.state.turn_id, "claim_ids": choice.claim_ids}
        )
    )
    assert picked.status == "answered"
    assert picked.resolved_claim_ids == choice.claim_ids
    assert "source MD" not in (picked.reply or "")  # not routed to the Dasha listing
    typed = service.respond(_turn("ONE_SIDED", f"Explain {label.lower()}", cid))
    assert typed.resolved_claim_ids == choice.claim_ids


# --- Admitted text is verbatim -----------------------------------------------------------


def test_admitted_timing_text_is_quoted_byte_for_byte(
    comparisons: dict[str, CareerYearComparison],
) -> None:
    column = comparisons["ONE_SIDED"].columns[0]
    assert column.timing_status == "MATCH"
    (indication,) = column.timing_indications
    assert indication.reviewed_statement in _ADMITTED_TEXTS
    assert indication.reviewed_statement in [sentence.text for sentence in column.timing]
    assert comparisons["ONE_SIDED"].columns[1].timing[0].text == (
        "No reviewed timing indication applies."
    )


# --- E4 guard tests ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "2028 is better for your career.",
        "2027 looks stronger.",
        "The indications are weaker in 2028.",
        "2027 is more favourable.",
        "2028 is the more favorable year.",
        "2028 has fewer indications.",
        "2028 has 2 matches and 2027 has 0.",
        "Two reviewed indications apply in 2027.",
        "2027 scores higher.",
        "This favours 2027.",
        "2027 is the worse year.",
    ],
)
def test_guard_rejects_ranking_words_and_tallies(text: str) -> None:
    assert ranking_violation(text) is not None


def test_no_ranking_language_or_tallies_in_any_comparison_sentence(
    comparisons: dict[str, CareerYearComparison],
) -> None:
    for comparison in comparisons.values():
        for text in _texts(comparison):
            assert ranking_violation(text) is None, text


def test_every_comparison_sentence_is_fact_or_rule_backed_or_fixed(
    comparisons: dict[str, CareerYearComparison],
) -> None:
    for comparison in comparisons.values():
        fixed = fixed_texts(comparison.years)
        for sentence in comparison.sentences():
            if sentence.basis == "fact":
                assert sentence.fact_ids, sentence.text
            elif sentence.basis == "rule":
                assert sentence.rule_ids, sentence.text
            else:
                assert sentence.text in fixed, sentence.text


def test_fixed_texts_and_follow_up_replies_are_free_of_ranking_language() -> None:
    for text in fixed_texts((2027, 2028)):
        assert ranking_violation(text) is None, text
    for template in FIXED_TEMPLATES:
        assert "{" not in template or "}" in template
    assert ranking_violation(COMPARISON_WHY_REPLY.format(a=2027, b=2028)) is None
    assert ranking_violation(COMPARISON_RANKING_PRECONDITIONS_REPLY) is None


class _RankingTransport:
    """Returns a structurally valid narrative whose summary ranks the two years."""

    def __init__(self, summary: str) -> None:
        self.summary = summary

    def complete(self, request: CompositionProviderRequest) -> CompositionProviderResponse:
        packet = json.loads(request.user_payload_json)
        ids = packet["evidence_item_ids"]
        body = {
            "summary": self.summary,
            "explanation": packet["approved_narrative_phrases"]["explanation"][ids[0]][2],
            "question_relevance": packet["domain_framing"][0],
            "limitations_text": " ".join(packet["deterministic_limitations"]),
            "follow_up": None,
            "supporting_evidence_item_ids": {
                "summary": ids,
                "explanation": [ids[0]],
                "question_relevance": ids,
            },
        }
        return CompositionProviderResponse(
            output_json=json.dumps(body), provider_id="test", model_id="test"
        )


def test_llm_validator_rejects_ranking_language_in_comparison_answers() -> None:
    analysis = DeterministicAnalysisService(
        DeterministicAstrologyContextService(SwissEphemerisProvider())
    ).analyze(_request("BOTH"))
    evidence = InterpretationEvidenceBuilder().build(analysis.selections[0])
    detailed = DetailedAnswerBuilder().build(evidence)
    composer = SeniorAstrologerComposer(_RankingTransport("2028 is the better year for you."))
    with pytest.raises(AnswerCompositionError) as raised:
        composer.compose(_QUESTION, detailed, evidence, comparison=True)
    assert raised.value.reason_code == "comparison_ranking_language"


def test_llm_ranking_narrative_falls_back_to_the_deterministic_side_by_side() -> None:
    ask = _ask(SeniorAstrologerComposer(_RankingTransport("2027 is stronger than 2028.")))
    answer = ask.answer(_request("BOTH")).answers[0]
    assert answer.narrative is None
    assert answer.career_comparison is not None
    assert answer.answer == answer.career_comparison.text()


# --- Amendment (e): comparison follow-ups -------------------------------------------------


def _consultation() -> ConsultationService:
    return ConsultationService(_ask(), ConsultationStore())


def _turn(profile: str, question: str, consultation_id: str | None = None) -> ConsultationRequest:
    return ConsultationRequest(
        birth_input=_BIRTHS[profile],
        as_of=_AS_OF,
        question=question,
        consultation_id=consultation_id,
    )


def test_why_after_a_comparison_explains_no_ranking_and_offers_three_buttons() -> None:
    service = _consultation()
    first = service.respond(_turn("ONE_SIDED", _QUESTION))
    cid = first.state.consultation_id
    why = service.respond(_turn("ONE_SIDED", "Why?", cid))
    assert why.status == "unsupported"
    assert why.reply == COMPARISON_WHY_REPLY.format(a=2027, b=2028)
    assert ABSENCE_NOT_AGAINST in (why.reply or "")
    assert [choice.label for choice in why.choices] == [
        "Explain 2027",
        "Explain 2028",
        "What would allow a ranking?",
    ]
    ranking = service.respond(_turn("ONE_SIDED", why.choices[2].question, cid))
    assert ranking.reply == COMPARISON_RANKING_PRECONDITIONS_REPLY
    assert [choice.label for choice in ranking.choices] == ["Explain 2027", "Explain 2028"]
    explained = service.respond(_turn("ONE_SIDED", why.choices[1].question, cid))
    assert explained.analysis is not None
    intent = explained.analysis.routing.intents[0]
    assert intent.time_range is not None and intent.time_range.start_date.year == 2028
    assert explained.analysis.answers[0].career_comparison is None
    # The explained year is now the anchor: "Why?" explains that year, not the comparison.
    after = service.respond(_turn("ONE_SIDED", "Why?", cid))
    assert after.reply != COMPARISON_WHY_REPLY.format(a=2027, b=2028)


def test_explain_each_year_button_returns_that_years_full_answer() -> None:
    for year in (2027, 2028):
        service = _consultation()
        first = service.respond(_turn("NEITHER", _QUESTION))
        reply = service.respond(_turn("NEITHER", f"Explain {year}", first.state.consultation_id))
        assert reply.analysis is not None
        answer = reply.analysis.answers[0]
        assert answer.consultation_sections[0].text.startswith(
            f"In {year} your calculated Vimshottari periods are"
        )


def test_comparison_follow_up_is_a_side_by_side_and_why_then_explains_it() -> None:
    service = _consultation()
    first = service.respond(_turn("ONE_SIDED", "How will my career be in 2027?"))
    cid = first.state.consultation_id
    compared = service.respond(_turn("ONE_SIDED", "Is 2028 better than 2027?", cid))
    assert compared.status == "unsupported"
    assert compared.career_comparison is not None
    assert compared.reply == compared.career_comparison.text()
    assert ABSENCE_NOT_AGAINST in (compared.reply or "")
    why = service.respond(_turn("ONE_SIDED", "Why?", cid))
    assert why.reply == COMPARISON_WHY_REPLY.format(a=2027, b=2028)


def test_a_year_question_without_comparison_is_unchanged_in_shape() -> None:
    answer = _ask().answer(_request("ONE_SIDED", "How is my career in 2027?")).answers[0]
    assert answer.career_comparison is None
    assert [section.kind for section in answer.consultation_sections] == [
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
