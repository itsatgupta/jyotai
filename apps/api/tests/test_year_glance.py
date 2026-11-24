"""NEXT-UX-SUMMARY: the "<Year> at a glance" block and the single 10th-lord statement.

Presentation only: the glance adds no facts, rules, or doctrine.  All birth inputs are
synthetic (lat/long 0, UTC); none describes a real person.
"""

import re
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest
from consultation_quality_benchmark import FORBIDDEN_SYNTHESIS_WORDS, PROSE_ID_PATTERN
from test_career_answer_wording import PROFILES, _ask, _birth

from astrologer.application.analyze import DeterministicAnalysisRequest
from astrologer.application.career_claims import timing_meaning_and_limit
from astrologer.application.consultation import (
    ConsultationRequest,
    ConsultationService,
    ConsultationStore,
)
from astrologer.application.year_glance import GLANCE_LINK_PRECEDENCE, select_glance_link
from astrologer.astrology.dasha_linkage import LinkageStatus
from astrologer.composition.career_claims import ClaimKind
from astrologer.composition.comparison_guard import ranking_violation
from astrologer.composition.models import CareerAnswerPlan, DetailedComposedAnswer

_AS_OF = datetime(2026, 1, 1, tzinfo=ZoneInfo("Asia/Kolkata"))
# Synthetic: Rahu MD with Saturn AD (Jan 1-22), then Mercury AD; Mercury shares the 10th
# lord's sign and Saturn occupies the 10th house.
RAHU_MERCURY = _birth("1978-06-12", "18:00:00")
CASES = [
    *((name, birth, year) for name, birth in PROFILES.items() for year in (2027, 2028)),
    ("rahu_mercury", RAHU_MERCURY, 2028),
    ("rahu_mercury", _birth("1994-10-03", "18:00:00"), 2028),
]
# A sentence that tells the reader which planet is the 10th lord (identity statements).
TENTH_LORD_IDENTITY = re.compile(
    r"\b10th lord is [A-Z][a-z]+\b|\b[A-Z][a-z]+(?:, [^.,]+,)? is your 10th lord\b"
    r"|tenth-house lord is placed"
)
EVALUATIVE = re.compile(r"\b(?:strong|strongest|strength|weak|weakest|significant|key)\b", re.I)


def _answer(birth: object, year: int) -> DetailedComposedAnswer:
    return (
        _ask()
        .answer(
            DeterministicAnalysisRequest(
                birth_input=birth,  # type: ignore[arg-type]
                as_of=_AS_OF,
                question=f"How is my career in {year}?",
            )
        )
        .answers[0]
    )


@pytest.fixture(scope="module")
def answers() -> dict[tuple[str, str, int], DetailedComposedAnswer]:
    return {(name, birth.birth_date, year): _answer(birth, year) for name, birth, year in CASES}


def _glance(answer: DetailedComposedAnswer):  # type: ignore[no-untyped-def]
    return next(s for s in answer.consultation_sections if s.kind == "glance")


def _known_fact_ids(answer: DetailedComposedAnswer) -> set[str]:
    plan = answer.career_answer_plan
    assert plan is not None
    known = {segment.segment_id for segment in plan.dasha_segments}
    known |= {fact.fact_id for fact in plan.tenth_lord_facts}
    for item in plan.dasha_linkages:
        known |= set(item.linkage.fact_ids())
    assert answer.claim_ledger is not None
    known |= {f for claim in answer.claim_ledger.claims for f in claim.fact_ids}
    return known


def _admitted(answer: DetailedComposedAnswer) -> list[str]:
    assert answer.claim_ledger is not None
    texts = []
    for claim in answer.claim_ledger.claims:
        if claim.kind in {
            ClaimKind.APPROVED_INTERPRETATION,
            ClaimKind.APPROVED_TIMING_INTERPRETATION,
        }:
            texts.append(claim.permitted_wording)
            texts.extend(t for t in timing_meaning_and_limit(claim.permitted_wording) if t)
    return texts


def _strip_admitted(text: str, answer: DetailedComposedAnswer) -> str:
    # Admitted rule text is quoted verbatim and is not counted as our own statement.
    for wording in sorted(_admitted(answer), key=len, reverse=True):
        text = text.replace(wording, "")
    return text


# --- (1) The glance is fact-backed ------------------------------------------------------------


def test_glance_follows_the_direct_line_with_three_to_five_ordered_bullets(answers) -> None:  # type: ignore[no-untyped-def]
    for key, answer in answers.items():
        kinds = [section.kind for section in answer.consultation_sections]
        assert kinds[:2] == ["direct", "glance"], key
        glance = _glance(answer)
        bullets = [sentence.text for sentence in glance.synthesis_sentences]
        assert 3 <= len(bullets) <= 5, key
        assert glance.text == " ".join(bullets)
        prefixes = [text.split(":", 1)[0] for text in bullets]
        # NEXT-ADMIT-01 adds the Period-themes bullet before Timing.
        assert prefixes in (
            ["Periods", "Natal", "Calculated link", "Period themes", "Timing"],
            ["Periods", "Natal", "Period themes", "Timing"],
            ["Periods", "Natal", "Calculated link", "Timing"],
            ["Periods", "Natal", "Timing"],
        ), key
        assert bullets[-1].startswith("Timing: ")


def test_every_glance_bullet_cites_only_known_facts_claims_and_rules(answers) -> None:  # type: ignore[no-untyped-def]
    for key, answer in answers.items():
        known = _known_fact_ids(answer)
        assert answer.claim_ledger is not None
        claims = {claim.claim_id: claim for claim in answer.claim_ledger.claims}
        assert answer.career_answer_plan is not None
        theme_rules = {r for s in answer.career_answer_plan.period_themes for r in s.rule_ids}
        for bullet in _glance(answer).synthesis_sentences:
            assert set(bullet.fact_ids) <= known, (key, bullet.text)
            assert set(bullet.claim_ids) <= set(claims), (key, bullet.text)
            cited_rules = {r for cid in bullet.claim_ids for r in claims[cid].rule_ids}
            if bullet.text.startswith("Period themes: "):
                # Cites the admitted signification entries and X18, as the section does.
                cited_rules = theme_rules
                assert bullet.rule_ids, (key, bullet.text)
            assert set(bullet.rule_ids) <= cited_rules, (key, bullet.text)
            if not bullet.text.startswith("Timing: no ") and not bullet.text.startswith(
                "Timing: reviewed Career timing was not"
            ):
                # Only a fixed timing-status bullet may stand without a fact or claim.
                assert bullet.fact_ids or bullet.claim_ids, (key, bullet.text)


def test_glance_quotes_no_admitted_text_and_leaks_no_ids(answers) -> None:  # type: ignore[no-untyped-def]
    for key, answer in answers.items():
        text = _glance(answer).text
        for wording in _admitted(answer):
            assert wording not in text, key
        assert not PROSE_ID_PATTERN.search(text), key


def test_glance_periods_match_the_planned_segments(answers) -> None:  # type: ignore[no-untyped-def]
    for key, answer in answers.items():
        plan = answer.career_answer_plan
        assert plan is not None
        periods = _glance(answer).synthesis_sentences[0]
        assert set(periods.fact_ids) == {s.segment_id for s in plan.dasha_segments}, key
        for segment in plan.dasha_segments:
            assert f"{segment.mahadasha_lord.title()} Mahadasha" in periods.text
            assert f"{segment.antardasha_lord.title()} Antardasha" in periods.text


def test_timing_bullet_names_the_matched_rule_or_says_none_applies(answers) -> None:  # type: ignore[no-untyped-def]
    for key, answer in answers.items():
        timing = _glance(answer).synthesis_sentences[-1]
        assert answer.claim_ledger is not None
        timed = [
            c
            for c in answer.claim_ledger.claims
            if c.kind is ClaimKind.APPROVED_TIMING_INTERPRETATION
        ]
        if timed:
            assert timing.text.startswith("Timing: the reviewed timing indication for "), key
            assert set(timing.claim_ids) == {c.claim_id for c in timed}
        else:
            assert timing.text == f"Timing: no reviewed timing rule applies to {key[2]}.", key


def test_the_2028_rahu_mercury_glance() -> None:
    answer = _answer(RAHU_MERCURY, 2028)
    assert [s.text for s in _glance(answer).synthesis_sentences] == [
        "Periods: Rahu Mahadasha throughout 2028, with Saturn Antardasha (Jan 1–Jan 22), then "
        "Mercury Antardasha (Jan 22–Dec 31).",
        # NEXT-ADMIT-02 (Sitting 2 item 29): the 7th-house part of v.72 is paused.
        "Natal: your 10th lord is Sun, in your 7th house; a reviewed indication exists; "
        "wording pending source verification.",
        "Calculated link: Mercury, your Antardasha lord (Jan 22–Dec 31), is in the same sign "
        "as your 10th lord.",
        # NEXT-THEMES-01: each period lord once, with only the houses it brings forward.
        "Period themes: Rahu: 11th house · Saturn: 3rd, 10th houses · Mercury: 11th, 7th houses.",
        "Timing: no reviewed timing rule applies to 2028.",
    ]
    link = _glance(answer).synthesis_sentences[2]
    assert "jyotish.dasha_linkage.v1.lord.mercury.same_sign_as_tenth_lord" in link.fact_ids
    assert "jyotish.d1.house.10.lord" in link.fact_ids


def test_tenth_lord_in_eighth_glance_withholds_the_wording() -> None:
    # Synthetic birth: 10th lord Saturn in the 8th (v.76, admitted as a calculated match only).
    answer = _answer(_birth("1985-01-15", "12:00:00"), 2027)
    natal = _glance(answer).synthesis_sentences[1]
    assert natal.text == (
        "Natal: your 10th lord is Saturn, in your 8th house; a reviewed indication exists for "
        "this placement; its wording is withheld pending further review."
    )
    assert "bphs.d1.house_lord.10.equals_8.v1" in natal.rule_ids
    lowered = answer.answer.lower()
    for word in ("cruel", "thief", "rogue", "short-lived", "short life", "lifespan", "alpāyu"):
        assert word not in lowered


# --- (2) The fixed display precedence ----------------------------------------------------------


def test_precedence_is_the_fixed_documented_order() -> None:
    assert GLANCE_LINK_PRECEDENCE == (
        "is_tenth_lord",
        "same_sign_as_tenth_lord",
        "occupies_tenth",
        "aspects_tenth_house",
        "aspects_tenth_lord",
        "SAME_HOUSE",
    )


def _expected_kind(plan: CareerAnswerPlan) -> tuple[str, str] | None:
    """Independent brute force: every (kind, lord) link present, then the first by rank."""
    present: list[tuple[int, int, str]] = []
    for order, item in enumerate(plan.dasha_linkages):
        for role_rank, lord in ((0, item.linkage.mahadasha), (1, item.linkage.antardasha)):
            for rank, kind in enumerate(GLANCE_LINK_PRECEDENCE[:-1]):
                fact = lord.fact(kind)  # type: ignore[arg-type]
                if fact.status is LinkageStatus.KNOWN and fact.value is True:
                    present.append((rank, role_rank * 100 + order, lord.lord.value))
    for link in plan.synthesis.links if plan.synthesis else ():
        if link.link_type == "SAME_HOUSE" and link.period_lord:
            role_rank = 0 if link.period_role == "Mahadasha" else 1
            present.append((5, role_rank * 100, link.period_lord.lower()))
    if not present:
        return None
    rank, _, lord = min(present)
    return GLANCE_LINK_PRECEDENCE[rank], lord


def test_selected_link_is_the_first_present_by_precedence(answers) -> None:  # type: ignore[no-untyped-def]
    for key, answer in answers.items():
        plan = answer.career_answer_plan
        assert plan is not None
        chosen = select_glance_link(plan, key[2])
        expected = _expected_kind(plan)
        if expected is None:
            assert chosen is None, key
            continue
        assert chosen is not None, key
        assert chosen.kind == expected[0], key
        if chosen.kind != "SAME_HOUSE":
            assert chosen.period_lord == expected[1], key


def test_precedence_prefers_same_sign_over_occupying_the_tenth() -> None:
    # Saturn (AD) occupies the 10th; Mercury (AD) shares the 10th lord's sign.
    plan = _answer(RAHU_MERCURY, 2028).career_answer_plan
    assert plan is not None
    saturn = next(
        i.linkage.antardasha
        for i in plan.dasha_linkages
        if i.linkage.antardasha.lord.value == "saturn"
    )
    assert saturn.fact("occupies_tenth").value is True
    chosen = select_glance_link(plan, 2028)
    assert chosen is not None and (chosen.kind, chosen.period_lord) == (
        "same_sign_as_tenth_lord",
        "mercury",
    )


def test_precedence_prefers_an_aspect_over_a_shared_house() -> None:
    # Jupiter (AD) aspects the 10th lord and also rules the 11th, the reviewed house.
    plan = _answer(PROFILES["shared_house"], 2027).career_answer_plan
    assert plan is not None and plan.synthesis is not None
    assert any(link.link_type == "SAME_HOUSE" for link in plan.synthesis.links)
    chosen = select_glance_link(plan, 2027)
    assert chosen is not None and chosen.kind == "aspects_tenth_lord"


def test_the_10th_lord_itself_ranks_first_and_the_link_refers_to_it_by_role() -> None:
    answer = _answer(PROFILES["period_lord"], 2027)
    plan = answer.career_answer_plan
    assert plan is not None
    chosen = select_glance_link(plan, 2027)
    assert chosen is not None and chosen.kind == "is_tenth_lord"
    natal, link = _glance(answer).synthesis_sentences[1:3]
    # The natal bullet names the 10th lord; the link bullet does not name it again.
    assert natal.text.startswith("Natal: your 10th lord is Jupiter, in your 4th house; ")
    assert link.text == (
        "Calculated link: your 10th lord is also your Mahadasha lord throughout 2027."
    )
    assert chosen.sentence.fact_ids == link.fact_ids


def test_unknown_node_aspects_never_count_as_a_link(answers) -> None:  # type: ignore[no-untyped-def]
    for key, answer in answers.items():
        plan = answer.career_answer_plan
        assert plan is not None
        chosen = select_glance_link(plan, key[2])
        if chosen is not None and chosen.period_lord in {"rahu", "ketu"}:
            assert chosen.kind not in {"aspects_tenth_house", "aspects_tenth_lord"}, key


# --- (3) The 10th lord is stated once --------------------------------------------------------


def test_year_answer_states_the_10th_lord_exactly_once(answers) -> None:  # type: ignore[no-untyped-def]
    for key, answer in answers.items():
        own = _strip_admitted(answer.answer, answer)
        statements = TENTH_LORD_IDENTITY.findall(own)
        assert len(statements) == 1, (key, statements)
        assert TENTH_LORD_IDENTITY.search(_glance(answer).text), key


def _comparison_texts(comparison) -> list[str]:  # type: ignore[no-untyped-def]
    texts = [
        s.text
        for group in (comparison.direct, comparison.differences, comparison.natal_shared)
        for s in group
    ]
    for column in comparison.columns:
        for group in (column.periods, column.timing, column.co_references, column.lord_facts):
            texts.extend(s.text for s in group)
    return texts


@pytest.mark.parametrize("birth", [PROFILES["shared_house"], RAHU_MERCURY])
def test_comparison_shows_the_natal_context_and_the_10th_lord_once(birth) -> None:  # type: ignore[no-untyped-def]
    service = ConsultationService(_ask(), ConsultationStore())
    response = service.respond(
        ConsultationRequest(
            birth_input=birth,
            as_of=datetime(2026, 1, 1, tzinfo=UTC),
            question="Which is better for my career, 2027 or 2028?",
        )
    )
    assert response.analysis is not None
    comparison = next(a.career_comparison for a in response.analysis.answers if a.career_comparison)
    texts = _comparison_texts(comparison)
    joined = " ".join(texts)
    assert len(TENTH_LORD_IDENTITY.findall(joined)) == 1, TENTH_LORD_IDENTITY.findall(joined)
    natal = [s.text for s in comparison.natal_shared]
    assert TENTH_LORD_IDENTITY.search(natal[0])
    # The natal indication appears in the shared block only, never per column.
    for column in comparison.columns:
        for group in (column.periods, column.timing, column.co_references, column.lord_facts):
            for sentence in group:
                assert sentence.text not in natal
                assert not sentence.text.startswith("Your chart matches")
                assert "natal" not in sentence.text.lower()


# --- (4) Governance guards ---------------------------------------------------------------------


def test_glance_uses_no_ranking_evaluative_or_causal_words(answers) -> None:  # type: ignore[no-untyped-def]
    for key, answer in answers.items():
        for bullet in _glance(answer).synthesis_sentences:
            assert ranking_violation(bullet.text) is None, (key, bullet.text)
            assert not FORBIDDEN_SYNTHESIS_WORDS.search(bullet.text.lower()), (key, bullet.text)
            assert not EVALUATIVE.search(bullet.text), (key, bullet.text)
