import type { Chart, House, Planet } from "../lib/contracts";
import { titleCase } from "../lib/format";
import { northIndianHouseSlots, zodiacSignNumber } from "./northIndianHouseSlots";
import "./kundli.css";

const abbreviation: Record<string, string> = {
  sun: "Su", moon: "Mo", mars: "Ma", mercury: "Me", jupiter: "Ju",
  venus: "Ve", saturn: "Sa", rahu: "Ra", ketu: "Ke",
};

function placementLabel(planet: Planet) {
  return `${titleCase(planet.body)}${planet.retrograde ? ", retrograde" : ""}`;
}

function HouseContents({ house, planets, isAscendant }: { house: House; planets: Planet[]; isAscendant: boolean }) {
  const slot = northIndianHouseSlots[house.number];
  return <g className="kundli-house" data-testid="kundli-house" data-house-number={house.number}>
    <g data-testid={`kundli-house-label-${house.number}`} transform={`translate(${slot.signAnchor.x} ${slot.signAnchor.y})`}>
      <text className="kundli-house-number" textAnchor="middle" y="0">{zodiacSignNumber(house.sign)}</text>
      <text className="kundli-sign" textAnchor="middle" y="15">{titleCase(house.sign).slice(0, 3)}</text>
      {isAscendant && <text className="kundli-ascendant" textAnchor="middle" y="29">ASC</text>}
    </g>
    <g data-testid={`kundli-planets-house-${house.number}`} transform={`translate(${slot.planetAnchor.x} ${slot.planetAnchor.y})`} aria-label={`${isAscendant ? "Ascendant, " : ""}House ${house.number}, ${titleCase(house.sign)}${planets.length ? `: ${planets.map(placementLabel).join(", ")}` : ", empty"}`}>
      {planets.map((planet, index) => <text key={planet.body} className="kundli-planet" data-testid={`kundli-planet-${planet.body}`} textAnchor="middle" y={index * 13}>
        <title>{placementLabel(planet)}</title>{abbreviation[planet.body] ?? titleCase(planet.body).slice(0, 2)}{planet.retrograde ? " ℞" : ""}
      </text>)}
    </g>
  </g>;
}

export function NorthIndianChart({ chart, title = "Lagna / Rashi Chart (D1)" }: { chart: Chart; title?: string }) {
  const planetsByHouse = new Map<number, Planet[]>();
  chart.planets.forEach((planet) => {
    const planets = planetsByHouse.get(planet.house_number) ?? [];
    planets.push(planet);
    planetsByHouse.set(planet.house_number, planets);
  });
  const houses = [...chart.houses].sort((left, right) => left.number - right.number);
  return <article className="kundli-card" aria-labelledby="kundli-title">
    <header><div><span className="eyebrow">Primary natal chart</span><h3 id="kundli-title">{title}</h3><p>The primary natal chart used to examine the overall structure of the horoscope, including houses, signs, planets, and major life themes.</p></div></header>
    <svg className="north-indian-chart" viewBox="0 0 400 400" role="img" aria-label="North Indian style Lagna Kundli. All labels use supplied backend house and sign placements." preserveAspectRatio="xMidYMid meet">
      <rect x="4" y="4" width="392" height="392" rx="3" className="kundli-outline" />
      <path className="kundli-lines" d="M4 4 200 200 396 4M396 4 200 200 396 396M396 396 200 200 4 396M4 396 200 200 4 4M4 200 200 4M200 4 396 200M396 200 200 396M200 396 4 200" />
      {houses.map((house) => <HouseContents key={house.number} house={house} planets={planetsByHouse.get(house.number) ?? []} isAscendant={house.number === 1} />)}
    </svg>
    <details className="chart-info"><summary>What is this chart used for?</summary><p>Primary natal chart; overall horoscope framework, houses, signs, planets, personality and major life areas.</p></details>
  </article>;
}
