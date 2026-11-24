// node scripts/visual/contrast-audit.mjs <outJson> [baseUrl] — WCAG AA text-contrast audit, light + dark, desktop + mobile,
// on home, chart dashboard and consultation answer (all <details> expanded).
// Background = rendered pixels under each text box with text made transparent (handles gradients/images).
// Text colour = computed colour, alpha x ancestor opacity, composited over each sampled pixel.
// Ratio reported = 10th-percentile over the sampled pixels (worst-case-ish, robust to stray glyph pixels).
import { chromium } from "playwright";
import { PNG } from "pngjs";
import fs from "node:fs";

const exe = process.env.CHROME_PATH; // optional: a local Chrome/Chromium binary
const field = (page, text) => page.locator("label", { has: page.locator(`xpath=./span[starts-with(normalize-space(.), "${text}") and (normalize-space(.) = "${text}" or substring-after(normalize-space(.), "${text}") = "Optional" or substring-after(normalize-space(.), "${text}") = "*")]`) }).locator("input").first();
const lum = ([r, g, b]) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }; return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };

async function collect(page) {
  return page.evaluate(() => {
    const out = [];
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
    let id = 0;
    for (let el = walker.currentNode; el; el = walker.nextNode()) {
      if (!(el instanceof Element)) continue;
      const own = [...el.childNodes].filter((n) => n.nodeType === 3 && n.textContent.trim()).map((n) => n.textContent.trim()).join(" ");
      const isField = el.matches("input:not([type=hidden]),textarea") && (el.value || el.placeholder);
      if (!own && !isField) continue;
      const full = el.getBoundingClientRect();
      const top = Math.max(0, full.top), bottom = Math.min(innerHeight, full.bottom);
      if (full.width < 2 || bottom - top < 8 || full.right <= 0 || full.left >= innerWidth) continue;
      const r = { left: full.left, top, width: full.width, height: bottom - top, bottom };
      const cs = getComputedStyle(el);
      if (cs.visibility === "hidden" || cs.display === "none") continue;
      if (el.closest(".sr-only,.orbit-instructions")) continue;
      let op = 1; for (let a = el; a; a = a.parentElement) op *= parseFloat(getComputedStyle(a).opacity);
      if (op < 0.05) continue;
      // occlusion: centre point must hit this element or a descendant
      const cx = Math.min(innerWidth - 1, r.left + r.width / 2), cy = Math.min(innerHeight - 1, r.top + r.height / 2);
      const hit = document.elementFromPoint(cx, cy);
      if (!hit || !(el === hit || el.contains(hit) || hit.contains(el))) continue;
      const decorative = Boolean(el.closest("[aria-hidden=true],svg"));
      const disabled = Boolean(el.closest(":disabled,[aria-disabled=true]"));
      const px = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight, 10) >= 700;
      const large = px >= 24 || (px >= 18.66 && bold);
      const placeholder = isField && !el.value;
      const color = placeholder ? getComputedStyle(el, "::placeholder").color : (el instanceof SVGElement ? cs.fill : cs.color);
      const tag = `a${id++}`; el.setAttribute("data-audit", tag);
      out.push({ tag, text: (own || el.value || el.placeholder).slice(0, 60), cls: `${el.tagName.toLowerCase()}.${(typeof el.className === "string" ? el.className : el.className.baseVal).split(" ").filter(Boolean).join(".")}`, color, op, large, decorative, disabled, placeholder, box: [r.left, r.top, r.width, r.height] });
    }
    return out;
  });
}
function parseColor(s) {
  const m = s.match(/rgba?\(([^)]+)\)/); if (m) { const p = m[1].split(/[ ,/]+/).filter(Boolean).map(Number); return [p[0], p[1], p[2], p[3] ?? 1]; }
  const c = s.match(/color\(srgb ([^)]+)\)/); if (c) { const p = c[1].split(/[ /]+/).filter(Boolean).map(Number); return [p[0] * 255, p[1] * 255, p[2] * 255, p[3] ?? 1]; }
  return null;
}
async function auditViewport(page, label, results) {
  const items = await collect(page);
  await page.addStyleTag({ content: `*{color:transparent!important;-webkit-text-fill-color:transparent!important;text-shadow:none!important;caret-color:transparent!important} *::placeholder{color:transparent!important} svg text{fill:transparent!important}` }).then((h) => h.evaluate((n) => n.setAttribute("data-audit-style", "")));
  const png = PNG.sync.read(await page.screenshot());
  await page.evaluate(() => document.querySelectorAll("[data-audit-style]").forEach((n) => n.remove()));
  for (const it of items) {
    const c = parseColor(it.color); if (!c) continue;
    const a = c[3] * it.op; const [x, y, w, h] = it.box; const ratios = [];
    for (let i = 1; i <= 6; i++) for (let j = 1; j <= 4; j++) {
      const px = Math.floor(x + (w * i) / 7), py = Math.floor(y + (h * j) / 5);
      if (px < 0 || py < 0 || px >= png.width || py >= png.height) continue;
      const k = (py * png.width + px) * 4; const bg = [png.data[k], png.data[k + 1], png.data[k + 2]];
      const fg = [0, 1, 2].map((q) => c[q] * a + bg[q] * (1 - a));
      ratios.push(ratio(fg, bg));
    }
    if (!ratios.length) continue;
    ratios.sort((p, q) => p - q);
    const r = ratios[Math.floor(ratios.length * 0.1)];
    results.push({ view: label, ...it, ratio: Math.round(r * 100) / 100, need: it.large ? 3 : 4.5 });
  }
}
async function scan(page, label, results) {
  const height = await page.evaluate(() => document.documentElement.scrollHeight);
  const vh = page.viewportSize().height;
  for (let y = 0; y < height; y += Math.floor(vh * 0.8)) {
    await page.evaluate((yy) => window.scrollTo(0, yy), y); await page.waitForTimeout(120);
    await auditViewport(page, label, results);
  }
  await page.evaluate(() => window.scrollTo(0, 0));
}

const browser = await chromium.launch({ executablePath: exe });
const results = [];
for (const [vp, viewport] of [["desktop", { width: 1440, height: 900 }], ["mobile", { width: 390, height: 844 }]]) for (const theme of ["light", "dark"]) {
  const ctx = await browser.newContext({ viewport, reducedMotion: "reduce" });
  await ctx.addInitScript((t) => localStorage.setItem("jyotai-theme", t), theme);
  const page = await ctx.newPage();
  await page.goto(process.argv[3] ?? "http://127.0.0.1:5173/"); await page.waitForLoadState("networkidle");
  await scan(page, `${vp}/${theme}/home`, results);
  for (const [t, v] of [["Name", "Synthetic Test"], ["Date of Birth", "2000-01-01"], ["Time of Birth", "12:00"]]) await field(page, t).fill(v);
  await page.getByPlaceholder("Search city, town, or address").fill("Test Location");
  await page.locator(".advanced-details summary").click();
  for (const [t, v] of [["Selected timezone", "UTC"], ["Latitude", "0"], ["Longitude", "0"], ["As-of date", "2026-10-30"], ["As-of time", "00:00"], ["As-of timezone", "UTC"]]) await field(page, t).fill(v);
  await page.getByRole("button", { name: "Create My Horoscope" }).click();
  await page.locator("#profile-heading").waitFor({ timeout: 30000 });
  await page.evaluate(() => document.querySelectorAll("details").forEach((d) => { d.open = true; }));
  await scan(page, `${vp}/${theme}/chart`, results);
  await page.evaluate(() => { location.hash = "#ask-jyotishai"; });
  await page.locator("#question").fill("How will my career be in 2027?");
  await page.locator("#question").press("Enter");
  await page.locator(".consultation-turn").first().waitFor({ timeout: 30000 });
  await page.locator("#question").fill("Which Dasha applies?");
  await page.evaluate(() => document.querySelectorAll("details").forEach((d) => { d.open = true; }));
  await page.waitForTimeout(300);
  await scan(page, `${vp}/${theme}/consultation`, results);
  await ctx.close();
}
await browser.close();
// de-duplicate identical element/text/view, keep worst
const key = (r) => `${r.view}|${r.cls}|${r.text}`;
const worst = new Map(); for (const r of results) if (!worst.has(key(r)) || worst.get(key(r)).ratio > r.ratio) worst.set(key(r), r);
const all = [...worst.values()];
const scored = all.filter((r) => !r.decorative && !r.disabled);
const fails = scored.filter((r) => r.ratio < r.need);
fs.writeFileSync(process.argv[2], JSON.stringify({ checked: scored.length, exempt: all.length - scored.length, fails, all }, null, 1));
const byView = {}; for (const r of scored) { const v = (byView[r.view] ??= { n: 0, fail: 0, min: 99 }); v.n++; if (r.ratio < r.need) v.fail++; v.min = Math.min(v.min, r.ratio); }
console.table(byView);
console.log(`checked ${scored.length} text elements, ${fails.length} below AA (decorative/disabled exempt: ${all.length - scored.length})`);
for (const f of fails.sort((a, b) => a.ratio - b.ratio).slice(0, 60)) console.log(f.ratio, "<", f.need, f.view, f.cls, JSON.stringify(f.text), f.color);
