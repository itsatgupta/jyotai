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
from astrologer.application.career_claims import timing_meaning_and_limit
from astrologer.application.career_comparison import ABSENCE_NOT_AGAINST, fixed_texts
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
from astrologer.composition.comparison_guard import ranking_violation
from astrologer.evidence import InterpretationEvidenceBuilder
from astrologer.knowledge import ACTIVE_PRODUCTION_RELEASE
from astrologer.main import create_app
from astrologer.timing_rules.registry import get_active_timing_release
from astrologer.timing_rules.service import CareerTimingAnalysisService

FIXTURE = Path(__file__).parent / "fixtures" / "consultation_quality_v1.json"
COMPARISON_FIXTURE = Path(__file__).parent / "fixtures" / "consultation_quality_comparison_v1.json"
MARRIAGE_FIXTURE = Path(__file__).parent / "fixtures" / "consultation_quality_marriage_v1.json"
WEALTH_FIXTURE = Path(__file__).parent / "fixtures" / "consultation_quality_wealth_v1.json"
PROPERTY_FIXTURE = Path(__file__).parent / "fixtures" / "consultation_quality_property_v1.json"
CHILDREN_FIXTURE = Path(__file__).parent / "fixtures" / "consultation_quality_children_v1.json"
CHILDREN_DOMAIN_FIXTURE = (
    Path(__file__).parent / "fixtures" / "consultation_quality_children_domain_v1.json"
)
BARE_COMPARISON_FIXTURE = (
    Path(__file__).parent / "fixtures" / "consultation_quality_bare_comparison_v1.json"
)
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
    if response.get("career_comparison") is not None:
        # v9: present only on a comparison follow-up reply.
        result["career_comparison"] = response["career_comparison"]
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
                **(
                    {"career_comparison": answer["career_comparison"]}
                    if answer.get("career_comparison") is not None
                    else {}
                ),
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
        if case_id in {"J14", "J15"}:
            # v28 (NEXT-CHILDREN-01, open item 19): a domain-template answer's follow-up points
            # to the calculated periods it lists, never "no timing evidence".
            return (
                status == "answered"
                and "No approved timing evidence" not in reply
                and "none reviewed yet" in reply
            )
        if case_id == "J18":
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
    comparison_rows = _run_comparison(client)
    bare_rows = _run_bare_comparison(client)
    marriage_rows = _run_marriage(client)
    wealth_rows = _run_wealth(client)
    property_rows = _run_property(client)
    children_rows = _run_children(client)
    children_domain_rows = _run_children(client, CHILDREN_DOMAIN_FIXTURE)
    return {
        "result_version": "consultation_quality_v28",
        "comparison_baseline": "consultation_quality_v27",
        # v28 (NEXT-CHILDREN-01): Children answers on the domain template (5th lord, Jupiter;
        # the two reviewed Children rules of Sitting 1 items 16 and 17; periods only; provisional
        # Children rules (5th lord: 9th/10th shown, 2nd/5th/6th/8th/12th held) and progeny
        # significations behind the flag, plus the 5th house's learning terms for Education);
        # router words kids, santan, bachcha; carry-overs A1 ("Which Dasha applies?" after a
        # Marriage, Wealth, Property or Children answer points to the listed periods: J14, J15)
        # and A3 (held notices "held for expert review": no journey snapshot carries a notice).
        # With the flag off every v27 count is identical; journey texts differ only by A1 and
        # the four Children answers of the guard set (K22-K24, K27's first answer).
        # ``children_domain_counts`` and ``children_domain_journeys`` are new.
        # v27 (NEXT-CHILDREN-GUARD-01): JyotAI never predicts or hints at a child's sex, in any
        # wording or domain ("JyotAI does not predict a child's sex."); fertility, pregnancy,
        # miscarriage, IVF, "will I have children at all" and counts get one out-of-scope
        # line (consult a doctor); childlessness and loss wording is barred everywhere; पुत्र
        # is shown with the gloss "children (the text says 'son')" (provisional corpus v5,
        # signification v4).  Every v26 journey is identical except the glossed v.12 Wealth
        # statement (flag on: W01-W04) and the corpus ids.  ``children_counts``,
        # ``children_journeys`` and ``child_guard_counts`` are new.
        # v26 (NEXT-PROPERTY-01): Property answers (4th lord; Mars, Jupiter, Venus as the
        # kārakas the text names for land, house and vehicles; periods only; provisional
        # Property rule and significations behind the flag); carry-overs: the router sends
        # money/income/savings/rich (and Hinglish) questions to Wealth and flat/land/plot/car/
        # ghar questions to Property when no other domain is named, numbered houses are not a
        # Property word, "kab" is a timing word; every Period-themes Mahadasha line is labelled
        # "(primary)" (Antardasha "(secondary)"); the v.54 Wealth item keeps its translation in
        # the review pack.  With include_provisional=false every v25 count and gate is
        # identical; journey texts differ from v25 only by the labels and J14 (the Property
        # journey, now the Property answer).  ``property_counts`` and ``property_journeys``
        # are new.
        # v25 (NEXT-WEALTH-01): carry-overs A1 (dignity prefix "Calculated fact (sign
        # dignity)"), A2 (कुटुम्ब retagged Wealth: one fewer Marriage signification item with
        # the flag on), A4 (periods past the window marked "(continues past the window)");
        # marriage runs on the generic domain pipeline (byte-identical apart from A1/A4);
        # Wealth answers (2nd/11th lords, Jupiter; periods only; provisional Wealth rules and
        # significations behind the flag).  With include_provisional=false every v24 count
        # and gate is identical; journey texts differ from v24 only by A1/A4, except J12
        # (the Wealth journey), which now carries the Wealth answer (same checks and
        # answerability).  ``wealth_counts`` and ``wealth_journeys`` are new.
        # v24 (NEXT-MARRIAGE-02): signification terms carry domain tags and an answer shows
        # only the terms tagged for its domain.  No reviewed term is tagged Marriage, so the
        # marriage Period themes list the periods only with the pending line; marriage answers
        # gain the "Calculated D9 (Navamsa) factors" section; with the flag on, the
        # provisional Marriage signification terms are added.  With include_provisional=false
        # every v23 count and gate is identical (every Career answer byte-identical); only the
        # marriage journeys (J15, J17 and ``marriage_journeys``) change.  ``marriage_counts``
        # and ``provisional_counts`` gain the new measurements.
        # v23 (NEXT-MARRIAGE-01) adds the Marriage domain: outlook, timing and year answers
        # (calculated factors, the 7th lord's and Venus's MD/AD periods in the asked range,
        # reviewed Period themes, "no reviewed timing rule", no date), polite one-line
        # out-of-scope answers, and provisional 7th-lord rules (corpus v2, most wording held).
        # With include_provisional=false every v22 count and gate is identical; the two v22
        # marriage journeys (J15, J17) now carry the marriage answer.  ``provisional_counts``
        # (flag on) now covers corpus v2; ``marriage_counts`` and ``marriage_journeys`` are new.
        # v22 (NEXT-PROVISIONAL-01) adds the provisional rule tier behind the request flag
        # ``include_provisional`` (default false).  Every journey runs with the flag off, so
        # every v21 count, gate and answer is unchanged; ``provisional_counts`` is new and
        # measures the flag separately (off: no provisional item anywhere; on: the reviewed
        # parts of every answer are byte-identical and each provisional item is badged,
        # justified and guard-clean).
        # v21 (NEXT-FIX-DEG-01) is wording only: each Dasha lord relationship is stated once
        # (no repeated "occupies your 10th house" sentence), an Antardasha of the
        # Mahadasha's own lord is one back-reference line with no "counted from" its own
        # sign, and a paused/withheld rule (v.72 7th house, v.76) is never named by label in
        # the direct line nor co-referenced in Why.  Every v20 count and gate is unchanged;
        # ``fixdeg01_counts`` is new.
        # v20 (NEXT-ADMIT-02) admits the reviewer's Sitting 1 + 2 verdicts: static release
        # v12 (24 rules confirmed under his record, wording changes for items 4–7, 14, 15, the
        # 4/10 split, the paused 7th-house part of v.72, the Children 10th-lord rule no longer
        # surfaced), timing production v3 (v.87 and v.140 wording), signification corpus v3
        # (glosses, शत्रु restored) and X18 v2 (compact form, one closing, Antardasha lines
        # "secondary"), plus the 10th lord's sign dignity as a calculated fact.  Every v19
        # count and gate is unchanged; ``admit02_counts`` is new.
        # v19 (NEXT-THEMES-01) is presentation only: a same-lord Mahadasha/Antardasha over the
        # same window gives one Period-themes line ("<Lord> Mahadasha and Antardasha"), the
        # glance names each period lord once with only its houses, and each answer lists the
        # review type of every cited rule (evidence disclosure only). Every count is identical
        # to v18; approved wording is unchanged.
        # v18 (NEXT-CLEANUP-01) is wording only: the comparison's "why no ranking" is one
        # sentence, and a non-Career timing question gets "No reviewed timing rule is
        # available for this area." instead of a second non-prediction sentence. Every count
        # is identical to v17.
        # v17 (NEXT-COMPARE-BARE) adds the bare year-vs-year journeys (separate counts);
        # every v16 key is unchanged.
        # v16 (NEXT-TONE-01) is wording only: one template non-prediction sentence per year
        # answer (the closing section), the Why framing carried for the evidence disclosure,
        # the direct line quoting only the timing rule's meaning sentence, and the comparison
        # limitation aligned. Counts are identical to v15. (v15, NEXT-SIG-02, removed
        # 6th-house शत्रु from the signification corpus, recording corpus v2.)
        "new_coverage_kind": "CHILDREN_DOMAIN",
        "fixture_version": fixture["fixture_version"],
        "comparison_fixture_version": json.loads(COMPARISON_FIXTURE.read_text())["fixture_version"],
        "as_of": fixture["as_of"],
        "baseline_head": "fb8a907225a0dc64db5f82bc6403be741fb04cd0",
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
                # v11: the glance section follows the direct line; v14: Period themes follow
                # the glance.
                == [
                    "direct",
                    "glance",
                    "period_themes",
                    "why",
                    "natal",
                    "dasha",
                    "dasha_context",
                    "timing",
                    "limit",
                ]
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
        # v11: counted separately so the v10 ``counts`` stay comparable.
        "glance_counts": _glance_counts(product_rows),
        # v13: production signification corpus and Period-themes output (filled in v14).
        "signification_counts": {
            "corpora_consulted": sorted(
                {
                    answer["career_answer_plan"]["signification_corpus_version"]
                    for row in rows
                    for answer in row.get("initial", {}).get("answers", [])
                    if answer["career_answer_plan"]
                    and answer["career_answer_plan"]["signification_corpus_version"]
                }
            ),
            "answers_with_period_themes": sum(
                any(s["kind"] == "period_themes" for s in answer["consultation_sections"])
                for row in rows
                for answer in row.get("initial", {}).get("answers", [])
            ),
        },
        # v20 (NEXT-ADMIT-02): the reviewer's verdicts as measured in the answers.
        "admit02_counts": _admit02_counts(rows, comparison_rows, bare_rows),
        # v21 (NEXT-FIX-DEG-01): the three wording fixes as measured in the answers.
        "fixdeg01_counts": _fixdeg01_counts(rows, comparison_rows, bare_rows),
        # v22 (NEXT-PROVISIONAL-01): the provisional tier, flag off and on.
        "provisional_counts": _provisional_counts(client, fixture),
        "comparison_counts": _comparison_counts(comparison_rows),
        "comparison_journeys": comparison_rows,
        # v17: bare year-vs-year questions, counted separately from every v16 count.
        "bare_comparison_fixture_version": json.loads(BARE_COMPARISON_FIXTURE.read_text())[
            "fixture_version"
        ],
        "bare_comparison_counts": _bare_comparison_counts(bare_rows),
        "bare_comparison_journeys": bare_rows,
        # v23 (NEXT-MARRIAGE-01): marriage journeys, each posted with the flag off and on.
        "marriage_fixture_version": json.loads(MARRIAGE_FIXTURE.read_text())["fixture_version"],
        "marriage_counts": _marriage_counts(marriage_rows),
        "marriage_journeys": marriage_rows,
        # v25 (NEXT-WEALTH-01): wealth journeys, each posted with the flag off and on.
        "wealth_fixture_version": json.loads(WEALTH_FIXTURE.read_text())["fixture_version"],
        "wealth_counts": _wealth_counts(wealth_rows),
        "wealth_journeys": wealth_rows,
        # v26 (NEXT-PROPERTY-01): property journeys, each posted with the flag off and on.
        "property_fixture_version": json.loads(PROPERTY_FIXTURE.read_text())["fixture_version"],
        "property_counts": _property_counts(property_rows),
        "property_journeys": property_rows,
        # v27 (NEXT-CHILDREN-GUARD-01): children journeys, each posted with the flag off and on.
        "children_fixture_version": json.loads(CHILDREN_FIXTURE.read_text())["fixture_version"],
        "children_counts": _children_counts(children_rows),
        "children_journeys": children_rows,
        # v28 (NEXT-CHILDREN-01): children-domain journeys, each posted with the flag off and on.
        "children_domain_fixture_version": json.loads(CHILDREN_DOMAIN_FIXTURE.read_text())[
            "fixture_version"
        ],
        "children_domain_counts": _children_domain_counts(children_domain_rows),
        "children_domain_journeys": children_domain_rows,
        # v28: the children wording guard over every displayed string of the new journeys
        # (answers, follow-ups and provisional items); the v27 key below is unchanged in scope.
        "children_domain_child_guard_counts": _child_guard_counts(children_domain_rows),
        # v27: the children wording guard over every displayed string of every journey set.
        "child_guard_counts": _child_guard_counts(
            rows,
            comparison_rows,
            bare_rows,
            marriage_rows,
            wealth_rows,
            property_rows,
            children_rows,
        ),
        # v26: the Period-themes role labels across every journey set (flag off).
        "period_theme_label_counts": _label_counts(
            rows, comparison_rows, bare_rows, marriage_rows, wealth_rows, property_rows
        ),
    }


TENTH_LORD_IDENTITY = re.compile(
    r"\b10th lord is [A-Z][a-z]+\b|\b[A-Z][a-z]+(?:, [^.,]+,)? is your 10th lord\b"
    r"|tenth-house lord is placed"
)
"""A sentence telling the reader which planet is the 10th lord (v11: once per answer)."""


def _admitted_wordings(answer: dict[str, Any]) -> list[str]:
    claims = answer["claim_ledger"]["claims"] if answer["claim_ledger"] else []
    texts: list[str] = []
    for claim in claims:
        if claim["kind"] in {"APPROVED_INTERPRETATION", "APPROVED_TIMING_INTERPRETATION"}:
            wording = claim["permitted_wording"]
            texts += [wording, *(t for t in timing_meaning_and_limit(wording) if t)]
    return sorted(texts, key=len, reverse=True)


def _glance_fact_backed(answer: dict[str, Any]) -> bool:
    plan = answer["career_answer_plan"]
    known = {segment["segment_id"] for segment in plan["dasha_segments"]}
    known |= {fact["fact_id"] for fact in plan["tenth_lord_facts"]}
    for item in plan["dasha_linkages"]:
        for role in ("mahadasha", "antardasha"):
            known.update(fact["fact_id"] for fact in item["linkage"][role]["facts"])
    claims = {c["claim_id"]: c for c in answer["claim_ledger"]["claims"]}
    known |= {f for claim in claims.values() for f in claim["fact_ids"]}
    glance = next(s for s in answer["consultation_sections"] if s["kind"] == "glance")
    theme_rules = {r for sentence in plan["period_themes"] for r in sentence["rule_ids"]}
    for bullet in glance["synthesis_sentences"]:
        if not set(bullet["fact_ids"]) <= known or not set(bullet["claim_ids"]) <= claims.keys():
            return False
        rules = {r for cid in bullet["claim_ids"] for r in claims[cid]["rule_ids"]}
        if bullet["text"].startswith("Period themes: "):
            # v14: cites the admitted signification entries and X18, as the section does.
            rules = theme_rules
        if not set(bullet["rule_ids"]) <= rules:
            return False
    return glance["text"] == " ".join(b["text"] for b in glance["synthesis_sentences"])


def _glance_counts(product_rows: list[dict[str, Any]]) -> dict[str, Any]:
    answers = [
        answer
        for row in product_rows
        for answer in row["initial"].get("answers", [])
        if any(s["kind"] == "glance" for s in answer["consultation_sections"])
    ]

    def own_text(answer: dict[str, Any]) -> str:
        text = str(answer["answer"])
        for wording in _admitted_wordings(answer):
            text = text.replace(wording, "")
        return text

    return {
        "year_answers_with_glance": len(answers),
        "glance_fully_fact_backed": sum(_glance_fact_backed(a) for a in answers),
        "glance_bullets": dict(
            sorted(
                Counter(
                    str(len(s["synthesis_sentences"]))
                    for a in answers
                    for s in a["consultation_sections"]
                    if s["kind"] == "glance"
                ).items()
            )
        ),
        "year_answers_stating_tenth_lord_once": sum(
            len(TENTH_LORD_IDENTITY.findall(own_text(a))) == 1 for a in answers
        ),
        "glance_ranking_or_forbidden_words_detected": sum(
            bool(
                ranking_violation(s["text"]) or FORBIDDEN_SYNTHESIS_WORDS.search(s["text"].lower())
            )
            for a in answers
            for s in a["consultation_sections"]
            if s["kind"] == "glance"
        ),
    }


_PERIOD_THEMES_CLOSING_V1 = "This does not predict an event or an outcome."
_PERIOD_THEMES_CLOSING_V2 = (
    "These are the reviewed themes associated with this period; actual results depend on the "
    "full chart and other active factors."
)
# v25 (A1): the prefix is "Calculated fact (sign dignity)"; v20–v24 matched the long form.
_DIGNITY_PREFIX = "Calculated fact (sign dignity):"
_ANTARDASHA_LINE = re.compile(r"\b[A-Z][a-z]+ Antardasha (\(secondary\) )?\(")
# v26 (NEXT-PROPERTY-01): every Mahadasha line of the Career Period themes is labelled primary.
_THEME_ROLE = re.compile(
    r"\b[A-Z][a-z]+(?: \(your [^)]*\))? (Mahadasha|Antardasha)( \((?:primary|secondary)\))?"
)


def _label_counts(*row_groups: list[dict[str, Any]]) -> dict[str, int]:
    """v26 (NEXT-PROPERTY-01): every Period-themes Mahadasha is labelled primary and every
    Antardasha secondary, in every domain (initial answers and flag-off responses)."""
    counts: Counter[str] = Counter()
    for rows in row_groups:
        for row in rows:
            snap = row.get("initial") or row.get("response") or {}
            for answer in snap.get("answers", []):
                for section in answer["consultation_sections"]:
                    if section["kind"] != "period_themes":
                        continue
                    counts["sections"] += 1
                    text = section["text"].replace(
                        "Mahadasha (primary) and Antardasha", "Mahadasha (primary). X Antardasha"
                    )
                    for match in _THEME_ROLE.finditer(text):
                        role, label = match.group(1), match.group(2) or ""
                        counts[f"{role.lower()}_lines"] += 1
                        expected = " (primary)" if role == "Mahadasha" else " (secondary)"
                        counts[f"{role.lower()}_lines_labelled"] += label == expected
    keys = (
        "sections",
        "mahadasha_lines",
        "mahadasha_lines_labelled",
        "antardasha_lines",
        "antardasha_lines_labelled",
    )
    return {key: counts[key] for key in keys}


def _admit02_counts(
    rows: list[dict[str, Any]],
    comparison_rows: list[dict[str, Any]],
    bare_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """NEXT-ADMIT-02 checks over every initial answer (journeys, comparison, bare)."""
    answers = [answer for row in rows for answer in row.get("initial", {}).get("answers", [])]
    for row in (*comparison_rows, *bare_rows):
        snap = row.get("initial") or {}
        answers.extend(snap.get("answers", []))
    # v25: the natal counts measure the Career verdicts, so a Wealth answer's natal section
    # (NEXT-WEALTH-01, journey J12) is not counted.
    career_sections = [
        s for a in answers if a.get("career_answer_plan") for s in a["consultation_sections"]
    ]
    # v26: likewise the Period-themes counts measure the Career X18 verdicts, so a generic
    # domain answer's Period themes (NEXT-PROPERTY-01, journey J14) are not counted; the
    # generic domains' labels are measured in their own counts.
    themes = [s for s in career_sections if s["kind"] == "period_themes"]
    natal = [s for s in career_sections if s["kind"] == "natal"]
    lines = [m for s in themes for m in _ANTARDASHA_LINE.finditer(s["text"])]
    return {
        "period_themes_sections": len(themes),
        "period_themes_sections_with_one_closing_at_end": sum(
            s["text"].count(_PERIOD_THEMES_CLOSING_V2) == 1
            and s["text"].endswith(_PERIOD_THEMES_CLOSING_V2)
            for s in themes
        ),
        "period_themes_old_closing_detected": sum(
            _PERIOD_THEMES_CLOSING_V1 in s["text"] for s in themes
        ),
        "antardasha_theme_lines": len(lines),
        "antardasha_theme_lines_labelled_secondary": sum(bool(m.group(1)) for m in lines),
        "natal_sections": len(natal),
        "natal_sections_with_tenth_lord_dignity_fact": sum(
            s["text"].count(_DIGNITY_PREFIX) == 1 for s in natal
        ),
        "natal_sections_mentioning_adversaries_term": sum(
            "adversaries, opposition, competition" in s["text"] for s in natal
        ),
    }


_DUPLICATE_OCCUPANCY = re.compile(
    r"\b([A-Z][a-z]+) occupies your (\d+(?:st|nd|rd|th)) house, [^.]*\. \1 occupies your"
)
_SELF_COUNT = re.compile(r"\b([A-Z][a-z]+) is in the \d+\w\w sign counted from \1's sign")
_SAME_LORD_LINE = "the same lord as the Mahadasha, stated above."
_WITHHELD_RULE_PREFIXES = (
    "bphs.d1.house_lord.10.equals_7.v1@",
    "bphs.d1.house_lord.10.equals_8.v1@",
)


PROVISIONAL_DOMAIN_QUESTIONS = (
    "What does my chart say about education?",
    "What does my chart say about wealth?",
    "What does my chart say about spirituality?",
)
_REVIEWED_WORD = re.compile(r"\breviewed\b", re.IGNORECASE)


def _provisional_counts(client: TestClient, fixture: dict[str, Any]) -> dict[str, Any]:
    """Every journey's initial question plus three domain prompts per profile, posted
    with ``include_provisional`` false and true (fresh consultations)."""
    from astrologer.application.provisional import _passes_guards
    from astrologer.knowledge.provisional_pack_v6 import ACTIVE_PROVISIONAL_CORPUS
    from astrologer.knowledge.provisional_signification import (
        ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS,
    )

    requests = [
        (fixture["profiles"][case["profile"]], case["question"])
        for case in fixture["journeys"]
        if case.get("action") != "missing_approved_fact"
    ] + [
        (profile, question)
        for _, profile in sorted(fixture["profiles"].items())
        for question in PROVISIONAL_DOMAIN_QUESTIONS
    ]
    provisional_ids = {rule.rule_id for rule in ACTIVE_PROVISIONAL_CORPUS.rules} | {
        term.term_id for term in ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS.terms
    }
    counts: Counter[str] = Counter()
    matched: Counter[str] = Counter()
    for birth, question in requests:
        body = {"birth_input": birth, "as_of": fixture["as_of"], "question": question}
        off = client.post("/api/v1/consultation", json=body).json()
        on = client.post("/api/v1/consultation", json={**body, "include_provisional": True}).json()
        counts["requests"] += 1
        off_answers = (off.get("analysis") or {}).get("answers", [])
        on_answers = (on.get("analysis") or {}).get("answers", [])
        counts["provisional_items_flag_off"] += sum(
            len(answer["provisional_interpretations"]) for answer in off_answers
        )
        strip = [
            {k: v for k, v in answer.items() if k != "provisional_interpretations"}
            for answer in on_answers
        ]
        counts["reviewed_parts_identical_flag_on"] += strip == [
            {k: v for k, v in answer.items() if k != "provisional_interpretations"}
            for answer in off_answers
        ]
        reviewed_text = json.dumps(strip, ensure_ascii=False)
        for answer in on_answers:
            for item in answer["provisional_interpretations"]:
                counts["provisional_items_flag_on"] += 1
                counts["signification_items_flag_on"] += item.get("kind") == "signification"
                matched[item["rule_id"]] += 1
                justification = item["justification"]
                counts["items_with_badge"] += (
                    item["badge"] == f"Provisional · {justification['confidence']} confidence"
                    and item["tier"] == "provisional"
                )
                # v23: a held rule sends no draft translation (it stays in the review pack)
                # but must say why its wording is held.
                # v24: a signification whose verse also lists death keeps its translation in
                # the review pack and says why (held_reason) without holding the statement.
                translated = justification["draft_translation"] or justification.get("held_reason")
                counts["items_with_full_justification"] += (
                    bool(translated)
                    and all(
                        justification[key]
                        for key in (
                            "source_work",
                            "locator",
                            "original_text",
                            "interpretive_reasoning",
                            "conventions",
                            "confidence",
                        )
                    )
                    and justification["author"]
                    in {
                        "project owner, provisional",
                        "drafted_by: AI agent; adopted_by: project owner (pending)",
                    }
                )
                counts["items_failing_guards"] += not _passes_guards(
                    item["statement"], item["placement_explanation"]
                )
                counts["items_labelled_reviewed"] += bool(
                    _REVIEWED_WORD.search(json.dumps(item, ensure_ascii=False))
                )
        counts["provisional_ids_in_reviewed_parts"] += sum(
            rule_id in reviewed_text for rule_id in provisional_ids
        )
    return {
        "corpus": ACTIVE_PROVISIONAL_CORPUS.release_id,
        "signification_corpus": ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS.release_id,
        **{
            key: counts[key]
            for key in (
                "requests",
                "provisional_items_flag_off",
                "reviewed_parts_identical_flag_on",
                "provisional_items_flag_on",
                "signification_items_flag_on",
                "items_with_badge",
                "items_with_full_justification",
                "items_failing_guards",
                "items_labelled_reviewed",
                "provisional_ids_in_reviewed_parts",
            )
        },
        "matched_rule_ids": dict(sorted(matched.items())),
    }


def _walk(value: Any) -> list[dict[str, Any]]:
    """Every dict nested anywhere in ``value`` (initial answers and follow-up turns)."""
    found: list[dict[str, Any]] = []
    stack = [value]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            found.append(item)
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)
    return found


def _fixdeg01_counts(
    rows: list[dict[str, Any]],
    comparison_rows: list[dict[str, Any]],
    bare_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """NEXT-FIX-DEG-01 checks over every turn (initial answers and follow-ups)."""
    nodes = _walk([rows, comparison_rows, bare_rows])
    contexts = [n for n in nodes if n.get("kind") == "dasha_context" and "fact_sentences" in n]
    withheld_links = 0
    for answer in (n for n in nodes if "claim_ledger" in n and "career_answer_plan" in n):
        synthesis = (answer.get("career_answer_plan") or {}).get("synthesis") or {}
        claims = {c["claim_id"]: c for c in (answer.get("claim_ledger") or {}).get("claims", [])}
        withheld_links += sum(
            any(
                rule.startswith(_WITHHELD_RULE_PREFIXES)
                for rule in claims.get(link["claim_id"], {}).get("rule_ids", [])
            )
            for link in synthesis.get("links", [])
        )
    return {
        "dasha_context_sections": len(contexts),
        "duplicate_occupancy_sentences_detected": sum(
            len(_DUPLICATE_OCCUPANCY.findall(s["text"])) for s in contexts
        ),
        "sections_with_a_repeated_sentence": sum(
            len({f["text"] for f in s["fact_sentences"]}) != len(s["fact_sentences"])
            for s in contexts
        ),
        "self_count_sentences_detected": sum(len(_SELF_COUNT.findall(s["text"])) for s in contexts),
        "same_lord_back_reference_lines": sum(s["text"].count(_SAME_LORD_LINE) for s in contexts),
        "why_links_on_paused_or_withheld_rules": withheld_links,
    }


def _comparison_of(snap: dict[str, Any]) -> dict[str, Any] | None:
    if snap.get("career_comparison"):
        return dict(snap["career_comparison"])
    for answer in snap.get("answers", []):
        if answer.get("career_comparison"):
            return dict(answer["career_comparison"])
    return None


def _comparison_sentences(comparison: dict[str, Any]) -> list[dict[str, Any]]:
    columns = [
        sentence
        for column in comparison["columns"]
        for key in ("periods", "lord_facts", "timing", "co_references")
        for sentence in column[key]
    ] + [column["dasha_interpretation"] for column in comparison["columns"]]
    return [
        *comparison["direct"],
        *comparison["differences"],
        *comparison["natal_shared"],
        *columns,
        *comparison["why_no_ranking"],
        *comparison["limitations"],
    ]


def _unbacked(comparison: dict[str, Any]) -> int:
    """Sentences that are neither fact-backed, rule-backed, nor a known fixed text."""
    fixed = fixed_texts((comparison["years"][0], comparison["years"][1]))
    return sum(
        not (
            (sentence["basis"] == "fact" and sentence["fact_ids"])
            or (sentence["basis"] == "rule" and sentence["rule_ids"])
            or (sentence["basis"] == "fixed" and sentence["text"] in fixed)
        )
        for sentence in _comparison_sentences(comparison)
    )


def _comparison_followup_success(item: dict[str, Any], years: list[int]) -> bool:
    response = item.get("response") or {}
    question = item["question"]
    choices = [choice["label"] for choice in response.get("choices", [])]
    if item["http_status"] != 200:
        return False
    if question == "Why?":
        return response["status"] == "unsupported" and choices == [
            f"Explain {years[0]}",
            f"Explain {years[1]}",
            "What would allow a ranking?",
        ]
    if question == "What would allow a ranking?":
        return response["status"] == "unsupported" and "none of them is in place" in (
            response.get("reply") or ""
        )
    if question.startswith("Explain "):
        intents = (response.get("routing") or {}).get("intents", [])
        return bool(response.get("answers")) and any(
            intent["career_focus"] == "period"
            and intent["time_range"]["start_date"].startswith(question.split()[-1])
            for intent in intents
        )
    if "better" in question:
        return response["status"] == "unsupported" and _comparison_of(response) is not None
    return False


def _absence_follows_statement(comparison: dict[str, Any]) -> bool:
    direct = [sentence["text"] for sentence in comparison["direct"]]
    if ABSENCE_NOT_AGAINST not in direct:
        return False
    index = direct.index(ABSENCE_NOT_AGAINST)
    return index > 0 and " and none applies in " in direct[index - 1]


def _run_comparison(client: TestClient) -> list[dict[str, Any]]:
    fixture = json.loads(COMPARISON_FIXTURE.read_text())
    rows: list[dict[str, Any]] = []
    for case in fixture["journeys"]:
        body = {
            "birth_input": fixture["profiles"][case["profile"]],
            "as_of": fixture["as_of"],
            "question": case["question"],
        }
        first = client.post("/api/v1/consultation", json=body)
        row: dict[str, Any] = {
            "id": case["id"],
            "profile": case["profile"],
            "question": case["question"],
            "http_status": first.status_code,
            "initial": _snapshot(first.json()),
            "followups": [],
        }
        consultation_id = first.json()["state"]["consultation_id"]
        comparison = _comparison_of(row["initial"])
        for question in case["followups"]:
            follow = client.post(
                "/api/v1/consultation",
                json={**body, "question": question, "consultation_id": consultation_id},
            )
            item: dict[str, Any] = {"question": question, "http_status": follow.status_code}
            item["response"] = _snapshot(follow.json()) if follow.status_code == 200 else None
            comparison = comparison or _comparison_of(item["response"] or {})
            row["followups"].append(item)
        years = list(comparison["years"]) if comparison else []
        for item in row["followups"]:
            item["structural_success"] = _comparison_followup_success(item, years)
        texts = (
            [sentence["text"] for sentence in _comparison_sentences(comparison or {})]
            if (comparison)
            else []
        )
        replies = [
            (item["response"] or {}).get("reply") or ""
            for item in row["followups"]
            if not (item["response"] or {}).get("career_comparison")
        ]
        one_sided = bool(comparison) and (
            len({column["timing_status"] for column in comparison["columns"]}) == 2
            and any(column["timing_indications"] for column in comparison["columns"])
        )
        row["checks"] = {
            "side_by_side": bool(comparison)
            and comparison["comparison_mode"] == "SIDE_BY_SIDE"
            and comparison["ranking_status"] == "unsupported",
            "expected_timing": bool(comparison)
            and {str(column["year"]): column["timing_status"] for column in comparison["columns"]}
            == case["expected_timing"],
            "no_ranking_language": not any(ranking_violation(text) for text in [*texts, *replies]),
            "every_sentence_backed": bool(comparison) and _unbacked(comparison) == 0,
            # v10: exactly once iff one-sided, directly after the direct-line statement.
            "absence_sentence_iff_one_sided": bool(comparison)
            and (texts.count(ABSENCE_NOT_AGAINST) == (1 if one_sided else 0))
            and (not one_sided or _absence_follows_statement(comparison)),
            "no_prose_ids": not any(PROSE_ID_PATTERN.search(text) for text in [*texts, *replies]),
        }
        rows.append(row)
    return rows


def _run_bare_comparison(client: TestClient) -> list[dict[str, Any]]:
    """v17: a bare year-vs-year question, with or without a prior Career turn."""
    fixture = json.loads(BARE_COMPARISON_FIXTURE.read_text())
    rows: list[dict[str, Any]] = []
    for case in fixture["journeys"]:
        body = {"birth_input": fixture["profiles"][case["profile"]], "as_of": fixture["as_of"]}
        consultation_id = None
        prior = None
        if case["prior"] is not None:
            first = client.post("/api/v1/consultation", json={**body, "question": case["prior"]})
            prior = first.json()["state"]
            consultation_id = prior["consultation_id"]
        bare = client.post(
            "/api/v1/consultation",
            json={
                **body,
                "question": case["question"],
                **({"consultation_id": consultation_id} if consultation_id else {}),
            },
        )
        response = bare.json()
        row: dict[str, Any] = {
            "id": case["id"],
            "profile": case["profile"],
            "prior": case["prior"],
            "question": case["question"],
            "expect": case["expect"],
            "http_status": bare.status_code,
            "response": _snapshot(response),
            "choice_response": None,
        }
        comparison = _comparison_of(row["response"])
        choices = response.get("choices") or []
        if case["expect"] == "clarification" and choices:
            # Press the first button as the web does: the anchor turn as reference, if any.
            reference = (
                {"reference_turn_id": prior["turn_id"]}
                if prior is not None and prior.get("domain")
                else {}
            )
            pressed = client.post(
                "/api/v1/consultation",
                json={
                    **body,
                    "question": choices[0]["question"],
                    "consultation_id": response["state"]["consultation_id"],
                    **reference,
                },
            )
            row["choice_response"] = _snapshot(pressed.json())
            comparison = _comparison_of(row["choice_response"])
        texts = [s["text"] for s in _comparison_sentences(comparison or {})]
        row["checks"] = {
            "expected_shape": (
                row["response"]["status"] == "clarification"
                and [c["label"] for c in choices] == ["Career"]
                if case["expect"] == "clarification"
                else _comparison_of(row["response"]) is not None
            ),
            "not_unsupported_language": "unsupported_language"
            not in json.dumps(row["response"].get("routing", {})),
            "side_by_side": bool(comparison)
            and comparison["comparison_mode"] == "SIDE_BY_SIDE"
            and comparison["ranking_status"] == "unsupported"
            and comparison["years"] == [2027, 2028],
            "no_ranking_language": not any(
                ranking_violation(t) for t in [*texts, row["response"]["reply"] or ""]
            ),
            "no_prose_ids": not any(PROSE_ID_PATTERN.search(t) for t in texts),
        }
        rows.append(row)
    return rows


def _bare_comparison_counts(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "journeys": len(rows),
        "with_prior_career_turn": sum(row["expect"] == "comparison" for row in rows),
        "clarified_then_compared": sum(row["expect"] == "clarification" for row in rows),
        "hard_gates": dict(
            Counter("PASS" if all(row["checks"].values()) else "FAIL" for row in rows)
        ),
        "checks_failed": sorted(
            f"{row['id']}:{name}" for row in rows for name, ok in row["checks"].items() if not ok
        ),
    }


def _comparison_counts(rows: list[dict[str, Any]]) -> dict[str, Any]:
    followups = [item for row in rows for item in row["followups"]]
    return {
        "journeys": len(rows),
        "hard_gates": dict(
            Counter("PASS" if all(row["checks"].values()) else "FAIL" for row in rows)
        ),
        "checks_failed": sorted(
            f"{row['id']}:{name}" for row in rows for name, ok in row["checks"].items() if not ok
        ),
        "followups_executed": len(followups),
        "followups_structurally_successful": sum(item["structural_success"] for item in followups),
    }


_MARRIAGE_DATE_CLAIM = re.compile(
    r"\byou will (?:get )?marr|\b(?:marriage|wedding) (?:is likely|will take place|"
    r"in (?:19|20)\d\d)|\bmarry in (?:19|20)\d\d",
    re.IGNORECASE,
)


def _run_marriage(client: TestClient, path: Path = MARRIAGE_FIXTURE) -> list[dict[str, Any]]:
    """v23: every marriage journey with ``include_provisional`` false (snapshot) and true.
    v25: the same runner posts the wealth journeys (``path``)."""
    fixture = json.loads(path.read_text())
    rows: list[dict[str, Any]] = []
    for case in fixture["journeys"]:
        body = {
            "birth_input": fixture["profiles"][case["profile"]],
            "as_of": fixture["as_of"],
            "question": case["question"],
        }
        off = client.post("/api/v1/consultation", json=body)
        on = client.post("/api/v1/consultation", json={**body, "include_provisional": True})
        row: dict[str, Any] = {
            "id": case["id"],
            "profile": case["profile"],
            "question": case["question"],
            "expect": case["expect"],
            "http_status": off.status_code,
        }
        if off.status_code == 200 and on.status_code == 200:
            off_json, on_json = off.json(), on.json()
            row["response"] = _snapshot(off_json)
            on_answers = on_json["analysis"]["answers"]
            off_answers = off_json["analysis"]["answers"]
            row["reviewed_parts_identical_flag_on"] = [
                {k: v for k, v in a.items() if k != "provisional_interpretations"}
                for a in on_answers
            ] == [
                {k: v for k, v in a.items() if k != "provisional_interpretations"}
                for a in off_answers
            ]
            row["provisional_items_flag_off"] = sum(
                len(a["provisional_interpretations"]) for a in off_answers
            )
            row["provisional_flag_on"] = [
                {
                    key: item[key]
                    for key in ("rule_id", "badge", "placement_explanation", "statement")
                }
                | {
                    "wording_held": item.get("wording_held", False),
                    "kind": item.get("kind", "rule"),
                }
                | (
                    {"translation_sent": item["justification"]["draft_translation"] is not None}
                    if path != MARRIAGE_FIXTURE
                    else {}
                )
                # v27: the source verse is held (a child-sex or childlessness clause); the
                # key is present only when it is, so other journeys keep their v26 rows.
                | (
                    {"source_verse_held": True}
                    if item["justification"].get("original_text_held")
                    else {}
                )
                for a in on_answers
                for item in a["provisional_interpretations"]
            ]
        rows.append(row)
    return rows


def _marriage_counts(rows: list[dict[str, Any]]) -> dict[str, Any]:
    from astrologer.application.marriage import (
        NO_TIMING_RULE,
        OUT_OF_SCOPE_REPLIES,
        THEMES_PENDING,
    )
    from astrologer.application.marriage_d9 import D9_FRAMING
    from astrologer.composition.marriage_guard import marriage_wording_violation
    from astrologer.knowledge.signification_admit02_v1 import ACTIVE_SIGNIFICATION_CORPUS

    # v24: every reviewed (Career-tagged) term; none may appear in a marriage answer.
    career_terms = {t.display for e in ACTIVE_SIGNIFICATION_CORPUS.entries for t in e.terms}

    counts: Counter[str] = Counter()
    gates: Counter[str] = Counter()
    for row in rows:
        counts["journeys"] += 1
        answers = (row.get("response") or {}).get("answers", [])
        if row["http_status"] != 200 or len(answers) != 1:
            gates["FAIL"] += 1
            continue
        answer = answers[0]
        kinds = [section["kind"] for section in answer["consultation_sections"]]
        text = answer["answer"]
        periods = next((s for s in answer["consultation_sections"] if s["kind"] == "periods"), None)
        listed = (
            [sentence["text"] for sentence in periods["synthesis_sentences"]] if periods else []
        )
        ok = marriage_wording_violation(text) is None and not _MARRIAGE_DATE_CLAIM.search(
            text.split(" These are calculated")[0]
        )
        themes = next(
            (s for s in answer["consultation_sections"] if s["kind"] == "period_themes"), None
        )
        d9 = next((s for s in answer["consultation_sections"] if s["kind"] == "d9_factors"), None)
        career_hits = sum(term in text for term in career_terms)
        counts["answers_with_career_terms"] += career_hits > 0
        if d9 is not None:
            counts["answers_with_d9_factors"] += 1
            counts["d9_sections_ending_with_framing"] += d9["text"].endswith(D9_FRAMING)
            counts["d9_vargottama_lines"] += "vargottama" in d9["text"]
        ok = ok and career_hits == 0
        if row["expect"] == "outlook":
            counts["outlook_answers"] += 1
            expected_kinds = ["direct", "chart_factors", "d9_factors", "limit"]
            counts["outlook_answers_calculated_factors_only"] += kinds == expected_kinds
            ok = ok and kinds == expected_kinds
        elif row["expect"] == "timing":
            counts["timing_answers"] += 1
            counts["timing_answers_stating_no_reviewed_timing_rule"] += NO_TIMING_RULE in text
            counts["timing_answers_with_periods"] += bool(listed)
            counts["periods_listed"] += len(listed)
            counts["timing_answers_with_period_themes"] += "period_themes" in kinds
            counts["period_themes_with_pending_line"] += bool(
                themes and themes["text"].endswith(THEMES_PENDING)
            )
            ok = ok and NO_TIMING_RULE in text and "timing_status" in kinds and d9 is not None
        else:
            counts["out_of_scope_answers"] += 1
            one_line = kinds == ["direct"] and text in OUT_OF_SCOPE_REPLIES.values()
            counts["out_of_scope_one_line"] += one_line
            ok = ok and one_line and row["provisional_flag_on"] == []
        counts["wording_guard_failures"] += marriage_wording_violation(text) is not None
        counts["date_claims_detected"] += bool(
            _MARRIAGE_DATE_CLAIM.search(text.split(" These are calculated")[0])
        )
        counts["provisional_items_flag_off"] += row["provisional_items_flag_off"]
        counts["reviewed_parts_identical_flag_on"] += row["reviewed_parts_identical_flag_on"]
        counts["provisional_items_flag_on"] += len(row["provisional_flag_on"])
        counts["provisional_items_wording_held"] += sum(
            item["wording_held"] for item in row["provisional_flag_on"]
        )
        counts["provisional_signification_items_flag_on"] += sum(
            item["kind"] == "signification" for item in row["provisional_flag_on"]
        )
        ok = ok and row["provisional_items_flag_off"] == 0
        ok = ok and row["reviewed_parts_identical_flag_on"]
        gates["PASS" if ok else "FAIL"] += 1
    keys = (
        "journeys",
        "outlook_answers",
        "outlook_answers_calculated_factors_only",
        "timing_answers",
        "timing_answers_stating_no_reviewed_timing_rule",
        "timing_answers_with_periods",
        "periods_listed",
        "timing_answers_with_period_themes",
        "period_themes_with_pending_line",
        "answers_with_career_terms",
        "answers_with_d9_factors",
        "d9_sections_ending_with_framing",
        "d9_vargottama_lines",
        "out_of_scope_answers",
        "out_of_scope_one_line",
        "wording_guard_failures",
        "date_claims_detected",
        "provisional_items_flag_off",
        "reviewed_parts_identical_flag_on",
        "provisional_items_flag_on",
        "provisional_items_wording_held",
        "provisional_signification_items_flag_on",
    )
    return {**{key: counts[key] for key in keys}, "hard_gates": dict(sorted(gates.items()))}


def _run_wealth(client: TestClient) -> list[dict[str, Any]]:
    """v25: every wealth journey with ``include_provisional`` false (snapshot) and true."""
    return _run_marriage(client, WEALTH_FIXTURE)


_WEALTH_DATE_CLAIM = re.compile(
    r"\byou will (?:become|be|get) (?:rich|wealthy)|\b(?:wealth|money|gain) (?:will come|is "
    r"likely|in (?:19|20)\d\d)",
    re.IGNORECASE,
)
_GENERAL_11_IN_9_OR_10 = "bphs.d1.house_lord.11.in_9_or_10.v1"


def _wealth_counts(rows: list[dict[str, Any]]) -> dict[str, Any]:
    from astrologer.application.domain_pipeline import CONTINUES
    from astrologer.application.wealth import NO_TIMING_RULE, OUT_OF_SCOPE_REPLIES, THEMES_PENDING
    from astrologer.composition.wealth_guard import wealth_wording_violation
    from astrologer.knowledge.signification_admit02_v1 import ACTIVE_SIGNIFICATION_CORPUS

    # Every reviewed (Career-tagged) term except the template's own words "wealth" and "gain",
    # and the Marriage terms; none may appear in a wealth answer.
    career_terms = {t.display for e in ACTIVE_SIGNIFICATION_CORPUS.entries for t in e.terms} - {
        "wealth",
        "gain",
    }
    marriage_terms = {"spouse", "marriage"}
    envelope = next(
        e for e in ACTIVE_PRODUCTION_RELEASE.envelopes if e.rule.rule_id == _GENERAL_11_IN_9_OR_10
    )
    general_statement = next(
        i.statement
        for i in ACTIVE_PRODUCTION_RELEASE.registry.interpretations
        if i.interpretation_id == envelope.interpretation_id
    )
    counts: Counter[str] = Counter()
    gates: Counter[str] = Counter()
    reviewed_rules: Counter[str] = Counter()
    for row in rows:
        counts["journeys"] += 1
        answers = (row.get("response") or {}).get("answers", [])
        if row["http_status"] != 200 or len(answers) != 1:
            gates["FAIL"] += 1
            continue
        answer = answers[0]
        kinds = [section["kind"] for section in answer["consultation_sections"]]
        text = answer["answer"]
        admitted = [item["reviewed_statement"] for item in answer["evidence"]]
        sections = {s["kind"]: s for s in answer["consultation_sections"]}
        listed = [s["text"] for s in sections.get("periods", {}).get("synthesis_sentences", [])]
        guard = wealth_wording_violation(text, admitted)
        date_claim = bool(_WEALTH_DATE_CLAIM.search(text))
        career_hits = sum(
            bool(re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE)) for term in career_terms
        )
        marriage_hits = sum(
            bool(re.search(rf"\b{term}\b", text, re.IGNORECASE)) for term in marriage_terms
        )
        counts["answers_with_career_terms"] += career_hits > 0
        counts["answers_with_marriage_terms"] += marriage_hits > 0
        for selection in row["response"].get("selected_evidence", []):
            for item in selection["matched"]:
                reviewed_rules[item["rule_id"]] += "natal" in kinds
        domains = {item["domain"] for item in answer["evidence"]}
        counts["answers_with_reviewed_natal"] += "natal" in kinds
        counts["answers_with_a_non_wealth_reviewed_rule"] += bool(domains - {"wealth"})
        counts["general_rule_statements_shown"] += general_statement in text
        ok = guard is None and not date_claim and career_hits == 0 and marriage_hits == 0
        ok = ok and domains <= {"wealth"}
        if row["expect"] == "outlook":
            counts["outlook_answers"] += 1
            expected = ["direct", *(["natal"] if "natal" in kinds else []), "chart_factors"]
            ok = ok and kinds == [*expected, "limit"]
            counts["outlook_answers_facts_and_reviewed_context_only"] += kinds == [
                *expected,
                "limit",
            ]
        elif row["expect"] == "timing":
            counts["timing_answers"] += 1
            counts["timing_answers_stating_no_reviewed_timing_rule"] += NO_TIMING_RULE in text
            counts["timing_answers_with_periods"] += bool(listed)
            counts["periods_listed"] += len(listed)
            counts["periods_continuing_past_the_window"] += sum(CONTINUES in p for p in listed)
            counts["period_themes_with_pending_line"] += bool(
                "period_themes" in sections
                and sections["period_themes"]["text"].endswith(THEMES_PENDING)
            )
            ok = ok and NO_TIMING_RULE in text and "timing_status" in kinds
        else:
            counts["out_of_scope_answers"] += 1
            one_line = kinds == ["direct"] and text in OUT_OF_SCOPE_REPLIES.values()
            counts["out_of_scope_one_line"] += one_line
            ok = ok and one_line and row["provisional_flag_on"] == []
        counts["wording_guard_failures"] += guard is not None
        counts["date_claims_detected"] += date_claim
        counts["provisional_items_flag_off"] += row["provisional_items_flag_off"]
        counts["reviewed_parts_identical_flag_on"] += row["reviewed_parts_identical_flag_on"]
        on = row["provisional_flag_on"]
        counts["provisional_items_flag_on"] += len(on)
        counts["provisional_rule_items_flag_on"] += sum(i["kind"] == "rule" for i in on)
        counts["provisional_signification_items_flag_on"] += sum(
            i["kind"] == "signification" for i in on
        )
        counts["provisional_items_wording_held"] += sum(i["wording_held"] for i in on)
        counts["provisional_items_with_translation_sent"] += sum(i["translation_sent"] for i in on)
        counts["provisional_items_failing_wealth_guard"] += sum(
            wealth_wording_violation(i["statement"]) is not None
            or wealth_wording_violation(i["placement_explanation"]) is not None
            for i in on
        )
        ok = ok and row["provisional_items_flag_off"] == 0
        ok = ok and row["reviewed_parts_identical_flag_on"]
        gates["PASS" if ok else "FAIL"] += 1
    keys = (
        "journeys",
        "outlook_answers",
        "outlook_answers_facts_and_reviewed_context_only",
        "answers_with_reviewed_natal",
        "answers_with_a_non_wealth_reviewed_rule",
        "general_rule_statements_shown",
        "timing_answers",
        "timing_answers_stating_no_reviewed_timing_rule",
        "timing_answers_with_periods",
        "periods_listed",
        "periods_continuing_past_the_window",
        "period_themes_with_pending_line",
        "answers_with_career_terms",
        "answers_with_marriage_terms",
        "out_of_scope_answers",
        "out_of_scope_one_line",
        "wording_guard_failures",
        "date_claims_detected",
        "provisional_items_flag_off",
        "reviewed_parts_identical_flag_on",
        "provisional_items_flag_on",
        "provisional_rule_items_flag_on",
        "provisional_signification_items_flag_on",
        "provisional_items_wording_held",
        "provisional_items_with_translation_sent",
        "provisional_items_failing_wealth_guard",
    )
    return {
        **{key: counts[key] for key in keys},
        "reviewed_rule_ids_shown": dict(sorted((k, v) for k, v in reviewed_rules.items() if v)),
        "hard_gates": dict(sorted(gates.items())),
    }


def _run_property(client: TestClient) -> list[dict[str, Any]]:
    """v26: every property journey with ``include_provisional`` false (snapshot) and true."""
    return _run_marriage(client, PROPERTY_FIXTURE)


_PROPERTY_ADVICE_OR_DATE = re.compile(
    r"\byou will (?:buy|get|own|sell|acquire)|\b(?:good|right|best|auspicious) time to "
    r"(?:buy|sell)|\b(?:property|house|land|a car) (?:will come|is likely|in (?:19|20)\d\d)",
    re.IGNORECASE,
)


def _other_domain_terms() -> set[str]:
    """Every reviewed (Career-tagged) term and every provisional Marriage or Wealth term."""
    from astrologer.knowledge.provisional_signification import (
        ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS,
    )
    from astrologer.knowledge.signification_admit02_v1 import ACTIVE_SIGNIFICATION_CORPUS

    terms = {t.display for e in ACTIVE_SIGNIFICATION_CORPUS.entries for t in e.terms}
    for domain in ("marriage", "wealth"):
        terms |= {
            term.display for term in ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS.for_domain(domain)
        }
    return terms


def _property_counts(rows: list[dict[str, Any]]) -> dict[str, Any]:
    from astrologer.application.domain_pipeline import CONTINUES
    from astrologer.application.property import (
        NO_TIMING_RULE,
        OUT_OF_SCOPE_REPLIES,
        THEMES_PENDING,
    )
    from astrologer.composition.property_guard import property_wording_violation

    other_terms = _other_domain_terms()
    counts: Counter[str] = Counter()
    gates: Counter[str] = Counter()
    for row in rows:
        counts["journeys"] += 1
        answers = (row.get("response") or {}).get("answers", [])
        if row["http_status"] != 200 or len(answers) != 1:
            gates["FAIL"] += 1
            continue
        answer = answers[0]
        kinds = [section["kind"] for section in answer["consultation_sections"]]
        text = answer["answer"]
        sections = {s["kind"]: s for s in answer["consultation_sections"]}
        listed = [s["text"] for s in sections.get("periods", {}).get("synthesis_sentences", [])]
        themes = sections.get("period_themes", {}).get("text", "")
        guard = property_wording_violation(text)
        advice = bool(_PROPERTY_ADVICE_OR_DATE.search(text))
        other_hits = sorted(
            term
            for term in other_terms
            if re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE)
        )
        counts["other_domain_terms_shown"] += len(other_hits)
        counts["answers_with_reviewed_evidence"] += bool(answer["evidence"])
        ok = guard is None and not advice and not other_hits and not answer["evidence"]
        intents = row["response"]["routing"]["intents"]
        ok = ok and [intent["domain"] for intent in intents] == ["property"]
        if row["expect"] == "outlook":
            counts["outlook_answers"] += 1
            facts_only = kinds == ["direct", "chart_factors", "limit"]
            counts["outlook_answers_calculated_factors_only"] += facts_only
            ok = ok and facts_only
        elif row["expect"] == "timing":
            counts["timing_answers"] += 1
            counts["timing_answers_stating_no_reviewed_timing_rule"] += NO_TIMING_RULE in text
            counts["timing_answers_with_periods"] += bool(listed)
            counts["periods_listed"] += len(listed)
            counts["periods_continuing_past_the_window"] += sum(CONTINUES in p for p in listed)
            counts["period_themes_with_pending_line"] += themes.endswith(THEMES_PENDING)
            counts["period_theme_mahadasha_lines"] += themes.count(" Mahadasha")
            counts["period_theme_mahadasha_lines_labelled_primary"] += themes.count(
                " Mahadasha (primary)"
            )
            counts["period_theme_antardasha_lines"] += themes.count(" Antardasha")
            counts["period_theme_antardasha_lines_labelled_secondary"] += themes.count(
                " Antardasha (secondary)"
            )
            ok = ok and NO_TIMING_RULE in text and "timing_status" in kinds
        else:
            counts["out_of_scope_answers"] += 1
            one_line = kinds == ["direct"] and text in OUT_OF_SCOPE_REPLIES.values()
            counts["out_of_scope_one_line"] += one_line
            ok = ok and one_line and row["provisional_flag_on"] == []
        counts["wording_guard_failures"] += guard is not None
        counts["advice_or_date_claims_detected"] += advice
        counts["provisional_items_flag_off"] += row["provisional_items_flag_off"]
        counts["reviewed_parts_identical_flag_on"] += row["reviewed_parts_identical_flag_on"]
        on = row["provisional_flag_on"]
        counts["provisional_items_flag_on"] += len(on)
        counts["provisional_rule_items_flag_on"] += sum(i["kind"] == "rule" for i in on)
        counts["provisional_signification_items_flag_on"] += sum(
            i["kind"] == "signification" for i in on
        )
        counts["provisional_items_wording_held"] += sum(i["wording_held"] for i in on)
        counts["provisional_items_with_translation_sent"] += sum(i["translation_sent"] for i in on)
        counts["provisional_items_failing_property_guard"] += sum(
            property_wording_violation(i["statement"]) is not None
            or property_wording_violation(i["placement_explanation"]) is not None
            for i in on
        )
        counts["provisional_items_with_other_domain_terms"] += sum(
            any(
                re.search(rf"\b{re.escape(term)}\b", i["statement"], re.IGNORECASE)
                for term in other_terms
            )
            for i in on
        )
        ok = ok and row["provisional_items_flag_off"] == 0
        ok = ok and row["reviewed_parts_identical_flag_on"]
        gates["PASS" if ok else "FAIL"] += 1
    keys = (
        "journeys",
        "outlook_answers",
        "outlook_answers_calculated_factors_only",
        "answers_with_reviewed_evidence",
        "timing_answers",
        "timing_answers_stating_no_reviewed_timing_rule",
        "timing_answers_with_periods",
        "periods_listed",
        "periods_continuing_past_the_window",
        "period_themes_with_pending_line",
        "period_theme_mahadasha_lines",
        "period_theme_mahadasha_lines_labelled_primary",
        "period_theme_antardasha_lines",
        "period_theme_antardasha_lines_labelled_secondary",
        "other_domain_terms_shown",
        "out_of_scope_answers",
        "out_of_scope_one_line",
        "wording_guard_failures",
        "advice_or_date_claims_detected",
        "provisional_items_flag_off",
        "reviewed_parts_identical_flag_on",
        "provisional_items_flag_on",
        "provisional_rule_items_flag_on",
        "provisional_signification_items_flag_on",
        "provisional_items_wording_held",
        "provisional_items_with_translation_sent",
        "provisional_items_failing_property_guard",
        "provisional_items_with_other_domain_terms",
    )
    return {**{key: counts[key] for key in keys}, "hard_gates": dict(sorted(gates.items()))}


def _run_children(client: TestClient, path: Path = CHILDREN_FIXTURE) -> list[dict[str, Any]]:
    """v27: every children journey with the flag off (snapshot) and on; a follow-up journey
    posts its second question in the same consultation.  v28: also the children-domain
    journeys (``path``)."""
    rows = _run_marriage(client, path)
    fixture = json.loads(path.read_text())
    for case, row in zip(fixture["journeys"], rows, strict=True):
        if "followup" not in case:
            continue
        body = {
            "birth_input": fixture["profiles"][case["profile"]],
            "as_of": fixture["as_of"],
            "question": case["question"],
        }
        first = client.post("/api/v1/consultation", json=body).json()
        second = client.post(
            "/api/v1/consultation",
            json={
                **body,
                "question": case["followup"],
                "consultation_id": first["state"]["consultation_id"],
            },
        )
        row["followup"] = case["followup"]
        row["followup_http_status"] = second.status_code
        row["followup_response"] = _snapshot(second.json()) if second.status_code == 200 else None
    return rows


def _children_counts(rows: list[dict[str, Any]]) -> dict[str, Any]:
    from astrologer.application.children import CHILD_SCOPE_REPLIES
    from astrologer.composition.children_guard import PUTRA_GLOSS
    from astrologer.questions.children_scope import ChildQuestionScope

    replies = {scope.value: reply for scope, reply in CHILD_SCOPE_REPLIES.items()}
    counts: Counter[str] = Counter()
    gates: Counter[str] = Counter()
    for row in rows:
        counts["journeys"] += 1
        response = row.get("followup_response") or row.get("response") or {}
        answers = response.get("answers", [])
        if row["http_status"] != 200 or len(answers) != 1:
            gates["FAIL"] += 1
            continue
        answer = answers[0]
        kinds = [section["kind"] for section in answer["consultation_sections"]]
        domains = [intent["domain"] for intent in response["routing"]["intents"]]
        expect = row["expect"].removeprefix("followup_")
        ok = row["provisional_items_flag_off"] == 0 and row["reviewed_parts_identical_flag_on"]
        if expect in replies:
            counts[f"{expect}_replies"] += 1
            one_line = kinds == ["direct"] and answer["answer"] == replies[expect]
            counts["one_line_replies"] += one_line
            counts["one_line_routed_children_only"] += domains == ["children"]
            counts["one_line_with_evidence"] += bool(answer["evidence"])
            if "followup" in row:
                counts["followup_one_line_replies"] += one_line
            else:
                counts["one_line_provisional_items_flag_on"] += len(row["provisional_flag_on"])
                ok = ok and row["provisional_flag_on"] == []
            ok = ok and one_line and domains == ["children"] and not answer["evidence"]
        elif expect in {"outlook", "timing"}:
            counts[f"children_{expect}_answers"] += 1
            counts["children_answers_with_reviewed_evidence"] += bool(answer["evidence"])
            ok = ok and domains == ["children"] and answer["answer"] not in replies.values()
        else:
            counts["other_domain_answers"] += 1
            glossed = [i for i in row["provisional_flag_on"] if PUTRA_GLOSS in i["statement"]]
            counts["provisional_statements_with_putra_gloss"] += len(glossed)
            ok = ok and domains == ["wealth"] and len(glossed) == 1
        gates["PASS" if ok else "FAIL"] += 1
    keys = (
        "journeys",
        *(f"{scope.value}_replies" for scope in ChildQuestionScope),
        "one_line_replies",
        "one_line_routed_children_only",
        "one_line_with_evidence",
        "one_line_provisional_items_flag_on",
        "followup_one_line_replies",
        "children_outlook_answers",
        "children_timing_answers",
        "children_answers_with_reviewed_evidence",
        "other_domain_answers",
        "provisional_statements_with_putra_gloss",
    )
    return {**{key: counts[key] for key in keys}, "hard_gates": dict(sorted(gates.items()))}


_CHILDREN_DATE_CLAIM = re.compile(
    r"\byou will (?:have|get) (?:a |any )?(?:child|children|kids|baby)|\b(?:a child|children|"
    r"a baby|birth) (?:will come|is likely|is due|in (?:19|20)\d\d)",
    re.IGNORECASE,
)


def _children_domain_counts(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """v28 (NEXT-CHILDREN-01): the Children answers on the domain template, flag off and on."""
    from astrologer.application.children import CHILD_SEX_REPLY
    from astrologer.application.children_domain import (
        LIMIT_OUTLOOK,
        LIMIT_TIMING,
        NO_TIMING_RULE,
        OUT_OF_SCOPE_REPLIES,
        THEMES_PENDING,
    )
    from astrologer.application.domain_pipeline import CONTINUES
    from astrologer.composition.children_domain_guard import children_domain_violation
    from astrologer.composition.children_guard import child_wording_violation
    from astrologer.knowledge.models import JyotishDomain
    from astrologer.knowledge.provisional_signification import (
        ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS,
    )

    interpretations = {
        record.interpretation_id: record.statement
        for record in ACTIVE_PRODUCTION_RELEASE.registry.interpretations
    }
    reviewed = {
        interpretations[envelope.interpretation_id]: envelope.rule.rule_id
        for envelope in ACTIVE_PRODUCTION_RELEASE.envelopes
        if envelope.interpretation_id in interpretations
    }
    tenth = {
        statement
        for statement in interpretations.values()
        if statement.startswith("With the D1 tenth-house lord in the fifth or eleventh house")
        and "children/progeny" in statement
    }
    other_terms = {
        term.display
        for term in ACTIVE_PROVISIONAL_SIGNIFICATION_CORPUS.terms
        if JyotishDomain.CHILDREN not in term.domains
    } | _other_domain_terms()
    counts: Counter[str] = Counter()
    gates: Counter[str] = Counter()
    rule_ids: Counter[str] = Counter()
    provisional_ids: Counter[str] = Counter()
    for row in rows:
        counts["journeys"] += 1
        answers = (row.get("response") or {}).get("answers", [])
        if row["http_status"] != 200 or len(answers) != 1:
            gates["FAIL"] += 1
            continue
        answer = answers[0]
        kinds = [section["kind"] for section in answer["consultation_sections"]]
        text = answer["answer"]
        admitted = [item["reviewed_statement"] for item in answer["evidence"]]
        own = text
        for statement in admitted:
            own = own.replace(statement, " ")
        sections = {s["kind"]: s for s in answer["consultation_sections"]}
        listed = [s["text"] for s in sections.get("periods", {}).get("synthesis_sentences", [])]
        themes = sections.get("period_themes", {}).get("text", "")
        child_bad = child_wording_violation(text)
        domain_bad = children_domain_violation(own)
        fixed = own.replace(LIMIT_OUTLOOK, " ").replace(LIMIT_TIMING, " ")
        dated = bool(_CHILDREN_DATE_CLAIM.search(fixed))
        other_hits = sorted(
            term for term in other_terms if re.search(rf"\b{re.escape(term)}\b", own, re.I)
        )
        counts["other_domain_terms_shown"] += len(other_hits)
        counts["answers_with_reviewed_evidence"] += bool(admitted)
        for statement in admitted:
            rule_ids[reviewed.get(statement, "unknown")] += 1
            counts["tenth_lord_children_rule_shown"] += statement in tenth
        intents = row["response"]["routing"]["intents"]
        ok = child_bad is None and domain_bad is None and not dated and not other_hits
        ok = ok and [intent["domain"] for intent in intents] == ["children"]
        ok = ok and not any(statement in tenth for statement in admitted)
        if row["expect"] == "outlook":
            counts["outlook_answers"] += 1
            facts_only = set(kinds) <= {"direct", "natal", "chart_factors", "limit"}
            counts["outlook_answers_facts_and_reviewed_context_only"] += facts_only
            ok = ok and facts_only
        elif row["expect"] == "timing":
            counts["timing_answers"] += 1
            counts["timing_answers_stating_no_reviewed_timing_rule"] += NO_TIMING_RULE in text
            counts["timing_answers_with_periods"] += bool(listed)
            counts["periods_listed"] += len(listed)
            counts["periods_continuing_past_the_window"] += sum(CONTINUES in p for p in listed)
            counts["period_themes_with_pending_line"] += themes.endswith(THEMES_PENDING)
            counts["period_theme_mahadasha_lines"] += themes.count(" Mahadasha")
            counts["period_theme_mahadasha_lines_labelled_primary"] += themes.count(
                " Mahadasha (primary)"
            )
            counts["period_theme_antardasha_lines"] += themes.count(" Antardasha")
            counts["period_theme_antardasha_lines_labelled_secondary"] += themes.count(
                " Antardasha (secondary)"
            )
            if intents[0]["shape"] == "comparative":
                counts["comparison_answers_not_ranked"] += "years are not ranked" in text
            ok = ok and NO_TIMING_RULE in text and "timing_status" in kinds
        else:
            counts["out_of_scope_answers"] += 1
            one_line = kinds == ["direct"] and text in OUT_OF_SCOPE_REPLIES.values()
            counts["out_of_scope_one_line"] += one_line
            ok = ok and one_line and row["provisional_flag_on"] == []
        counts["child_guard_violations"] += child_bad is not None
        counts["children_domain_guard_failures"] += domain_bad is not None
        counts["date_claims_detected"] += dated
        if "followup" in row:
            follow = row.get("followup_response") or {}
            reply = follow.get("reply") or ""
            if row["followup"] == "Which Dasha applies?":
                counts["dasha_followups"] += 1
                pointed = follow.get("status") == "answered" and (
                    reply.startswith("The Dasha periods for this answer are the calculated")
                    or reply.startswith("This answer lists no Dasha periods")
                )
                counts["dasha_followups_pointing_to_the_periods"] += pointed
                counts["dasha_followups_saying_no_timing_evidence"] += (
                    "No approved timing evidence" in reply
                )
                ok = ok and pointed and all(p in reply for p in listed)
            else:
                follow_answers = follow.get("answers", [])
                one_line = [a["answer"] for a in follow_answers] == [CHILD_SEX_REPLY]
                counts["child_sex_followups_one_line"] += one_line
                ok = ok and one_line
        on = row["provisional_flag_on"]
        counts["provisional_items_flag_off"] += row["provisional_items_flag_off"]
        counts["reviewed_parts_identical_flag_on"] += row["reviewed_parts_identical_flag_on"]
        counts["provisional_items_flag_on"] += len(on)
        counts["provisional_rule_items_flag_on"] += sum(i["kind"] == "rule" for i in on)
        counts["provisional_signification_items_flag_on"] += sum(
            i["kind"] == "signification" for i in on
        )
        counts["provisional_items_wording_held"] += sum(i["wording_held"] for i in on)
        counts["provisional_items_source_verse_held"] += sum(
            i.get("source_verse_held", False) for i in on
        )
        counts["provisional_items_with_translation_sent"] += sum(i["translation_sent"] for i in on)
        counts["provisional_items_failing_children_guards"] += sum(
            child_wording_violation(i[key]) is not None
            or children_domain_violation(i[key]) is not None
            for i in on
            for key in ("statement", "placement_explanation")
        )
        counts["provisional_items_with_other_domain_terms"] += sum(
            any(
                re.search(rf"\b{re.escape(term)}\b", i["statement"], re.IGNORECASE)
                for term in other_terms
            )
            for i in on
        )
        counts["provisional_items_labelled_reviewed"] += sum(
            bool(_REVIEWED_WORD.search(json.dumps(i, ensure_ascii=False))) for i in on
        )
        provisional_ids.update(i["rule_id"] for i in on)
        ok = ok and row["provisional_items_flag_off"] == 0
        ok = ok and row["reviewed_parts_identical_flag_on"]
        gates["PASS" if ok else "FAIL"] += 1
    keys = (
        "journeys",
        "outlook_answers",
        "outlook_answers_facts_and_reviewed_context_only",
        "answers_with_reviewed_evidence",
        "tenth_lord_children_rule_shown",
        "timing_answers",
        "timing_answers_stating_no_reviewed_timing_rule",
        "timing_answers_with_periods",
        "periods_listed",
        "periods_continuing_past_the_window",
        "period_themes_with_pending_line",
        "period_theme_mahadasha_lines",
        "period_theme_mahadasha_lines_labelled_primary",
        "period_theme_antardasha_lines",
        "period_theme_antardasha_lines_labelled_secondary",
        "comparison_answers_not_ranked",
        "other_domain_terms_shown",
        "out_of_scope_answers",
        "out_of_scope_one_line",
        "child_guard_violations",
        "children_domain_guard_failures",
        "date_claims_detected",
        "dasha_followups",
        "dasha_followups_pointing_to_the_periods",
        "dasha_followups_saying_no_timing_evidence",
        "child_sex_followups_one_line",
        "provisional_items_flag_off",
        "reviewed_parts_identical_flag_on",
        "provisional_items_flag_on",
        "provisional_rule_items_flag_on",
        "provisional_signification_items_flag_on",
        "provisional_items_wording_held",
        "provisional_items_source_verse_held",
        "provisional_items_with_translation_sent",
        "provisional_items_failing_children_guards",
        "provisional_items_with_other_domain_terms",
        "provisional_items_labelled_reviewed",
    )
    return {
        **{key: counts[key] for key in keys},
        "reviewed_rule_ids_shown": dict(sorted(rule_ids.items())),
        "provisional_ids_shown_flag_on": dict(sorted(provisional_ids.items())),
        "hard_gates": dict(sorted(gates.items())),
    }


# The user's own words and verbatim source text are not answer wording.
_NOT_ANSWER_TEXT = {"question", "followup", "original_text"}


def _displayed_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [
            text
            for key, item in value.items()
            if key not in _NOT_ANSWER_TEXT
            for text in _displayed_strings(item)
        ]
    if isinstance(value, list):
        return [text for item in value for text in _displayed_strings(item)]
    return []


def _child_guard_counts(*row_groups: list[dict[str, Any]]) -> dict[str, Any]:
    """v27: the children wording guard over every displayed string of every journey."""
    from astrologer.composition.children_guard import CHILD_HELD_NOTICE, child_wording_violation

    strings = [text for rows in row_groups for row in rows for text in _displayed_strings(row)]
    hits = sorted({hit for text in strings if (hit := child_wording_violation(text))})
    held = [
        item["rule_id"]
        for rows in row_groups
        for row in rows
        for item in row.get("provisional_flag_on", ())
        if item.get("source_verse_held")
    ]
    return {
        "journeys": sum(len(rows) for rows in row_groups),
        "strings_checked": len(strings),
        "violations": sum(child_wording_violation(text) is not None for text in strings),
        "violating_words": hits,
        # Text the guard held shows a notice: none in any journey's answer text; the source
        # verses held (flag on) per rule id.
        "held_text_notices": sum(CHILD_HELD_NOTICE in text for text in strings),
        "source_verses_held_flag_on": len(held),
        "source_verses_held_by_rule": dict(sorted(Counter(held).items())),
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
