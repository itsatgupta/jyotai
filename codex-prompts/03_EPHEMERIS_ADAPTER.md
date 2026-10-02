# Codex Prompt 03 — Ephemeris Adapter

Read AGENTS.md and docs/ASTROLOGY_METHOD.md.

Implement an abstraction for astronomical calculations.

Requirements:

1. Define an `EphemerisProvider` interface/protocol.
2. Add a concrete provider using a properly licensed/appropriate ephemeris library.
3. Keep the provider behind the interface.
4. Make zodiac and ayanamsa configuration explicit.
5. Add tests for provider behavior using known regression fixtures.

Do not implement the full application.

Important:
Do not ask an LLM to calculate anything.

Before adding a dependency, verify its current licensing implications for a commercial application and document the decision.

Run tests.
