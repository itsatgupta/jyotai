// @vitest-environment node
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const here = fileURLToPath(new URL(".", import.meta.url));

// Colour literals live only in theme/tokens.css (NEXT-UI-AMBER). Everything else uses var(--…).
const srcDir = join(here, "..");
const webDir = join(srcDir, "..");
const tokensFile = join(srcDir, "theme", "tokens.css");
const literal = /#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch)\(/;
const named = /:\s*[^;{}]*\b(?:white|black|red|green|blue|purple|violet|indigo|gold|orange|teal|gray|grey|silver|navy|crimson|ivory)\b/;

function files(dir: string): string[] {
  return readdirSync(dir).flatMap((name) => {
    const path = join(dir, name);
    return statSync(path).isDirectory() ? files(path) : [path];
  });
}

const tokens = readFileSync(tokensFile, "utf8");
const defined = new Set([...tokens.matchAll(/(--[a-z0-9-]+)\s*:/g)].map((match) => match[1]));
const primitive = (name: string) => tokens.match(new RegExp(`${name}:\\s*(#[0-9a-f]{6})`))?.[1];

describe("design tokens", () => {
  const sources = files(srcDir).filter((path) => /\.(css|tsx?)$/.test(path) && path !== tokensFile && !/\.test\.tsx?$/.test(path));

  it.each(sources.map((path) => [relative(srcDir, path), path]))("%s has no hard-coded colours", (_name, path) => {
    const code = readFileSync(path, "utf8").replace(/\/\*[\s\S]*?\*\//g, "").replace(/var\(--[a-z0-9-]+\)/g, "var()");
    const offending = code.split("\n").filter((line) => literal.test(line) || (path.endsWith(".css") && named.test(line)));
    expect(offending).toEqual([]);
  });

  it("every token a stylesheet references is defined", () => {
    const missing = new Set<string>();
    for (const path of sources.filter((file) => file.endsWith(".css"))) {
      const css = readFileSync(path, "utf8");
      const local = new Set([...css.matchAll(/(--[a-z0-9-]+)\s*:/g)].map((match) => match[1]));
      for (const [, name] of css.matchAll(/var\((--(?:indigo|amber|saffron|maroon|turquoise|violet|parchment|rose|sage|ui|planet)-[a-z0-9-]+)/g)) {
        if (!defined.has(name) && !local.has(name)) missing.add(name);
      }
    }
    expect([...missing]).toEqual([]);
  });

  it("gives light and dark values for every semantic token", () => {
    const blocks = tokens.split(/\n(?=\[data-theme="dark"\])/);
    const names = (block: string) => [...block.matchAll(/(--(?:ui|planet)-[a-z0-9-]+)\s*:/g)].map((match) => match[1]).sort();
    expect(blocks).toHaveLength(2);
    expect(names(blocks[1])).toEqual(names(blocks[0]));
    expect(names(blocks[0]).length).toBeGreaterThan(20);
  });

  it("keeps the browser theme-color in step with --indigo-950", () => {
    for (const page of ["index.html", "preview.html"]) {
      const html = readFileSync(join(webDir, page), "utf8");
      expect(html).toContain(`<meta name="theme-color" content="${primitive("--indigo-950")}" />`);
    }
  });
});
