import { useState } from "react";

import { NorthIndianChart } from "./NorthIndianChart";
import { planetGlyph, signGlyph } from "../lib/glyphs";
import type { Chart, Context, Planet } from "../lib/contracts";
import { titleCase } from "../lib/format";

const tabs = ["Overview", "D1", "D9", "D10", "Dasha", "Transits"] as const;
const chartInfo: Record<"D9" | "D10", { title: string; subtitle: string; info: string }> = {
  D9: { title: "D9 / Navamsha", subtitle: "Traditionally examined alongside D1 for marriage, dharma, and deeper assessment of planetary placements.", info: "Traditionally examined for marriage/dharma and complementary assessment of planetary condition." },
  D10: { title: "D10 / Dasamsha", subtitle: "Traditionally examined for profession, career, and public work.", info: "Traditionally used for profession/career/public work." },
};

export function Workspace({ context }: { context: Context }) {
  const [active, setActive] = useState<(typeof tabs)[number]>("Overview");
  return <section className="workspace" aria-labelledby="workspace-heading"><div className="workspace-title"><span className="eyebrow">Your chart</span><h2 id="workspace-heading">Horoscope workspace</h2><p>Factual placements, periods, and snapshots from your deterministic chart.</p></div><div className="tablist" role="tablist" aria-label="Astrology data">{tabs.map((tab) => <button key={tab} role="tab" aria-selected={active === tab} className={active === tab ? "active" : ""} onClick={() => setActive(tab)}>{tab}</button>)}</div><div className="tab-panel" role="tabpanel">
    {active === "Overview" && <div className="overview"><NorthIndianChart chart={context.d1} /><Dasha context={context} /></div>}
    {active === "D1" && <div className="overview"><NorthIndianChart chart={context.d1} /><ChartTable title="D1 planetary details" chart={context.d1} ascendant /></div>}
    {active === "D9" && <SecondaryChart chart={context.d9} chartKey="D9" />}
    {active === "D10" && <SecondaryChart chart={context.d10} chartKey="D10" />}
    {active === "Dasha" && <Dasha context={context} />}{active === "Transits" && <Transits context={context} />}
  </div></section>;
}

function SecondaryChart({ chart, chartKey }: { chart: Chart; chartKey: "D9" | "D10" }) { const info = chartInfo[chartKey]; return <article className="chart-card"><header><div><span className="eyebrow">Deterministic chart</span><h3>{info.title}</h3><p className="chart-subtitle">{info.subtitle}</p></div></header><ChartRows chart={chart} /><details className="chart-info"><summary>What is this chart used for?</summary><p>{info.info}</p></details></article>; }
function ChartTable({ title, chart, ascendant = false }: { title: string; chart: Chart; ascendant?: boolean }) { return <article className="chart-card"><header><div><span className="eyebrow">Deterministic chart</span><h3>{title}</h3></div>{ascendant && chart.ascendant && <p className="chart-ascendant"><span>{signGlyph(chart.ascendant.sign)}</span> Ascendant <strong>{titleCase(chart.ascendant.sign)} {degree(chart.ascendant.degree_in_sign)}</strong></p>}</header><ChartRows chart={chart} /></article>; }
function ChartRows({ chart }: { chart: Chart }) { return <div className="planet-table"><div className="planet-head" aria-hidden="true"><span>Body</span><span>Sign</span><span>House</span><span>Degree</span><span>Nakshatra</span><span>Motion</span></div>{chart.planets.map((planet) => <PlanetRow key={planet.body} planet={planet} />)}</div>; }
function PlanetRow({ planet }: { planet: Planet }) { return <article className="planet-row"><span className="body"><i aria-hidden="true">{planetGlyph(planet.body)}</i><strong>{titleCase(planet.body)}</strong></span><span><i aria-hidden="true">{signGlyph(planet.sign)}</i>{titleCase(planet.sign)}</span><span data-label="House">{planet.house_number ?? "—"}</span><span data-label="Degree">{degree(planet.degree_in_sign)}</span><span data-label="Nakshatra">{planet.nakshatra ? `${titleCase(planet.nakshatra.nakshatra)} · Pada ${planet.nakshatra.pada}` : "—"}</span><span data-label="Motion"><b className={planet.retrograde ? "motion retrograde" : "motion"}>{planet.retrograde ? "Retrograde" : "Direct"}</b></span></article>; }
function Dasha({ context }: { context: Context }) { const dasha = context.active_dasha; return <article className="dasha-section"><header><div><span className="eyebrow">Vimshottari</span><h3>Active Dasha</h3></div><p>Snapshot {dateOnly(dasha.instant)}</p></header><div className="dasha-grid"><Period title="Current Mahadasha" period={dasha.mahadasha} /><Period title="Current Antardasha" period={dasha.antardasha} /></div></article>; }
function Period({ title, period }: { title: string; period: { lord: string; start: string; end: string } }) { return <article className="period"><span>{title}</span><div><i aria-hidden="true">{planetGlyph(period.lord)}</i><strong>{titleCase(period.lord)}</strong></div><div className="timeline" aria-hidden="true"><span /></div><p><time dateTime={period.start}>{dateOnly(period.start)}</time><b aria-hidden="true">→</b><time dateTime={period.end}>{dateOnly(period.end)}</time></p></article>; }
function Transits({ context }: { context: Context }) { const snapshot = context.transit_snapshot; return <article className="transit-section"><header><div><span className="eyebrow">Transit snapshot</span><h3>As-of transits</h3></div><p>{dateOnly(snapshot.normalized_utc_instant)}</p></header><div className="transit-grid">{snapshot.positions.map((planet) => <article className="transit" key={planet.body}><i aria-hidden="true">{planetGlyph(planet.body)}</i><strong>{titleCase(planet.body === "rahu" ? "True Rahu" : planet.body)}</strong><span>{signGlyph(planet.sign)} {titleCase(planet.sign)} · {degree(planet.degree_in_sign)}</span><small>{titleCase(planet.nakshatra)} · Pada {planet.pada}</small><b className={planet.retrograde ? "motion retrograde" : "motion"}>{planet.retrograde ? "Retrograde" : "Direct"}</b></article>)}</div></article>; }
const degree = (value: string | number) => `${Number(value).toFixed(2)}°`;
const dateOnly = (value: string) => new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(value));
