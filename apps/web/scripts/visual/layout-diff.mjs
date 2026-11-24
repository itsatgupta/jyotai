// node scripts/visual/layout-diff.mjs <baseUrl> <out.json> : records every element's box, font and padding on
// home, chart and consultation (desktop + mobile). Diff two runs (e.g. production builds before/after a
// colour-only change) to prove geometry is unchanged.
import { chromium } from "playwright";
import fs from "node:fs";
const field = (page, text) => page.locator("label", { has: page.locator(`xpath=./span[starts-with(normalize-space(.), "${text}") and (normalize-space(.) = "${text}" or substring-after(normalize-space(.), "${text}") = "Optional" or substring-after(normalize-space(.), "${text}") = "*")]`) }).locator("input").first();
const grab = (page) => page.evaluate(() => [...document.querySelectorAll("body *")].map((e) => { const r = e.getBoundingClientRect(); const cs = getComputedStyle(e); return `${e.tagName}.${typeof e.className === "string" ? e.className : ""}|${Math.round(r.x)},${Math.round(r.y + scrollY)},${Math.round(r.width)},${Math.round(r.height)}|${cs.fontSize} ${cs.fontWeight} ${cs.fontFamily.slice(0, 20)}|${cs.padding}|${cs.borderTopWidth}`; }));
const b = await chromium.launch({ executablePath: process.env.CHROME_PATH }); const out = {};
for (const [vp, viewport] of [["desktop", { width: 1440, height: 900 }], ["mobile", { width: 390, height: 844 }]]) {
  const ctx = await b.newContext({ viewport, reducedMotion: "reduce" }); const page = await ctx.newPage();
  await page.goto(process.argv[2]); await page.waitForLoadState("networkidle"); out[`${vp}/home`] = await grab(page);
  for (const [t, v] of [["Date of Birth", "2000-01-01"], ["Time of Birth", "12:00"]]) await field(page, t).fill(v);
  await page.getByPlaceholder("Search city, town, or address").fill("Test Location"); await page.locator(".advanced-details summary").click();
  for (const [t, v] of [["Selected timezone", "UTC"], ["Latitude", "0"], ["Longitude", "0"], ["As-of date", "2026-10-30"], ["As-of time", "00:00"], ["As-of timezone", "UTC"]]) await field(page, t).fill(v);
  await page.getByRole("button", { name: "Create My Horoscope" }).click(); await page.locator("#profile-heading").waitFor({ timeout: 30000 });
  await page.waitForTimeout(300); out[`${vp}/chart`] = await grab(page);
  await page.evaluate(() => { location.hash = "#ask-jyotishai"; }); await page.locator("#question").fill("How will my career be in 2027?"); await page.locator("#question").press("Enter");
  await page.locator(".consultation-turn").first().waitFor({ timeout: 30000 }); await page.waitForTimeout(400); await page.evaluate(() => scrollTo(0, 0)); out[`${vp}/consultation`] = await grab(page);
  await ctx.close();
}
await b.close(); fs.writeFileSync(process.argv[3], JSON.stringify(out));
