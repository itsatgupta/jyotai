# NEXT-UI-03: approved celestial design integration

## Preview to production mapping

| Approved preview | Live application |
| --- | --- |
| `preview/Preview.tsx` sidebar, top bar, hero, profile strip and footer | `App.tsx` uses the same structure and `preview.css` tokens; profile values come from `Context` |
| `preview/Preview.tsx` `OrbitArtwork` | Shared `components/OrbitArtwork.tsx`, imported by preview and live hero; artwork is decorative |
| Synthetic `Kundli` SVG | Existing `NorthIndianChart` with fixed North Indian house slots and supplied `Chart` houses and planets |
| Synthetic planet cards | `Workspace` cards derived from the selected D1, D9 or D10 `Chart.planets`; selection highlights the corresponding chart house and planet |
| Sample Dasha track | Existing `Workspace` Vimshottari period component, styled with the approved palette; dates and progress use `Context.active_dasha` |
| Sample consultation form and answer | Dedicated `QuestionAnalysis` chat workspace with a chronological message thread and persistent composer; content remains the API's governed response |

The preview remains at `/preview.html` for visual comparison. Its sample placements and answer copy are confined to `src/preview/`.

## Data and governance

- D1, D9 and D10 use their corresponding backend `Chart` objects. The UI does not recalculate or alter houses, signs, planetary positions, Lahiri settings, or node conventions.
- The selected planet card, detail panel, and chart highlight all read the same `Planet` object. Absent optional nakshatra fields stay absent in cards; no strength score or event prediction is derived.
- The active Mahadasha and Antardasha use backend lords and exact interval boundaries. Their local calendar dates use the birth profile timezone. Exact UTC instants remain in the collapsed technical details. Invalid or missing period data displays an unavailable state.
- Consultation answers and their evidence stay attached to the assistant message that returned them. The thread retains every turn in the open page, auto-scrolls to the latest answer, and keeps the composer available below the scrollable history. The five-turn career follow-up sequence is covered by frontend and backend regression tests.
- The consultation request, session ID, profile binding, claim ledger, source references, UNKNOWN and NO_MATCH distinction, and server expiry remain in the existing API and `QuestionAnalysis` flow. Claim clarification buttons send validated claim IDs and the reference turn ID. An expired server session disables the composer and offers New Consultation; changing the profile clears the prior conversation. No preview answer is used in production.
- The rotating zodiac wheel never contains chart data. North Indian chart geometry stays in its own SVG and does not receive rotation transforms.

## Known location issue

City autocomplete, including selection of Meerut, remains a separate **NEXT-LOC-01** defect. The existing manual latitude, longitude and timezone fields remain available under advanced location details. Do not assume or guess coordinates.

## Mac visual review still required

Automated screenshot attempts on this Mac did not render: headless Google Chrome exited 134 and Safari WebDriver exited 1. No screenshot or visual approval is claimed. Use these steps on the Mac:

1. Run `uv run uvicorn astrologer.main:app --host 127.0.0.1 --port 8000` from `apps/api`, then `npm run dev -- --host 127.0.0.1 --port 5173` from `apps/web`. If the ports are occupied, use the displayed Vite port and confirm its `/api` proxy points to the intended API.
2. Open `/preview.html` and `/` in separate browser tabs. Set responsive widths to **1440**, **768**, and **390** pixels. At each width, inspect dark and light modes, the celestial hero, wheel controls, sidebar or mobile navigation, profile strip, chart, planet cards, Dasha, consultation, and footer. Inspect contrast, clipping, focus indicators, and touch targets.
3. Create a synthetic profile using a selected city suggestion or the manual location fields. Confirm the profile values are calculated, then switch D1, D9 and D10. Select a planet card in each view and compare its sign and house with the chart and technical row. Rotate the decorative wheel by drag, touch, arrows, buttons and Reset; verify the Kundli does not rotate. Test Pause/Play and reduced motion.
4. Inspect active Mahadasha and Antardasha lords and local boundaries against the expanded exact UTC details. Navigate to consultation. Ask `How will my career be in 2027?`, `Why did you say that?`, `Which Dasha applies?`, `What about next year?`, and `Is next year better?`. Expand evidence and verify claim IDs and sources. Confirm unsupported predictions are limited. Test a new consultation and a changed profile to ensure old context is not reused.
5. Capture screenshots of both tabs at all six width and theme combinations before approving the visual match. Recheck the 390 pixel layout with actual touch input if available.

## Deployment plan

After rendered comparison and any visual fixes, review the complete diff and untracked files. Then stage only intended UI and documentation files, commit after final review, deploy to a preview environment, run the synthetic acceptance flow there, and request production approval. No push or deployment is part of this task.
