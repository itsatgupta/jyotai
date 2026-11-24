// NEXT-PROVISIONAL-01. Usage: node scripts/visual/provisional.mjs <outDir> [baseUrl]
// Screenshots of the "Show provisional interpretations (beta)" toggle and a provisional badge.
// Synthetic profile P_MATCH of the benchmark (1978-01-01 12:00 UTC, 0°, 0°): its D1 fifth lord
// is in the seventh, which matches the provisional Spirituality rule. Needs the API + Vite.
import { chromium } from "playwright";
import fs from "node:fs";

const out = process.argv[2];
const base = process.argv[3] ?? "http://127.0.0.1:5173/";
fs.mkdirSync(out, { recursive: true });

const field = (page, text) => page.locator("label", { has: page.locator(`xpath=./span[starts-with(normalize-space(.), "${text}") and (normalize-space(.) = "${text}" or substring-after(normalize-space(.), "${text}") = "Optional" or substring-after(normalize-space(.), "${text}") = "*")]`) }).locator("input").first();
async function makeProfile(page) {
  await field(page, "Name").fill("Synthetic Test");
  await field(page, "Date of Birth").fill("1978-01-01");
  await field(page, "Time of Birth").fill("12:00");
  await page.getByPlaceholder("Search city, town, or address").fill("Test Location");
  await page.locator(".advanced-details summary").click();
  await field(page, "Selected timezone").fill("UTC");
  await field(page, "Latitude").fill("0");
  await field(page, "Longitude").fill("0");
  await field(page, "As-of date").fill("2026-01-01");
  await field(page, "As-of time").fill("00:00");
  await field(page, "As-of timezone").fill("UTC");
  await page.getByRole("button", { name: "Create My Horoscope" }).click();
  await page.locator("#profile-heading").waitFor({ timeout: 30000 });
}

const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH });
for (const [name, viewport] of Object.entries({ desktop: { width: 1440, height: 900 }, mobile: { width: 390, height: 844 } })) {
  for (const theme of ["light", "dark"]) {
    const ctx = await browser.newContext({ viewport, deviceScaleFactor: 2, reducedMotion: "reduce" });
    await ctx.addInitScript((t) => localStorage.setItem("jyotai-theme", t), theme);
    const page = await ctx.newPage();
    await page.goto(base);
    await page.waitForLoadState("networkidle");
    await makeProfile(page);
    await page.evaluate(() => { location.hash = "#ask-jyotishai"; });
    const toggle = page.getByRole("switch", { name: "Show provisional interpretations (beta)" });
    await toggle.waitFor();
    await page.locator(".consultation-toolbar").screenshot({ path: `${out}/toggle-off-${name}-${theme}.png` });
    await toggle.check();
    await page.locator(".consultation-toolbar").screenshot({ path: `${out}/toggle-on-${name}-${theme}.png` });
    await page.locator("#question").fill("What does my chart say about spirituality?");
    await page.locator("#question").press("Enter");
    const section = page.locator(".provisional-interpretations");
    await section.waitFor({ timeout: 30000 });
    await page.waitForTimeout(400);
    // Scroll to the top so the sticky composer does not cover the element.
    await section.evaluate((element) => element.scrollIntoView({ block: "start" }));
    await page.addStyleTag({ content: ".question-form { visibility: hidden !important; }" });
    await section.screenshot({ path: `${out}/badge-${name}-${theme}.png` });
    await page.locator(".consultation-turn").first().screenshot({ path: `${out}/answer-${name}-${theme}.png` });
    await page.locator(".evidence-details > summary").first().click();
    const justification = page.locator(".provisional-justifications");
    await justification.evaluate((element) => element.scrollIntoView({ block: "start" }));
    await justification.screenshot({ path: `${out}/justification-${name}-${theme}.png` });
    // Remembered per browser: a reload keeps the toggle on.
    await page.reload();
    await page.waitForLoadState("networkidle");
    const remembered = await page.evaluate(() => localStorage.getItem("jyotai-show-provisional"));
    if (remembered !== "on") throw new Error(`toggle not remembered: ${remembered}`);
    await ctx.close();
    console.log("done", name, theme);
  }
}
await browser.close();
