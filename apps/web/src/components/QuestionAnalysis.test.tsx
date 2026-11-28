import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { QuestionAnalysis } from "./QuestionAnalysis";
import type { AnalysisResult, ConsultationMessage, ConsultationSection } from "../lib/contracts";

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
    const bullets = ["Periods: Rahu Mahadasha throughout 2027, with Saturn Antardasha.", "Natal: your 10th lord is Sun, in your 7th house; no reviewed natal Career indication matched your chart.", "Timing: no reviewed timing rule applies to 2027."];
    answered.answers[0].consultation_sections = [
      { kind: "direct", text: `For 2027, ${reviewed}` },
      { kind: "glance", text: bullets.join(" "), synthesis_sentences: bullets.map((text) => ({ text, claim_ids: [], fact_ids: ["segment-1"], rule_ids: [], calc_method_ids: [] })) },
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
    expect(sections).toHaveLength(3);
    // NEXT-UX-SUMMARY: the glance sits on top, one bullet per server sentence.
    expect(sections[0]).toHaveClass("year-glance");
    expect(sections[0].querySelector("h4")).toHaveTextContent("2027 at a glance");
    expect([...sections[0].querySelectorAll("li")].map((item) => item.textContent)).toEqual(bullets);
    // No timing rule matched: the Overview only repeats the glance, so it is hidden.
    expect(document.querySelector(".detailed-answer .direct-answer")).toBeNull();
    expect(sections[1]).toHaveTextContent("No reviewed Career timing rule matched 2027");
    expect(sections[2]).toHaveTextContent("does not establish a specific Career outcome");
    // The chronology moved into the collapsed "Chart details" disclosure.
    const chartDetails = document.querySelector(".detailed-answer > details.chart-details");
    expect(chartDetails).not.toHaveAttribute("open");
    expect(chartDetails?.querySelector("summary")).toHaveTextContent("Chart details");
    expect(chartDetails).toHaveTextContent("Rahu Mahadasha, Saturn Antardasha");
    expect(document.querySelector(".detailed-answer")?.textContent).not.toContain(reviewed);
    expect(document.querySelector(".evidence-details")).toHaveTextContent("2027-01-01 00:00 UTC to 2028-01-01 00:00 UTC");
    expect(document.querySelector(".evidence-details")).not.toHaveAttribute("open");
  });

  it("shows a server-supplied Period themes section visibly, after Why, and none otherwise", () => {
    const answered = result("NO_MATCH");
    const theme = "During your Rahu Mahadasha throughout 2028, the reviewed significations associated with Rahu (forces) are the themes the texts associate with this period.";
    answered.answers[0].consultation_sections = [
      { kind: "direct", text: "In 2028 your calculated Vimshottari periods are the Rahu Mahadasha." },
      { kind: "why", text: "No reviewed Career indication applies to 2028." },
      { kind: "period_themes", text: `${theme} This does not predict an event or an outcome.` },
      { kind: "limit", text: "The available reviewed timing evidence does not establish a specific Career outcome for 2028." },
    ];
    const { unmount } = render(<QuestionAnalysis result={answered} onAnalyze={vi.fn()} loading={false} error="" />);
    const sections = [...document.querySelectorAll(".detailed-answer > section")];
    const themes = document.querySelector(".detailed-answer > section.consultation-period_themes");
    expect(themes).not.toBeNull();
    expect(themes?.querySelector("h4")).toHaveTextContent("Period themes");
    expect(themes).toHaveTextContent(theme);
    expect(sections.indexOf(themes!)).toBe(sections.findIndex((section) => section.classList.contains("consultation-why")) + 1);
    unmount();
    answered.answers[0].consultation_sections = answered.answers[0].consultation_sections.filter((section) => section.kind !== "period_themes");
    render(<QuestionAnalysis result={answered} onAnalyze={vi.fn()} loading={false} error="" />);
    expect(document.querySelector(".consultation-period_themes")).toBeNull();
    expect(document.body).not.toHaveTextContent("Period themes");
  });

  it("shows each rule's review type only inside the evidence disclosure", () => {
    const answered = result("NO_MATCH");
    answered.answers[0].consultation_sections = [
      { kind: "direct", text: "In 2028 your calculated Vimshottari periods are the Rahu Mahadasha." },
      { kind: "limit", text: "The available reviewed timing evidence does not establish a specific Career outcome for 2028." },
    ];
    answered.answers[0].rule_review_types = [
      { rule_id: "bphs.d1.house_lord.10.equals_1.v1", review_type: "Independent reviewer (Pandit ji, Acharya)" },
      { rule_id: "bphs.d1.house_lord.10.in_4_or_10.v1", review_type: "Project-owner review (not independently certified)" },
    ];
    const { unmount } = render(<QuestionAnalysis result={answered} onAnalyze={vi.fn()} loading={false} error="" />);
    const disclosure = document.querySelector(".evidence-details .rule-review-types");
    expect(disclosure).not.toBeNull();
    expect(disclosure).toHaveTextContent("bphs.d1.house_lord.10.equals_1.v1: Independent reviewer (Pandit ji, Acharya)");
    expect(disclosure).toHaveTextContent("bphs.d1.house_lord.10.in_4_or_10.v1: Project-owner review (not independently certified)");
    for (const section of document.querySelectorAll(".detailed-answer > section")) {
      expect(section).not.toHaveTextContent("Pandit ji");
      expect(section).not.toHaveTextContent("Project-owner review");
    }
    unmount();
    answered.answers[0].rule_review_types = [];
    render(<QuestionAnalysis result={answered} onAnalyze={vi.fn()} loading={false} error="" />);
    expect(document.querySelector(".rule-review-types")).toBeNull();
  });

  it("keeps the Overview below the glance when a reviewed timing rule matched", () => {
    const answered = result("MATCH");
    const framing = "Your current Jupiter Mahadasha matches a reviewed BPHS timing rule.";
    const bullets = ["Periods: Jupiter Mahadasha throughout 2027, with Saturn Antardasha.", "Timing: the reviewed timing indication for Jupiter Mahadasha applies."];
    answered.answers[0].consultation_sections = [
      { kind: "direct", text: framing },
      { kind: "glance", text: bullets.join(" "), synthesis_sentences: bullets.map((text) => ({ text, claim_ids: [], fact_ids: ["segment-1"], rule_ids: [], calc_method_ids: [] })) },
      { kind: "limit", text: "The available reviewed timing evidence does not establish a specific Career outcome for 2027." },
    ];
    answered.answers[0].career_answer_plan = {
      plan_version: "career-answer-plan-v1", question_intent: answered.routing.intents[0],
      requested_time_scope: { start_date: "2027-01-01", end_date: "2027-12-31" },
      calculated_fact_ids: [], matched_claim_ids: ["timing-1"], timing_evidence_ids: ["bphs.timing.vimshottari.career.10th_lord.in_4.md.v1"],
      timing_references: [], approved_source_locators: [], limitation_ids: [], answerability: "REVIEWED_TIMING_CONTEXT", dasha_segments: [],
    };
    render(<QuestionAnalysis result={answered} onAnalyze={vi.fn()} loading={false} error="" />);
    const sections = document.querySelectorAll(".detailed-answer > section");
    expect(sections[0]).toHaveClass("year-glance");
    expect(sections[1]).toHaveClass("direct-answer");
    expect(sections[1]).toHaveTextContent(framing);
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
    // Visible: Overview, Reviewed timing, conclusion; chronology and lord relationships sit,
    // in order, inside the collapsed "Chart details" disclosure.
    expect(document.querySelectorAll(".detailed-answer > section")).toHaveLength(3);
    const details = document.querySelector(".detailed-answer > details.chart-details");
    expect(details).not.toHaveAttribute("open");
    const inner = details!.querySelectorAll("section");
    expect(inner).toHaveLength(2);
    expect(inner[0]).toHaveClass("consultation-dasha");
    expect(inner[1]).toHaveClass("consultation-section", "consultation-dasha_context");
    expect(inner[1]).toHaveTextContent("Calculated Dasha lord relationships");
    expect(inner[1]).toHaveTextContent(framing);
    expect(inner[1]).not.toHaveTextContent("jyotish.dasha_linkage.v1");
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
  // NEXT-TONE-01: the server carries the framing in `framing` only; the visible text is the lines.
  const why = { kind: "why" as const, text: line, framing, synthesis_links: [link], synthesis_sentences: [{ text: line, claim_ids: [link.claim_id], fact_ids: [...link.claim_fact_ids, ...link.dasha_fact_ids], rule_ids: link.claim_rule_ids, calc_method_ids: link.calc_method_ids }] };
  const natal = { kind: "natal" as const, text: "The available reviewed natal Career context is: Your D1 tenth-house lord is placed in the fourth house." };

  it("renders the why section after the overview and keeps citations in evidence details", () => {
    const answered = result("MATCH");
    answered.answers[0].consultation_sections = [
      { kind: "direct", text: "For 2027, no reviewed Career timing rule matched. The reviewed indication about your 10th lord's placement concerns your 10th lord, Jupiter, and Jupiter is the Mahadasha lord throughout 2027." },
      why,
      natal,
      { kind: "dasha", text: "Calculated Vimshottari periods in 2027 (local dates): Jupiter Mahadasha, Moon Antardasha." },
      { kind: "limit", text: "These are reviewed indications and calculated periods for 2027, not a prediction of specific events." },
    ];
    answered.answers[0].answer = answered.answers[0].consultation_sections.map((section) => section.text).join(" ");
    render(<QuestionAnalysis result={answered} onAnalyze={vi.fn()} loading={false} error="" />);
    const sections = document.querySelectorAll(".detailed-answer > section");
    expect(sections[1]).toHaveClass("consultation-section", "consultation-why");
    expect(sections[1]).toHaveTextContent("Why: shared references with the Dasha periods");
    expect(sections[1]).toHaveTextContent(line);
    expect(sections[1]).not.toHaveTextContent(framing);
    expect(sections[1]).not.toHaveTextContent("jyotish.dasha_linkage.v1.lord.jupiter.is_tenth_lord");
    const evidence = document.querySelector(".evidence-details");
    expect(evidence?.querySelector(".synthesis-framing")).toHaveTextContent(framing);
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
    expect(details?.querySelector(".synthesis-framing")).toHaveTextContent(framing);
    expect(screen.getByText(reply)).not.toHaveTextContent(framing);
    expect(details).toHaveTextContent("jyotish.dasha_linkage.v1.lord.jupiter.ruled_houses");
  });

  it("renders a bare-comparison domain choice on a fresh conversation and sends it without a reference", () => {
    const state = { consultation_id: "fresh", turn_id: "clarify", domain: null, intent: null, claim_ids: [], evidence_item_ids: [], timing_references: [], manifest_id: "production", manifest_version: "v1", methodology_version: "v1", timing_release_id: "timing", timing_release_version: "v1", limitation: true };
    const choices = [{ label: "Career", question: "Compare 2027 and 2028 for my career", claim_ids: [] }];
    const messages: ConsultationMessage[] = [
      { question: "Which is better, 2027 or 2028?", response: { state, analysis: null, reply: "Which area should I compare 2027 and 2028 for?", status: "clarification", source_references: [], resolved_claim_ids: [], resolved_evidence_item_ids: [], resolved_timing_references: [], choices } },
    ];
    const onAnalyze = vi.fn().mockResolvedValue(true);
    render(<QuestionAnalysis result={null} messages={messages} onAnalyze={onAnalyze} loading={false} error="" />);
    expect(screen.getByText("Which area should I compare 2027 and 2028 for?")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Career" }));
    expect(onAnalyze).toHaveBeenCalledWith("Compare 2027 and 2028 for my career", "Career", undefined);
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

const provisionalItem = {
  rule_id: "provisional.bphs.d1.house_lord.5.equals_7.spirituality.v1", rule_version: "v1", tier: "provisional" as const,
  badge: "Provisional · low confidence" as const, domain: "spirituality",
  placement_explanation: "Your D1 fifth-house lord is placed in the seventh house.",
  statement: "With the D1 fifth-house lord in the seventh house, the text associates the placement with adherence to every dharma.",
  fact_ids: ["jyotish.d1.house_lord.5.placement_house"], corpus_release: "jyotish.provisional@v1",
  justification: {
    source_work: "Brihat Parashara Hora Shastra (selected edition)", locator: "Sutesha-phala, verse 40; PDF p. 188",
    original_text: "सुतेशे कामगे मानी सर्वधर्मसमन्वितः ।", draft_translation: "When the lord of the fifth is in the seventh…",
    interpretive_reasoning: "Devotional qualities, so Spirituality.", conventions: ["Houses counted from the D1 Lagna."],
    confidence: "low" as const, author: "drafted_by: AI agent; adopted_by: project owner (pending)" as const, status: "provisional" as const, transcription_notes: "Kept as printed.",
  },
};

function provisionalResult(): AnalysisResult {
  return {
    context: {} as AnalysisResult["context"],
    routing: { status: "routable", intents: [{ intent_id: "intent-1", domain: "spirituality", shape: "descriptive", temporal_intent: "timeless", requires_timing: false }], issues: [] },
    selections: [],
    answers: [{ ...baseAnswer, answer: "Your D1 chart contains reviewed contextual evidence relevant to Spirituality.", reviewed_interpretations: ["Reviewed spirituality wording."], provisional_interpretations: [provisionalItem] }],
  };
}

describe("QuestionAnalysis provisional tier (NEXT-PROVISIONAL-01)", () => {
  it("offers the beta toggle, off by default, and reports changes", () => {
    const onChange = vi.fn();
    render(<QuestionAnalysis result={null} onAnalyze={vi.fn()} loading={false} error="" onShowProvisionalChange={onChange} />);
    const toggle = screen.getByRole("switch", { name: "Show provisional interpretations (beta)" });
    expect(toggle).not.toBeChecked();
    fireEvent.click(toggle);
    expect(onChange).toHaveBeenCalledWith(true);
  });

  it("renders provisional content with its badge, apart from the reviewed answer, and the full justification in the evidence", () => {
    render(<QuestionAnalysis result={provisionalResult()} onAnalyze={vi.fn()} loading={false} error="" showProvisional onShowProvisionalChange={vi.fn()} />);
    const section = screen.getByRole("region", { name: "Provisional interpretations" });
    expect(section).toHaveTextContent("Provisional · low confidence");
    expect(section).toHaveTextContent(provisionalItem.statement);
    expect(section).toHaveTextContent("These have not been through expert review yet.");
    expect(screen.getByText("Reviewed spirituality wording.").closest(".provisional-interpretations")).toBeNull();
    const disclosure = document.querySelector(".evidence-details .provisional-justifications");
    expect(disclosure).not.toBeNull();
    for (const text of [provisionalItem.justification.original_text, provisionalItem.justification.draft_translation, provisionalItem.justification.interpretive_reasoning, provisionalItem.justification.locator, "drafted_by: AI agent; adopted_by: project owner (pending)", "Houses counted from the D1 Lagna.", "Low (author's own)", "Kept as printed."]) {
      expect(disclosure).toHaveTextContent(text);
    }
    expect(disclosure?.querySelector(".provisional-badge")).toHaveTextContent("Provisional · low confidence");
    expect(section.textContent).not.toMatch(/\breviewed\b/i);
  });

  it("hides provisional content while the toggle is off, even if the response carries it", () => {
    render(<QuestionAnalysis result={provisionalResult()} onAnalyze={vi.fn()} loading={false} error="" showProvisional={false} onShowProvisionalChange={vi.fn()} />);
    expect(screen.queryByRole("region", { name: "Provisional interpretations" })).toBeNull();
    expect(document.querySelector(".provisional-justifications")).toBeNull();
    expect(screen.queryByText("Provisional · low confidence")).toBeNull();
  });
});

// NEXT-MARRIAGE-01: a marriage timing answer (texts from benchmark v23 journey M04, synthetic).
const marriageSection = (kind: ConsultationSection["kind"], lines: string[]): ConsultationSection => ({
  kind, text: lines.join(" "), fact_sentences: [], framing: null, interpretation_rule_ids: [], synthesis_links: [],
  synthesis_sentences: lines.map((text) => ({ text, claim_ids: [], fact_ids: [], rule_ids: [], calc_method_ids: [] })),
});
const heldItem = {
  ...provisionalItem,
  rule_id: "provisional.bphs.d1.house_lord.7.equals_9.marriage.v1", badge: "Provisional · high confidence" as const, domain: "marriage",
  placement_explanation: "Your D1 seventh-house lord is placed in the ninth house.",
  statement: "A provisional source verse exists for this placement; its wording is held for the expert review.",
  wording_held: true,
  justification: { ...provisionalItem.justification, confidence: "high" as const, draft_translation: null, held_reason: "The verse's marriage clause is a judgement about a person's conduct or fidelity." },
};

function marriageResult(): AnalysisResult {
  return {
    context: {} as AnalysisResult["context"],
    routing: { status: "routable", intents: [{ intent_id: "intent-1", domain: "marriage", shape: "timing", temporal_intent: "time_bound", requires_timing: true }], issues: [] },
    selections: [],
    answers: [{
      ...baseAnswer,
      answer: "No reviewed timing rule exists for marriage, so JyotAI gives no date for a marriage.",
      corpus_limitation: true,
      consultation_sections: [
        marriageSection("direct", ["No reviewed timing rule exists for marriage, so JyotAI gives no date for a marriage. In 2038, the Mahadasha and Antardasha periods of your 7th lord, Mercury, and of Venus are listed below with their reviewed Period themes."]),
        marriageSection("periods", ["Venus Antardasha in the Saturn Mahadasha: 6 Jan 2038 to 8 Mar 2041."]),
        marriageSection("period_themes", ["Venus Antardasha (secondary): reviewed themes — Venus: adviser or counsellor.", "These are the reviewed themes associated with this period; actual results depend on the full chart and other active factors."]),
        marriageSection("chart_factors", ["Your 7th lord is Mercury, placed in the 9th house.", "Calculated fact (sign dignity, shown as a modifier only): Venus is in none of its own, exaltation or debilitation signs."]),
        marriageSection("timing_status", ["Timing rules for marriage: none reviewed yet."]),
        marriageSection("dasha", ["Running: Saturn Mahadasha / Ketu Antardasha: 28 Nov 2036 to 6 Jan 2038."]),
        marriageSection("limit", ["These are calculated periods and reviewed themes; they do not predict whether or when a marriage will happen."]),
      ],
      provisional_interpretations: [heldItem],
    }],
  };
}

describe("QuestionAnalysis marriage answers (NEXT-MARRIAGE-01)", () => {
  it("renders the marriage sections in the consultation layout, one line per calculated fact", () => {
    render(<QuestionAnalysis result={marriageResult()} onAnalyze={vi.fn()} loading={false} error="" showProvisional={false} onShowProvisionalChange={vi.fn()} />);
    expect(screen.getByRole("heading", { name: "Overview" }).parentElement).toHaveTextContent("JyotAI gives no date for a marriage");
    const periods = screen.getByRole("heading", { name: "Periods of your 7th lord and Venus" }).parentElement!;
    expect(within(periods).getAllByRole("listitem").map((item) => item.textContent)).toEqual(["Venus Antardasha in the Saturn Mahadasha: 6 Jan 2038 to 8 Mar 2041."]);
    expect(within(screen.getByRole("heading", { name: "Calculated marriage factors" }).parentElement!).getAllByRole("listitem")).toHaveLength(2);
    expect(screen.getByRole("heading", { name: "Timing status" }).parentElement).toHaveTextContent("none reviewed yet");
    expect(screen.getByRole("heading", { name: "Period themes" })).toBeInTheDocument();
    // The running periods sit in the collapsed Chart details, as in Career answers.
    expect(screen.getByText("Chart details").closest("details")).toHaveTextContent("Running: Saturn Mahadasha / Ketu Antardasha");
    expect(screen.queryByRole("region", { name: "Provisional interpretations" })).toBeNull();
  });

  it("shows a held provisional rule only with the toggle on, without its draft translation", () => {
    render(<QuestionAnalysis result={marriageResult()} onAnalyze={vi.fn()} loading={false} error="" showProvisional onShowProvisionalChange={vi.fn()} />);
    const section = screen.getByRole("region", { name: "Provisional interpretations" });
    expect(section).toHaveTextContent("Provisional · high confidence");
    expect(section).toHaveTextContent(heldItem.statement);
    const disclosure = document.querySelector(".evidence-details .provisional-justifications");
    expect(disclosure).toHaveTextContent("Held with the wording until the expert review");
    expect(disclosure).toHaveTextContent("Why the wording is held");
    expect(disclosure).toHaveTextContent(heldItem.justification.held_reason);
  });
});

// NEXT-MARRIAGE-02: tagged significations (periods only + pending line), D9 facts, provisional terms.
const significationItem = {
  ...provisionalItem,
  rule_id: "provisional.signification.bhava.7.jaya", badge: "Provisional · high confidence" as const, domain: "marriage", kind: "signification" as const,
  placement_explanation: "Provisional signification: your D1 7th house, Aries, whose lord is Mars.",
  statement: "The text lists the spouse (जाया) among the matters judged from the 7th house.",
  justification: { ...provisionalItem.justification, confidence: "high" as const, draft_translation: null, held_reason: "The verse's other clauses include death, which is not a marriage term." },
};

function marriage02Result(): AnalysisResult {
  const result = marriageResult();
  const [answer] = result.answers;
  return {
    ...result,
    answers: [{
      ...answer,
      consultation_sections: [
        marriageSection("direct", ["No reviewed timing rule exists for marriage, so JyotAI gives no date for a marriage. In 2038, the Mahadasha and Antardasha periods of your 7th lord, Mercury, and of Venus are listed below."]),
        marriageSection("periods", ["Venus Antardasha in the Saturn Mahadasha: 6 Jan 2038 to 8 Mar 2041."]),
        marriageSection("period_themes", ["Venus Antardasha (secondary).", "Reviewed marriage meanings for these periods are pending expert review."]),
        marriageSection("d9_factors", ["Your D9 Lagna is Aries.", "Your D9 7th house is Libra; its lord is Venus.", "Venus, your D9 7th lord, is in Sagittarius, in the 9th house of your D9 chart.", "These are calculated D9 (Navamsa) positions; no reviewed interpretation of the D9 chart for marriage exists yet, so JyotAI reads no meaning into them."]),
        marriageSection("limit", ["These are calculated periods; they do not predict whether or when a marriage will happen."]),
      ],
      provisional_interpretations: [heldItem, significationItem],
    }],
  };
}

describe("QuestionAnalysis marriage answers (NEXT-MARRIAGE-02)", () => {
  it("renders the D9 factors one per line and Period themes without Career terms", () => {
    render(<QuestionAnalysis result={marriage02Result()} onAnalyze={vi.fn()} loading={false} error="" showProvisional={false} onShowProvisionalChange={vi.fn()} />);
    const d9 = screen.getByRole("heading", { name: "Calculated D9 (Navamsa) factors" }).parentElement!;
    expect(within(d9).getAllByRole("listitem")).toHaveLength(4);
    const themes = screen.getByRole("heading", { name: "Period themes" }).parentElement!;
    expect(themes).toHaveTextContent("Reviewed marriage meanings for these periods are pending expert review.");
    expect(themes).not.toHaveTextContent("adviser or counsellor");
    expect(screen.queryByText(significationItem.statement)).toBeNull();
  });

  it("shows provisional signification terms only with the toggle on", () => {
    render(<QuestionAnalysis result={marriage02Result()} onAnalyze={vi.fn()} loading={false} error="" showProvisional onShowProvisionalChange={vi.fn()} />);
    const section = screen.getByRole("region", { name: "Provisional interpretations" });
    expect(section).toHaveTextContent(significationItem.statement);
    expect(section).toHaveTextContent(significationItem.placement_explanation);
    const disclosure = document.querySelector(".evidence-details .provisional-justifications");
    expect(disclosure).toHaveTextContent("Why the translation is not shown");
  });
});

// NEXT-WEALTH-01: a wealth timing answer (texts from benchmark v25 journey W02, synthetic).
const wealthRuleItem = {
  ...provisionalItem,
  rule_id: "provisional.bphs.d1.house_lord.2.equals_5.wealth.v1", badge: "Provisional · high confidence" as const, domain: "wealth",
  placement_explanation: "Your D1 second-house lord is placed in the fifth house.",
  statement: "With the D1 second-house lord in the fifth house, the text describes wealth through a son (पुत्रतो धनवान्).",
  justification: { ...provisionalItem.justification, confidence: "high" as const, draft_translation: null, held_reason: "The verse's other clauses (miserliness, sorrow, fame, sons) are not wealth themes; only the wealth clause is shown, and the full translation is kept for the expert review." },
};

function wealthResult(): AnalysisResult {
  return {
    context: {} as AnalysisResult["context"],
    routing: { status: "routable", intents: [{ intent_id: "intent-1", domain: "wealth", shape: "timing", temporal_intent: "future_general", requires_timing: true }], issues: [] },
    selections: [],
    answers: [{
      ...baseAnswer,
      answer: "No reviewed timing rule exists for wealth, so JyotAI gives no date or period for wealth.",
      corpus_limitation: true,
      consultation_sections: [
        marriageSection("direct", ["No reviewed timing rule exists for wealth, so JyotAI gives no date or period for wealth. In the next 20 years (1 Jan 2026 to 1 Jan 2046), the Mahadasha and Antardasha periods of your 2nd lord, Mars, of your 11th lord, Saturn, and of Jupiter are listed below."]),
        marriageSection("periods", ["Jupiter Mahadasha: 18 Mar 2015 to 18 Mar 2031.", "Saturn (your 11th lord) Mahadasha: 18 Mar 2031 to 17 Mar 2050 (continues past the window)."]),
        marriageSection("period_themes", ["Jupiter Mahadasha.", "Saturn (your 11th lord) Mahadasha.", "Reviewed wealth meanings for these periods are pending expert review."]),
        marriageSection("chart_factors", ["Your 2nd lord is Mars, placed in the 5th house.", "Calculated fact (sign dignity): your 2nd lord, Mars, is in its debilitation sign.", "Jupiter is placed in the 4th house."]),
        marriageSection("timing_status", ["Timing rules for wealth: none reviewed yet. The periods above are calculated facts and are not read as a time of financial gain."]),
        marriageSection("limit", ["Nothing here predicts income, an amount of money or a financial outcome."]),
      ],
      provisional_interpretations: [wealthRuleItem],
    }],
  };
}

describe("QuestionAnalysis wealth answers (NEXT-WEALTH-01)", () => {
  it("uses the wealth headings for the shared section kinds and marks periods past the window", () => {
    render(<QuestionAnalysis result={wealthResult()} onAnalyze={vi.fn()} loading={false} error="" showProvisional={false} onShowProvisionalChange={vi.fn()} />);
    const periods = screen.getByRole("heading", { name: "Periods of your 2nd lord, 11th lord and Jupiter" }).parentElement!;
    expect(within(periods).getAllByRole("listitem")[1]).toHaveTextContent("(continues past the window)");
    expect(within(screen.getByRole("heading", { name: "Calculated wealth factors" }).parentElement!).getAllByRole("listitem")).toHaveLength(3);
    expect(screen.queryByRole("heading", { name: "Calculated marriage factors" })).toBeNull();
    expect(screen.queryByRole("heading", { name: "Periods of your 7th lord and Venus" })).toBeNull();
    expect(screen.getByRole("heading", { name: "Period themes" }).parentElement).toHaveTextContent("Reviewed wealth meanings for these periods are pending expert review.");
    expect(screen.queryByText(wealthRuleItem.statement)).toBeNull();
  });

  it("shows a provisional Wealth rule only with the toggle on, without its translation", () => {
    render(<QuestionAnalysis result={wealthResult()} onAnalyze={vi.fn()} loading={false} error="" showProvisional onShowProvisionalChange={vi.fn()} />);
    const section = screen.getByRole("region", { name: "Provisional interpretations" });
    expect(section).toHaveTextContent(wealthRuleItem.statement);
    expect(section).toHaveTextContent("Provisional · high confidence");
    const disclosure = document.querySelector(".evidence-details .provisional-justifications");
    expect(disclosure).toHaveTextContent("Why the translation is not shown");
    expect(disclosure).not.toHaveTextContent("Why the wording is held");
    expect(disclosure).toHaveTextContent(wealthRuleItem.justification.held_reason);
  });
});

// NEXT-CHILDREN-GUARD-01: the server holds a source verse with a child-sex or childlessness
// clause (texts from benchmark v27 journey W01, synthetic); the notice is shown in its place.
const SOURCE_HELD_NOTICE = "The source verse is held for expert review; the full verse is in the final review pack.";
const heldVerseItem = {
  ...wealthRuleItem,
  rule_version: "v2",
  statement: "With the D1 second-house lord in the fifth house, the text describes wealth through children (the text says 'son'): पुत्रतो धनवान्.",
  justification: { ...wealthRuleItem.justification, original_text: SOURCE_HELD_NOTICE, original_text_held: true },
};

describe("QuestionAnalysis held source verse (NEXT-CHILDREN-GUARD-01)", () => {
  it("shows the held notice in place of the source verse, as English text", () => {
    const result = wealthResult();
    result.answers[0] = { ...result.answers[0], provisional_interpretations: [heldVerseItem] };
    render(<QuestionAnalysis result={result} onAnalyze={vi.fn()} loading={false} error="" showProvisional onShowProvisionalChange={vi.fn()} />);
    const disclosure = document.querySelector(".evidence-details .provisional-justifications")!;
    expect(disclosure).toHaveTextContent(SOURCE_HELD_NOTICE);
    const original = within(disclosure as HTMLElement).getByText(SOURCE_HELD_NOTICE);
    expect(original.tagName).toBe("DD");
    expect(original).not.toHaveAttribute("lang");
    expect(disclosure).not.toHaveTextContent("पुत्रवान्");
    expect(screen.getByRole("region", { name: "Provisional interpretations" })).toHaveTextContent(heldVerseItem.statement);
  });

  it("keeps a verse that is not held in Sanskrit", () => {
    render(<QuestionAnalysis result={wealthResult()} onAnalyze={vi.fn()} loading={false} error="" showProvisional onShowProvisionalChange={vi.fn()} />);
    const disclosure = document.querySelector(".evidence-details .provisional-justifications")!;
    expect(within(disclosure as HTMLElement).getByText(wealthRuleItem.justification.original_text)).toHaveAttribute("lang", "sa");
    expect(disclosure).not.toHaveTextContent(SOURCE_HELD_NOTICE);
  });
});

// NEXT-PROPERTY-01: a property timing answer (texts from benchmark v26 journey P02, synthetic).
function propertyResult(): AnalysisResult {
  return {
    context: {} as AnalysisResult["context"],
    routing: { status: "routable", intents: [{ intent_id: "intent-1", domain: "property", shape: "timing", temporal_intent: "time_bound", requires_timing: true }], issues: [] },
    selections: [],
    answers: [{
      ...baseAnswer,
      answer: "No reviewed timing rule exists for property, so JyotAI gives no date or period for property.",
      corpus_limitation: true,
      consultation_sections: [
        marriageSection("direct", ["No reviewed timing rule exists for property, so JyotAI gives no date or period for property."]),
        marriageSection("periods", ["Jupiter Mahadasha: 18 Mar 2015 to 18 Mar 2031.", "Mars Antardasha in the Jupiter Mahadasha: 16 Nov 2027 to 22 Oct 2028."]),
        marriageSection("period_themes", ["Jupiter Mahadasha (primary).", "Mars Antardasha (secondary).", "Reviewed property meanings for these periods are pending expert review."]),
        marriageSection("chart_factors", ["Your 4th lord is Mercury, placed in the 9th house.", "Mars is placed in the 5th house."]),
        marriageSection("timing_status", ["Timing rules for property: none reviewed yet."]),
        marriageSection("limit", ["These are calculated periods and chart facts; they do not predict a purchase, a sale, a price or a legal outcome."]),
      ],
    }],
  };
}

describe("QuestionAnalysis property answers (NEXT-PROPERTY-01)", () => {
  it("uses the property headings for the shared section kinds", () => {
    render(<QuestionAnalysis result={propertyResult()} onAnalyze={vi.fn()} loading={false} error="" showProvisional={false} onShowProvisionalChange={vi.fn()} />);
    const periods = screen.getByRole("heading", { name: "Periods of your 4th lord, Mars, Jupiter and Venus" }).parentElement!;
    expect(within(periods).getAllByRole("listitem")).toHaveLength(2);
    expect(within(screen.getByRole("heading", { name: "Calculated property factors" }).parentElement!).getAllByRole("listitem")).toHaveLength(2);
    expect(screen.queryByRole("heading", { name: "Calculated wealth factors" })).toBeNull();
    expect(screen.getByRole("heading", { name: "Period themes" }).parentElement).toHaveTextContent("Jupiter Mahadasha (primary).");
  });
});

// NEXT-CHILDREN-01: a children timing answer (texts from benchmark v28 journey D08, synthetic).
function childrenResult(): AnalysisResult {
  return {
    context: {} as AnalysisResult["context"],
    routing: { status: "routable", intents: [{ intent_id: "intent-1", domain: "children", shape: "timing", temporal_intent: "time_bound", requires_timing: true }], issues: [] },
    selections: [],
    answers: [{
      ...baseAnswer,
      answer: "No reviewed timing rule exists for children, so JyotAI gives no date or period for children.",
      corpus_limitation: false,
      consultation_sections: [
        marriageSection("direct", ["No reviewed timing rule exists for children, so JyotAI gives no date or period for children."]),
        marriageSection("periods", ["Moon (your 5th lord) Antardasha in the Mercury Mahadasha: 21 Aug 2026 to 20 Jan 2028.", "Jupiter Antardasha in the Mercury Mahadasha: 6 Aug 2031 to 11 Nov 2033."]),
        marriageSection("period_themes", ["Moon (your 5th lord) Antardasha (secondary).", "Jupiter Antardasha (secondary).", "Reviewed children meanings for these periods are pending expert review."]),
        marriageSection("chart_factors", ["Your 5th lord is Moon, placed in the 11th house.", "Jupiter is placed in the 9th house."]),
        marriageSection("timing_status", ["Timing rules for children: none reviewed yet."]),
        marriageSection("limit", ["These are calculated periods and chart facts; they do not predict whether or when children will come, how many, or any medical matter."]),
      ],
    }],
  };
}

describe("QuestionAnalysis children answers (NEXT-CHILDREN-01)", () => {
  it("uses the children headings, never the marriage ones", () => {
    render(<QuestionAnalysis result={childrenResult()} onAnalyze={vi.fn()} loading={false} error="" showProvisional={false} onShowProvisionalChange={vi.fn()} />);
    const periods = screen.getByRole("heading", { name: "Periods of your 5th lord and Jupiter" }).parentElement!;
    expect(within(periods).getAllByRole("listitem")).toHaveLength(2);
    expect(within(screen.getByRole("heading", { name: "Calculated children factors" }).parentElement!).getAllByRole("listitem")).toHaveLength(2);
    expect(screen.queryByRole("heading", { name: "Calculated marriage factors" })).toBeNull();
    expect(screen.queryByRole("heading", { name: "Periods of your 7th lord and Venus" })).toBeNull();
  });
});
