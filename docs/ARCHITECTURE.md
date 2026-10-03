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
Interpretation Evidence Contract
     |
     v
Future renderer / AI Gateway
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

Builds the complete evidence package and, in Task 13, performs pure,
exact-domain selection for one atomic question intent. Selection preserves
TRUE/FALSE/UNKNOWN and direction labels without scoring or interpretation.
Static and timing-required rule posture do not establish timing answerability;
timing/corroboration requirements remain explicitly unmet until a future,
separate governed capability exists.

Task 17C adds an internal `InterpretationEvidence` contract after exact-domain
selection. It is a hashable, status-preserving projection of only selected,
manifest-admitted items and their compact rule/source/fact provenance. It is
not a user answer: it creates no astrology calculations or doctrine, contains
no source prose, and establishes no timing. Future LLM work must consume this
governed contract rather than raw chart data for doctrinal inference.

### ai/

LLM provider abstraction and interpretation.

### api/

FastAPI endpoints.

### web/

Task 14 adds a React + Vite + TypeScript browser UI. It renders only backend-returned
deterministic facts, routing states, and governed evidence. It keeps audit/provenance details
behind progressive disclosure and contains no frontend astrology calculations or interpretation.

### Task 14 stateless analysis orchestration

`POST /api/v1/analyze` receives explicit `BirthInput`, explicit timezone-aware `as_of`, and a
question. It composes one Task 10 context, passes that same explicit instant to Task 12 as the
router reference instant, evaluates the fixed admitted corpus, builds Task 11 evidence, and
selects Task 13 evidence per routable atomic intent. It adds no new calculation, doctrine,
scoring, timing capability, or LLM behavior.

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
