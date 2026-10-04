# AI Pipeline

## Principle

Any future AI interpretation layer must consume evidence; it must not calculate
the horoscope. No AI interpretation layer is implemented by Task 11.

## Constrained answer composition

Task 17D adds an internal-only, provider-neutral `AnswerComposer`. It accepts
only the original user question, a validated `InterpretationEvidence` contract,
and the fixed versioned composition policy. Its transport receives a smaller
allowlisted projection: question intent, timing flag, manifest identifiers,
status-preserving selected evidence, and the reviewed interpretation statement
and scope notes attached to that evidence. It never receives birth data, raw
charts, resolved fact values, source text, excluded items, or held candidates.

The policy requires JSON output with evidence-item references. The composer
rejects unknown references, malformed output, timing flags, and some obvious
timing language as defense in depth; that lexical check is not the timing
guarantee. For a timing request without timing answerability, the provider gets
only a static-context task and its generated prose is never returned. The
application deterministically returns reviewed static wording plus the explicit
limitation that timing is not established by the current governed evidence. A
`FALSE` item remains an unmatched rule rather than opposite evidence; `UNKNOWN`
remains unresolved. If there is no matched governed evidence, the composer does
not call a provider: it returns a deterministic statement that the current
governed corpus does not establish the requested interpretation. This layer is
not wired to a router or public API in Task 17D.

Task 14 exposes a stateless browser-facing orchestration endpoint, `POST /api/v1/analyze`. It
returns deterministic context, routing, evidence package, and per-intent selections only. The
explicit request `as_of` is also the router's explicit reference instant. No interpretation,
source prose duplication, or LLM call is added.

## Flow

```text
User language
  |
  v
QuestionIntent
  |
  v
QuestionIntent + EvidencePackage
  |
  v
Future EvidenceSelectionResult
  |
  v
Future constrained interpretation layer
```

## Question intent

Task 12 adds a separate, immutable language-routing contract. It accepts an
original user question and optional caller-supplied timezone-aware reference
instant, and returns ordered atomic intents plus explicit routing issues. It
recognizes only the governed vocabulary `general`, `career`, `business`,
`wealth`, `education`, `marriage`, `health`, and `property`. Business is an
independent governed domain with exactly one Business Pack v1 rule, rather than
an alias for career.

The router has no implicit clock: unresolved relative periods remain structured
relative expressions until a caller supplies a reference instant. It does not
inspect evidence, select rules, calculate astrology, or call an LLM. A future
EvidenceSelector, rather than the router, will combine `QuestionIntent` with an
`EvidencePackage`.

## Evidence selection

Task 13 selects existing package items for one atomic `QuestionIntent`; it does
not calculate, evaluate rules, load a corpus, inspect sources, or interpret
astrology. Its v1 policy is explicit and exact-domain only: an item is eligible
only when its governed domain equals the intent domain. `general` is not a
wildcard and general contextual evidence is not exposed to another domain.

Eligible `TRUE`, `FALSE`, and `UNKNOWN` items remain separate as selected
matched, relevant unmatched, and relevant unknown collections. FALSE is not
opposite evidence and UNKNOWN is not repaired. Directions remain governed,
unscored labels; the selector neither ranks nor reconciles them.

Static items can remain relevant background evidence for a timing request, but
they do not make timing answerable. A `timing_required` match states that timing
corroboration is required, not supplied. Likewise, a `corroboration_required`
match is retained with corroboration handling explicitly deferred. There is no
Task 13 timing-evidence capability, timing calculation, corroboration engine,
or interpretation.

Education Pack v1 is static contextual evidence only. For an Education timing
request, a matched Education statement may be returned, but the application
appends exactly: “Timing is not established by the current governed evidence.”
It supplies no dates, exam or score prediction, academic-result timing, Dasha,
or transit interpretation. The fifth-lord-in-eleventh Education and Wealth
rules share provenance only; exact-domain selection excludes the other rule.

Business Pack v1 is also D1/Rashi static contextual evidence only. Its sole
approved rule is sixth-house lord in ninth; candidate 2 is HOLD and candidates
3, 4, and 5 are REJECTED. A matched Business timing request may show the static
reviewed statement, followed exactly by: “Timing is not established by the
current governed evidence.” It establishes neither success, profit, revenue,
nor timing. Exact-domain selection excludes General, Career, Wealth, and
Education items from a Business intent, and excludes the Business item from
those intents.

## Evidence package

Task 11 supersedes the prior question-oriented evidence-schema draft. Its
immutable, hashable `EvidencePackage` contains the compact deterministic
context identity/provenance, the complete approved corpus manifest and hash,
and three disjoint, rule-ID/version-ordered collections:

- `matched_evidence`: only `TRUE` evaluations;
- `unmatched_evaluations`: only `FALSE` evaluations, never opposite evidence;
- `unknown_evaluations`: only `UNKNOWN` evaluations, never silently repaired.

Each evidence item keeps its condition trace, only facts actually resolved by
the evaluator, and compact governance/fact provenance identifiers. Source
passage, translation, and reviewed-interpretation text are deliberately not
duplicated into the package.

`supporting`, `challenging`, and `contextual` are qualitative governed
directions for matched evidence only. They are not weights, scores,
probabilities, confidence values, or conflict-resolution instructions. The
package preserves simultaneous conflicting matched items unchanged.

EvidenceBuilder is stateless and does not calculate astrology, evaluate rules,
interpret Dasha/transits/Vargas, infer outcomes, or access an LLM. Its package
hash uses canonical JSON over all package content except the self-referential
hash field. An empty approved manifest produces a valid, hashable package with
zero items.

## Public Ask JyotAI wiring (Task 17E)

`POST /api/v1/analyze` preserves its deterministic response fields and adds an ordered `answers`
array. Its runtime path is request -> deterministic analysis -> exact-domain selection ->
`InterpretationEvidenceBuilder` -> `AnswerComposer` -> validated response -> web result display.
The route does not evaluate rules or rebuild evidence itself.

The OpenAI-compatible HTTP adapter remains behind `LanguageModelTransport`; it receives only the
fixed system policy and the composer’s safe projection. It never receives birth input, raw chart
data, fact values, source PDF text, excluded evidence, or held candidates. `LLM_PROVIDER`,
`LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY`, and `LLM_TIMEOUT_SECONDS` configure it. Provider
transport failures, malformed JSON, unsupported evidence references, and composition validation
failures fail closed with a controlled API error; unvalidated prose is never returned.

The reviewed corpus remains intentionally limited. No matched rule returns a deterministic
corpus-limit answer without a provider call. Static evidence never establishes timing: for “When
will my career improve?” the answer can contain reviewed static career context but says timing is
not established by the current governed evidence.
