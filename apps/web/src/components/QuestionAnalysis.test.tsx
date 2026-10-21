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
});
