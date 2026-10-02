# Codex Prompt 13 — AI Interpreter

Implement the first interpretation pipeline.

Input:

- user question
- evidence package

Output:

- summary
- timelines
- reasoning
- supporting factors
- contradicting factors
- uncertainty
- practical notes

Use the prompt files under `packages/prompts`.

Validate model output against JSON schema.

Add tests that verify the model cannot introduce unsupported dates or chart facts.

If a live model is unavailable, implement a mock provider for tests.
