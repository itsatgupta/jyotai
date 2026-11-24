# JyotAI handover

Last refreshed 2026-11-24 (NEXT-COMPARE-BARE). This file replaces the older status in `PROJECT_STATUS.md` (Tasks
01–14), which is kept only as history.

## Live state

| Item | Value |
| --- | --- |
| Repo | `itsatgupta/jyotai`, branch `main` |
| Live SHA | **Render** `/health`: `01dbe20` (NEXT-COMPARE-BARE merge, the latest first-parent `main` commit touching `apps/`). **Vercel** `githubCommitSha`: `origin/main` HEAD, i.e. this docs-only commit (same code as `01dbe20`). Verified 2026-11-24: Render `/health` = `01dbe20`, Vercel production READY at `01dbe20` before this commit; live: "Which is better, 2027 or 2028?" after a Career turn returns the Career side-by-side, and on a fresh conversation returns "Which area should I compare 2027 and 2028 for?" with a Career button that returns the side-by-side; narrative null. Render does not rebuild docs-only commits (see deploy procedure). Rollback target `f96ff26`. |
| Backend | Render, `https://jyotai-api-2x0m.onrender.com`; `GET /health` → `{"status":"ok","commit":"<sha>"}` (from `RENDER_GIT_COMMIT`) |
| Frontend | Vercel (Vite/React, `apps/web`); `VITE_API_BASE_URL` set at build time |
| Method | Vedic, sidereal, **Lahiri**, Whole Sign from D1 Lagna, true nodes, **Vimshottari** (365.25-day year). Never change these silently. |
| LLM | Optional narrative layer only (`LLM_ENABLED`, default `false`). It gets a closed packet and is validated; failure falls back to the deterministic answer. **Production: OFF.** On 2026-11-23 the live smoke test found `LLM_ENABLED` enabled on Render (answers carried a `narrative`, e.g. 10th lord in the 9th, "How is my career?"), contrary to the gate. The owner set `LLM_ENABLED=false` on Render the same day; 15 re-run requests then all returned `narrative: null`. The gate below stands. |

## What answers can do now (Career year questions, e.g. "How is my career in 2027?")

- **Governed direct line.** With one matched timing rule: a framing sentence built from facts
  (period lord, source work), then the admitted **meaning sentence verbatim**, then "The full
  reviewed text is quoted in the Reviewed Career timing section below." (the timing section
  keeps the whole admitted text, non-guarantee included). With no match: the year's MD/AD
  periods, the reviewed natal indication by its plain label, then "No reviewed timing rule
  applies to <year>."
- **Why section** (`career-synthesis-v1`): co-reference links SAME_PLANET / SAME_HOUSE /
  SAME_PERIOD only. It never combines, weighs, or ranks. Its framing sentence ("Each line
  states only …") is in the section's `framing` field, shown in the evidence disclosure.
- **One template non-prediction sentence per answer** (NEXT-TONE-01), in the closing "What can
  be concluded" section: "These are reviewed themes and calculated periods for <year>, not a
  prediction of specific events." ("reviewed indications" without Period themes; periods only
  when nothing reviewed matched). A comparison has one, in its limitations. Admitted/approved
  text is not counted and stays where quoted (timing non-guarantee, natal rule text, the X18
  closing "This does not predict an event or an outcome.", the v.76 withheld notice); UNKNOWN
  wording is unchanged. Follow-up replies already carried one each and are unchanged.
  Guard: `tests/test_tone.py`.
- **Dasha context** (`jyotish.dasha_linkage.v1`): per-lord linkage facts (ruled houses,
  placement, 10th lord?, occupies/aspects 10th, same sign as 10th lord, own/exaltation).
- **DashaInterpretationSlot**: present and review-gated. The Dasha corpus is **empty**.
- Plain-language **drill-down buttons** ("Why?", "Which Dasha applies?", "What does … mean?").
- **Comparison is a factual side-by-side, never a ranking** (NEXT-COMPARE-02,
  `comparison-view-v1`, `application/career_comparison.py`). "Which is better for my career,
  2027 or 2028?" returns the view below. **Bare year-vs-year questions** ("Which is better,
  2027 or 2028?", "2027 or 2028?", "compare 2027 and 2028", "is 2028 better than 2027?";
  NEXT-COMPARE-BARE): after a Career turn they are the Career comparison; with no Career turn
  (fresh, unsupported first turn, or a non-Career turn) the consultation replies "Which area
  should I compare 2027 and 2028 for?" with one button per comparison domain
  (`COMPARISON_DOMAINS`, only "Career"), whose question "Compare 2027 and 2028 for my career"
  runs the comparison; typing "Career" works too. The stateless router (`/analyze`) is
  unchanged and still returns `unsupported_language` for them. The view: direct line ("I can't rank …") → what differs (opens with any Mahadasha change
  inside either year, else the Antardasha changes; then periods and dates, which reviewed
  timing indications apply, co-reference links in one year only) → same in both years
  (natal) → full two-column side-by-side (disclosure) → why no ranking → limitations. When the
  direct line says an indication applies in one year only, the next sentence is "An
  indication not applying in a year is not evidence against that year." (once). Unit is the calendar year (MD/AD boundaries shown); ranking
  status stays `unsupported`. "Why?" after a comparison offers "Explain <year>" ×2 and "What
  would allow a ranking?". `composition/comparison_guard.py` bans ranking words and match
  tallies in the view, the follow-ups, and the LLM narrative. **Promotion is still
  UNSUPPORTED.**
- **Timing labels name their periods** (NEXT-COMPARE-02b): "the reviewed timing indication
  for Moon Mahadasha with Venus Antardasha" / "… for Jupiter Mahadasha", from the window's
  calculated lords (`CareerClaim.period_lords`), in year answers, Why, comparisons, buttons.
- **"<Year> at a glance"** (NEXT-UX-SUMMARY, `application/year_glance.py`): a `glance`
  section after `direct` (rendered on top) with 3–4 bullets: periods; the natal indication (naming the 10th lord); one calculated
  10th-lord/10th-house link by a **fixed display precedence** (is the 10th lord > same sign as
  the 10th lord > occupies the 10th > aspects the 10th > aspects the 10th lord > SAME_HOUSE;
  display order only, never strength; see ASTROLOGY_METHOD); the timing status. With no
  matched timing rule the web view hides the Overview, which would only repeat the glance. Every bullet's ids are in its `SynthesisSentence` mapping.
- **The 10th lord is stated once** per year answer, in the glance (this replaces E1's
  naming in the direct line). The framing sentence, the natal section and the year answer's
  `dasha_context` no longer restate it. In comparisons it appears only in "Same in both
  years". The "Which Dasha applies?" reply still names it.
- **Web:** "Chart details" disclosure (collapsed) holds the Dasha chronology and lord
  relationships. Why, natal and Reviewed timing stay visible.
- **Signification corpus and "Period themes"** (NEXT-SIG-01; filled by NEXT-ADMIT-01):
  `knowledge/signification.py` (`signification-corpus-v1`), production corpus
  `knowledge/signification_part0b_v1.py` (`jyotish.signification.production@v2`: packet 0b
  terms plus the X18 record), and `application/period_themes.py` (template
  `period-themes-v1`, the reviewer-approved wording, unchanged). One sentence per **Mahadasha
  and Antardasha** lord of the year, in a section directly **after the glance**, then "This
  does not predict an event or an outcome." Rahu and Ketu use their occupied house only. The
  glance gains one "Period themes:" bullet listing each period's terms. See ASTROLOGY_METHOD.
- **Natal Career covers every placement** (NEXT-ADMIT-01): 10th lord in 1 (v.71) and 2/3/7
  (v.72) show their packet wording. 10th lord in 8 (v.76) is a calculated match only: the
  answer and glance say "a reviewed indication exists for this placement; its wording is
  withheld pending further review", and v.76's text and lifespan clause are never shown.
- Other domains (Wealth, Business, Education, Children, Travel, Friends, Spirituality) have
  natal contextual rules only.

**Active rules.** Natal production release `jyotish.production.cumulative@v11`
(`knowledge/career_part0_pack_v1.py`, 25 rules) contains, for Career, the 10th lord in 1,
2/3/7, 4/10, 5/11, 6/12, 8 or 9 (every resolvable placement has exactly one rule), and the
11th lord in 9/10. All of these are `CONTEXTUAL`, with no polarity. Timing release `jyotish.timing.production.career@v2` contains
v.87 (10th lord in 4th, MD) and v.140 (Moon MD / Venus AD, Venus own/exalted). v.89 (9th lord
in 10th) is a **candidate only**.

## Governance rules (non-negotiable)

- The LLM never calculates. All positions, Dasha, and houses come from deterministic code.
- Admitted rule text is quoted **byte-for-byte**. Plain-language rewording needs an approved
  `display_text` (X10).
- No scores, weighted sums, or "overall" verdicts. UNKNOWN is never FALSE. Absence of a match
  is not negative evidence.
- New doctrine (rules, polarity, domain mappings, Dasha meanings) goes in only through
  independent review plus a governance record. An AI preparer is never a reviewer.
- **AI pre-review (NEXT-PREREVIEW-01).** `.claude/agents/jyotish-prereview.md` drafts proposals for
  the human reviewer into `research/prereview/` only (path guard: `.claude/hooks/prereview-guard.py`).
  Its output is never a review, admission or user text. Every admission path rejects a review
  record whose reviewer or notes cite a pre-review or an AI agent
  (`knowledge/reviewer_guard.py`, `tests/test_reviewer_guard.py`).
- Store methodology, rule, synthesis, and prompt versions with every answer.
- CALC-02 is **NO-GO** for independent numerical calculation certification. Every rule
  carries that caveat. CALC-03 (`docs/validation/CALC-03-expert-check.md`) records an expert's
  general confirmation of chart and Dasha calculations (charts, quantities, reference software
  and differences: not recorded). It is not numerical certification.
- **Gate (stands; production was found in breach on 2026-11-23 and switched off the same
  day):** `LLM_ENABLED` must not be turned on until the ranking-word and evaluative-word
  guards pass against a real model on the full benchmark. Ranking: `composition/comparison_guard.py`.
  Evaluative: `composition/evaluative_guard.py` (favourable, auspicious, strong, weak, good,
  bad, lucky, unlucky, …). The evaluative guard rejects any LLM narrative containing such a
  word outside admitted rule text and approved signification terms; the answer then falls back
  to the deterministic composer. Template output is checked against every benchmark response
  in `tests/test_evaluative_guard.py`. Both guards are tested only with fake LLM transports so
  far; no real model has been run.

## Conventions

- Facts: `jyotish.d1.*`, `jyotish.timing.vimshottari.*`, `jyotish.dasha_linkage.v1.*`. Prose
  never contains ids; ids live in `SynthesisSentence` mappings.
- Seven classical sign rulers. Rahu/Ketu own no sign, and their aspects and dignity are
  unmodeled. Houses are counted from the D1 Lagna only.
- Commits: Conventional Commits (`feat(career):`, `docs(review):`…). Each task merges to `main`
  with `--no-ff` as `Merge NEXT-<TASK>: <summary>`. Docs and refactors are not mixed into
  feature commits.
- Benchmarks: `apps/api/tests/consultation_quality_benchmark.py`. Earlier result fixtures stay
  frozen, and each wording change adds a new `vN` (currently v17, eight bare-comparison journeys in `consultation_quality_bare_comparison_v1.json` with separate `bare_comparison_counts`, every v16 key unchanged; v16 was NEXT-TONE-01 wording only over v15 with every count identical; v15 was signification corpus v2 over v14 with only the recorded corpus version changed; v14 was Part 0 doctrine over v13: release v11, Period themes in 11 answers, 5 glance bullets, J21 UNSUPPORTED → PARTIALLY_SUPPORTED, 34/34 hard gates; v13 was empty signification infrastructure over v12 with identical counts plus separate `signification_counts`; v12 was glance bullet order over v11; v11 was presentation only over v10
  with identical `counts` and `comparison_counts`, plus separate `glance_counts`; v10 was
  wording only over v9; v9 kept v8 counts identical and added four separately counted
  comparison journeys in `consultation_quality_comparison_v1.json`).

## Branch, backup, and deploy procedure

1. Branch from `main`: `next-<task>`.
2. Before any squash, rebase, or history rewrite: `git branch backup/<task>-pre-squash`
   (existing: `backup/next-career-02-pre-squash`).
3. Gate: `cd apps/api && uv run pytest && uv run ruff check . && uv run mypy src`;
   `cd apps/web && npm test && npm run lint && npm run build`; `git diff --check`.
4. Before every commit, show `git diff --cached --name-only`. Stage paths explicitly
   (never `git add -A`).
5. `git checkout main && git merge --no-ff next-<task>`.
6. Push and deploy **only with explicit owner approval**. Render deploys the backend from
   `main`; Vercel deploys the frontend. **Vercel redeploys on every push, docs-only commits
   included. Render does not redeploy docs-only commits** (likely a build filter in the
   Render dashboard; there is no `render.yaml` in the repo; observed 2026-11-23 with
   `48dd0bb`).
7. Verify both:
   - **Render:** `curl -s https://jyotai-api-2x0m.onrender.com/health`. Its `commit` must
     equal the latest `main` commit that touched application code:
     `git log -1 --first-parent --format=%H origin/main -- apps/` (`--first-parent` returns
     the merge commit Render built, not the feature commit inside it). This is not
     necessarily `origin/main` HEAD.
   - **Vercel:** the production deployment's `githubCommitSha` (Vercel CLI) must equal
     `git rev-parse origin/main` (HEAD).
   If either shows `"unknown"` or an older SHA than these, that deploy is not live.

## Protected files

- **`jyotai-marriage-pack-research.txt`**: never open, read, or stage.
- **`google-adk/`**: untracked. Never stage it, and do not read it unless the owner asks.
- `research/next_08d/`: do not read unless the owner asks.
- BPHS PDF (repo root, SHA-256 `d333ebe1…6108`): the source artifact; do not modify.
- Never commit secrets or real birth data. Fixtures use clearly synthetic births.

## Test baselines (after NEXT-COMPARE-BARE; Render live is `01dbe20`)

- Backend: **988 passed** (`uv run pytest`, NEXT-COMPARE-BARE); 956 at `f96ff26`, 947 at NEXT-PREREVIEW-01, 882 at `b46667e`, 879 at `5d0f126`, 842 at `4ace4b7`.
- Frontend: **69 passed** (`npm test`, Vitest; NEXT-COMPARE-BARE adds the fresh-conversation domain button); 68 at `b423155`.

## Known gaps

- No ranking method (the side-by-side is factual only). Promotion is unsupported. No income
  timing rule.
- The Dasha interpretation corpus is empty. Linkage facts are calculated, with no meaning.
- No strength model. Debilitation is computed but not admitted. v.80 is open (X2).
- CALC-02 has no independent numerical reference. Swiss Ephemeris data-file setup and the
  Moshier fallback are still to validate. CALC-03's expert confirmation records no charts,
  quantities, reference or differences.
- `PROJECT_STATUS.md` and `docs/ROADMAP.md` checkboxes are stale. This file is current.

## Review packet

`research/next_dasha_01_review/review-packet.md`. Status: **Part 0 ADMITTED under a general
approval** (NEXT-ADMIT-01, 2026-11-23; records in `docs/admissions/`). **Part 1 and Part 2
remain REVIEW_REQUESTED; nothing in them is approved.**

**Part 0 approval, exactly as recorded:** reviewer "Pandit ji" (**full name pending**),
qualification Acharya, independence not recorded; verbal, relayed by Atul, 2026-11-23:
"All data points look good. The app is giving good calculation results. Mahadasha and
Antardasha are both good, including their calculations and results. Proceed." The reviewer
has seen the review packet PDF. Approved as proposed; no item-level readings, OCR issues or
translations individually addressed. Owner decisions in the same task: v.76 wording withheld;
राज्यापभ्रंश and all six [uncertain] terms excluded (the packet marks six, not five),
आकाशवृत्ति excluded; X18 uses the approved `period-themes-v1` wording unchanged. 0b शत्रु was
kept in corpus v1 and **removed in v2** (NEXT-SIG-02, 2026-11-23): its proposal was
conditional ("reviewer to confirm Career use") and the general approval did not confirm it
(`docs/admissions/jyotish.signification.part0b.admission.v2.md`).

**AI pre-review for Part 1 and the open items** (not an approval): `research/prereview/part1-prereview.md`,
`x2-addendum.md`, `images-addendum.md` (v.71, v.76 line 2 and P6 re-read from page images; page
images in `research/prereview/pages/` are git-ignored and never committed), and the reviewer's
checklist `pandit-ji-checklist.md` (PDF exported outside the repo).

**Open items:** (1) add the reviewer's full name to the five admission records and CALC-03
(by a superseding record); (2) v.76 user wording (withheld); (3) the packet's specific
questions that the general approval did not address (readings, मद = 7th, [uncertain] terms,
आकाशवृत्ति, a source verse for X18); (4) **6th-house शत्रु ("adversaries"): the reviewer to
confirm or reject its Career use**. The 6th house has no signification entry until then.

- **Order: Part 0, then Part 1. Part 2 is optional.**
- **Part 0 (first):** 0a, the 10th lord in houses 1, 2, 3, 7, 8 (bhāveśa-phala vv.71, 72,
  76, PDF p. 193; all five located), which would give every chart a natal Career rule;
  0b, the career-relevant significations of the 9 grahas (ch. 3 vv.1–4, ch. 12 v.18) and
  the 12 bhavas (ch. 12 vv.1–12), with a keep/strike column per term and uncertain terms
  marked for exclusion; X18, the lordship principle that gates "Period themes". No fixed
  bhāva-kāraka list was located in this edition. v.76 (10th lord in the 8th) is adverse
  and includes a lifespan clause; the preparer proposes withholding its wording.
- **Part 1:** P1–P6 (BPHS Dasha-phala vv.79, 83b, 85, 89), X1–X10 and X17.
- **Part 2 (appendix, optional): comparison and promotion.** X11 polarity per rule
  (favourable / adverse / contextual / conditional-mixed), X12 dimensions per rule, X14
  absence vs adverse, X15 *rājya* as promotion context. Each has an empty decision block.
- Not in the packet: X13 (conflict convention) stays in `docs/design/NEXT-COMPARE-01.md` §f;
  X16 (comparison unit) is settled by the product as the calendar year for now.

## Roadmap from here

1. **Done (NEXT-COMPARE-02):** NEXT-COMPARE-01 E1–E5 (10th lord in the no-match line,
   factual side-by-side comparison, guard tests, web view). **Done (NEXT-UX-SUMMARY,
   live at `8ece605`):** year glance, single 10th-lord statement,
   "Chart details" disclosure, benchmark v11.
2. **Done (NEXT-ADMIT-01, live at `4ace4b7`):** Part 0 (0a natal rules, 0b terms, X18 Period
   themes). **Next, on Part 1 review return:** admit approved principles (P1–P6),
   `display_text` (X10), and MD/AD scope (X1). Fill the DashaInterpretationSlot. Promote
   v.89 if P3 is approved.
3. **After X11–X14 and sign-off:** polarity and dimension schema (B1), then per-dimension
   `comparison-method-v1` (B2), then promotion context (B3).
4. **Later:** CALC-02 independent reference, strength model (v.80), more domains, marriage pack
   (research held separately).
