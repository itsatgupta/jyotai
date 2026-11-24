# JyotAI handover

Last refreshed 2026-11-24 (NEXT-FIX-DEG-01, deployed). Current status file; `PROJECT_STATUS.md` and
`docs/ROADMAP.md` checkboxes are history only. Earlier detail per task: git history and
`docs/ASTROLOGY_METHOD.md`.

## Live state

| Item | Value |
| --- | --- |
| Repo | `itsatgupta/jyotai`, branch `main` |
| Live SHA | **Render** `/health`: `5ea4af1` (NEXT-FIX-DEG-01 merge, the latest first-parent `main` commit touching `apps/`). **Vercel** `githubCommitSha`: `origin/main` HEAD, i.e. this docs-only commit (same code as `5ea4af1`). Verified 2026-11-24: Render `/health` = `5ea4af1`; Vercel Production READY at `5ea4af1` before this commit; live synthetic checks PASS (10th lord in 7th and in 8th: pending-verification direct line, no Why link; Rahu/Rahu: same-lord line, no self-count; no duplicate occupancy in any; D1 planet cards show DD°MM′, nakshatra · pada, ℞ on desktop 1440px and mobile 390px). Rollback target `fb8a907` (code `3eb8216`). |
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
- **Reviewer verdicts** (NEXT-ADMIT-02, Sitting 1 + 2): reviewer weights (secondary rules shown
  as "Supporting", after primary ones; display order only); the rule lord's sign dignity as a
  calculated fact next to the rule (modifier only); Period themes in the compact X18 v2 form,
  one closing at the end ("These are the reviewed themes associated with this period; actual
  results depend on the full chart and other active factors."), Antardasha lines labelled
  "(secondary)"; Travel shown as "Residence away from birthplace"; X18 labelled "Project
  interpretive convention, reviewer-approved; no source verse identified" in the evidence.
- **Wording fixes** (NEXT-FIX-DEG-01): in "Calculated Dasha lord relationships" each relationship
  is stated once per lord (a TRUE `occupies_tenth` is carried by the placement sentence); an
  Antardasha of the Mahadasha's own lord is one line ("<Lord> Antardasha (dates): the same lord
  as the Mahadasha, stated above.") with no "counted from" its own sign; a paused/withheld rule
  (v.72 7th house, v.76) gets the direct line "A reviewed indication exists for your 10th lord's
  placement; its wording is pending source verification." and is excluded from Why
  (`CareerSynthesis.withheld_claim_ids`; Why says it is not linked). The glance wording for
  these rules is unchanged.
- **Planet degrees** (NEXT-FIX-DEG-01, calculated facts only): every D1 graha and the Lagna
  expose `degree_in_sign_dms` (DD°MM′, minutes truncated; `chart.format_degree_in_sign`)
  next to the existing `degree_in_sign`, `nakshatra`/`pada` and `retrograde` (speed < 0;
  true nodes, Ketu mirrors Rahu). Shown on the D1 planet cards (sign + degree, nakshatra ·
  pada, "℞ Retrograde") and in "D1 planetary details". The Kundli diagram stays without
  degrees (houses with 3+ planets would not stay readable on mobile). D9/D10 and transits
  keep the decimal degree.
- **Palette** (NEXT-UI-AMBER, presentation only): saffron/amber/gold primary accent, indigo
  depth, turquoise sparing, violet a subtle tint; light theme parchment with saffron/maroon
  accents. Every colour is a token in `apps/web/src/theme/tokens.css` (primitives + `--ui-*` /
  `--planet-*` semantics for light and dark); `theme/components.css` (imported last, colour
  only) styles buttons, chips, composer, Dasha periods and the wheel. Guards:
  `src/theme/tokens.test.ts` (no literals outside tokens) and `contrast.test.ts` (WCAG AA
  pairs). Rendered audit 0/1,732 text elements below AA (was 241/1,730). Palette, method and
  screenshots: `docs/FRONTEND_VISUAL_SYSTEM.md`, `docs/design/screenshots/next-ui-amber/`.
  Layout verified unchanged against production builds (`scripts/visual/layout-diff.mjs`).
  Not done: profile-strip/transit sign glyphs remain OS colour emoji (violet tiles on Apple);
  text presentation there would change line heights.
- **Tone rule** (NEXT-TONE-01, NEXT-CLEANUP-01): at most one template non-prediction sentence per answer, at the end.
  Admitted/approved text is not counted and is never reworded. Guard: `tests/test_tone.py`.

## What is admitted (records)

| Item | Release / module | Record |
| --- | --- | --- |
| Natal rules, 26: Career 9 (10th lord: 1; 2/3; 7 (wording paused, v.72 मद); 4; 10; 5/11; 6/12; 8 (wording withheld); 9), General 1 (11th lord in 9/10), Wealth 4, Spirituality 4, Children 2, Education 3, Business 1, Travel 1, Friends 1. All `CONTEXTUAL`, no polarity; weights primary/secondary (`rule_weights.py`). Children "10th lord in 5/11" kept in the ledger, not surfaced. | `jyotish.production.cumulative@v12` (`knowledge/admit02_pack_v1.py`); v11 and earlier unchanged | Part 0: `docs/admissions/jyotish.career.10th-lord-in-1.admission.v1.md`, `…10th-lord-in-2-3-7.admission.v1.md`, `…10th-lord-in-8.admission.v1.md`; earlier packs (pre-Part-0 Career rules and every other domain): in-code `ReviewRecord`s in `knowledge/*_pack_v1.py`, "JyotAI project-owner review", not independently certified |
| Timing, 2 (Career): v.87 10th lord in 4th (MD only); v.140 Moon MD / Venus AD, Venus own/exalted (conjunctive). Reviewer wording since v3. v.89 is a candidate only. | `jyotish.timing.production.career@v3` (v1/v2 unchanged) | `timing_rules/registry.py`; `docs/admissions/jyotish.admit02.sitting-1-2.admission.v1.md` |
| Significations (0b terms, reviewer glosses, शत्रु restored) + X18 v2 (compact form, MD primary / AD secondary) | `jyotish.signification.production@v3` (`signification_admit02_v1.py`; v1/v2 unchanged) | `docs/admissions/jyotish.signification.part0b.admission.v1.md`, `…v2.md` (शत्रु removed), `docs/admissions/jyotish.lordship-principle.x18.admission.v1.md` |
| Dasha interpretation corpus | — | **Empty** (slot present, review-gated) |

**NEXT-ADMIT-02** (2026-11-24): the reviewer's Sitting 1 + 2 written verdicts
(`research/prereview/pandit-ji-verdicts-2026-11-24.md`, verbatim) admitted on owner
instruction. Record: reviewer "Pandit ji (full name pending)", Acharya; written verdicts
relayed by Atul, 2026-11-24; authorship of the written verdicts not independently confirmed.
Every item and decision: `docs/admissions/jyotish.admit02.sitting-1-2.admission.v1.md`.
Held: P1–P4, P6 (pending source verification), P5 (no reviewer-approved wording for the two
Dashas; the packet's only result is śubha, which item 21 makes a modifier). Paused: the
7th-house part of v.72.

Part 0 approval as recorded: reviewer "Pandit ji" (**full name pending**), Acharya, verbal, relayed by Atul,
2026-11-23, general approval "as proposed". **Part 1 and Part 2 remain REVIEW_REQUESTED.** Reviewer feedback of
2026-11-24 (`docs/admissions/feedback-2026-11-24.md`, "the app is producing good results") is general feedback on
live output: **not an admission, not a Part 1 decision.** AI pre-review (`research/prereview/`) is never a review.

## Open items

| # | Item | Owner |
| --- | --- | --- |
| 1 | Reviewer's full name → superseding records for the five admission records and CALC-03 | Atul (obtain), engineering (records) |
| 2 | Held Part 1 items: source verification for P1, P2 (and the v.78/v.79 frame), P3 (then promote v.89), P4, P6 (दशाशुभा reading); P5 needs reviewer wording for each lord's Dasha. Dasha slot still empty | Reviewer, then engineering |
| 3 | v.76 user wording (10th lord in 8th; withheld; द्व reading and अल्पायु discrepancy open) and v.72 मद (7th house, paused) | Reviewer (source), Atul (decision) |
| 4 | Item 23 label: verdict wording "Residence away from birthplace / foreign-place comfort indication" vs the shorter label in use | Atul |
| 5 | CALC-03 details: charts, quantities, reference software, differences (`docs/validation/CALC-03-expert-check.md`) | Atul / reviewer |
| 6 | A source verse for X18 (now labelled a project interpretive convention) | Reviewer |
| 7 | LLM real-model gate: run the ranking and evaluative guards against a real model on the full benchmark before `LLM_ENABLED` | Engineering (run), Atul (approve) |
| 8 | Other domains: timing, comparisons, more rules (new doctrine via review only) | Reviewer (doctrine), engineering |
| 9 | Test-user feedback (`USER_RATING_PENDING` in the benchmark) | Atul |
| 10 | Part 2 (optional): polarity X11, dimensions X12, X14, X15 → ranking/promotion | Reviewer |
| 11 | Candidate methodology items now that degrees are shown (none implemented; each needs a reviewer-approved method and wording): combustion (asta) orbs per graha; conjunction orb / degree-based yuti; avasthas (e.g. bālādi by degree); degree-based strength (deep exaltation/debilitation, shadbala); nakshatra-lord interpretation; pada-based (D9) reading | Reviewer (method), Atul (decision) |

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
   Current **v21** (NEXT-FIX-DEG-01, wording; every v20 count and gate identical, new `fixdeg01_counts` over every turn:
   18 Dasha-context sections, 0 duplicate occupancy (v20: 5), 0 repeated sentences (v20: 1), 0 self-count (v20: 1),
   1 same-lord back-reference, 0 Why links on paused/withheld rules). Before it, **v20** (NEXT-ADMIT-02, doctrine; every v19 count and gate identical, new `admit02_counts`: 12/12 Period
   themes with one closing, 0 old closings, 23/23 Antardasha lines "(secondary)", 12/12 natal sections with the dignity
   fact). 34 product journeys (hard gates 34/34 PASS, 25/25 follow-ups), 4 comparison journeys (4/4, 9/9 follow-ups),
   8 bare-comparison journeys (8/8).

**Protected:** never open or stage `jyotai-marriage-pack-research.txt`; never stage `google-adk/`; do not read
`research/next_08d/`; do not modify the BPHS PDF (SHA-256 `d333ebe1…6108`); synthetic births only; no secrets.

## Test baselines (after NEXT-UI-AMBER, local)

- Backend: **1078 passed** (`uv run pytest`); 1041 after NEXT-ADMIT-02, 1005 after NEXT-THEMES-01.
- Frontend: **189 passed** (`npm test`; 113 of them the theme token/contrast guards); 76 after
  NEXT-FIX-DEG-01, 71 after NEXT-ADMIT-02.
- Ruff check and format clean (168 files); mypy clean (101 source files).

## Known gaps

No ranking method; promotion unsupported; no income timing rule. Dasha corpus empty. No strength model (X2: sign
dignity is shown as a calculated modifier only). Degrees are displayed but no degree-based
rule exists (combustion, orbs, avasthas: open item 11).
CALC-02 lacks an independent numerical reference; Swiss Ephemeris data files and the Moshier fallback still to validate.
