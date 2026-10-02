# Rule Engine

The rule engine translates calculated chart facts into explicit evidence.

It must not perform astronomical calculations.

## Rule object

Example:

```yaml
rule_id: CAREER_001
domain: career
title: Career and gains connection
priority: medium

conditions:
  all:
    - fact: tenth_lord_connected_to_eleventh
      value: true

interpretation:
  positive: >
    Indicates a relationship between professional activity and gains.

timing:
  requires:
    - dasha_activation
    - supportive_transit

source:
  type: documented_methodology
  reference: career_rules
```

## Rule result

```json
{
  "rule_id": "CAREER_001",
  "active": true,
  "strength": "moderate",
  "evidence": [
    "..."
  ]
}
```

## Initial domains

- career
- business
- wealth
- marriage
- property
- education
- family
- general

## Rule quality

Every production rule should eventually have:

- rule ID
- domain
- condition
- interpretation
- modifiers
- timing requirements
- source/reference
- tests
- version

Do not invent unsupported rules merely to make an answer positive.

## Task 08 framework boundary

Task 08 implements only a provider-independent, declarative framework. It
evaluates precomputed structured facts; it performs no astrology or astronomical
calculation. In particular, it does not derive longitudes, signs, houses,
lordships, aspects, conjunctions, dignity, yogas, Dasha, transit facts, timing,
or outcomes. Derived Jyotish facts and reviewed knowledge rules are deferred to
Task 09 / Task 09A. There is no production Jyotish rule corpus, prediction
logic, evidence aggregation, or LLM integration in this task.

The intended future chain is:

```text
deterministic calculation -> derived fact -> condition -> rule -> evidence -> LLM statement
```

Task 09A now supplies a D1-only, ordered structural `FactSet` through a
one-way adapter. The evaluator remains Jyotish-agnostic: it does not import the
derived-facts or chart modules. Task 09A facts have the `jyotish.d1.` namespace
and retain their methodology/source-register and chart provenance in the
upstream bundle; Task 08 continues to receive only immutable scalar facts.
Rahu/Ketu-derived aspect, ownership, and dignity families are deliberately
absent, allowing unavailable future conditions to evaluate as `UNKNOWN`.

Only the condition-to-rule segment exists here. A `Fact` is immutable
JSON-compatible input with a unique stable `fact_id` and value. Conditions use
the ID, enabling results to report both referenced and resolved facts. The
framework deliberately does not define the final Jyotish fact vocabulary.
Uncontrolled semantic flags such as `career_good` are not a framework concept.

Rules are validated data, never executable code. The framework uses no Python
`eval`/`exec`, embedded scripts, dynamic imports, executable YAML, or runtime
functions supplied by rule definitions. The loader accepts already-parsed,
JSON-compatible mappings or Pydantic models and deliberately adds no YAML
dependency. V1 supports only `EQUALS`, `NOT_EQUALS`, `IN`, `NOT_IN`, and
`EXISTS` leaves plus `ALL`, `ANY`, and `NOT` compound nodes.

### Three-state semantics

Every condition evaluates to `TRUE`, `FALSE`, or `UNKNOWN`:

- `TRUE`: a supplied fact establishes the condition.
- `FALSE`: the required fact exists and establishes that the condition does not
  hold. For `EXISTS`, an absent fact is definitively `FALSE`.
- `UNKNOWN`: a comparison requires a fact that was not supplied.

`UNKNOWN` is never silently converted to `FALSE`. The framework uses Kleene
three-valued logic: `ALL` is false if any child is false, otherwise unknown if
any child is unknown, otherwise true. `ANY` is true if any child is true,
otherwise unknown if any child is unknown, otherwise false. `NOT` inverts true
and false and preserves unknown.

Rules carry an ID, rule version, ruleset version, name, domain, optional source
placeholder, condition, and effect metadata. Results retain rule/ruleset/
framework versions, a nested condition trace, and stable referenced/resolved
fact IDs. `strength_label`, if later supplied by a rule, is declarative internal
metadata only—not empirical probability, scientific confidence, or an
evaluator-derived astrology score. Task 08 has no cross-rule aggregation.

`RuleLoader` validates parsed definitions, rejects malformed trees and
unsupported operations, enforces a shared ruleset version, rejects duplicate
`(rule_id, rule_version)` pairs, and sorts rules deterministically. The only
included rules are synthetic demonstrations: `TEST_RULE_ALL_TRUE`,
`TEST_RULE_ANY_TRUE`, and `TEST_RULE_UNKNOWN`. They make no Jyotish claim and
are not source-validated.

Task 08 does not duplicate upstream chart, Dasha, or transit provenance. Future
fact/evidence layers must retain their methodology and provider provenance,
including the current Moshier/internal-ephemeris limitation and outstanding
external Swiss Ephemeris data-file validation. This framework does not alter or
obscure those limitations.

## Task 09B-v1 knowledge governance boundary

Task 09B-v1 adds a separate `astrologer.knowledge` governance package. It does
not change Task 08's generic `RuleDefinition`, evaluator, or loader. A future
production rule is an immutable governance envelope containing a Task 08 rule,
linked to a source passage, optional reviewed translation, and a separately
reviewed interpretation statement.

The lifecycle is `draft`, `source_identified`, `source_verified`,
`interpretation_reviewed`, `formalized`, `tested`, `approved`, then
`production_active`, with explicit rejected/on-hold/disputed/deprecated/
superseded states. `approved` does not make a rule runtime-active. Production
loading requires a `production_active`, non-demo rule in an approved,
versioned, hashable corpus manifest and validates its fact contract, source
registry, translation/review state, and manifest membership.

Evidence direction is exactly `supporting`, `challenging`, or `contextual`.
Those are qualitative source-reviewed semantics, not scores, probabilities,
scientific confidence, or weights. Rules remain independent; Task 09B performs
no conflict aggregation.

The initial source registry and approved production manifest are valid but
empty. No interpretive Jyotish rule has been admitted. Runtime production
loading accepts data only and rejects synthetic demonstrations, inactive or
unadmitted rules, callable/script/import-like content, malformed definitions,
and incompatible rule/framework/fact-contract versions. It provides no runtime
rule-authoring facility.

## Task 09C1 governed evaluation bridge

Task 09C1 adds a knowledge-layer bridge around, not inside, Task 08. It accepts
an approved manifest, candidate production envelopes, source registry, fact
contract, supplied `FactSet`, and explicit Task 09A fact provenance. It first
uses `ProductionCorpusLoader` unchanged as the admission boundary, then passes
only its admitted `RuleDefinition` objects to the unchanged generic Task 08
evaluator.

Each immutable governed result contains the unmodified Task 08 result and its
condition/fact trace, qualitative envelope evidence direction, compact source
and release identifiers, and canonical SHA-256 hashes for the envelope,
manifest, supplied facts, and Task 09A derived-fact provenance. Source passage,
translation, and interpretation text is not copied into every result.

Governance reviews are categorized as source verification, translation
verification, interpretation review, or formalization review. A
production-active rule requires reviewed records in the matching category for
the source passage, interpretation, and formalization. It also requires a
reviewed translation when its interpretation marks translation as `required`.
When a verified source is already in the accepted working language,
`not_applicable` explicitly records that no translation is used; it cannot be a
silent omission of a required translation.

The historical empty manifest remains unchanged and evaluates to zero governed
results. The production Jyotish corpus remains empty; Task 09C1 introduces no
source material, doctrine, prediction, aggregation, or LLM behavior.
