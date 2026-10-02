# Codex Prompt 10 — Question Router

Read docs/AI_PIPELINE.md.

Implement natural-language question classification.

Initial domains:

- career
- business
- wealth
- marriage
- property
- education
- family
- general

Initial goals:

- current_status
- improvement
- timing
- change
- opportunity
- risk
- long_term_outlook

The router should produce structured JSON.

For MVP, make the classifier provider-independent.

Add tests for questions such as:

- When will my business improve?
- When will my financial situation improve?
- When can I buy a house?
- When will my career change?
- What are the important periods in the next five years?

Do not generate astrological predictions yet.
