"""Frozen consultation baseline and important acceptance gates."""

import json
import re
import subprocess
import sys
from pathlib import Path

from consultation_quality_benchmark import run

from astrologer.application.career_claims import (
    TIMING_FULL_TEXT_POINTER,
    timing_meaning_and_limit,
)
from astrologer.application.career_comparison import WHY_NO_RANKING
from astrologer.application.career_synthesis import WHY_FRAMING
from astrologer.application.detailed_answer import _NO_TIMING_RULE as NO_TIMING_RULE
from astrologer.timing_rules.models import (
    MoonVenusOwnExaltationTimingSourceRecord,
    TimingSourceRecord,
)

RESULTS = Path(__file__).parent / "fixtures" / "consultation_quality_v1_results.json"
RESULTS_V2 = Path(__file__).parent / "fixtures" / "consultation_quality_v2_results.json"
RESULTS_V3 = Path(__file__).parent / "fixtures" / "consultation_quality_v3_results.json"
RESULTS_V4 = Path(__file__).parent / "fixtures" / "consultation_quality_v4_results.json"
RESULTS_V5 = Path(__file__).parent / "fixtures" / "consultation_quality_v5_results.json"
RESULTS_V6 = Path(__file__).parent / "fixtures" / "consultation_quality_v6_results.json"
RESULTS_V7 = Path(__file__).parent / "fixtures" / "consultation_quality_v7_results.json"
RESULTS_V8 = Path(__file__).parent / "fixtures" / "consultation_quality_v8_results.json"
RESULTS_V9 = Path(__file__).parent / "fixtures" / "consultation_quality_v9_results.json"
RESULTS_V10 = Path(__file__).parent / "fixtures" / "consultation_quality_v10_results.json"
RESULTS_V11 = Path(__file__).parent / "fixtures" / "consultation_quality_v11_results.json"
RESULTS_V12 = Path(__file__).parent / "fixtures" / "consultation_quality_v12_results.json"
RESULTS_V13 = Path(__file__).parent / "fixtures" / "consultation_quality_v13_results.json"
RESULTS_V14 = Path(__file__).parent / "fixtures" / "consultation_quality_v14_results.json"
RESULTS_V15 = Path(__file__).parent / "fixtures" / "consultation_quality_v15_results.json"
RESULTS_V16 = Path(__file__).parent / "fixtures" / "consultation_quality_v16_results.json"
RESULTS_V17 = Path(__file__).parent / "fixtures" / "consultation_quality_v17_results.json"
RESULTS_V18 = Path(__file__).parent / "fixtures" / "consultation_quality_v18_results.json"
RESULTS_V19 = Path(__file__).parent / "fixtures" / "consultation_quality_v19_results.json"
RESULTS_V20 = Path(__file__).parent / "fixtures" / "consultation_quality_v20_results.json"
RESULTS_V21 = Path(__file__).parent / "fixtures" / "consultation_quality_v21_results.json"
RESULTS_V22 = Path(__file__).parent / "fixtures" / "consultation_quality_v22_results.json"
PART0_RULE_IDS = {
    "bphs.d1.house_lord.10.equals_1.v1",
    "bphs.d1.house_lord.10.in_2_3_or_7.v1",
    "bphs.d1.house_lord.10.equals_8.v1",
}


def test_frozen_consultation_journeys_reproduce_v22_api_responses() -> None:
    actual = run()
    expected = json.loads(RESULTS_V22.read_text())
    assert actual == expected
    assert '"birth_input"' not in RESULTS_V22.read_text()
    assert actual["provisional_counts"] == {
        "corpus": "jyotish.provisional@v1",
        "requests": 48,
        "provisional_items_flag_off": 0,
        "reviewed_parts_identical_flag_on": 48,
        "provisional_items_flag_on": 1,
        "items_with_badge": 1,
        "items_with_full_justification": 1,
        "items_failing_guards": 0,
        "items_labelled_reviewed": 0,
        "provisional_ids_in_reviewed_parts": 0,
        "matched_rule_ids": {"provisional.bphs.d1.house_lord.5.equals_7.spirituality.v1": 1},
    }
    assert actual["fixdeg01_counts"] == {
        "dasha_context_sections": 18,
        "duplicate_occupancy_sentences_detected": 0,
        "sections_with_a_repeated_sentence": 0,
        "self_count_sentences_detected": 0,
        "same_lord_back_reference_lines": 1,
        "why_links_on_paused_or_withheld_rules": 0,
    }
    assert actual["admit02_counts"] == {
        "period_themes_sections": 12,
        "period_themes_sections_with_one_closing_at_end": 12,
        "period_themes_old_closing_detected": 0,
        "antardasha_theme_lines": 23,
        "antardasha_theme_lines_labelled_secondary": 23,
        "natal_sections": 12,
        "natal_sections_with_tenth_lord_dignity_fact": 12,
        "natal_sections_mentioning_adversaries_term": 0,
    }
    assert actual["bare_comparison_counts"] == {
        "journeys": 8,
        "with_prior_career_turn": 4,
        "clarified_then_compared": 4,
        "hard_gates": {"PASS": 8},
        "checks_failed": [],
    }
    assert actual["signification_counts"] == {
        "corpora_consulted": ["jyotish.signification.production@v3"],
        "answers_with_period_themes": 11,
    }
    assert actual["glance_counts"] == {
        "year_answers_with_glance": 6,
        "glance_fully_fact_backed": 6,
        "glance_bullets": {"5": 6},
        "year_answers_stating_tenth_lord_once": 6,
        "glance_ranking_or_forbidden_words_detected": 0,
    }
    assert actual["comparison_counts"] == {
        "journeys": 4,
        "hard_gates": {"PASS": 4},
        "checks_failed": [],
        "followups_executed": 9,
        "followups_structurally_successful": 9,
    }
    assert '"birth_input"' not in RESULTS_V10.read_text()
    assert actual["counts"]["hard_gates"] == {"PASS": 34}
    assert actual["counts"]["followups_executed"] == 25
    assert actual["counts"]["followups_structurally_successful"] == 25
    assert actual["user_rating"] == "USER_RATING_PENDING"
    assert actual["optional_llm_path"] == "NOT EXECUTED"
    assert actual["counts"]["product_questions_with_substantive_target_answer_editorial"] == 10
    assert actual["counts"]["plan_fidelity_pass"] == 34
    assert (
        actual["counts"]["planned_answers_fidelity_pass"]
        == actual["counts"]["planned_answers"]
        == 24
    )
    assert '"birth_input"' not in RESULTS_V8.read_text()
    assert actual["counts"]["prose_id_leaks_detected"] == 0
    assert actual["counts"]["synthesis_links_with_method_id_as_rule"] == 0


def _direct(answer: dict) -> str:  # type: ignore[type-arg]
    return str(answer["consultation_sections"][0]["text"])


_V17_WHY = (
    "This is a factual side-by-side, not a verdict. JyotishAI has no reviewed method for "
    "ranking one period above another, so it shows what was calculated and which reviewed "
    "indications apply in each, without ranking them.",
    "The reviewed rules describe context. None of them has an approved direction or an "
    "approved way to compare periods, so listing them side by side is as far as the evidence "
    "goes.",
)
_V17_TIMING = "Timing is not established by the current governed evidence."


def _cleanup_normalised(value: object) -> object:
    """Map the v17 wording of each NEXT-CLEANUP-01 change to its v18 wording."""
    if isinstance(value, dict):
        return {k: _cleanup_normalised(v) for k, v in value.items()}
    if isinstance(value, list):
        out: list[object] = []
        i = 0
        while i < len(value):
            pair = value[i : i + 2]
            if [s.get("text") if isinstance(s, dict) else None for s in pair] == list(_V17_WHY):
                out.append(_cleanup_normalised({**pair[0], "text": WHY_NO_RANKING}))
                i += 2
            else:
                out.append(_cleanup_normalised(value[i]))
                i += 1
        return out
    if isinstance(value, str):
        value = re.sub(
            re.escape(_V17_WHY[0]) + r"\s+" + re.escape(_V17_WHY[1]), WHY_NO_RANKING, value
        )
        return value.replace(_V17_TIMING, NO_TIMING_RULE)
    return value


_GLANCE_THEMES = re.compile(r"Period themes: [^.]*\.")


def _themes_glance_normalised(value: object) -> object:
    """Replace every glance Period-themes bullet (the only NEXT-THEMES-01 text change)."""
    if isinstance(value, dict):
        return {k: _themes_glance_normalised(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_themes_glance_normalised(v) for v in value]
    if isinstance(value, str):
        return _GLANCE_THEMES.sub("Period themes: <glance>.", value)
    return value


def test_v20_admits_the_verdicts_and_keeps_every_v19_count_and_gate() -> None:
    before = json.loads(RESULTS_V19.read_text())
    after = json.loads(RESULTS_V20.read_text())
    assert after["result_version"] == "consultation_quality_v20"
    assert after["comparison_baseline"] == "consultation_quality_v19"
    assert after["new_coverage_kind"] == "DOCTRINE"
    assert set(after) == set(before) | {"admit02_counts"}
    assert before["active_static_release"] == "jyotish.production.cumulative@v11"
    assert after["active_static_release"] == "jyotish.production.cumulative@v12"
    assert after["active_timing_release"] == "jyotish.timing.production.career@v3"
    assert after["active_timing_rule_ids"] == before["active_timing_rule_ids"]
    old_ids, new_ids = set(before["active_static_rule_ids"]), set(after["active_static_rule_ids"])
    assert old_ids - new_ids == {
        "bphs.d1.house_lord.10.in_4_or_10.v1",
        "bphs.d1.house_lord.10.in_2_3_or_7.v1",
        "bphs.d1.house_lord.10.in_5_or_11.children.v1",
    }
    assert new_ids - old_ids == {
        "bphs.d1.house_lord.10.equals_4.v1",
        "bphs.d1.house_lord.10.equals_10.v1",
        "bphs.d1.house_lord.10.in_2_or_3.v1",
        "bphs.d1.house_lord.10.equals_7.v1",
    }
    assert after["signification_counts"] == {
        **before["signification_counts"],
        "corpora_consulted": ["jyotish.signification.production@v3"],
    }
    for key in ("counts", "glance_counts", "comparison_counts", "bare_comparison_counts"):
        assert after[key] == before[key], key
    for rows in ("journeys", "comparison_journeys", "bare_comparison_journeys"):
        old = {row["id"]: row for row in before[rows]}
        new = {row["id"]: row for row in after[rows]}
        assert old.keys() == new.keys()
        for case_id in old:
            assert old[case_id].get("checks") == new[case_id].get("checks"), case_id
    text = RESULTS_V20.read_text()
    assert "This does not predict an event or an outcome." not in text
    assert "rājya-pradāyinī—giving rājya-related results" not in text
    assert "army or forces" not in text and "royal or sovereign role" not in text


def test_v19_changes_presentation_only_and_keeps_every_count() -> None:
    before = json.loads(RESULTS_V18.read_text())
    after = json.loads(RESULTS_V19.read_text())
    assert after["result_version"] == "consultation_quality_v19"
    assert after["comparison_baseline"] == "consultation_quality_v18"
    assert after["new_coverage_kind"] == "WORDING"
    for key in (
        "counts",
        "glance_counts",
        "comparison_counts",
        "signification_counts",
        "bare_comparison_counts",
    ):
        assert after[key] == before[key], key
    assert set(after) == set(before)
    for rows in ("journeys", "comparison_journeys", "bare_comparison_journeys"):
        old = {row["id"]: row for row in before[rows]}
        new = {row["id"]: row for row in after[rows]}
        assert old.keys() == new.keys()
        for case_id in old:
            assert old[case_id].get("checks") == new[case_id].get("checks"), case_id
    metadata = {"result_version", "comparison_baseline", "new_coverage_kind", "baseline_head"}
    trimmed = [{k: v for k, v in r.items() if k not in metadata} for r in (before, after)]
    assert _themes_glance_normalised(trimmed[0]) == _themes_glance_normalised(trimmed[1])
    text = RESULTS_V19.read_text()
    # The glance names lords and houses only; the X18 sentences are byte-identical.
    for bullet in _GLANCE_THEMES.findall(text):
        assert "Mahadasha" not in bullet and "Antardasha" not in bullet and "(" not in bullet
    old_sentences = set(re.findall(r"During your [^.]*\.", RESULTS_V18.read_text()))
    assert set(re.findall(r"During your [^.]*\.", text)) == old_sentences


def test_v18_changes_wording_only_and_keeps_every_count() -> None:
    before = json.loads(RESULTS_V17.read_text())
    after = json.loads(RESULTS_V18.read_text())
    assert after["result_version"] == "consultation_quality_v18"
    assert after["comparison_baseline"] == "consultation_quality_v17"
    assert after["new_coverage_kind"] == "WORDING"
    for key in (
        "counts",
        "glance_counts",
        "comparison_counts",
        "signification_counts",
        "bare_comparison_counts",
    ):
        assert after[key] == before[key], key
    assert set(after) == set(before)
    for rows in ("journeys", "comparison_journeys", "bare_comparison_journeys"):
        old = {row["id"]: row for row in before[rows]}
        new = {row["id"]: row for row in after[rows]}
        assert old.keys() == new.keys()
        for case_id in old:
            assert old[case_id].get("checks") == new[case_id].get("checks"), case_id
    # The v17 timing line appeared only in the two non-Career timing journeys.
    assert [row["id"] for row in before["journeys"] if _V17_TIMING in json.dumps(row)] == [
        "J14",
        "J15",
    ]
    metadata = {"result_version", "comparison_baseline", "new_coverage_kind", "baseline_head"}
    trimmed = [{k: v for k, v in r.items() if k not in metadata} for r in (before, after)]
    assert _cleanup_normalised(trimmed[0]) == trimmed[1]
    text = RESULTS_V18.read_text()
    assert "not a verdict" not in text and _V17_TIMING not in text
    assert _V17_WHY[1] not in text


def test_v17_adds_bare_comparison_journeys_and_keeps_every_v16_key() -> None:
    before = json.loads(RESULTS_V16.read_text())
    after = json.loads(RESULTS_V17.read_text())
    assert after["result_version"] == "consultation_quality_v17"
    assert after["comparison_baseline"] == "consultation_quality_v16"
    assert after["new_coverage_kind"] == "JOURNEYS"
    metadata = {"result_version", "comparison_baseline", "new_coverage_kind", "baseline_head"}
    assert set(after) - set(before) == {
        "bare_comparison_fixture_version",
        "bare_comparison_counts",
        "bare_comparison_journeys",
    }
    for key in set(before) - metadata:
        assert after[key] == before[key], key
    rows = {row["id"]: row for row in after["bare_comparison_journeys"]}
    for case_id in ("B01", "B02", "B03", "B04"):
        assert rows[case_id]["prior"] == "How is my career in 2027?"
        assert rows[case_id]["response"]["career_comparison"]["years"] == [2027, 2028]
    for case_id in ("B05", "B06", "B07", "B08"):
        response = rows[case_id]["response"]
        assert response["status"] == "clarification"
        assert response["reply"] == "Which area should I compare 2027 and 2028 for?"
        assert [c["label"] for c in response["choices"]] == ["Career"]


def _tone_normalised(results: dict) -> str:  # type: ignore[type-arg]
    """Map the v15 and v16 wording of each changed sentence to one token (NEXT-TONE-01)."""
    trimmed = {
        k: v
        for k, v in results.items()
        if k not in {"result_version", "comparison_baseline", "new_coverage_kind", "baseline_head"}
    }
    text = json.dumps(trimmed, sort_keys=True)
    text = text.replace(" " + WHY_FRAMING, "")
    text = text.replace(", so no specific Career event is established for this year.", ".")
    text = re.sub(
        r"The available reviewed timing evidence does not establish a specific Career "
        r"outcome for (\d{4})\.",
        r"CLOSING(\1)",
        text,
    )
    text = re.sub(
        r"These are (?:reviewed themes and |reviewed indications and )?calculated periods "
        r"for (\d{4}), not a prediction of specific events\.",
        r"CLOSING(\1)",
        text,
    )
    text = text.replace(
        "None of this establishes a specific event, promotion, income change, or date.",
        "COMPARISON_CLOSING",
    )
    text = re.sub(
        r"These are (?:reviewed indications and )?calculated periods for \d{4} and \d{4}, "
        r"not a prediction of specific events\.",
        "COMPARISON_CLOSING",
        text,
    )
    # v15 quoted the rule's non-guarantee in the direct line; v16 points to the timing
    # section, which still quotes it verbatim inside the full admitted wording.
    for record in (TimingSourceRecord(), MoonVenusOwnExaltationTimingSourceRecord()):
        _, guarantee = timing_meaning_and_limit(record.reviewed_interpretation)
        assert guarantee is not None
        text = text.replace(guarantee, "POINTER")
    return text.replace(TIMING_FULL_TEXT_POINTER, "POINTER")


def test_v16_changes_wording_only_and_keeps_every_count() -> None:
    before = json.loads(RESULTS_V15.read_text())
    after = json.loads(RESULTS_V16.read_text())
    assert after["result_version"] == "consultation_quality_v16"
    assert after["comparison_baseline"] == "consultation_quality_v15"
    assert after["new_coverage_kind"] == "WORDING"
    for key in ("counts", "glance_counts", "comparison_counts", "signification_counts"):
        assert after[key] == before[key], key
    old = {row["id"]: row for row in before["journeys"]}
    new = {row["id"]: row for row in after["journeys"]}
    assert old.keys() == new.keys()
    for case_id in old:
        assert old[case_id]["checks"] == new[case_id]["checks"], case_id
    # Every text difference is one of the NEXT-TONE-01 substitutions, and nothing else.
    assert _tone_normalised(before) == _tone_normalised(after)
    text = RESULTS_V16.read_text()
    assert "so no specific Career event is established" not in text
    assert "None of this establishes a specific event" not in text
    assert " " + WHY_FRAMING not in text


def test_v15_changes_only_the_signification_corpus_version() -> None:
    before = json.loads(RESULTS_V14.read_text())
    after = json.loads(RESULTS_V15.read_text())
    assert after["result_version"] == "consultation_quality_v15"
    assert after["comparison_baseline"] == "consultation_quality_v14"
    assert after["new_coverage_kind"] == "CORPUS_VERSION"

    def normalised(results: dict) -> str:  # type: ignore[type-arg]
        trimmed = {
            k: v
            for k, v in results.items()
            if k
            not in {"result_version", "comparison_baseline", "new_coverage_kind", "baseline_head"}
        }
        return (
            json.dumps(trimmed, sort_keys=True)
            .replace("jyotish.signification.production@v1", "CORPUS")
            .replace("jyotish.signification.production@v2", "CORPUS")
        )

    assert normalised(before) == normalised(after)
    assert "adversaries" not in RESULTS_V15.read_text()
    assert "शत्रु" not in RESULTS_V15.read_text()


def test_v14_admits_part0_and_changes_only_the_expected_counts() -> None:
    before = json.loads(RESULTS_V13.read_text())
    after = json.loads(RESULTS_V14.read_text())
    assert after["result_version"] == "consultation_quality_v14"
    assert after["comparison_baseline"] == "consultation_quality_v13"
    assert after["new_coverage_kind"] == "DOCTRINE"
    assert after["active_static_release"] == "jyotish.production.cumulative@v11"
    assert set(after["active_static_rule_ids"]) == set(before["active_static_rule_ids"]) | (
        PART0_RULE_IDS
    )
    for key in ("active_timing_rule_ids", "active_timing_release", "comparison_counts"):
        assert after[key] == before[key], key
    changed = {k for k in before["counts"] if before["counts"][k] != after["counts"][k]}
    assert changed == {
        "answerability",
        "product_answerability",
        "product_questions_with_matched_evidence",
    }
    # J21 (P_OTHER, 10th lord in the 1st) gains the v.71 natal context.
    assert after["counts"]["product_questions_with_matched_evidence"] == 22
    assert after["counts"]["product_answerability"]["UNSUPPORTED"] == 4
    assert after["counts"]["hard_gates"] == {"PASS": 34}
    assert after["glance_counts"] == {**before["glance_counts"], "glance_bullets": {"5": 6}}
    old = {row["id"]: row for row in before["journeys"]}
    new = {row["id"]: row for row in after["journeys"]}
    assert old.keys() == new.keys()
    for case_id in old:
        assert old[case_id]["checks"] == new[case_id]["checks"], case_id
    text = RESULTS_V14.read_text().lower()
    for word in ("lifespan", "short-lived", "short life", "alpāyu", "cruel", "thief", "rogue"):
        assert word not in text, word


def test_v13_adds_empty_signification_infrastructure_with_identical_counts() -> None:
    before = json.loads(RESULTS_V12.read_text())
    after = json.loads(RESULTS_V13.read_text())
    assert after["result_version"] == "consultation_quality_v13"
    assert after["comparison_baseline"] == "consultation_quality_v12"
    assert after["new_coverage_kind"] == "INFRASTRUCTURE"
    for key in (
        "active_static_rule_ids",
        "active_timing_rule_ids",
        "active_static_release",
        "active_timing_release",
        "counts",
        "comparison_counts",
        "glance_counts",
    ):
        assert after[key] == before[key], key
    old = {row["id"]: row for row in before["journeys"]}
    new = {row["id"]: row for row in after["journeys"]}
    assert old.keys() == new.keys()
    planned = 0
    for case_id in old:
        assert old[case_id]["checks"] == new[case_id]["checks"]
        for old_answer, new_answer in zip(
            old[case_id].get("initial", {}).get("answers", []),
            new[case_id].get("initial", {}).get("answers", []),
            strict=True,
        ):
            # Same sections, claims and evidence; the plan only records the (empty) corpus.
            assert old_answer["consultation_sections"] == new_answer["consultation_sections"]
            assert old_answer["claim_ledger"] == new_answer["claim_ledger"]
            assert old_answer["evidence"] == new_answer["evidence"]
            old_plan, new_plan = old_answer["career_answer_plan"], new_answer["career_answer_plan"]
            if old_plan is None:
                assert new_plan is None
                continue
            planned += 1
            new_fields = {"signification_corpus_version", "period_themes"}
            assert {k: v for k, v in new_plan.items() if k not in new_fields} == old_plan
            assert new_plan["period_themes"] == []
            assert new_plan["signification_corpus_version"] in (
                None,
                "jyotish.signification.production@v0-empty",
            )
            assert (new_plan["signification_corpus_version"] is None) == (
                not new_plan["dasha_segments"]
            )
    assert planned > 0


def test_v12_only_reorders_the_glance_bullets() -> None:
    before = json.loads(RESULTS_V11.read_text())
    after = json.loads(RESULTS_V12.read_text())
    assert after["result_version"] == "consultation_quality_v12"
    assert after["comparison_baseline"] == "consultation_quality_v11"
    assert after["new_coverage_kind"] == "PRESENTATION"
    for key in (
        "active_static_rule_ids",
        "active_timing_rule_ids",
        "active_static_release",
        "active_timing_release",
        "counts",
        "comparison_counts",
        "glance_counts",
    ):
        assert after[key] == before[key], key
    old = {row["id"]: row for row in before["journeys"]}
    new = {row["id"]: row for row in after["journeys"]}
    assert old.keys() == new.keys()
    seen = 0
    for case_id in old:
        assert old[case_id]["checks"] == new[case_id]["checks"]
        for old_answer, new_answer in zip(
            old[case_id].get("initial", {}).get("answers", []),
            new[case_id].get("initial", {}).get("answers", []),
            strict=True,
        ):
            assert old_answer["claim_ledger"] == new_answer["claim_ledger"]
            assert old_answer["career_answer_plan"] == new_answer["career_answer_plan"]
            pairs = list(
                zip(
                    old_answer["consultation_sections"],
                    new_answer["consultation_sections"],
                    strict=True,
                )
            )
            for old_section, new_section in pairs:
                if old_section["kind"] != "glance":
                    assert old_section == new_section
                    continue
                seen += 1
                prefixes = [b["text"].split(":", 1)[0] for b in new_section["synthesis_sentences"]]
                assert prefixes[:2] == ["Periods", "Natal"] and prefixes[-1] == "Timing"
                # Same bullets (ids unchanged); only the order and the is-10th-lord wording.
                ids = lambda s: sorted(  # noqa: E731
                    (tuple(b["fact_ids"]), tuple(b["claim_ids"])) for b in s["synthesis_sentences"]
                )
                assert ids(old_section) == ids(new_section)
    assert seen == 11  # all initial year answers, including the safety journeys
    j20 = new["J20"]["initial"]["answers"][0]
    glance = next(s for s in j20["consultation_sections"] if s["kind"] == "glance")
    assert [b["text"] for b in glance["synthesis_sentences"]][1:3] == [
        "Natal: your 10th lord is Venus, in your 11th house; your chart matches the reviewed "
        "indication about your 10th lord's placement.",
        "Calculated link: your 10th lord is also your Mahadasha lord throughout 2027.",
    ]


def test_v11_is_presentation_only_with_identical_counts() -> None:
    before = json.loads(RESULTS_V10.read_text())
    after = json.loads(RESULTS_V11.read_text())
    assert after["result_version"] == "consultation_quality_v11"
    assert after["comparison_baseline"] == "consultation_quality_v10"
    assert after["new_coverage_kind"] == "PRESENTATION"
    for key in (
        "active_static_rule_ids",
        "active_timing_rule_ids",
        "active_static_release",
        "active_timing_release",
        "counts",
        "comparison_counts",
    ):
        assert after[key] == before[key], key
    old = {row["id"]: row for row in before["journeys"]}
    new = {row["id"]: row for row in after["journeys"]}
    assert old.keys() == new.keys()
    for case_id in old:
        assert old[case_id]["checks"] == new[case_id]["checks"]
        assert old[case_id].get("answerability") == new[case_id].get("answerability")
        old_initial, new_initial = old[case_id].get("initial", {}), new[case_id].get("initial", {})
        assert old_initial.get("routing") == new_initial.get("routing")
        assert old_initial.get("selected_evidence") == new_initial.get("selected_evidence")
        for old_answer, new_answer in zip(
            old_initial.get("answers", []), new_initial.get("answers", []), strict=True
        ):
            # Same evidence, claims, rules, wording and plan; only sections are re-presented.
            assert old_answer["evidence"] == new_answer["evidence"]
            assert old_answer["claim_ledger"] == new_answer["claim_ledger"]
            assert old_answer["career_answer_plan"] == new_answer["career_answer_plan"]
            old_kinds = [s["kind"] for s in old_answer["consultation_sections"]]
            new_kinds = [s["kind"] for s in new_answer["consultation_sections"]]
            assert [k for k in new_kinds if k != "glance"] == old_kinds
            assert new_kinds.count("glance") == (1 if "dasha" in old_kinds else 0)
            for old_section, new_section in zip(
                old_answer["consultation_sections"],
                [s for s in new_answer["consultation_sections"] if s["kind"] != "glance"],
                strict=True,
            ):
                if old_section["kind"] in {"why", "dasha", "timing", "limit"}:
                    assert old_section == new_section
    # The 2027 no-match direct line keeps its periods, natal label and status; the 10th lord
    # moves to the glance.
    j20 = new["J20"]["initial"]["answers"][0]
    assert "Your 10th lord is" not in _direct(j20)
    glance = next(s for s in j20["consultation_sections"] if s["kind"] == "glance")
    # Venus is both the 10th lord and the Mahadasha lord, so the link bullet names it.
    assert "Venus, your Mahadasha lord throughout 2027, is your 10th lord." in glance["text"]
    assert "Natal: Venus is in your 11th house; your chart matches" in glance["text"]


def test_v10_is_wording_only_with_identical_counts() -> None:
    before = json.loads(RESULTS_V9.read_text())
    after = json.loads(RESULTS_V10.read_text())
    assert after["result_version"] == "consultation_quality_v10"
    assert after["comparison_baseline"] == "consultation_quality_v9"
    assert after["new_coverage_kind"] == "WORDING"
    for key in (
        "active_static_rule_ids",
        "active_timing_rule_ids",
        "active_static_release",
        "active_timing_release",
        "counts",
        "comparison_counts",
    ):
        assert after[key] == before[key], key
    old = {row["id"]: row for row in before["journeys"]}
    new = {row["id"]: row for row in after["journeys"]}
    assert old.keys() == new.keys()
    for case_id in old:
        assert old[case_id]["checks"] == new[case_id]["checks"]
        old_initial, new_initial = old[case_id].get("initial", {}), new[case_id].get("initial", {})
        assert old_initial.get("routing") == new_initial.get("routing")
        assert old_initial.get("selected_evidence") == new_initial.get("selected_evidence")
        for old_answer, new_answer in zip(
            old_initial.get("answers", []), new_initial.get("answers", []), strict=True
        ):
            assert old_answer["evidence"] == new_answer["evidence"]
            old_claims = old_answer["claim_ledger"]["claims"] if old_answer["claim_ledger"] else []
            new_claims = new_answer["claim_ledger"]["claims"] if new_answer["claim_ledger"] else []
            # Same claims, rules and wording; timing claims only gain their period lords.
            assert [
                {k: v for k, v in claim.items() if k != "period_lords"} for claim in new_claims
            ] == old_claims
            assert all(
                bool(claim["period_lords"]) == (claim["kind"] == "APPROVED_TIMING_INTERPRETATION")
                for claim in new_claims
            )
    # Timing labels now name their periods (J09: Jupiter Mahadasha, v.87).
    j09 = new["J09"]["followups"][0]["response"]["reply"]
    assert "the reviewed timing indication for Jupiter Mahadasha" in j09
    assert "about your 10th lord's Mahadasha" not in j09


def test_v9_keeps_v8_counts_and_changes_only_comparison_and_no_match_wording() -> None:
    before = json.loads(RESULTS_V8.read_text())
    after = json.loads(RESULTS_V9.read_text())
    assert after["result_version"] == "consultation_quality_v9"
    assert after["comparison_baseline"] == "consultation_quality_v8"
    assert after["new_coverage_kind"] == "COMPARISON_VIEW"
    for key in (
        "active_static_rule_ids",
        "active_timing_rule_ids",
        "active_static_release",
        "active_timing_release",
    ):
        assert after[key] == before[key], key
    # Existing counts are identical; comparison journeys are counted separately.
    assert after["counts"] == before["counts"]
    old = {row["id"]: row for row in before["journeys"]}
    new = {row["id"]: row for row in after["journeys"]}
    assert old.keys() == new.keys()
    for case_id in old:
        assert old[case_id]["checks"] == new[case_id]["checks"]
        assert old[case_id].get("answerability") == new[case_id].get("answerability")
        old_initial, new_initial = old[case_id].get("initial", {}), new[case_id].get("initial", {})
        assert old_initial.get("routing") == new_initial.get("routing")
        assert old_initial.get("selected_evidence") == new_initial.get("selected_evidence")
        for old_answer, new_answer in zip(
            old_initial.get("answers", []), new_initial.get("answers", []), strict=True
        ):
            assert old_answer["evidence"] == new_answer["evidence"]
            old_plan, new_plan = old_answer["career_answer_plan"], new_answer["career_answer_plan"]
            if old_plan is not None:
                # Only the E1 tenth-lord facts are added to the plan.
                trimmed = {k: v for k, v in new_plan.items() if k != "tenth_lord_facts"}
                assert trimmed == old_plan
                assert bool(new_plan["tenth_lord_facts"]) == bool(new_plan["dasha_segments"])
            if case_id != "J28":
                assert old_answer["claim_ledger"] == new_answer["claim_ledger"]
                assert (
                    old_answer["consultation_sections"][1:]
                    == (new_answer["consultation_sections"][1:])
                )
    # E1: the no-match direct line names the 10th lord's planet and house.
    j20 = _direct(new["J20"]["initial"]["answers"][0])
    assert "Your 10th lord is Venus, in your 11th house, and your chart matches" in j20
    # E3: the fresh comparison and the comparison follow-ups are side-by-sides.
    j28 = new["J28"]["initial"]["answers"][0]
    assert j28["career_comparison"]["comparison_mode"] == "SIDE_BY_SIDE"
    assert j28["answer"].startswith("I can't rank 2027 against 2028")
    for case_id in ("J10", "J33"):
        reply = new[case_id]["followups"][0]["response"]
        assert reply["status"] == "unsupported"
        assert reply["career_comparison"]["ranking_status"] == "unsupported"


def test_v8_rewords_only_with_identical_counts_facts_claims_and_rules() -> None:
    before = json.loads(RESULTS_V7.read_text())
    after = json.loads(RESULTS_V8.read_text())
    assert after["result_version"] == "consultation_quality_v8"
    assert after["comparison_baseline"] == "consultation_quality_v7"
    assert after["new_coverage_kind"] == "WORDING"
    for key in (
        "active_static_rule_ids",
        "active_timing_rule_ids",
        "active_static_release",
        "active_timing_release",
    ):
        assert after[key] == before[key], key
    assert after["counts"] == before["counts"]
    old = {row["id"]: row for row in before["journeys"]}
    new = {row["id"]: row for row in after["journeys"]}
    assert old.keys() == new.keys()
    direct_changes = year_answers = 0
    for case_id in old:
        assert old[case_id]["checks"] == new[case_id]["checks"]
        assert old[case_id]["initial"]["routing"] == new[case_id]["initial"]["routing"]
        assert (
            old[case_id]["initial"]["selected_evidence"]
            == new[case_id]["initial"]["selected_evidence"]
        )
        for old_answer, new_answer in zip(
            old[case_id]["initial"].get("answers", []),
            new[case_id]["initial"].get("answers", []),
            strict=True,
        ):
            assert old_answer["claim_ledger"] == new_answer["claim_ledger"]
            assert old_answer["evidence"] == new_answer["evidence"]
            assert old_answer["career_answer_plan"] == new_answer["career_answer_plan"]
            # Only the direct line's wording changes; every other section is identical.
            assert (
                old_answer["consultation_sections"][1:] == new_answer["consultation_sections"][1:]
            )
            plan = new_answer["career_answer_plan"]
            if plan and plan["synthesis"]:
                year_answers += 1
                direct_changes += _direct(old_answer) != _direct(new_answer)
                timed = [
                    claim
                    for claim in new_answer["claim_ledger"]["claims"]
                    if claim["kind"] == "APPROVED_TIMING_INTERPRETATION"
                ]
                if timed:
                    assert _direct(new_answer).startswith("Your current ")
                else:
                    assert _direct(new_answer).startswith("In 2027 your calculated Vimshottari")
                    assert " concerns " not in _direct(new_answer)
    # Every planned year answer (all journeys, not only product questions) was reworded.
    assert direct_changes == year_answers > 0


def test_v7_rewords_without_new_facts_claims_or_rules() -> None:
    before = json.loads(RESULTS_V6.read_text())
    after = json.loads(RESULTS_V7.read_text())
    assert after["result_version"] == "consultation_quality_v7"
    assert after["comparison_baseline"] == "consultation_quality_v6"
    assert after["new_coverage_kind"] == "WORDING"
    assert after["active_static_rule_ids"] == before["active_static_rule_ids"]
    assert after["active_timing_rule_ids"] == before["active_timing_rule_ids"]
    assert after["active_static_release"] == before["active_static_release"]
    assert after["active_timing_release"] == before["active_timing_release"]
    # Every v6 count is unchanged, including synthesis link counts by type.
    for key, value in before["counts"].items():
        assert after["counts"][key] == value, key
    year_answers = after["counts"]["planned_year_answers_with_synthesis"]
    assert after["counts"]["planned_year_direct_lines_with_two_or_three_sentences"] == year_answers
    assert after["counts"]["prose_id_leaks_detected"] == 0
    assert after["counts"]["synthesis_links_with_method_id_as_rule"] == 0
    old = {row["id"]: row for row in before["journeys"]}
    new = {row["id"]: row for row in after["journeys"]}
    assert old.keys() == new.keys()
    for case_id in old:
        assert old[case_id]["checks"] == new[case_id]["checks"]
        assert old[case_id]["initial"]["routing"] == new[case_id]["initial"]["routing"]
        assert (
            old[case_id]["initial"]["selected_evidence"]
            == new[case_id]["initial"]["selected_evidence"]
        )
        assert old[case_id]["initial"].get("facts") == new[case_id]["initial"].get("facts")
        for old_answer, new_answer in zip(
            old[case_id]["initial"].get("answers", []),
            new[case_id]["initial"].get("answers", []),
            strict=True,
        ):
            # Same facts, claims and rules.
            assert old_answer["claim_ledger"] == new_answer["claim_ledger"]
            assert old_answer["evidence"] == new_answer["evidence"]
            old_plan, new_plan = old_answer["career_answer_plan"], new_answer["career_answer_plan"]
            if old_plan is None:
                assert new_plan is None
                continue
            for field in (
                "calculated_fact_ids",
                "matched_claim_ids",
                "timing_evidence_ids",
                "dasha_linkages",
                "dasha_segments",
                "limitation_ids",
            ):
                assert old_plan[field] == new_plan[field], (case_id, field)
            if old_plan["synthesis"] is None:
                assert new_plan["synthesis"] is None
                continue
            old_links = old_plan["synthesis"]["links"]
            new_links = new_plan["synthesis"]["links"]
            assert len(old_links) == len(new_links)
            for old_link, new_link in zip(old_links, new_links, strict=True):
                for field in (
                    "link_type",
                    "claim_id",
                    "claim_fact_ids",
                    "claim_rule_ids",
                    "dasha_fact_ids",
                    "segment_ids",
                    "shared_reference",
                ):
                    assert old_link[field] == new_link[field], (case_id, field)
                # The v6 Dasha "rule" was a calculation method; v7 moves it to calc_method_ids.
                assert set(old_link["dasha_rule_ids"]) == set(new_link["calc_method_ids"])
                assert new_link["dasha_rule_ids"] == []


def test_v6_adds_structural_synthesis_without_new_facts_or_rules() -> None:
    before = json.loads(RESULTS_V5.read_text())
    after = json.loads(RESULTS_V6.read_text())
    assert after["result_version"] == "consultation_quality_v6"
    assert after["comparison_baseline"] == "consultation_quality_v5"
    # New coverage is structural synthesis, not new astrology.
    assert after["new_coverage_kind"] == "STRUCTURAL_SYNTHESIS"
    assert after["active_static_rule_ids"] == before["active_static_rule_ids"]
    assert after["active_timing_rule_ids"] == before["active_timing_rule_ids"]
    assert after["active_static_release"] == before["active_static_release"]
    assert after["active_timing_release"] == before["active_timing_release"]
    for key, value in before["counts"].items():
        assert after["counts"][key] == value, key
    year_answers = after["counts"]["planned_year_answers_with_dasha_chronology"]
    assert after["counts"]["planned_year_answers_with_synthesis"] == year_answers
    assert after["counts"]["synthesis_links_fully_cited"] == year_answers
    assert after["counts"]["synthesis_forbidden_connectives_detected"] == 0
    old = {row["id"]: row for row in before["journeys"]}
    new = {row["id"]: row for row in after["journeys"]}
    assert old.keys() == new.keys()
    for case_id in old:
        assert old[case_id]["checks"] == new[case_id]["checks"]
        assert old[case_id]["initial"]["routing"] == new[case_id]["initial"]["routing"]
        assert (
            old[case_id]["initial"]["selected_evidence"]
            == new[case_id]["initial"]["selected_evidence"]
        )
        for old_answer, new_answer in zip(
            old[case_id]["initial"].get("answers", []),
            new[case_id]["initial"].get("answers", []),
            strict=True,
        ):
            # Same facts, claims and rules: the ledger and the plan's evidence are unchanged.
            assert old_answer["claim_ledger"] == new_answer["claim_ledger"]
            old_plan, new_plan = old_answer["career_answer_plan"], new_answer["career_answer_plan"]
            if old_plan is None:
                assert new_plan is None
                continue
            for field in (
                "calculated_fact_ids",
                "matched_claim_ids",
                "timing_evidence_ids",
                "dasha_linkages",
            ):
                assert old_plan[field] == new_plan[field], (case_id, field)
    # The live gap: a bare "Why?" after a year answer now explains the synthesis.
    j09_why = new["J09"]["followups"][0]
    assert old["J09"]["followups"][0]["response"]["status"] == "clarification"
    assert j09_why["response"]["status"] == "answered" and j09_why["structural_success"]
    # Asking about "this particular claim" still asks which claim.
    assert new["J09"]["followups"][1]["response"]["status"] == "clarification"


def test_v5_adds_descriptive_dasha_context_without_changing_v4_scope() -> None:
    before = json.loads(RESULTS_V4.read_text())
    after = json.loads(RESULTS_V5.read_text())
    assert after["result_version"] == "consultation_quality_v5"
    assert after["comparison_baseline"] == "consultation_quality_v4"
    unchanged = set(before["counts"]) - {"planned_year_answers_with_targeted_structure"}
    for key in unchanged:
        assert after["counts"][key] == before["counts"][key], key
    # The same year answers keep their structure, now with the Dasha context section.
    assert (
        after["counts"]["planned_year_answers_with_targeted_structure"]
        == before["counts"]["planned_year_answers_with_targeted_structure"]
    )
    year_answers = after["counts"]["planned_year_answers_with_dasha_chronology"]
    assert after["counts"]["planned_year_answers_with_dasha_context"] == year_answers
    assert after["counts"]["dasha_context_sections_fully_fact_backed"] == year_answers
    # Production Dasha interpretation corpus is empty: descriptive facts only.
    assert after["counts"]["dasha_interpretation_claims"] == 0
    old = {row["id"]: row for row in before["journeys"]}
    new = {row["id"]: row for row in after["journeys"]}
    assert old.keys() == new.keys()
    for case_id in old:
        assert old[case_id]["initial"]["routing"] == new[case_id]["initial"]["routing"]
        assert (
            old[case_id]["initial"]["selected_evidence"]
            == new[case_id]["initial"]["selected_evidence"]
        )
        assert old[case_id]["checks"] == new[case_id]["checks"]


def test_v4_preserves_frozen_case_scope_and_reports_presentation_gain_only() -> None:
    before = json.loads(RESULTS_V3.read_text())
    after = json.loads(RESULTS_V4.read_text())
    assert after["result_version"] == "consultation_quality_v4"
    assert after["comparison_baseline"] == "consultation_quality_v3"
    for key in (
        "journeys",
        "hard_gates",
        "routing",
        "question_target_routing_editorial",
        "followups_executed",
        "followups_structurally_successful",
        "product_questions",
        "product_questions_with_matched_evidence",
        "product_questions_with_substantive_target_answer_editorial",
    ):
        assert after["counts"][key] == before["counts"][key]
    old = {row["id"]: row for row in before["journeys"]}
    new = {row["id"]: row for row in after["journeys"]}
    assert old.keys() == new.keys()
    for case_id in old:
        assert old[case_id]["question"] == new[case_id]["question"]
        assert old[case_id]["initial"]["routing"] == new[case_id]["initial"]["routing"]
        assert (
            old[case_id]["initial"]["selected_evidence"]
            == new[case_id]["initial"]["selected_evidence"]
        )
    assert (
        new["J20"]["initial"]["answers"][0]["career_answer_plan"]["answerability"]
        == "NATAL_CONTEXT_ONLY"
    )
    assert "Calculated Vimshottari periods in 2027" in new["J20"]["initial"]["answers"][0]["answer"]
    assert (
        new["J03"]["initial"]["answers"][0]["career_answer_plan"]["answerability"]
        == "REVIEWED_TIMING_CONTEXT"
    )


def test_v3_preserves_prior_initial_answers_and_scopes_followup_changes() -> None:
    previous = json.loads(RESULTS_V2.read_text())
    current = json.loads(RESULTS_V3.read_text())
    before = {row["id"]: row for row in previous["journeys"]}
    after = {row["id"]: row for row in current["journeys"]}
    assert before.keys() == after.keys()
    for case_id, row in before.items():
        assert after[case_id]["initial"] == row["initial"]
        if case_id not in {"J03", "J09", "J20"}:
            assert after[case_id] == row
    assert before["J20"]["followups"][0]["response"]["status"] == "unsupported"
    assert after["J20"]["followups"][0]["response"]["status"] == "answered"
    assert after["J20"]["followups"][0]["structural_success"]


def test_v2_changes_only_three_target_followups() -> None:
    v1 = json.loads(RESULTS.read_text())
    v2 = json.loads(RESULTS_V2.read_text())
    before = {row["id"]: row for row in v1["journeys"]}
    after = {row["id"]: row for row in v2["journeys"]}
    assert before.keys() == after.keys()
    for case_id, row in before.items():
        if case_id not in {"J02", "J32", "J33"}:
            assert after[case_id] == row
        else:
            assert after[case_id]["initial"] == row["initial"]
            assert after[case_id]["checks"] == row["checks"]
    assert before["J02"]["followups"][0] == after["J02"]["followups"][0]
    for case_id, index in (("J02", 1), ("J32", 0), ("J33", 0)):
        assert not before[case_id]["followups"][index]["structural_success"]
        assert after[case_id]["followups"][index]["structural_success"]
    j02 = after["J02"]
    limitation = j02["initial"]["answers"][0]["limitations"][0]
    follow = j02["followups"][1]["response"]
    assert limitation in follow["reply"]
    assert set(follow["resolved_claim_ids"]) <= set(j02["initial"]["state"]["claim_ids"])
    j32 = after["J32"]["followups"][0]["response"]
    assert j32["routing"]["intents"][0]["time_range"]["start_date"] == "2028-01-01"
    assert j32["answers"][0]["timing"]["requested_start_date"] == "2028-01-01"
    j33 = after["J33"]["followups"][0]["response"]
    assert j33["status"] == "unsupported"
    assert "No approved two-period comparison methodology" in j33["reply"]
    assert "2027:" in j33["reply"] and "2028:" in j33["reply"]
    for window in (
        after["J33"]["initial"]["answers"][0]["timing"]["windows"]
        + j32["answers"][0]["timing"]["windows"]
    ):
        assert window["rule_id"] in j33["reply"]
        assert window["effective_start"].replace("Z", "+00:00") in j33["reply"]
    assert after["J20"]["initial"]["answers"][0]["timing"]["status"] == "NO_MATCH"
    assert after["J31"]["initial"]["selected_evidence"][0]["unknown_rule_ids"]
    assert v2["optional_llm_path"] == "NOT EXECUTED"
    assert '"birth_input"' not in RESULTS_V2.read_text()


def test_benchmark_distinguishes_limited_answerability_and_failed_followups() -> None:
    data = json.loads(RESULTS.read_text())
    by_id = {item["id"]: item for item in data["journeys"]}
    assert by_id["J20"]["initial"]["answers"][0]["timing"]["status"] == "NO_MATCH"
    assert by_id["J18"]["initial"]["answers"][0]["timing"]["status"] == "UNSUPPORTED"
    assert by_id["J31"]["initial"]["selected_evidence"][0]["unknown_rule_ids"]
    assert by_id["J31"]["fault_injection"]["omitted_fact"]
    assert by_id["J05"]["answerability"] == "FACTS_ONLY"
    assert by_id["J28"]["initial"]["answers"][0]["timing"]["status"] == "UNSUPPORTED"
    assert not by_id["J02"]["followups"][1]["structural_success"]
    assert not by_id["J32"]["followups"][0]["structural_success"]
    assert not by_id["J33"]["followups"][0]["structural_success"]
    assert by_id["J25"]["followups"][1]["structural_success"]
    assert by_id["J34"]["followups"][0]["http_status"] == 409


def test_runner_refuses_to_overwrite_frozen_results() -> None:
    before = RESULTS.read_bytes()
    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).parent / "consultation_quality_benchmark.py"),
            "--output",
            str(RESULTS),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "output already exists" in result.stderr
    assert RESULTS.read_bytes() == before


def test_v21_fixes_the_wording_and_keeps_every_v20_count_and_gate() -> None:
    from consultation_quality_benchmark import _fixdeg01_counts

    before = json.loads(RESULTS_V20.read_text())
    after = json.loads(RESULTS_V21.read_text())
    assert after["result_version"] == "consultation_quality_v21"
    assert after["comparison_baseline"] == "consultation_quality_v20"
    assert after["new_coverage_kind"] == "WORDING"
    assert set(after) == set(before) | {"fixdeg01_counts"}
    for key in (
        "active_static_release",
        "active_static_rule_ids",
        "active_timing_release",
        "active_timing_rule_ids",
        "counts",
        "glance_counts",
        "comparison_counts",
        "bare_comparison_counts",
        "signification_counts",
        "admit02_counts",
    ):
        assert after[key] == before[key], key
    for rows in ("journeys", "comparison_journeys", "bare_comparison_journeys"):
        old = {row["id"]: row for row in before[rows]}
        new = {row["id"]: row for row in after[rows]}
        assert old.keys() == new.keys()
        for case_id in old:
            assert old[case_id].get("checks") == new[case_id].get("checks"), case_id
    # The same counter over the frozen v20 answers shows what v21 removed.
    assert _fixdeg01_counts(
        before["journeys"], before["comparison_journeys"], before["bare_comparison_journeys"]
    ) == {
        "dasha_context_sections": 18,
        "duplicate_occupancy_sentences_detected": 5,
        "sections_with_a_repeated_sentence": 1,
        "self_count_sentences_detected": 1,
        "same_lord_back_reference_lines": 0,
        "why_links_on_paused_or_withheld_rules": 0,
    }


def test_v22_adds_the_provisional_tier_and_keeps_every_v21_count_gate_and_answer() -> None:
    before = json.loads(RESULTS_V21.read_text())
    after = json.loads(RESULTS_V22.read_text())
    assert after["result_version"] == "consultation_quality_v22"
    assert after["comparison_baseline"] == "consultation_quality_v21"
    assert after["new_coverage_kind"] == "PROVISIONAL_TIER"
    assert set(after) == set(before) | {"provisional_counts"}
    # With include_provisional=false (every journey) everything else is identical,
    # including every journey's full snapshot, not only the counts.
    for key in set(before) - {"result_version", "comparison_baseline", "new_coverage_kind"}:
        assert after[key] == before[key], key
