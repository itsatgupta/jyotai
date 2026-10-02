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

The current implementation is the FastAPI backend in `apps/api`.

```bash
cd apps/api
uv sync --extra dev
uv run pytest
uv run uvicorn astrologer.main:app --reload
```

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
