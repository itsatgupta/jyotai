# Project Structure

```text
ai-astrologer/
|
├── AGENTS.md
├── README.md
├── .gitignore
├── .env.example
├── docker-compose.yml
|
├── apps/
│   ├── api/
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── astrologer/
│   │   │       ├── api/
│   │   │       ├── astrology/
│   │   │       ├── timing/
│   │   │       ├── rules/
│   │   │       ├── questions/
│   │   │       ├── evidence/
│   │   │       ├── ai/
│   │   │       └── common/
│   │   └── tests/
│   │
│   └── web/
│       ├── app/
│       ├── components/
│       ├── lib/
│       └── package.json
|
├── packages/
│   ├── schemas/
│   └── prompts/
|
├── knowledge/
│   ├── rules/
│   │   ├── career/
│   │   ├── business/
│   │   ├── wealth/
│   │   ├── marriage/
│   │   └── property/
│   └── sources/
|
├── fixtures/
│   └── charts/
|
├── scripts/
|
├── docs/
|
└── codex-prompts/
```
