# Codex Prompt 14 — Public API

Implement versioned FastAPI endpoints:

POST `/v1/charts`
GET `/v1/charts/{chart_id}`
POST `/v1/questions`
GET `/v1/questions/{question_id}`

For now, use a simple persistence implementation if PostgreSQL is not ready.

Requirements:

- validation
- structured errors
- request IDs
- no secrets in logs
- API tests

Do not implement authentication yet.
