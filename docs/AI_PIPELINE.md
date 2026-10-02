# AI Pipeline

## Principle

The AI interprets evidence. It does not calculate the horoscope.

## Flow

```text
Question
  |
  v
Intent Classification
  |
  v
Required Factors
  |
  v
Chart + Dasha + Transit
  |
  v
Rules
  |
  v
Evidence Package
  |
  v
LLM
  |
  v
Schema Validation
  |
  v
Answer
```

## Evidence package

```json
{
  "question": "...",
  "methodology": {},
  "chart_facts": [],
  "dasha_periods": [],
  "transits": [],
  "rules": [],
  "timing_windows": []
}
```

## Answer

```json
{
  "summary": "...",
  "timelines": [],
  "reasoning": [],
  "supporting_factors": [],
  "contradicting_factors": [],
  "uncertainty": "...",
  "practical_notes": []
}
```

## AI behavior

Prefer:

> "The astrological indicators are more supportive of..."

Avoid:

> "This will definitely happen."

Never invent dates or chart facts.
