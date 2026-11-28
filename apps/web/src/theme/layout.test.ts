// @vitest-environment node
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

// NEXT-CHILDREN-01 (open item 21): no page wider than the viewport at 360/390/430 px. The
// rendered check is scripts/visual/overflow.mjs (needs API + Vite); these static guards keep
// the two causes it found from coming back.
const srcDir = join(fileURLToPath(new URL(".", import.meta.url)), "..");

function cssFiles(dir: string): string[] {
  return readdirSync(dir).flatMap((name) => {
    const path = join(dir, name);
    if (statSync(path).isDirectory()) return cssFiles(path);
    return path.endsWith(".css") ? [path] : [];
  });
}

describe("phone layout guards", () => {
  it("never lets the chart-room tab list bleed past its container", () => {
    for (const file of cssFiles(srcDir)) {
      for (const rule of readFileSync(file, "utf8").matchAll(/\.tablist\s*\{([^}]*)\}/g)) {
        expect(rule[1], file).not.toMatch(/margin(?:-right|-inline-end)?\s*:[^;]*-\d/);
      }
    }
  });

  it("wraps the consultation toolbar on phones", () => {
    const css = readFileSync(join(srcDir, "components", "QuestionAnalysis.css"), "utf8");
    const phone = css.match(/@media \(max-width: 600px\) \{(.*)\}\s*$/m)?.[1] ?? "";
    expect(phone).toMatch(/\.consultation-toolbar \{[^}]*flex-wrap: wrap/);
  });
});
