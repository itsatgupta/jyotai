# AI Pipeline

## Principle

Any future AI interpretation layer must consume evidence; it must not calculate
the horoscope. No AI interpretation layer is implemented by Task 11.

## Flow

```text
Deterministic context + admitted governed rule evaluations
  |
  v
Evidence Package
  |
  v
Future constrained interpretation layer
```

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
