import { useEffect, useRef, useState } from "react";

import { BirthProfile } from "./components/BirthProfile";
import { GovernedInsights } from "./components/GovernedInsights";
import { QuestionAnalysis } from "./components/QuestionAnalysis";
import { Workspace } from "./components/Workspace";
import { api } from "./lib/api";
import type { AnalysisResult, BirthInput, ConsultationMessage, Context } from "./lib/contracts";
import { titleCase } from "./lib/format";
import { planetGlyph, signGlyph } from "./lib/glyphs";
import { CelestialBackdrop, TrustMark } from "./components/VisualOrnaments";

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
  const [messages, setMessages] = useState<ConsultationMessage[]>([]);
  const [consultationId, setConsultationId] = useState<string | null>(null);
  const [questionError, setQuestionError] = useState("");
  const [loading, setLoading] = useState<"profile" | "question" | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try { window.localStorage.setItem("jyotai-theme", theme); } catch { /* Storage may be unavailable. */ }
  }, [theme]);
  async function createProfile(input: BirthInput, instant: string) { const generation = ++consultationGeneration.current; setLoading("profile"); setError(""); setQuestionError(""); setAnalysis(null); setMessages([]); setConsultationId(null); try { const next = await api.context(input, instant); if (generation === consultationGeneration.current) { setContext(next); setBirth(input); setAsOf(instant); } } catch (reason) { if (generation === consultationGeneration.current) setError(message(reason)); } finally { if (generation === consultationGeneration.current) setLoading(null); } }
  async function analyze(question: string, displayQuestion = question): Promise<boolean> { if (!birth || !asOf) return false; const generation = consultationGeneration.current; setLoading("question"); setError(""); setQuestionError(""); try { const response = await api.consultation({ birth_input: birth, as_of: asOf, question, ...(consultationId ? { consultation_id: consultationId } : {}) }); if (generation !== consultationGeneration.current) return false; setConsultationId(response.state.consultation_id); setMessages((current) => [...current, { question: displayQuestion, response }].slice(-20)); if (response.analysis) { setAnalysis(response.analysis); setContext(response.analysis.context); } return true; } catch (reason) { if (generation === consultationGeneration.current) setQuestionError(message(reason)); return false; } finally { if (generation === consultationGeneration.current) setLoading(null); } }
  function newConsultation() { consultationGeneration.current += 1; setMessages([]); setConsultationId(null); setAnalysis(null); setQuestionError(""); }
  return <main>
    <a className="skip-link" href="#birth-profile">Skip to birth details</a>
    <header className="site-header"><a className="wordmark" href="#top" aria-label="JyotishAI home">Jyotish<span>AI</span></a><nav aria-label="Main navigation"><a href="#birth-profile">Birth details</a>{context && <><a href="#workspace-heading">Kundli</a><a href="#dasha">Dasha</a><a href="#ask-jyotishai">Consultation</a><a href="#insights-heading">Evidence</a></>}</nav><button type="button" className="theme-toggle" aria-label={`Switch to ${theme === "light" ? "dark" : "light"} theme`} aria-pressed={theme === "dark"} onClick={() => setTheme(theme === "light" ? "dark" : "light")}><span aria-hidden="true">{theme === "light" ? "☾" : "☀"}</span><span>{theme === "light" ? "Dark" : "Light"}</span></button></header>
    <Hero />
    <div className="shell">{error && !questionError && <div className="notice error" role="alert"><strong>We couldn’t create your chart.</strong><span>{error}</span></div>}<BirthProfile onSubmit={createProfile} loading={loading === "profile"} />{context && birth && <div id="dashboard"><ProfileHeader context={context} /><Journey /><Workspace context={context} /><GovernedInsights key={`${asOf}-${birth.birth_date}-${birth.birth_time}`} birth={birth} asOf={asOf} /><QuestionAnalysis result={analysis} messages={messages} onNewConsultation={newConsultation} onAnalyze={analyze} loading={loading !== null} error={questionError} /></div>}</div>
    <footer className="site-footer"><span>JyotishAI</span><p>Sidereal Vedic methodology · Lahiri ayanamsa · Deterministic calculations</p></footer>
  </main>;
}

function Hero() { return <section className="hero" id="top"><div className="hero-copy"><span className="eyebrow">JyotishAI · Vedic astrology, thoughtfully made</span><h1>Your Vedic Astrology, <em>intelligently decoded.</em></h1><p>Begin with your birth details. Explore calculated chart facts, then read interpretations grounded in reviewed Jyotish evidence.</p><div className="hero-actions"><a className="button primary" href="#birth-profile">Create My Horoscope</a></div><p className="trust-line">Sidereal <i>·</i> Lahiri ayanamsa <i>·</i> Deterministic calculations</p></div><CelestialVisual /></section>; }
function Journey() { return <nav className="journey" id="journey" aria-label="Your chart journey"><a href="#birth-profile"><span>01</span> Birth details</a><a href="#workspace-heading"><span>02</span> Kundli &amp; Dasha</a><a href="#insights-heading"><span>03</span> Governed insights</a><a href="#ask-jyotishai"><span>04</span> Ask JyotishAI</a></nav>; }
function CelestialVisual() { return <div className="celestial" aria-hidden="true"><span className="star s1" /><span className="star s2" /><span className="star s3" /><svg viewBox="0 0 500 500" focusable="false"><circle cx="250" cy="250" r="190" className="orbit outer" /><circle cx="250" cy="250" r="140" className="orbit" /><circle cx="250" cy="250" r="84" className="orbit" /><path className="mandala" d="M250 55v390M55 250h390M112 112l276 276M388 112L112 388" /><circle cx="250" cy="250" r="38" className="sun" /><text x="250" y="267" textAnchor="middle">☉</text><text x="250" y="89" textAnchor="middle">♈</text><text x="411" y="257" textAnchor="middle">♋</text><text x="250" y="427" textAnchor="middle">♎</text><text x="89" y="257" textAnchor="middle">♑</text></svg></div>; }
function ProfileHeader({ context }: { context: Context }) { const moon = context.d1.planets.find((planet) => planet.body === "moon"); const name = context.birth_input.display_name?.trim() || "Your"; return <section className="profile-summary" aria-labelledby="profile-heading"><CelestialBackdrop compact /><div className="profile-intro"><span className="eyebrow">Your chart atlas</span><h2 id="profile-heading">{name}’s Vedic profile</h2><p className="profile-subtitle">A personal view of calculated chart facts and reviewed context.</p><details className="profile-private"><summary>View birth details</summary><p>{context.birth_input.birth_date} <span aria-hidden="true">·</span> {context.birth_input.birth_time.slice(0, 5)} <span aria-hidden="true">·</span> {context.birth_input.place_name || "Birthplace selected"}</p></details><div className="trust-marks"><TrustMark>Governed interpretation</TrustMark><TrustMark>Deterministic chart calculation</TrustMark></div></div><div className="profile-seal" aria-hidden="true"><span>✦</span><strong>{signGlyph(context.d1.ascendant?.sign)}</strong></div><div className="profile-facts"><Fact label="Ascendant" glyph={signGlyph(context.d1.ascendant?.sign)} value={titleCase(context.d1.ascendant?.sign ?? "—")} /><Fact label="Moon sign" glyph={signGlyph(moon?.sign)} value={titleCase(moon?.sign ?? "—")} /><Fact label="Mahadasha" glyph={planetGlyph(context.active_dasha.mahadasha.lord)} value={titleCase(context.active_dasha.mahadasha.lord)} /><Fact label="Antardasha" glyph={planetGlyph(context.active_dasha.antardasha.lord)} value={titleCase(context.active_dasha.antardasha.lord)} /></div></section>; }
function Fact({ label, glyph, value }: { label: string; glyph: string; value: string }) { return <article><span className="fact-glyph" aria-hidden="true">{glyph}</span><span>{label}</span><strong>{value}</strong></article>; }
function message(reason: unknown) { return reason instanceof Error ? reason.message : "The deterministic service is temporarily unavailable."; }
