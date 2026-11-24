# Frontend visual system

## Colour system (NEXT-UI-AMBER, 2026-11-24)

Saffron, amber and gold are the primary accent (sunrise, temple brass, diya light); indigo is
depth and background; turquoise is a sparing secondary; violet is only a subtle tint (the
decorative wheel's outer halo and the Moon/Rahu planet hues).

All colour lives in design tokens. `apps/web/src/theme/tokens.css` is the only file allowed to
contain colour literals; every stylesheet and component uses `var(--…)`. Two layers:

1. **Primitives**, fixed ramps: `indigo`, `amber`, `saffron`, `maroon`, `turquoise`, `violet`,
   `parchment` (warm neutrals), plus `rose` and `sage` (planet hues only).
2. **Semantics**, `--ui-*` and `--planet-*`, with light values on `:root` /
   `[data-theme="light"]` / `[data-preview-theme="light"]` and dark values on the dark
   selectors. The app shell's `--bg`, `--surface`, `--text`, `--muted`, `--gold`, `--violet`,
   `--teal`, `--chart-*` and planet tones resolve to these.

`apps/web/src/theme/components.css` is imported last and assigns semantic colours to key
components (primary buttons, chips, composer, question bubble, Dasha periods, wheel, chart-room
labels). It sets colour, background, border colour, shadow and outline only, never layout.

| Primitive ramp | Steps |
| --- | --- |
| `--indigo` | `950` #070a1c · `900` #0c1030 · `850` #11163c · `800` #181d4b · `700` #252b62 · `600` #353c7b · `500` #4c5390 · `400` #6c73a9 · `300` #959bc5 · `200` #c1c4df · `100` #e2e4f0 · `50` #f1f2f8 |
| `--amber` | `50` #fff8e6 · `100` #fdedc7 · `200` #f9dc98 · `300` #f4c566 · `400` #eeae3d · `500` #d9941f · `600` #b87714 · `700` #8f5a10 · `800` #6a420f · `900` #44290a |
| `--saffron` | `50` #fff3e8 · `100` #fde1c8 · `200` #f9c495 · `300` #f4a35e · `400` #eb8634 · `500` #d26c1a · `600` #9e4c0f · `700` #86400f · `800` #5f2e0c |
| `--maroon` | `50` #fcf1ef · `100` #f6dcd8 · `200` #ebb5ae · `300` #db8a82 · `400` #c4625b · `500` #a3443f · `600` #842f30 · `700` #682227 · `800` #4b181d · `900` #2e0f13 |
| `--turquoise` | `50` #eafaf7 · `100` #c9f0ea · `200` #9be2d8 · `300` #66cfc2 · `400` #36b3a6 · `500` #1d958a · `600` #127870 · `700` #0d5d57 · `800` #0a433f |
| `--violet` | `100` #ece7f4 · `200` #d8cfe8 · `300` #b3a5d1 · `500` #6b5a98 · `700` #3a2f5c · `900` #1c1633 |
| `--parchment` | `0` #fffdf8 · `50` #fcf7ec · `100` #f6eedc · `200` #ece0c6 · `300` #dccaa6 · `400` #bfa984 · `500` #93805f · `600` #655640 · `700` #514533 · `800` #362e22 · `900` #211c14 |
| `--rose`, `--sage` | rose `200` #e9a6bd · `600` #9b3f63; sage `200` #b4cf95 · `600` #56703c |

| Semantic token | Light | Dark |
| --- | --- | --- |
| `--ui-bg` / `--ui-bg-2` | parchment-50 #fcf7ec / parchment-100 #f6eedc | indigo-950 #070a1c / indigo-900 #0c1030 |
| `--ui-surface` / `--ui-surface-2` | parchment-0 #fffdf8 / parchment-100 #f6eedc | indigo-850 #11163c / indigo-800 #181d4b |
| `--ui-sidebar` | parchment-0 #fffdf8 | indigo-950 #070a1c |
| `--ui-text` | indigo-900 #0c1030 | parchment-50 #fcf7ec |
| `--ui-muted` | parchment-600 #655640 | 70% parchment-100 + indigo-300 (#d9d5d5) |
| `--ui-accent` / `--ui-accent-hover` | amber-400 #eeae3d / amber-300 #f4c566 | same |
| `--ui-accent-ink` (text on amber) | indigo-950 #070a1c | same |
| `--ui-accent-text` | saffron-600 #9e4c0f | amber-300 #f4c566 |
| `--ui-accent-deep` | maroon-600 #842f30 | amber-200 #f9dc98 |
| `--ui-accent-soft` | 16% amber-400 on surface | 14% amber-400 on surface |
| `--ui-secondary` | turquoise-700 #0d5d57 | turquoise-300 #66cfc2 |
| `--ui-focus` | saffron-600 #9e4c0f | amber-300 #f4c566 |
| `--ui-line` / `--ui-rule` | 20% parchment-700 / amber-300 | 14% amber-200 / 45% amber-400 |
| `--ui-chart-line` / `--ui-chart-fill` | parchment-500 / parchment-0 | parchment-400 / indigo-850 |
| `--ui-glow`, `--ui-card-tint`, `--ui-shadow` | amber 22% / amber 6% / parchment-800 12% | amber 28% / amber 4% / indigo-950 40% |
| `--planet-*` (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu) | saffron-600, violet-500, maroon-500, turquoise-600, amber-700, rose-600, indigo-500, violet-700, sage-600 | saffron-300, violet-200, maroon-300, turquoise-300, amber-300, rose-200, indigo-300, violet-300, sage-200 |

The decorative wheel's zodiac glyphs render as gold text (U+FE0E, `font-variant-emoji: text`,
a symbol-font stack); they are absolutely positioned SVG, so this cannot move layout. The sign
glyphs in the profile strip and transit cards still render as the operating system's colour
emoji (violet tiles on Apple platforms): text presentation there changes line-box heights
(transit cards 191 → 186 px), so it is left for a change that may adjust layout.

**Layout unchanged.** `apps/web/scripts/visual/layout-diff.mjs` records every element's box,
font and padding. Production builds of `0cb1d08` and the NEXT-UI-AMBER result are identical on
home, chart and consultation at 1440 and 390 px, apart from the 12 wheel glyphs. (The dev
server orders CSS differently from the production bundle, e.g. the composer label is 21 px in
dev and 14.4 px in production; this predates NEXT-UI-AMBER.)

**Guards.** `src/theme/tokens.test.ts` fails on any hex, `rgb()`/`hsl()`-family function or named
colour outside `tokens.css`, on an undefined token, on a semantic token missing from either
theme, and if the HTML `theme-color` drifts from `--indigo-950`. `src/theme/contrast.test.ts`
checks every semantic text pair against WCAG AA (4.5:1; focus ring 3:1) in both themes.

## Views

The D1, D9, and D10 diagrams read house, sign, and planet placements from the context response. Planet colors distinguish markers visually; the expandable house list gives the same placements in text. D9 and D10 remain factual displays.

The active Vimshottari view shows the supplied Mahadasha and Antardasha as nested periods, with progress calculated from their supplied timestamps. Calendar dates use the birth profile's IANA timezone. Exact timestamps remain available in the technical section. The progress bar is elapsed time, not a strength or outcome score.

Consultation cards display the supplied answer, calculated facts, reviewed wording, timing context, and limitations in that order. Claim and rule IDs remain available in expandable evidence. Clarification choices submit the actual approved claim IDs to the consultation endpoint. No interpretation is calculated in the browser.

When the backend supplies a multi-period Dasha follow-up, the conversation shows each supplied overlap as a readable period card with minute-level local timestamps. The unaltered reply, including exact UTC precision, remains in an expandable technical section.

## Visual acceptance status

**Rendered contrast audit (NEXT-UI-AMBER).** `apps/web/scripts/visual/contrast-audit.mjs` drives
headless Chromium through the synthetic profile below at 1440 × 900 and 390 × 844, in light and
dark, over the home page, the chart room and a Career consultation answer (every `<details>`
expanded). For each visible, unoccluded text element it screenshots the page with text made
transparent, samples the real background under the text box (gradients included), composites
the computed text colour and opacity, and compares the 10th-percentile ratio with WCAG AA
(4.5:1; 3:1 for large text). Disabled controls and `aria-hidden` decoration are exempt.
Result: **0 of 1,732** text elements below AA (minimum 4.52:1). The same audit on the previous
palette (`main` at `0cb1d08`): **241 of 1,730** below AA, including pale Dasha-card labels in
the light theme and an `!important` light-theme eyebrow colour leaking into dark.

Before/after screenshots (synthetic data): `docs/design/screenshots/next-ui-amber/{before,after}/`,
`home-` and `consultation-` × `desktop`/`mobile` × `light`/`dark`. Regenerate with
`apps/web/scripts/visual/screenshots.mjs`. Both scripts need the API and Vite dev server running
and `npm i --no-save playwright pngjs`; set `CHROME_PATH` to use a local Chromium. A person's
review on a real device (below) remains the acceptance step.

### Mac screenshot and acceptance procedure

1. In `apps/api`, run `uv run uvicorn astrologer.main:app --host 127.0.0.1 --port 8000`. In `apps/web`, run `npm run dev -- --host 127.0.0.1`. Open `http://127.0.0.1:5173/` in Chrome on a Mac.
2. Use Chrome DevTools (`⌘⌥I`), then its device toolbar (`⌘⇧M`). Set the viewport to **1440 × 900**, **768 × 1024**, and **390 × 844** in turn. For each width, use the app's theme toggle to review **light and dark**. In DevTools' command menu (`⌘⇧P`), run **Capture full size screenshot** for each theme and width. Name files `jyotai-1440-light.png`, `jyotai-1440-dark.png`, and likewise for 768 and 390.
3. Use synthetic input only: name `Synthetic Test`, birth date `2000-01-01`, time `12:00`, place `Test Location`; in Advanced location details enter timezone `UTC`, latitude `0`, longitude `0`, as-of date `2026-10-30`, time `00:00`, timezone `UTC`. The manual place values work without a location service key.
4. At every width and theme, inspect the landing/profile, D1, D9, D10, planetary rows, Dasha timeline, Career consultation, follow-up conversation, and expanded evidence. Ask `How will my career be in 2027?`, then `Which Dasha applies?` and `What about 2028?`. Check that the result remains limited to the supplied evidence.
5. In the 390px viewport, verify no page-level horizontal scroll (`document.documentElement.scrollWidth <= window.innerWidth` in the DevTools console), legible planet abbreviations and house list, visible focus rings, and touch-friendly controls. Check the same views with reduced motion enabled in DevTools' Rendering panel. Record any clipping, overlap, low contrast, or unusable control before approving visual acceptance.
