# NEXT-COMPARE-01: Comparison framework (design only)

Status: **DESIGN, not implemented.** Base: `main` @ `bd96d1c`. No code, rule, or review-packet
change is made by this document.

## Problem

Users ask "Which is better, 2027 or 2028?" Today:

- A fresh comparison question routes to `CareerQuestionFocus.COMPARISON`
  (`questions/router.py`). The direct line says no comparison method is active and repeats the
  static natal context (`application/career_claims.py`).
- A comparison follow-up runs `ConsultationService._compare` (`application/consultation.py`).
  It lists each year's matched timing windows (or the timing status) with status
  `unsupported`. It does **not** show MD/AD lords for years with no match, linkage facts, or
  co-references.
- Promotion questions return "No approved Career rule establishes whether or when a promotion
  will occur."

Every admitted Career rule is `EvidenceDirection.CONTEXTUAL`. No rule has approved polarity
(favourable/adverse) or a dimension tag. `career-synthesis-v1` lists
"claim-agreement-or-conflict" as out of scope for the same reason. Ranking is impossible with
the current corpus. A **factual side-by-side** is possible now.

## a) Comparison dimensions

"Natal" rules are identical for both years, so they never tell two years apart. Only
Dasha-conditioned (timing) rules can vary by year.

| Dimension | What users mean | Admitted rules that speak to it today | Missing methodology |
| --- | --- | --- | --- |
| Career opportunity | openings, progress at work | Timing: v.87 (10th lord in 4th, MD, *rājya-pradāyinī*); v.140 (Moon MD / Venus AD, Venus own/exalted, *rājya-lābha*). Both are "broad career/status context", with no direction. Natal Career rules (10th lord in 4/10, 5/11, 6/12, 9; 11th lord in 9/10) are year-invariant. | Polarity per rule; a reviewed mapping from *rājya* to "opportunity" (X5, X6); P1, P3 pending review |
| Stability | continuity, job security | None | No admitted source. Would need reviewed rules on Dasha continuity or adverse lords (v.80, vv.90–95 are not admitted) |
| Income | salary, earnings | Natal Wealth rules only (11th lord in 1, 2/5, 9/10; 5th lord in 11): year-invariant, Wealth domain. No timing rule. | X8 (P1 *vitta*, P2 *lābha*, P4 *sampat*: Career vs Income); a timing rule for income |
| Recognition | status, authority, visibility | Same two timing rules (*rājya*). Wording forbids promotion, office, or authority claims. | X5 rendering of *rājya*; dimension metadata; P3 promotion to production |
| Change | job switch, relocation, new role | None | No source identified; nothing in the packet covers change |
| Business potential | own venture | Natal `bphs.d1.house_lord.6.in_9.business.v1` only (year-invariant) | Any Business timing rule; a Career/Business domain decision for timing claims |
| Risk | setbacks, loss | None admitted. The natal 10th-lord-in-6/12 rule is contextual, **not** adverse. | Polarity metadata; v.80 handling (X2); admission of adverse clauses (vv.90–95) with their own review |

Conclusion: today no dimension has a rule that both varies by year and has an approved
direction. So no dimension can be ranked.

## b) What may be compared today, without ranking

A **side-by-side of calculated facts and reviewed matches**, one column per year (or period).
Every row is computed independently per year and is never combined across years.

| Row | Source | Already computed? |
| --- | --- | --- |
| MD/AD periods overlapping the year, with local dates | Vimshottari-v1 segments (`answer_plan`) | Yes |
| Per-lord linkage facts (10th lord?, placement house, ruled houses, occupies/aspects 10th, same sign as 10th lord, own/exaltation sign) | `jyotish.dasha_linkage.v1` | Yes |
| Reviewed timing indications that apply, quoted verbatim with non-guarantee | Timing release v2 | Yes |
| Reviewed natal indications (shown **once**, marked "same for both years") | Production corpus | Yes |
| Co-reference links (SAME_PLANET / SAME_HOUSE / SAME_PERIOD) | `career-synthesis-v1` | Yes |
| DashaInterpretationSlot | Dasha corpus (empty) | Yes, renders "none admitted" |

Required framing (fixed text, not LLM-generated):

> "This is a factual side-by-side, not a verdict. JyotishAI has no reviewed method for
> deciding which period is better, so it shows what was calculated and which reviewed
> indications apply in each, without ranking them."

Hard rules for the side-by-side:

- No "more", "stronger", "better", or counts presented as a measure. ("2028 has 2 matches,
  2027 has 0" must not appear as a comparison. Matches are listed, not tallied.)
- An empty column says "No reviewed timing indication applies." It never says "weaker" or
  "less favourable". UNKNOWN stays UNKNOWN.
- Status stays `unsupported` for the ranking part. The response carries a
  `comparison_mode: "SIDE_BY_SIDE"` marker (proposed) so the UI and benchmark can tell it
  apart from a ranked answer.
- Methodology, rule, synthesis, and prompt versions are stored per column, as for single-year
  answers.

## c) Preconditions for any ranking

Ranking stays disabled until **all** of the following hold. Each one is checked in code, not
by convention.

1. **Polarity metadata.** Every rule that may contribute carries a reviewer-approved
   `polarity` (`FAVOURABLE` / `ADVERSE` / `CONTEXTUAL`) on its governance record. A
   `CONTEXTUAL` rule never contributes to a ranking.
2. **Dimension metadata.** Every contributing rule carries reviewer-approved `dimensions` from
   the table in (a). A ranking is only ever per dimension, never "overall".
3. **Approved conflict-resolution convention.** A reviewed, versioned convention says what
   happens when the two years have opposing or incomparable indications (for example: "report
   both, no ranking"; or a cited classical precedence such as MD over AD). It is
   source-backed and stored as `comparison-method-vN`.
4. **Expert sign-off.** An independent Jyotish reviewer signs off on the method and on worked
   test cases, with a governance record (`research/next_dasha_01_review/governance-record-template.md`).
5. **CALC-02 caveat** is carried into every ranked answer while independent calculation
   certification is NO-GO.

**Forbidden, now and later:** numeric scores, point systems, weighted sums, averaging, counting
matches as strength, LLM-judged preference, and any "overall" verdict across dimensions. If the
approved convention cannot decide, the answer is the side-by-side.

## d) Response template: "Which is better, 2027 or 2028?"

### Now (side-by-side, no ranking)

```
Direct line:
  I can't tell you which year is better: JyotishAI has no reviewed method for ranking
  periods. Here is what was calculated for each year, side by side.

2027                                         | 2028
---------------------------------------------|---------------------------------------------
Periods: <MD> Mahadasha with <AD> Antardasha | Periods: <MD> Mahadasha with <AD>
  (<local dates>)                            |   Antardasha (<local dates>)
Period lords: <Planet> rules your <N>th and  | <same facts for 2028's lords>
  <M>th houses and sits in your <K>th house; |
  <is / is not> your 10th lord               |
Reviewed timing indication: <verbatim text   | Reviewed timing indication: none applies.
  + non-guarantee> OR "none applies"         |
Links: <co-reference sentences>              | Links: <co-reference sentences>

Same for both years (natal): Your chart matches <plain labels of reviewed natal indications>.

Why no ranking: The reviewed rules describe context, not whether a period is better or
worse. None of them is approved to compare periods, so listing them side by side is as far
as the evidence goes. None of this establishes a specific event, promotion, income change,
or date.

Follow-up buttons: "What does <rule label> mean?" · "Which Dasha applies in 2027?" ·
"Which Dasha applies in 2028?"
```

### Later (only once all of (c) is met)

```
Direct line (per dimension, never overall):
  On <dimension>, the reviewed method favours <year>: <rule label> applies in <year>
  (<polarity>), and nothing reviewed applies to <dimension> in <other year>.
  [Or: "On <dimension>, the reviewed indications point in different directions; the
  approved convention <name> does not rank them."]
Per-dimension table: dimension | 2027 indications | 2028 indications | method result
                     (FAVOURS 2027 / FAVOURS 2028 / NOT RANKED)
Side-by-side facts: as in "Now".
Provenance: comparison-method-vN, reviewer record id, rule versions, CALC-02 caveat.
Limits: no event, promotion, income amount, or date is established.
```

## e) Implementation backlog

### ENGINEERING-NOW (no new doctrine)

| # | Item | Size | Depends on |
| --- | --- | --- | --- |
| E1 | **No-match direct line names the 10th lord's planet and house** from calculated facts (`jyotish.d1.house.10.lord`, `jyotish.d1.house_lord.10.placement_house`), e.g. "Your 10th lord is Saturn, in your 4th house." Fact ids go in the `SynthesisSentence`. No meaning is attached. Benchmark v9. | S | none |
| E2 | `CareerYearComparison` model: two independently built per-year columns (periods, linkage facts, timing matches, co-references, slot) plus a shared natal block. Versioned `comparison-view-v1`, no ranking fields. | M | none |
| E3 | Route fresh COMPARISON questions and the `_compare` follow-up through E2. Fixed "not a verdict" framing. Status `unsupported` for ranking, plus `comparison_mode: SIDE_BY_SIDE`. | M | E2 |
| E4 | Guard tests: no comparative words or match counts in comparison prose; the LLM composer validator rejects ranking language in comparison answers. | S | E3 |
| E5 | Web: two-column side-by-side view (stacked on mobile), with drill-down buttons per year. | M | E3 |

### BLOCKED-ON-REVIEW

| # | Item | Size | Depends on |
| --- | --- | --- | --- |
| B1 | Add `polarity` and `dimensions` fields to the governance record and rule envelope (default `CONTEXTUAL`, empty). Schema only, with all values reviewer-supplied. | S | X11, X12 |
| B2 | `comparison-method-v1`: per-dimension ranking under the approved conflict convention, with a stored method version, refusal paths, and worked test cases from the reviewer. | L | B1, X13, X14, reviewer sign-off |
| B3 | Promotion questions: answer with reviewed *rājya* timing context, never "promotion will occur". | M | X5, X6, X15 |

## f) New reviewer questions (proposed; not added to the packet)

| ID | Question |
| --- | --- |
| X11 | **Polarity per rule.** For v.87, v.140, and each of P1–P6, plus the admitted natal Career rules: is the stated result `FAVOURABLE`, `ADVERSE`, or `CONTEXTUAL` (no direction)? |
| X12 | **Dimension tags per rule.** Which of career opportunity / stability / income / recognition / change / business potential / risk does each rule's result speak to? (This overlaps X6/X8; X12 is the comparison-facing form.) |
| X13 | **Conflict convention.** When two periods carry different indications, is there a classical basis for preferring one (for example MD over AD, or a stronger lord via v.80)? Or must the answer always be "not ranked"? |
| X14 | **Absence vs adverse.** May "a reviewed favourable indication applies in year A and none in year B" ever support "A is better on this dimension"? Or does absence of a match carry no comparative weight? |
| X15 | **Promotion mapping.** May *rājya-pradāyinī* / *rājya-lābha* ever be cited for a promotion question as context, under fixed non-guarantee wording? |
| X16 | **Comparison unit.** Should comparisons be by calendar year (which splits Dasha periods) or by Dasha period (MD/AD) as the classical unit? |
