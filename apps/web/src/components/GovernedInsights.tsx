import { useEffect, useState } from "react";

import { api } from "../lib/api";
import type { BirthInput, DashboardDomain, DashboardInsight, DashboardInsightsResult } from "../lib/contracts";
import { titleCase } from "../lib/format";

const domains: DashboardDomain[] = ["career", "wealth", "education", "business", "children", "spirituality", "travel", "friends"];
const noMatch = "No reviewed interpretation is currently available for this area from the active governed corpus.";
const unknown = "Available chart facts are not sufficient to evaluate the reviewed rules for this area.";

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
  const state = insight?.has_matched_evidence ? "match" : (insight?.unknown_count ?? 0) > 0 ? "unknown" : "no-match";
  const evidenceCount = insight ? insight.matched_count + insight.unmatched_count + insight.unknown_count : 0;
  return <article className="insight-card">
    <h3>{titleCase(domain)}</h3>
    {state === "match" && insight?.answers.map((answer, index) => <p key={`${answer.answer}-${index}`}>{answer.answer}</p>)}
    {state === "unknown" && <p>{unknown}</p>}
    {state === "no-match" && <p>{noMatch}</p>}
    {insight && evidenceCount > 0 && <details className="insight-methodology"><summary>View governed evidence &amp; methodology</summary><p>{insight.matched_count} matched, {insight.unmatched_count} not matched, and {insight.unknown_count} unavailable evaluation{insight.unknown_count === 1 ? "" : "s"}. These statuses remain distinct.</p></details>}
  </article>;
}
