import { describe, expect, it } from "vitest";
import { planetGlyph, planetKey, signGlyph } from "./glyphs";

// NEXT-UI-VIOLET-01: glyphs carry U+FE0E so no OS draws them as colour emoji.
describe("astrological glyphs", () => {
  it("uses text presentation for every planet and sign", () => {
    for (const body of ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]) expect(planetGlyph(body)).toMatch(/^.︎$/u);
    for (const sign of ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]) expect(signGlyph(sign)).toMatch(/^.︎$/u);
    expect(planetGlyph("Saturn")).toBe("♄︎");
  });
  it("falls back to a star for unknown bodies and signs", () => {
    expect(planetGlyph("pluto")).toBe("✦");
    expect(signGlyph(undefined)).toBe("✦");
  });
  it("gives the data-planet key only for the nine grahas", () => {
    expect(planetKey("Rahu")).toBe("rahu");
    expect(planetKey("ascendant")).toBeUndefined();
  });
});
