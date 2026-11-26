"""NEXT-MARRIAGE-02: topic-tagged significations, provisional Marriage terms, D9 facts.

All births are synthetic (lat/long 0, UTC); none describes a real person.
"""

import json

import pytest
from test_career_answer_wording import _ask
from test_marriage import (
    _AS_OF,
    BY_SEVENTH_LORD_HOUSE,
    OUTLOOK,
    TIMING,
    YEAR,
    _answer,
    _consult,
    answer_chart,
)

from astrologer.application.analyze import DeterministicAnalysisRequest
from astrologer.application.answer import AskJyotAIService, _d1_fact_values
from astrologer.application.marriage import LIMIT_TIMING_PERIODS_ONLY, THEMES_PENDING
from astrologer.application.marriage_d9 import D9_FRAMING, d9_marriage_factors
from astrologer.application.provisional import provisional_signification_items
from astrologer.astrology.derived_facts import SIGN_RULERS
from astrologer.astrology.vargas import DivisionalChartType, VargaEngine
from astrologer.composition.marriage_guard import marriage_wording_violation
from astrologer.composition.models import DetailedComposedAnswer
from astrologer.knowledge.models import JyotishDomain
from astrologer.knowledge.provisional import PROVISIONAL_AUTHOR_AI_DRAFTED
from astrologer.knowledge.provisional_signification import (
    ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS,
    SECOND_HOUSE_FAMILY,
    SEVENTH_HOUSE_SPOUSE,
    VENUS_KARAKA_SPOUSE,
    ProvisionalSignification,
)
from astrologer.knowledge.signification import admit_entries
from astrologer.knowledge.signification_admit02_v1 import (
    ACTIVE_SIGNIFICATION_CORPUS,
    PRODUCTION_SIGNIFICATION_MANIFEST_V3,
)
from astrologer.knowledge.signification_part0b_v1 import (
    PRODUCTION_SIGNIFICATION_MANIFEST,
    SIGNIFICATION_MANIFEST_V1,
)
from astrologer.knowledge.signification_tags import (
    ACTIVE_SIGNIFICATION_TAG_SET,
    DomainTag,
    SignificationTagSet,
    TermTags,
    domain_view,
)

CAREER_TERMS = ("trade or business", "adviser or counsellor")
MARRIAGE, CAREER = JyotishDomain.MARRIAGE, JyotishDomain.CAREER


def _themes(answer: DetailedComposedAnswer) -> str | None:
    return next((s.text for s in answer.consultation_sections if s.kind == "period_themes"), None)


@pytest.fixture(scope="module")
def answers() -> dict[tuple[int, str], DetailedComposedAnswer]:
    return {
        (house, question): _answer(birth, question)
        for house, birth in BY_SEVENTH_LORD_HOUSE.items()
        for question in (OUTLOOK, TIMING, YEAR)
    }


# --- 1. Tagging ------------------------------------------------------------------------------


def test_every_reviewed_term_is_tagged_career_reviewed_only() -> None:
    tags = ACTIVE_SIGNIFICATION_TAG_SET
    for manifest in (
        SIGNIFICATION_MANIFEST_V1,
        PRODUCTION_SIGNIFICATION_MANIFEST,
        PRODUCTION_SIGNIFICATION_MANIFEST_V3,
    ):
        assert f"{manifest.manifest_id}@{manifest.manifest_version}" in tags.covers_corpora
        for entry in manifest.entries:
            for term in entry.terms:
                key = (entry.subject_kind, entry.subject, term.sanskrit)
                assert tags.reviewed_domains(key) == frozenset({CAREER}), key
    assert all(tag.status == "reviewed" for term in tags.terms for tag in term.tags)


def test_career_view_is_the_corpus_itself_and_marriage_view_has_no_term() -> None:
    assert domain_view(ACTIVE_SIGNIFICATION_CORPUS, CAREER, ACTIVE_SIGNIFICATION_TAG_SET) is (
        ACTIVE_SIGNIFICATION_CORPUS
    )
    marriage = domain_view(ACTIVE_SIGNIFICATION_CORPUS, MARRIAGE, ACTIVE_SIGNIFICATION_TAG_SET)
    assert marriage.entries == ()
    assert marriage.version == "jyotish.signification.production@v3+marriage"
    assert marriage.lordship_principle == ACTIVE_SIGNIFICATION_CORPUS.lordship_principle


def test_a_term_tagged_marriage_is_shown_in_marriage_only_that_term() -> None:
    # व्यापार tagged Career AND Marriage (a hypothetical tag set): the 7th house keeps it in a
    # Marriage view; every other term is dropped.
    tags = ACTIVE_SIGNIFICATION_TAG_SET.model_copy(
        update={
            "terms": tuple(
                term.model_copy(
                    update={
                        "tags": (
                            *term.tags,
                            DomainTag(domain=MARRIAGE, status="reviewed"),
                        )
                    }
                )
                if term.key == ("bhava", "7", "व्यापार")
                else term
                for term in ACTIVE_SIGNIFICATION_TAG_SET.terms
            )
        }
    )
    view = domain_view(ACTIVE_SIGNIFICATION_CORPUS, MARRIAGE, tags)
    assert [(e.subject_kind, e.subject) for e in view.entries] == [("bhava", "7")]
    seventh = view.bhava(7)
    assert seventh is not None and [t.display for t in seventh.terms] == ["trade or business"]


def test_an_untagged_term_in_a_covered_corpus_is_shown_nowhere() -> None:
    tags = ACTIVE_SIGNIFICATION_TAG_SET.model_copy(
        update={
            "terms": tuple(
                term
                for term in ACTIVE_SIGNIFICATION_TAG_SET.terms
                if term.key != ("graha", "venus", "सचिवः")
            )
        }
    )
    view = domain_view(ACTIVE_SIGNIFICATION_CORPUS, CAREER, tags)
    assert view is not ACTIVE_SIGNIFICATION_CORPUS
    assert view.graha("venus") is None  # its only term was untagged
    assert view.graha("jupiter") is not None


def test_a_corpus_the_tag_set_does_not_cover_is_career_only() -> None:
    entry = ACTIVE_SIGNIFICATION_CORPUS.entries[0]
    fixture = admit_entries("fixture.signification", "v1", (entry,))
    assert domain_view(fixture, CAREER, ACTIVE_SIGNIFICATION_TAG_SET) is fixture
    assert domain_view(fixture, MARRIAGE, ACTIVE_SIGNIFICATION_TAG_SET).entries == ()


def test_a_reviewed_tag_set_rejects_provisional_tags() -> None:
    with pytest.raises(ValueError, match="reviewed tags only"):
        SignificationTagSet(
            tag_set_id="fixture.tags",
            tag_set_version="v1",
            covers_corpora=("x@v1",),
            basis="test",
            terms=(
                TermTags(
                    subject_kind="bhava",
                    subject="7",
                    sanskrit="व्यापार",
                    tags=(DomainTag(domain=MARRIAGE, status="provisional"),),
                ),
            ),
        )


def test_a_marriage_answer_never_shows_career_terms(answers: dict) -> None:  # type: ignore[type-arg]
    every_career_term = {t.display for e in ACTIVE_SIGNIFICATION_CORPUS.entries for t in e.terms}
    assert set(CAREER_TERMS) <= every_career_term
    for key, answer in answers.items():
        for term in every_career_term:
            assert term not in answer.answer, (key, term)
        for section in answer.consultation_sections:
            assert not any(
                r.startswith("bphs.signification.")
                for s in section.synthesis_sentences
                for r in s.rule_ids
            ), key


def test_a_career_answer_is_unchanged_by_tagging() -> None:
    # The tag set shows every reviewed term for Career, so the Career answer equals the one
    # built from the corpus directly (no filtering at all).
    request = DeterministicAnalysisRequest(
        birth_input=BY_SEVENTH_LORD_HOUSE[9], as_of=_AS_OF, question="How is my career in 2027?"
    )
    tagged = _ask().answer(request).answers[0]
    untagged_service: AskJyotAIService = _ask()
    untagged_service._signification_tags = ACTIVE_SIGNIFICATION_TAG_SET.model_copy(
        update={"covers_corpora": ("none@v0",)}  # untagged corpus: Career only, no filtering
    )
    untagged = untagged_service.answer(request).answers[0]
    assert tagged == untagged
    assert "period_themes" in [s.kind for s in tagged.consultation_sections]


# --- 4. Period themes with the toggle off ----------------------------------------------------


def test_period_themes_list_periods_only_with_the_pending_line(answers: dict) -> None:  # type: ignore[type-arg]
    seen = 0
    for (house, question), answer in answers.items():
        themes = _themes(answer)
        if question == OUTLOOK:
            assert themes is None
            continue
        if themes is None:  # no 7th-lord / Venus period in the range
            continue
        seen += 1
        assert themes.endswith(THEMES_PENDING)
        assert "reviewed themes" not in themes and "house (" not in themes
        assert answer.consultation_sections[-1].text == LIMIT_TIMING_PERIODS_ONLY
        assert answer.answer.count(THEMES_PENDING) == 1, (house, question)
    assert seen >= 12


# --- 2. Provisional Marriage significations --------------------------------------------------


def test_provisional_terms_and_confidence() -> None:
    corpus = ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS
    assert corpus.release_id == "jyotish.provisional.signification@v1"
    found = {(t.subject_kind, t.subject, t.sanskrit, t.display): t for t in corpus.terms}
    assert set(found) == {
        ("bhava", "7", "जाया", "spouse"),
        ("graha", "venus", "कलत्र", "spouse (kāraka)"),
        ("bhava", "2", "कुटुम्ब", "family"),
    }
    assert SEVENTH_HOUSE_SPOUSE.justification.confidence.value == "high"
    assert VENUS_KARAKA_SPOUSE.justification.confidence.value == "high"
    assert SECOND_HOUSE_FAMILY.justification.confidence.value == "low"
    for term in corpus.terms:
        j = term.justification
        assert term.tags == (DomainTag(domain=MARRIAGE, status="provisional"),)
        assert j.author == PROVISIONAL_AUTHOR_AI_DRAFTED
        assert "PDF p." in j.locator and j.original_text.endswith("॥") and j.transcription_notes
        assert term.sanskrit in j.original_text and term.sanskrit in term.statement
        # Only terms the text gives: no "marriage" or "partnership" term was drafted.
        assert "marriage" not in term.display and "partnership" not in term.display
        for text in (term.statement, j.interpretive_reasoning, term.translation_held_reason or ""):
            assert marriage_wording_violation(text) is None, text


def test_provisional_term_admission_guards() -> None:
    base = SEVENTH_HOUSE_SPOUSE.model_dump()
    with pytest.raises(ValueError, match="start with"):
        ProvisionalSignification(**{**base, "term_id": "bphs.signification.bhava.7"})
    with pytest.raises(ValueError, match="provisional tags only"):
        ProvisionalSignification(
            **{**base, "tags": ({"domain": "marriage", "status": "reviewed"},)}
        )
    with pytest.raises(ValueError, match="reviewed"):
        ProvisionalSignification(**{**base, "statement": "The reviewed text lists जाया."})
    with pytest.raises(ValueError, match="marriage wording"):
        ProvisionalSignification(**{**base, "statement": "जाया: marriage may face delay."})


def test_items_carry_the_chart_subject_badge_and_justification() -> None:
    facts = _d1_fact_values(answer_chart(BY_SEVENTH_LORD_HOUSE[12]))
    items = provisional_signification_items(
        ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS, facts, "marriage"
    )
    assert [item.rule_id for item in items] == [
        t.term_id for t in ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS.terms
    ]
    by_id = {item.rule_id: item for item in items}
    seventh = by_id[SEVENTH_HOUSE_SPOUSE.term_id]
    sign = str(facts["jyotish.d1.house.7.sign"]).title()
    lord = str(facts["jyotish.d1.house.7.lord"]).title()
    assert seventh.placement_explanation == (
        f"Provisional signification: your D1 7th house, {sign}, whose lord is {lord}."
    )
    assert seventh.badge == "Provisional · high confidence"
    assert by_id[SECOND_HOUSE_FAMILY.term_id].badge == "Provisional · low confidence"
    for item in items:
        assert item.kind == "signification" and item.domain == "marriage"
    # The 7th- and 2nd-house verses also list death: translation kept for the review pack.
    assert seventh.justification.draft_translation is None and seventh.justification.held_reason
    venus = by_id[VENUS_KARAKA_SPOUSE.term_id]
    assert venus.justification.draft_translation == (
        VENUS_KARAKA_SPOUSE.justification.draft_translation
    )
    # Other domains get none.
    assert (
        provisional_signification_items(ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS, facts, "career")
        == ()
    )


@pytest.mark.parametrize("question", [OUTLOOK, TIMING, YEAR])
def test_significations_only_with_the_toggle(question: str) -> None:
    birth = BY_SEVENTH_LORD_HOUSE[9]
    off = _consult(question, birth, False)
    on = _consult(question, birth, True)
    assert off["provisional_interpretations"] == []
    kinds = [item["kind"] for item in on["provisional_interpretations"]]
    assert kinds.count("signification") == 3
    strip = {k: v for k, v in on.items() if k != "provisional_interpretations"}
    assert strip == {k: v for k, v in off.items() if k != "provisional_interpretations"}
    text = json.dumps(strip, ensure_ascii=False)
    for term in ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS.terms:
        assert term.term_id not in text and term.statement not in text


def test_career_answers_get_no_provisional_signification() -> None:
    on = _consult("How is my career in 2027?", BY_SEVENTH_LORD_HOUSE[9], True)
    assert all(item["kind"] == "rule" for item in on["provisional_interpretations"])


# --- 3. D9 calculated facts ------------------------------------------------------------------


def _d9(house: int) -> tuple[str, ...]:
    chart = answer_chart(BY_SEVENTH_LORD_HOUSE[house])
    return tuple(s.text for s in d9_marriage_factors(chart, _d1_fact_values(chart)))


@pytest.mark.parametrize("house", sorted(BY_SEVENTH_LORD_HOUSE))
def test_d9_factors_match_the_varga_engine(house: int) -> None:
    chart = answer_chart(BY_SEVENTH_LORD_HOUSE[house])
    d1 = _d1_fact_values(chart)
    d9 = VargaEngine().calculate(chart, DivisionalChartType.D9)
    planets = {p.body.value: p for p in d9.planets}
    lagna = d9.ascendant.sign
    seventh_sign = next(h.sign for h in d9.houses if h.number == 7)
    lord = SIGN_RULERS[seventh_sign].value
    lines = _d9(house)
    assert lines[0] == f"Your D9 Lagna is {lagna.value.title()}."
    if lord == "venus":
        assert lines[1] == f"Your D9 7th house is {seventh_sign.value.title()}; its lord is Venus."
        assert lines[2].startswith("Venus, your D9 7th lord, is in")
    else:
        assert lines[1] == (
            f"Your D9 7th house is {seventh_sign.value.title()}; its lord, {lord.title()}, is "
            f"in the {_ord(planets[lord].house_number)} house of your D9 chart."
        )
        assert lines[2] == (
            f"Venus is in {planets['venus'].sign.value.title()}, in the "
            f"{_ord(planets['venus'].house_number)} house of your D9 chart."
        )
    d1_lord = str(d1["jyotish.d1.house.7.lord"])
    d1_sign = next(p.sign for p in chart.planets if p.body.value == d1_lord)
    same = d1_sign is planets[d1_lord].sign
    assert ("so it is vargottama" in lines[3]) is same
    assert ("so it is not vargottama" in lines[3]) is (not same)
    assert lines[-1] == D9_FRAMING


def test_vargottama_true_and_false_cases_exist() -> None:
    assert "so it is vargottama" in _d9(1)[3]  # Mercury, Sagittarius in D1 and D9
    assert "so it is not vargottama" in _d9(2)[3]  # Venus, Taurus in D1, Gemini in D9


def test_d9_section_in_every_marriage_answer_with_fact_ids(answers: dict) -> None:  # type: ignore[type-arg]
    for key, answer in answers.items():
        section = next(s for s in answer.consultation_sections if s.kind == "d9_factors")
        *facts, framing = section.synthesis_sentences
        assert framing.text == D9_FRAMING, key
        assert all(sentence.fact_ids for sentence in facts), key
        assert all("jyotish-d9-derived-facts-v1" in sentence.calc_method_ids for sentence in facts)
        assert marriage_wording_violation(section.text) is None


def _ord(number: int) -> str:
    suffix = (
        "th" if 10 <= number % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    )
    return f"{number}{suffix}"
