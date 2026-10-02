# AI Astrologer API

Backend foundation for the AI Astrologer application.

## Local development

From this directory:

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run mypy src
uv run uvicorn astrologer.main:app --reload
```

The service exposes `GET /health` for a lightweight availability check.
