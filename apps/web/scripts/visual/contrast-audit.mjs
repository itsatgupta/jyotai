// node scripts/visual/contrast-audit.mjs <outJson> [baseUrl]
// WCAG AA text-contrast audit (NEXT-UI-VIOLET-02 method), light + dark, 1440 x 900 + 390 x 844, on
// home, the chart dashboard (every <details> open), a Career answer with a follow-up typed, and a
// Wealth answer with the provisional toggle on. Synthetic birth only. Needs the API + Vite.
//
// Browser: pinned in audit-browser.json (Playwright's bundled Chromium); any other version aborts
// unless AUDIT_ANY_CHROMIUM=1.
//
// Background = computed styles, not a screenshot. At 6 points inside each text box the audit takes
// document.elementsFromPoint() (pointer-events forced on, so decorative layers count) and
// composites, bottom-up, every layer under the text: background-color, every gradient colour stop
// (each stop is a candidate, so the worst case over the gradient is used), inset box-shadow colours
// (with and without), the layer's own opacity, and filled SVG shapes. The reported ratio is the
// worst candidate over all points. Only when a point lies over a raster image (url() background,
// <img>, <canvas>, <video>) or an SVG paint server (fill: url(#…)) does the audit fall back to a
// pixel sample, taken from a screenshot after it has verified that text is actually transparent
// (the earlier pixel method sampled frames where the hiding stylesheet had not applied yet, giving
// impossible 1.0:1 readings). Text colour = computed colour (fill for SVG text, ::placeholder for
// empty fields), alpha x ancestor opacity. Disabled controls and aria-hidden decoration are exempt.
import { chromium } from "playwright";
import { PNG } from "pngjs";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const pin = JSON.parse(fs.readFileSync(new URL("./audit-browser.json", import.meta.url), "utf8"));
const exe = process.env.CHROME_PATH ?? path.join(os.homedir(), "Library/Caches/ms-playwright", `chromium_headless_shell-${pin.chromiumRevision}`, "chrome-headless-shell-mac-arm64/chrome-headless-shell");
const field = (page, text) => page.locator("label", { has: page.locator(`xpath=./span[starts-with(normalize-space(.), "${text}") and (normalize-space(.) = "${text}" or substring-after(normalize-space(.), "${text}") = "Optional" or substring-after(normalize-space(.), "${text}") = "*")]`) }).locator("input").first();
const lum = ([r, g, b]) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }; return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };

// Runs in the page: text elements plus, per sample point, the candidate backdrop colours.
function collectInPage() {
  const canvas = document.createElement("canvas"); canvas.width = canvas.height = 1;
  const g2d = canvas.getContext("2d", { willReadFrequently: true });
  const cache = new Map();
  const parse = (s) => {
    if (cache.has(s)) return cache.get(s);
    let out = null;
    const m = s.match(/^rgba?\(([^)]+)\)$/);
    const c = s.match(/^color\(srgb ([^)]+)\)$/);
    if (s === "transparent") out = [0, 0, 0, 0];
    else if (m) { const p = m[1].split(/[ ,/]+/).filter(Boolean).map(Number); out = [p[0], p[1], p[2], p[3] ?? 1]; }
    else if (c) { const p = c[1].split(/[ /]+/).filter(Boolean).map(Number); out = [p[0] * 255, p[1] * 255, p[2] * 255, p[3] ?? 1]; }
    else { g2d.clearRect(0, 0, 1, 1); g2d.fillStyle = "#000"; g2d.fillStyle = s; g2d.fillRect(0, 0, 1, 1); const d = g2d.getImageData(0, 0, 1, 1).data; out = [d[0], d[1], d[2], d[3] / 255]; }
    cache.set(s, out); return out;
  };
  const COLOR = /(?:rgba?|color|oklch|oklab|lab|lch|hsla?|hwb)\([^()]*\)|transparent/g;
  const splitTop = (s) => { const parts = []; let depth = 0, cur = ""; for (const ch of s) { if (ch === "(") depth++; if (ch === ")") depth--; if (ch === "," && depth === 0) { parts.push(cur.trim()); cur = ""; } else cur += ch; } if (cur.trim()) parts.push(cur.trim()); return parts; };
  const over = (top, base) => { const a = top[3]; return [0, 1, 2].map((i) => top[i] * a + base[i] * (1 - a)); };
  const prune = (list) => { const seen = new Map(); for (const c of list) seen.set(c.map((v) => Math.round(v)).join(","), c); let out = [...seen.values()]; if (out.length > 48) { out.sort((p, q) => p[0] * .3 + p[1] * .6 + p[2] * .1 - (q[0] * .3 + q[1] * .6 + q[2] * .1)); out = out.filter((_, i) => i % Math.ceil(out.length / 48) === 0 || i === out.length - 1); } return out; };
  const pseudoCache = new Map();
  const paintedPseudo = (el) => {
    if (!pseudoCache.has(el)) pseudoCache.set(el, ["::before", "::after"].some((p) => { const ps = getComputedStyle(el, p); return ps.content !== "none" && ps.display !== "none" && (parse(ps.backgroundColor)[3] > 0 || ps.backgroundImage !== "none"); }));
    return pseudoCache.get(el);
  };
  // One element's paint as alternative layer stacks (bottom first): solid colours only, plus
  // with/without each inset shadow that covers the point. null = this point needs a pixel read.
  const opCache = new Map();
  const effectiveOpacity = (el) => { if (!el || el.nodeType !== 1) return 1; if (!opCache.has(el)) opCache.set(el, parseFloat(getComputedStyle(el).opacity) * effectiveOpacity(el.parentElement)); return opCache.get(el); };
  const layersOf = (el, point) => {
    const cs = getComputedStyle(el);
    const op = effectiveOpacity(el);
    if (el instanceof SVGElement && !(el instanceof SVGSVGElement)) {
      if (el instanceof SVGTextElement || el instanceof SVGTSpanElement) return [];
      const fill = cs.fill;
      if (!fill || fill === "none") return [];
      if (fill.startsWith("url(")) return null;
      const c = parse(fill); return [[[c[0], c[1], c[2], c[3] * parseFloat(cs.fillOpacity) * op]]];
    }
    if (el.matches("img,canvas,video,picture,iframe")) return null;
    if (cs.backgroundImage !== "none") return null; // gradient or image: read the verified pixel
    if (paintedPseudo(el)) return null;
    const stacks = [[]];
    const bg = parse(cs.backgroundColor);
    if (bg[3] > 0) stacks[0].push([bg[0], bg[1], bg[2], bg[3] * op]);
    if (cs.boxShadow !== "none") {
      const r = el.getBoundingClientRect();
      for (const sh of splitTop(cs.boxShadow).filter((x) => /\binset\b/.test(x))) {
        const c = (sh.match(COLOR) ?? []).map(parse)[0]; if (!c || c[3] === 0) continue;
        // An inset shadow paints outside its "hole": the box moved by the offset and shrunk by the
        // spread. Within the blur its alpha fades, so a covered point gets both candidates.
        const [ox = 0, oy = 0, blur = 0, spread = 0] = (sh.replace(COLOR, "").match(/-?[\d.]+px/g) ?? []).map(parseFloat);
        const inset = spread + blur;
        const inHole = point.x > r.left + ox + inset && point.x < r.right + ox - inset && point.y > r.top + oy + inset && point.y < r.bottom + oy - inset;
        if (inHole) continue;
        const n = stacks.length; for (let i = 0; i < n && stacks.length < 128; i++) stacks.push([...stacks[i], [c[0], c[1], c[2], c[3] * op]]);
      }
    }
    return stacks;
  };
  const selector = (el) => {
    const parts = [];
    for (let a = el; a && a !== document.body && parts.length < 3; a = a.parentElement) {
      const cls = typeof a.className === "string" ? a.className : a.className?.baseVal ?? "";
      const c = cls.split(/\s+/).filter((x) => x && !x.startsWith("tone-") && x !== "astro-glyph").slice(0, 2).map((x) => "." + x).join("");
      parts.unshift(a.tagName.toLowerCase() + (a.id ? "#" + a.id : "") + c);
      if (a.id) break;
    }
    return parts.join(" > ");
  };

  const force = document.createElement("style"); force.textContent = "*{pointer-events:auto!important}"; // added after occlusion checks
  const items = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
  const candidates = [];
  for (let el = walker.currentNode; el; el = walker.nextNode()) {
    if (!(el instanceof Element)) continue;
    const own = [...el.childNodes].filter((n) => n.nodeType === 3 && n.textContent.trim()).map((n) => n.textContent.trim()).join(" ");
    const isField = el.matches("input:not([type=hidden],[type=checkbox],[type=radio],[type=range],[type=color],[type=file]),textarea") && (el.value || el.placeholder);
    if (!own && !isField) continue;
    const full = el.getBoundingClientRect();
    const top = Math.max(0, full.top), bottom = Math.min(innerHeight, full.bottom);
    if (full.width < 2 || bottom - top < 8 || full.right <= 0 || full.left >= innerWidth) continue;
    const cs = getComputedStyle(el);
    if (cs.visibility === "hidden" || cs.display === "none") continue;
    // content of a closed <details> keeps a layout box but is not rendered (content-visibility)
    if (!el.checkVisibility({ contentVisibilityAuto: true, visibilityProperty: true })) continue;
    if (el.closest(".sr-only,.orbit-instructions")) continue;
    let op = 1; for (let a = el; a; a = a.parentElement) op *= parseFloat(getComputedStyle(a).opacity);
    if (op < 0.05) continue;
    const box = { left: Math.max(0, full.left), right: Math.min(innerWidth, full.right), top, bottom };
    const cx = (box.left + box.right) / 2, cy = (top + bottom) / 2;
    const hit = document.elementFromPoint(Math.min(innerWidth - 1, cx), Math.min(innerHeight - 1, cy));
    if (!hit || !(el === hit || el.contains(hit) || hit.contains(el))) continue;
    candidates.push({ el, own, isField, cs, op, box });
  }
  document.head.append(force);
  for (const { el, own, isField, cs, op, box } of candidates) {
    const decorative = Boolean(el.closest("[aria-hidden=true],svg"));
    const disabled = Boolean(el.closest(":disabled,[aria-disabled=true]"));
    const px = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight, 10) >= 700;
    const placeholder = isField && !el.value;
    const colorStr = placeholder ? getComputedStyle(el, "::placeholder").color : (el instanceof SVGElement ? cs.fill : (cs.webkitTextFillColor && cs.webkitTextFillColor !== cs.color ? cs.webkitTextFillColor : cs.color));
    const color = parse(colorStr);
    // Sample inside the text's own line boxes (not the padding box, which can hold accent bars or
    // icons); for form fields, inside the content box.
    let rects = [];
    if (isField) { const pl = parseFloat(cs.paddingLeft) + parseFloat(cs.borderLeftWidth), pr = parseFloat(cs.paddingRight) + parseFloat(cs.borderRightWidth); rects = [{ left: box.left + pl, right: box.right - pr, top: box.top + parseFloat(cs.paddingTop), bottom: box.bottom - parseFloat(cs.paddingBottom) }]; }
    else for (const t of [...el.childNodes].filter((n) => n.nodeType === 3 && n.textContent.trim())) { const r = document.createRange(); r.selectNodeContents(t); rects.push(...r.getClientRects()); }
    rects = rects.map((r) => ({ left: Math.max(0, r.left), right: Math.min(innerWidth, r.right), top: Math.max(0, r.top), bottom: Math.min(innerHeight, r.bottom) })).filter((r) => r.right - r.left >= 1 && r.bottom - r.top >= 4);
    if (!rects.length) continue;
    const grid = [];
    const per = Math.max(1, Math.floor(24 / rects.length));
    const cols = Math.max(1, Math.ceil(per / 2)), rows = per >= 2 ? 2 : 1;
    for (const r of rects.slice(0, 24)) for (let i = 1; i <= cols; i++) for (let j = 1; j <= rows; j++) grid.push([r.left + (r.right - r.left) * i / (cols + 1), r.top + (r.bottom - r.top) * j / (rows + 1)]);
    const points = [];
    for (const [gx, gy] of grid) {
      const x = Math.min(innerWidth - 1, gx), y = Math.min(innerHeight - 1, gy);
      const stack = document.elementsFromPoint(x, y);
      const at = stack.indexOf(el);
      if (at < 0 && !stack.some((n) => el.contains(n))) continue; // clipped here (e.g. a scroller)
      // layers under the text: the element itself and everything painted beneath it
      const below = (at >= 0 ? stack.slice(at) : stack.slice(stack.findIndex((n) => !el.contains(n)))).filter((n) => !el.contains(n) || n === el).reverse();
      // top-down from the text: stop at the first opaque solid background (nothing under it shows)
      const used = [];
      let pixel = false;
      for (const n of [...below].reverse()) {
        const stacks = layersOf(n, { x, y });
        if (stacks === null) { pixel = true; break; }
        used.push(stacks);
        if (stacks.every((st) => st.length && st[0][3] >= 1)) break;
      }
      let set = [[255, 255, 255]];
      if (!pixel) for (const stacks of used.reverse()) {
        if (!stacks.length || !stacks[0].length && stacks.length === 1) continue;
        const next = [];
        for (const base of set) for (const s of stacks) next.push(s.reduce((acc, layer) => over(layer, acc), base));
        set = prune(next);
      }
      points.push({ x, y, pixel, bgs: pixel ? [] : set });
    }
    if (!points.length) continue; // fully clipped
    const pixels = points.filter((p) => p.pixel).length;
    const tag = `a${items.length}`;
    items.push({ tag, sel: selector(el), text: (own || el.value || el.placeholder).slice(0, 60), color, colorStr, op, large: px >= 24 || (px >= 18.66 && bold), decorative, disabled, placeholder, pixels, points, box: [box.left, box.top, box.right - box.left, box.bottom - box.top] });
  }
  force.remove();
  return items;
}

const CROSSCHECK = process.env.AUDIT_CROSSCHECK === "1"; // also read pixels at computed-style points
async function pixelBackdrops(page, items) {
  const need = CROSSCHECK ? items : items.filter((it) => it.pixels > 0);
  if (!need.length) return;
  // Inline !important beats every stylesheet rule (a stylesheet `*{color:transparent!important}`
  // loses to more specific !important rules); the previous inline values are restored afterwards.
  await page.evaluate(async () => {
    window.__auditSaved = [];
    for (const n of document.querySelectorAll("body, body *")) {
      window.__auditSaved.push([n, n.getAttribute("style")]);
      n.style.setProperty("transition", "none", "important");
      n.style.setProperty("color", "transparent", "important");
      n.style.setProperty("-webkit-text-fill-color", "transparent", "important");
      n.style.setProperty("text-shadow", "none", "important");
      n.style.setProperty("caret-color", "transparent", "important");
      if (n instanceof SVGTextElement || n instanceof SVGTSpanElement) n.style.setProperty("fill", "transparent", "important");
    }
    const s = document.createElement("style"); s.id = "audit-hide"; s.textContent = "*::placeholder{color:transparent!important}"; document.head.append(s);
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  });
  const ok = await page.evaluate(() => [...document.querySelectorAll("body, body *")].filter((n) => n.checkVisibility({ contentVisibilityAuto: true })).every((n) => { const cs = getComputedStyle(n); return cs.color === "rgba(0, 0, 0, 0)" && cs.webkitTextFillColor === "rgba(0, 0, 0, 0)"; }));
  if (!ok) throw new Error("text did not become transparent; refusing to sample pixels");
  const png = PNG.sync.read(await page.screenshot());
  await page.evaluate(() => {
    document.getElementById("audit-hide")?.remove();
    for (const [n, saved] of window.__auditSaved) { if (saved === null) n.removeAttribute("style"); else n.setAttribute("style", saved); }
    delete window.__auditSaved;
  });
  for (const it of need) for (const p of it.points) {
    const k = (Math.floor(p.y) * png.width + Math.floor(p.x)) * 4;
    const px = [png.data[k], png.data[k + 1], png.data[k + 2]];
    if (p.pixel) p.bgs = [px]; else p.px = px;
  }
}

function score(it, view) {
  const a = it.color[3] * it.op;
  // per point: worst candidate backdrop; per element: 10th percentile over the 24 points, so one
  // star dot or hairline under a single point cannot decide the result
  const perPoint = it.points.map((p) => Math.min(...p.bgs.map((bg) => ratio([0, 1, 2].map((q) => it.color[q] * a + bg[q] * (1 - a)), bg)))).filter(Number.isFinite).sort((x, y) => x - y);
  const worst = perPoint.length ? perPoint[Math.floor(perPoint.length * 0.1)] : Infinity;
  let crossDiff;
  if (CROSSCHECK && it.pixels === 0) {
    const pxs = it.points.filter((p) => p.px).map((p) => ratio([0, 1, 2].map((q) => it.color[q] * a + p.px[q] * (1 - a)), p.px)).sort((x, y) => x - y);
    if (pxs.length) crossDiff = Math.round((pxs[Math.floor(pxs.length * 0.1)] - worst) * 100) / 100;
  }
  const { points, color, ...rest } = it;
  const method = it.pixels === 0 ? "styles" : it.pixels === points.length ? "pixels" : "mixed";
  return { view, ...rest, method, crossDiff, ratio: Math.round(worst * 100) / 100, need: it.large ? 3 : 4.5 };
}

async function scan(page, label, results) {
  const height = await page.evaluate(() => document.documentElement.scrollHeight);
  const vh = page.viewportSize().height;
  for (let y = 0; y < height; y += Math.floor(vh * 0.8)) {
    await page.evaluate((yy) => window.scrollTo(0, yy), y);
    await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
    const items = await page.evaluate(collectInPage);
    await pixelBackdrops(page, items);
    for (const it of items) results.push(score(it, label));
  }
  await page.evaluate(() => window.scrollTo(0, 0));
}

// Canary: two planted texts with a known ratio, one on a solid colour (computed-style path) and one
// on a gradient (pixel path). The run aborts unless both are measured correctly and flagged.
const CANARY_FG = [153, 153, 153], CANARY_BG = [128, 128, 128];
async function canary(page) {
  await page.evaluate(([fg, bg]) => {
    const wrap = document.createElement("div"); wrap.id = "audit-canary";
    wrap.innerHTML = `<p style="position:fixed;left:8px;top:120px;z-index:2147483647;margin:0;padding:6px;font:16px sans-serif;color:rgb(${fg});background:rgb(${bg})">Canary solid</p><p style="position:fixed;left:8px;top:170px;z-index:2147483647;margin:0;padding:6px;font:16px sans-serif;color:rgb(${fg});background:linear-gradient(rgb(${bg}),rgb(${bg}))">Canary gradient</p>`;
    document.body.append(wrap);
  }, [CANARY_FG.join(","), CANARY_BG.join(",")]);
  const items = await page.evaluate(collectInPage);
  await pixelBackdrops(page, items);
  await page.evaluate(() => document.getElementById("audit-canary").remove());
  const expected = Math.round(ratio(CANARY_FG, CANARY_BG) * 100) / 100;
  for (const [text, method] of [["Canary solid", "styles"], ["Canary gradient", "pixels"]]) {
    const r = items.filter((it) => it.text === text).map((it) => score(it, "canary"))[0];
    if (!r || r.method !== method || Math.abs(r.ratio - expected) > 0.05 || r.ratio >= r.need) throw new Error(`canary "${text}" measured ${r ? `${r.ratio} via ${r.method}` : "nothing"}, expected ${expected} via ${method}`);
  }
}

async function profile(page) {
  for (const [t, v] of [["Name", "Synthetic Test"], ["Date of Birth", "2000-01-01"], ["Time of Birth", "12:00"]]) await field(page, t).fill(v);
  await page.getByPlaceholder("Search city, town, or address").fill("Test Location");
  await page.locator(".advanced-details summary").click();
  for (const [t, v] of [["Selected timezone", "UTC"], ["Latitude", "0"], ["Longitude", "0"], ["As-of date", "2026-10-30"], ["As-of time", "00:00"], ["As-of timezone", "UTC"]]) await field(page, t).fill(v);
  await page.getByRole("button", { name: "Create My Horoscope" }).click();
  await page.locator("#profile-heading").waitFor({ timeout: 30000 });
}
const openDetails = (page) => page.evaluate(() => document.querySelectorAll("details").forEach((d) => { d.open = true; }));

const browser = await chromium.launch({ executablePath: exe });
const chromiumVersion = browser.version();
if (chromiumVersion !== pin.chromiumVersion && process.env.AUDIT_ANY_CHROMIUM !== "1") {
  await browser.close();
  throw new Error(`Chromium ${chromiumVersion} is not the pinned ${pin.chromiumVersion} (audit-browser.json); set AUDIT_ANY_CHROMIUM=1 to run anyway`);
}
const base = process.argv[3] ?? "http://127.0.0.1:5173/";
const results = [];
for (const [vp, viewport] of [["desktop", { width: 1440, height: 900 }], ["mobile", { width: 390, height: 844 }]]) for (const theme of ["light", "dark"]) {
  const ctx = await browser.newContext({ viewport, reducedMotion: "reduce" });
  await ctx.addInitScript((t) => { localStorage.setItem("jyotai-theme", t); localStorage.setItem("jyotai-show-provisional", "off"); }, theme);
  const page = await ctx.newPage();
  await page.goto(base); await page.waitForLoadState("networkidle");
  await canary(page);
  await scan(page, `${vp}/${theme}/home`, results);
  await profile(page);
  await openDetails(page);
  await scan(page, `${vp}/${theme}/chart`, results);
  await page.evaluate(() => { location.hash = "#ask-jyotishai"; });
  await page.locator("#question").fill("How will my career be in 2027?");
  await page.locator("#question").press("Enter");
  await page.locator(".consultation-turn").first().waitFor({ timeout: 30000 });
  await page.locator("#question").fill("Which Dasha applies?");
  await openDetails(page);
  await page.waitForTimeout(300);
  await scan(page, `${vp}/${theme}/consultation`, results);
  await ctx.close();
  // Wealth with the provisional toggle on, in a fresh session (open item 20)
  const wctx = await browser.newContext({ viewport, reducedMotion: "reduce" });
  await wctx.addInitScript((t) => localStorage.setItem("jyotai-theme", t), theme);
  const wpage = await wctx.newPage();
  await wpage.goto(base); await wpage.waitForLoadState("networkidle");
  await profile(wpage);
  await wpage.evaluate(() => { location.hash = "#ask-jyotishai"; });
  await wpage.getByRole("switch", { name: "Show provisional interpretations (beta)" }).check();
  await wpage.locator("#question").fill("When will my wealth grow?");
  await wpage.locator("#question").press("Enter");
  await wpage.locator(".provisional-interpretations, .provisional-item").first().waitFor({ timeout: 30000 });
  await openDetails(wpage);
  await wpage.waitForTimeout(300);
  await canary(wpage);
  await scan(wpage, `${vp}/${theme}/wealth-provisional`, results);
  await wctx.close();
}
await browser.close();
// de-duplicate identical element/text/view, keep worst
const key = (r) => `${r.view}|${r.sel}|${r.text}`;
const worst = new Map(); for (const r of results) if (!worst.has(key(r)) || worst.get(key(r)).ratio > r.ratio) worst.set(key(r), r);
const all = [...worst.values()];
const scored = all.filter((r) => !r.decorative && !r.disabled);
const fails = scored.filter((r) => r.ratio < r.need).sort((a, b) => a.ratio - b.ratio);
const pixelCount = scored.filter((r) => r.method !== "styles").length;
fs.writeFileSync(process.argv[2], JSON.stringify({ chromium: chromiumVersion, method: "computed-styles@v2", checked: scored.length, exempt: all.length - scored.length, pixelFallback: pixelCount, fails, all }, null, 1));
const byView = {}; for (const r of scored) { const v = (byView[r.view] ??= { n: 0, fail: 0, min: 99 }); v.n++; if (r.ratio < r.need) v.fail++; v.min = Math.min(v.min, r.ratio); }
console.table(byView);
console.log(`Chromium ${chromiumVersion}: checked ${scored.length} text elements, ${fails.length} below AA (decorative/disabled exempt: ${all.length - scored.length}; pixel reads for gradient/image points: ${pixelCount})`);
if (CROSSCHECK) {
  const diffs = scored.filter((r) => r.crossDiff !== undefined);
  const off = diffs.filter((r) => Math.abs(r.crossDiff) > 0.25).sort((x, y) => Math.abs(y.crossDiff) - Math.abs(x.crossDiff));
  console.log(`cross-check: ${diffs.length} computed-style elements, ${off.length} differ from the pixel reading by > 0.25`);
  for (const r of off.slice(0, 30)) console.log("  ", r.crossDiff, r.ratio, r.view, r.sel, JSON.stringify(r.text));
}
for (const f of fails) console.log(f.ratio, "<", f.need, f.method, f.view, f.sel, JSON.stringify(f.text), f.colorStr);
