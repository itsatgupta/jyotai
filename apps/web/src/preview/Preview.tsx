import { useState } from "react";
import { OrbitArtwork } from "../components/OrbitArtwork";
import { northIndianHouseSlots } from "../components/northIndianHouseSlots";
import "./preview.css";

type PlanetName = "Sun" | "Moon" | "Mars" | "Mercury" | "Jupiter" | "Venus" | "Saturn" | "Rahu" | "Ketu";
type SamplePlanet = { name: PlanetName; glyph: string; house: number; tone: string; note: string };

// Deliberately synthetic display data. The preview never presents these as a calculated chart.
const signs = ["Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces", "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo"];
const planets: SamplePlanet[] = [
  { name: "Sun", glyph: "☉", house: 7, tone: "saffron", note: "Aries · House 7" },
  { name: "Moon", glyph: "☽", house: 4, tone: "lilac", note: "Capricorn · House 4" },
  { name: "Mars", glyph: "♂", house: 9, tone: "coral", note: "Gemini · House 9" },
  { name: "Mercury", glyph: "☿", house: 7, tone: "teal", note: "Aries · House 7" },
  { name: "Jupiter", glyph: "♃", house: 5, tone: "gold", note: "Aquarius · House 5" },
  { name: "Venus", glyph: "♀", house: 1, tone: "rose", note: "Libra · House 1" },
  { name: "Saturn", glyph: "♄", house: 3, tone: "blue", note: "Sagittarius · House 3" },
  { name: "Rahu", glyph: "☊", house: 10, tone: "violet", note: "Cancer · House 10" },
  { name: "Ketu", glyph: "☋", house: 4, tone: "mint", note: "Capricorn · House 4" },
];
const planetShort: Record<PlanetName, string> = { Sun: "Su", Moon: "Mo", Mars: "Ma", Mercury: "Me", Jupiter: "Ju", Venus: "Ve", Saturn: "Sa", Rahu: "Ra", Ketu: "Ke" };


function Kundli({ selected, onSelect }: { selected: PlanetName | null; onSelect: (name: PlanetName | null) => void }) {
  return <div className="preview-kundli-wrap">
    <svg className="preview-kundli" viewBox="0 0 400 400" role="img" aria-label="North Indian D1 chart layout. Synthetic sample: Libra ascendant, signs proceed by house, planet placements are illustrative." preserveAspectRatio="xMidYMid meet">
      <rect x="4" y="4" width="392" height="392" rx="7" className="pk-frame"/>
      <rect x="11" y="11" width="378" height="378" rx="3" className="pk-inner-frame"/>
      <path d="M4 4 200 200 396 4M396 4 200 200 396 396M396 396 200 200 4 396M4 396 200 200 4 4M4 200 200 4M200 4 396 200M396 200 200 396M200 396 4 200" className="pk-lines"/>
      {signs.map((sign, index) => {
        const house = index + 1;
        const slot = northIndianHouseSlots[house];
        const placed = planets.filter((planet) => planet.house === house);
        const active = selected !== null && placed.some((planet) => planet.name === selected);
        return <g key={house} className={`pk-house ${active ? "pk-house-active" : ""}`}>
          <title>House {house}, {sign}{placed.length ? `: ${placed.map((planet) => planet.name).join(", ")}` : ": no sample planets"}</title>
          <text x={slot.signAnchor.x} y={slot.signAnchor.y} textAnchor="middle" className="pk-sign-number">{((6 + index) % 12) + 1}</text>
          <text x={slot.signAnchor.x} y={slot.signAnchor.y + 16} textAnchor="middle" className="pk-sign-name">{sign.slice(0, 3).toUpperCase()}</text>
          {house === 1 && <text x={slot.signAnchor.x} y={slot.signAnchor.y + 30} textAnchor="middle" className="pk-asc">ASC</text>}
          {placed.map((planet, planetIndex) => <g key={planet.name}>{selected === planet.name && <circle cx={slot.planetAnchor.x} cy={slot.planetAnchor.y + planetIndex * 15 - 4} r="16" className="pk-selection-halo"/>}<text x={slot.planetAnchor.x} y={slot.planetAnchor.y + planetIndex * 15} textAnchor="middle" className={`pk-planet pk-${planet.tone} ${selected === planet.name ? "pk-selected" : ""}`}>{planetShort[planet.name]}</text></g>)}
        </g>;
      })}
    </svg>
    <div className="kundli-controls"><span>Houses fixed · signs and planets synthetic</span><button type="button" onClick={() => onSelect(null)} disabled={selected === null}>Clear selection</button></div>
  </div>;
}

export default function Preview() {
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [selected, setSelected] = useState<PlanetName | null>(null);
  const [question, setQuestion] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const selectedPlanet = planets.find((planet) => planet.name === selected);
  return <div className="preview-app" data-preview-theme={theme}>
    <a className="preview-skip" href="#preview-overview">Skip to overview</a>
    <aside className="preview-sidebar" aria-label="Preview navigation">
      <a className="preview-brand" href="#preview-top" aria-label="JyotishAI preview home"><span className="brand-sigil">✦</span><span>Jyotish<span>AI</span><small>CELESTIAL ATLAS</small></span></a>
      <div className="sidebar-caption">YOUR SPACE</div>
      <nav className="sidebar-nav" aria-label="Dashboard sections">
        <a href="#preview-overview" className="nav-selected"><span>◈</span> Overview</a>
        <a href="#preview-chart"><span>◇</span> Birth chart</a>
        <a href="#preview-planets"><span>✶</span> Planets</a>
        <a href="#preview-dasha"><span>◷</span> Dasha cycles</a>
        <a href="#preview-consult"><span>✧</span> Ask JyotishAI</a>
      </nav>
      <div className="sidebar-divider" />
      <div className="sidebar-caption">DESIGN PREVIEW</div>
      <p className="sidebar-note">A visual direction using synthetic sample data. No chart has been calculated.</p>
      <div className="sidebar-bottom"><div className="sidebar-avatar">S</div><div><strong>Sample profile</strong><span>Illustrative workspace</span></div><span aria-hidden="true">⌄</span></div>
    </aside>

    <div className="preview-main" id="preview-top">
      <header className="preview-topbar"><div className="topbar-trail">PERSONAL ATLAS <span>/</span> OVERVIEW</div><div className="topbar-actions"><span className="demo-pill"><span /> SYNTHETIC SAMPLE</span><button type="button" className="theme-button" onClick={() => setTheme(theme === "dark" ? "light" : "dark")} aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}><span aria-hidden="true">{theme === "dark" ? "☀" : "☾"}</span><span>{theme === "dark" ? "Light" : "Dark"}</span></button></div></header>

      <div className="preview-content">
        <section className="preview-hero" id="preview-overview" aria-labelledby="preview-heading"><div className="hero-stars" aria-hidden="true"/><div className="hero-copy"><div className="hero-kicker"><span className="kicker-star">✦</span> THE ART OF SEEING CLEARLY</div><h1 id="preview-heading">A universe,<br/><em>uniquely yours.</em></h1><p>A luminous home for the geometry of your chart, the rhythm of planetary periods, and questions worth exploring with care.</p><div className="hero-cta"><a href="#preview-chart" className="gold-button">Explore the sample chart <span>↗</span></a><span>Vedic astrology · clear by design</span></div></div><div className="hero-art"><OrbitArtwork/><div className="orbit-caption">ZODIAC ARTWORK · DECORATIVE ONLY</div></div><div className="hero-corner">✦ <span>AS ABOVE<br/>SO BELOW</span></div></section>

        <section className="profile-strip" aria-label="Synthetic sample birth profile"><div className="profile-identity"><div className="profile-monogram">S<span>✦</span></div><div><span className="section-kicker">THE BIRTH PROFILE</span><h2>Sample profile</h2><p>Illustrative details · no birth record</p></div></div><div className="profile-stat"><span>ASCENDANT <i>✦</i></span><strong><b>♎</b> Libra</strong><small>Synthetic chart example</small></div><div className="profile-stat"><span>MOON SIGN <i>✦</i></span><strong><b>♑</b> Capricorn</strong><small>Synthetic chart example</small></div><div className="profile-stat"><span>CHART METHOD</span><strong>Sidereal · D1</strong><small>Lahiri · North Indian</small></div></section>

        <div className="section-title" id="preview-chart"><div><span className="section-kicker">01 / THE FOUNDATION</span><h2>Your sky, <em>mapped beautifully.</em></h2><p>Explore the traditional North Indian D1 layout. House positions stay fixed while signs and sample planets appear inside them.</p></div><span className="section-aside">ILLUSTRATIVE PLACEMENTS <i>✧</i> NO CALCULATION</span></div>
        <section className="chart-section" aria-label="Sample Kundli and selected planet"><div className="chart-card"><div className="card-top"><div><span className="section-kicker">THE NATAL MAP</span><h3>D1 · Rashi Kundli</h3></div><span className="chart-badge">◇ SAMPLE CHART</span></div><Kundli selected={selected} onSelect={setSelected}/><div className="chart-footer"><span>◇</span><p>Traditional fixed house geometry. Zodiac numerals and planet abbreviations belong to this synthetic demonstration only.</p></div></div><div className="chart-side"><div className="insight-panel"><div className="insight-flare">✧</div><span className="section-kicker">A CLOSER LOOK</span><div aria-live="polite" aria-atomic="true"><h3>{selectedPlanet ? selectedPlanet.name : "The chart comes alive."}</h3><p>{selectedPlanet ? `${selectedPlanet.note} in this synthetic sample. Select another planet to locate its house in the D1 chart.` : "Select a planet card to illuminate its house in the Kundli. The chart and cards are linked for easy reading."}</p></div><div className="insight-divider"/><div className="insight-fact"><span>HOUSE IN FOCUS</span><strong>{selectedPlanet ? String(selectedPlanet.house).padStart(2, "0") : "—"}</strong></div><div className="insight-fact"><span>DISPLAY STATUS</span><strong>Illustrative</strong></div></div><div className="method-card"><span className="method-icon">✦</span><div><strong>Crafted for clarity</strong><p>Artwork is decorative. Only the outlined D1 panel represents chart structure. Live calculation and interpretations are outside this preview.</p></div></div></div></section>

        <div className="section-title compact-title" id="preview-planets"><div><span className="section-kicker">02 / CELESTIAL BODIES</span><h2>Meet the <em>planetary cast.</em></h2><p>Color, symbol, and house location make a dense chart easier to scan.</p></div><span className="section-aside">SELECT A CARD TO HIGHLIGHT ITS HOUSE ↘</span></div>
        <section className="planet-grid" aria-label="Synthetic sample planets">{planets.map((planet) => <button type="button" key={planet.name} className={`planet-card tone-${planet.tone} ${selected === planet.name ? "planet-card-selected" : ""}`} onClick={() => { setSelected(planet.name); document.getElementById("preview-chart")?.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth", block: "start" }); }} aria-pressed={selected === planet.name} aria-controls="preview-chart" aria-label={`${planet.name}, synthetic ${planet.note}; highlight in chart`}><span className="planet-orbit" aria-hidden="true"><span>{planet.glyph}</span></span><span className="planet-card-copy"><small>HOUSE {String(planet.house).padStart(2, "0")}</small><strong>{planet.name}</strong><span>{planet.note.split(" · ")[0]}</span></span><span className="planet-arrow" aria-hidden="true">↗</span></button>)}</section>

        <section className="dasha-section" id="preview-dasha" aria-labelledby="dasha-heading"><div className="dasha-heading"><div><span className="section-kicker">03 / THE RHYTHM OF TIME</span><h2 id="dasha-heading">Life in <em>planetary chapters.</em></h2><p>A visual treatment for Mahadasha and Antardasha. Periods shown here are layout examples only; no dates or active period are asserted.</p></div><span className="dasha-mark" aria-hidden="true">◷</span></div><div className="dasha-body"><div className="dasha-label"><span>MAHADASHA / SAMPLE SEQUENCE</span><strong>Major periods</strong></div><ol className="dasha-track" aria-label="Illustrative Mahadasha order. No dates, durations, or current period shown"><li className="dasha-node node-jupiter"><span aria-hidden="true">♃</span><div><small>MD · 01</small><strong>Jupiter</strong></div></li><li className="dasha-node node-saturn"><span aria-hidden="true">♄</span><div><small>MD · 02</small><strong>Saturn</strong></div></li><li className="dasha-node node-mercury"><span aria-hidden="true">☿</span><div><small>MD · 03</small><strong>Mercury</strong></div></li></ol><div className="dasha-label lower"><span>ANTARDASHA / EXAMPLE NAMES</span><strong>Subperiods within an MD</strong></div><ol className="antardasha-track" aria-label="Illustrative Antardasha order. No dates, durations, or parent Mahadasha implied">{["Jupiter", "Saturn", "Mercury", "Ketu", "Venus"].map((name, index) => <li key={name}><small>AD · {String(index + 1).padStart(2, "0")}</small><i aria-hidden="true">{["♃", "♄", "☿", "☋", "♀"][index]}</i><strong>{name}</strong></li>)}</ol><div className="dasha-disclaimer">✦ <span>Sequence is illustrative and spacing does not represent duration or progress. Actual intervals require deterministic birth data calculations.</span></div></div></section>

        <section className="consult-section" id="preview-consult" aria-labelledby="consult-heading"><div className="consult-copy"><span className="section-kicker">04 / A THOUGHTFUL CONVERSATION</span><h2 id="consult-heading">Ask with curiosity.<br/><em>Read with clarity.</em></h2><p>A clear answer separates what the sample chart displays from what can responsibly be interpreted. Explore the format below; it is not a reading.</p><div className="consult-art" aria-hidden="true"><span>✧</span><span>☾</span><span>✦</span></div></div><div className="consult-stack"><div className="consult-card"><div className="consult-card-head"><div className="consult-avatar" aria-hidden="true">✦</div><div><strong>JyotishAI consultation</strong><span>Evidence-led answers in the live experience</span></div><span className="consult-status">PREVIEW</span></div><label htmlFor="sample-question">What would you like to explore?</label><textarea id="sample-question" value={question} onChange={(event) => { setQuestion(event.target.value); setSubmitted(false); }} placeholder="Ask a focused question about your chart…" rows={4}/><div className="question-suggestions"><span>TRY A QUESTION</span>{["What does my D1 chart show?", "How do Dasha periods work?"].map((prompt) => <button type="button" key={prompt} onClick={() => { setQuestion(prompt); setSubmitted(false); }}>{prompt}</button>)}</div><div className="consult-action"><span>✧ No question leaves this preview</span><button type="button" onClick={() => setSubmitted(true)} disabled={!question.trim()}>Preview question <b>↗</b></button></div>{submitted && <p className="consult-feedback" role="status">Question staged for visual review. No analysis was generated or sent.</p>}</div><article className="answer-preview" aria-labelledby="answer-preview-heading"><div className="answer-preview-top"><span className="section-kicker">ANSWER COMPOSITION</span><span>STATIC FORMAT EXAMPLE</span></div><h3 id="answer-preview-heading">From chart detail to clear context</h3><div className="answer-part"><span className="answer-part-icon">01</span><div><h4>Chart facts</h4><p>In this synthetic display, Libra is shown in the first house and Venus is placed there. These are sample placements, not a calculated birth chart.</p></div></div><div className="answer-part"><span className="answer-part-icon">02</span><div><h4>Interpretation</h4><p>A live answer would connect relevant chart factors to a specific question, explain competing indications, and label the strength of each indication. No conclusion is offered for this sample.</p></div></div><div className="answer-part answer-limit"><span className="answer-part-icon">03</span><div><h4>Limits &amp; timing</h4><p>Birth details, verified calculations, and evidence are required before chart interpretation or timing. Astrology is not scientific certainty.</p></div></div><details className="answer-evidence"><summary>View example evidence structure <span aria-hidden="true">⌄</span></summary><div><p><strong>Method</strong> · Vedic / sidereal / Lahiri / Vimshottari</p><p><strong>Displayed facts</strong> · Libra ascendant; Venus in house 1 (synthetic)</p><p><strong>Unavailable</strong> · verified birth data, calculated Dasha intervals, interpretation rules, and timing evidence</p></div></details></article></div></section>
        <footer className="preview-footer"><span>✦ JyotishAI</span><p>Design prototype · synthetic content · Vedic / sidereal / Lahiri / Vimshottari</p><a href="/">Return to current app ↗</a></footer>
      </div>
    </div>
  </div>;
}
