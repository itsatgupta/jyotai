import { useState } from "react";

import type { AnalysisResult, ComposedAnswer, Evidence, Intent, Selection } from "../lib/contracts";
import { titleCase } from "../lib/format";

const prompts = ["Career", "Wealth", "Education", "Foreign residence"];

export function QuestionAnalysis({ result, onAnalyze, loading, error }: { result: AnalysisResult | null; onAnalyze: (question: string) => Promise<void>; loading: boolean; error: string }) {
  const [question, setQuestion] = useState("");

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (question.trim()) await onAnalyze(question);
  }

  return <section className="question-section" id="ask-jyotishai" aria-labelledby="ask-heading"><div className="question-copy"><span className="eyebrow">Ask JyotishAI</span><h2 id="ask-heading">What’s on your mind?</h2><p>Ask about career, wealth, education, business, children, spirituality, travel or friendships. JyotishAI shows only what the current governed evidence can support.</p><div className="prompt-chips" aria-label="Question prompts">{prompts.map((prompt) => <button type="button" key={prompt} onClick={() => setQuestion(prompt === "Foreign residence" ? "Is there any indication related to foreign residence?" : `What does my chart say about ${prompt.toLowerCase()}?`)}>{prompt}</button>)}</div></div><form className="question-form" onSubmit={submit}><label className="sr-only" htmlFor="question">Your astrology question</label><textarea id="question" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="For example, what does my chart say about career?" /><button className="button primary" disabled={loading || !question.trim()}>{loading ? "Understanding your question…" : "Ask JyotishAI"}</button>{error && <div className="question-error" role="alert"><strong>JyotishAI couldn’t understand that request right now.</strong><span>{error}</span></div>}</form>{result && <AnalysisPanels result={result} />}</section>;
}

function AnalysisPanels({ result }: { result: AnalysisResult }) {
  if (result.routing.status !== "routable") return <article className="notice warning"><strong>{result.routing.status === "unsupported" ? "This question is not supported yet." : "A clarification is needed."}</strong><span>{result.routing.issues.map(titleCase).join(" · ") || "Please ask a supported domain question."}</span></article>;
  const answers = result.answers ?? [];
  if (answers.some((answer) => answer.corpus_limitation)) return <div className="analysis-results corpus-limit-results"><Interpretation answers={answers} /><CorpusLimitEvidence selections={result.selections} /></div>;
  return <div className="analysis-results"><QuestionUnderstanding intents={result.routing.intents} /><EvidenceArea selections={result.selections} /><Interpretation answers={answers} /></div>;
}

function CorpusLimitEvidence({ selections }: { selections: Selection[] }) {
  const domains = [...new Set(selections.filter((selection) => !selection.capability_summary.has_matched_evidence).map((selection) => titleCase(selection.question_intent.domain)))];
  return <section className="understanding corpus-limit-context"><p>No reviewed governed evidence is currently available for {domains.join(" and ") || "this topic"}.</p><details className="evidence-details"><summary>View governed evidence &amp; methodology</summary>{selections.map((selection) => <EvidencePanel key={selection.question_intent.intent_id} selection={selection} />)}</details></section>;
}

function QuestionUnderstanding({ intents }: { intents: Intent[] }) {
  return <section className="understanding"><span className="eyebrow">Question understanding</span><h3>How JyotishAI understood your question</h3><p>Your question is organized into separate supported domains before evidence is selected.</p><details><summary>View routing details</summary><div className="intent-grid">{intents.map((intent) => <IntentCard key={intent.intent_id} intent={intent} />)}</div></details></section>;
}

function EvidenceArea({ selections }: { selections: Selection[] }) {
  return <section className="evidence-area"><span className="eyebrow">Governed evidence</span><h3>Evidence availability</h3>{selections.map((selection) => <EvidencePanel key={selection.question_intent.intent_id} selection={selection} />)}</section>;
}

function IntentCard({ intent }: { intent: Intent }) {
  return <article className="intent-card"><strong>{titleCase(intent.domain)} question</strong><dl><dt>Question shape</dt><dd>{titleCase(intent.shape)}</dd><dt>Temporal intent</dt><dd>{titleCase(intent.temporal_intent)}</dd><dt>Requires timing</dt><dd>{intent.requires_timing ? "Yes" : "No"}</dd>{intent.time_range && <><dt>Resolved range</dt><dd>{intent.time_range.start_date} — {intent.time_range.end_date}</dd></>}{intent.unresolved_relative_time && <><dt>Unresolved time</dt><dd>{titleCase(intent.unresolved_relative_time)}</dd></>}</dl></article>;
}

function EvidencePanel({ selection }: { selection: Selection }) {
  const timing = selection.capability_summary.timing_requested && !selection.capability_summary.timing_answerability_established;
  const none = !selection.capability_summary.has_matched_evidence;
  return <article className="evidence-panel"><header><h4>{titleCase(selection.question_intent.domain)}</h4><span>Exact-domain selection</span></header>{timing && <Info title="Timing evidence is not yet available." text="No timing conclusion has been established from the current governed evidence." />}{none && <Info title="No governed evidence is currently available for this domain." text="JyotishAI is currently operating with a limited reviewed rule corpus." />}{!timing && !none && <Info title="Governed evidence is available for this domain." text="Review the evidence and methodology below." />}<details className="evidence-details"><summary>Evidence &amp; methodology</summary><EvidenceGroup title="Matched evidence" items={selection.selected_matched} /><EvidenceGroup title="Unmatched evaluations" items={selection.relevant_unmatched} /><EvidenceGroup title="Unknown evaluations" items={selection.relevant_unknown} /><ExcludedEvidence items={selection.excluded} /></details></article>;
}

function Info({ title, text }: { title: string; text: string }) {
  return <div className="info-state"><strong>{title}</strong><span>{text}</span></div>;
}

function EvidenceGroup({ title, items }: { title: string; items: Evidence[] }) {
  return <section className="evidence-group"><h5>{title}</h5>{items.length ? items.map((item) => <article className="evidence-item" key={`${item.rule_id}@${item.rule_version}`}><strong>Governed rule available</strong><span>{titleCase(item.evaluation_status)} · {titleCase(item.evidence_direction)} · {titleCase(item.posture)}</span><details className="provenance"><summary>Advanced provenance</summary><dl><dt>Rule</dt><dd>{item.rule_id}@{item.rule_version}</dd><dt>Resolved facts</dt><dd>{item.resolved_facts.map((fact) => `${fact.fact_id}: ${JSON.stringify(fact.value)}`).join(", ") || "None"}</dd><dt>Provenance</dt><dd><pre>{JSON.stringify({ governance: item.governance_provenance, facts: item.fact_provenance, trace: item.condition_trace }, null, 2)}</pre></dd></dl></details></article>) : <p>None.</p>}</section>;
}

function ExcludedEvidence({ items }: { items: Selection["excluded"] }) {
  if (!items.length) return null;
  const byDomain = items.reduce<Record<string, { count: number; reasons: Set<string> }>>((groups, item) => {
    const group = groups[item.domain] ?? { count: 0, reasons: new Set<string>() };
    group.count += 1;
    group.reasons.add(titleCase(item.exclusion_reason));
    groups[item.domain] = group;
    return groups;
  }, {});
  return <section className="evidence-group excluded-summary"><h5>Excluded evidence by domain</h5><ul>{Object.entries(byDomain).map(([domain, group]) => <li key={domain}><strong>{titleCase(domain)}</strong>: {group.count} {group.count === 1 ? "evaluation" : "evaluations"} excluded ({[...group.reasons].join(", ")}).</li>)}</ul></section>;
}

function Interpretation({ answers }: { answers: ComposedAnswer[] }) {
  return <section className="interpretation"><span className="eyebrow">JyotishAI answer</span><h3>Governed interpretation</h3>{answers.map((answer, index) => <article key={`${answer.interpretation_contract_sha256}-${index}`}><p>{answer.answer}</p>{answer.corpus_limitation && <p className="muted">This answer reflects the current limited governed corpus.</p>}</article>)}</section>;
}
