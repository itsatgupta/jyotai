# Architecture

## Request lifecycle

```text
Birth Details
     |
     v
Normalized Birth Input
     |
     v
Deterministic Chart Engine
     |
     +--> D1
     +--> Nakshatra
     +--> D9/D10/D2 as required
     |
     v
Timing Engine
     |
     +--> Vimshottari Dasha
     +--> Transits
     |
     v
Natural Language Question
     |
     v
Question Router
     |
     v
Relevant Astrology Factors
     |
     v
Rules Engine
     |
     v
Evidence Package
     |
     v
AI Gateway
     |
     v
Structured Answer
```

## Core separation

### astrology/

Only calculations.

Task 09A additionally contains D1-only deterministic structural derivation.
It consumes a canonical chart and may adapt its scalar output to `rules.FactSet`;
it does not calculate ephemerides, interpret a chart, or import the evaluator.

### timing/

Dasha and transit calculations.

### rules/

Declarative deterministic rule evaluation over precomputed facts. Task 08
implements this package only; it does not calculate astrology, provide a
production Jyotish corpus, aggregate evidence, or call an LLM.

Task 09B, the reviewed knowledge and production-rule corpus, remains separate
and unstarted.

### questions/

Natural-language intent detection and domain selection.

### evidence/

Builds the complete evidence package supplied to the LLM.

### ai/

LLM provider abstraction and interpretation.

### api/

FastAPI endpoints.

### web/

Next.js UI.

## Model independence

The AI gateway must allow different models later.

Example:

```text
AI Gateway
  |
  +-- Local Qwen
  +-- JEV
  +-- OpenAI-compatible provider
  +-- Other provider
```

Do not implement JEV yet. The interface should simply make future providers possible.
