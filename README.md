# JyotishAI

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

Ask JyotishAI can use an OpenAI-compatible Senior Astrologer Composer only as a constrained
narrative layer when `LLM_ENABLED=true`. It receives a closed packet of the question, routed domain,
deterministic summary, safe placement descriptions, exact reviewed statements, fixed limitations,
timing status, and safe display provenance. It never receives birth data, charts, fact/rule IDs,
hashes, registry content, or BPHS text. The default `LLM_ENABLED=false` uses the fully functional
deterministic detailed answer and makes no external provider call or API-key request. Provider,
schema, or safety-validation failures return that same deterministic answer. When enabling live composition, set
`LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY`, and `LLM_TIMEOUT_SECONDS` for the
backend deployment. The provider returns structured narrative fields only; deterministic evidence,
limitations, timing, and methodology stay application-controlled. The validator rejects unsupported
doctrine, placements, timing, remedies, certainty language, and other unsafe claims.
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

`POST /api/v1/insights/dashboard` is the additive post-Kundli dashboard contract. It accepts
the same explicit birth input and timezone-aware as-of instant, then deliberately selects the
fixed Career, Wealth, Education, Business, Children, Spirituality, Travel, and Friends domains.
It does not route a user question. It reuses the active governed pipeline and returns each domain
in that stable order with matched reviewed wording where available, plus distinct unmatched and
UNKNOWN counts. Absence of a match is not a negative chart conclusion. The endpoint adds no
astrology doctrine and uses deterministic reviewed wording without requiring an LLM provider.

With `LLM_ENABLED=false`, governed answers use the deterministic reviewed-wording
fallback and never call a provider. The active governed release is
`jyotish.production.cumulative@v10` with 22 explicit rules: the historical
General rule, four Career rules, four Wealth rules, three Education Pack v1
rules, one Business Pack v1 rule, three Children / Progeny Pack v1 rules, and
four Spirituality / Dharma Pack v1 rules, one Travel / Foreign Residence Pack v1 rule, and
one Friends / Social Network Pack v1 rule.
Children Pack v1 admits only D1 fifth lord in 11, eleventh lord in 2 or 5, and
tenth lord in 5 or 11 as static, contextual natal evidence. It makes no
fertility, exact child-count, gender, health, loss, reproductive, or timing
claim; candidates 4 and 5 are HOLD, and sensitive reproductive/loss passages
are excluded. Shared BPHS passages retain distinct cross-domain rule and
interpretation identities under exact-domain selection. The immutable
FactContract remains `jyotish.d1.structural.rule1@v5`. Birth data stays in
browser memory only; the app adds no persistence, analytics, accounts, or
geocoding.

Spirituality / Dharma Pack v1 admits only D1 tenth lord in 4 or 10, tenth lord
in 9, eleventh lord in 2 or 5, and eleventh lord in 9 or 10 as static,
contextual natal evidence. Candidates 1, 6, 8, and 9 are HOLD; candidates 7
and 10 are REJECTED. It makes no religious-identity, moral-ranking,
moksha/supernatural, timing, or certainty claim. Shared BPHS provenance is
permitted only with distinct domain-specific rule and interpretation identities.

Travel / Foreign Residence Pack v1 admits exactly one D1/Rashi static contextual
rule: sixth-house lord in 2 or 10. It makes no immigration, visa, citizenship,
permanent-settlement, exact-destination, or timing prediction. Candidates 2 and
3 are HOLD; candidates 4 and 5 are REJECTED. The FactContract remains
`jyotish.d1.structural.rule1@v5`.

Friends / Social Network Pack v1 admits exactly one D1/Rashi static contextual rule:
tenth-house lord in 9. It makes no popularity, friend-count, betrayal, loyalty,
social-media influence, professional-networking, or timing prediction. Candidates 2, 3,
and 4 are HOLD; candidate 5 is REJECTED. Its source provenance is shared with Career and
Spirituality, but its rule, domain, and immutable interpretation identity are distinct and
exact-domain selection keeps them separate.

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

## Post-Kundli dashboard

After a birth profile is created, JyotishAI shows the profile summary, factual D1/D9/D10, current
Vimshottari Dasha boundaries, factual transits, governed insights, and Ask JyotishAI. The browser
calls `POST /api/v1/insights/dashboard` once with the same birth input and as-of instant and never
evaluates rules. Its fixed domains are Career, Wealth, Education, Business, Children, Spirituality,
Travel, and Friends. MATCH shows reviewed wording; no-match and UNKNOWN are distinct,
non-negative states. LLM remains optional and disabled by default. Visible branding is JyotishAI;
internal repository, package, API, environment, and deployment identifiers remain unchanged.

## Deterministic detailed Ask answers

Ask JyotishAI adds an Ask-only detailed-answer projection from the already selected governed
evidence. It provides a neutral direct summary, deterministic D1 house-lord placement explanation,
the immutable reviewed statement, domain framing, concise domain limitations, and safe BPHS source
metadata. Multiple matches remain separately identifiable and are never combined into a stronger
claim. No-match and UNKNOWN remain distinct; static natal evidence never establishes timing. The
dashboard continues to use concise reviewed wording, and `LLM_ENABLED=false` remains the default.
