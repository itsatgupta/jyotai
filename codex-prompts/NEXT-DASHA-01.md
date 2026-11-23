# NEXT-DASHA-01 — Dasha-lord chart linkage facts and a review-gated interpretation slot

**Recommended setup**
- Session: **fresh** Codex session (do not reuse a long implementation context).
- Model: the strongest Codex coding/reasoning model your Codex UI actually offers.
- Reasoning effort: **High**.
- Git: local commits only. **No push, no deploy.**

---

## Paste-ready prompt

```text
You are working in the Jyotish AI repository (apps/api = Python/FastAPI, apps/web = React/TS).
Read AGENTS.md first and follow it. Task: NEXT-DASHA-01.

## Precondition — check before writing any code

This task builds on CareerAnswerPlan (apps/api/src/astrologer/application/answer_plan.py,
CareerAnswerPlan / PlannedDashaSegment / ConsultationSection in composition/models.py),
merged to local main at 9effec8. Verify all of the following, else STOP and report:
  - `answer_plan.py` exists and `build_career_answer_plan` takes a required `dasha_engine`;
  - no production code under apps/api/src constructs `VimshottariDashaEngine()` outside
    constructor defaults (context.py, timing.py);
  - tests/test_dasha_engine_injection.py exists and passes.
Linkage facts must obtain Dasha periods only through the injected engine
(`DeterministicAnalysisService.dasha_engine`), never a new instance.

## Protected files — never open, modify, stage, commit or delete

- jyotai-marriage-pack-research.txt
- google-adk/ (unrelated local experiment containing .env files; never stage)

## Goal

When a consultation answer shows operating Vimshottari periods (Mahadasha / Antardasha),
attach DETERMINISTIC chart-linkage facts for each operating Dasha lord, so the answer is
personal ("Saturn, your Antardasha lord, rules your 10th and 11th houses and occupies your
4th") without introducing any interpretation. Also add an empty, review-gated slot where an
admitted Dasha interpretation rule can attach later.

This task adds NO astrological doctrine. It must not label anything favourable, unfavourable,
strong, weak, good, bad, auspicious, malefic, benefic, difficult, or challenging.

## Scope

### 1. Pure linkage-fact module

Create `apps/api/src/astrologer/astrology/dasha_linkage.py` (pure functions, Pydantic models,
type hints, no I/O, no rules, no LLM). Input: the D1 `Chart`, its `DerivedFactBundle`
(astrology/derived_facts.py), and one operating MD/AD pair. Output: a frozen
`DashaLordLinkage` per lord, with a methodology/version id such as
`jyotish.dasha_linkage.v1`.

ALL house counting is from the D1 Lagna (Whole Sign) ONLY. No Moon, Sun, Arudha, Dasha-lord
or any other reference point. Record this in the methodology model as an explicit field
(e.g. `reference_point: Literal["d1_lagna"]`) and state it in user-facing text (see §3).

For each operating lord, emit facts. Each has its own stable fact_id, and the source
derived-fact ids it was computed from:
- `ruled_houses`: houses whose sign the lord rules (classical SIGN_RULERS; reuse
  `jyotish.d1.house.N.lord`). Rahu/Ketu: rules no house under the current convention —
  emit an empty tuple with an explicit `lordship_convention` note, not "no lordship".
- `placement_house`: house occupied (reuse `jyotish.d1.planet.X.placement_house`).
- `sign` and, for the seven classical planets, the existing `own_sign` / `exaltation_sign`
  booleans only (these are the admitted dignity facts; do NOT surface `debilitation_sign`,
  which is computed but not source-admitted — see docs/DIGNITY_SOURCE_ADMISSION.md).
- `is_tenth_lord`, `occupies_tenth`.
- `aspects_tenth_house`, `aspects_tenth_lord`: from the existing seven-planet aspect facts.
  For Rahu and Ketu these are **UNKNOWN** (the seven-planet aspect convention has
  `rahu_ketu_aspects = "unmodeled"`). Never emit False / "no aspect" for Rahu or Ketu.
  Use the project's existing three-valued convention (UNKNOWN is not FALSE).
- `same_sign_as_tenth_lord`: from `jyotish.d1.same_sign.*`. If the lord IS the tenth lord,
  emit not-applicable, not True/False.
- `ad_house_from_md`: the house number of the AD lord's sign counted from the MD lord's
  sign, inclusive (1–12). A plain integer. **No relationship labels** — no "6/8", "2/12",
  "shadashtaka", "kendra", "trikona", "dusthana", "friendly", "inimical", etc. — anywhere
  in the model, fact ids, prose, or UI. (This is the only fact not counted from Lagna; it
  is a sign-distance number, and the prose must describe it literally, e.g. "Saturn is in
  the 9th sign counted from Rahu's sign.")

### 2. Review-gated interpretation slot

- Add a `DashaInterpretationSlot` to the answer plan: holds zero or more admitted Dasha
  interpretation claims, each with rule_id, rule_version, source locator, permitted_wording.
- It can ONLY be filled by rules admitted through the existing admission/production-release
  machinery (knowledge/admission.py, timing_rules/registry.py patterns). Ship the production
  Dasha-interpretation corpus EMPTY. Never fill it from LLM output.
- Store rule ids + versions with the generated answer (AGENTS.md rule 6).

### 3. Dasha context section

Add a `ConsultationSection(kind="dasha_context")` to calendar-year Career answers (and to the
existing "Which Dasha applies?" follow-up path in application/consultation.py), after the
calculated chronology section.

It contains exactly:
- Fact sentences. EVERY sentence must be generated from one or more linkage fact ids, and
  the section must carry the mapping sentence → fact_ids (e.g. a tuple of
  `(text, fact_ids)` pairs; the rendered text is their join plus the framing line).
- ONE fixed framing sentence per section, verbatim, defined once as a constant:
  "These are calculated chart relationships, counted from your D1 Lagna; a reviewed Career
  interpretation of this Dasha is not yet available."
  When the interpretation slot is non-empty, the framing sentence is replaced by a fixed
  alternative constant that names that the following interpretation is reviewed, followed by
  the admitted permitted_wording verbatim with its rule id.
- When interpretation is absent, the text must never imply the Dasha has no significance.

### 4. Frontend

Minimal: render the new section in the existing consultation layout
(apps/web/src/components/QuestionAnalysis.tsx) using the existing section styles; put the
fact-id mapping inside the existing evidence disclosure. Update typed contracts
(apps/web/src/lib/contracts.ts), strict TS, no `any`. No visual redesign.

## Out of scope

New doctrine; D9/D10 interpretation; transits; year comparison or ranking; Moon/other
reference points; relationship labels; changes to Dasha calculation; changing
Lahiri / Whole Sign / Vimshottari / true-node settings; unrelated refactors.

## Acceptance criteria

1. Reference 2027 case (existing synthetic profile in tests/test_career_consultation.py,
   question "How will my career be in 2027?", as_of 2026-01-01 Asia/Kolkata). The calculated
   2027 periods for that profile are Jupiter MD / Moon AD (local 2027-01-01 → 2027-11-16) and
   Jupiter MD / Mars AD (2027-11-16 → 2028-01-01, end exclusive) — verify this from the engine
   rather than trusting this prompt. The answer shows each operating lord's ruled houses,
   placement, tenth-house relationships and `ad_house_from_md`; every fact has a fact id
   traceable to D1 derived facts. Expected values in the test must be asserted from derived
   facts computed in-test, not hand-typed from memory. Also add one Rahu-MD case (any
   synthetic profile/as_of whose MD is Rahu) to exercise the UNKNOWN aspect path end-to-end.
   Do not use any real person's birth data.
2. Unit tests in tests/test_dasha_linkage.py cover all nine Dasha lords, including:
   Rahu/Ketu ruled_houses empty with convention note; Rahu/Ketu aspect facts UNKNOWN (and a
   test asserting they are never False); tenth lord → same_sign_as_tenth_lord not-applicable;
   `ad_house_from_md` for MD=AD (1), adjacent signs, and wrap-around (e.g. Pisces→Aries = 2).
3. A test asserts the methodology reference point is `d1_lagna` and that the framing line
   (which states the Lagna reference) is present.
4. With the interpretation corpus empty: framing sentence present exactly once; slot empty;
   no "no significance"-type wording.
5. A fixture Dasha rule admitted through the admission path fills the slot and its rule id +
   version are stored on the answer; the same rule NOT admitted does not fill it.
6. Structural test: the dasha_context section consists ONLY of (a) sentences each backed by
   ≥1 fact id that exists in the linkage output, plus (b) the framing constant. Any other
   sentence fails the test.
7. Blocklist test over the section text and the linkage models' string fields, at least:
   favourable/favorable, unfavourable/unfavorable, auspicious, inauspicious, strong, weak,
   good, bad, malefic, benefic, difficult, challenging, lucky, promising, 6/8, 2/12,
   shadashtaka, dusthana, kendra, trikona, friendly, inimical, enemy.
8. Consultation-quality benchmark (tests/consultation_quality_benchmark.py) re-run; record
   this as descriptive coverage, NOT new astrological coverage.
9. Gates all pass: `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check` on
   every file you touched, `uv run mypy src` (apps/api); `npm test`, `npm run lint`,
   `npm run build` (apps/web); `git diff --check`.
10. Docs: apps/api/README.md and docs/ASTROLOGY_METHOD.md describe the linkage facts, the
    Lagna-only reference, and the UNKNOWN Rahu/Ketu aspect convention.

## Git requirements

- Work on a new local branch `next-dasha-01` from the current branch.
- Before committing, show `git diff --cached --name-only` and confirm neither protected
  path is staged.
- One focused commit (or a small series). No push, no deploy, no merge to main.
- Final report: files changed, test counts, gate outputs, anything left UNKNOWN, and any
  place where you had to make a convention choice.
```
