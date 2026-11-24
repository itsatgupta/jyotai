# JyotAI handover

Last refreshed 2026-11-24 (NEXT-THEMES-01). Current status file; `PROJECT_STATUS.md` and
`docs/ROADMAP.md` checkboxes are history only. Earlier detail per task: git history and
`docs/ASTROLOGY_METHOD.md`.

## Live state

| Item | Value |
| --- | --- |
| Repo | `itsatgupta/jyotai`, branch `main` |
| Live SHA | **Render** `/health`: `c8df17d` (NEXT-THEMES-01 merge, the latest first-parent `main` commit touching `apps/`). **Vercel** `githubCommitSha`: `origin/main` HEAD, i.e. this docs-only commit (same code as `c8df17d`). Verified 2026-11-24: Render `/health` = `c8df17d`; Vercel Production deployment `success` at `c8df17d` before this commit. Rollback target `bc171a2`. |
| Backend | Render, `https://jyotai-api-2x0m.onrender.com`; `GET /health` → `{"status":"ok","commit":"<sha>"}` |
| Frontend | Vercel (Vite/React, `apps/web`); `VITE_API_BASE_URL` set at build time |
| Method | Vedic, sidereal, **Lahiri**, Whole Sign from D1 Lagna, true nodes, **Vimshottari** (365.25-day year). Never change silently. |
| LLM | Optional narrative layer (`LLM_ENABLED`). **Production: OFF** (found on 2026-11-23, switched off the same day). The gate below stands. |

## Current capabilities

- **Career year answers** ("How is my career in 2027?"): direct line (matched timing rule: framing + admitted meaning
  sentence verbatim + pointer to the timing section; no match: the year's MD/AD, the natal indication, "No reviewed
  timing rule applies to <year>."), "<Year> at a glance" (periods, natal with the 10th lord named once, one calculated
  link by fixed display precedence, Period themes, timing status), Period themes (X18), Why (co-reference links only;
  never combines, weighs or ranks), natal, Dasha + linkage facts ("Chart details"), reviewed timing, one closing
  non-prediction sentence. Drill-down buttons ("Why?", "Which Dasha applies?", "What does … mean?").
- **Career comparison** ("Which is better for my career, 2027 or 2028?"; bare "2027 or 2028?" after a Career turn, else
  a which-area clarification): factual side-by-side, never a ranking (`comparison-view-v1`). The no-ranking point is
  made twice: the direct line ("I can't rank …") and one "why" sentence ("The reviewed rules describe context and have
  no approved way to compare periods."), then one limitation. `composition/comparison_guard.py` bans ranking words.
- **Other domains** (Wealth, Education, Business, Children, Travel, Friends, Spirituality, General): natal contextual
  rules only, via `application/detailed_answer.py`. One template non-prediction sentence (the closing limitation); a
  timing question gets the factual line "No reviewed timing rule is available for this area." (NEXT-CLEANUP-01).
- **Period themes presentation** (NEXT-THEMES-01): a same-lord MD/AD over the same window gives one line
  ("<Lord> Mahadasha and Antardasha"); the glance bullet names each lord once with its houses ("Saturn: 9th, 10th,
  7th houses · …"); every answer carries `rule_review_types` (Independent reviewer (Pandit ji, Acharya) /
  Project-owner review (not independently certified)), shown only in the evidence disclosure. The X18 record's
  "glance lists each period's terms" placement note predates this owner-requested presentation change.
- **Tone rule** (NEXT-TONE-01, NEXT-CLEANUP-01): at most one template non-prediction sentence per answer, at the end.
  Admitted/approved text is not counted and is never reworded. Guard: `tests/test_tone.py`.

## What is admitted (records)

| Item | Release / module | Record |
| --- | --- | --- |
| Natal rules, 25: Career 8 (10th lord in every placement: 1; 2/3/7; 4/10; 5/11; 6/12; 8 (wording withheld); 9; 11th lord in 9/10), Wealth 4, Spirituality 4, Children 3, Education 3, Business 1, Travel 1, Friends 1. All `CONTEXTUAL`, no polarity. | `jyotish.production.cumulative@v11`, `knowledge/*_pack_v1.py`, `career_part0_pack_v1.py` | Part 0: `docs/admissions/jyotish.career.10th-lord-in-1.admission.v1.md`, `…10th-lord-in-2-3-7.admission.v1.md`, `…10th-lord-in-8.admission.v1.md`; earlier packs (pre-Part-0 Career rules and every other domain): in-code `ReviewRecord`s in `knowledge/*_pack_v1.py`, "JyotAI project-owner review", not independently certified |
| Timing, 2 (Career): v.87 10th lord in 4th (MD); v.140 Moon MD / Venus AD, Venus own/exalted. v.89 is a candidate only. | `jyotish.timing.production.career@v2` | `timing_rules/registry.py` |
| Significations (0b terms) + X18 lordship principle (Period themes) | `jyotish.signification.production@v2` | `docs/admissions/jyotish.signification.part0b.admission.v1.md`, `…v2.md` (शत्रु removed), `docs/admissions/jyotish.lordship-principle.x18.admission.v1.md` |
| Dasha interpretation corpus | — | **Empty** (slot present, review-gated) |

Part 0 approval as recorded: reviewer "Pandit ji" (**full name pending**), Acharya, verbal, relayed by Atul,
2026-11-23, general approval "as proposed". **Part 1 and Part 2 remain REVIEW_REQUESTED.** Reviewer feedback of
2026-11-24 (`docs/admissions/feedback-2026-11-24.md`, "the app is producing good results") is general feedback on
live output: **not an admission, not a Part 1 decision.** AI pre-review (`research/prereview/`) is never a review.

## Open items

| # | Item | Owner |
| --- | --- | --- |
| 1 | Reviewer's full name → superseding records for the five admission records and CALC-03 | Atul (obtain), engineering (records) |
| 2 | Part 1 (P1–P6, X1–X10, X17) plus the NEXT-THEMES-01 addendum (items 25–56: 22 owner-reviewed rules, X10 glosses, X18 compact form) via `research/prereview/pandit-ji-checklist.md`; on return admit P1–P6, `display_text` (X10), MD/AD scope (X1), fill the Dasha slot, promote v.89 if P3 approved | Reviewer, then engineering |
| 3 | v.76 user wording (10th lord in 8th; withheld) | Reviewer (wording), Atul (decision) |
| 4 | 6th-house शत्रु: confirm or reject its Career use | Reviewer |
| 5 | CALC-03 details: charts, quantities, reference software, differences (`docs/validation/CALC-03-expert-check.md`) | Atul / reviewer |
| 6 | X18 closing "This does not predict an event or an outcome." stays as approved text (so Period-themes answers keep it beside the closing line); a source verse for X18; any change needs approval | Reviewer |
| 7 | LLM real-model gate: run the ranking and evaluative guards against a real model on the full benchmark before `LLM_ENABLED` | Engineering (run), Atul (approve) |
| 8 | Other domains: timing, comparisons, more rules (new doctrine via review only) | Reviewer (doctrine), engineering |
| 9 | Test-user feedback (`USER_RATING_PENDING` in the benchmark) | Atul |
| 10 | Part 2 (optional): polarity X11, dimensions X12, X14, X15 → ranking/promotion | Reviewer |

## Governance (non-negotiable)

- The LLM never calculates. Admitted text is quoted byte for byte; rewording needs approved `display_text`.
- No scores, weighted sums, rankings or verdicts. UNKNOWN is never FALSE; absence is not negative evidence.
- New doctrine only through independent human review plus a record; `knowledge/reviewer_guard.py` rejects AI/pre-review.
- CALC-02 is **NO-GO** for numerical certification; CALC-03 is a general expert confirmation only.
- **Gate:** `LLM_ENABLED` stays off until `composition/comparison_guard.py` and `composition/evaluative_guard.py` pass
  against a real model on the full benchmark (so far tested with fake transports only).

## Procedure

1. Branch `next-<task>` from `main`; `git branch backup/<task>-pre-squash` before any history rewrite.
2. Gate: `cd apps/api && uv run pytest && uv run ruff check . && uv run ruff format --check . && uv run mypy src`;
   `cd apps/web && npm test && npm run lint && npm run build`; `git diff --check`.
3. Show `git diff --cached --name-only` before every commit; stage paths explicitly. Conventional Commits; merge
   `--no-ff` as `Merge NEXT-<TASK>: …`.
4. Push/deploy only with owner approval. Vercel redeploys every push; **Render skips docs-only commits**.
5. Verify: Render `/health` commit = `git log -1 --first-parent --format=%H origin/main -- apps/`; Vercel production
   `githubCommitSha` = `git rev-parse origin/main`.
6. Benchmarks (`apps/api/tests/consultation_quality_benchmark.py`): earlier fixtures stay frozen; each change adds `vN`.
   Current **v19** (NEXT-THEMES-01, presentation only over v18, every count identical). 34 product journeys (hard gates
   34/34 PASS, 25/25 follow-ups), 4 comparison journeys (4/4, 9/9 follow-ups), 8 bare-comparison journeys (8/8).

**Protected:** never open or stage `jyotai-marriage-pack-research.txt`; never stage `google-adk/`; do not read
`research/next_08d/`; do not modify the BPHS PDF (SHA-256 `d333ebe1…6108`); synthetic births only; no secrets.

## Test baselines (after NEXT-THEMES-01; Render live is `c8df17d`)

- Backend: **1005 passed** (`uv run pytest`); 993 at `bc171a2`, 988 at `01dbe20`.
- Frontend: **71 passed** (`npm test`); 70 at `bc171a2`.
- Ruff check and format clean (161 files); mypy clean (97 source files).

## Known gaps

No ranking method; promotion unsupported; no income timing rule. Dasha corpus empty. No strength model (v.80 open, X2).
CALC-02 lacks an independent numerical reference; Swiss Ephemeris data files and the Moshier fallback still to validate.
