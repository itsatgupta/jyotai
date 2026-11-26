# JyotAI handover

Last refreshed 2026-11-26 (NEXT-PROPERTY-01, deployed). Current status file; `PROJECT_STATUS.md` and
`docs/ROADMAP.md` checkboxes are history only. Earlier detail per task: git history and
`docs/ASTROLOGY_METHOD.md`.

## Live state

| Item | Value |
| --- | --- |
| Repo | `itsatgupta/jyotai`, branch `main` |
| Live SHA | **Vercel** `githubCommitSha`: `origin/main` HEAD, i.e. this docs-only commit (code `4ecf0e9`, NEXT-PROPERTY-01 merge). **Render** `/health`: `4ecf0e9` (= `git log --first-parent -1 --format=%h -- apps/api`). Verified 2026-11-26: Render `/health` = `4ecf0e9cceee88668c5e6132369e0940918040db`; GitHub deployment 8078936405 (Vercel, Production) success at `4ecf0e9`; live synthetic check (benchmark profile P_MATCH, "When will I buy a house?"): `/api/v1/consultation` returns direct, periods, period_themes ("(primary)"/"(secondary)" + pending line), chart_factors, timing_status, limit; 0 provisional items without the flag; 8 with `include_provisional=true` (the Property significations), no translation sent. Screenshots: `docs/design/screenshots/next-property-01/` (property/ and wealth/, toggle off and on, desktop/mobile, light/dark; `apps/web/scripts/visual/domain-answer.mjs` against a local API with `CORS_ALLOWED_ORIGINS='["http://localhost:5173"]'` and base URL `http://localhost:5173/`). Rollback target: Vercel and Render `cb4f25a` (NEXT-WEALTH-01). |
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
- **Other domains** (Education, Business, Children, Travel, Friends, Spirituality, General): natal contextual
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
- **Provisional tier** (NEXT-PROVISIONAL-01; owner decision: all domains provisional first, one
  final expert review). Separate corpus `jyotish.provisional@v1` (3 rules: Education v.37,
  Spirituality v.40, Wealth v.54; author "project owner, provisional"; status PROVISIONAL,
  never REVIEWED). Shown only with `include_provisional=true` / the web toggle "Show
  provisional interpretations (beta)" (off by default, remembered per browser), badged
  "Provisional — pending expert review", justification in the evidence disclosure. Promotion
  only via `promote_to_reviewed` with human review records. Review pack:
  `research/final-review/review-pack.md` (`uv run python -m astrologer.knowledge.review_pack
  --pdf`). Method: `docs/ASTROLOGY_METHOD.md` "Provisional rule tier". Screenshots:
  `docs/design/screenshots/next-provisional-01/`.
- **Marriage domain, provisional** (NEXT-MARRIAGE-01): outlook, timing and year questions in
  the consultation layout (calculated 7th lord / Venus factors with sign dignity as a modifier
  fact; for timing, the 7th lord's and Venus's MD/AD periods in the asked range, their
  reviewed Period themes, "No reviewed timing rule exists for marriage", no date, no
  ranking). One-line out-of-scope answers: compatibility / guna milan, Mangal checks,
  predictions of a marriage ending, fatalistic questions. Marriage wording guard
  (`composition/marriage_guard.py`). Provisional corpus `jyotish.provisional@v2`: 9 Marriage
  rules (BPHS vv. 50–56; 12th house shown, 8 houses wording held, 3rd/5th/11th located but
  not drafted). Author field: "drafted_by: AI agent; adopted_by: project owner (pending)"
  (seed rules included); badge "Provisional · <confidence> confidence". Method:
  `docs/ASTROLOGY_METHOD.md` "Marriage domain, provisional". Screenshots:
  `docs/design/screenshots/next-marriage-01/` (`apps/web/scripts/visual/marriage.mjs`).
- **Topic-tagged significations + D9 facts** (NEXT-MARRIAGE-02): every signification term
  carries domain tags (reviewed/provisional); answers show only terms tagged for the asked
  domain (`knowledge/signification_tags.py`, tag set `jyotish.signification.domain-tags@v1`:
  every reviewed term Career (reviewed) only; manifests untouched, Career answers
  byte-identical). Marriage Period themes therefore list the periods only + "Reviewed
  marriage meanings for these periods are pending expert review." Provisional Marriage
  significations (`jyotish.provisional.signification@v1`, toggle only, kind `signification`):
  7th house जाया "spouse" (high), Venus कलत्र kāraka "spouse" (high), 2nd house कुटुम्ब
  "family" (low); the 7th/2nd verses' translations stay in the review pack (they also list
  death). Marriage answers gain "Calculated D9 (Navamsa) factors" (D9 Lagna, D9 7th lord and
  its D9 house, Venus's D9 sign/house, D1 7th lord vargottama yes/no; facts only). Method:
  `docs/ASTROLOGY_METHOD.md` "Topic-tagged significations …".
- **Domain template + Wealth, provisional** (NEXT-WEALTH-01): `application/domain_pipeline.py`
  (one pipeline from a `DomainConfig`: houses/lords, kārakas, tag, texts, guard, out-of-scope,
  divisional facts) and the registry `application/domains.py`. Marriage runs on it
  (byte-identical apart from the carry-overs). Career: config only (10th house, Career tag);
  its timing/year/comparison composition is still the Career code (open item 15). Wealth
  answers: 2nd/11th lords and Jupiter as calculated facts with dignity; reviewed natal Wealth
  rules (Sitting 1 items 8–11 only; the General 11th-lord rule never shows: exact-domain
  selector); periods of the 2nd lord, 11th lord and Jupiter only ("No reviewed timing rule
  exists for wealth"); Period themes = periods + "Reviewed wealth meanings … pending expert
  review"; no Career or Marriage term; out-of-scope lines for investment, amounts, fatalistic
  questions; guard `composition/wealth_guard.py`. Provisional Wealth (toggle): corpus
  `jyotish.provisional@v3` (+9 second-lord rules: 7 shown, v.13 and v.18 held) and
  `jyotish.provisional.signification@v2` (धन 2nd, लाभ 11th, Jupiter धन kāraka, कुटुम्ब moved
  from Marriage to Wealth); every Wealth item's translation stays in the review pack. Carry-overs:
  dignity line "Calculated fact (sign dignity)" everywhere; untagged corpora show in no domain
  except the named legacy/test ones; periods past the window "(continues past the window)".
  Method: `docs/ASTROLOGY_METHOD.md` "Domain template, Wealth domain, provisional".
- **Property domain, provisional** (NEXT-PROPERTY-01): `application/property.py` on the domain
  template: the 4th lord and the kārakas the text names for land, house and vehicles with a
  high-confidence reading (Mars भूमि/सद्म v.3, Jupiter गृह v.5, Venus यान v.6; PDF p. 109) as
  calculated facts with dignity; periods only for timing ("No reviewed timing rule exists for
  property"); Period themes = periods + "Reviewed property meanings … pending expert review";
  no Career, Marriage or Wealth term; no reviewed Property rule exists. Out-of-scope lines:
  prices, buy/sell/invest advice, legal matters, fatalistic questions; guard
  `composition/property_guard.py`. D4 is not calculated (open item 18). Provisional (toggle):
  `jyotish.provisional@v4` (+ 4th lord in 2nd, v.27 सर्वसम्पद्युत, low; 11 placements not
  drafted: no land/house/vehicle clause) and `jyotish.provisional.signification@v3` (+8 Property
  terms: 4th house गृह, क्षेत्र, वाहन; Mars भूमि, सद्म; Jupiter गृह; Venus यान; Sun क्षेत्र);
  every translation stays in the review pack. Carry-overs: router (money/income/savings/rich and
  Hinglish → Wealth, flat/land/plot/car/ghar → Property, only when no other domain is named;
  numbered houses are not a Property word; "kab" is a timing word); Period themes label every
  Mahadasha "(primary)" and Antardasha "(secondary)" in all domains; v.54 record v2 (translation
  in the review pack). Method: `docs/ASTROLOGY_METHOD.md` "Property domain, provisional".
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
| 12 | Final expert review of every provisional rule (`research/final-review/review-pack.md`); then promote/change/reject each through `promote_to_reviewed`. More provisional rules per domain are owner work (justification record required) | Atul (author), reviewer (decision), engineering (records) |
| 13 | Marriage: reviewer wording for the 8 held 7th-lord rules (owner: stays held, no fear-based text); decision on the 3 provisional Marriage significations (review pack, section "Provisional significations: Marriage"); any marriage timing rule | Reviewer, Atul |
| 14 | D9 interpretation for marriage (now shown as calculated facts only: D9 Lagna, D9 7th lord and house, Venus in D9, vargottama): a reviewer-approved method and wording, if any | Reviewer (method), Atul (decision) |
| 15 | Career only partly on the domain template (timing, year and comparison still on the Career code) | Engineering |
| 16 | Wealth: decisions on the 9 provisional second-lord rules (wording for held v.13/v.18), the 4 provisional Wealth significations, and the review-pack questions (v.35/v.36; may the Career-tagged धन/लाभ/वृद्धि be tagged Wealth); any wealth timing rule | Reviewer, Atul |
| 17 | Property: decisions on the provisional 4th-lord rule (v.27, सम्पद्: property or wealth?) and the 8 Property significations; which kārakas (Mars, Jupiter, Venus used; Sun's क्षेत्र medium; v.37 Moon/Mercury); any property timing rule; whether बन्धु/मातृसौख्य need a domain of their own | Reviewer, Atul |
| 18 | D4 (Chaturthāṁśa) is not calculated: a reviewer-approved D4 method first, then D4 facts in Property answers | Reviewer (method), engineering |
| 19 | Generic domains (Marriage, Wealth, Property): the follow-up "Which Dasha applies?" still replies "No approved timing evidence is available for this domain", although the answer lists the calculated periods | Engineering |
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
5. Verify: Render `/health` commit = the last `apps/api` commit on main, `git log --first-parent -1 --format=%h --
   apps/api` (compare the short SHA); Vercel production `githubCommitSha` = `git rev-parse origin/main` (HEAD).
6. Benchmarks (`apps/api/tests/consultation_quality_benchmark.py`): earlier fixtures stay frozen; each change adds `vN`.
   Current **v26** (NEXT-PROPERTY-01: with `include_provisional=false` every v25 count and gate
   is identical except `signification_counts.answers_with_period_themes` 11 → 12 (J14's Property
   answer). Journeys changed: LABEL only ("Mahadasha (primary)" / merged "Mahadasha (primary) and
   Antardasha (secondary)"): J03, J09, J10, J20, J23–J26, J32–J34, C01, C02, C04, W02–W04, W06;
   A4 only (v.54 translation no longer sent, flag on): W07, W08; PROPERTY: J14 (now the Property
   answer; checks, answerability, follow-up unchanged). The router changes affect no journey.
   Flag on: `provisional_counts` +8 (J14's Property significations), `wealth_counts` translation
   sent 2 → 0. New `property_counts` over 14 journeys P01–P14 (flag off and on): 14/14 PASS, 0
   other-domain terms, 0 reviewed evidence, 26 periods (4 continuing), 5/5 MD lines "(primary)",
   12/12 AD lines "(secondary)", 5 out-of-scope one-liners, 0 guard failures, 0 advice/date
   claims, flag on 75 items (3 rule, 72 signification, 0 translations sent); new
   `period_theme_label_counts` over every journey set: 23/23 MD primary, 46/46 AD secondary.
   v25 file unedited; the replay test points at v26). Before it, **v25** (NEXT-WEALTH-01: with `include_provisional=false` every v24 count and gate
   is identical; journey texts differ from v24 only by A1 (dignity prefix: J02–J04, J06–J11,
   J13, J16–J21, J23–J26, J28–J30, J32–J34, C01–C04, B05–B08), A1+A4 (J15), A1/A2/A4 (M01–M14:
   A2 removes the कुटुम्ब item with the flag on) and the Wealth answer (J12; J22's Wealth
   answer). New `wealth_counts` over 12 wealth journeys W01–W12: 12/12 PASS, 0 Career or
   Marriage terms, 0 General-rule statements, 0 guard failures, 0 date claims, 15 periods
   (6 continuing past the window), flag on 46 items (2 held). v24 file unedited; the replay
   test points at v25). Before it, **v24** (NEXT-MARRIAGE-02: with `include_provisional=false` every v23 count, gate
   and non-marriage journey is identical (all Career answers byte-identical); only J15/J17 and
   the 14 marriage journeys change. `marriage_counts`: 14/14 PASS, 0 answers with a Career
   term, 4/4 Period themes with the pending line, 10 D9 sections (each ending with the
   framing line), 0 guard failures, 0 date claims, flag on 40 items (10 rules, 7 held, 30
   significations). `provisional_counts`: 9 items flag on (6 significations), 48/48 reviewed
   parts identical). Before it, **v23** (NEXT-MARRIAGE-01: with `include_provisional=false` every v22 count and
   gate is identical; only the two v22 marriage journeys J15/J17 now carry the marriage answer
   (same checks and answerability). New `marriage_counts` over 14 marriage journeys: 14/14
   hard gates PASS, 3 outlook (calculated factors only), 7 timing (all state no reviewed timing
   rule; 8 periods listed), 4 out-of-scope one-liners, 0 wording-guard failures, 0 date claims,
   0 provisional items with the flag off, 10 with it on (7 held). `provisional_counts` now on
   corpus v2). Before it, **v22** (NEXT-PROVISIONAL-01: every journey runs with `include_provisional=false`
   and every v21 key, count, gate and journey snapshot is identical; new `provisional_counts`
   over 48 requests, flag off/on: 0 provisional items with the flag off, 48/48 reviewed parts
   byte-identical with it on, 1 provisional item (Spirituality v.40) badged, fully justified,
   0 guard failures, 0 labelled reviewed). Before it, **v21** (NEXT-FIX-DEG-01, wording; every v20 count and gate identical, new `fixdeg01_counts` over every turn:
   18 Dasha-context sections, 0 duplicate occupancy (v20: 5), 0 repeated sentences (v20: 1), 0 self-count (v20: 1),
   1 same-lord back-reference, 0 Why links on paused/withheld rules). Before it, **v20** (NEXT-ADMIT-02, doctrine; every v19 count and gate identical, new `admit02_counts`: 12/12 Period
   themes with one closing, 0 old closings, 23/23 Antardasha lines "(secondary)", 12/12 natal sections with the dignity
   fact). 34 product journeys (hard gates 34/34 PASS, 25/25 follow-ups), 4 comparison journeys (4/4, 9/9 follow-ups),
   8 bare-comparison journeys (8/8).

**Protected:** never open or stage `jyotai-marriage-pack-research.txt`; never stage `google-adk/`; do not read
`research/next_08d/`; do not modify the BPHS PDF (SHA-256 `d333ebe1…6108`); synthetic births only; no secrets.

## Test baselines (after NEXT-PROPERTY-01, local)

- Backend: **1303 passed** (`uv run pytest`); 1243 after NEXT-WEALTH-01.
- Frontend: **203 passed** (`npm test`); 202 after NEXT-WEALTH-01.
- Ruff check and format clean (192 files); mypy clean (119 source files).

## Known gaps

No ranking method; promotion unsupported; no income, wealth or property timing rule; no D4. Dasha corpus empty. No
reviewed signification term is tagged for any domain but Career. D9 is shown as facts only. No strength model (X2: sign
dignity is shown as a calculated modifier only). Degrees are displayed but no degree-based
rule exists (combustion, orbs, avasthas: open item 11).
CALC-02 lacks an independent numerical reference; Swiss Ephemeris data files and the Moshier fallback still to validate.
