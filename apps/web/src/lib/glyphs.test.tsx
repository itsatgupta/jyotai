import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AstroGlyph, GlyphTile, PLANET_GLYPHS, SIGN_GLYPHS, STROKE } from "../components/AstroGlyph";
import { planetKey } from "./glyphs";

// NEXT-UI-VIOLET-02: glyphs are inline SVG with one stroke weight; no text, so no OS symbol font.
describe("astrological glyphs", () => {
  it("draws all nine grahas and twelve signs", () => {
    expect(PLANET_GLYPHS).toEqual(["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]);
    expect(SIGN_GLYPHS).toEqual(["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]);
  });
  it.each([...PLANET_GLYPHS.map((n) => ["planet", n]), ...SIGN_GLYPHS.map((n) => ["sign", n])] as ["planet" | "sign", string][])("%s %s is a decorative SVG with the shared stroke and no text", (kind, name) => {
    const { container } = render(<AstroGlyph kind={kind} name={name} />);
    const svg = container.querySelector("svg")!;
    expect(svg.getAttribute("data-glyph")).toBe(`${kind}-${name}`);
    expect(svg.getAttribute("viewBox")).toBe("0 0 24 24");
    expect(svg.getAttribute("stroke-width")).toBe(String(STROKE));
    expect(svg.getAttribute("stroke")).toBe("currentColor");
    expect(svg.getAttribute("aria-hidden")).toBe("true");
    expect(svg.querySelectorAll("path, circle").length).toBeGreaterThan(0);
    // no per-shape stroke-width override, and no text nodes
    expect([...svg.querySelectorAll("[stroke-width]")]).toEqual([]);
    expect(svg.textContent).toBe("");
  });
  it("falls back to a star for unknown bodies and signs", () => {
    const { container } = render(<><AstroGlyph kind="planet" name="pluto" /><AstroGlyph kind="sign" /></>);
    expect([...container.querySelectorAll("svg")].map((s) => s.getAttribute("data-glyph"))).toEqual(["planet-pluto", "sign-unknown"]);
  });
  it("puts the glyph on an orb inside a tile, with the planet or ascendant hue", () => {
    const { container } = render(<><GlyphTile kind="planet" name="Saturn" as="i" /><GlyphTile kind="sign" name="libra" tileClass="sign-tile" hue="ascendant" /><GlyphTile kind="sign" name="capricorn" tileClass="sign-tile" hue="moon" /></>);
    const [saturn, lagna, moon] = [...container.children] as HTMLElement[];
    expect(saturn.tagName).toBe("I");
    expect(saturn.className).toBe("planet-tile");
    expect(saturn.dataset.planet).toBe("saturn");
    expect(saturn.querySelector(".planet-orb > svg")?.getAttribute("data-glyph")).toBe("planet-saturn");
    expect(lagna.dataset.signOf).toBe("ascendant");
    expect(lagna.dataset.planet).toBeUndefined();
    expect(moon.dataset.planet).toBe("moon");
    expect(moon.querySelector("svg")?.getAttribute("data-glyph")).toBe("sign-capricorn");
    for (const tile of [saturn, lagna, moon]) expect(tile.getAttribute("aria-hidden")).toBe("true");
  });
  it("gives the data-planet key only for the nine grahas", () => {
    expect(planetKey("Rahu")).toBe("rahu");
    expect(planetKey("ascendant")).toBeUndefined();
  });
});
