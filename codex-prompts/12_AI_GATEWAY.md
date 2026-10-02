# Codex Prompt 12 — AI Gateway

Read AGENTS.md and docs/AI_PIPELINE.md.

Implement a provider-independent AI gateway.

Create an interface similar to:

```python
class LLMProvider(Protocol):
    async def generate(...): ...
```

Add:

- structured output support
- timeout handling
- retries where appropriate
- provider configuration
- logging without sensitive data
- schema validation

Do NOT hard-code JEV.

Do NOT implement astrology calculations in the model.

For local development, support an OpenAI-compatible local endpoint if practical.

The AI receives only the evidence package and user question.
