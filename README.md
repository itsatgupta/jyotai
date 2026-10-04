# JyotAI

## Goal

Build an AI astrology application where a user enters birth details once and can ask natural-language questions such as:

- When will my career improve?
- When will my business grow?
- When will my financial situation improve?
- When can I buy a house?
- What are the important periods over the next five years?

The system must use deterministic astrology calculations first and an AI model second.

## Local development

The current implementation includes a FastAPI backend in `apps/api` and a React/Vite browser
vertical slice in `apps/web`.

```bash
cd apps/api
uv sync --extra dev
uv run pytest
uv run uvicorn astrologer.main:app --reload
```

In a separate terminal, run the browser app:

```bash
cd apps/web
npm install
npm run dev
```

Vite proxies `/api` to `http://localhost:8000` locally. A deployed browser app uses the
build-time `VITE_API_BASE_URL` environment variable. Configure the backend's
`CORS_ALLOWED_ORIGINS` as a JSON array of exact frontend origins for cross-origin deployment;
do not use a wildcard origin.

Ask JyotAI uses an OpenAI-compatible model endpoint only as a constrained language layer when
`LLM_ENABLED=true`. The default `LLM_ENABLED=false` uses deterministic reviewed governed wording
and makes no external provider call or API-key request. When enabling live composition, set
`LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY`, and `LLM_TIMEOUT_SECONDS` for the
backend deployment. Provider failures fail closed; the API never returns unvalidated model prose.
The current governed corpus is intentionally limited, and static natal evidence does not establish
timing.

Copy `.env.example` to `.env` only for local configuration. Never commit the
resulting `.env` file or credentials.

## Architecture

```text
User
  |
  v
Next.js Web App
  |
  v
FastAPI
  |
  +--> Question Router
  |
  +--> Astrology Engine
  |       +--> Ephemeris
  |       +--> Houses
  |       +--> Nakshatra
  |       +--> Vargas
  |
  +--> Timing Engine
  |       +--> Vimshottari Dasha
  |       +--> Transits
  |
  +--> Rules Engine
  |
  +--> Evidence Builder
  |
  +--> AI Gateway
  |
  v
Structured Answer
```

## Important

Do NOT ask an LLM to calculate planetary positions, houses, dashas, or transits.

Those calculations must be deterministic.

The LLM interprets a verified evidence package.

## Initial methodology

- Vedic/Jyotish
- Sidereal zodiac
- Lahiri ayanamsa
- Vimshottari Dasha
- Configurable house system

These settings must be configurable and versioned.

## Initial stack

- Python 3.12+
- FastAPI
- Pydantic
- PostgreSQL
- Next.js
- TypeScript
- Docker
- pytest
- Ruff
- model-independent AI gateway

## Task 14 vertical slice

The browser app accepts explicit birth coordinates, IANA timezone, and an explicit
timezone-aware as-of instant. It displays deterministic D1/D9/D10, active Dasha, and
transit-v1 facts. It can also call `POST /api/v1/analyze`, which statelessly composes the
approved deterministic context, question router, governed production evaluation, evidence
package, and exact-domain evidence selection.

With `LLM_ENABLED=false`, governed answers use the deterministic reviewed-wording
fallback and never call a provider. The active governed release is
`jyotish.production.cumulative@v5` with 12 explicit rules: the historical
General rule, four Career rules, four Wealth rules, and three Education Pack v1
rules. Education is D1/Rashi static contextual evidence only: no timing,
health, scoring, or prediction. Education candidates 4 and 6 are HOLD and 5, 7,
and 8 are REJECTED. Its fifth-lord-in-eleventh rule shares source provenance
with Wealth while retaining separate Education rule and interpretation
identities. Birth data stays in browser memory only; the app adds no
persistence, analytics, accounts, or geocoding.

## Development rule

Do not build everything in one step.

Use the numbered prompts in:

`codex-prompts/`

Complete each prompt, run tests, review the result, then continue.

## User role

The product owner does not need to be an astrologer.

The user provides:

- desired product behavior
- questions the product should answer
- feedback on whether answers are useful

The engineering agent builds the software.

The astrology methodology and rules should be sourced, documented, versioned, and independently testable.
