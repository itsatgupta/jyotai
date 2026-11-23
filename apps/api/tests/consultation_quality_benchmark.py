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
        "choices": response.get("choices", []),
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
                "career_answer_plan": answer["career_answer_plan"],
                "consultation_sections": answer["consultation_sections"],
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
        if question == "Why did you say that?" and status == "answered":
            # v6: a bound year answer's synthesis is explained directly, main points first.
            return (
                status == "answered"
                and reply.startswith("For ")
                and "To go deeper" in reply
                and bool(item["response"]["resolved_claim_ids"])
            )
        return status == "clarification" and bool(reply)
    if "placement" in question.lower() or "why" in question.lower():
        return status == "answered" and bool(item["response"]["source_references"])
    return False


def _plan_fidelity(snap: dict[str, Any]) -> bool:
    """Check newly planned prose against selected claims and calculated intervals."""
    for answer in snap.get("answers", []):
        plan = answer["career_answer_plan"]
        if plan is None:
            continue
        claims = answer["claim_ledger"]["claims"]
        approved = {
            claim["claim_id"]: claim
            for claim in claims
            if claim["kind"] in {"APPROVED_INTERPRETATION", "APPROVED_TIMING_INTERPRETATION"}
        }
        if not set(plan["matched_claim_ids"]) <= approved.keys():
            return False
        if set(plan["approved_source_locators"]) != {
            approved[claim_id]["source_reference"] for claim_id in plan["matched_claim_ids"]
        }:
            return False
        if set(plan["timing_evidence_ids"]) != {
            rule_id
            for claim in approved.values()
            if claim["kind"] == "APPROVED_TIMING_INTERPRETATION"
            for rule_id in claim["rule_ids"]
        }:
            return False
        if set(plan["timing_references"]) != {
            claim["timing_reference"]
            for claim in approved.values()
            if claim["kind"] == "APPROVED_TIMING_INTERPRETATION"
        }:
            return False
        for segment in plan["dasha_segments"]:
            starts = [
                segment["effective_start"],
                segment["mahadasha_start"],
                segment["antardasha_start"],
            ]
            ends = [segment["effective_end"], segment["mahadasha_end"], segment["antardasha_end"]]
            start, major_start, minor_start = map(datetime.fromisoformat, starts)
            end, major_end, minor_end = map(datetime.fromisoformat, ends)
            if not (
                major_start <= start < end <= major_end and minor_start <= start < end <= minor_end
            ):
                return False
        sections = answer["consultation_sections"]
        if sections and answer["answer"] != " ".join(section["text"] for section in sections):
            return False
        if sections and any(
            answer["answer"].count(approved[claim_id]["permitted_wording"]) != 1
            for claim_id in plan["matched_claim_ids"]
        ):
            return False
    return True


FORBIDDEN_SYNTHESIS_WORDS = re.compile(
    r"\b(?:activates?|triggers?|therefore|because|strengthens?|delivers?|brings?|causes?|"
    r"leads to|results in|favou?rable|auspicious|good|bad|positive|negative)\b"
)


CALC_METHOD_IDS = {"jyotish.dasha_linkage.v1", "vimshottari-v1"}
# v7: rule, claim and method ids must never appear in user-visible prose.
PROSE_ID_PATTERN = re.compile(
    r"\b[a-z][a-z0-9_]*(?:\.[a-z0-9_@-]+){2,}"
    r"|\bcareer-(?:timing|approved|calculated|insufficient|synthesis)[\w.@-]*"
    r"|\bvimshottari-v\d"
)


def _prose_texts(row: dict[str, Any]) -> list[str]:
    """Every user-visible string of a journey: answers, sections, replies and choices."""
    texts: list[str] = []
    for answer in row.get("initial", {}).get("answers", []):
        texts.append(answer["answer"])
        texts.extend(section["text"] for section in answer["consultation_sections"])
    for item in row["followups"]:
        response = item.get("response") or {}
        texts.append(response.get("reply") or "")
        for choice in response.get("choices", []):
            texts.extend((choice["label"], choice["question"]))
        for answer in response.get("answers", []):
            texts.append(answer["answer"])
            texts.extend(section["text"] for section in answer["consultation_sections"])
    return texts


def _synthesis_fully_cited(answer: dict[str, Any]) -> bool:
    """Every synthesis link cites claim facts/rules in the ledger and Dasha facts in the plan."""
    plan = answer["career_answer_plan"]
    claims = {claim["claim_id"]: claim for claim in answer["claim_ledger"]["claims"]}
    known: set[str] = {segment["segment_id"] for segment in plan["dasha_segments"]}
    for item in plan["dasha_linkages"]:
        for role in ("mahadasha", "antardasha"):
            known.update(fact["fact_id"] for fact in item["linkage"][role]["facts"])
    for link in plan["synthesis"]["links"]:
        claim = claims.get(link["claim_id"])
        if claim is None or link["claim_id"] not in plan["matched_claim_ids"]:
            return False
        if not set(claim["fact_ids"]) <= set(link["claim_fact_ids"]):
            return False
        if link["claim_rule_ids"] != claim["rule_ids"] or not link["calc_method_ids"]:
            return False
        # v7: calculation methods are provenance, never rule ids.
        if set(link["dasha_rule_ids"]) & CALC_METHOD_IDS:
            return False
        if not link["dasha_fact_ids"] or not set(link["dasha_fact_ids"]) <= known:
            return False
    return True


def _dasha_context_fact_backed(answer: dict[str, Any]) -> bool:
    """Every dasha_context sentence cites linkage (or D1 10th-lord) fact ids in the plan."""
    plan = answer["career_answer_plan"]
    if not plan:
        return False
    known: set[str] = set()
    for item in plan["dasha_linkages"]:
        linkage = item["linkage"]
        for role in ("mahadasha", "antardasha"):
            known.update(fact["fact_id"] for fact in linkage[role]["facts"])
        known.add(linkage["ad_house_from_md"]["fact_id"])
        if item.get("tenth_lord"):
            known.add(item["tenth_lord"]["fact_id"])
    for section in answer["consultation_sections"]:
        if section["kind"] != "dasha_context":
            continue
        sentences = section["fact_sentences"]
        if not sentences or any(
            not sentence["fact_ids"] or not set(sentence["fact_ids"]) <= known
            for sentence in sentences
        ):
            return False
        expected = " ".join([*(sentence["text"] for sentence in sentences), section["framing"]])
        if section["text"] != expected:
            return False
    return True


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
        row["plan_fidelity"] = _plan_fidelity(row["initial"])
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
        "result_version": "consultation_quality_v8",
        "comparison_baseline": "consultation_quality_v7",
        # v8 is a WORDING pass over v7: a fact-backed framing sentence before a matched timing
        # rule; without a timing match the direct line states periods, natal label and status
        # (co-references stay in Why); the no-match prompt reuses the button labels.
        # Deterministic templates only. No facts, claims or rules added.
        "new_coverage_kind": "WORDING",
        "fixture_version": fixture["fixture_version"],
        "as_of": fixture["as_of"],
        "baseline_head": "2c248b4f6d44670fef191debb2c45c8e82903dbf",
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
            "plan_fidelity_pass": sum(row.get("plan_fidelity", False) for row in rows),
            "planned_answers": sum(
                answer["career_answer_plan"] is not None
                for row in rows
                for answer in row["initial"].get("answers", [])
            ),
            "planned_answers_fidelity_pass": sum(
                row.get("plan_fidelity", False) and answer["career_answer_plan"] is not None
                for row in rows
                for answer in row["initial"].get("answers", [])
            ),
            "planned_year_answers_with_dasha_chronology": sum(
                bool(
                    answer["career_answer_plan"] and answer["career_answer_plan"]["dasha_segments"]
                )
                for row in product_rows
                for answer in row["initial"].get("answers", [])
            ),
            "planned_year_answers_with_targeted_structure": sum(
                [section["kind"] for section in answer["consultation_sections"]]
                == ["direct", "why", "natal", "dasha", "dasha_context", "timing", "limit"]
                for row in product_rows
                for answer in row["initial"].get("answers", [])
            ),
            # Descriptive only: calculated lord-linkage facts, not astrological coverage.
            "planned_year_answers_with_dasha_context": sum(
                any(
                    section["kind"] == "dasha_context"
                    for section in answer["consultation_sections"]
                )
                for row in product_rows
                for answer in row["initial"].get("answers", [])
            ),
            "dasha_context_sections_fully_fact_backed": sum(
                _dasha_context_fact_backed(answer)
                for row in product_rows
                for answer in row["initial"].get("answers", [])
                if any(
                    section["kind"] == "dasha_context"
                    for section in answer["consultation_sections"]
                )
            ),
            "dasha_interpretation_claims": sum(
                len((answer["career_answer_plan"]["dasha_interpretation"] or {}).get("claims", []))
                for row in product_rows
                for answer in row["initial"].get("answers", [])
                if answer["career_answer_plan"]
            ),
            # STRUCTURAL SYNTHESIS (career-synthesis-v1): co-references only.
            "planned_year_answers_with_synthesis": sum(
                bool(answer["career_answer_plan"] and answer["career_answer_plan"]["synthesis"])
                for row in product_rows
                for answer in row["initial"].get("answers", [])
            ),
            "synthesis_links_by_type": dict(
                sorted(
                    Counter(
                        link["link_type"]
                        for row in product_rows
                        for answer in row["initial"].get("answers", [])
                        if answer["career_answer_plan"]
                        and answer["career_answer_plan"]["synthesis"]
                        for link in answer["career_answer_plan"]["synthesis"]["links"]
                    ).items()
                )
            ),
            "synthesis_links_fully_cited": sum(
                _synthesis_fully_cited(answer)
                for row in product_rows
                for answer in row["initial"].get("answers", [])
                if answer["career_answer_plan"] and answer["career_answer_plan"]["synthesis"]
            ),
            "synthesis_answers_with_no_co_reference": sum(
                bool(
                    answer["career_answer_plan"]
                    and answer["career_answer_plan"]["synthesis"]
                    and not answer["career_answer_plan"]["synthesis"]["links"]
                )
                for row in product_rows
                for answer in row["initial"].get("answers", [])
            ),
            "synthesis_forbidden_connectives_detected": sum(
                bool(FORBIDDEN_SYNTHESIS_WORDS.search(section["text"].lower()))
                for row in product_rows
                for answer in row["initial"].get("answers", [])
                for section in answer["consultation_sections"]
                if section["kind"] == "why"
            ),
            "planned_year_answers_with_repeated_limit": sum(
                answer["answer"].count(
                    "The available reviewed timing evidence does not establish "
                    "a specific Career outcome"
                )
                > 1
                for row in product_rows
                for answer in row["initial"].get("answers", [])
            ),
            "unsupported_outcome_phrase_detected": sum(
                not row["checks"].get("no_invented_outcome", True) for row in rows
            ),
            # v7 WORDING gates.
            "prose_id_leaks_detected": sum(
                bool(PROSE_ID_PATTERN.search(text)) for row in rows for text in _prose_texts(row)
            ),
            "planned_year_direct_lines_with_two_or_three_sentences": sum(
                2 <= len(answer["consultation_sections"][0]["synthesis_sentences"]) <= 3
                for row in product_rows
                for answer in row["initial"].get("answers", [])
                if answer["career_answer_plan"] and answer["career_answer_plan"]["synthesis"]
            ),
            "synthesis_links_with_method_id_as_rule": sum(
                bool(set(link["dasha_rule_ids"]) & CALC_METHOD_IDS)
                for row in product_rows
                for answer in row["initial"].get("answers", [])
                if answer["career_answer_plan"] and answer["career_answer_plan"]["synthesis"]
                for link in answer["career_answer_plan"]["synthesis"]["links"]
            ),
            "why_lines": sum(
                len(section["synthesis_sentences"])
                for row in product_rows
                for answer in row["initial"].get("answers", [])
                for section in answer["consultation_sections"]
                if section["kind"] == "why"
            ),
            "followups_with_plain_choices": sum(
                bool((item.get("response") or {}).get("choices"))
                for row in rows
                for item in row["followups"]
            ),
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
