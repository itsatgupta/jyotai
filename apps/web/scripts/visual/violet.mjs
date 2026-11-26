// NEXT-UI-VIOLET-01. Usage: node scripts/visual/violet.mjs <outDir> [baseUrl]
// Profile, D1 planet cards, Dasha + transits, a Career answer and a Wealth answer (provisional
// toggle on) at 1440 and 390 px, light and dark. Synthetic birth only. Needs the API + Vite.
import { chromium } from "playwright";
import fs from "node:fs";

const out = process.argv[2];
const base = process.argv[3] ?? "http://127.0.0.1:5173/";
fs.mkdirSync(out, { recursive: true });
const viewports = { "1440": { width: 1440, height: 900 }, "390": { width: 390, height: 844 } };

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
async function shoot(locator, path) {
  await locator.evaluate((element) => element.scrollIntoView({ block: "start" }));
  await locator.page().waitForTimeout(250);
  await locator.screenshot({ path });
}
async function ask(page, question) {
  const before = await page.locator(".consultation-turn").count();
  await page.locator("#question").fill(question);
  await page.locator("#question").press("Enter");
  await page.locator(".consultation-turn").nth(before).waitFor({ timeout: 30000 });
  await page.waitForTimeout(500);
  return page.locator(".consultation-turn").nth(before);
}

const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH });
for (const [vp, viewport] of Object.entries(viewports)) {
  for (const theme of ["light", "dark"]) {
    const ctx = await browser.newContext({ viewport, deviceScaleFactor: 1, reducedMotion: "reduce" });
    await ctx.addInitScript((t) => { localStorage.setItem("jyotai-theme", t); localStorage.setItem("jyotai-show-provisional", "off"); }, theme);
    const page = await ctx.newPage();
    await page.goto(base);
    await page.waitForLoadState("networkidle");
    await page.screenshot({ path: `${out}/home-${vp}-${theme}.png` });
    await makeProfile(page);
    await page.waitForTimeout(400);
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.screenshot({ path: `${out}/profile-${vp}-${theme}.png` });
    await shoot(page.locator(".chart-explorer").first(), `${out}/d1-${vp}-${theme}.png`);
    await shoot(page.locator(".dasha-section").first(), `${out}/dasha-${vp}-${theme}.png`);
    await shoot(page.locator(".transit-section").first(), `${out}/transits-${vp}-${theme}.png`);
    await page.evaluate(() => { location.hash = "#ask-jyotishai"; });
    await page.addStyleTag({ content: ".question-form { position: static !important; }" });
    const career = await ask(page, "How will my career be in 2027?");
    await shoot(career, `${out}/career-${vp}-${theme}.png`);
    await ctx.close();
    // Wealth in a fresh session (in the Career thread it would be read as a follow-up)
    const wctx = await browser.newContext({ viewport, deviceScaleFactor: 1, reducedMotion: "reduce" });
    await wctx.addInitScript((t) => { localStorage.setItem("jyotai-theme", t); }, theme);
    const wpage = await wctx.newPage();
    await wpage.goto(base);
    await wpage.waitForLoadState("networkidle");
    await makeProfile(wpage);
    await wpage.evaluate(() => { location.hash = "#ask-jyotishai"; });
    await wpage.addStyleTag({ content: ".question-form { position: static !important; }" });
    const toggle = wpage.getByRole("switch", { name: "Show provisional interpretations (beta)" });
    await toggle.check();
    const wealth = await ask(wpage, "When will my wealth grow?");
    await wpage.locator(".provisional-interpretations, .provisional-item").first().waitFor({ timeout: 30000 });
    await shoot(wealth, `${out}/wealth-on-${vp}-${theme}.png`);
    await wctx.close();
    console.log("done", vp, theme);
  }
}
await browser.close();
