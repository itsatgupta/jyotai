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
