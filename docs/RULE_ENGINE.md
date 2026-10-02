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
