import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { NorthIndianChart } from "./NorthIndianChart";
import type { Chart, Planet } from "../lib/contracts";

const signs = ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"];
type Anchor = { x: number; y: number };
type ExpectedAnchors = { sign: Anchor; planets: Anchor };

// Independently reviewed against the SVG path, rather than imported from the
// renderer's geometry module. Each point must lie inside its fixed house polygon.
const expectedAnchors: Record<number, ExpectedAnchors> = {
  1: { sign: { x: 200, y: 58 }, planets: { x: 200, y: 135 } },
  2: { sign: { x: 95, y: 28 }, planets: { x: 100, y: 61 } },
  3: { sign: { x: 28, y: 90 }, planets: { x: 48, y: 130 } },
  4: { sign: { x: 50, y: 200 }, planets: { x: 125, y: 200 } },
  5: { sign: { x: 28, y: 270 }, planets: { x: 45, y: 310 } },
  6: { sign: { x: 100, y: 354 }, planets: { x: 105, y: 335 } },
  7: { sign: { x: 200, y: 350 }, planets: { x: 200, y: 260 } },
  8: { sign: { x: 300, y: 354 }, planets: { x: 295, y: 335 } },
  9: { sign: { x: 372, y: 270 }, planets: { x: 350, y: 310 } },
  10: { sign: { x: 350, y: 200 }, planets: { x: 275, y: 200 } },
  11: { sign: { x: 372, y: 90 }, planets: { x: 350, y: 130 } },
  12: { sign: { x: 300, y: 28 }, planets: { x: 300, y: 61 } },
};

const polygons: Record<number, Anchor[]> = {
  1: [{ x: 200, y: 4 }, { x: 298, y: 102 }, { x: 200, y: 200 }, { x: 100, y: 100 }],
  2: [{ x: 4, y: 4 }, { x: 200, y: 4 }, { x: 100, y: 100 }],
  3: [{ x: 4, y: 4 }, { x: 100, y: 100 }, { x: 4, y: 200 }],
  4: [{ x: 4, y: 200 }, { x: 100, y: 100 }, { x: 200, y: 200 }, { x: 102, y: 298 }],
  5: [{ x: 4, y: 200 }, { x: 102, y: 298 }, { x: 4, y: 396 }],
  6: [{ x: 4, y: 396 }, { x: 102, y: 298 }, { x: 200, y: 396 }],
  7: [{ x: 102, y: 298 }, { x: 200, y: 200 }, { x: 298, y: 298 }, { x: 200, y: 396 }],
  8: [{ x: 200, y: 396 }, { x: 298, y: 298 }, { x: 396, y: 396 }],
  9: [{ x: 396, y: 200 }, { x: 298, y: 298 }, { x: 396, y: 396 }],
  10: [{ x: 298, y: 102 }, { x: 396, y: 200 }, { x: 298, y: 298 }, { x: 200, y: 200 }],
  11: [{ x: 396, y: 4 }, { x: 396, y: 200 }, { x: 298, y: 102 }],
  12: [{ x: 200, y: 4 }, { x: 396, y: 4 }, { x: 298, y: 102 }],
};

function planet(body: string, house_number: number, retrograde = false, sign = signs[house_number - 1]): Planet {
  return { body, sign, degree_in_sign: 0, house_number, retrograde };
}

function chart(planets: Planet[], houseSigns = signs): Chart {
  return {
    methodology: { chart_type: "D1/Rashi" },
    ascendant: { sign: houseSigns[0], degree_in_sign: 0, nakshatra: { nakshatra: "ashwini", pada: 1 } },
    houses: houseSigns.map((sign, index) => ({ number: index + 1, sign })),
    planets,
  };
}

function houseElement(house: number): HTMLElement {
  const element = screen.getAllByTestId("kundli-house").find((candidate) => candidate.getAttribute("data-house-number") === String(house));
  if (!element) throw new Error(`House ${house} was not rendered`);
  return element;
}

function isInsidePolygon(point: Anchor, polygon: Anchor[]): boolean {
  let inside = false;
  for (let index = 0, previous = polygon.length - 1; index < polygon.length; previous = index++) {
    const current = polygon[index];
    const prior = polygon[previous];
    if ((current.y > point.y) !== (prior.y > point.y) && point.x < ((prior.x - current.x) * (point.y - current.y)) / (prior.y - current.y) + current.x) inside = !inside;
  }
  return inside;
}

describe("NorthIndianChart", () => {
  it("places H1-H12 in distinct fixed SVG polygons with separate sign and planet anchors", () => {
    render(<NorthIndianChart chart={chart(Array.from({ length: 12 }, (_, index) => planet(`h${index + 1}`, index + 1)))} />);

    for (let house = 1; house <= 12; house += 1) {
      const anchors = expectedAnchors[house];
      expect(screen.getByTestId(`kundli-house-label-${house}`)).toHaveAttribute("transform", `translate(${anchors.sign.x} ${anchors.sign.y})`);
      expect(screen.getByTestId(`kundli-planets-house-${house}`)).toHaveAttribute("transform", `translate(${anchors.planets.x} ${anchors.planets.y})`);
      expect(isInsidePolygon(anchors.sign, polygons[house])).toBe(true);
      expect(isInsidePolygon(anchors.planets, polygons[house])).toBe(true);
      expect(screen.getByTestId(`kundli-planet-h${house}`).parentElement?.parentElement).toBe(houseElement(house));
    }
  });

  it("uses house number for the requested placements and preserves sign content", () => {
    render(<NorthIndianChart chart={chart([
      planet("sun", 6, false, "aries"), planet("mercury", 6, false, "taurus"), planet("jupiter", 6, false, "gemini"),
      planet("moon", 7, false, "cancer"), planet("venus", 8, false, "leo"), planet("ketu", 8, true, "virgo"), planet("saturn", 9, false, "libra"),
    ])} />);

    expect(screen.getByTestId("kundli-planets-house-5")).toHaveAccessibleName(/House 5, Leo, empty/);
    for (const [body, house] of [["sun", 6], ["mercury", 6], ["jupiter", 6], ["moon", 7], ["venus", 8], ["ketu", 8], ["saturn", 9]] as const) {
      expect(screen.getByTestId(`kundli-planet-${body}`).parentElement?.parentElement).toBe(houseElement(house));
    }
    expect(screen.getByTestId("kundli-house-label-6")).toHaveTextContent("6Vir");
    expect(screen.getByTestId("kundli-house-label-8")).toHaveTextContent("8Sco");
  });

  it("keeps Ascendant in fixed house 1 while signs rotate through house labels", () => {
    const rotatedSigns = [...signs.slice(1), signs[0]];
    render(<NorthIndianChart chart={chart([], rotatedSigns)} />);

    expect(screen.getByTestId("kundli-house-label-1")).toHaveAttribute("transform", "translate(200 58)");
    expect(screen.getByTestId("kundli-house-label-1")).toHaveTextContent("2TauASC");
    expect(screen.getByTestId("kundli-house-label-12")).toHaveTextContent("1Ari");
    expect(screen.getByText("ASC").parentElement?.parentElement).toBe(houseElement(1));
  });
});
