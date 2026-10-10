import { useState } from "react";

import "./QuestionAnalysis.css";
import type { AnalysisResult, CareerTimingContext, DetailedComposedAnswer, Intent, Selection } from "../lib/contracts";
import { titleCase } from "../lib/format";

const prompts = ["Career", "Wealth", "Education", "Business", "Children", "Spirituality", "Travel", "Friends"];
const timingSentence = "Timing is not established by the current governed evidence.";

export function QuestionAnalysis({ result, onAnalyze, loading, error }: { result: AnalysisResult | null; onAnalyze: (question: string) => Promise<void>; loading: boolean; error: string }) {
  const [question, setQuestion] = useState("");
  async function submit(event: React.FormEvent<HTMLFormElement>) { event.preventDefault(); if (question.trim()) await onAnalyze(question); }
  return <section className="question-section" id="ask-jyotishai" aria-labelledby="ask-heading"><div className="question-copy"><span className="eyebrow">Ask JyotishAI</span><h2 id="ask-heading">Ask with clarity.</h2><p>Ask about the areas currently covered by the governed interpretation corpus. JyotishAI shows only what the current reviewed evidence can support.</p><div className="prompt-chips" aria-label="Question prompts">{prompts.map((prompt) => <button type="button" key={prompt} onClick={() => setQuestion(`What does my chart say about ${prompt.toLowerCase()}?`)}>{prompt}</button>)}<button type="button" onClick={() => setQuestion("When is a career-related period indicated?")}>Career timing</button></div></div><form className="question-form" onSubmit={submit}><label className="sr-only" htmlFor="question">Your astrology question</label><textarea id="question" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="For example, what does my chart say about career?" /><button className="button primary" disabled={loading || !question.trim()}>{loading ? "Understanding your question…" : "Ask JyotishAI"}</button>{error && <div className="question-error" role="alert"><strong>JyotishAI couldn’t understand that request right now.</strong><span>{error}</span></div>}</form>{result && <AnalysisPanels result={result} />}</section>;
}

function AnalysisPanels({ result }: { result: AnalysisResult }) {
  if (result.routing.status !== "routable") return <article className="notice warning"><strong>{result.routing.status === "unsupported" ? "This question is not supported yet." : "A clarification is needed."}</strong><span>{result.routing.issues.map(titleCase).join(" · ") || "Please ask a supported domain question."}</span></article>;
  return <div className="analysis-results"><QuestionUnderstanding intents={result.routing.intents} /><DetailedAnswers answers={result.answers ?? []} selections={result.selections} /></div>;
}

function QuestionUnderstanding({ intents }: { intents: Intent[] }) {
  return <section className="understanding"><span className="eyebrow">Question understanding</span><h3>How JyotishAI understood your question</h3><p>Your question is organized into separate supported domains before evidence is selected.</p><details><summary>View routing details</summary><div className="intent-grid">{intents.map((intent) => <article className="intent-card" key={intent.intent_id}><strong>{titleCase(intent.domain)} question</strong><dl><dt>Question shape</dt><dd>{titleCase(intent.shape)}</dd><dt>Requires timing</dt><dd>{intent.requires_timing ? "Yes" : "No"}</dd></dl></article>)}</div></details></section>;
}

function DetailedAnswers({ answers, selections }: { answers: DetailedComposedAnswer[]; selections: Selection[] }) {
  return <section className="detailed-answers"><span className="eyebrow">JyotishAI answer</span><h3>Governed interpretation</h3>{answers.map((answer, index) => <DetailedAnswer key={`${answer.interpretation_contract_sha256}-${index}`} answer={answer} selection={selections[index]} />)}</section>;
}

function DetailedAnswer({ answer, selection }: { answer: DetailedComposedAnswer; selection: Selection | undefined }) {
  const hasTiming = answer.answer.endsWith(timingSentence);
  const directAnswer = hasTiming ? answer.answer.slice(0, -timingSentence.length).trim() : answer.answer;
  const details = answer.evidence ?? [];
  const narrative = answer.narrative;
  return <article className="detailed-answer"><section><h4>JyotishAI answer</h4>{narrative ? <><p>{narrative.summary}</p><p>{narrative.explanation}</p><p>{narrative.question_relevance}</p>{narrative.follow_up && <p>{narrative.follow_up}</p>}</> : <p>{directAnswer}</p>}{answer.corpus_limitation && <p className="muted">This answer reflects the current limited governed corpus.</p>}</section>{(answer.why_it_applies?.length ?? 0) > 0 && <section><h4>Why this applies</h4><ul>{answer.why_it_applies?.map((item) => <li key={item}>{item}</li>)}</ul></section>}{(answer.reviewed_interpretations?.length ?? 0) > 0 && <section><h4>Reviewed interpretation</h4>{answer.reviewed_interpretations?.map((item) => <p key={item}>{item}</p>)}</section>}{(answer.limitations?.length ?? 0) > 0 && <section><h4>What this does not establish</h4><ul>{answer.limitations?.map((item) => <li key={item}>{item}</li>)}</ul></section>}{answer.timing ? <CareerTiming timing={answer.timing} /> : hasTiming && <section><h4>Timing</h4><p>{timingSentence}</p></section>}<details className="evidence-details"><summary>View governed evidence &amp; methodology</summary>{details.length ? details.map((item) => <article className="evidence-item" key={`${item.source_section}-${item.placement_explanation}`}><strong>{item.placement_explanation}</strong><span>{item.question_framing}</span><dl><dt>Source work</dt><dd>{item.source_work}</dd><dt>Source section</dt><dd>{item.source_section}</dd><dt>Chart scope</dt><dd>{item.chart_scope} · {item.posture}</dd></dl></article>) : <CorpusDetails selection={selection} />}</details></article>;
}

function CareerTiming({ timing }: { timing: CareerTimingContext }) {
  return <section className="career-timing"><div className="timing-heading"><h4>Career Timing Context</h4></div><p>{timing.message}</p>{timing.status === "MATCH" && <div className="timing-windows">{timing.windows.map((window) => <article className="timing-window" key={`${window.rule_id}-${window.effective_start}-${window.effective_end}`}><span className={`timing-precision timing-precision-${window.precision.toLowerCase()}`}>{timingPrecisionLabel(window.precision)}</span><p className="timing-dates">{formatTimingDate(window.effective_start)} – {formatTimingDate(window.effective_end)}</p><h5>Why this period applies</h5><p>{window.why_this_period_applies}</p><h5>Source-backed timing interpretation</h5><p>{window.reviewed_statement}</p><h5>What this does not establish</h5><ul>{window.limitations.map((item) => <li key={item}>{item}</li>)}</ul><details className="timing-provenance"><summary>View timing evidence &amp; methodology</summary><dl><dt>Source work</dt><dd>{window.source.source_work}</dd><dt>Section</dt><dd>{window.source.section}</dd><dt>Verse</dt><dd>{window.source.verse}</dd><dt>Chart scope</dt><dd>{window.source.chart_scope}</dd><dt>Dasha scope</dt><dd>{window.source.dasha_scope}</dd><dt>Precision</dt><dd>{timingPrecisionLabel(window.source.precision)}</dd></dl></details></article>)}</div>}</section>;
}

function timingPrecisionLabel(precision: "BROAD_PERIOD" | "SUB_PERIOD"): string {
  return precision === "BROAD_PERIOD" ? "Broad period" : "Sub-period";
}

function formatTimingDate(value: string): string {
  return new Intl.DateTimeFormat("en-GB", { timeZone: "UTC", day: "numeric", month: "long", year: "numeric" }).format(new Date(value));
}

function CorpusDetails({ selection }: { selection: Selection | undefined }) {
  if (!selection) return <p>No governed evidence is available.</p>;
  if (selection.relevant_unknown.length) return <p>Some reviewed rules could not be evaluated because required chart facts were not available. UNKNOWN is not treated as a negative conclusion.</p>;
  return <p>No matched reviewed rule is being presented as a negative conclusion.</p>;
}
