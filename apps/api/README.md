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
