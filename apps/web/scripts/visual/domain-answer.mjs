// NEXT-WEALTH-01. Usage:
//   node scripts/visual/domain-answer.mjs <outDir> <birthDate> <birthTime> <question> [baseUrl]
// Screenshots of a domain timing answer (Marriage, Wealth) with the provisional toggle off and
// on, desktop and mobile, light and dark. Synthetic births only (UTC, 0°, 0°). Needs API + Vite.
import { chromium } from "playwright";
import fs from "node:fs";

const [out, birthDate, birthTime, question] = process.argv.slice(2, 6);
const base = process.argv[6] ?? "http://127.0.0.1:5173/";
fs.mkdirSync(out, { recursive: true });

const field = (page, text) => page.locator("label", { has: page.locator(`xpath=./span[starts-with(normalize-space(.), "${text}") and (normalize-space(.) = "${text}" or substring-after(normalize-space(.), "${text}") = "Optional" or substring-after(normalize-space(.), "${text}") = "*")]`) }).locator("input").first();
async function makeProfile(page) {
  await field(page, "Name").fill("Synthetic Test");
  await field(page, "Date of Birth").fill(birthDate);
  await field(page, "Time of Birth").fill(birthTime);
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
    for (const provisional of [false, true]) {
      const ctx = await browser.newContext({ viewport, deviceScaleFactor: 2, reducedMotion: "reduce" });
      await ctx.addInitScript((t) => localStorage.setItem("jyotai-theme", t), theme);
      const page = await ctx.newPage();
      await page.goto(base);
      await page.waitForLoadState("networkidle");
      await makeProfile(page);
      await page.evaluate(() => { location.hash = "#ask-jyotishai"; });
      const toggle = page.getByRole("switch", { name: "Show provisional interpretations (beta)" });
      await toggle.waitFor();
      if (provisional) await toggle.check();
      await page.locator("#question").fill(question);
      await page.locator("#question").press("Enter");
      await page.locator(".consultation-periods").waitFor({ timeout: 30000 });
      if (provisional) await page.locator(".provisional-interpretations").waitFor({ timeout: 30000 });
      else if (await page.locator(".provisional-interpretations").count()) throw new Error("provisional shown with the toggle off");
      await page.waitForTimeout(400);
      await page.addStyleTag({ content: ".question-form { visibility: hidden !important; }" });
      const answer = page.locator(".detailed-answer").first();
      await answer.evaluate((element) => element.scrollIntoView({ block: "start" }));
      await answer.screenshot({ path: `${out}/answer-${provisional ? "on" : "off"}-${name}-${theme}.png` });
      await ctx.close();
      console.log("done", name, theme, provisional ? "on" : "off");
    }
  }
}
await browser.close();
