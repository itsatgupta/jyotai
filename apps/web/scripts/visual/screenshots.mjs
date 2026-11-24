// Usage: node scripts/visual/screenshots.mjs <outDir> [baseUrl]  (synthetic profile; needs the API + Vite dev server)
import { chromium } from "playwright";
import fs from "node:fs";

const out = process.argv[2];
const base = process.argv[3] ?? "http://127.0.0.1:5173/";
fs.mkdirSync(out, { recursive: true });
const viewports = { desktop: { width: 1440, height: 900 }, mobile: { width: 390, height: 844 } };

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

const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH });
for (const [vpName, viewport] of Object.entries(viewports)) {
  for (const theme of ["light", "dark"]) {
    const ctx = await browser.newContext({ viewport, deviceScaleFactor: 1, reducedMotion: "reduce" });
    await ctx.addInitScript((t) => localStorage.setItem("jyotai-theme", t), theme);
    const page = await ctx.newPage();
    await page.goto(base);
    await page.waitForLoadState("networkidle");
    await page.screenshot({ path: `${out}/home-${vpName}-${theme}.png`, fullPage: true });
    await page.screenshot({ path: `${out}/home-${vpName}-${theme}-viewport.png` });
    await makeProfile(page);
    await page.waitForTimeout(400);
    await page.locator("#workspace-heading").scrollIntoViewIfNeeded();
    await page.screenshot({ path: `${out}/chart-${vpName}-${theme}.png`, fullPage: true });
    await page.evaluate(() => { location.hash = "#ask-jyotishai"; });
    await page.locator("#question").fill("How will my career be in 2027?");
    await page.locator("#question").press("Enter");
    await page.locator(".consultation-turn").first().waitFor({ timeout: 30000 });
    await page.waitForTimeout(600);
    await page.screenshot({ path: `${out}/consultation-${vpName}-${theme}.png`, fullPage: true });
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(200);
    await page.screenshot({ path: `${out}/consultation-${vpName}-${theme}-viewport.png` });
    await ctx.close();
    console.log("done", vpName, theme);
  }
}
await browser.close();
