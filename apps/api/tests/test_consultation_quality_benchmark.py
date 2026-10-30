"""Frozen consultation baseline and important acceptance gates."""

import json
import subprocess
import sys
from pathlib import Path

from consultation_quality_benchmark import run

RESULTS = Path(__file__).parent / "fixtures" / "consultation_quality_v1_results.json"


def test_frozen_consultation_journeys_reproduce_actual_api_responses() -> None:
    actual = run()
    expected = json.loads(RESULTS.read_text())
    assert actual == expected
    assert actual["counts"]["hard_gates"] == {"PASS": 34}
    assert actual["counts"]["followups_executed"] == 25
    assert actual["user_rating"] == "USER_RATING_PENDING"
    assert actual["optional_llm_path"] == "NOT EXECUTED"


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
