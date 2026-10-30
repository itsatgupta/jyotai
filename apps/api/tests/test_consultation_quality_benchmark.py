"""Frozen consultation baseline and important acceptance gates."""

import json
import subprocess
import sys
from pathlib import Path

from consultation_quality_benchmark import run

RESULTS = Path(__file__).parent / "fixtures" / "consultation_quality_v1_results.json"
RESULTS_V2 = Path(__file__).parent / "fixtures" / "consultation_quality_v2_results.json"
RESULTS_V3 = Path(__file__).parent / "fixtures" / "consultation_quality_v3_results.json"


def test_frozen_consultation_journeys_reproduce_v3_api_responses() -> None:
    actual = run()
    expected = json.loads(RESULTS_V3.read_text())
    assert actual == expected
    assert actual["counts"]["hard_gates"] == {"PASS": 34}
    assert actual["counts"]["followups_executed"] == 25
    assert actual["counts"]["followups_structurally_successful"] == 25
    assert actual["user_rating"] == "USER_RATING_PENDING"
    assert actual["optional_llm_path"] == "NOT EXECUTED"


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
