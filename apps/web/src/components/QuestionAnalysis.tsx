import { useState } from "react";

import "./QuestionAnalysis.css";
import type { AnalysisResult, CareerTimingContext, ConsultationMessage, DetailedComposedAnswer, Intent, Selection } from "../lib/contracts";
import { titleCase } from "../lib/format";

const prompts = ["Career", "Wealth", "Education", "Business", "Children", "Spirituality", "Travel", "Friends"];
const timingSentence = "Timing is not established by the current governed evidence.";
const unsupportedDomains = new Set(["property", "marriage", "health"]);

export function QuestionAnalysis({ result, messages, onNewConsultation, onAnalyze, loading, error }: { result: AnalysisResult | null; messages?: ConsultationMessage[]; onNewConsultation?: () => void; onAnalyze: (question: string) => Promise<boolean | void>; loading: boolean; error: string }) {
  const [question, setQuestion] = useState("");
  async function submit(event: React.FormEvent<HTMLFormElement>) { event.preventDefault(); if (question.trim()) { const accepted = await onAnalyze(question.trim()); if (accepted !== false) setQuestion(""); } }
  const last = messages?.slice().reverse().find((message) => Boolean(message.response.analysis));
  const suggestions = last ? followUps(last) : [];
  return <section className="question-section" id="ask-jyotishai" aria-labelledby="ask-heading"><div className="question-copy"><span className="eyebrow">Ask JyotishAI</span><h2 id="ask-heading">A question, answered with evidence.</h2><p>Ask about areas covered by the reviewed corpus. Answers keep chart facts, reviewed interpretation, and timing evidence distinct.</p><p className="capability-note"><strong>Current coverage</strong> Career, wealth, education, business, children, spirituality, travel, and friends. Career timing is available only when governed timing evidence supports it. Property, marriage, and health have no approved production rules.</p>{!messages?.length && <div className="prompt-chips" aria-label="Question prompts">{prompts.map((prompt) => <button type="button" key={prompt} onClick={() => setQuestion(`What does my chart say about ${prompt.toLowerCase()}?`)}>{prompt}</button>)}<button type="button" onClick={() => setQuestion("When is a career-related period indicated?")}>Career timing</button></div>}</div>{messages && messages.length > 0 && <div className="consultation-thread" role="log" aria-label="Consultation conversation" aria-live="polite"><div className="consultation-toolbar"><strong>Consultation</strong>{onNewConsultation && <button type="button" onClick={onNewConsultation} disabled={loading}>Start a new consultation</button>}</div>{messages.map((message) => <article className="consultation-turn" key={message.response.state.turn_id}><h3>You asked</h3><p className="consultation-question">{message.question}</p>{message.response.analysis ? <AnalysisPanels result={message.response.analysis} /> : <div className={`consultation-reply ${message.response.status}`}><h3>{message.response.status === "clarification" ? "Clarification needed" : "JyotishAI answer"}</h3><p>{message.response.reply}</p>{message.response.source_references.length > 0 && <p className="career-evidence-refs"><strong>Approved sources:</strong> {message.response.source_references.join("; ")}</p>}</div>}</article>)}</div>}<form className="question-form" onSubmit={submit} aria-busy={loading}><label htmlFor="question">{messages?.length ? "Ask a follow-up" : "Your astrology question"}</label><textarea id="question" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder={messages?.length ? "For example, why did you say that?" : "For example, what does my chart say about career?"} rows={6} />{suggestions.length > 0 && <div className="prompt-chips" aria-label="Suggested follow-ups">{suggestions.map((suggestion) => <button type="button" key={suggestion} onClick={() => setQuestion(suggestion)}>{suggestion}</button>)}</div>}<div className="question-form-footer"><span>{messages?.length ? "Ask about the displayed answer, or start a new consultation for another topic." : "Choose a topic above or write your own question."}</span><button className="button primary" disabled={loading || !question.trim()}>{loading ? "Reviewing evidence…" : "Ask JyotishAI"}</button></div>{loading && <p className="section-status" role="status">Reviewing the available chart evidence…</p>}{error && <div className="question-error" role="alert"><strong>We couldn’t answer that question right now.</strong><span>{error}</span></div>}</form>{!messages && result && <AnalysisPanels result={result} />}</section>;
}

function followUps(message: ConsultationMessage): string[] {
  const analysis = message.response.analysis;
  if (!analysis || analysis.routing.status !== "routable" || analysis.answers.length !== 1) return [];
  const answer = analysis.answers[0];
  const claims = answer.claim_ledger?.claims ?? [];
  const suggestions: string[] = [];
  if (claims.filter((claim) => claim.kind === "APPROVED_INTERPRETATION").length === 1) suggestions.push("Which planetary placement supports this?");
  if (analysis.routing.intents[0]?.domain === "career" && analysis.routing.intents[0]?.time_range) suggestions.push("Which Dasha applies?");
  const approved = claims.filter((claim) => claim.kind === "APPROVED_INTERPRETATION" || claim.kind === "APPROVED_TIMING_INTERPRETATION");
  if (approved.length === 1) suggestions.push("Why did you say that?");
  if (approved.length === 1 && answer.timing && (answer.timing.status === "NO_MATCH" || answer.timing.status === "UNKNOWN")) suggestions.push("Why no reviewed Career timing rule matched?");
  if (approved.length > 1) suggestions.push(...approved.map((claim) => `Explain claim ${claim.claim_id}`));
  if (claims.length > 0) suggestions.push("What does this interpretation NOT establish?");
  const range = analysis.routing.intents[0]?.time_range;
  if (range && range.start_date.slice(0, 4) === range.end_date.slice(0, 4) && analysis.routing.intents[0]?.domain === "career") suggestions.push(`What about ${Number(range.start_date.slice(0, 4)) + 1}?`);
  return suggestions;
}

function AnalysisPanels({ result }: { result: AnalysisResult }) {
  if (result.routing.status !== "routable") return <article className="notice warning"><strong>{result.routing.status === "unsupported" ? "This question is not supported yet." : "A clarification is needed."}</strong><span>{result.routing.issues.map(titleCase).join(" · ") || "Please ask a supported domain question."}</span></article>;
  return <div className="analysis-results"><QuestionUnderstanding intents={result.routing.intents} /><DetailedAnswers answers={result.answers ?? []} selections={result.selections} /></div>;
}

function QuestionUnderstanding({ intents }: { intents: Intent[] }) {
  return <section className="understanding"><span className="eyebrow">Question understanding</span><h3>How JyotishAI understood your question</h3><p>Your question is organized into separate supported domains before evidence is selected.</p><details><summary>View routing details</summary><div className="intent-grid">{intents.map((intent) => <article className="intent-card" key={intent.intent_id}><strong>{titleCase(intent.domain)} question</strong><dl><dt>Question shape</dt><dd>{titleCase(intent.shape)}</dd><dt>Requires timing</dt><dd>{intent.requires_timing ? "Yes" : "No"}</dd></dl></article>)}</div></details></section>;
}

function DetailedAnswers({ answers, selections }: { answers: DetailedComposedAnswer[]; selections: Selection[] }) {
  return <section className="detailed-answers" aria-live="polite"><span className="eyebrow">JyotishAI answer</span><h3>Governed interpretation</h3>{answers.length ? answers.map((answer, index) => <DetailedAnswer key={`${answer.interpretation_contract_sha256}-${index}`} answer={answer} selection={selections[index]} />) : <p className="section-status">No answer was supplied for this question.</p>}</section>;
}

function DetailedAnswer({ answer, selection }: { answer: DetailedComposedAnswer; selection: Selection | undefined }) {
  const hasTiming = answer.answer.endsWith(timingSentence);
  const directAnswer = hasTiming ? answer.answer.slice(0, -timingSentence.length).trim() : answer.answer;
  const details = answer.evidence ?? [];
  const narrative = answer.narrative;
  const ledger = answer.claim_ledger;
  const timingFocus = ledger?.requested_question_shape === "period" || ledger?.requested_question_shape === "promotion";
  const supportedClaims = ledger?.claims.filter((claim) => timingFocus ? claim.kind === "APPROVED_TIMING_INTERPRETATION" : claim.kind === "APPROVED_INTERPRETATION") ?? [];
  const placement = ledger?.claims.find((claim) => claim.kind === "CALCULATED_FACT")?.permitted_wording;
  const natalInterpretations = ledger?.claims.filter((claim) => claim.kind === "APPROVED_INTERPRETATION").map((claim) => claim.permitted_wording) ?? [];
  const primaryAnswer = ledger ? natalInterpretations.reduce((value, wording) => value.replace(wording, ""), placement ? answer.answer.replace(placement, "") : answer.answer).trim() : directAnswer;
  const unsupported = selection && unsupportedDomains.has(selection.question_intent.domain);
  const state = !selection || (!selection.selected_matched.length && !selection.relevant_unknown.length && !selection.relevant_unmatched.length) ? "No approved rule" : selection.selected_matched.length ? "MATCH · reviewed evidence" : selection.relevant_unknown.length ? "UNKNOWN · could not evaluate" : "NO_MATCH/FALSE · rule did not match";
  return <article className="detailed-answer">
    <span className="answer-state">{unsupported ? "No approved rule" : ledger && answer.timing ? `Natal ${state} · Career timing ${answer.timing.status}` : state}</span>
    <section><h4>JyotishAI answer</h4>
      {unsupported ? <p>No reviewed interpretation is currently available for this area from the active governed corpus.</p> : ledger ? <p>{primaryAnswer}</p> : narrative ? <><p>{narrative.summary}</p><p>{narrative.explanation}</p><p>{narrative.question_relevance}</p>{narrative.follow_up && <p>{narrative.follow_up}</p>}</> : <p>{directAnswer}</p>}
      {answer.corpus_limitation && !ledger && <p className="muted">This answer reflects the current limited governed corpus.</p>}
    </section>
    {ledger && placement && <section><h4>Calculated placement</h4><p>{placement}</p></section>}
    {ledger && natalInterpretations.length > 0 && <section><h4>Reviewed interpretation</h4>{natalInterpretations.map((wording) => <p key={wording}>{wording}</p>)}</section>}
    {!unsupported && <>
      {!ledger && (answer.why_it_applies?.length ?? 0) > 0 && <section><h4>Why this applies</h4><ul>{answer.why_it_applies?.map((item) => <li key={item}>{item}</li>)}</ul></section>}
      {!ledger && (answer.reviewed_interpretations?.length ?? 0) > 0 && <section><h4>Reviewed interpretation</h4>{answer.reviewed_interpretations?.map((item) => <p key={item}>{item}</p>)}</section>}
      {!ledger && (answer.limitations?.length ?? 0) > 0 && <section><h4>What this does not establish</h4><ul>{answer.limitations?.map((item) => <li key={item}>{item}</li>)}</ul></section>}
      {answer.timing ? <CareerTiming timing={answer.timing} concise={Boolean(ledger)} /> : hasTiming && <section><h4>Timing</h4><p>{timingSentence}</p></section>}
    </>}
    <details className="evidence-details"><summary>View governed evidence &amp; methodology</summary>
      {ledger ? <div className="claim-list">{supportedClaims.length > 0 && <p><strong>Approved interpretation sources:</strong> {supportedClaims.map((claim) => `${claim.rule_ids[0]} · ${claim.source_reference}`).join("; ")}</p>}{ledger.claims.map((claim) => <article className="evidence-item" key={claim.claim_id}><strong>{claim.kind === "CALCULATED_FACT" ? "Calculated placement fact" : claim.kind === "INSUFFICIENT_EVIDENCE" ? "Nonmatching or unavailable rule diagnostic" : titleCase(claim.kind)} · {claim.evaluation_status}</strong><dl><dt>Claim ID</dt><dd>{claim.claim_id}</dd><dt>{claim.kind === "CALCULATED_FACT" ? "Interpretive rule" : "Rule"}</dt><dd>{claim.kind === "CALCULATED_FACT" ? "Not applicable to a calculated fact" : claim.rule_ids.join(", ") || "—"}</dd><dt>{claim.kind === "CALCULATED_FACT" ? "Linked interpretation evidence ID" : "Evidence ID"}</dt><dd>{claim.evidence_item_ids.join(", ") || "—"}</dd><dt>Fact</dt><dd>{claim.fact_ids.join(", ") || "—"}</dd><dt>{claim.kind === "CALCULATED_FACT" ? "Calculated fact provenance" : "Source / locator"}</dt><dd>{claim.source_reference}</dd><dt>Methodology</dt><dd>{claim.methodology_version} · {claim.calculation_version}</dd>{claim.authorized_precision && <><dt>Precision</dt><dd>{titleCase(claim.authorized_precision)}</dd></>}{claim.timing_reference && <><dt>Timing interval</dt><dd>{claim.timing_reference}</dd></>}{claim.missing_evidence.length > 0 && <><dt>Missing</dt><dd>{claim.missing_evidence.join(", ")}</dd></>}</dl></article>)}</div> : !unsupported && details.length ? details.map((item, index) => <article className="evidence-item" key={`${item.source_section}-${index}`}><strong>{item.placement_explanation}</strong><span>{item.question_framing}</span><dl><dt>Source work</dt><dd>{item.source_work}</dd><dt>Source section</dt><dd>{item.source_section}</dd>{item.source_reference && <><dt>Reference</dt><dd>{item.source_reference}</dd></>}<dt>Chart scope</dt><dd>{item.chart_scope} · {item.posture}</dd></dl></article>) : <CorpusDetails selection={selection} />}
      {selection && <p className="evidence-state-line">{selection.selected_matched.length} MATCH · {selection.relevant_unmatched.length} NO_MATCH/FALSE · {selection.relevant_unknown.length} UNKNOWN</p>}
    </details>
  </article>;
}

function CareerTiming({ timing, concise = false }: { timing: CareerTimingContext; concise?: boolean }) {
  return <section className="career-timing"><div className="timing-heading"><h4>Career Timing Context</h4><span className="timing-status">{timing.status}{timing.partially_supported ? " · partially supported range" : ""}</span></div>
    <p>{timing.message}</p>
    {timing.scope === "requested_range" && timing.requested_start_date && timing.requested_end_date && <p>Requested calendar dates: {timing.requested_start_date} through {timing.requested_end_date} (inclusive{timing.calendar_timezone_offset ? `, UTC${timing.calendar_timezone_offset.slice(0, 3)}:${timing.calendar_timezone_offset.slice(3)}` : ""}).</p>}
    {timing.scope === "default_40_year_horizon" && <p>Scope: default 40-year forward horizon.</p>}
    {timing.scope === "historical_unbounded" && <p>Scope: historical question without a supported forward interval.</p>}
    {timing.evaluated_start && timing.evaluated_end && <p>Evaluated interval: {formatTimingInstant(timing.evaluated_start)} to {formatTimingInstant(timing.evaluated_end)} (end exclusive).</p>}
    {timing.partially_supported && <p>Only the displayed evaluated portion falls within the supported forward horizon.</p>}
    {timing.status === "UNSUPPORTED" && <p>No Career timing evidence was evaluated for this request.</p>}
    {timing.status === "MATCH" && <div className="timing-windows">{timing.windows.map((window) => <article className="timing-window" key={`${window.rule_id}-${window.effective_start}-${window.effective_end}`}><span className={`timing-precision timing-precision-${window.precision.toLowerCase()}`}>{timingPrecisionLabel(window.precision)}</span><p className="timing-dates">Displayed intersection: {formatTimingInstant(window.effective_start)} to {formatTimingInstant(window.effective_end)} (end exclusive).</p>{window.mahadasha_lord && <p>Calculated Mahadasha: {titleCase(window.mahadasha_lord)}{window.antardasha_lord ? ` · Antardasha: ${titleCase(window.antardasha_lord)}` : ""}</p>}{!concise && <><p>Governed period context; this is not an event prediction.</p><h5>Why this period applies</h5><p>{window.why_this_period_applies}</p><h5>Source-backed timing interpretation</h5><p>{window.reviewed_statement}</p><h5>What this does not establish</h5><ul>{window.limitations.map((item) => <li key={item}>{item}</li>)}</ul></>}<details className="timing-provenance"><summary>View timing evidence &amp; methodology</summary><dl><dt>Original governed interval</dt><dd>{formatTimingInstant(window.source_start)} to {formatTimingInstant(window.source_end)} (end exclusive)</dd><dt>Rule ID</dt><dd>{window.rule_id}</dd><dt>Release</dt><dd>{timing.timing_release_id} {timing.timing_release_version}</dd><dt>Source work</dt><dd>{window.source.source_work}</dd><dt>Section</dt><dd>{window.source.section}</dd><dt>Verse</dt><dd>{window.source.verse}</dd><dt>Chart scope</dt><dd>{window.source.chart_scope}</dd><dt>Dasha scope</dt><dd>{window.source.dasha_scope}</dd><dt>Precision</dt><dd>{timingPrecisionLabel(window.source.precision)}</dd></dl></details></article>)}</div>}</section>;
}

function timingPrecisionLabel(precision: "BROAD_PERIOD" | "SUB_PERIOD"): string {
  return precision === "BROAD_PERIOD" ? "Broad period" : "Sub-period";
}

function formatTimingInstant(value: string): string {
  return new Date(value).toISOString().slice(0, 16).replace("T", " ") + " UTC";
}

function CorpusDetails({ selection }: { selection: Selection | undefined }) {
  if (!selection) return <p>No governed evidence is available.</p>;
  if (selection.relevant_unknown.length) return <p>Some reviewed rules could not be evaluated because required chart facts were not available. UNKNOWN is not treated as a negative conclusion.</p>;
  return <p>No matched reviewed rule is being presented as a negative conclusion.</p>;
}
