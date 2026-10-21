import { useEffect, useState } from "react";

import { api } from "../lib/api";
import type { BirthInput, DashboardDomain, DashboardInsight, DashboardInsightsResult } from "../lib/contracts";
import { titleCase } from "../lib/format";
import { DomainIllustration } from "./VisualOrnaments";

const domains: DashboardDomain[] = ["career", "wealth", "education", "business", "children", "spirituality", "travel", "friends"];
const noMatch = "No reviewed interpretation is currently available for this area from the active governed corpus.";
const unknown = "Available chart facts are not sufficient to evaluate the reviewed rules for this area.";
const noRule = "No approved production rule is available for this area. No interpretation is shown.";

export function GovernedInsights({ birth, asOf }: { birth: BirthInput; asOf: string }) {
  const [result, setResult] = useState<DashboardInsightsResult | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    setResult(null);
    setError("");
    api.dashboardInsights(birth, asOf).then((response) => {
      if (active) setResult(response);
    }).catch((reason: unknown) => {
      if (active) setError(reason instanceof Error ? reason.message : "Governed insights are temporarily unavailable.");
    });
    return () => { active = false; };
  }, [birth, asOf]);

  return <section className="insights-section" aria-labelledby="insights-heading">
    <div className="workspace-title"><span className="eyebrow">Governed insights</span><h2 id="insights-heading">Reviewed chart context</h2><p>Each area uses the active reviewed corpus. These cards do not evaluate astrology rules in your browser.</p></div>
    {!result && !error && <p className="section-status" role="status">Loading governed insights…</p>}
    {error && <div className="section-status error" role="alert"><strong>Governed insights are unavailable right now.</strong><span>{error}</span></div>}
    {result && <div className="insight-grid">{domains.map((domain) => <InsightCard key={domain} domain={domain} insight={result.insights.find((item) => item.domain === domain)} />)}</div>}
  </section>;
}

function InsightCard({ domain, insight }: { domain: DashboardDomain; insight?: DashboardInsight }) {
  const state = !insight ? "unavailable" : insight.has_matched_evidence ? "match" : insight.unknown_count > 0 ? "unknown" : insight.unmatched_count > 0 ? "no-match" : "no-rule";
  const evidenceCount = insight ? insight.matched_count + insight.unmatched_count + insight.unknown_count : 0;
  return <article className={`insight-card insight-${domain} insight-${state}`}>
    <header><DomainIllustration domain={domain} /><div><span className="insight-state">{state === "match" ? "Matched reviewed evidence · MATCH" : state === "unknown" ? "Could not evaluate · UNKNOWN" : state === "no-match" ? "Rule did not match · FALSE" : state === "no-rule" ? "No approved rule" : "Insight unavailable"}</span><h3>{titleCase(domain)}</h3></div></header>
    {state === "match" && insight?.answers.map((answer, index) => <div className="insight-answer" key={`${answer.answer}-${index}`}><p>{answer.answer}</p>{answer.evidence?.length ? <details className="insight-methodology"><summary>View source references</summary>{answer.evidence.map((item, evidenceIndex) => <dl key={`${item.source_work}-${item.source_section}-${evidenceIndex}`}><dt>Source work</dt><dd>{item.source_work}</dd><dt>Source section</dt><dd>{item.source_section}</dd>{item.source_reference && <><dt>Reference</dt><dd>{item.source_reference}</dd></>}<dt>Chart scope</dt><dd>{item.chart_scope} · {item.posture}</dd></dl>)}</details> : null}</div>)}
    {state === "unknown" && <p>{unknown}</p>}
    {state === "no-match" && <p>{noMatch}</p>}
    {state === "no-rule" && <p>{noRule}</p>}
    {state === "unavailable" && <p>No governed insight was supplied for this area.</p>}
    {insight && evidenceCount > 0 && <details className="insight-methodology"><summary>View governed evidence &amp; methodology</summary><p>Contract states: {insight.matched_count} MATCH, {insight.unmatched_count} NO_MATCH/FALSE, {insight.unknown_count} UNKNOWN. UNKNOWN means unevaluated and does not imply an adverse result.</p></details>}
  </article>;
}
