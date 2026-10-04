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

### Task 17E Ask JyotAI response path

```text
POST /api/v1/analyze
  -> DeterministicAnalysisService
  -> EvidenceSelectionResult (exact domain)
  -> InterpretationEvidenceBuilder
  -> AnswerComposer
  -> validated `answers` API field
  -> existing Ask JyotAI result display
```

Only the composer’s narrow safe projection crosses the model boundary. Provider failures and
invalid provider responses fail closed; the current static governed coverage does not establish
timing.

### Governed dashboard insights API v1

`POST /api/v1/insights/dashboard` accepts explicit birth input and a timezone-aware as-of
instant. It constructs the application-owned fixed sequence of exact domains—Career, Wealth,
Education, Business, Children, Spirituality, Travel, and Friends—without invoking the
natural-language question router. It reuses `DeterministicAnalysisService`, the active production
release, the immutable `jyotish.d1.structural.rule1@v5` FactContract, `EvidenceSelector`,
`InterpretationEvidenceBuilder`, and the deterministic reviewed-wording composer. Its response
contains one ordered entry per domain, preserving separate MATCH, unmatched, and UNKNOWN counts;
UNKNOWN is never collapsed into FALSE. This additive retrieval path introduces no calculation,
rule, or astrology methodology.

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

The active governed release is `jyotish.production.cumulative@v10`: 22
explicitly admitted General, Career, Wealth, Education, Business, Children, Spirituality,
Travel / Foreign Residence, and Friends / Social Network rules. Its immutable FactContract remains
`jyotish.d1.structural.rule1@v5`; Spirituality / Dharma Pack v1 reuses only
facts already admitted by that contract. It has four D1/Rashi static contextual
rules (tenth lord in 4 or 10, tenth lord in 9, eleventh lord in 2 or 5, and
eleventh lord in 9 or 10), with no religious-identity, moral-ranking,
moksha/supernatural, timing, scoring, or prediction claim. Its shared-source
provenance has distinct cross-domain rule and interpretation identities under
exact-domain selection. Children Pack v1 retains its three D1/Rashi static
contextual rules (fifth lord in 11, eleventh lord in 2 or 5, and tenth lord in
5 or 11), with no fertility, child-count, gender, health,
loss, reproductive, or timing claims. Candidates 4 and 5 are HOLD and sensitive
reproductive/loss passages are excluded. Shared sources are allowed only with
distinct domain rule and interpretation identities; exact-domain selection
enforces their separation. Releases and their manifests remain immutable; no
rule discovery by glob is used.

Travel / Foreign Residence Pack v1 contributes exactly one D1/Rashi static
contextual rule: sixth-house lord in 2 or 10. It uses the existing v5 fact
vocabulary and introduces no calculation semantics. Candidates 2 and 3 are HOLD;
candidates 4 and 5 are REJECTED. It makes no immigration, visa, citizenship,
permanent-settlement, exact-destination, or timing prediction. Its rule and
reviewed interpretation identities are distinct from Business, and exact-domain
selection keeps Travel and Business evidence separate.

Friends / Social Network Pack v1 contributes exactly one D1/Rashi static contextual rule:
tenth lord in 9. It uses the existing v5 fact vocabulary and adds no calculation semantics.
It establishes no popularity, friend count, loyalty, betrayal, social-media influence,
professional networking, or timing. Its three avastha candidates are HOLD and the Mars
Sabha candidate is REJECTED. Source provenance is shared with Career and Spirituality only;
exact-domain selection separates the three distinct domain, rule, and interpretation identities.

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

## Post-Kundli dashboard web flow

The JyotishAI web client loads deterministic context, then makes exactly one independent dashboard
request using that birth input and as-of value. It renders Career, Wealth, Education, Business,
Children, Spirituality, Travel, and Friends in fixed order without frontend rule evaluation. MATCH
renders reviewed deterministic wording; no-match and UNKNOWN are separate non-negative states.
D1/D9/D10 remain factual views, as do Dasha and Transits. Ask JyotishAI continues to use the
separate `/api/v1/analyze` flow.

The frontend presentation layer uses CSS design tokens and local inline decorative components only;
it introduces no frontend astrology evaluation. Its profile header, Kundli workspace, factual
Cosmic Context, domain cards, and Ask panel are responsive and use native disclosure controls for
progressive evidence access.

### Governed detailed answer / justification v1

Ask builds an additive detailed response only after exact-domain selection and interpretation-evidence
admission. Its placement sentence is a deterministic rendering of the selected resolved D1
house-lord placement fact; it is not frontend inference or new doctrine. The reviewed statement is
copied unchanged, while source title/locator, D1/Rashi scope, and static/contextual posture are
renderer-safe provenance. Multiple matches stay ordered, separate evidence blocks. UNKNOWN is not
FALSE, no-match is a corpus limitation, and static evidence appends the established timing limitation
when timing is requested. Dashboard contracts continue to use concise `ComposedAnswer` wording.

### Optional Senior Astrologer Composer v1

Ask may append a validated `narrative` object to its deterministic detailed answer when
`LLM_ENABLED=true`. The narrative is never a source of astrology: deterministic calculation,
governed evaluation, exact-domain selection, detailed-answer construction, and all provenance remain
authoritative. The provider sees a closed packet only: question, domain, deterministic summary, safe
placement descriptions, reviewed statements, fixed limitations, timing status, and safe source display
metadata. It never sees birth data, chart objects, fact/rule IDs, hashes, registry content, unmatched
wording, or BPHS source text.

The provider must return a strict structured object. A post-generation validator fails closed for
unsupported doctrine or placements, timing language when timing is unavailable, remedies, certainty
or probability language, and off-domain claims. It derives sensitive-concept authorization exclusively
from the closed governed packet, never the user question. A concept supplied only in a deterministic
limitation is limitation-only: it may be restated as a limitation but cannot become a prediction.
Provider, schema, and validation failures retain the deterministic answer. Dashboard insights remain
deterministic. Static evidence has no timing authority.
