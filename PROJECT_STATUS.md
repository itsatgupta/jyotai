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
- stateless staging chart API for D1, D2, D9, and D10 deployment verification

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

## Next planned task

Task 08 — not started

## Deployment plan

- GitHub = source control
- Render = FastAPI staging/backend (active)
- Render staging URL = https://jyotai-api-2x0m.onrender.com
- Render health endpoint verified at `GET /health`
- Vercel = future Next.js frontend

## Staging verification API

- `POST /api/v1/charts/calculate` calls the existing validated `BirthInput`,
  deterministic `ChartEngine`, and `VargaEngine` only.
- It is stateless and does not persist or log birth details.
- Task 06 is the latest completed astrology task; it was benchmarked against
  two AstroSage charts. See `docs/VALIDATION_REPORT.md` for the documented
  methodology differences.
