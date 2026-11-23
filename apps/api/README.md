# AI Astrologer API

Backend foundation for the AI Astrologer application.

## Local development

From this directory:

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run mypy src
uv run uvicorn astrologer.main:app --reload
```

The service exposes `GET /health` for a lightweight availability check.

## Internal D9/D10 structural facts

`VargaStructuralFactsEngine` in `astrologer.astrology.varga_derived_facts` projects
completed deterministic D9 or D10 charts into scope-specific house signs, planet
signs, planet placement houses, and same-sign equality facts. Call `calculate(chart,
ChartScope.D9_NAVAMSA)` or `calculate(chart, ChartScope.D10_DASAMSA)` with the matching
Varga chart. Each scope has its own `jyotish-d9-derived-facts-v1` or
`jyotish-d10-derived-facts-v1` methodology and exact `jyotish.d9.structural@v1` or
`jyotish.d10.structural@v1` fact contract. The ordered bundle records the input Varga
methodology, D1 source methodology, inherited ephemeris provenance, and fact count.
Varga longitudes are divisional coordinates, not new astronomical positions. These
facts are internal only; no active release, evidence path, or answer path consumes them.

The application configures the `astrologer` logger at `INFO`. Its diagnostics are
written to stderr when Uvicorn's default logging configuration leaves the root
logger without a handler. Diagnostics deliberately exclude birth data, question
text, chart data, and credentials.

It also exposes stateless deterministic calculation routes:

- `POST /api/v1/charts/calculate` for D1/D2/D9/D10.
- `POST /api/v1/context/snapshot` with `{ "birth_input": {...}, "as_of":
  "<timezone-aware datetime>" }` for D1, D9, D10, active Dasha, a transit
  snapshot, and D1 derived facts. It performs no interpretation or rule
  evaluation.

- `POST /api/v1/analyze` with `{ "birth_input": {...}, "as_of":
  "<timezone-aware datetime>", "question": "..." }` returns the deterministic context,
  language-only routing result, complete governed evidence package, and separate exact-domain
  selection results for routable atomic intents, plus a deterministic detailed answer.

- `POST /api/v1/consultation` also returns short-lived, profile-bound conversation state.
  A Career calendar-year answer carries `career_answer_plan` with selected fact and claim IDs,
  reviewed source locators, timing references, calculated Mahadasha/Antardasha intersections,
  limitations, and answerability. `consultation_sections` are deterministic prose generated
  from that plan. The main Dasha chronology uses local calendar dates; the plan retains exact
  UTC half-open source and overlap intervals. Calculated periods do not imply Career events.
  Follow-up references remain bound to the original turn and approved claims.
- Each planned Dasha segment also carries `dasha_linkages` (`jyotish.dasha_linkage.v1`):
  deterministic facts for the Mahadasha and Antardasha lords — ruled houses, placement house
  and sign, own/exaltation sign (seven classical planets only), 10th-lord and 10th-house
  relationships, same sign as the 10th lord, and `ad_house_from_md`. Every house is counted
  from the D1 Lagna (Whole Sign) only; `ad_house_from_md` is a plain inclusive sign count from
  the MD lord's sign, with no relationship label. Rahu/Ketu rule no sign under the classical
  seven-planet lordship convention (empty tuple plus a convention note), and their aspect facts
  are `UNKNOWN` because the seven-planet aspect convention does not model them — never "no
  aspect". A `dasha_context` consultation section (also returned by the "Which Dasha
  applies?" follow-up) renders only fact-ID-backed sentences plus one fixed framing line.
  `dasha_interpretation` is a review-gated slot filled only by rules admitted through
  `admit_dasha_interpretation_corpus` (the shared production admission path); the production
  corpus `jyotish.dasha_interpretation.career@v1` is empty.

The frozen 34-journey consultation fixture is `tests/fixtures/consultation_quality_v1.json`.
Results v1 through v4 remain historical baselines; `consultation_quality_v5_results.json`
captures the descriptive consultation comparison (v5 adds the calculated Dasha context
section; it is descriptive coverage, not new astrological coverage). Reproduce it with
`uv run python tests/consultation_quality_benchmark.py --output /private/tmp/new-results.json`
from `apps/api`, then compare the generated result with the versioned fixture. The editorial
substantive classification is unchanged; a clearer presentation is not counted as new
astrological coverage.

The optional senior narrative receives only governed display evidence, source metadata, domain
framing, deterministic limitations, and a closed phrase catalog. It does not receive the birth
input, original question, raw chart, or timing windows. Each accepted section must use an exact
approved phrase and reference the required selected evidence IDs. Invalid or unavailable provider
output is discarded as a whole; the deterministic detailed answer remains the fallback.

`CORS_ALLOWED_ORIGINS` is an optional JSON array of exact frontend origins. Leave it empty for
local Vite proxy development; do not configure wildcard production origins.

## Birthplace autocomplete

Set `GEOAPIFY_API_KEY` only in the FastAPI/Render environment to enable
`GET /api/v1/locations/search?q=Gurgaon`. The browser never receives this key; the endpoint
returns only a display label, coordinates, IANA timezone, and provider ID. Geoapify receives
the typed place query only, not the complete birth profile. Do not log location request bodies.
