// NEXT-CHILDREN-01 (open item 21). Usage:
//   node scripts/visual/overflow.mjs [baseUrl]
// Checks that no page is wider than the viewport at 360, 390 and 430 px, light and dark: the
// landing page, every chart-room tab, and the consultation view with a Children answer
// (provisional toggle on). For each view it compares the document's scrollWidth with the
// viewport and lists any element that sticks out past the right edge without a clipping or
// scrolling ancestor. Also checks that the active nav item is scrolled into view on phones.
// Synthetic birth only (UTC, 0°, 0°). Needs API + Vite. Exits 1 on any overflow.
import { chromium } from "playwright";

const base = process.argv[2] ?? "http://127.0.0.1:5173/";
const widths = [360, 390, 430];
const field = (page, text) => page.locator("label", { has: page.locator(`xpath=./span[starts-with(normalize-space(.), "${text}") and (normalize-space(.) = "${text}" or substring-after(normalize-space(.), "${text}") = "Optional" or substring-after(normalize-space(.), "${text}") = "*")]`) }).locator("input").first();

async function makeProfile(page) {
  await field(page, "Name").fill("Synthetic Test");
  await field(page, "Date of Birth").fill("1960-04-01");
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

async function measure(page, label) {
  await page.waitForTimeout(250);
  return page.evaluate((view) => {
    const width = document.documentElement.clientWidth;
    const scrollWidth = Math.max(document.documentElement.scrollWidth, document.body.scrollWidth);
    const clips = (element) => {
      for (let node = element.parentElement; node && node !== document.body; node = node.parentElement) {
        const style = getComputedStyle(node);
        if (["hidden", "auto", "scroll", "clip"].includes(style.overflowX)) return true;
      }
      return false;
    };
    const offenders = [];
    for (const element of document.body.querySelectorAll("*")) {
      const rect = element.getBoundingClientRect();
      if (rect.width === 0 || rect.right <= width + 0.5 || clips(element)) continue;
      const style = getComputedStyle(element);
      if (style.position === "fixed" || style.visibility === "hidden") continue;
      offenders.push(`${element.tagName.toLowerCase()}${element.className && typeof element.className === "string" ? "." + element.className.trim().split(/\s+/).join(".") : ""} right=${Math.round(rect.right)}`);
    }
    return { view, width, scrollWidth, overflow: scrollWidth > width, offenders: offenders.slice(0, 8) };
  }, label);
}

const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH });
const results = [];
for (const width of widths) {
  for (const theme of ["light", "dark"]) {
    const ctx = await browser.newContext({ viewport: { width, height: 844 }, deviceScaleFactor: 1, reducedMotion: "reduce" });
    await ctx.addInitScript((t) => localStorage.setItem("jyotai-theme", t), theme);
    const page = await ctx.newPage();
    await page.goto(base);
    await page.waitForLoadState("networkidle");
    const tag = `${width}px ${theme}`;
    results.push({ tag, ...(await measure(page, "landing")) });
    await makeProfile(page);
    results.push({ tag, ...(await measure(page, "profile")) });
    const tabs = page.locator(".tablist [role=tab]");
    for (let index = 0; index < (await tabs.count()); index += 1) {
      const tab = tabs.nth(index);
      const name = (await tab.textContent())?.trim();
      await tab.click();
      results.push({ tag, ...(await measure(page, `tab ${name}`)) });
      const visible = await tab.evaluate((element) => {
        const list = element.closest(".tablist").getBoundingClientRect();
        const rect = element.getBoundingClientRect();
        return rect.left >= list.left - 1 && rect.right <= list.right + 1;
      });
      if (!visible) results.push({ tag, view: `tab ${name} not scrolled into view`, overflow: true, offenders: [] });
    }
    await page.evaluate(() => { location.hash = "#ask-jyotishai"; });
    const toggle = page.getByRole("switch", { name: "Show provisional interpretations (beta)" });
    await toggle.waitFor();
    await toggle.check();
    await page.locator("#question").fill("When will I have children?");
    await page.locator("#question").press("Enter");
    await page.locator(".provisional-interpretations").waitFor({ timeout: 30000 });
    results.push({ tag, ...(await measure(page, "consultation (Children answer, toggle on)")) });
    const nav = await page.evaluate(() => {
      const active = document.querySelector("[aria-current=page]");
      if (!active) return null;
      let scroller = active.parentElement;
      while (scroller && getComputedStyle(scroller).overflowX === "visible") scroller = scroller.parentElement;
      if (!scroller) return true;
      const box = scroller.getBoundingClientRect();
      const rect = active.getBoundingClientRect();
      return rect.left >= box.left - 1 && rect.right <= box.right + 1;
    });
    if (nav === false) results.push({ tag, view: "active nav item not scrolled into view", overflow: true, offenders: [] });
    await ctx.close();
  }
}
await browser.close();
let failed = 0;
for (const row of results) {
  const status = row.overflow ? "OVERFLOW" : "ok";
  if (row.overflow) failed += 1;
  console.log(`${status.padEnd(8)} ${row.tag.padEnd(12)} ${row.view}${row.scrollWidth ? ` (scrollWidth ${row.scrollWidth} / ${row.width})` : ""}${row.offenders?.length ? `\n         ${row.offenders.join("\n         ")}` : ""}`);
}
console.log(`${results.length} checks, ${failed} overflow`);
process.exit(failed ? 1 : 0);
