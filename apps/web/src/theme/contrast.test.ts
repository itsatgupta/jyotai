// @vitest-environment node
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const here = fileURLToPath(new URL(".", import.meta.url));

// WCAG AA for the semantic token pairs, both themes. The rendered-page audit
// (docs/FRONTEND_VISUAL_SYSTEM.md) covers composited backgrounds; this guards the palette itself.
const css = readFileSync(join(here, "tokens.css"), "utf8");
type Rgb = [number, number, number];

function declarations(block: string) {
  return Object.fromEntries([...block.matchAll(/(--[a-z0-9-]+)\s*:\s*([^;]+);/g)].map((match) => [match[1], match[2].trim()]));
}
const [primitivesAndLight, dark] = css.split(/\n(?=\[data-theme="dark"\])/);
const [primitives, light] = primitivesAndLight.split(/\n(?=:root,\n\[data-theme="light"\])/);
const themes = {
  light: { ...declarations(primitives), ...declarations(light) },
  dark: { ...declarations(primitives), ...declarations(dark) },
};

function resolve(value: string, vars: Record<string, string>): Rgb {
  const v = value.trim();
  const ref = v.match(/^var\((--[a-z0-9-]+)\)$/);
  if (ref) return resolve(vars[ref[1]], vars);
  if (/^#[0-9a-f]{6}$/i.test(v)) return [1, 3, 5].map((i) => parseInt(v.slice(i, i + 2), 16)) as Rgb;
  const mix = v.match(/^color-mix\(in srgb,\s*(.+?)\s+(\d+(?:\.\d+)?)%,\s*(.+)\)$/);
  if (mix && mix[3] !== "transparent") {
    const p = Number(mix[2]) / 100;
    const [a, b] = [resolve(mix[1], vars), resolve(mix[3], vars)];
    return a.map((channel, i) => channel * p + b[i] * (1 - p)) as Rgb;
  }
  throw new Error(`Cannot resolve ${v}`);
}
const luminance = (rgb: Rgb) => {
  const [r, g, b] = rgb.map((channel) => { const c = channel / 255; return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
};
const ratio = (a: Rgb, b: Rgb) => { const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x); return (hi + 0.05) / (lo + 0.05); };

const surfaces = ["--ui-bg", "--ui-bg-2", "--ui-surface", "--ui-surface-2"];
const textPairs: [string, string[]][] = [
  ["--ui-text", surfaces],
  ["--ui-muted", surfaces],
  ["--ui-accent-text", [...surfaces, "--ui-accent-soft"]],
  ["--ui-accent-deep", surfaces],
  ["--ui-secondary", ["--ui-surface", "--ui-surface-2"]],
  ["--ui-accent-ink", ["--ui-accent", "--ui-accent-hover"]],
  ...["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"].map((planet): [string, string[]] => [`--planet-${planet}`, ["--ui-surface", "--ui-bg-2"]]),
];

describe.each(Object.entries(themes))("%s theme", (_theme, vars) => {
  it.each(textPairs.flatMap(([fg, bgs]) => bgs.map((bg) => [fg, bg])))("%s on %s meets 4.5:1", (fg, bg) => {
    expect(ratio(resolve(vars[fg], vars), resolve(vars[bg], vars))).toBeGreaterThanOrEqual(4.5);
  });
  it("focus ring meets 3:1 against the page and surfaces", () => {
    for (const bg of surfaces) expect(ratio(resolve(vars["--ui-focus"], vars), resolve(vars[bg], vars))).toBeGreaterThanOrEqual(3);
  });
});
