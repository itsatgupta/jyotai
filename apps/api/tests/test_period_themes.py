"""NEXT-SIG-01: the review-gated signification corpus and the "Period themes" sentence.

FIXTURE corpora only.  The terms below are synthetic test fixtures, borrowed from the review
packet's Part 0b drafts so the sentence reads naturally; they are NOT the production corpus
(``signification_part0b_v1``, NEXT-ADMIT-01, tested in ``test_part0_admission.py``).
All births are synthetic (lat/long 0, UTC).
"""

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest
from consultation_quality_benchmark import FORBIDDEN_SYNTHESIS_WORDS, PROSE_ID_PATTERN
from test_career_answer_wording import _birth

from astrologer.application import period_themes as period_themes_module
from astrologer.application.analyze import (
    DeterministicAnalysisRequest,
    DeterministicAnalysisService,
)
from astrologer.application.answer import AskJyotAIService
from astrologer.application.context import DeterministicAstrologyContextService
from astrologer.application.period_themes import PERIOD_THEMES_CLOSING, build_period_themes
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.composition import DeterministicAnswerComposer
from astrologer.composition.comparison_guard import ranking_violation
from astrologer.composition.models import DetailedComposedAnswer
from astrologer.evidence import InterpretationEvidenceBuilder
from astrologer.knowledge.models import ReviewCategory, ReviewRecord, ReviewStatus
from astrologer.knowledge.signification import (
    EMPTY_SIGNIFICATION_CORPUS,
    EMPTY_SIGNIFICATION_MANIFEST,
    PERIOD_THEMES_TEMPLATE_VERSION,
    ApprovedTerm,
    LordshipPrincipleRecord,
    SignificationCorpus,
    SignificationCorpusError,
    SignificationEntry,
    admit_entries,
)
from astrologer.timing_rules.service import CareerTimingAnalysisService

_AS_OF = datetime(2026, 1, 1, tzinfo=ZoneInfo("Asia/Kolkata"))
# Synthetic: Rahu MD (in the 11th); Saturn AD (rules 3, 4; in the 10th) to Jan 22, then
# Mercury AD (rules 8, 11; in the 7th).
RAHU_MERCURY = _birth("1978-06-12", "18:00:00")
_REVIEWED = datetime(2026, 11, 23, tzinfo=UTC)


def _review(
    status: ReviewStatus = ReviewStatus.REVIEWED,
    reviewer: str = "Fixture Reviewer (synthetic)",
    category: ReviewCategory = ReviewCategory.INTERPRETATION_REVIEW,
) -> ReviewRecord:
    return ReviewRecord(category=category, status=status, reviewer=reviewer, reviewed_at=_REVIEWED)


def _entry(kind: str, subject: str, *displays: str, **review: object) -> SignificationEntry:
    return SignificationEntry(
        subject_kind=kind,  # type: ignore[arg-type]
        subject=subject,
        terms=tuple(ApprovedTerm(sanskrit=f"fixture-{d}", display=d) for d in displays),
        rule_id=f"fixture.signification.{kind}.{subject}",
        rule_version="v1",
        source_locator="FIXTURE, not a source",
        governance_record_ref="FIXTURE-GR-0",
        review=_review(**review),  # type: ignore[arg-type]
    )


def _x18(scope: str = "MAHADASHA_AND_ANTARDASHA", **overrides: object) -> LordshipPrincipleRecord:
    fields: dict[str, object] = {
        "rule_id": "fixture.lordship.x18",
        "rule_version": "v1",
        "approved_template_version": PERIOD_THEMES_TEMPLATE_VERSION,
        "scope": scope,
        "source_locator": "FIXTURE, not a source",
        "governance_record_ref": "FIXTURE-GR-0",
        "review": _review(),
        **overrides,
    }
    return LordshipPrincipleRecord(**fields)  # type: ignore[arg-type]


ENTRIES = (
    _entry("graha", "mercury", "speech"),
    _entry("graha", "saturn", "service"),
    _entry("graha", "rahu", "forces"),
    _entry("bhava", "3", "valour", "counsel"),
    _entry("bhava", "7", "trade"),
    _entry("bhava", "10", "royal authority", "honour"),
    _entry("bhava", "11", "gain"),
)


def _corpus(entries=ENTRIES, principle=None) -> SignificationCorpus:  # type: ignore[no-untyped-def]
    return admit_entries("fixture.signification", "v1", entries, principle)


def _answer(corpus: SignificationCorpus | None, year: int = 2028) -> DetailedComposedAnswer:
    provider = SwissEphemerisProvider()
    service = AskJyotAIService(
        DeterministicAnalysisService(DeterministicAstrologyContextService(provider)),
        InterpretationEvidenceBuilder(),
        DeterministicAnswerComposer(),
        CareerTimingAnalysisService(provider),
        signification_corpus=corpus,
    )
    request = DeterministicAnalysisRequest(
        birth_input=RAHU_MERCURY, as_of=_AS_OF, question=f"How is my career in {year}?"
    )
    return service.answer(request).answers[0]


def _themes(answer: DetailedComposedAnswer):  # type: ignore[no-untyped-def]
    return next((s for s in answer.consultation_sections if s.kind == "period_themes"), None)


# --- The empty (NEXT-SIG-01) corpus produces nothing -------------------------------------------


def test_empty_corpus_produces_no_section() -> None:
    assert EMPTY_SIGNIFICATION_MANIFEST.entries == ()
    assert EMPTY_SIGNIFICATION_MANIFEST.lordship_principle is None
    assert EMPTY_SIGNIFICATION_CORPUS.lordship_principle is None
    assert EMPTY_SIGNIFICATION_CORPUS.graha("jupiter") is None
    answer = _answer(EMPTY_SIGNIFICATION_CORPUS)
    plan = answer.career_answer_plan
    assert plan is not None
    assert plan.period_themes == ()
    assert plan.signification_corpus_version == "jyotish.signification.production@v0-empty"
    assert _themes(answer) is None


# --- A fixture-admitted corpus fills -----------------------------------------------------------


def test_admitted_entries_and_x18_fill_period_themes() -> None:
    answer = _answer(_corpus(principle=_x18()))
    section = _themes(answer)
    assert section is not None
    assert [s.text for s in section.synthesis_sentences] == [
        "During your Rahu Mahadasha throughout 2028, the reviewed significations associated "
        "with Rahu (forces) and with the house it occupies (11th house: gain) are the themes "
        "the texts associate with this period.",
        "During your Saturn Antardasha (Jan 1–Jan 22), the reviewed significations associated "
        "with Saturn (service) and with the houses it rules and occupies (3rd house: valour, "
        "counsel; 10th house: royal authority, honour) are the themes the texts associate "
        "with this period.",
        "During your Mercury Antardasha (Jan 22–Dec 31), the reviewed significations "
        "associated with Mercury (speech) and with the houses it rules and occupies (11th "
        "house: gain; 7th house: trade) are the themes the texts associate with this period.",
        PERIOD_THEMES_CLOSING,
    ]
    kinds = [s.kind for s in answer.consultation_sections]
    # Directly after the glance (NEXT-ADMIT-01).
    assert kinds.index("period_themes") == kinds.index("glance") + 1
    assert answer.answer == " ".join(s.text for s in answer.consultation_sections)
    plan = answer.career_answer_plan
    assert plan is not None and plan.signification_corpus_version == "fixture.signification@v1"


def test_rahu_occupied_house_only_is_named_when_that_house_is_admitted() -> None:
    # Rahu rules no sign; it occupies the 11th, so "the house it occupies" (not "rules").
    entries = (_entry("bhava", "11", "gain"),)
    themes = _answer(_corpus(entries, _x18("MAHADASHA_ONLY"))).career_answer_plan.period_themes  # type: ignore[union-attr]
    assert themes[0].text == (
        "During your Rahu Mahadasha throughout 2028, the reviewed significations associated "
        "with the house it occupies (11th house: gain) are the themes the texts associate "
        "with this period."
    )
    assert themes[0].fact_ids[-1] == "jyotish.dasha_linkage.v1.lord.rahu.placement_house"


def test_every_sentence_maps_to_known_facts_rules_and_versions() -> None:
    answer = _answer(_corpus(principle=_x18()))
    plan = answer.career_answer_plan
    assert plan is not None
    known = {s.segment_id for s in plan.dasha_segments}
    for item in plan.dasha_linkages:
        known |= set(item.linkage.fact_ids())
    rule_ids = {f"{e.rule_id}@{e.rule_version}" for e in ENTRIES} | {"fixture.lordship.x18@v1"}
    for sentence in plan.period_themes[:-1]:
        assert sentence.fact_ids and set(sentence.fact_ids) <= known
        assert "fixture.lordship.x18@v1" in sentence.rule_ids
        assert set(sentence.rule_ids) <= rule_ids
        assert PERIOD_THEMES_TEMPLATE_VERSION in sentence.calc_method_ids
        assert not PROSE_ID_PATTERN.search(sentence.text)


def test_mahadasha_only_scope_omits_antardasha_lords() -> None:
    themes = _answer(_corpus(principle=_x18("MAHADASHA_ONLY"))).career_answer_plan.period_themes  # type: ignore[union-attr]
    assert [t.text.split(",")[0] for t in themes[:-1]] == [
        "During your Rahu Mahadasha throughout 2028"
    ]


# --- Non-admitted fixtures do not fill ---------------------------------------------------------


@pytest.mark.parametrize(
    ("entries", "principle"),
    [
        (ENTRIES, None),  # 0b entries admitted, X18 not
        ((), "x18"),  # X18 admitted, no 0b entries
        ((_entry("graha", "jupiter", "knowledge"), _entry("bhava", "5", "learning")), "x18"),
    ],
    ids=["no-x18", "no-entries", "entries-irrelevant-to-these-periods"],
)
def test_section_is_absent_unless_both_gates_and_a_relevant_entry_are_admitted(
    entries, principle
) -> None:  # type: ignore[no-untyped-def]
    answer = _answer(_corpus(entries, _x18() if principle else None))
    assert answer.career_answer_plan.period_themes == ()  # type: ignore[union-attr]
    assert _themes(answer) is None


@pytest.mark.parametrize(
    "build",
    [
        lambda: _corpus((_entry("graha", "mercury", "speech", status=ReviewStatus.DRAFT),)),
        lambda: _corpus((_entry("graha", "mercury", "speech", reviewer="Claude (AI preparer)"),)),
        lambda: _corpus(
            (
                _entry(
                    "graha",
                    "mercury",
                    "speech",
                    category=ReviewCategory.SOURCE_VERIFICATION,
                ),
            )
        ),
        lambda: _corpus((_entry("graha", "jupiter", "good career"),)),
        lambda: _corpus((_entry("graha", "jupiter", "strongest"),)),
        lambda: _corpus((_entry("bhava", "10", "brings promotion"),)),
        lambda: _corpus((_entry("graha", "mars", "valour"), _entry("graha", "mars", "valour"))),
        lambda: _corpus((), _x18(approved_template_version="period-themes-v0")),
        lambda: _corpus((), _x18(review=_review(status=ReviewStatus.DRAFT))),
    ],
    ids=[
        "draft-review",
        "ai-reviewer",
        "wrong-review-category",
        "evaluative-term",
        "ranking-term",
        "causal-event-term",
        "duplicate-subject",
        "x18-wrong-template",
        "x18-draft",
    ],
)
def test_admission_rejects_unreviewed_or_forbidden_material(build) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(SignificationCorpusError):
        build()


def test_unknown_subjects_are_rejected_by_the_schema() -> None:
    with pytest.raises(ValueError):
        _entry("graha", "pluto", "x")
    with pytest.raises(ValueError):
        _entry("bhava", "13", "x")


def test_corpora_are_created_only_by_admission() -> None:
    with pytest.raises(TypeError):
        SignificationCorpus(token=object(), manifest=EMPTY_SIGNIFICATION_MANIFEST)


# --- Guards -------------------------------------------------------------------------------------


def test_generated_text_passes_the_ranking_causal_and_evaluative_guards() -> None:
    section = _themes(_answer(_corpus(principle=_x18())))
    assert section is not None
    for sentence in section.synthesis_sentences:
        assert ranking_violation(sentence.text) is None, sentence.text
        assert not FORBIDDEN_SYNTHESIS_WORDS.search(sentence.text.lower()), sentence.text


def test_a_guard_hit_drops_the_sentence_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    plan = _answer(None).career_answer_plan
    assert plan is not None
    corpus = _corpus(principle=_x18())
    assert build_period_themes(plan.dasha_linkages, plan.dasha_segments, corpus, 2028)
    monkeypatch.setattr(period_themes_module, "term_violation", lambda text: "flagged")
    assert build_period_themes(plan.dasha_linkages, plan.dasha_segments, corpus, 2028) == ()


# --- NEXT-THEMES-01: presentation only ---------------------------------------------------------


def _glance_themes(answer: DetailedComposedAnswer) -> str:
    glance = next(s for s in answer.consultation_sections if s.kind == "glance")
    return next(s.text for s in glance.synthesis_sentences if s.text.startswith("Period themes"))


def test_same_lord_mahadasha_and_antardasha_in_the_same_window_is_emitted_once() -> None:
    # Synthetic: Rahu MD begins Feb 9, 2020 with its own Rahu AD, which outlasts the year.
    themes = _answer(_corpus(principle=_x18()), 2020).career_answer_plan.period_themes  # type: ignore[union-attr]
    texts = [s.text for s in themes]
    assert texts[1] == (
        "During your Rahu Mahadasha and Antardasha (Feb 9–Dec 31), the reviewed significations "
        "associated with Rahu (forces) and with the house it occupies (11th house: gain) are "
        "the themes the texts associate with this period."
    )
    assert sum("Rahu" in text for text in texts) == 1
    assert not any("Rahu Antardasha" in text for text in texts)
    assert texts[-1] == PERIOD_THEMES_CLOSING


def test_same_lord_merged_throughout_the_year() -> None:
    themes = _answer(_corpus(principle=_x18()), 2021).career_answer_plan.period_themes  # type: ignore[union-attr]
    assert [s.text for s in themes][0].startswith(
        "During your Rahu Mahadasha and Antardasha throughout 2021, "
    )
    assert len(themes) == 2  # one line, then the closing


def test_same_lord_over_different_windows_stays_two_lines() -> None:
    # Rahu MD runs all of 2022; its own Rahu AD ends part-way through, so the windows differ.
    texts = [
        s.text
        for s in _answer(_corpus(principle=_x18()), 2022).career_answer_plan.period_themes  # type: ignore[union-attr]
    ]
    assert any(t.startswith("During your Rahu Mahadasha throughout 2022") for t in texts)
    assert any(t.startswith("During your Rahu Antardasha (Jan 1–") for t in texts)
    assert not any("Mahadasha and Antardasha" in t for t in texts)


def test_glance_lists_each_lord_once_with_only_its_houses() -> None:
    text = _glance_themes(_answer(_corpus(principle=_x18())))
    assert text == (
        "Period themes: Rahu: 11th house · Saturn: 3rd, 10th houses · Mercury: 11th, 7th houses."
    )
    # The full terms stay in the Period themes section, never in the glance.
    for entry in ENTRIES:
        for term in entry.terms:
            assert term.display not in text
    merged = _glance_themes(_answer(_corpus(principle=_x18()), 2020))
    assert merged == "Period themes: Mars: 10th house · Rahu: 11th house · Moon: 10th house."
    assert merged.count("Rahu") == 1


def test_glance_names_a_lord_with_no_admitted_house_alone() -> None:
    # Only Mercury's own entry is admitted; its houses (11th, 7th) have none.
    entries = (_entry("graha", "mercury", "speech"),)
    assert _glance_themes(_answer(_corpus(entries, _x18()))) == "Period themes: Mercury."
