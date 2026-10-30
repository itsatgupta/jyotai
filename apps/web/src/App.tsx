import { useEffect, useRef, useState } from "react";

import { BirthProfile } from "./components/BirthProfile";
import { GovernedInsights } from "./components/GovernedInsights";
import { QuestionAnalysis } from "./components/QuestionAnalysis";
import { Workspace } from "./components/Workspace";
import type { WorkspaceTab } from "./components/Workspace";
import { ApiError, api } from "./lib/api";
import type { AnalysisResult, BirthInput, ConsultationMessage, Context } from "./lib/contracts";
import { titleCase } from "./lib/format";
import { signGlyph } from "./lib/glyphs";
import { OrbitArtwork } from "./components/OrbitArtwork";

export default function App() {
  const consultationGeneration = useRef(0);
  const [theme, setTheme] = useState<"light" | "dark">(() => {
    try { return window.localStorage.getItem("jyotai-theme") === "dark" ? "dark" : "light"; }
    catch { return "light"; }
  });
  const [context, setContext] = useState<Context | null>(null);
  const [birth, setBirth] = useState<BirthInput | null>(null);
  const [asOf, setAsOf] = useState("");
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [workspaceTab, setWorkspaceTab] = useState<WorkspaceTab>("Overview");
  const [messages, setMessages] = useState<ConsultationMessage[]>([]);
  const [consultationId, setConsultationId] = useState<string | null>(null);
  const [sessionExpired, setSessionExpired] = useState(false);
  const [questionError, setQuestionError] = useState("");
  const [loading, setLoading] = useState<"profile" | "question" | null>(null);
  const [error, setError] = useState("");
  const profileKey = birth ? JSON.stringify([birth, asOf]) : "no-profile";
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try { window.localStorage.setItem("jyotai-theme", theme); } catch { /* Storage may be unavailable. */ }
  }, [theme]);
  useEffect(() => { if (workspaceTab === "Dasha" && window.location.hash === "#dasha") window.requestAnimationFrame(() => document.getElementById("dasha")?.scrollIntoView?.()); }, [workspaceTab]);
  async function createProfile(input: BirthInput, instant: string) { const generation = ++consultationGeneration.current; setLoading("profile"); setError(""); setQuestionError(""); setAnalysis(null); setMessages([]); setConsultationId(null); setSessionExpired(false); setWorkspaceTab("Overview"); try { const next = await api.context(input, instant); if (generation === consultationGeneration.current) { setContext(next); setBirth(input); setAsOf(instant); } } catch (reason) { if (generation === consultationGeneration.current) setError(message(reason)); } finally { if (generation === consultationGeneration.current) setLoading(null); } }
  async function analyze(question: string, displayQuestion = question, reference?: { reference_turn_id: string; claim_ids: string[] }): Promise<boolean> { if (!birth || !asOf || sessionExpired) return false; const generation = consultationGeneration.current; setLoading("question"); setError(""); setQuestionError(""); try { const response = await api.consultation({ birth_input: birth, as_of: asOf, question, ...(consultationId ? { consultation_id: consultationId } : {}), ...reference }); if (generation !== consultationGeneration.current) return false; setConsultationId(response.state.consultation_id); setMessages((current) => [...current, { question: displayQuestion, response }]); if (response.analysis) { setAnalysis(response.analysis); setContext(response.analysis.context); } return true; } catch (reason) { if (generation === consultationGeneration.current) { setQuestionError(message(reason)); if (reason instanceof ApiError && reason.status === 409 && reason.message.includes("Start a new consultation")) setSessionExpired(true); } return false; } finally { if (generation === consultationGeneration.current) setLoading(null); } }
  function newConsultation() { consultationGeneration.current += 1; setMessages([]); setConsultationId(null); setAnalysis(null); setQuestionError(""); setSessionExpired(false); }
  const profileName = context?.birth_input.display_name?.trim() || "Your profile";
  return <main className="preview-app integrated-app" data-preview-theme={theme}>
    <a className="preview-skip" href="#birth-profile">Skip to birth details</a>
    <aside className="preview-sidebar" aria-label="Main navigation">
      <a className="preview-brand" href="#top" aria-label="JyotishAI home"><span className="brand-sigil" aria-hidden="true">✦</span><span>Jyotish<span>AI</span><small>CELESTIAL ATLAS</small></span></a>
      <div className="sidebar-caption">YOUR SPACE</div>
      <nav className="sidebar-nav" aria-label="Dashboard sections">
        <a href="#top"><span aria-hidden="true">◈</span> Overview</a>
        <a href={context ? "#profile-heading" : "#birth-profile"}><span aria-hidden="true">✧</span> Birth details</a>
        {context && <><a href="#workspace-heading" onClick={() => setWorkspaceTab("Overview")}><span aria-hidden="true">◇</span> Kundli</a><a href="#dasha" onClick={() => setWorkspaceTab("Dasha")}><span aria-hidden="true">◷</span> Dasha</a><a href="#ask-jyotishai"><span aria-hidden="true">✦</span> Consultation</a><a href="#insights-heading"><span aria-hidden="true">✶</span> Evidence</a></>}
      </nav>
      <div className="sidebar-divider" />
      <p className="sidebar-note">Vedic · sidereal · Lahiri · Vimshottari. Chart facts are calculated; interpretations use reviewed evidence.</p>
      {context && <div className="sidebar-bottom"><div className="sidebar-avatar">{profileName.charAt(0).toUpperCase()}</div><div><strong>{profileName}</strong><span>Private birth profile</span></div></div>}
    </aside>
    <div className="preview-main" id="top">
      <header className="preview-topbar"><div className="topbar-trail">PERSONAL ATLAS <span>/</span> {context ? "YOUR CHART" : "WELCOME"}</div><div className="topbar-actions"><span className="demo-pill"><span /> {context ? "CALCULATED CHART" : "CREATE YOUR CHART"}</span><button type="button" className="theme-button" aria-label={`Switch to ${theme === "light" ? "dark" : "light"} theme`} aria-pressed={theme === "dark"} onClick={() => setTheme(theme === "light" ? "dark" : "light")}><span aria-hidden="true">{theme === "light" ? "☾" : "☀"}</span><span>{theme === "light" ? "Dark" : "Light"}</span></button></div></header>
      <div className="preview-content">
        <section className="preview-hero" aria-labelledby="hero-heading"><div className="hero-stars" aria-hidden="true"/><div className="hero-copy"><div className="hero-kicker"><span className="kicker-star">✦</span> THE ART OF SEEING CLEARLY</div><h1 id="hero-heading">A universe,<br/><em>uniquely yours.</em></h1><p>A luminous home for the geometry of your chart, the rhythm of planetary periods, and questions worth exploring with care.</p><div className="hero-cta"><a className="gold-button" href={context ? "#workspace-heading" : "#birth-profile"}>{context ? "Explore your chart" : "Create your birth chart"} <span aria-hidden="true">↗</span></a><span>Vedic astrology · clear by design</span></div></div><div className="hero-art"><OrbitArtwork/><div className="orbit-caption">ZODIAC ARTWORK · DECORATIVE ONLY</div></div><div className="hero-corner">✦ <span>AS ABOVE<br/>SO BELOW</span></div></section>
        {error && !questionError && <div className="notice error" role="alert"><strong>We couldn’t create your chart.</strong><span>{error}</span></div>}
        {!context && <BirthProfile onSubmit={createProfile} loading={loading === "profile"} />}
        {context && birth && <div id="dashboard"><ProfileStrip context={context} /><details className="profile-editor"><summary>Edit birth details</summary><BirthProfile key={`editor:${profileKey}`} initialBirth={birth} initialAsOf={asOf} onSubmit={createProfile} loading={loading === "profile"} /></details><Workspace key={`workspace:${profileKey}`} context={context} active={workspaceTab} onActiveChange={setWorkspaceTab} /><GovernedInsights key={`insights:${profileKey}`} birth={birth} asOf={asOf} /><QuestionAnalysis key={`consultation:${profileKey}`} result={analysis} messages={messages} onNewConsultation={newConsultation} onAnalyze={analyze} loading={loading !== null} error={questionError} sessionExpired={sessionExpired} /></div>}
        <footer className="preview-footer"><span>✦ JyotishAI</span><p>Sidereal Vedic methodology · Lahiri ayanamsa · deterministic calculations</p></footer>
      </div>
    </div>
  </main>;
}

function ProfileStrip({ context }: { context: Context }) {
  const moon = context.d1.planets.find((planet) => planet.body === "moon");
  const name = context.birth_input.display_name?.trim();
  return <section className="profile-strip" aria-labelledby="profile-heading"><div className="profile-identity"><div className="profile-monogram">{name?.charAt(0).toUpperCase() || "✦"}<span>✦</span></div><div><span className="section-kicker">THE BIRTH PROFILE</span><h2 id="profile-heading">{name ? `${name}’s` : "Your"} Vedic profile</h2><details className="profile-private"><summary>View birth details</summary><p>{context.birth_input.birth_date} · {context.birth_input.birth_time.slice(0, 5)} · {context.birth_input.place_name || "Birthplace selected"}</p></details><div className="profile-assurances"><span>Governed interpretation</span><span>Deterministic chart calculation</span></div></div></div><div className="profile-stat"><span>ASCENDANT <i>✦</i></span><strong><b>{signGlyph(context.d1.ascendant?.sign)}</b> {titleCase(context.d1.ascendant?.sign ?? "Unavailable")}</strong><small>Calculated D1 placement</small></div><div className="profile-stat"><span>MOON SIGN <i>✦</i></span><strong><b>{signGlyph(moon?.sign)}</b> {titleCase(moon?.sign ?? "Unavailable")}</strong><small>Calculated D1 placement</small></div><div className="profile-stat"><span>CHART METHOD</span><strong>Sidereal · D1</strong><small>Lahiri · North Indian</small></div></section>;
}

function message(reason: unknown) { return reason instanceof Error ? reason.message : "The deterministic service is temporarily unavailable."; }
