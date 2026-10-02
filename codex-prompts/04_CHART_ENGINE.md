# Codex Prompt 04 — Deterministic Chart Engine

Read AGENTS.md, docs/ASTROLOGY_METHOD.md and docs/ARCHITECTURE.md.

Build the deterministic chart engine on top of the ephemeris adapter.

Implement:

- ascendant
- planetary positions
- signs
- degrees
- houses
- nakshatra
- pada
- retrograde where supported
- methodology metadata

Create a canonical `Chart` Pydantic model.

Example high-level output:

```json
{
  "methodology": {},
  "birth_input": {},
  "ascendant": {},
  "planets": [],
  "houses": [],
  "nakshatras": []
}
```

Do not implement AI.

Add regression tests.

Do not silently choose different astrology settings from docs.
