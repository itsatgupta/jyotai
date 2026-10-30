"""Reproduce a frozen, synthetic consultation benchmark through the public API.

Run from apps/api: uv run python tests/consultation_quality_benchmark.py --output PATH
The output contains no birth input or process-random consultation identifiers.
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
from collections import Counter
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from astrologer.application.analyze import DeterministicAnalysisService
from astrologer.application.answer import AskJyotAIService
from astrologer.application.consultation import ConsultationStore
from astrologer.application.context import (
    DeterministicAstrologyContext,
    DeterministicAstrologyContextService,
    DeterministicContextRequest,
)
from astrologer.astrology.chart import Chart
from astrologer.astrology.dasha import VimshottariDashaEngine
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.common.config import Settings
from astrologer.composition import DeterministicAnswerComposer
from astrologer.evidence import InterpretationEvidenceBuilder
from astrologer.knowledge import ACTIVE_PRODUCTION_RELEASE
from astrologer.main import create_app
from astrologer.timing_rules.registry import get_active_timing_release
from astrologer.timing_rules.service import CareerTimingAnalysisService

FIXTURE = Path(__file__).parent / "fixtures" / "consultation_quality_v1.json"
API_MODULE = importlib.import_module("astrologer.api.analyze")
SAFETY_CASES = {"J23", "J24", "J25", "J26", "J31", "J34"}
METHOD_BOUNDARY_MISROUTES = {"J06", "J16", "J17"}
# Manual, versioned editorial coding of the captured initial answers. This is not a user rating.
SUBSTANTIVE_INITIAL = {"J03", "J07", "J08", "J09", "J10", "J12", "J13", "J30", "J32", "J33"}


def _snapshot(response: dict[str, Any]) -> dict[str, Any]:
    """Keep the actual user-visible text and referenceable evidence, without personal input."""
    state = response["state"]
    result: dict[str, Any] = {
        "status": response["status"],
        "state": {
            key: state[key]
            for key in (
                "domain",
                "claim_ids",
                "evidence_item_ids",
                "timing_references",
                "limitation",
            )
        },
        "reply": response["reply"],
        "source_references": response["source_references"],
        "resolved_claim_ids": response["resolved_claim_ids"],
        "resolved_evidence_item_ids": response["resolved_evidence_item_ids"],
        "resolved_timing_references": response["resolved_timing_references"],
    }
    analysis = response.get("analysis")
    if analysis:
        result["routing"] = {
            "status": analysis["routing"]["status"],
            "issues": analysis["routing"]["issues"],
            "intents": [
                {
                    "domain": intent["domain"],
                    "shape": intent["shape"],
                    "career_focus": intent["career_focus"],
                    "requires_timing": intent["requires_timing"],
                    "time_range": intent["time_range"],
                }
                for intent in analysis["routing"]["intents"]
            ],
        }
        result["facts"] = {
            fact["fact_id"]: fact["value"]
            for fact in analysis["context"]["derived_facts"]["facts"]
            if fact["fact_id"].startswith("jyotish.d1.house_lord.")
            and fact["fact_id"].endswith(".placement_house")
        }
        chain = analysis["context"]["active_dasha"]
        result["active_dasha"] = {
            "mahadasha": {key: chain["mahadasha"][key] for key in ("lord", "start", "end")},
            "antardasha": {key: chain["antardasha"][key] for key in ("lord", "start", "end")},
        }
        result["selected_evidence"] = [
            {
                "matched": [
                    {
                        "evidence_item_id": item["evidence_item_id"],
                        "rule_id": item["rule_id"],
                        "resolved_facts": item["resolved_facts"],
                        "status": item["evaluation_status"],
                        "direction": item["evidence_direction"],
                    }
                    for item in selection["selected_matched"]
                ],
                "unmatched_rule_ids": [item["rule_id"] for item in selection["relevant_unmatched"]],
                "unknown_rule_ids": [item["rule_id"] for item in selection["relevant_unknown"]],
            }
            for selection in analysis["selections"]
        ]
        result["answers"] = [
            {
                "answer": answer["answer"],
                "reviewed_interpretations": answer["reviewed_interpretations"],
                "why_it_applies": answer["why_it_applies"],
                "limitations": answer["limitations"],
                "evidence": answer["evidence"],
                "claim_ledger": answer["claim_ledger"],
                "timing": answer["timing"],
                "timing_answered": answer["timing_answered"],
                "corpus_limitation": answer["corpus_limitation"],
                "provider_id": answer["provider_id"],
                "model_id": answer["model_id"],
                "narrative": answer["narrative"],
            }
            for answer in analysis["answers"]
        ]
        result["methodology"] = {
            "context_version": analysis["context"]["context_version"],
            "dasha": chain["provenance"]["methodology"]["methodology_id"],
            "manifest_id": analysis["evidence_package"]["corpus_release"]["manifest_id"],
            "manifest_version": analysis["evidence_package"]["corpus_release"]["manifest_version"],
        }
    return result


def _checks(snap: dict[str, Any], expected_domain: str, raw: dict[str, Any]) -> dict[str, bool]:
    """Structural correctness gates; passing them does not prove prediction accuracy."""
    if "answers" not in snap:
        return {
            "routing": False,
            "fact_trace": True,
            "rule_trace": True,
            "timing_boundaries": True,
            "scope": True,
        }
    rules = {item.rule_id for item in ACTIVE_PRODUCTION_RELEASE.manifest.rules}
    timing_rules = {item.rule_id for item in get_active_timing_release().rules}
    facts = snap["facts"]
    selected = {
        item["evidence_item_id"]: item
        for selection in snap["selected_evidence"]
        for item in selection["matched"]
    }
    routing = snap["routing"]
    checks = {
        "routing": routing["status"] == "routable"
        and any(intent["domain"] == expected_domain for intent in routing["intents"])
    }
    checks["fact_trace"] = all(
        fact["fact_id"] in facts and facts[fact["fact_id"]] == fact["value"]
        for item in selected.values()
        for fact in item["resolved_facts"]
    )
    checks["rule_trace"] = all(
        item["rule_id"] in rules and item["status"] == "true" for item in selected.values()
    )
    checks["scope"] = all(
        evidence["chart_scope"] == "D1/Rashi"
        for answer in snap["answers"]
        for evidence in answer["evidence"]
    )
    checks["domain_scope"] = all(
        evidence["domain"] == intent["domain"]
        for answer, intent in zip(snap["answers"], routing["intents"], strict=True)
        for evidence in answer["evidence"]
    )
    checks["no_invented_outcome"] = all(
        not re.search(
            r"\b(?:you will (?:be promoted|get promoted|earn)|your salary will be|"
            r"you should become)\b|(?:[$₹£€]\s*\d[\d,]*)",
            answer["answer"].lower(),
        )
        for answer in snap["answers"]
    )
    checks["timing_boundaries"] = True
    checks["active_dasha"] = True
    as_of = datetime.fromisoformat(raw["analysis"]["context"]["normalized_as_of_utc"])
    active = snap["active_dasha"]
    md, ad = active["mahadasha"], active["antardasha"]
    if not (
        datetime.fromisoformat(md["start"]) <= as_of < datetime.fromisoformat(md["end"])
        and datetime.fromisoformat(ad["start"]) <= as_of < datetime.fromisoformat(ad["end"])
        and datetime.fromisoformat(md["start"]) <= datetime.fromisoformat(ad["start"])
        and datetime.fromisoformat(ad["end"]) <= datetime.fromisoformat(md["end"])
    ):
        checks["active_dasha"] = False
    chart = Chart.model_validate(raw["analysis"]["context"]["d1"])
    dasha_engine = VimshottariDashaEngine()
    for answer in snap["answers"]:
        timing = answer["timing"]
        if timing is None:
            continue
        if timing["status"] != "MATCH" and (timing["windows"] or answer["timing_answered"]):
            checks["timing_boundaries"] = False
        for window in timing["windows"]:
            start = datetime.fromisoformat(window["source_start"])
            end = datetime.fromisoformat(window["source_end"])
            effective_start = datetime.fromisoformat(window["effective_start"])
            effective_end = datetime.fromisoformat(window["effective_end"])
            if not (start <= effective_start < effective_end <= end):
                checks["timing_boundaries"] = False
            if window["rule_id"] not in timing_rules:
                checks["rule_trace"] = False
            midpoint = start + (end - start) / 2
            calculated = dasha_engine.at(chart, midpoint)
            period = (
                calculated.antardasha
                if window["precision"] == "SUB_PERIOD"
                else calculated.mahadasha
            )
            if (
                period.start != start
                or period.end != end
                or calculated.mahadasha.lord.value != window["mahadasha_lord"]
                or (
                    window["precision"] == "SUB_PERIOD"
                    and calculated.antardasha.lord.value != window["antardasha_lord"]
                )
            ):
                checks["timing_boundaries"] = False
        ledger = answer["claim_ledger"]
        if ledger:
            for claim in ledger["claims"]:
                kind = claim["kind"]
                if kind == "CALCULATED_FACT" and not all(fid in facts for fid in claim["fact_ids"]):
                    checks["fact_trace"] = False
                if kind == "APPROVED_INTERPRETATION" and not (
                    claim["evaluation_status"] == "MATCH"
                    and all(rule in rules for rule in claim["rule_ids"])
                    and all(item in selected for item in claim["evidence_item_ids"])
                ):
                    checks["rule_trace"] = False
                if kind == "APPROVED_TIMING_INTERPRETATION" and not (
                    claim["evaluation_status"] == "MATCH"
                    and all(rule in timing_rules for rule in claim["rule_ids"])
                    and any(
                        claim["timing_reference"]
                        == (
                            f"[{window['effective_start'].replace('Z', '+00:00')},"
                            f"{window['effective_end'].replace('Z', '+00:00')})"
                        )
                        for window in (timing or {}).get("windows", [])
                    )
                ):
                    checks["rule_trace"] = False
                if kind in {"APPROVED_INTERPRETATION", "APPROVED_TIMING_INTERPRETATION"}:
                    if not claim["source_reference"] or not claim["permitted_wording"]:
                        checks["rule_trace"] = False
    checks["no_unauthorized_precision"] = all(
        not answer["timing"]
        or answer["timing"]["scope"] != "precision_unsupported"
        or (not answer["timing"]["windows"] and not answer["timing_answered"])
        for answer in snap["answers"]
    )
    return checks


def _answerability(case: dict[str, Any], snap: dict[str, Any]) -> str:
    if case["id"] in {"J05", "J06", "J16", "J17"}:
        return "FACTS_ONLY"  # Calculated context exists, but no requested-method interpretation.
    if "answers" not in snap or not snap["answers"]:
        return "UNSUPPORTED"
    answers = snap["answers"]
    if len(answers) != 1:
        return "PARTIALLY_SUPPORTED" if any(a["evidence"] for a in answers) else "UNSUPPORTED"
    answer = answers[0]
    timing = answer["timing"]
    question = case["question"].lower()
    if any(term in question for term in ("d9", "d10", "mahadasha", "antardasha")):
        return "UNSUPPORTED"
    if not answer["evidence"]:
        return "UNSUPPORTED"
    if case["domain"] == "business" and "suit me" in question:
        return "PARTIALLY_SUPPORTED"
    if case["domain"] == "career" and timing and timing["status"] == "MATCH":
        return "PARTIALLY_SUPPORTED"  # Broad period context does not answer an outcome forecast.
    if timing and timing["status"] in {"UNSUPPORTED", "UNKNOWN", "NO_MATCH"}:
        return "PARTIALLY_SUPPORTED"
    if answer["corpus_limitation"]:
        return "PARTIALLY_SUPPORTED"
    if snap["routing"]["intents"][0]["career_focus"] in {
        "strengths",
        "development",
        "profession",
        "promotion",
        "comparison",
    }:
        return "PARTIALLY_SUPPORTED"
    if case["domain"] in {"wealth", "education", "general"}:
        return "PARTIALLY_SUPPORTED"  # Natal placement context, not a full domain consultation.
    return "FULLY_SUPPORTED_WITHIN_DECLARED_SCOPE"


def _followup_success(case_id: str, item: dict[str, Any]) -> bool:
    """Check a concrete response contract for each follow-up, including safe declines."""
    question = item["question"]
    status = item.get("response", {}).get("status") if item.get("response") else None
    reply = (item.get("response") or {}).get("reply") or ""
    if question in {
        "changed_profile",
        "forged_reference",
        "expired",
        "stale_reference",
        "new_process_store",
    }:
        return item["http_status"] == 409
    if question == "start fresh after expiry":
        return item["http_status"] == 200 and bool(item["response"].get("answers"))
    if question == "explicit_claim":
        return status == "answered" and bool(item["response"]["resolved_claim_ids"])
    if item["http_status"] != 200:
        return False
    if question == "What are the limitations?":
        return status == "answered" and bool(reply) and "does not establish" in reply
    if question == "What about 2028?":
        intents = (item["response"].get("routing") or {}).get("intents", [])
        return status == "answered" and any(
            intent["time_range"] and intent["time_range"]["start_date"].startswith("2028")
            for intent in intents
        )
    if question == "What about next year?":
        intents = (item["response"].get("routing") or {}).get("intents", [])
        return status == "answered" and any(
            intent["time_range"] and intent["time_range"]["start_date"].startswith("2028")
            for intent in intents
        )
    if question in {"Is 2028 better than 2027?", "Is next year better?"}:
        return status == "unsupported" and "2027" in reply and "2028" in reply
    if "Dasha" in question:
        if case_id in {"J14", "J15", "J18"}:
            return status == "unsupported" and bool(reply)
        if case_id == "J20":
            return (
                status == "answered"
                and "source MD" in reply
                and "source AD" in reply
                and "No reviewed Career timing rule matched 2027" in reply
                and not item["response"]["source_references"]
            )
        return (
            status == "answered"
            and "Mahadasha" in reply
            and bool(item["response"]["source_references"])
        )
    if case_id in {"J09", "J22"} and question in {
        "Why did you say that?",
        "Explain this particular claim",
    }:
        return status == "clarification" and bool(reply)
    if "placement" in question.lower() or "why" in question.lower():
        return status == "answered" and bool(item["response"]["source_references"])
    return False


def run() -> dict[str, Any]:
    fixture = json.loads(FIXTURE.read_text())
    API_MODULE.consultation_store = ConsultationStore()
    app = create_app(Settings(llm_enabled=False))
    client = TestClient(app)
    rows = []
    for case in fixture["journeys"]:
        if case.get("action") == "missing_approved_fact":

            class MissingFactContext(DeterministicAstrologyContextService):
                def build(
                    self, request: DeterministicContextRequest
                ) -> DeterministicAstrologyContext:
                    context = super().build(request)
                    facts = context.derived_facts.model_copy(
                        update={
                            "facts": tuple(
                                fact
                                for fact in context.derived_facts.facts
                                if fact.fact_id != "jyotish.d1.house_lord.10.placement_house"
                            )
                        }
                    )
                    return context.model_copy(update={"derived_facts": facts})

            provider = SwissEphemerisProvider()
            ask = AskJyotAIService(
                DeterministicAnalysisService(MissingFactContext(provider)),
                InterpretationEvidenceBuilder(),
                DeterministicAnswerComposer(),
                CareerTimingAnalysisService(provider),
            )
            app.dependency_overrides[API_MODULE.get_ask_jyotai_service] = lambda ask=ask: ask
        body = {
            "birth_input": fixture["profiles"][case["profile"]],
            "as_of": fixture["as_of"],
            "question": case["question"],
        }
        response = client.post("/api/v1/consultation", json=body)
        app.dependency_overrides.clear()
        row: dict[str, Any] = {
            "id": case["id"],
            "profile": case["profile"],
            "domain": case["domain"],
            "question": case["question"],
            "http_status": response.status_code,
            "followups": [],
        }
        if response.status_code != 200:
            row["error"] = response.json().get("detail")
            row["checks"] = {"initial_request": False}
            rows.append(row)
            continue
        first = response.json()
        row["initial"] = _snapshot(first)
        row["checks"] = _checks(row["initial"], case["domain"], first)
        row["routing_target_accurate"] = (
            row["checks"]["routing"] and case["id"] not in METHOD_BOUNDARY_MISROUTES
        )
        row["answerability"] = _answerability(case, row["initial"])
        consultation_id = first["state"]["consultation_id"]
        for question in case.get("followups", []):
            follow_body = {**body, "question": question, "consultation_id": consultation_id}
            follow = client.post("/api/v1/consultation", json=follow_body)
            item: dict[str, Any] = {"question": question, "http_status": follow.status_code}
            if follow.status_code == 200:
                item["response"] = _snapshot(follow.json())
            else:
                item["error"] = follow.json().get("detail")
            item["structural_success"] = _followup_success(case["id"], item)
            row["followups"].append(item)
        action = case.get("action")
        if action == "missing_approved_fact":
            row["fault_injection"] = {
                "omitted_fact": "jyotish.d1.house_lord.10.placement_house",
                "purpose": "exercise approved-rule UNKNOWN; not a normal engine output",
            }
            row["checks"]["unknown_preserved"] = (
                bool(row["initial"]["selected_evidence"][0]["unknown_rule_ids"])
                and not row["initial"]["answers"][0]["evidence"]
            )
            rows.append(row)
            continue
        if action:
            special = {
                **body,
                "question": "Why did you say that?",
                "consultation_id": consultation_id,
            }
            if action == "changed_profile":
                special["birth_input"] = fixture["profiles"]["P_OTHER"]
            elif action == "forged_reference":
                special.update(
                    {
                        "claim_ids": ["forged-reference"],
                        "reference_turn_id": first["state"]["turn_id"],
                    }
                )
            elif action == "expired":
                record = API_MODULE.consultation_store.get(consultation_id)
                API_MODULE.consultation_store.put(consultation_id, replace(record, expires_at=0))
            elif action == "stale_reference":
                special.update(
                    {
                        "claim_ids": first["state"]["claim_ids"][:1],
                        "reference_turn_id": "stale-turn",
                    }
                )
            elif action == "new_process_store":
                API_MODULE.consultation_store = ConsultationStore()
            elif action == "explicit_claim":
                claim = next(
                    c
                    for c in first["analysis"]["answers"][0]["claim_ledger"]["claims"]
                    if c["kind"] == "APPROVED_INTERPRETATION"
                )
                special.update(
                    {
                        "question": f"Explain claim {claim['claim_id']}",
                        "claim_ids": [claim["claim_id"]],
                        "reference_turn_id": first["state"]["turn_id"],
                    }
                )
            follow = client.post("/api/v1/consultation", json=special)
            action_item = {
                "question": action,
                "http_status": follow.status_code,
                "error": follow.json().get("detail") if follow.status_code != 200 else None,
                "response": _snapshot(follow.json()) if follow.status_code == 200 else None,
            }
            action_item["structural_success"] = _followup_success(case["id"], action_item)
            row["followups"].append(action_item)
            row["checks"][
                "reference_resolution" if action == "explicit_claim" else "reference_rejected"
            ] = (
                claim["claim_id"] in follow.json().get("resolved_claim_ids", [])
                if action == "explicit_claim" and follow.status_code == 200
                else follow.status_code == 409
            )
            if action == "expired":
                recovered = client.post("/api/v1/consultation", json=body)
                recovery_item = {
                    "question": "start fresh after expiry",
                    "http_status": recovered.status_code,
                    "response": _snapshot(recovered.json())
                    if recovered.status_code == 200
                    else None,
                    "error": recovered.json().get("detail")
                    if recovered.status_code != 200
                    else None,
                }
                recovery_item["structural_success"] = _followup_success(case["id"], recovery_item)
                row["followups"].append(recovery_item)
                row["checks"]["expiry_recovery"] = recovered.status_code == 200
        rows.append(row)
    counts = Counter(row.get("answerability", "NOT_EVALUATED") for row in rows)
    gates = Counter(
        "PASS" if all(value for key, value in row["checks"].items() if key != "routing") else "FAIL"
        for row in rows
    )
    routing = Counter("PASS" if row["checks"].get("routing") else "FAIL" for row in rows)
    target_routing = Counter(
        "PASS" if row.get("routing_target_accurate") else "FAIL" for row in rows
    )
    followups = [item for row in rows for item in row["followups"]]
    product_rows = [row for row in rows if row["id"] not in SAFETY_CASES]
    product_answerability = Counter(row["answerability"] for row in product_rows)
    evidence_backed = sum(
        row["checks"].get("routing", False)
        and any(answer["evidence"] for answer in row["initial"].get("answers", []))
        for row in product_rows
    )
    substantive = sum(
        row["id"] in SUBSTANTIVE_INITIAL
        and row["checks"].get("routing", False)
        and any(answer["evidence"] for answer in row["initial"].get("answers", []))
        for row in product_rows
    )
    conflicting = sum(
        {"supporting", "challenging"} <= {item["direction"] for item in selection["matched"]}
        for row in rows
        for selection in row["initial"].get("selected_evidence", [])
    )
    return {
        "fixture_version": fixture["fixture_version"],
        "as_of": fixture["as_of"],
        "baseline_head": "bae4e3160f28ff96f1973f2acf0c168e8901a585",
        "active_static_release": ACTIVE_PRODUCTION_RELEASE.manifest.manifest_id
        + "@"
        + ACTIVE_PRODUCTION_RELEASE.manifest.manifest_version,
        "active_timing_release": get_active_timing_release().release_id,
        "active_static_rule_ids": [
            rule.rule_id for rule in ACTIVE_PRODUCTION_RELEASE.manifest.rules
        ],
        "active_timing_rule_ids": [rule.rule_id for rule in get_active_timing_release().rules],
        "provider_path": "deterministic",
        "optional_llm_path": "NOT EXECUTED",
        "user_rating": "USER_RATING_PENDING",
        "prediction_accuracy": "NOT_EVALUATED",
        "counts": {
            "journeys": len(rows),
            "hard_gates": dict(gates),
            "routing": dict(routing),
            "question_target_routing_editorial": dict(target_routing),
            "answerability": dict(counts),
            "followups_executed": len(followups),
            "followups_http_200": sum(item["http_status"] == 200 for item in followups),
            "followups_structurally_successful": sum(
                item["structural_success"] for item in followups
            ),
            "product_questions": len(product_rows),
            "product_answerability": dict(product_answerability),
            "product_questions_with_matched_evidence": evidence_backed,
            "product_questions_with_substantive_target_answer_editorial": substantive,
            "matched_supporting_and_challenging_selections": conflicting,
        },
        "journeys": rows,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"output already exists; choose a new path: {args.output}")
    output = run()
    with args.output.open("x") as destination:
        destination.write(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output["counts"], indent=2))
