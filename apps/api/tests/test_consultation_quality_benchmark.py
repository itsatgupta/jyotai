"""Frozen consultation baseline and important acceptance gates."""

import json
import subprocess
import sys
from pathlib import Path

from consultation_quality_benchmark import run

RESULTS = Path(__file__).parent / "fixtures" / "consultation_quality_v1_results.json"
RESULTS_V2 = Path(__file__).parent / "fixtures" / "consultation_quality_v2_results.json"
RESULTS_V3 = Path(__file__).parent / "fixtures" / "consultation_quality_v3_results.json"
RESULTS_V4 = Path(__file__).parent / "fixtures" / "consultation_quality_v4_results.json"
RESULTS_V5 = Path(__file__).parent / "fixtures" / "consultation_quality_v5_results.json"
RESULTS_V6 = Path(__file__).parent / "fixtures" / "consultation_quality_v6_results.json"
RESULTS_V7 = Path(__file__).parent / "fixtures" / "consultation_quality_v7_results.json"


def test_frozen_consultation_journeys_reproduce_v7_api_responses() -> None:
    actual = run()
    expected = json.loads(RESULTS_V7.read_text())
    assert actual == expected
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
    assert '"birth_input"' not in RESULTS_V7.read_text()
    assert actual["counts"]["prose_id_leaks_detected"] == 0
    assert actual["counts"]["synthesis_links_with_method_id_as_rule"] == 0


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
