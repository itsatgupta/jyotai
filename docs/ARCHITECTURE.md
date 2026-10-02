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
Question Intent
     |
     v
Deterministic Context + Governed Evaluations
     |
     v
Evidence Package
     |
     v
Evidence Selector
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

Task 09B-v1 supplies a separate reviewed-knowledge governance layer around the
generic rule framework: source registry -> reviewed interpretation -> production
rule envelope -> admission validator -> versioned corpus manifest. The
historical initial production corpus remains deliberately empty; Task 09C2 adds
one separate reviewed D1 rule release. The layer does not interpret charts,
derive facts, aggregate evidence, call an LLM, or provide runtime rule
authoring.

Task 09C1 adds an immutable governed-evaluation adapter in `knowledge/`. It
keeps the production loader as the admission boundary and Task 08 as the generic
fact evaluator, while joining admitted envelope, manifest, registry, and Task
09A fact provenance to the resulting evaluation trace. It adds no rule corpus.

### application/

Task 10 adds a stateless deterministic context-composition service. It uses one
shared D1 chart to compose D9/D10, active Vimshottari, a point-in-time transit
snapshot, and Task 09A D1 structural facts for an explicit as-of instant. It
does not load rules, build evidence, interpret any output, or call an LLM.
The API route depends on this service rather than duplicating engine calls.

### questions/

Task 12 supplies immutable, deterministic language-only intent detection and
domain routing. It has no astrology, evidence, corpus, or LLM dependencies.
It returns one ordered atomic intent per explicitly requested supported domain;
future evidence selection is a separate boundary.

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
