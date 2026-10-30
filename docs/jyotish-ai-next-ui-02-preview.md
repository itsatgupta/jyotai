# JYOTISH-AI-NEXT-UI-02 design preview

The design preview is a separate Vite page at `/preview.html`. It does not load the current app entry point or call the API. The build includes both `index.html` and `preview.html` so the integrated dashboard can be compared with the approved design.

## Open on a Mac

From `apps/web`, run:

```sh
npm run dev -- --host 127.0.0.1 --port 4173
```

Open <http://127.0.0.1:4173/preview.html> in Chrome or Safari. If port 4173 is occupied, use the URL Vite prints with `/preview.html` appended.

Review at viewport widths **1440, 768, and 390 px** in both themes. In Chrome, open DevTools with `⌘⌥I`, then toggle device emulation with `⌘⇧M` and enter each width. Check the hero, profile strip, Kundli, planet cards, Dasha layout, and consultation panel. Select a planet card to highlight its house; clear the selection. Open the example evidence disclosure and try a suggested consultation question. The button only stages text and creates no answer. Inspect keyboard focus and reduced motion using the browser's accessibility and rendering tools.

The zodiac wheel is original decorative SVG artwork. The D1 panel follows the existing fixed North Indian house geometry. Its signs and planetary placements are synthetic layout examples. The MD and AD lists show only example names and order, without proportional duration, progress, dates, or an active-period claim. The consultation panel has a static answer-format specimen with facts, interpretation boundaries, limits, and expandable example evidence. It does not connect to an evidence package or AI. Actual chart data, Dasha calculations, and interpretations remain in the current application.

The main dashboard integration is documented in [jyotish-ai-next-ui-03-integration.md](jyotish-ai-next-ui-03-integration.md). City autocomplete remains a separate unresolved issue.
