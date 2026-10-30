import { useState } from "react";

import "./QuestionAnalysis.css";
import type { AnalysisResult, CareerClaimLedger, CareerTimingContext, ConsultationMessage, DetailedComposedAnswer, Intent, Selection } from "../lib/contracts";
import { titleCase } from "../lib/format";

const prompts = ["Career", "Wealth", "Education", "Business", "Children", "Spirituality", "Travel", "Friends"];
const timingSentence = "Timing is not established by the current governed evidence.";
const unsupportedDomains = new Set(["property", "marriage", "health"]);

export function QuestionAnalysis({ result, messages, onNewConsultation, onAnalyze, loading, error }: { result: AnalysisResult | null; messages?: ConsultationMessage[]; onNewConsultation?: () => void; onAnalyze: (question: string, displayQuestion?: string) => Promise<boolean | void>; loading: boolean; error: string }) {
  const [question, setQuestion] = useState("");
  async function submit(event: React.FormEvent<HTMLFormElement>) { event.preventDefault(); if (question.trim()) { const accepted = await onAnalyze(question.trim()); if (accepted !== false) setQuestion(""); } }
  const last = messages?.slice().reverse().find((message) => Boolean(message.response.analysis));
  const suggestions = last ? followUps(last) : [];
  return <section className="question-section" id="ask-jyotishai" aria-labelledby="ask-heading"><div className="question-copy"><span className="eyebrow">Ask JyotishAI</span><h2 id="ask-heading">A question, answered with evidence.</h2><p>Ask about areas covered by the reviewed corpus. Answers keep chart facts, reviewed interpretation, and timing evidence distinct.</p><p className="capability-note"><strong>Current coverage</strong> Career, wealth, education, business, children, spirituality, travel, and friends. Career timing is available only when governed timing evidence supports it. Property, marriage, and health have no approved production rules.</p>{!messages?.length && <div className="prompt-chips" aria-label="Question prompts">{prompts.map((prompt) => <button type="button" key={prompt} onClick={() => setQuestion(`What does my chart say about ${prompt.toLowerCase()}?`)}>{prompt}</button>)}<button type="button" onClick={() => setQuestion("When is a career-related period indicated?")}>Career timing</button></div>}</div>{messages && messages.length > 0 && <div className="consultation-thread" role="log" aria-label="Consultation conversation" aria-live="polite"><div className="consultation-toolbar"><strong>Consultation</strong>{onNewConsultation && <button type="button" onClick={onNewConsultation} disabled={loading}>Start a new consultation</button>}</div>{messages.map((message, index) => <article className="consultation-turn" key={message.response.state.turn_id}><div className="consultation-user"><span>You asked</span><p className="consultation-question">{message.question}</p></div>{message.response.analysis ? <AnalysisPanels result={message.response.analysis} /> : <div className={`consultation-reply ${message.response.status}`}><span className="eyebrow">JyotishAI</span><h3>{message.response.status === "clarification" ? "Choose what to explain" : "JyotishAI answer"}</h3><FollowUpReply reply={message.response.reply} />{message.response.status === "clarification" && <ClarificationChoices prior={messages.slice(0, index).reverse().find((item) => item.response.analysis)?.response.analysis ?? null} onAnalyze={onAnalyze} loading={loading} />}{message.response.source_references.length > 0 && <details className="reply-evidence"><summary>View approved sources and claim references</summary><p>{message.response.source_references.join("; ")}</p><p>Resolved claims: {message.response.resolved_claim_ids.join(", ") || "—"}</p></details>}</div>}</article>)}</div>}<form className="question-form" onSubmit={submit} aria-busy={loading}><label htmlFor="question">{messages?.length ? "Ask a follow-up" : "Your astrology question"}</label><textarea id="question" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder={messages?.length ? "For example, why did you say that?" : "For example, what does my chart say about career?"} rows={6} />{suggestions.length > 0 && <div className="prompt-chips" aria-label="Suggested follow-ups">{suggestions.map((suggestion) => <button type="button" key={suggestion} onClick={() => setQuestion(suggestion)}>{suggestion}</button>)}</div>}<div className="question-form-footer"><span>{messages?.length ? "Ask about the displayed answer, or start a new consultation for another topic." : "Choose a topic above or write your own question."}</span><button className="button primary" disabled={loading || !question.trim()}>{loading ? "Reviewing evidence…" : "Ask JyotishAI"}</button></div>{loading && <p className="section-status" role="status">Reviewing the available chart evidence…</p>}{error && <div className="question-error" role="alert"><strong>We couldn’t answer that question right now.</strong><span>{error}</span></div>}</form>{!messages && result && <AnalysisPanels result={result} />}</section>;
}

function ClarificationChoices({ prior, onAnalyze, loading }: { prior: AnalysisResult | null; onAnalyze: (question: string, displayQuestion?: string) => Promise<boolean | void>; loading: boolean }) {
  const ledger = prior?.answers[0]?.claim_ledger;
  if (!ledger) return null;
  const choices = ledger.claims.filter((claim) => claim.kind === "APPROVED_INTERPRETATION" || claim.kind === "APPROVED_TIMING_INTERPRETATION" || (claim.kind === "INSUFFICIENT_EVIDENCE" && claim.claim_id.includes("timing")));
  if (choices.length < 2) return null;
  const placement = ledger.claims.find((claim) => claim.kind === "CALCULATED_FACT")?.permitted_wording ?? "";
  const house = placement.match(/\bin the (\w+) house\b/i)?.[1];
  const year = prior?.routing.intents[0]?.time_range?.start_date.slice(0, 4);
  return <div className="clarification-choices" aria-label="Choose an approved claim to explain"><p>Choose a reference from the answer above:</p>{choices.map((claim) => <button type="button" key={claim.claim_id} disabled={loading} onClick={() => void onAnalyze(`Explain claim ${claim.claim_id}`, clarificationLabel(claim, house, year))}>{clarificationLabel(claim, house, year)}</button>)}</div>;
}

function clarificationLabel(claim: CareerClaimLedger["claims"][number], house?: string, year?: string) {
  if (claim.kind === "APPROVED_INTERPRETATION") return `Explain the ${house ? `${house}-house` : "natal"} Career interpretation`;
  if (claim.kind === "INSUFFICIENT_EVIDENCE") return `Explain the ${year ? `${year} ` : ""}Career timing limitation`;
  return `Explain the reviewed Career timing period`;
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
    <section className="direct-answer"><span className="eyebrow">01 · Direct answer</span><h4>JyotishAI answer</h4>
      {unsupported ? <p>No reviewed interpretation is currently available for this area from the active governed corpus.</p> : ledger ? <p>{primaryAnswer || directAnswer}</p> : narrative ? <><p>{narrative.summary}</p><p>{narrative.explanation}</p><p>{narrative.question_relevance}</p>{narrative.follow_up && <p>{narrative.follow_up}</p>}</> : <p>{directAnswer}</p>}
      {answer.corpus_limitation && !ledger && <p className="muted">This answer reflects the current limited governed corpus.</p>}
    </section>
    {ledger && placement && <section className="fact-panel"><span className="eyebrow">02 · Calculated fact</span><h4>Calculated placement</h4><p>{placement}</p></section>}
    {ledger && natalInterpretations.length > 0 && <section className="reviewed-panel"><span className="eyebrow">03 · Reviewed context</span><h4>Reviewed interpretation</h4>{natalInterpretations.map((wording) => <p key={wording}>{wording}</p>)}</section>}
    {!unsupported && <>
      {!ledger && (answer.why_it_applies?.length ?? 0) > 0 && <section><h4>Why this applies</h4><ul>{answer.why_it_applies?.map((item) => <li key={item}>{item}</li>)}</ul></section>}
      {!ledger && (answer.reviewed_interpretations?.length ?? 0) > 0 && <section><h4>Reviewed interpretation</h4>{answer.reviewed_interpretations?.map((item) => <p key={item}>{item}</p>)}</section>}
      {!ledger && (answer.limitations?.length ?? 0) > 0 && <section><h4>What this does not establish</h4><ul>{answer.limitations?.map((item) => <li key={item}>{item}</li>)}</ul></section>}
      {answer.timing ? <CareerTiming timing={answer.timing} concise={Boolean(ledger)} /> : hasTiming && <section><h4>Timing</h4><p>{timingSentence}</p></section>}
      {ledger && (answer.limitations?.length ?? 0) > 0 && <section className="limitation-panel"><h4>What this does not establish</h4><ul>{answer.limitations?.map((item) => <li key={item}>{item}</li>)}</ul></section>}
    </>}
    <details className="evidence-details"><summary>View governed evidence &amp; methodology</summary>
      <p className="evidence-state-line">{unsupported ? "No approved rule" : ledger && answer.timing ? `Natal ${state} · Career timing ${answer.timing.status}` : state}</p>
      {ledger ? <div className="claim-list">{supportedClaims.length > 0 && <p><strong>Approved interpretation sources:</strong> {supportedClaims.map((claim) => `${claim.rule_ids[0]} · ${claim.source_reference}`).join("; ")}</p>}{ledger.claims.map((claim) => <article className="evidence-item" key={claim.claim_id}><strong>{claim.kind === "CALCULATED_FACT" ? "Calculated placement fact" : claim.kind === "INSUFFICIENT_EVIDENCE" ? "Nonmatching or unavailable rule diagnostic" : titleCase(claim.kind)} · {claim.evaluation_status}</strong><dl><dt>Claim ID</dt><dd>{claim.claim_id}</dd><dt>{claim.kind === "CALCULATED_FACT" ? "Interpretive rule" : "Rule"}</dt><dd>{claim.kind === "CALCULATED_FACT" ? "Not applicable to a calculated fact" : claim.rule_ids.join(", ") || "—"}</dd><dt>{claim.kind === "CALCULATED_FACT" ? "Linked interpretation evidence ID" : "Evidence ID"}</dt><dd>{claim.evidence_item_ids.join(", ") || "—"}</dd><dt>Fact</dt><dd>{claim.fact_ids.join(", ") || "—"}</dd><dt>{claim.kind === "CALCULATED_FACT" ? "Calculated fact provenance" : "Source / locator"}</dt><dd>{claim.source_reference}</dd><dt>Methodology</dt><dd>{claim.methodology_version} · {claim.calculation_version}</dd>{claim.authorized_precision && <><dt>Precision</dt><dd>{titleCase(claim.authorized_precision)}</dd></>}{claim.timing_reference && <><dt>Timing interval</dt><dd>{claim.timing_reference}</dd></>}{claim.missing_evidence.length > 0 && <><dt>Missing</dt><dd>{claim.missing_evidence.join(", ")}</dd></>}</dl></article>)}</div> : !unsupported && details.length ? details.map((item, index) => <article className="evidence-item" key={`${item.source_section}-${index}`}><strong>{item.placement_explanation}</strong><span>{item.question_framing}</span><dl><dt>Source work</dt><dd>{item.source_work}</dd><dt>Source section</dt><dd>{item.source_section}</dd>{item.source_reference && <><dt>Reference</dt><dd>{item.source_reference}</dd></>}<dt>Chart scope</dt><dd>{item.chart_scope} · {item.posture}</dd></dl></article>) : <CorpusDetails selection={selection} />}
      {selection && <><p className="evidence-state-line">{selection.selected_matched.length} MATCH · {selection.relevant_unmatched.length} NO_MATCH/FALSE · {selection.relevant_unknown.length} UNKNOWN</p><RuleDiagnostics selection={selection} /></>}
    </details>
  </article>;
}

function CareerTiming({ timing, concise = false }: { timing: CareerTimingContext; concise?: boolean }) {
  return <section className="career-timing"><div className="timing-heading"><div><span className="eyebrow">04 · Governed timing</span><h4>Career Timing Context</h4></div><span className="timing-status">{timing.status === "MATCH" ? "Reviewed period context" : "Timing not established"}{timing.partially_supported ? " · partial range" : ""}</span></div>
    <p>{timing.message}</p>
    {timing.scope === "requested_range" && timing.requested_start_date && timing.requested_end_date && <p className="requested-period"><strong>Requested period</strong> {timing.requested_start_date} through {timing.requested_end_date} (inclusive{timing.calendar_timezone_offset ? `, UTC${timing.calendar_timezone_offset.slice(0, 3)}:${timing.calendar_timezone_offset.slice(3)}` : ""}).</p>}
    {timing.scope === "default_40_year_horizon" && <p>Scope: default 40-year forward horizon.</p>}
    {timing.scope === "historical_unbounded" && <p>Scope: historical question without a supported forward interval.</p>}
    {timing.evaluated_start && timing.evaluated_end && <p>Evaluated interval: {formatTimingDate(timing.evaluated_start, timing.calendar_timezone_offset)} to {formatTimingDate(timing.evaluated_end, timing.calendar_timezone_offset)} (end exclusive).</p>}
    {timing.partially_supported && <p>Only the displayed evaluated portion falls within the supported forward horizon.</p>}
    {timing.status === "UNSUPPORTED" && <p>No Career timing evidence was evaluated for this request.</p>}
    {timing.status === "MATCH" && <div className="timing-windows">{timing.windows.map((window, index) => <article className="timing-window" key={`${window.rule_id}-${window.effective_start}-${window.effective_end}`}><span className="timing-step" aria-hidden="true">{String(index + 1).padStart(2, "0")}</span><div><span className={`timing-precision timing-precision-${window.precision.toLowerCase()}`}>{timingPrecisionLabel(window.precision)}</span><p className="timing-dates">Displayed intersection: {formatTimingDate(window.effective_start, timing.calendar_timezone_offset)} to {formatTimingDate(window.effective_end, timing.calendar_timezone_offset)} (end exclusive).</p>{index > 0 && Date.parse(window.effective_start) < Date.parse(timing.windows[index - 1].effective_end) && <p className="timing-overlap">This period overlaps the previous displayed window.</p>}{window.mahadasha_lord && <p>Calculated Mahadasha: {titleCase(window.mahadasha_lord)}{window.antardasha_lord ? ` · Antardasha: ${titleCase(window.antardasha_lord)}` : ""}</p>}{!concise && <><p>Governed period context; this is not an event prediction.</p><h5>Why this period applies</h5><p>{window.why_this_period_applies}</p><h5>Source-backed timing interpretation</h5><p>{window.reviewed_statement}</p><h5>What this does not establish</h5><ul>{window.limitations.map((item) => <li key={item}>{item}</li>)}</ul></>}<details className="timing-provenance"><summary>View timing evidence &amp; methodology</summary><dl><dt>Displayed intersection UTC</dt><dd>{formatTimingInstant(window.effective_start)} to {formatTimingInstant(window.effective_end)} (end exclusive)</dd><dt>Original governed interval</dt><dd>{formatTimingInstant(window.source_start)} to {formatTimingInstant(window.source_end)} (end exclusive)</dd><dt>Rule ID</dt><dd>{window.rule_id}</dd><dt>Release</dt><dd>{timing.timing_release_id} {timing.timing_release_version}</dd><dt>Source work</dt><dd>{window.source.source_work}</dd><dt>Section</dt><dd>{window.source.section}</dd><dt>Verse</dt><dd>{window.source.verse}</dd><dt>Chart scope</dt><dd>{window.source.chart_scope}</dd><dt>Dasha scope</dt><dd>{window.source.dasha_scope}</dd><dt>Precision</dt><dd>{timingPrecisionLabel(window.source.precision)}</dd></dl></details></div></article>)}</div>}{timing.evaluated_start && timing.evaluated_end && <details className="timing-provenance"><summary>View exact evaluated UTC interval</summary><p>{formatTimingInstant(timing.evaluated_start)} to {formatTimingInstant(timing.evaluated_end)} (end exclusive)</p></details>}</section>;
}

function formatTimingDate(value: string, offset?: string | null): string {
  const minutes = offset && /^[+-]\d{4}$/.test(offset) ? (offset[0] === "-" ? -1 : 1) * (Number(offset.slice(1, 3)) * 60 + Number(offset.slice(3, 5))) : null;
  const date = new Date(Date.parse(value) + (minutes ?? 0) * 60_000);
  return new Intl.DateTimeFormat("en", { dateStyle: "medium", ...(minutes !== null ? { timeZone: "UTC" } : {}) }).format(date);
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

function RuleDiagnostics({ selection }: { selection: Selection }) {
  const groups = [
    { label: "Matched rules", items: selection.selected_matched },
    { label: "Rules that did not match", items: selection.relevant_unmatched },
    { label: "Rules awaiting facts", items: selection.relevant_unknown },
  ];
  return <details className="rule-diagnostics"><summary>View rule evaluation details</summary>{groups.map((group) => group.items.length > 0 && <section key={group.label}><h5>{group.label}</h5>{group.items.map((item) => <dl key={`${item.rule_id}-${item.rule_version}`}><dt>Rule</dt><dd>{item.rule_id} · {item.rule_version}</dd><dt>Status</dt><dd>{item.evaluation_status}</dd><dt>Resolved facts</dt><dd>{item.resolved_facts.map((fact) => fact.fact_id).join(", ") || "—"}</dd></dl>)}</section>)}{selection.excluded.length > 0 && <section><h5>Excluded rules</h5>{selection.excluded.map((item) => <p key={`${item.rule_id}-${item.rule_version}`}>{item.rule_id} · {item.rule_version}: {item.exclusion_reason}</p>)}</section>}</details>;
}

type ReplyPeriod = { mahadasha: string; antardasha: string; start: string; end: string };

function parseDashaReply(reply: string): { intro: string; periods: ReplyPeriod[]; conclusion: string } | null {
  if (!reply.includes("calculated Vimshottari periods are:")) return null;
  const matches = [...reply.matchAll(/([A-Z][a-z]+) Mahadasha, ([A-Z][a-z]+) Antardasha:[\s\S]*?local overlap (\d{4}-\d{2}-\d{2}T[^\s]+) to (\d{4}-\d{2}-\d{2}T[^\s]+) \(end exclusive\)\./g)];
  if (!matches.length || matches.some((item) => !formatLocalInstant(item[3]) || !formatLocalInstant(item[4]))) return null;
  const first = matches[0];
  const last = matches.at(-1)!;
  return {
    intro: reply.slice(0, first.index).trim(),
    periods: matches.map((item) => ({ mahadasha: item[1], antardasha: item[2], start: item[3], end: item[4] })),
    conclusion: reply.slice(last.index + last[0].length).trim(),
  };
}

function formatLocalInstant(value: string): string | null {
  const match = /^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}):\d{2}(?:\.\d+)?(Z|[+-]\d{2}:\d{2})$/.exec(value);
  if (!match || !Number.isFinite(Date.parse(value))) return null;
  const date = new Intl.DateTimeFormat("en", { dateStyle: "medium", timeZone: "UTC" }).format(new Date(`${match[1]}T00:00:00Z`));
  return `${date}, ${match[2]} ${match[3] === "Z" ? "UTC" : `UTC${match[3]}`}`;
}

function FollowUpReply({ reply }: { reply: string | null }) {
  if (!reply) return null;
  const dasha = parseDashaReply(reply);
  if (dasha) return <div className="reply-periods"><p>{dasha.intro}</p><div className="reply-period-grid">{dasha.periods.map((period, index) => <article className="reply-period" key={`${period.start}-${period.end}`}><span className="eyebrow">Period {index + 1} · requested range overlap</span><h4>{period.mahadasha} Mahadasha</h4><strong>{period.antardasha} Antardasha</strong><p>{formatLocalInstant(period.start)} → {formatLocalInstant(period.end)} <span>(end exclusive)</span></p></article>)}</div>{dasha.conclusion && <p className="reply-limitation">{dasha.conclusion}</p>}<details className="reply-evidence"><summary>View exact Dasha response and UTC precision</summary><p>{reply}</p></details></div>;
  const visible = reply.replace(/(\d{2}:\d{2}:\d{2})\.\d+(?=Z|[+-]\d{2}:\d{2})/g, "$1");
  return <><p>{visible}</p>{visible !== reply && <details className="reply-evidence"><summary>View exact response</summary><p>{reply}</p></details>}</>;
}
