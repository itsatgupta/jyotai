import { readFileSync } from "node:fs";

import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { QuestionAnalysis } from "./QuestionAnalysis";
import type { AnalysisResult, CareerYearColumn, CareerYearComparison, ComparisonSentence, ConsultationMessage } from "../lib/contracts";

const ABSENCE = "An indication not applying in a year is not evidence against that year.";
const sentence = (text: string, basis: ComparisonSentence["basis"] = "fixed"): ComparisonSentence => ({ text, basis, claim_ids: [], fact_ids: basis === "fact" ? ["fact"] : [], rule_ids: basis === "rule" ? ["rule"] : [], calc_method_ids: [] });

function column(year: number, applies: boolean): CareerYearColumn {
  return {
    year, dasha_segments: [], periods: [sentence(`In ${year} your calculated Vimshottari periods are the Moon Mahadasha.`, "fact")],
    lord_facts: [sentence("Moon rules your 12th house.", "fact")], timing_status: applies ? "MATCH" : "NO_MATCH",
    timing_indications: [], timing: [sentence(applies ? "Admitted timing text, verbatim." : "No reviewed timing indication applies.", applies ? "rule" : "fixed")],
    co_references: [sentence("No co-reference link was found for this year.")], dasha_interpretation: sentence("No reviewed interpretation of these Dasha periods is admitted."),
    manifest_id: "jyotish.production.cumulative", manifest_version: "v10", methodology_version: "m", timing_release_id: "t", timing_release_version: "v2", synthesis_version: "career-synthesis-v1", answer_plan_version: "career-answer-plan-v1",
  };
}

const comparison: CareerYearComparison = {
  view_version: "comparison-view-v1", comparison_mode: "SIDE_BY_SIDE", ranking_status: "unsupported", unit: "calendar_year", years: [2027, 2028],
  direct: [sentence("I can't rank 2027 against 2028 for your career: JyotishAI has no reviewed method for ranking periods."), sentence("A reviewed timing indication applies in 2027 and none applies in 2028.")],
  differences: [sentence("In 2027 your calculated Vimshottari periods are the Moon Mahadasha.", "fact"), sentence("In 2028, no reviewed timing indication applies."), sentence(ABSENCE)],
  natal_shared: [sentence("Your 10th lord is Venus, in your 10th house.", "fact")],
  columns: [column(2027, true), column(2028, false)],
  why_no_ranking: [sentence("This is a factual side-by-side, not a verdict.")],
  limitations: [sentence("None of this establishes a specific event, promotion, income change, or date.")],
};

const state = { consultation_id: "one", turn_id: "first", domain: "career", intent: null, claim_ids: [], evidence_item_ids: [], timing_references: [], manifest_id: "production", manifest_version: "v1", methodology_version: "v1", timing_release_id: "timing", timing_release_version: "v1", limitation: true };

function analysis(): AnalysisResult {
  return {
    context: {} as AnalysisResult["context"],
    routing: { status: "routable", intents: [{ intent_id: "intent-1", domain: "career", shape: "comparative", temporal_intent: "time_bound", requires_timing: true }], issues: [] },
    selections: [],
    answers: [{ answer: "plain", referenced_evidence_item_ids: [], timing_answered: false, corpus_limitation: false, interpretation_contract_sha256: "a".repeat(64), manifest_id: "m", manifest_version: "v", policy_id: "p", policy_version: "v1", prompt_version: "p", limitations: [], career_comparison: comparison }],
  } as unknown as AnalysisResult;
}

describe("CareerComparison side-by-side", () => {
  it("shows the direct line, then differences, natal, columns in a disclosure, why, and limits in order", () => {
    render(<QuestionAnalysis result={analysis()} onAnalyze={vi.fn()} loading={false} error="" />);
    const view = document.querySelector(".career-comparison")!;
    const order = ["comparison-direct", "comparison-differs", "comparison-natal", "comparison-columns-disclosure", "comparison-why", "comparison-limits"];
    expect(Array.from(view.children).map((child) => order.find((name) => child.classList.contains(name)))).toEqual(order);
    expect(screen.getByRole("heading", { name: "What differs between 2027 and 2028" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Same in both years (natal)" })).toBeInTheDocument();
    expect(within(view.querySelector(".comparison-differs")! as HTMLElement).getByText(ABSENCE)).toBeInTheDocument();
    expect(view.querySelector("details.comparison-columns-disclosure")).not.toHaveAttribute("open");
    expect(view.querySelectorAll(".comparison-column")).toHaveLength(2);
    expect(view.textContent).not.toMatch(/\b(better|worse|stronger|weaker|fewer)\b/i);
  });

  it("offers per-year drill-down buttons and comparison follow-up suggestions", () => {
    const onAnalyze = vi.fn().mockResolvedValue(true);
    const messages: ConsultationMessage[] = [{ question: "Which is better for my career, 2027 or 2028?", response: { state, analysis: analysis(), reply: null, status: "answered", source_references: [], resolved_claim_ids: [], resolved_evidence_item_ids: [], resolved_timing_references: [] } }];
    render(<QuestionAnalysis result={null} messages={messages} onAnalyze={onAnalyze} loading={false} error="" />);
    const columns = document.querySelectorAll<HTMLElement>(".comparison-column");
    fireEvent.click(within(columns[1]).getByRole("button", { name: "Explain 2028" }));
    expect(onAnalyze).toHaveBeenCalledWith("Explain 2028", "Explain 2028");
    const suggested = screen.getByLabelText("Suggested follow-ups");
    expect(within(suggested).getAllByRole("button").map((button) => button.textContent)).toEqual(["Why?", "Explain 2027", "Explain 2028"]);
  });

  it("renders a comparison follow-up reply as the side-by-side, not as raw text", () => {
    const first = { question: "How is my career in 2027?", response: { state, analysis: { ...analysis(), answers: [] }, reply: null, status: "answered" as const, source_references: [], resolved_claim_ids: [], resolved_evidence_item_ids: [], resolved_timing_references: [] } };
    const follow = { question: "Is 2028 better than 2027?", response: { state: { ...state, turn_id: "second" }, analysis: null, reply: "plain text reply", status: "unsupported" as const, source_references: [], resolved_claim_ids: [], resolved_evidence_item_ids: [], resolved_timing_references: [], career_comparison: comparison } };
    render(<QuestionAnalysis result={null} messages={[first, follow]} onAnalyze={vi.fn()} loading={false} error="" />);
    expect(document.querySelectorAll(".consultation-reply .career-comparison")).toHaveLength(1);
    expect(screen.queryByText("plain text reply")).not.toBeInTheDocument();
  });

  it("stacks the two columns on mobile widths in its stylesheet", () => {
    const css = readFileSync("src/components/CareerComparison.css", "utf8");
    expect(css).toMatch(/\.comparison-columns \{[^}]*grid-template-columns: repeat\(2, minmax\(0, 1fr\)\)/);
    expect(css).toMatch(/@media \(max-width: 700px\) \{\s*\.comparison-columns \{ grid-template-columns: 1fr; \}/);
  });

  it("names the period in the fallback timing-claim button label", () => {
    const claim = (id: string, kind: "APPROVED_INTERPRETATION" | "APPROVED_TIMING_INTERPRETATION", lords?: string[]) => ({ claim_id: id, kind, evaluation_status: "MATCH" as const, fact_ids: [], rule_ids: ["r"], evidence_item_ids: [], calculation_version: "v", methodology_version: "m", source_reference: "s", permitted_wording: "w", missing_evidence: [], ...(lords ? { period_lords: lords } : {}) });
    const first = analysis();
    first.answers = [{ ...first.answers[0], career_comparison: null, claim_ledger: { ledger_version: "v1", domain: "career", question_shape: "timing", requested_question_shape: "period", claims: [claim("natal", "APPROVED_INTERPRETATION"), claim("timed", "APPROVED_TIMING_INTERPRETATION", ["moon", "venus"])] } }];
    const messages: ConsultationMessage[] = [
      { question: "How is my career in 2027?", response: { state, analysis: first, reply: null, status: "answered", source_references: [], resolved_claim_ids: [], resolved_evidence_item_ids: [], resolved_timing_references: [] } },
      { question: "Which one?", response: { state: { ...state, turn_id: "second" }, analysis: null, reply: "Which claim do you mean?", status: "clarification", source_references: [], resolved_claim_ids: [], resolved_evidence_item_ids: [], resolved_timing_references: [] } },
    ];
    render(<QuestionAnalysis result={null} messages={messages} onAnalyze={vi.fn()} loading={false} error="" />);
    expect(screen.getByRole("button", { name: "Explain the reviewed timing indication for Moon Mahadasha with Venus Antardasha" })).toBeInTheDocument();
  });
});
