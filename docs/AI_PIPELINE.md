# AI Pipeline

## Principle

Any future AI interpretation layer must consume evidence; it must not calculate
the horoscope. No AI interpretation layer is implemented by Task 11.

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
recognizes only the governed vocabulary `general`, `career`, `wealth`,
`marriage`, `health`, and `property`. User-language references to business are
an alias for `career`, not a new Jyotish domain or doctrine.

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
