import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { QuestionAnalysis } from "./QuestionAnalysis";
import type { AnalysisResult, ConsultationMessage } from "../lib/contracts";

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
  it("renders a planned year consultation once and keeps exact UTC periods in evidence details", () => {
    const answered = result("NO_MATCH");
    const reviewed = "Reviewed natal Career context from the active source.";
    answered.answers[0].answer = `For 2027, ${reviewed} Calculated Vimshottari periods in 2027 (local dates): Rahu Mahadasha, Saturn Antardasha. No reviewed Career timing rule matched 2027. The available reviewed timing evidence does not establish a specific Career outcome for 2027.`;
    answered.answers[0].consultation_sections = [
      { kind: "direct", text: `For 2027, ${reviewed}` },
      { kind: "dasha", text: "Calculated Vimshottari periods in 2027 (local dates): Rahu Mahadasha, Saturn Antardasha." },
      { kind: "timing", text: "No reviewed Career timing rule matched 2027." },
      { kind: "limit", text: "The available reviewed timing evidence does not establish a specific Career outcome for 2027." },
    ];
    answered.answers[0].career_answer_plan = {
      plan_version: "career-answer-plan-v1", question_intent: answered.routing.intents[0],
      requested_time_scope: { start_date: "2027-01-01", end_date: "2027-12-31" },
      calculated_fact_ids: ["jyotish.d1.house_lord.10.placement_house"], matched_claim_ids: ["natal-1"],
      timing_evidence_ids: [], timing_references: [], approved_source_locators: ["reviewed source"],
      limitation_ids: ["career-year-outcome-unestablished", "career-timing-no_match"], answerability: "NATAL_CONTEXT_ONLY",
      dasha_segments: [{ segment_id: "segment-1", mahadasha_lord: "rahu", antardasha_lord: "saturn", mahadasha_start: "2020-01-01T00:00:00Z", mahadasha_end: "2038-01-01T00:00:00Z", antardasha_start: "2026-01-01T00:00:00Z", antardasha_end: "2028-01-01T00:00:00Z", effective_start: "2027-01-01T00:00:00Z", effective_end: "2028-01-01T00:00:00Z", local_start: "2027-01-01T05:30:00+05:30", local_end: "2028-01-01T05:30:00+05:30" }],
    };
    render(<QuestionAnalysis result={answered} onAnalyze={vi.fn()} loading={false} error="" />);
    const sections = document.querySelectorAll(".detailed-answer > section");
    expect(sections).toHaveLength(4);
    expect(sections[0]).toHaveTextContent(reviewed);
    expect(sections[1]).toHaveTextContent("Rahu Mahadasha, Saturn Antardasha");
    expect(sections[2]).toHaveTextContent("No reviewed Career timing rule matched 2027");
    expect(sections[3]).toHaveTextContent("does not establish a specific Career outcome");
    expect(document.querySelector(".detailed-answer")?.textContent?.match(new RegExp(reviewed, "g"))).toHaveLength(1);
    expect(document.querySelector(".evidence-details")).toHaveTextContent("2027-01-01 00:00 UTC to 2028-01-01 00:00 UTC");
    expect(document.querySelector(".evidence-details")).not.toHaveAttribute("open");
  });

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
    expect(document.querySelector(".technical-disclosure")).not.toHaveAttribute("open");
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
    screen.getByRole("button", { name: "New Consultation" }).click();
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
    expect(screen.getByText(/Displayed intersection: Mar 12, 2030 to Mar 12, 2046/)).toBeInTheDocument();
    expect(document.querySelector(".timing-provenance")).toHaveTextContent("2030-03-12 00:00 UTC to 2046-03-12 00:00 UTC");
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
    expect(screen.getByText("This period overlaps the previous displayed window.")).toBeInTheDocument();
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
    expect(screen.getByText(/2031-03-01 through 2031-03-31 \(inclusive, UTC\+05:30\)/)).toBeInTheDocument();
    expect(screen.getByText(/Evaluated interval: Mar 1, 2031 to Apr 1, 2031/)).toBeInTheDocument();
    expect(screen.getByText(/Displayed intersection: Mar 1, 2031 to Apr 1, 2031/)).toBeInTheDocument();
    expect(document.querySelector(".timing-provenance")).toHaveTextContent("2031-03-01 00:00 UTC to 2031-04-01 00:00 UTC");
    expect(screen.getByText(/2030-03-12 00:00 UTC to 2046-03-12 00:00 UTC/)).toBeInTheDocument();
  });

  it("offers readable clarification choices backed by the exact prior claim IDs", () => {
    const first = result("NO_MATCH");
    first.routing.intents[0].time_range = { start_date: "2027-01-01", end_date: "2027-12-31" };
    first.answers[0].claim_ledger = {
      ledger_version: "career-claim-ledger-v1", domain: "career", question_shape: "timing", requested_question_shape: "period",
      claims: [
        { claim_id: "career-fact", kind: "CALCULATED_FACT", evaluation_status: "MATCH", fact_ids: [], rule_ids: [], evidence_item_ids: [], calculation_version: "v1", methodology_version: "v1", source_reference: "fact", permitted_wording: "Your D1 tenth-house lord is placed in the fifth house.", missing_evidence: [] },
        { claim_id: "career-natal", kind: "APPROVED_INTERPRETATION", evaluation_status: "MATCH", fact_ids: [], rule_ids: ["natal-rule"], evidence_item_ids: [], calculation_version: "v1", methodology_version: "v1", source_reference: "source", permitted_wording: "Reviewed Career context.", missing_evidence: [] },
        { claim_id: "career-timing-status", kind: "INSUFFICIENT_EVIDENCE", evaluation_status: "NO_MATCH", fact_ids: [], rule_ids: ["timing-rule"], evidence_item_ids: [], calculation_version: "v1", methodology_version: "v1", source_reference: "source", permitted_wording: "No reviewed timing rule matched.", missing_evidence: [] },
      ],
    };
    const state = { consultation_id: "one", turn_id: "first", domain: "career", intent: first.routing.intents[0], claim_ids: ["career-natal", "career-timing-status"], evidence_item_ids: [], timing_references: [], manifest_id: "production", manifest_version: "v1", methodology_version: "v1", timing_release_id: "timing", timing_release_version: "v1", limitation: false };
    const messages = [
      { question: "How is my career in 2027?", response: { state, analysis: first, reply: null, status: "answered" as const, source_references: [], resolved_claim_ids: [], resolved_evidence_item_ids: [], resolved_timing_references: [] } },
      { question: "Why did you say that?", response: { state: { ...state, turn_id: "second" }, analysis: null, reply: "Which claim do you mean?", status: "clarification" as const, source_references: [], resolved_claim_ids: [], resolved_evidence_item_ids: [], resolved_timing_references: [] } },
    ];
    const onAnalyze = vi.fn().mockResolvedValue(true);
    render(<QuestionAnalysis result={first} messages={messages} onAnalyze={onAnalyze} loading={false} error="" />);
    fireEvent.click(screen.getByRole("button", { name: "Explain the fifth-house Career interpretation" }));
    expect(onAnalyze).toHaveBeenCalledWith("Explain claim career-natal", "Explain the fifth-house Career interpretation", { reference_turn_id: "first", claim_ids: ["career-natal"] });
    fireEvent.click(screen.getByRole("button", { name: "Explain the 2027 Career timing limitation" }));
    expect(onAnalyze).toHaveBeenCalledWith("Explain claim career-timing-status", "Explain the 2027 Career timing limitation", { reference_turn_id: "first", claim_ids: ["career-timing-status"] });
  });

  it("shows Dasha follow-up transitions without microseconds and retains the exact reply", () => {
    const reply = "For 2027, the calculated Vimshottari periods are: Saturn Mahadasha, Sun Antardasha: source MD 2016-09-18T13:31:45.502436+00:00 to 2035-09-19T07:31:45.502436+00:00 UTC; local overlap 2027-01-01T00:00:00+00:00 to 2027-08-22T22:04:45.502436+00:00 (end exclusive). Saturn Mahadasha, Moon Antardasha: source MD 2016-09-18T13:31:45.502436+00:00 to 2035-09-19T07:31:45.502436+00:00 UTC; local overlap 2027-08-22T22:04:45.502436+00:00 to 2028-01-01T00:00:00+00:00 (end exclusive). No reviewed Career timing rule matched 2027. These calculated periods alone do not establish a promotion.";
    const response = { state: { consultation_id: "one", turn_id: "reply", domain: "career", intent: null, claim_ids: [], evidence_item_ids: [], timing_references: [], manifest_id: "production", manifest_version: "v1", methodology_version: "v1", timing_release_id: "timing", timing_release_version: "v1", limitation: true }, analysis: null, reply, status: "answered" as const, source_references: [], resolved_claim_ids: [], resolved_evidence_item_ids: [], resolved_timing_references: [] };
    render(<QuestionAnalysis result={null} messages={[{ question: "Which Dasha applies?", response }]} onAnalyze={vi.fn()} loading={false} error="" />);
    expect(document.querySelectorAll(".reply-period")).toHaveLength(2);
    expect(document.querySelector(".reply-period-grid")).toHaveTextContent("Aug 22, 2027, 22:04 UTC+00:00");
    expect(document.querySelector(".reply-period-grid")).not.toHaveTextContent(".502436");
    expect(document.querySelector(".reply-limitation")).toHaveTextContent("No reviewed Career timing rule matched 2027");
    expect(screen.getByText("View exact Dasha response and UTC precision").closest("details")).toHaveTextContent(".502436");
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
    expect(screen.getByLabelText("Your astrology question")).toHaveAttribute("readonly");
    expect(screen.getByLabelText("Your astrology question")).not.toBeDisabled();
    expect(screen.getByText("Verse 12")).toBeInTheDocument();
  });

  it("sends with Enter and keeps Shift+Enter available for a new line", async () => {
    const onAnalyze = vi.fn().mockResolvedValue(true);
    render(<QuestionAnalysis result={null} messages={[]} onAnalyze={onAnalyze} loading={false} error="" />);
    const input = screen.getByLabelText("Your astrology question");
    fireEvent.change(input, { target: { value: "How is my career?" } });
    fireEvent.keyDown(input, { key: "Enter", shiftKey: true });
    expect(onAnalyze).not.toHaveBeenCalled();
    fireEvent.keyDown(input, { key: "Enter" });
    await waitFor(() => expect(onAnalyze).toHaveBeenCalledWith("How is my career?"));
    expect(input).toHaveValue("");
  });

  it("follows the latest response only while the reader is near the page bottom", () => {
    const scrollIntoView = vi.fn();
    const original = Element.prototype.scrollIntoView;
    Object.defineProperty(Element.prototype, "scrollIntoView", { configurable: true, value: scrollIntoView });
    const frame = vi.spyOn(window, "requestAnimationFrame").mockImplementation((callback) => { callback(0); return 1; });
    Object.defineProperty(document.documentElement, "scrollHeight", { configurable: true, value: 2000 });
    Object.defineProperty(window, "innerHeight", { configurable: true, value: 600 });
    const message = (turnId: string) => ({ question: `Question ${turnId}`, response: { state: { turn_id: turnId }, analysis: null, reply: `Reply ${turnId}`, status: "answered", source_references: [], resolved_claim_ids: [] } }) as unknown as ConsultationMessage;
    try {
      const { rerender } = render(<QuestionAnalysis result={null} messages={[message("one")]} onAnalyze={vi.fn()} loading={false} error="" />);
      expect(scrollIntoView).toHaveBeenCalledTimes(1);
      Object.defineProperty(window, "scrollY", { configurable: true, value: 100 });
      fireEvent.scroll(window);
      rerender(<QuestionAnalysis result={null} messages={[message("one"), message("two")]} onAnalyze={vi.fn()} loading={false} error="" />);
      expect(scrollIntoView).toHaveBeenCalledTimes(1);
    } finally {
      Object.defineProperty(Element.prototype, "scrollIntoView", { configurable: true, value: original });
      frame.mockRestore();
    }
  });
});

describe("QuestionAnalysis Dasha context", () => {
  const framing = "These are calculated chart relationships, counted from your D1 Lagna; a reviewed Career interpretation of this Dasha is not yet available.";
  const context = {
    kind: "dasha_context" as const,
    text: `Rahu, your Mahadasha lord, is not assigned sign rulership under the classical seven-planet lordship convention used here. ${framing}`,
    fact_sentences: [{ text: "Rahu, your Mahadasha lord, is not assigned sign rulership under the classical seven-planet lordship convention used here.", fact_ids: ["jyotish.dasha_linkage.v1.lord.rahu.ruled_houses"] }],
    framing,
    interpretation_rule_ids: [],
  };

  it("renders the Dasha context after the chronology and keeps the fact mapping in evidence details", () => {
    const answered = result("NO_MATCH");
    answered.answers[0].consultation_sections = [
      { kind: "direct", text: "For 2027, no reviewed natal Career interpretation is available." },
      { kind: "dasha", text: "Calculated Vimshottari periods in 2027 (local dates): Rahu Mahadasha, Saturn Antardasha." },
      context,
      { kind: "timing", text: "No reviewed Career timing rule matched 2027." },
      { kind: "limit", text: "The available reviewed timing evidence does not establish a specific Career outcome for 2027." },
    ];
    answered.answers[0].answer = answered.answers[0].consultation_sections.map((section) => section.text).join(" ");
    render(<QuestionAnalysis result={answered} onAnalyze={vi.fn()} loading={false} error="" />);
    const sections = document.querySelectorAll(".detailed-answer > section");
    expect(sections).toHaveLength(5);
    expect(sections[2]).toHaveClass("consultation-section", "consultation-dasha_context");
    expect(sections[2]).toHaveTextContent("Calculated Dasha lord relationships");
    expect(sections[2]).toHaveTextContent(framing);
    expect(sections[2]).not.toHaveTextContent("jyotish.dasha_linkage.v1");
    const evidence = document.querySelector(".evidence-details");
    expect(evidence).not.toHaveAttribute("open");
    expect(evidence).toHaveTextContent("jyotish.dasha_linkage.v1.lord.rahu.ruled_houses");
  });

  it("renders the follow-up Dasha context separately from the limitation line", () => {
    const reply = `For 2027, the calculated Vimshottari periods are: Rahu Mahadasha, Venus Antardasha: source MD 2018-01-01T00:00:00+00:00 to 2036-01-01T00:00:00+00:00 UTC; local overlap 2027-01-01T00:00:00+00:00 to 2028-01-01T00:00:00+00:00 (end exclusive). ${context.text} No reviewed Career timing rule matched 2027. These calculated periods alone do not establish a promotion.`;
    const response = { state: { consultation_id: "one", turn_id: "reply", domain: "career", intent: null, claim_ids: [], evidence_item_ids: [], timing_references: [], manifest_id: "production", manifest_version: "v1", methodology_version: "v1", timing_release_id: "timing", timing_release_version: "v1", limitation: true }, analysis: null, reply, status: "answered" as const, source_references: [], resolved_claim_ids: [], resolved_evidence_item_ids: [], resolved_timing_references: [], consultation_sections: [context] };
    render(<QuestionAnalysis result={null} messages={[{ question: "Which Dasha applies?", response }]} onAnalyze={vi.fn()} loading={false} error="" />);
    expect(document.querySelector(".consultation-dasha_context")).toHaveTextContent(framing);
    expect(document.querySelector(".reply-limitation")).toHaveTextContent("No reviewed Career timing rule matched 2027");
    expect(document.querySelector(".reply-limitation")).not.toHaveTextContent("counted from your D1 Lagna");
    expect(document.querySelector(".reply-evidence")).toHaveTextContent("jyotish.dasha_linkage.v1.lord.rahu.ruled_houses");
  });
});

describe("QuestionAnalysis year synthesis", () => {
  const framing = "Each line states only a shared calculated reference between a reviewed indication and a period; it does not combine, weigh, or rank the indications.";
  const link = {
    link_type: "SAME_PLANET" as const,
    claim_id: "career-approved_interpretation-bphs.d1.house_lord.10.in_4_or_10.v1@v1",
    claim_label: "the reviewed indication about your 10th lord's placement",
    claim_subject: "your 10th lord, Jupiter",
    claim_fact_ids: ["jyotish.d1.house_lord.10.placement_house", "jyotish.d1.house.10.lord"],
    claim_rule_ids: ["bphs.d1.house_lord.10.in_4_or_10.v1"],
    dasha_fact_ids: ["jyotish.dasha_linkage.v1.lord.jupiter.ruled_houses", "jyotish.dasha_linkage.v1.lord.jupiter.is_tenth_lord"],
    dasha_rule_ids: [],
    calc_method_ids: ["jyotish.dasha_linkage.v1"],
    segment_ids: ["vimshottari-v1:a:b"],
    period_role: "Mahadasha" as const,
    period_lord: "Jupiter",
    period_span: "18 Mar 2015 to 18 Mar 2031",
    period_covers_year: true,
    shared_reference: "planet:jupiter",
    text: "Shared planet, Jupiter: the reviewed indication about your 10th lord's placement concerns your 10th lord, Jupiter, and Jupiter is the Mahadasha lord (18 Mar 2015 to 18 Mar 2031).",
  };
  const line = "The reviewed indication about your 10th lord's placement concerns your 10th lord, Jupiter, and Jupiter is the Mahadasha lord (18 Mar 2015 to 18 Mar 2031).";
  const why = { kind: "why" as const, text: `${line} ${framing}`, framing, synthesis_links: [link], synthesis_sentences: [{ text: line, claim_ids: [link.claim_id], fact_ids: [...link.claim_fact_ids, ...link.dasha_fact_ids], rule_ids: link.claim_rule_ids, calc_method_ids: link.calc_method_ids }] };
  const natal = { kind: "natal" as const, text: "The available reviewed natal Career context is: Your D1 tenth-house lord is placed in the fourth house." };

  it("renders the why section after the overview and keeps citations in evidence details", () => {
    const answered = result("MATCH");
    answered.answers[0].consultation_sections = [
      { kind: "direct", text: "For 2027, no reviewed Career timing rule matched. The reviewed indication about your 10th lord's placement concerns your 10th lord, Jupiter, and Jupiter is the Mahadasha lord throughout 2027." },
      why,
      natal,
      { kind: "dasha", text: "Calculated Vimshottari periods in 2027 (local dates): Jupiter Mahadasha, Moon Antardasha." },
      { kind: "limit", text: "The available reviewed timing evidence does not establish a specific Career outcome for 2027." },
    ];
    answered.answers[0].answer = answered.answers[0].consultation_sections.map((section) => section.text).join(" ");
    render(<QuestionAnalysis result={answered} onAnalyze={vi.fn()} loading={false} error="" />);
    const sections = document.querySelectorAll(".detailed-answer > section");
    expect(sections[1]).toHaveClass("consultation-section", "consultation-why");
    expect(sections[1]).toHaveTextContent("Why: shared references with the Dasha periods");
    expect(sections[1]).toHaveTextContent(framing);
    expect(sections[1]).not.toHaveTextContent("jyotish.dasha_linkage.v1.lord.jupiter.is_tenth_lord");
    const evidence = document.querySelector(".evidence-details");
    expect(evidence).toHaveTextContent("SAME_PLANET · planet:jupiter");
    expect(evidence).toHaveTextContent("jyotish.dasha_linkage.v1.lord.jupiter.is_tenth_lord");
    // Calculation method is provenance, shown apart from (absent) admitted Dasha rules.
    expect(evidence).toHaveTextContent("rules none admitted");
    expect(evidence).toHaveTextContent("calculation method jyotish.dasha_linkage.v1");
    expect(sections[2]).toHaveClass("consultation-section", "consultation-natal");
    expect(sections[2]).toHaveTextContent("Reviewed natal context");
    expect(sections[2]).toHaveTextContent(natal.text);
    expect(sections[0]).not.toHaveTextContent("natal Career context");
    for (const section of Array.from(sections).slice(0, 3)) expect(section).not.toHaveTextContent(link.claim_id);
  });

  it("renders a Why? reply with its synthesis citations behind a disclosure", () => {
    const reply = `For 2027: ${why.text} To go deeper, choose the reviewed indication about your 10th lord's placement for its rule, source and calculated facts, or ask about a named Dasha period.`;
    const response = { state: { consultation_id: "one", turn_id: "reply", domain: "career", intent: null, claim_ids: [], evidence_item_ids: [], timing_references: [], manifest_id: "production", manifest_version: "v1", methodology_version: "v1", timing_release_id: "timing", timing_release_version: "v1", limitation: false }, analysis: null, reply, status: "answered" as const, source_references: [], resolved_claim_ids: [link.claim_id], resolved_evidence_item_ids: [], resolved_timing_references: [], consultation_sections: [why] };
    render(<QuestionAnalysis result={null} messages={[{ question: "Why?", response }]} onAnalyze={vi.fn()} loading={false} error="" />);
    expect(screen.getByText(reply)).toBeInTheDocument();
    expect(screen.getByText(reply)).not.toHaveTextContent(link.claim_id);
    expect(screen.queryByText("Choose what to explain")).not.toBeInTheDocument();
    const details = document.querySelector(".reply-evidence");
    expect(details).toHaveTextContent("View synthesis citations");
    expect(details).toHaveTextContent("jyotish.dasha_linkage.v1.lord.jupiter.ruled_houses");
  });

  it("renders server choices as plain-language buttons that send ids only as references", () => {
    const first = result("MATCH");
    const state = { consultation_id: "one", turn_id: "first", domain: "career", intent: first.routing.intents[0], claim_ids: [link.claim_id, "career-timing-1"], evidence_item_ids: [], timing_references: [], manifest_id: "production", manifest_version: "v1", methodology_version: "v1", timing_release_id: "timing", timing_release_version: "v1", limitation: false };
    const choices = [
      { label: "The reviewed indication about your 10th lord's placement", question: "Explain the reviewed indication about your 10th lord's placement", claim_ids: [link.claim_id] },
      { label: "The reviewed timing indication about your 10th lord's Mahadasha", question: "Explain the reviewed timing indication about your 10th lord's Mahadasha", claim_ids: ["career-timing-1"] },
    ];
    const prompt = "Which reviewed indication do you mean: the reviewed indication about your 10th lord's placement or the reviewed timing indication about your 10th lord's Mahadasha?";
    const messages: ConsultationMessage[] = [
      { question: "How will my career be in 2027?", response: { state, analysis: first, reply: null, status: "answered", source_references: [], resolved_claim_ids: [], resolved_evidence_item_ids: [], resolved_timing_references: [] } },
      { question: "Explain this particular claim", response: { state: { ...state, turn_id: "second" }, analysis: null, reply: prompt, status: "clarification", source_references: [], resolved_claim_ids: [], resolved_evidence_item_ids: [], resolved_timing_references: [], choices } },
    ];
    const onAnalyze = vi.fn().mockResolvedValue(true);
    render(<QuestionAnalysis result={first} messages={messages} onAnalyze={onAnalyze} loading={false} error="" />);
    const group = screen.getByLabelText("Choose what to explain", { selector: ".clarification-choices" });
    expect(group).not.toHaveTextContent(link.claim_id);
    expect(group).not.toHaveTextContent("career-timing-1");
    fireEvent.click(screen.getByRole("button", { name: choices[1].label }));
    expect(onAnalyze).toHaveBeenCalledWith(choices[1].question, choices[1].label, { reference_turn_id: "first", claim_ids: ["career-timing-1"] });
  });
});
