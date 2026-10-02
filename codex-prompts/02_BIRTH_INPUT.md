# Codex Prompt 02 — Birth Input Model

Read AGENTS.md and docs/ASTROLOGY_METHOD.md.

Implement validated birth input models.

Requirements:

- date
- time
- timezone
- latitude
- longitude
- optional place name
- optional display name

Create:

- Pydantic models
- normalization service
- validation errors
- unit tests

Important:
Do not calculate planetary positions yet.

The output should be a canonical `BirthInput` object suitable for the astrology engine.

Run tests.
