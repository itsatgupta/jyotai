// Astrological glyphs in text presentation (U+FE0E, NEXT-UI-VIOLET-01): without the variation
// selector Apple and some Android fonts draw ♈–♓ (and some planet symbols) as colour emoji tiles,
// so the same chart would look different per OS. CSS adds `font-variant-emoji: text` and a
// symbol-font stack (`.astro-glyph`, theme/components.css).
const TEXT = "︎";
const SIGNS: Record<string, string> = { aries: "♈", taurus: "♉", gemini: "♊", cancer: "♋", leo: "♌", virgo: "♍", libra: "♎", scorpio: "♏", sagittarius: "♐", capricorn: "♑", aquarius: "♒", pisces: "♓" };
const PLANETS: Record<string, string> = { sun: "☉", moon: "☽", mars: "♂", mercury: "☿", jupiter: "♃", venus: "♀", saturn: "♄", rahu: "☊", ketu: "☋" };

export function signGlyph(sign?: string) { const glyph = SIGNS[sign ?? ""]; return glyph ? glyph + TEXT : "✦"; }
export function planetGlyph(planet?: string) { const glyph = PLANETS[(planet ?? "").toLowerCase()]; return glyph ? glyph + TEXT : "✦"; }
/** The planet's key for `data-planet` (hue and tile ring), or undefined for an unknown body. */
export function planetKey(planet?: string) { const key = (planet ?? "").toLowerCase(); return key in PLANETS ? key : undefined; }
