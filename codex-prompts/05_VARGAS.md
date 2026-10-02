# Codex Prompt 05 — Deterministic Vargas / Divisional Charts

Read `AGENTS.md`, `docs/ASTROLOGY_METHOD.md`,
`docs/CALCULATION_CONVENTIONS.md`, and the existing D1 chart models/tests.

Implement deterministic, provider-neutral derivation of only:

- D1 / Rashi
- D2 / Hora
- D9 / Navamsa
- D10 / Dasamsa

Derive each Varga exclusively from an already-calculated canonical D1 chart.
Do not make ephemeris calls or use provider-specific types. A Varga longitude is
a synthetic deterministic transformation, not a new astronomical position.

Use immutable Pydantic models with explicit chart type, factor, mapping variant,
source D1 methodology, birth input, calculation instant, provenance, derived
ascendant, Whole Sign houses, and a placement for every D1 body including Rahu
and Ketu. Each placement must retain its source D1 longitude, derived longitude,
sign, degree-in-sign, and house number.

Do not derive a nakshatra or pada from synthetic Varga longitudes. Do not
recalculate motion or retrograde; if exposed, label them explicitly as inherited
D1 facts.

For sign ordinal `i` (Aries = 0) and D1 degree `d` within a sign, use factor
`N`, division index `floor(d * N / 30)`, and Varga degree `(d * N) mod 30`.
Exact boundaries belong to the following division.

Use these fixed, versioned Parashari conventions:

- **D1:** identity mapping.
- **D2:** Parashari Sun/Moon Hora. Odd signs: first Hora Leo, second Cancer.
  Even signs: first Hora Cancer, second Leo.
- **D9:** movable signs start from the same sign, fixed signs from the ninth
  sign, and dual signs from the fifth sign. Subsequent Navamsas advance one
  sign zodiacally.
- **D10:** odd signs start from the same sign; even signs from the ninth sign.
  Subsequent Dasamsas advance one sign zodiacally.

Derive the divisional ascendant with the same transformation and use it as the
Whole Sign house anchor. Update `docs/CALCULATION_CONVENTIONS.md` with these
definitions and boundary behavior.

Add deterministic tests for D2 odd/even mappings and boundaries; D9 movable,
fixed, and dual start cases plus zodiacal advancement; D10 odd/even start cases
plus zodiacal advancement; D9/D10 boundary behavior; Pisces wraparound; D1
identity; derived houses; all required bodies; reproducibility; serialization;
and proof that the Varga engine requires no provider.

Do not implement Dasha, transits, rules, AI, API, database, frontend, or other
Vargas. Run pytest, Ruff checks and formatting checks, and mypy before handoff.
