import { useState } from "react";
import type { Chart, Context, Planet } from "../lib/contracts";
import { titleCase } from "../lib/format";

const tabs = ["Overview", "D1", "D9", "D10", "Dasha", "Transits"] as const;

export function Workspace({ context }: { context: Context }) {
  const [active, setActive] = useState<(typeof tabs)[number]>("Overview");
  return <section className="workspace" aria-label="Astrology workspace">
    <div className="tablist" role="tablist" aria-label="Astrology data">
      {tabs.map((tab) => <button key={tab} role="tab" aria-selected={active === tab} className={active === tab ? "active" : ""} onClick={() => setActive(tab)}>{tab}</button>)}
    </div>
    <div className="tab-panel" role="tabpanel">
      {active === "Overview" && <Overview context={context} />}
      {active === "D1" && <ChartTable title="D1 / Rashi" chart={context.d1} ascendant />}
      {active === "D9" && <ChartTable title="D9 / Navamsa" chart={context.d9} />}
      {active === "D10" && <ChartTable title="D10 / Dasamsa" chart={context.d10} />}
      {active === "Dasha" && <Dasha context={context} />}
      {active === "Transits" && <Transits context={context} />}
    </div>
  </section>;
}

function Overview({ context }: { context: Context }) { return <div className="overview"><ChartTable title="D1 / Rashi" chart={context.d1} ascendant /><Dasha context={context} /></div>; }
function ChartTable({ title, chart, ascendant = false }: { title: string; chart: Chart; ascendant?: boolean }) {
  return <article className="data-card"><div className="section-heading"><div><div className="eyebrow">Deterministic chart</div><h2>{title}</h2></div>{ascendant && chart.ascendant && <div className="ascendant"><span>Ascendant</span><strong>{titleCase(chart.ascendant.sign)} {degree(chart.ascendant.degree_in_sign)}</strong></div>}</div><div className="table-wrap"><table><thead><tr><th>Body</th><th>Sign</th><th>House</th><th>Degree</th><th>Nakshatra</th><th>Motion</th></tr></thead><tbody>{chart.planets.map((planet) => <PlanetRow key={planet.body} planet={planet} />)}</tbody></table></div></article>;
}
function PlanetRow({ planet }: { planet: Planet }) { return <tr><td>{titleCase(planet.body)}</td><td>{titleCase(planet.sign)}</td><td>{planet.house_number ?? "—"}</td><td>{degree(planet.degree_in_sign)}</td><td>{planet.nakshatra ? `${titleCase(planet.nakshatra.nakshatra)} · Pada ${planet.nakshatra.pada}` : "—"}</td><td>{planet.retrograde ? "Retrograde" : "Direct"}</td></tr>; }
function Dasha({ context }: { context: Context }) { const dasha = context.active_dasha; return <article className="data-card"><div className="section-heading"><div><div className="eyebrow">Vimshottari</div><h2>Active Dasha</h2></div><span className="muted">Snapshot {formatDate(dasha.instant)}</span></div><div className="dasha-grid"><Period title="Current Mahadasha" period={dasha.mahadasha} /><Period title="Current Antardasha" period={dasha.antardasha} /></div></article>; }
function Period({ title, period }: { title: string; period: { lord: string; start: string; end: string } }) { return <div className="period"><span>{title}</span><strong>{titleCase(period.lord)}</strong><small>Start {formatDate(period.start)}</small><small>End {formatDate(period.end)}</small></div>; }
function Transits({ context }: { context: Context }) { return <article className="data-card"><div className="section-heading"><div><div className="eyebrow">Transit-v1</div><h2>As-of transits</h2></div><span className="muted">{formatDate(context.transit_snapshot.normalized_utc_instant)}</span></div><div className="transit-grid">{context.transit_snapshot.positions.map((planet) => <div className="transit" key={planet.body}><strong>{titleCase(planet.body)}</strong><span>{titleCase(planet.sign)} · {degree(planet.degree_in_sign)}</span><small>{planet.nakshatra ? `${titleCase(planet.nakshatra.nakshatra)} · Pada ${planet.nakshatra.pada}` : "—"}</small><small>{planet.retrograde ? "Retrograde" : "Direct"}{planet.motion_speed ? ` · ${planet.motion_speed}°/day` : ""}</small></div>)}</div></article>; }
const degree = (value: string | number) => `${Number(value).toFixed(2)}°`;
const formatDate = (value: string) => new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
