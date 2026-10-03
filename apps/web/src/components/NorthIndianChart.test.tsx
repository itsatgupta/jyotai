import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { NorthIndianChart } from "./NorthIndianChart";
import type { Chart, Planet } from "../lib/contracts";

const signs = ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"];
const expectedSlotTransforms: Record<number, string> = {
  1: "translate(200 66)", 2: "translate(95 72)", 3: "translate(38 145)",
  4: "translate(83 218)", 5: "translate(200 350)", 6: "translate(305 336)",
  7: "translate(362 255)", 8: "translate(362 145)", 9: "translate(306 72)",
  10: "translate(200 151)", 11: "translate(200 255)", 12: "translate(92 336)",
};

function planet(body: string, house_number: number, retrograde = false, sign = signs[house_number - 1]): Planet {
  return {
    body,
    sign,
    degree_in_sign: 0,
    house_number,
    retrograde,
  };
}

function chart(planets: Planet[]): Chart {
  return {
    methodology: { chart_type: "D1/Rashi" },
    ascendant: { sign: "aries", degree_in_sign: 0, nakshatra: { nakshatra: "ashwini", pada: 1 } },
    houses: signs.map((sign, index) => ({ number: index + 1, sign })),
    planets,
  };
}

function houseElement(house: number): HTMLElement {
  const element = screen.getAllByTestId("kundli-house").find((candidate) => candidate.getAttribute("data-house-number") === String(house));
  if (!element) throw new Error(`House ${house} was not rendered`);
  return element;
}

describe("NorthIndianChart", () => {
  it("places every one-based house in its fixed North Indian visual slot", () => {
    const uniqueHouseMarkers = Array.from({ length: 12 }, (_, index) => planet(`h${index + 1}`, index + 1));

    render(<NorthIndianChart chart={chart(uniqueHouseMarkers)} />);

    for (let house = 1; house <= 12; house += 1) {
      const renderedHouse = houseElement(house);
      expect(renderedHouse).toHaveAttribute("transform", expectedSlotTransforms[house]);
      expect(renderedHouse).toHaveTextContent(`${house}`);
      expect(screen.getByTestId(`kundli-planet-h${house}`).parentElement?.parentElement).toBe(renderedHouse);
    }
  });

  it("uses house number, not sign, for the specified D1 placements", () => {
    const d1 = chart([
      planet("sun", 6, false, "aries"), planet("mercury", 6, false, "taurus"), planet("jupiter", 6, false, "gemini"),
      planet("moon", 7, false, "cancer"), planet("venus", 8, false, "leo"), planet("ketu", 8, true, "virgo"), planet("saturn", 9, false, "libra"),
    ]);

    render(<NorthIndianChart chart={d1} />);

    expect(houseElement(5).querySelector("g[aria-label]")).toHaveAccessibleName(/House 5, Leo, empty/);
    expect(screen.getByTestId("kundli-planet-sun").parentElement?.parentElement).toHaveAttribute("data-house-number", "6");
    expect(screen.getByTestId("kundli-planet-mercury").parentElement?.parentElement).toHaveAttribute("data-house-number", "6");
    expect(screen.getByTestId("kundli-planet-jupiter").parentElement?.parentElement).toHaveAttribute("data-house-number", "6");
    expect(screen.getByTestId("kundli-planet-moon").parentElement?.parentElement).toHaveAttribute("data-house-number", "7");
    expect(screen.getByTestId("kundli-planet-venus").parentElement?.parentElement).toHaveAttribute("data-house-number", "8");
    expect(screen.getByTestId("kundli-planet-ketu").parentElement?.parentElement).toHaveAttribute("data-house-number", "8");
    expect(screen.getByTestId("kundli-planet-saturn").parentElement?.parentElement).toHaveAttribute("data-house-number", "9");
    expect(screen.getByText("ASC").parentElement).toHaveAttribute("data-house-number", "1");
    expect(screen.getByText("Leo")).toBeInTheDocument();
    expect(houseElement(6)).toHaveTextContent("Vir");
    expect(houseElement(8)).toHaveTextContent("Sco");
  });
});
