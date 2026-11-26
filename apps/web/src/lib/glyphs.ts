// Planet keys for `data-planet` (orb hue and tile ring). The glyphs themselves are inline SVG
// (components/AstroGlyph.tsx, NEXT-UI-VIOLET-02), so no OS symbol font or colour emoji is used.
const PLANETS = new Set(["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]);

/** The planet's key for `data-planet`, or undefined for an unknown body. */
export function planetKey(planet?: string) { const key = (planet ?? "").toLowerCase(); return PLANETS.has(key) ? key : undefined; }
