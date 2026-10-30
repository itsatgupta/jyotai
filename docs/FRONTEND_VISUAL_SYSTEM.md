# Frontend visual system

The frontend uses `apps/web/src/celestial-ui.css` as its final visual layer. Its light and dark tokens cover surfaces, text, borders, focus, chart ink, and shadows. Royal indigo, violet, turquoise, saffron, and gold give the product its celestial character without external image assets or runtime dependencies.

The D1, D9, and D10 diagrams read house, sign, and planet placements from the context response. Planet colors distinguish markers visually; the expandable house list gives the same placements in text. D9 and D10 remain factual displays.

The active Vimshottari view shows the supplied Mahadasha and Antardasha as nested periods, with progress calculated from their supplied timestamps. Calendar dates use the birth profile's IANA timezone. Exact timestamps remain available in the technical section. The progress bar is elapsed time, not a strength or outcome score.

Consultation cards display the supplied answer, calculated facts, reviewed wording, timing context, and limitations in that order. Claim and rule IDs remain available in expandable evidence. Clarification choices submit the actual approved claim IDs to the consultation endpoint. No interpretation is calculated in the browser.

When the backend supplies a multi-period Dasha follow-up, the conversation shows each supplied overlap as a readable period card with minute-level local timestamps. The unaltered reply, including exact UTC precision, remains in an expandable technical section.

## Visual acceptance status

**VISUAL_ACCEPTANCE_PENDING.** The frontend build and DOM tests pass, and a synthetic request works through the local Vite proxy. This environment could not capture or inspect a rendered browser viewport: headless Chrome exited with code 134 and Safari could not launch. No desktop, tablet, mobile, light, or dark screenshot has been approved. This commit is implementation work awaiting visual QA, not a production release approval.

### Mac screenshot and acceptance procedure

1. In `apps/api`, run `uv run uvicorn astrologer.main:app --host 127.0.0.1 --port 8000`. In `apps/web`, run `npm run dev -- --host 127.0.0.1`. Open `http://127.0.0.1:5173/` in Chrome on a Mac.
2. Use Chrome DevTools (`⌘⌥I`), then its device toolbar (`⌘⇧M`). Set the viewport to **1440 × 900**, **768 × 1024**, and **390 × 844** in turn. For each width, use the app's theme toggle to review **light and dark**. In DevTools' command menu (`⌘⇧P`), run **Capture full size screenshot** for each theme and width. Name files `jyotai-1440-light.png`, `jyotai-1440-dark.png`, and likewise for 768 and 390.
3. Use synthetic input only: name `Synthetic Test`, birth date `2000-01-01`, time `12:00`, place `Test Location`; in Advanced location details enter timezone `UTC`, latitude `0`, longitude `0`, as-of date `2026-10-30`, time `00:00`, timezone `UTC`. The manual place values work without a location service key.
4. At every width and theme, inspect the landing/profile, D1, D9, D10, planetary rows, Dasha timeline, Career consultation, follow-up conversation, and expanded evidence. Ask `How will my career be in 2027?`, then `Which Dasha applies?` and `What about 2028?`. Check that the result remains limited to the supplied evidence.
5. In the 390px viewport, verify no page-level horizontal scroll (`document.documentElement.scrollWidth <= window.innerWidth` in the DevTools console), legible planet abbreviations and house list, visible focus rings, and touch-friendly controls. Check the same views with reduced motion enabled in DevTools' Rendering panel. Record any clipping, overlap, low contrast, or unusable control before approving visual acceptance.
