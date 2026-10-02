# JyotAI — Project Status

## Application

JyotAI

## Completed

- Task 01 backend foundation
- Task 02 birth input
- Task 03 ephemeris abstraction
- Task 04 Swiss Ephemeris + deterministic D1
- Task 05 deterministic Vargas

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

## Task 05 quality gate

- 51 tests passed
- Ruff passed
- mypy passed

## Known outstanding validation

- independent known-chart validation
- Swiss ephemeris data-file setup
- current Moshier fallback when Swiss data files are absent
- commercial licensing review if product is commercialized

## Next planned task

Task 06 — Vimshottari Dasha

## Deployment plan

- GitHub = source control
- Render = FastAPI staging/backend
- Vercel = future Next.js frontend
