# JyotAI — Project Status

## Application

JyotAI

## Completed

- Task 01 backend foundation
- Task 02 birth input
- Task 03 ephemeris abstraction
- Task 04 Swiss Ephemeris + deterministic D1
- Task 05 deterministic Vargas
- Task 06 deterministic Vimshottari Mahadasha and Antardasha, completed and
  benchmarked against two AstroSage charts with documented methodology
  differences
- Task 07 deterministic transit-v1 positions and sign/station events for
  Jupiter, Saturn, true Rahu, and Ketu
- Task 08 deterministic declarative rule-framework v1: validated supplied
  facts, three-state condition evaluation, rule/result traceability, and a
  format-neutral loader; synthetic demonstrations only
- Task 09A deterministic Jyotish derived facts v1: D1-only structural facts
  for Whole Sign rulership/lordship, house classifications, approved
  seven-planet Graha Drishti, same-sign occupancy, and sign-level dignity;
  no production rule corpus or interpretation
- Task 09B-v1 Jyotish knowledge governance: immutable source/review/rule
  envelopes, deterministic admission and manifest controls
- Task 09C1 governed evaluation/provenance bridge: immutable governed results
  retain Task 08 traces with source/release and Task 09A fact provenance; the
  production corpus remains empty
- Task 10 deterministic astrology context snapshot: stateless composition of
  D1, D9, D10, active Vimshottari, transit-v1, and Task 09A D1 facts for one
  explicit instant; no interpretation or rule evaluation
- Task 09C2 first admitted Jyotish rule pilot: one source-reviewed, D1-only,
  contextual production rule with immutable registry, fact contract, manifest,
  and governed-evaluation provenance

## Current deterministic capabilities

- Sidereal Jyotish
- Lahiri ayanamsa
- True Rahu/Ketu
- Whole Sign houses
- D1
- D2
- D9
- D10
- Ascendant
- planetary positions
- nakshatra/pada on D1
- deterministic retrograde
- Vimshottari-v1 birth Mahadasha balance, Mahadasha, Antardasha, and period lookup
- transit-v1 point-in-time snapshots, explicit UTC-normalized ranges, sidereal
  sign ingress, station-retrograde, and station-direct events
- deterministic rule-framework v1 operating only on precomputed facts; no
  astrology calculations, production rules, predictions, evidence aggregation,
  or LLM integration
- `jyotish-derived-facts-v1` D1-only structural fact bundle and Task 08
  `FactSet` adapter; Rahu/Ketu rulership, dignity, and aspects are unmodeled
- stateless staging chart API for D1, D2, D9, and D10 deployment verification
- stateless deterministic context API for D1, D9, D10, active Dasha, transit
  snapshot, and D1 derived facts at an explicit instant

## Task 06 quality gate

- 95 tests passed
- Ruff passed
- mypy passed

## Task 07 quality gate

- 108 tests passed
- Ruff passed
- mypy passed

## Known outstanding validation

- continued independent known-chart validation as the engine evolves
- Swiss Ephemeris data-file validation/setup
- current Moshier fallback when Swiss data files are absent
- commercial licensing review if product is commercialized

## Current production corpus

One D1-only contextual rule is admitted in the first non-empty production
release. The historical empty release remains immutable. The source review is
internal project-owner review and is not independent Sanskrit/Jyotish expert
certification.

## Deployment plan

- GitHub = source control
- Render = FastAPI staging/backend (active)
- Render staging URL = https://jyotai-api-2x0m.onrender.com
- Render health endpoint verified at `GET /health`
- Vercel = future Next.js frontend

## Staging verification API

- `POST /api/v1/charts/calculate` calls the existing validated `BirthInput`,
  deterministic `ChartEngine`, and `VargaEngine` only.
- `POST /api/v1/context/snapshot` composes existing deterministic D1, D9, D10,
  active Vimshottari, transit-v1, and Task 09A facts at an explicit instant.
- It is stateless and does not persist or log birth details.
- Task 06 Vimshottari was benchmarked against two AstroSage charts. See
  `docs/VALIDATION_REPORT.md` for documented methodology differences.
