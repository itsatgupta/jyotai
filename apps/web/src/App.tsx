import { useState } from "react";
import { BirthProfile } from "./components/BirthProfile";
import { QuestionAnalysis } from "./components/QuestionAnalysis";
import { Workspace } from "./components/Workspace";
import { api } from "./lib/api";
import type { AnalysisResult, BirthInput, Context } from "./lib/contracts";
import { titleCase } from "./lib/format";

export default function App() {
  const [context, setContext] = useState<Context | null>(null);
  const [birth, setBirth] = useState<BirthInput | null>(null);
  const [asOf, setAsOf] = useState("");
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState<"profile" | "question" | null>(null);
  const [error, setError] = useState("");
  async function createProfile(input: BirthInput, instant: string) {
    setLoading("profile"); setError(""); setAnalysis(null);
    try { setContext(await api.context(input, instant)); setBirth(input); setAsOf(instant); }
    catch (reason) { setError(message(reason)); }
    finally { setLoading(null); }
  }
  async function analyze(question: string) {
    if (!birth || !asOf) return;
    setLoading("question"); setError("");
    try { const result = await api.analyze({ birth_input: birth, as_of: asOf, question }); setAnalysis(result); setContext(result.context); }
    catch (reason) { setError(message(reason)); }
    finally { setLoading(null); }
  }
  return <main><header className="site-header"><a className="wordmark" href="#top">Jyot<span>AI</span></a><div><strong>Deterministic Vedic Astrology Intelligence</strong><span className="engine-badge">Deterministic engine</span></div></header><div id="top" className="shell"><BirthProfile onSubmit={createProfile} loading={loading === "profile"} />{error && <div className="notice error" role="alert"><strong>We couldn’t complete that request.</strong><span>{error}</span></div>}{context && <><Summary context={context} /><Workspace context={context} /><QuestionAnalysis result={analysis} onAnalyze={analyze} loading={loading === "question"} /></>}</div></main>;
}

function Summary({ context }: { context: Context }) { return <section className="summary-strip" aria-label="Profile summary"><SummaryCard label="Ascendant" value={context.d1.ascendant ? `${titleCase(context.d1.ascendant.sign)} ${Number(context.d1.ascendant.degree_in_sign).toFixed(2)}°` : "—"} /><SummaryCard label="Moon sign" value={titleCase(context.d1.planets.find((planet) => planet.body === "moon")?.sign ?? "—")} /><SummaryCard label="Current Mahadasha" value={titleCase(context.active_dasha.mahadasha.lord)} /><SummaryCard label="Current Antardasha" value={titleCase(context.active_dasha.antardasha.lord)} /><SummaryCard label="As-of date" value={new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(context.requested_as_of))} /></section>; }
function SummaryCard({ label, value }: { label: string; value: string }) { return <article><span>{label}</span><strong>{value}</strong></article>; }
function message(reason: unknown) { return reason instanceof Error ? reason.message : "The deterministic service is temporarily unavailable."; }
