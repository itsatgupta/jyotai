import type { Chart, House, Planet } from "../lib/contracts";
import { titleCase } from "../lib/format";
import "./kundli.css";

type Slot = { x: number; y: number; anchor?: "start" | "middle" | "end" };

// These are visual slots only. Every house number and sign is supplied by the API.
const slots: Record<number, Slot> = {
  1: { x: 200, y: 66 }, 2: { x: 95, y: 72 }, 3: { x: 38, y: 145 },
  4: { x: 83, y: 218 }, 5: { x: 92, y: 336 }, 6: { x: 200, y: 350 },
  7: { x: 305, y: 336 }, 8: { x: 362, y: 255 }, 9: { x: 362, y: 145 },
  10: { x: 306, y: 72 }, 11: { x: 200, y: 151 }, 12: { x: 200, y: 255 },
};

const abbreviation: Record<string, string> = {
  sun: "Su", moon: "Mo", mars: "Ma", mercury: "Me", jupiter: "Ju",
  venus: "Ve", saturn: "Sa", rahu: "Ra", ketu: "Ke",
};

function placementLabel(planet: Planet) {
  return `${titleCase(planet.body)}${planet.retrograde ? ", retrograde" : ""}`;
}

function HouseContents({ house, planets, isAscendant }: { house: House; planets: Planet[]; isAscendant: boolean }) {
  const slot = slots[house.number];
  return <g className="kundli-house" data-testid="kundli-house" transform={`translate(${slot.x} ${slot.y})`}>
    <text className="kundli-house-number" textAnchor="middle" y="0">{house.number}</text>
    <text className="kundli-sign" textAnchor="middle" y="15">{titleCase(house.sign).slice(0, 3)}</text>
    {isAscendant && <text className="kundli-ascendant" textAnchor="middle" y="29">ASC</text>}
    <g aria-label={`${isAscendant ? "Ascendant, " : ""}House ${house.number}, ${titleCase(house.sign)}${planets.length ? `: ${planets.map(placementLabel).join(", ")}` : ", empty"}`}>
      {planets.map((planet, index) => <text key={planet.body} className="kundli-planet" data-testid={`kundli-planet-${planet.body}`} textAnchor="middle" y={isAscendant ? 44 + index * 13 : 30 + index * 13}>
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
