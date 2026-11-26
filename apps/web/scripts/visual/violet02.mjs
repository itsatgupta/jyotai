// NEXT-UI-VIOLET-02. Usage: node scripts/visual/violet02.mjs <outDir> <beforeBaseUrl> <afterBaseUrl>
// Profile strip, D1 planet cards, Dasha and transits at 1440 and 390 px, light and dark, for a
// "before" build (NEXT-UI-VIOLET-01) and an "after" build, plus side-by-side composites in
// <outDir>/compare/. Synthetic birth only. Needs the API and both Vite servers.
import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";

const [out, beforeUrl, afterUrl] = process.argv.slice(2);
if (!out || !beforeUrl || !afterUrl) throw new Error("usage: violet02.mjs <outDir> <beforeBaseUrl> <afterBaseUrl>");
const viewports = { "1440": { width: 1440, height: 900 }, "390": { width: 390, height: 844 } };
const views = ["profile", "d1", "transits", "dasha"];

const field = (page, text) => page.locator("label", { has: page.locator(`xpath=./span[starts-with(normalize-space(.), "${text}") and (normalize-space(.) = "${text}" or substring-after(normalize-space(.), "${text}") = "Optional" or substring-after(normalize-space(.), "${text}") = "*")]`) }).locator("input").first();
async function makeProfile(page) {
  await field(page, "Name").fill("Synthetic Test");
  await field(page, "Date of Birth").fill("2000-01-01");
  await field(page, "Time of Birth").fill("12:00");
  await page.getByPlaceholder("Search city, town, or address").fill("Test Location");
  await page.locator(".advanced-details summary").click();
  await field(page, "Selected timezone").fill("UTC");
  await field(page, "Latitude").fill("0");
  await field(page, "Longitude").fill("0");
  await field(page, "As-of date").fill("2026-10-30");
  await field(page, "As-of time").fill("00:00");
  await field(page, "As-of timezone").fill("UTC");
  await page.getByRole("button", { name: "Create My Horoscope" }).click();
  await page.locator("#profile-heading").waitFor({ timeout: 30000 });
}
async function shoot(locator, file) {
  await locator.evaluate((element) => element.scrollIntoView({ block: "start" }));
  await locator.page().waitForTimeout(250);
  await locator.screenshot({ path: file });
}

const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH });
for (const [label, base] of [["before", beforeUrl], ["after", afterUrl]]) {
  const dir = path.join(out, label);
  fs.mkdirSync(dir, { recursive: true });
  for (const [vp, viewport] of Object.entries(viewports)) for (const theme of ["light", "dark"]) {
    const ctx = await browser.newContext({ viewport, deviceScaleFactor: 2, reducedMotion: "reduce" });
    await ctx.addInitScript((t) => { localStorage.setItem("jyotai-theme", t); localStorage.setItem("jyotai-show-provisional", "off"); }, theme);
    const page = await ctx.newPage();
    await page.goto(base);
    await page.waitForLoadState("networkidle");
    await makeProfile(page);
    await page.waitForTimeout(400);
    await shoot(page.locator(".profile-strip").first(), `${dir}/profile-${vp}-${theme}.png`);
    await shoot(page.locator(".planet-grid").first(), `${dir}/d1-${vp}-${theme}.png`);
    await shoot(page.locator(".transit-section").first(), `${dir}/transits-${vp}-${theme}.png`);
    await shoot(page.locator(".dasha-section").first(), `${dir}/dasha-${vp}-${theme}.png`);
    await ctx.close();
    console.log("done", label, vp, theme);
  }
}

// Side-by-side composites, rendered by the browser so each half is captioned
const compare = path.join(out, "compare");
fs.mkdirSync(compare, { recursive: true });
const page = await browser.newPage({ viewport: { width: 1200, height: 800 }, deviceScaleFactor: 1 });
for (const view of views) for (const vp of Object.keys(viewports)) for (const theme of ["light", "dark"]) {
  const name = `${view}-${vp}-${theme}.png`;
  const src = (side) => "data:image/png;base64," + fs.readFileSync(path.join(out, side, name)).toString("base64");
  const maxWidth = vp === "390" ? 420 : 760;
  await page.setContent(`<!doctype html><meta charset="utf-8"><style>body{margin:0;padding:16px;background:${theme === "dark" ? "#070a1c" : "#fcf7ec"};color:${theme === "dark" ? "#fcf7ec" : "#0c1030"};font:600 14px system-ui,sans-serif;display:inline-flex;gap:16px;align-items:flex-start}figure{margin:0}figcaption{margin:0 0 8px}img{display:block;max-width:${maxWidth}px;height:auto;border:1px solid ${theme === "dark" ? "#353c7b" : "#dccaa6"}}</style><figure><figcaption>Before · NEXT-UI-VIOLET-01 · ${view} · ${vp} px · ${theme}</figcaption><img src="${src("before")}"></figure><figure><figcaption>After · NEXT-UI-VIOLET-02 · ${view} · ${vp} px · ${theme}</figcaption><img src="${src("after")}"></figure>`);
  await page.waitForLoadState("load");
  await page.locator("body").screenshot({ path: path.join(compare, name) });
}
await browser.close();
console.log("composites in", compare);
