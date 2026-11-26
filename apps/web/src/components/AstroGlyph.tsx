import type { ReactNode } from "react";
import { planetKey } from "../lib/glyphs";

// Inline SVG astrological glyphs (NEXT-UI-VIOLET-02). Every glyph is drawn on the same 24-unit
// grid with one stroke weight (STROKE, round caps and joins) in currentColor, so no OS symbol font
// or colour-emoji renderer is involved and every platform draws the same shapes.
export const STROKE = 1.9;

const planets: Record<string, ReactNode> = {
  sun: <><circle cx="12" cy="12" r="8" /><circle cx="12" cy="12" r="1.7" fill="currentColor" stroke="none" /></>,
  moon: <path d="M14.5 3.5A8.5 8.5 0 1 0 14.5 20.5A10 10 0 0 1 14.5 3.5Z" />,
  mars: <><circle cx="10" cy="14" r="5.5" /><path d="M14 10L19.5 4.5M14.5 4.5H19.5V9.5" /></>,
  mercury: <><path d="M8 2.6A4 4 0 0 0 16 2.6" /><circle cx="12" cy="11.6" r="4.2" /><path d="M12 15.8V22M9 19.2H15" /></>,
  jupiter: <path d="M5.5 8A3.75 3.75 0 0 1 13 8C13 11.5 9 14 5 16.5H19.5M16 4V21" />,
  venus: <><circle cx="12" cy="9" r="5.5" /><path d="M12 14.5V21.5M8.5 18H15.5" /></>,
  saturn: <path d="M8.5 3V15.5M5.5 6.5H11.5M8.5 11.5C9.5 9 15.5 8.5 15.5 13.5C15.5 16.5 12 17.5 12.5 21" />,
  rahu: <><path d="M7 16.2A6.5 6.5 0 1 1 17 16.2" /><circle cx="5.8" cy="18.2" r="2" /><circle cx="18.2" cy="18.2" r="2" /></>,
  ketu: <><path d="M7 7.8A6.5 6.5 0 1 0 17 7.8" /><circle cx="5.8" cy="5.8" r="2" /><circle cx="18.2" cy="5.8" r="2" /></>,
};

const signs: Record<string, ReactNode> = {
  aries: <path d="M12 20.5V10M12 10C12 3 4 3 4 8.5C4 10.5 5.5 11.5 6.5 11.5M12 10C12 3 20 3 20 8.5C20 10.5 18.5 11.5 17.5 11.5" />,
  taurus: <><circle cx="12" cy="15" r="5" /><path d="M4.5 4.5C5.5 9 9 10 12 10C15 10 18.5 9 19.5 4.5" /></>,
  gemini: <path d="M5 4C9 5.5 15 5.5 19 4M5 20C9 18.5 15 18.5 19 20M9 5.1V18.9M15 5.1V18.9" />,
  cancer: <><circle cx="7.5" cy="9" r="2.5" /><path d="M7.5 6.5C11 4.5 16 4.5 20 7" /><circle cx="16.5" cy="15" r="2.5" /><path d="M16.5 17.5C13 19.5 8 19.5 4 17" /></>,
  leo: <><circle cx="7.5" cy="14.5" r="2.8" /><path d="M10.3 14.5C10.3 10 8.5 8.5 8.5 7A4 4 0 0 1 16.5 7C16.5 10.5 13 13 13 16.5C13 19 15 20.5 17 20.5C18.5 20.5 19.5 19.5 19.5 18" /></>,
  virgo: <path d="M4 7C5.5 7 6 8 6 9V18M6 9.5C6 6 10.5 6 10.5 9.5V18M10.5 9.5C10.5 6 15 6 15 9.5V16.5C15 18.5 16 20 17.5 20M15 14C18 10.5 21 13.5 18 17C16.5 18.8 14.5 20 13 21" />,
  libra: <path d="M4 19.5H20M4 15.5H8.5A4.2 4.2 0 1 1 15.5 15.5H20" />,
  scorpio: <path d="M4 7C5.5 7 6 8 6 9V18M6 9.5C6 6 10.5 6 10.5 9.5V18M10.5 9.5C10.5 6 15 6 15 9.5V17C15 18.5 16 19.5 17.5 19.5H20M18 17.5L20 19.5L18 21.5" />,
  sagittarius: <path d="M5 19L19 5M12 5H19V12M7.5 11.5L12.5 16.5" />,
  capricorn: <><path d="M4 6C5.5 6 6.5 7 6.5 9V18M6.5 9C7.5 4.5 12 4.5 12.5 9V15C12.5 19 15 21 17.5 19.5" /><circle cx="16.5" cy="16.5" r="3" /></>,
  aquarius: <path d="M4 10L7 7L10 10L13 7L16 10L19 7M5 17L8 14L11 17L14 14L17 17L20 14" />,
  pisces: <path d="M6.5 4C10.5 8 10.5 16 6.5 20M17.5 4C13.5 8 13.5 16 17.5 20M5 12H19" />,
};

// four-point star for an unknown body or sign (was "✦")
const star = <path d="M12 3L13.8 10.2L21 12L13.8 13.8L12 21L10.2 13.8L3 12L10.2 10.2Z" fill="currentColor" strokeWidth={1} />;

export const PLANET_GLYPHS = Object.keys(planets);
export const SIGN_GLYPHS = Object.keys(signs);

type GlyphProps = { kind: "planet" | "sign"; name?: string | null; className?: string };

/** One glyph as inline SVG, decorative (aria-hidden): the name is always given in text nearby. */
export function AstroGlyph({ kind, name, className }: GlyphProps) {
  const key = (name ?? "").toLowerCase();
  const shape = (kind === "planet" ? planets : signs)[key] ?? star;
  return <svg className={`astro-svg${className ? ` ${className}` : ""}`} data-glyph={`${kind}-${key || "unknown"}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={STROKE} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false">{shape}</svg>;
}

type TileProps = GlyphProps & { as?: "span" | "i" | "b"; tileClass?: string; hue?: string };

/**
 * A violet tile holding a filled orb in the planet's hue with the glyph in dark ink
 * (NEXT-UI-VIOLET-02). `hue` picks the orb colour (a graha key, or "ascendant" for amber);
 * it defaults to the planet itself.
 */
export function GlyphTile({ kind, name, as: Tag = "span", tileClass = "planet-tile", hue, className }: TileProps) {
  const hueKey = hue === "ascendant" ? undefined : planetKey(hue ?? (kind === "planet" ? name ?? undefined : undefined));
  return <Tag className={`${tileClass}${className ? ` ${className}` : ""}`} data-planet={hueKey} data-sign-of={hue === "ascendant" ? "ascendant" : undefined} aria-hidden="true"><span className="planet-orb"><AstroGlyph kind={kind} name={name} /></span></Tag>;
}
