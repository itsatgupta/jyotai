# JyotAI handover

Last refreshed 2026-11-23. This file replaces the older status in `PROJECT_STATUS.md` (Tasks
01–14), which is kept only as history.

## Live state

| Item | Value |
| --- | --- |
| Repo | `itsatgupta/jyotai`, branch `main` |
| Live SHA | `0292eda` (NEXT-COMPARE-02b; verified on Render `/health` and Vercel). This docs-only commit redeploys the same code; rollback target `d5171b3`. |
| Backend | Render, `https://jyotai-api-2x0m.onrender.com`; `GET /health` → `{"status":"ok","commit":"<sha>"}` (from `RENDER_GIT_COMMIT`) |
| Frontend | Vercel (Vite/React, `apps/web`); `VITE_API_BASE_URL` set at build time |
| Method | Vedic, sidereal, **Lahiri**, Whole Sign from D1 Lagna, true nodes, **Vimshottari** (365.25-day year). Never change these silently. |
| LLM | Optional narrative layer only (`LLM_ENABLED`, default `false`). It gets a closed packet and is validated; failure falls back to the deterministic answer. |

## What answers can do now (Career year questions, e.g. "How is my career in 2027?")

- **Governed direct line.** With one matched timing rule: a framing sentence built from facts
  (period lord, 10th lordship, placement house), then the admitted text **verbatim** with its
  non-guarantee. With no match: the year's MD/AD periods, the reviewed natal indication by its
  plain label, then "No reviewed timing rule applies to <year>…".
- **Why section** (`career-synthesis-v1`): co-reference links SAME_PLANET / SAME_HOUSE /
  SAME_PERIOD only. It never combines, weighs, or ranks.
- **Dasha context** (`jyotish.dasha_linkage.v1`): per-lord linkage facts (ruled houses,
  placement, 10th lord?, occupies/aspects 10th, same sign as 10th lord, own/exaltation).
- **DashaInterpretationSlot**: present and review-gated. The Dasha corpus is **empty**.
- Plain-language **drill-down buttons** ("Why?", "Which Dasha applies?", "What does … mean?").
- **Comparison is a factual side-by-side, never a ranking** (NEXT-COMPARE-02,
  `comparison-view-v1`, `application/career_comparison.py`). "Which is better, 2027 or 2028?"
  returns: direct line ("I can't rank …") → what differs (opens with any Mahadasha change
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
- Other domains (Wealth, Business, Education, Children, Travel, Friends, Spirituality) have
  natal contextual rules only.

**Active rules.** Natal production release `jyotish.production.cumulative` contains, for
Career, the 10th lord in 4/10, 5/11, 6/12, or 9, and the 11th lord in 9/10. All of these are
`CONTEXTUAL`, with no polarity. Timing release `jyotish.timing.production.career@v2` contains
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
- Store methodology, rule, synthesis, and prompt versions with every answer.
- CALC-02 is **NO-GO** for independent calculation certification. Every rule carries that
  caveat.
- **Gate:** `LLM_ENABLED` must not be turned on until the ranking-word and evaluative-word
  guards pass against a real model on the full benchmark.

## Conventions

- Facts: `jyotish.d1.*`, `jyotish.timing.vimshottari.*`, `jyotish.dasha_linkage.v1.*`. Prose
  never contains ids; ids live in `SynthesisSentence` mappings.
- Seven classical sign rulers. Rahu/Ketu own no sign, and their aspects and dignity are
  unmodeled. Houses are counted from the D1 Lagna only.
- Commits: Conventional Commits (`feat(career):`, `docs(review):`…). Each task merges to `main`
  with `--no-ff` as `Merge NEXT-<TASK>: <summary>`. Docs and refactors are not mixed into
  feature commits.
- Benchmarks: `apps/api/tests/consultation_quality_benchmark.py`. Earlier result fixtures stay
  frozen, and each wording change adds a new `vN` (currently v12, glance bullet order over v11 with identical counts; v11 was presentation only over v10
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
   `main`; Vercel deploys the frontend.
7. Verify: `curl -s https://jyotai-api-2x0m.onrender.com/health`. Its `commit` must equal
   `git rev-parse origin/main`. If it shows `"unknown"` or an older SHA, the deploy is not live.

## Protected files

- **`jyotai-marriage-pack-research.txt`**: never open, read, or stage.
- **`google-adk/`**: untracked. Never stage it, and do not read it unless the owner asks.
- `research/next_08d/`: do not read unless the owner asks.
- BPHS PDF (repo root, SHA-256 `d333ebe1…6108`): the source artifact; do not modify.
- Never commit secrets or real birth data. Fixtures use clearly synthetic births.

## Test baselines (after NEXT-UX-SUMMARY, not yet deployed)

- Backend: **786 passed** (`uv run pytest`); 785 at `f78520a`, 768 at `0292eda`.
- Frontend: **67 passed** (`npm test`, Vitest); 66 at `f78520a` and `0292eda`.

## Known gaps

- No ranking method (the side-by-side is factual only). Promotion is unsupported. No income
  timing rule.
- The Dasha interpretation corpus is empty. Linkage facts are calculated, with no meaning.
- No strength model. Debilitation is computed but not admitted. v.80 is open (X2).
- CALC-02 has no independent numerical reference. Swiss Ephemeris data-file setup and the
  Moshier fallback are still to validate.
- `PROJECT_STATUS.md` and `docs/ROADMAP.md` checkboxes are stale. This file is current.

## Review packet

`research/next_dasha_01_review/review-packet.md`. Status: **REVIEW_REQUESTED**, awaiting an
external Jyotish/Sanskrit reviewer. Nothing in it is approved.

- **Part 1 (priority):** P1–P6 (BPHS Dasha-phala vv.79, 83b, 85, 89) and X1–X10.
- **Part 2 (appendix, lower priority): comparison and promotion.** X11 polarity per rule
  (favourable / adverse / contextual / conditional-mixed), X12 dimensions per rule, X14
  absence vs adverse, X15 *rājya* as promotion context. Each has an empty decision block.
- Not in the packet: X13 (conflict convention) stays in `docs/design/NEXT-COMPARE-01.md` §f;
  X16 (comparison unit) is settled by the product as the calendar year for now.

## Roadmap from here

1. **Done (NEXT-COMPARE-02):** NEXT-COMPARE-01 E1–E5 (10th lord in the no-match line,
   factual side-by-side comparison, guard tests, web view). **Done (NEXT-UX-SUMMARY,
   merged locally, push pending approval):** year glance, single 10th-lord statement,
   "Chart details" disclosure, benchmark v11.
2. **On review return:** record decisions on governance records, then admit approved
   principles (P1–P6), `display_text` (X10), and MD/AD scope (X1). Fill the
   DashaInterpretationSlot. Promote v.89 if P3 is approved.
3. **After X11–X14 and sign-off:** polarity and dimension schema (B1), then per-dimension
   `comparison-method-v1` (B2), then promotion context (B3).
4. **Later:** CALC-02 independent reference, strength model (v.80), more domains, marriage pack
   (research held separately).
