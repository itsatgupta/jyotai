import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { QuestionAnalysis } from "./QuestionAnalysis";
import type { AnalysisResult } from "../lib/contracts";

const baseAnswer = {
  answer: "Your D1 chart contains reviewed contextual evidence relevant to Career.",
  referenced_evidence_item_ids: [],
  timing_answered: false as const,
  corpus_limitation: false,
  interpretation_contract_sha256: "a".repeat(64),
  manifest_id: "jyotish.production.cumulative",
  manifest_version: "v10",
  policy_id: "governed-answer-composition",
  policy_version: "v1",
  prompt_version: "governed-answer-composition-prompt-v1",
  limitations: [],
};

const broadWindow = {
  rule_id: "bphs.timing.vimshottari.career.10th_lord.in_4.md.v1", precision: "BROAD_PERIOD" as const,
  source_start: "2030-03-12T00:00:00Z", source_end: "2046-03-12T00:00:00Z", effective_start: "2030-03-12T00:00:00Z", effective_end: "2046-03-12T00:00:00Z",
  reviewed_statement: "Reviewed source-backed Career timing context.", why_this_period_applies: "The D1 tenth-house lord is placed in the fourth house.", limitations: ["no exact event date", "no promotion claim"],
  source: { source_work: "Brihat Parāśara Horā Śāstra", section: "Dasha-phala", verse: "87", chart_scope: "D1/Rashi" as const, dasha_scope: "Vimshottari Mahadasha", precision: "BROAD_PERIOD" as const },
};

const subPeriodWindow = {
  ...broadWindow, rule_id: "bphs.timing.vimshottari.career.moon_md.venus_ad.own_or_exaltation.v1", precision: "SUB_PERIOD" as const,
  source_start: "2031-03-12T00:00:00Z", source_end: "2032-03-12T00:00:00Z", effective_start: "2031-03-12T00:00:00Z", effective_end: "2032-03-12T00:00:00Z",
  why_this_period_applies: "This sub-period corresponds to Moon Mahadasha and Venus Antardasha.", source: { ...broadWindow.source, verse: "140", dasha_scope: "Vimshottari Moon Mahadasha / Venus Antardasha", precision: "SUB_PERIOD" as const },
};

function result(status: "MATCH" | "NO_MATCH" | "UNKNOWN" = "MATCH"): AnalysisResult {
  const timing = status === "MATCH"
    ? {
        domain: "career" as const, timing_answerability_established: true, status,
        timing_release_id: "jyotish.timing.production.career@v1", timing_release_version: "v1",
        windows: [broadWindow], message: "Reviewed Career timing context is available for this chart.",
      }
    : {
        domain: "career" as const, timing_answerability_established: false, status,
        timing_release_id: "jyotish.timing.production.career@v1", timing_release_version: "v1", windows: [],
        message: status === "UNKNOWN" ? "Available chart facts were not sufficient to evaluate the reviewed Career timing rule." : "No reviewed Career timing window is currently established from the active governed timing corpus.",
      };
  return {
    context: {} as AnalysisResult["context"],
    routing: { status: "routable", intents: [{ intent_id: "intent-1", domain: "career", shape: "timing", temporal_intent: "time_bound", requires_timing: true }], issues: [] },
    selections: [], answers: [{ ...baseAnswer, timing }],
  };
}

describe("QuestionAnalysis Career timing", () => {
  it("puts the direct answer first and labels calculated fact provenance correctly", () => {
    const answered = result("NO_MATCH");
    const placement = "Your D1 tenth-house lord is placed in the fifth house.";
    const interpretation = "Reviewed fifth or eleventh house Career context.";
    answered.answers[0].answer = `${placement} No reviewed Career timing rule matched the requested period. ${interpretation}`;
    answered.answers[0].claim_ledger = {
      ledger_version: "career-claim-ledger-v1", domain: "career", question_shape: "timing", requested_question_shape: "period",
      claims: [
        { claim_id: "career-fact", kind: "CALCULATED_FACT", evaluation_status: "MATCH", fact_ids: ["d1.tenth_lord.house"], rule_ids: [], evidence_item_ids: ["linked-evidence"], calculation_version: "v1", methodology_version: "lahiri", source_reference: "d1.tenth_lord.house", permitted_wording: placement, timing_reference: null, authorized_precision: null, missing_evidence: [] },
        { claim_id: "career-interpretation", kind: "APPROVED_INTERPRETATION", evaluation_status: "MATCH", fact_ids: ["d1.tenth_lord.house"], rule_ids: ["reviewed-rule"], evidence_item_ids: ["linked-evidence"], calculation_version: "v1", methodology_version: "lahiri", source_reference: "reviewed source", permitted_wording: interpretation, timing_reference: null, authorized_precision: null, missing_evidence: [] },
      ],
    };
    render(<QuestionAnalysis result={answered} onAnalyze={vi.fn()} loading={false} error="" />);
    const sections = document.querySelectorAll(".detailed-answer > section");
    expect(sections[0]).toHaveTextContent("No reviewed Career timing rule matched");
    expect(sections[1]).toHaveTextContent(placement);
    expect(sections[2]).toHaveTextContent(interpretation);
    expect(document.querySelector(".evidence-details")).toHaveTextContent("Not applicable to a calculated fact");
    expect(document.querySelector(".evidence-details")).toHaveTextContent("Linked interpretation evidence ID");
    expect(document.querySelector(".evidence-details")).toHaveTextContent("Calculated fact provenance");
  });

  it("keeps prior turns visible and offers only supported follow-ups", () => {
    const first = result();
    first.routing.intents[0].time_range = { start_date: "2027-01-01", end_date: "2027-12-31" };
    first.answers[0].claim_ledger = {
      ledger_version: "career-claim-ledger-v1", domain: "career", question_shape: "timing", requested_question_shape: "period",
      claims: [{ claim_id: "career-timing-1", kind: "APPROVED_TIMING_INTERPRETATION", evaluation_status: "MATCH", fact_ids: [], rule_ids: [broadWindow.rule_id], evidence_item_ids: [], calculation_version: "v1", methodology_version: "v1", source_reference: "BPHS, verse 87", permitted_wording: broadWindow.reviewed_statement, timing_reference: "[2030-03-12,2046-03-12)", authorized_precision: "BROAD_PERIOD", missing_evidence: [] }],
    };
    const messages = [{ question: "How is my career in 2027?", response: { state: { consultation_id: "one", turn_id: "turn-one", domain: "career", intent: first.routing.intents[0], claim_ids: ["career-timing-1"], evidence_item_ids: [], timing_references: [], manifest_id: "production", manifest_version: "v1", methodology_version: "v1", timing_release_id: "timing", timing_release_version: "v1", limitation: false }, analysis: first, reply: null, status: "answered" as const, source_references: [], resolved_claim_ids: [], resolved_evidence_item_ids: [], resolved_timing_references: [] } }];
    const onNew = vi.fn();
    render(<QuestionAnalysis result={first} messages={messages} onNewConsultation={onNew} onAnalyze={vi.fn()} loading={false} error="" />);
    expect(screen.getByRole("log")).toHaveTextContent("How is my career in 2027?");
    expect(screen.getByRole("button", { name: "Which Dasha applies?" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "What about 2028?" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /better than/ })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Wealth" })).not.toBeInTheDocument();
    screen.getByRole("button", { name: "Start a new consultation" }).click();
    expect(onNew).toHaveBeenCalledOnce();
  });

  it("keeps unsupported exact-month requests free of broad timing windows", () => {
    const answered = result();
    answered.answers[0].answer = "The requested timing precision is unsupported by the active Career methods.";
    answered.answers[0].timing = {
      ...answered.answers[0].timing!, status: "UNSUPPORTED", scope: "precision_unsupported",
      timing_answerability_established: false, windows: [],
      message: "The requested month or date precision is not supported by active Career timing rules; timing was not evaluated.",
    };
    render(<QuestionAnalysis result={answered} onAnalyze={vi.fn()} loading={false} error="" />);
    expect(screen.getByText(/requested timing precision is unsupported/)).toBeInTheDocument();
    expect(screen.getByText(/No Career timing evidence was evaluated for this request/)).toBeInTheDocument();
    expect(screen.queryByText(/Broad period/)).not.toBeInTheDocument();
    expect(screen.queryByText(/default 40-year forward horizon/)).not.toBeInTheDocument();
  });

  it("shows a Career direct answer and linked source without repeating its interpretation", () => {
    const answered = result();
    answered.answers[0].answer = broadWindow.reviewed_statement;
    answered.answers[0].claim_ledger = {
      ledger_version: "career-claim-ledger-v1", domain: "career", question_shape: "timing", requested_question_shape: "period",
      claims: [{
        claim_id: "career-timing-1", kind: "APPROVED_TIMING_INTERPRETATION", evaluation_status: "MATCH",
        fact_ids: [], rule_ids: [broadWindow.rule_id], evidence_item_ids: [],
        calculation_version: "v2", methodology_version: "vimshottari-v1",
        source_reference: "Brihat Parāśara Horā Śāstra, Dasha-phala, verse 87",
        permitted_wording: broadWindow.reviewed_statement,
        timing_reference: "[2030-03-12,2046-03-12)", authorized_precision: "BROAD_PERIOD", missing_evidence: [],
      }],
    };
    render(<QuestionAnalysis result={answered} onAnalyze={vi.fn()} loading={false} error="" />);
    expect(screen.getAllByText(broadWindow.reviewed_statement)).toHaveLength(1);
    expect(document.querySelector(".evidence-details")).toHaveTextContent(/Approved interpretation sources:.*bphs\.timing\.vimshottari\.career/);
    expect(screen.queryByText("Source-backed timing interpretation")).not.toBeInTheDocument();
    expect(screen.getByText("View governed evidence & methodology")).toBeInTheDocument();
  });

  it("renders application-owned broad timing dates and limitations", () => {
    render(<QuestionAnalysis result={result()} onAnalyze={vi.fn()} loading={false} error="" />);
    expect(screen.getByText("Career Timing Context")).toBeInTheDocument();
    expect(screen.getAllByText("Broad period")[0]).toBeInTheDocument();
    expect(screen.getByText(/Displayed intersection: 2030-03-12 00:00 UTC to 2046-03-12 00:00 UTC/)).toBeInTheDocument();
    expect(screen.getByText("Source-backed timing interpretation")).toBeInTheDocument();
    expect(screen.getByText("no exact event date")).toBeInTheDocument();
    expect(screen.queryByText(/exact prediction/i)).not.toBeInTheDocument();
  });

  it("renders mixed precision windows independently with collapsed provenance", () => {
    const mixed = result();
    mixed.answers[0].timing!.windows = [broadWindow, subPeriodWindow];
    render(<QuestionAnalysis result={mixed} onAnalyze={vi.fn()} loading={false} error="" />);
    expect(screen.getAllByText("Broad period")[0]).toBeInTheDocument();
    expect(screen.getAllByText("Sub-period")[0]).toBeInTheDocument();
    expect(screen.getByText(/Moon Mahadasha and Venus Antardasha/)).toBeInTheDocument();
    expect(screen.getAllByText("View timing evidence & methodology")).toHaveLength(2);
    expect(document.querySelectorAll(".timing-provenance")).toHaveLength(2);
    expect([...document.querySelectorAll<HTMLDetailsElement>(".timing-provenance")].every((item) => !item.open)).toBe(true);
    expect(screen.queryByText(/strongest|best/i)).not.toBeInTheDocument();
  });

  it("renders no-match and UNKNOWN messages distinctly", () => {
    const { rerender } = render(<QuestionAnalysis result={result("NO_MATCH")} onAnalyze={vi.fn()} loading={false} error="" />);
    expect(screen.getByText(/No reviewed Career timing window/)).toBeInTheDocument();
    rerender(<QuestionAnalysis result={result("UNKNOWN")} onAnalyze={vi.fn()} loading={false} error="" />);
    expect(screen.getByText(/not sufficient to evaluate/)).toBeInTheDocument();
  });

  it("shows requested and evaluated ranges and the source interval separately", () => {
    const bounded = result();
    bounded.answers[0].timing = {
      ...bounded.answers[0].timing!,
      scope: "requested_range",
      requested_start_date: "2031-03-01",
      requested_end_date: "2031-03-31",
      calendar_timezone_offset: "+0530",
      evaluated_start: "2031-03-01T00:00:00Z",
      evaluated_end: "2031-04-01T00:00:00Z",
      windows: [{ ...broadWindow, effective_start: "2031-03-01T00:00:00Z", effective_end: "2031-04-01T00:00:00Z" }],
    };
    render(<QuestionAnalysis result={bounded} onAnalyze={vi.fn()} loading={false} error="" />);
    expect(screen.getByText(/Requested calendar dates: 2031-03-01 through 2031-03-31 \(inclusive, UTC\+05:30\)/)).toBeInTheDocument();
    expect(screen.getByText(/Evaluated interval: 2031-03-01 00:00 UTC to 2031-04-01 00:00 UTC/)).toBeInTheDocument();
    expect(screen.getByText(/Displayed intersection: 2031-03-01 00:00 UTC to 2031-04-01 00:00 UTC/)).toBeInTheDocument();
    expect(screen.getByText(/2030-03-12 00:00 UTC to 2046-03-12 00:00 UTC/)).toBeInTheDocument();
  });

  it("distinguishes full and partial unsupported ranges", () => {
    const unsupported = result("NO_MATCH");
    unsupported.answers[0].timing = { ...unsupported.answers[0].timing!, status: "UNSUPPORTED", scope: "requested_range", requested_start_date: "2070-01-01", requested_end_date: "2070-12-31" };
    const { rerender } = render(<QuestionAnalysis result={unsupported} onAnalyze={vi.fn()} loading={false} error="" />);
    expect(screen.getByText(/No Career timing evidence was evaluated/)).toBeInTheDocument();
    const partial = result("NO_MATCH");
    partial.answers[0].timing = { ...partial.answers[0].timing!, scope: "requested_range", requested_start_date: "2065-01-01", requested_end_date: "2067-12-31", evaluated_start: "2065-01-01T00:00:00Z", evaluated_end: "2066-01-01T00:00:00Z", partially_supported: true };
    rerender(<QuestionAnalysis result={partial} onAnalyze={vi.fn()} loading={false} error="" />);
    expect(screen.getByText(/Only the displayed evaluated portion/)).toBeInTheDocument();
  });

  it.each(["property", "marriage", "health"])("shows no interpretation for unsupported %s", (domain) => {
    const unsupported = result();
    unsupported.routing.intents[0].domain = domain;
    unsupported.selections = [{ question_intent: unsupported.routing.intents[0], selected_matched: [], relevant_unmatched: [], relevant_unknown: [], excluded: [], capability_summary: { timing_requested: false, timing_answerability_established: false, has_matched_evidence: false } }];
    unsupported.answers[0].narrative = { summary: "Unapproved interpretive claim", explanation: "Unapproved detail", question_relevance: "Unapproved relevance" };
    render(<QuestionAnalysis result={unsupported} onAnalyze={vi.fn()} loading={false} error="" />);
    expect(screen.getByText("No reviewed interpretation is currently available for this area from the active governed corpus.")).toBeInTheDocument();
    expect(screen.queryByText("Unapproved interpretive claim")).not.toBeInTheDocument();
    expect(screen.queryByText("Career Timing Context")).not.toBeInTheDocument();
  });

  it("shows supplied source references and a loading state", () => {
    const answered = result();
    answered.answers[0].evidence = [{ placement_explanation: "Supplied placement", reviewed_statement: "Reviewed statement", question_framing: "Supplied framing", source_work: "BPHS", source_section: "Section 1", source_reference: "Verse 12", chart_scope: "D1/Rashi", posture: "static/contextual", domain: "career" }];
    render(<QuestionAnalysis result={answered} onAnalyze={vi.fn()} loading={true} error="" />);
    expect(screen.getByRole("status")).toHaveTextContent("Reviewing the available chart evidence");
    expect(screen.getByRole("button", { name: "Reviewing evidence…" })).toBeDisabled();
    expect(screen.getByText("Verse 12")).toBeInTheDocument();
  });
});
