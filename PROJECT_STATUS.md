# JyotAI — Project Status

## Application

JyotAI

## Completed

- Task 01 backend foundation
- Task 02 birth input
- Task 03 ephemeris abstraction
- Task 04 Swiss Ephemeris + deterministic D1
- Task 05 deterministic Vargas
- Task 06 deterministic Vimshottari Mahadasha and Antardasha

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
- stateless staging chart API for D1, D2, D9, and D10 deployment verification

## Task 06 quality gate

- 95 tests passed
- Ruff passed
- mypy passed

## Known outstanding validation

- independent known-chart validation
- Swiss ephemeris data-file setup
- current Moshier fallback when Swiss data files are absent
- commercial licensing review if product is commercialized

## Next planned task

Task 07 — Transits

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
- Task 05 remains the latest completed astrology task; Task 06 remains next.
- Independent astrology accuracy validation remains outstanding.
