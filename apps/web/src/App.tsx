import { useState } from "react";

import { BirthProfile } from "./components/BirthProfile";
import { QuestionAnalysis } from "./components/QuestionAnalysis";
import { Workspace } from "./components/Workspace";
import { api } from "./lib/api";
import type { AnalysisResult, BirthInput, Context } from "./lib/contracts";
import { titleCase } from "./lib/format";
import { planetGlyph, signGlyph } from "./lib/glyphs";

export default function App() {
  const [context, setContext] = useState<Context | null>(null);
  const [birth, setBirth] = useState<BirthInput | null>(null);
  const [asOf, setAsOf] = useState("");
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState<"profile" | "question" | null>(null);
  const [error, setError] = useState("");
  async function createProfile(input: BirthInput, instant: string) { setLoading("profile"); setError(""); setAnalysis(null); try { setContext(await api.context(input, instant)); setBirth(input); setAsOf(instant); } catch (reason) { setError(message(reason)); } finally { setLoading(null); } }
  async function analyze(question: string) { if (!birth || !asOf) return; setLoading("question"); setError(""); try { const result = await api.analyze({ birth_input: birth, as_of: asOf, question }); setAnalysis(result); setContext(result.context); } catch (reason) { setError(message(reason)); } finally { setLoading(null); } }
  return <main>
    <header className="site-header"><a className="wordmark" href="#top" aria-label="JyotAI home">Jyot<span>AI</span></a><nav aria-label="Main navigation"><a href="#birth-profile">Birth profile</a><a href="#ask-jyotai">Ask JyotAI</a></nav><span className="header-method">Sidereal Vedic astrology</span></header>
    <Hero />
    <div className="shell">{error && <div className="notice error" role="alert"><strong>We couldn’t complete that request.</strong><span>{error}</span></div>}<BirthProfile onSubmit={createProfile} loading={loading === "profile"} />{context && <><ProfileHeader context={context} /><Workspace context={context} /><QuestionAnalysis result={analysis} onAnalyze={analyze} loading={loading === "question"} /></>}</div>
    <footer className="site-footer"><span>JyotAI</span><p>Sidereal Vedic methodology · Lahiri ayanamsa · Deterministic calculations</p></footer>
  </main>;
}

function Hero() { return <section className="hero" id="top"><div className="hero-copy"><span className="eyebrow">Vedic astrology, thoughtfully made</span><h1>Your Vedic Astrology, <em>intelligently decoded.</em></h1><p>Build a precise sidereal chart from your birth details, then explore its deterministic facts and governed evidence with clarity.</p><div className="hero-actions"><a className="button primary" href="#birth-profile">Create My Horoscope</a><a className="button secondary" href="#ask-jyotai">Ask JyotAI</a></div><p className="trust-line">Sidereal <i>·</i> Lahiri ayanamsa <i>·</i> Deterministic calculations</p></div><CelestialVisual /></section>; }
function CelestialVisual() { return <div className="celestial" aria-hidden="true"><span className="star s1" /><span className="star s2" /><span className="star s3" /><svg viewBox="0 0 500 500" focusable="false"><circle cx="250" cy="250" r="190" className="orbit outer" /><circle cx="250" cy="250" r="140" className="orbit" /><circle cx="250" cy="250" r="84" className="orbit" /><path className="mandala" d="M250 55v390M55 250h390M112 112l276 276M388 112L112 388" /><circle cx="250" cy="250" r="38" className="sun" /><text x="250" y="267" textAnchor="middle">☉</text><text x="250" y="89" textAnchor="middle">♈</text><text x="411" y="257" textAnchor="middle">♋</text><text x="250" y="427" textAnchor="middle">♎</text><text x="89" y="257" textAnchor="middle">♑</text></svg></div>; }
function ProfileHeader({ context }: { context: Context }) { const moon = context.d1.planets.find((planet) => planet.body === "moon"); const name = context.birth_input.display_name?.trim() || "Your"; return <section className="profile-summary" aria-labelledby="profile-heading"><div className="profile-intro"><span className="eyebrow">Personal astrology summary</span><h2 id="profile-heading">{name.toUpperCase()}’S ASTROLOGY PROFILE</h2><p>{context.birth_input.place_name || "Birthplace selected"} <span aria-hidden="true">·</span> Calculated as of {dateOnly(context.requested_as_of)}</p></div><div className="profile-seal" aria-hidden="true"><span>✦</span><strong>{signGlyph(context.d1.ascendant?.sign)}</strong></div><div className="profile-facts"><Fact label="Ascendant" glyph={signGlyph(context.d1.ascendant?.sign)} value={titleCase(context.d1.ascendant?.sign ?? "—")} /><Fact label="Moon sign" glyph={signGlyph(moon?.sign)} value={titleCase(moon?.sign ?? "—")} /><Fact label="Mahadasha" glyph={planetGlyph(context.active_dasha.mahadasha.lord)} value={titleCase(context.active_dasha.mahadasha.lord)} /><Fact label="Antardasha" glyph={planetGlyph(context.active_dasha.antardasha.lord)} value={titleCase(context.active_dasha.antardasha.lord)} /></div></section>; }
function Fact({ label, glyph, value }: { label: string; glyph: string; value: string }) { return <article><span className="fact-glyph" aria-hidden="true">{glyph}</span><span>{label}</span><strong>{value}</strong></article>; }
function dateOnly(value: string) { return new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(value)); }
function message(reason: unknown) { return reason instanceof Error ? reason.message : "The deterministic service is temporarily unavailable."; }
