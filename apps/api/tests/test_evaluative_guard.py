"""Evaluative-word guard: LLM narrative (fake transports) and deterministic template output.

Synthetic facts and synthetic births only.  No real model is called: the HANDOVER gate keeps
``LLM_ENABLED`` off until this guard and the ranking-word guard pass against a real model on
the full benchmark.
"""

import json
from pathlib import Path
from typing import Any

import pytest
from test_analyze_api import _matched_career_detailed, _NarrativeTransport, _senior_client
from test_analyze_api import _matched_career_request as _career_request
from test_interpretation_evidence import (
    _BUILDER,
    FACT_ID,
    _FakeTransport,
    _governed_items,
    _selection,
)

from astrologer.common.config import Settings
from astrologer.composition import AnswerComposer, SeniorAstrologerComposer
from astrologer.composition.comparison_guard import RANKING_LANGUAGE
from astrologer.composition.composer import AnswerCompositionError
from astrologer.composition.evaluative_guard import EVALUATIVE_LANGUAGE, evaluative_violation
from astrologer.composition.models import CompositionProviderRequest, CompositionProviderResponse
from astrologer.knowledge.signification import term_violation
from astrologer.knowledge.signification_part0b_v1 import PRODUCTION_SIGNIFICATION_MANIFEST
from astrologer.questions.models import QuestionDomain
from astrologer.rules.models import Fact, FactSet

RESULTS_V15 = Path(__file__).parent / "fixtures" / "consultation_quality_v15_results.json"
# The admitted 10th-lord-in-9th Career statement contains "good" ("good companions or friends").
_TENTH_IN_NINTH = FactSet(facts=(Fact(fact_id=FACT_ID, value=9),))


# --- The guard itself ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "word",
    [
        "favourable",
        "favorable",
        "unfavourable",
        "auspicious",
        "inauspicious",
        "strong",
        "weak",
        "good",
        "bad",
        "lucky",
        "unlucky",
        "fortunate",
        "unfortunate",
        "positive",
        "negative",
        "excellent",
        "promising",
        "benefic",
        "malefic",
    ],
)
def test_guard_flags_evaluative_words_in_any_case(word: str) -> None:
    assert evaluative_violation(f"This period is {word}.") == word
    assert evaluative_violation(f"This period is {word.upper()}.") == word.upper()


@pytest.mark.parametrize(
    "text",
    [
        "The reviewed significations associated with the 9th house: fortune, dharma.",
        "Saturn rules your 8th and 9th houses.",
        "No strength model is admitted.",
        "These broader life themes do not by themselves establish a profession.",
    ],
)
def test_guard_passes_neutral_text(text: str) -> None:
    assert evaluative_violation(text) is None


def test_admitted_text_is_exempt_only_where_quoted_verbatim() -> None:
    admitted = "The text associates this placement with good companions or friends."
    assert evaluative_violation(f"Context: {admitted}", (admitted,)) is None
    # The same word outside the admitted passage still trips the guard.
    assert evaluative_violation(f"Context: {admitted} This is good.", (admitted,)) == "good"
    # A paraphrase is not the admitted text.
    assert evaluative_violation("It mentions good friends.", (admitted,)) == "good"


def test_evaluative_guard_is_a_separate_list_from_the_ranking_guard() -> None:
    # Parallel guards: "good", "lucky" and "auspicious" alone are not ranking words.
    for word in ("good", "lucky", "auspicious", "strong"):
        assert RANKING_LANGUAGE.search(word) is None
        assert EVALUATIVE_LANGUAGE.search(word) is not None


def test_signification_term_check_includes_the_evaluative_guard() -> None:
    assert term_violation("lucky") == "lucky"
    for entry in PRODUCTION_SIGNIFICATION_MANIFEST.entries:
        for term in entry.terms:
            assert evaluative_violation(term.display) is None, term.display


# --- LLM path: AnswerComposer (fake transport) -------------------------------------------------


def _career_evidence():  # type: ignore[no-untyped-def]
    return _BUILDER.build(_selection(QuestionDomain.CAREER, _governed_items(_TENTH_IN_NINTH)))


def _compose(answer: str):  # type: ignore[no-untyped-def]
    transport = _FakeTransport(json.dumps({"answer": answer, "timing_answered": False}))
    return AnswerComposer(transport).compose("How is my career?", _career_evidence())


def test_composer_rejects_evaluative_words_outside_admitted_text() -> None:
    with pytest.raises(AnswerCompositionError) as raised:
        _compose("Your chart shows a very favourable career placement.")
    assert raised.value.reason_code == "evaluative_language"


def test_composer_accepts_admitted_text_that_itself_contains_good() -> None:
    evidence = _career_evidence()
    statement = evidence.selected_matched[0].reviewed_statement
    assert "good" in statement
    assert _compose(f"Reviewed context: {statement}").answer.endswith(statement)


def test_composer_rejects_good_added_next_to_admitted_text() -> None:
    statement = _career_evidence().selected_matched[0].reviewed_statement
    with pytest.raises(AnswerCompositionError) as raised:
        _compose(f"{statement} Overall this is a good chart.")
    assert raised.value.reason_code == "evaluative_language"


# --- LLM path: SeniorAstrologerComposer (fake transport) ---------------------------------------


class _EvaluativeTransport:
    """A structurally valid, closed-phrase narrative whose summary is replaced."""

    def __init__(self, summary: str) -> None:
        self.summary = summary
        self.calls = 0

    def complete(self, request: CompositionProviderRequest) -> CompositionProviderResponse:
        self.calls += 1
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


@pytest.mark.parametrize(
    "summary",
    [
        "This is an auspicious placement for your career.",
        "Your 10th lord is strong here.",
        "This is a lucky chart.",
    ],
)
def test_senior_composer_rejects_evaluative_narrative(summary: str) -> None:
    detailed, evidence = _matched_career_detailed()
    with pytest.raises(AnswerCompositionError) as raised:
        SeniorAstrologerComposer(_EvaluativeTransport(summary)).compose(
            "How is my career?", detailed, evidence
        )
    assert raised.value.reason_code == "evaluative_language"


def test_evaluative_narrative_falls_back_to_the_deterministic_answer() -> None:
    transport = _EvaluativeTransport("This is a very favourable period for you.")
    response = _senior_client(transport).post(  # type: ignore[arg-type]
        "/api/v1/analyze", json=_career_request("How is my career?")
    )
    assert response.status_code == 200
    answer = response.json()["answers"][0]
    assert transport.calls == 1
    assert answer["narrative"] is None
    assert answer["reviewed_interpretations"]


def test_valid_senior_narrative_is_still_accepted() -> None:
    response = _senior_client(_NarrativeTransport()).post(
        "/api/v1/analyze", json=_career_request("How is my career?")
    )
    assert response.json()["answers"][0]["narrative"]["summary"]


# --- Template path: every benchmark response, outside admitted text ----------------------------


def _admitted(answer: dict[str, Any]) -> list[str]:
    passages = list(answer.get("reviewed_interpretations") or [])
    for claim in (answer.get("claim_ledger") or {}).get("claims") or []:
        if claim.get("permitted_wording"):
            passages.append(claim["permitted_wording"])
    for item in answer.get("evidence") or []:
        passages.extend(
            v for k, v in item.items() if k in {"reviewed_statement", "scope_notes"} and v
        )
    terms = [
        term.display for entry in PRODUCTION_SIGNIFICATION_MANIFEST.entries for term in entry.terms
    ]
    return [*passages, *terms]


def _texts(value: Any) -> list[str]:
    if isinstance(value, dict):
        return [t for key, v in value.items() if key not in {"question"} for t in _texts(v)]
    if isinstance(value, list):
        return [t for v in value for t in _texts(v)]
    return [value] if isinstance(value, str) else []


def _prose(answer: dict[str, Any]) -> list[str]:
    texts = [answer.get("answer") or "", *(s["text"] for s in answer["consultation_sections"])]
    texts += [
        s["text"]
        for sec in answer["consultation_sections"]
        for s in sec.get("synthesis_sentences") or []
    ]
    if answer.get("career_comparison"):
        texts += _texts(answer["career_comparison"])
    return texts


def test_no_template_output_outside_admitted_text_is_evaluative() -> None:
    # The v15 fixture is exactly the live API output (frozen-benchmark test).
    results = json.loads(RESULTS_V15.read_text())
    checked = 0
    violations = []
    for row in [*results["journeys"], *results["comparison_journeys"]]:
        answers = row["initial"].get("answers", [])
        allowed = [p for answer in answers for p in _admitted(answer)]
        texts = [t for answer in answers for t in _prose(answer)]
        texts += [row["initial"].get("reply") or ""]
        texts += [(f.get("response") or {}).get("reply") or "" for f in row.get("followups", [])]
        for text in texts:
            checked += bool(text)
            if (word := evaluative_violation(text, allowed)) is not None:
                violations.append((row["id"], word, text[:120]))
    assert checked > 500
    assert violations == []


def test_template_answer_quoting_admitted_good_passes_only_through_the_exemption() -> None:
    # Synthetic birth: 10th lord in the 9th; the natal section quotes "good companions".
    from test_year_glance import _answer, _birth

    answer = _answer(_birth("1983-01-10", "12:00:00"), 2027)
    assert answer.claim_ledger is not None
    admitted = [claim.permitted_wording for claim in answer.claim_ledger.claims]
    natal = next(s.text for s in answer.consultation_sections if s.kind == "natal")
    assert "good companions or friends" in natal
    assert evaluative_violation(natal) == "good"
    for section in answer.consultation_sections:
        assert evaluative_violation(section.text, admitted) is None, section.kind
    assert evaluative_violation(answer.answer, admitted) is None


# --- The gate ----------------------------------------------------------------------------------


def test_llm_stays_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LLM_ENABLED", raising=False)
    assert Settings().llm_enabled is False
