# Astrology Methodology

## Timing Foundation v1

Vimshottari timing facts retain the existing deterministic `vimshottari-v1` convention: the D1,
sidereal Lahiri Moon determines the initial lord and remaining MD; a dasha year is 365.25 days;
durations are calculated at microsecond resolution with half-even fractional-microsecond rounding.
MD and AD intervals are UTC-normalized, ordered, contiguous, and half-open: `[start, end)`. Thus
the instant equal to an end boundary belongs to the following period.

The foundation exposes complete canonical MD intervals and each parent MD's nine complete AD
intervals, selected by an explicit bounded analysis horizon. It is factual only. It establishes no
event, outcome, activation, positivity, or date prediction. Pratyantardasha is deliberately
deferred; transit facts remain separate and are not timing doctrine.

## Career Timing Pack v2 production methodology

The active timing release is `jyotish.timing.production.career@v2`, with exactly two independently
governed rules: the retained v1 D1 tenth-lord/fourth-house Mahadasha rule (`BROAD_PERIOD`) and the
reviewed v2 Moon Mahadasha/Venus Antardasha, D1 Venus own-or-exaltation rule (`SUB_PERIOD`). The v2
source interval is the complete qualifying Moon/Venus AD and its effective window is only its
`[start,end)` horizon intersection. Production v1 and candidate v2 are immutable historical records.
There is no ranking, transit or Pratyantardasha refinement, exact-event prediction, or LLM timing.

The active governed production timing release is `jyotish.timing.production.career@v2`, containing
exactly the retained v1 rule and the reviewed v2 Moon/Venus own-or-exaltation rule. It is selected
through a dedicated active timing-release pointer, separate from the static release. Production v1
and candidate v2 remain immutable. The v1 reviewed provenance is *Brihat
Parāśara Horā Śāstra*, *अथ दशाफलाध्यायः / Dasha-phala*, verse 87; printed p. 439, local artifact PDF
p. 437, with adjacent Hindi continuation PDF p. 438. The reviewed translation says: “The Dasha of
the tenth-house lord situated in the fourth house is described as giving rājya-related results.”

Its bounded interpretation is broad Career context only: if the deterministic D1 tenth-house lord
is in house four, only a matching Vimshottari Mahadasha qualifies. `rājya` is not formalized as a
claim of employment, promotion, office, authority, income, government work, or a specific event.
The v2 rule is limited to Moon Mahadasha/Venus Antardasha with natal D1 Venus in its own or exaltation
sign; its complete AD and requested-horizon intersection are `SUB_PERIOD`. There is no Pratyantardasha
or transit refinement, no exact-date prediction, ranking, or LLM date selection. The retained v1 rule
remains `BROAD_PERIOD`, with per-window provenance and precision.

## Initial configuration

The MVP starts with:

- Vedic/Jyotish
- Sidereal zodiac
- Lahiri ayanamsa
- Vimshottari Dasha

### Optional narrative explanation boundary

The Senior Astrologer Composer is a prose-only layer over already resolved governed evidence. It does
not calculate, infer, or add Jyotish doctrine, and it cannot interpret Dasha or Transits. Its output is
accepted only after deterministic structured-output and unsupported-claim validation; otherwise the
deterministic detailed answer is used. `LLM_ENABLED=false` remains a complete production-safe mode.

## Required calculation outputs

### Birth chart

- Ascendant
- Sun
- Moon
- Mars
- Mercury
- Jupiter
- Venus
- Saturn
- Rahu
- Ketu

### Derived values

- longitude
- sign
- degree
- house
- nakshatra
- pada
- retrograde
- combustion where supported
- dignity where supported
- aspects

### Task 09A derived structural facts

`jyotish-derived-facts-v1` consumes an existing canonical D1/Rashi chart and
does not calculate astronomical positions. It applies to D1 only, not D2, D9,
D10, or other Vargas. It provides structural Whole Sign rulership/lordship,
house classifications, seven-planet Graha Drishti, same-sign occupancy, and
sign-level own/exaltation/debilitation facts. It has no interpretive, predictive,
strength-scoring, Dasha, Transit, evidence, or LLM behavior.

Rahu and Ketu have no modeled ownership, dignity, or Graha Drishti in this
version. Same-sign occupancy is a symmetric structural relation, not a
conjunction-strength doctrine. Angular separation and conjunction orbs are
deferred.

### Classical dignity foundation v1

`jyotish.timing.dignity@v1` is a timing-local factual projection reserved for
future separately governed timing rules. It projects only the existing D1
sign-level facts `own_sign` and `exaltation_sign` for Sun through Saturn. An
own-sign fact is true when the planet is the approved Whole Sign ruler of its
occupied sign; an exaltation fact is true when the occupied sign matches the
approved planet-to-sign table in `task09a-v1-approved-conventions`. Missing or
non-boolean input is `UNKNOWN`, never false.

The local convention register has status `REVIEWED_EXACT_LOCATOR`. The
immutable locator record is
[`DIGNITY_SOURCE_ADMISSION.md`](DIGNITY_SOURCE_ADMISSION.md): it records the
selected-edition BPHS source, exact verses/pages, Sanskrit excerpts, the
reviewed Hindi rendering, and the computational mappings. This is a scoped
admission of factual sign ownership and exaltation only, not a claim that all
Jyotish traditions are identical. Mūlatrikoṇa remains held: this task does not
admit its degree ranges. These facts state neither strength nor good or bad
results, and they establish no timing, event, or interpretation. A future
timing rule may consume them only after separate source review and admission.
They are not supplied to the LLM answer path.

### Task 09B-v1 knowledge governance

Task 09B-v1 adds no astrology doctrine, calculation, prediction, or admitted
interpretive rule. It governs how future reviewed rules may cite an identified
source passage, reviewed translation where necessary, and a distinct
human-reviewed interpretation. Model memory, unsourced repetition, and
astrology websites/blogs treated merely as commonly repeated authority are not
admissible primary sources. Classical or otherwise identified primary material
is preferred; secondary material may only be explicitly identified
corroboration or explanation. Ambiguity defaults to non-admission unless a
human review explicitly scopes it. Conflicting authorities remain separate
claims/rules and traditions are never silently merged.

The historical initial production corpus remains empty and is retained as an
immutable release. Task 09C2 admits exactly one reviewed D1 structural rule:
`bphs.d1.house_lord.11.in_9_or_10.v1`. It records a reviewed textual
association as contextual natal evidence only; it does not make a prediction,
score evidence, or add timing. D9/D10/Varga interpretation, Dasha and Transit
interpretation, yogas, cancellation, scoring, and probability remain out of
scope.

### Career Pack v1

The cumulative production release `jyotish.production.cumulative@v2` contains
five rules: the unchanged historical general Rule #1 plus four Career Pack v1
rules for D1 tenth-house-lord placement in 4/10, 5/11, 6/12, and 9. The Career
rules cite `bphs.selected-edition@v1`, भावेशफलाध्यायः / अथ कर्मेशभावफलम्,
verses 73–75 (PDF p. 193) and verse 77 (PDF p. 194, running-page label about
196). Their records use the adjacent Hindi rendering as a basis and are an
internal project-owner review, not Sanskrit or Jyotish expert certification.

They are static, contextual D1/Rashi natal evidence only: they retain each
passage's compound outcome scope, make no guarantee or modern career
prediction, and provide no timing. The explicit v2 fact contract permits only
`jyotish.d1.house_lord.10.placement_house` and
`jyotish.d1.house_lord.11.placement_house`. Career candidates 01 and 05 remain
on HOLD and are absent because their compound passages include health/longevity
outcomes; no parts are cherry-picked. No D9/D10 interpretation, LLM,
aggregation, polarity, scoring, or timing capability is added.

### Wealth Pack v1

The cumulative production release `jyotish.production.cumulative@v4` retains all
five v3 rules and adds exactly four approved Wealth Pack v1 rules: D1
eleventh-house lord in 1; in 2 or 5; in 9 or 10; and D1 fifth-house lord in
11. It is D1/Rashi, static, contextual natal evidence only, with no timing,
health, scoring, or prediction. Wealth candidates 5–7 remain on HOLD and
candidates 8–11 are REJECTED; none are admitted.

The 11th-lord-in-9-or-10 Wealth rule shares its reviewed BPHS source passage
with the immutable historical General rule, but has an independent Wealth rule
and reviewed-interpretation identity. Exact-domain selection keeps the two
separate. The release is cumulative and does not alter historical releases.

### Education Pack v1

The cumulative production release `jyotish.production.cumulative@v5` retains the
previous nine rules and adds exactly three approved Education Pack v1 rules:
D1 fourth-house lord in 1 or 7; D1 fifth-house lord in 11; and D1 eleventh-house
lord in 11. The immutable FactContract is now
`jyotish.d1.structural.rule1@v4`, adding only
`jyotish.d1.house_lord.4.placement_house`; the existing fifth- and
eleventh-lord placement facts are unchanged. The active release contains 12
explicitly admitted rules.

Education Pack v1 is D1/Rashi, static, contextual natal evidence only. It adds
no timing, health, scoring, prediction, Dasha, transit, or divisional-chart
interpretation. Candidates 4 and 6 are HOLD; candidates 5, 7, and 8 are
REJECTED and are absent. The fifth-lord-in-eleventh Education rule shares the
reviewed Sutesha-phala v.42 source passage (PDF p. 188) with the Wealth rule,
but has a distinct Education rule and reviewed-interpretation identity;
exact-domain selection keeps each rule out of the other domain.

### Business Pack v1

The cumulative production release `jyotish.production.cumulative@v6` retains
the prior 12 rules and adds exactly one approved Business Pack v1 rule: D1
sixth-house lord in 9. The immutable FactContract is now
`jyotish.d1.structural.rule1@v5`, adding only
`jyotish.d1.house_lord.6.placement_house`; its deterministic D1 derivation and
UNKNOWN semantics are unchanged. The active release contains 13 explicitly
admitted rules.

Business Pack v1 is D1/Rashi, static, contextual natal evidence only. It adds
no timing, health, scoring, success, profit, or revenue prediction. Candidate
2 is HOLD; candidates 3, 4, and 5 are REJECTED and absent. The approved source
is Bhavesha-phala verse 49 (PDF p. 190); the reviewed rendering is limited to
commercial activity and trade context, without inferring livelihood,
self-employment, ownership, industry, or certainty.

### Children / Progeny Pack v1

The cumulative production release `jyotish.production.cumulative@v7` retains
the prior 13 rules and adds exactly three approved Children / Progeny Pack v1
rules: D1 fifth-house lord in 11; eleventh-house lord in 2 or 5; and
tenth-house lord in 5 or 11. The active release contains 16 explicitly
admitted rules. The FactContract remains `jyotish.d1.structural.rule1@v5`:
all three existing deterministic house-lord placement facts were already
admitted, so its vocabulary and UNKNOWN semantics are unchanged.

Children Pack v1 is D1/Rashi, static, contextual natal evidence only. It makes
no fertility, exact child-count, gender, health, loss, reproductive, timing,
scoring, or prediction claim. Candidates 4 (fifth lord in 9 or 10) and 5
(second lord in 5) remain HOLD. Passages concerning child loss/death, disease,
infertility, hostility, adoption/purchased-child claims, and other sensitive
reproductive content are excluded. The fifth-lord-in-eleventh source is shared
with distinct Wealth and Education rules; the eleventh-lord-in-2-or-5 source is
shared with a distinct Wealth rule; and the tenth-lord-in-5-or-11 source is
shared with a distinct Career rule. Each Children rule has its own immutable
reviewed-interpretation identity, and exact-domain selection keeps all
cross-domain rules separate.

### Spirituality / Dharma Pack v1

The cumulative production release `jyotish.production.cumulative@v8` retains
the previous 16 rules and adds exactly four approved Spirituality / Dharma Pack
v1 rules: D1 tenth-house lord in 4 or 10, tenth-house lord in 9, eleventh-house
lord in 2 or 5, and eleventh-house lord in 9 or 10. The active release contains
20 explicitly admitted rules. The FactContract remains
`jyotish.d1.structural.rule1@v5`; all required D1 house-lord placement facts
were already admitted, so its vocabulary and UNKNOWN semantics are unchanged.

The pack is D1/Rashi, static, contextual natal evidence only. It makes no
religious-identity claim, moral ranking, moksha or supernatural guarantee,
timing, scoring, or prediction claim. Candidates 1, 6, 8, and 9 are HOLD;
candidates 7 and 10 are REJECTED and absent. The tenth-lord-in-4-or-10 and
tenth-lord-in-9 passages share provenance with Career; eleventh-lord-in-2-or-5
shares provenance with Wealth and Children; and eleventh-lord-in-9-or-10 shares
provenance with General and Wealth. Every Spirituality rule and reviewed
interpretation has a distinct immutable identity, and exact-domain selection
keeps all cross-domain rules separate. The historical 82/83 source verse-number
ambiguity is retained without normalization.

### Travel / Foreign Residence Pack v1

The cumulative production release `jyotish.production.cumulative@v9` retains the
previous 20 rules and adds exactly one approved Travel / Foreign Residence Pack
v1 rule: D1 sixth-house lord in 2 or 10. The active release contains 21
explicitly admitted rules. The FactContract remains
`jyotish.d1.structural.rule1@v5`; the required deterministic house-lord
placement fact and its UNKNOWN semantics are unchanged.

The pack is D1/Rashi, static, contextual natal evidence only. It makes no
immigration, visa, citizenship, permanent-settlement, exact-destination, timing,
scoring, or prediction claim. Candidates 2 and 3 are HOLD; candidates 4 and 5
are REJECTED and absent. The approved source is Bhavesha-phala /
Shashthesha-phala v44 (PDF p. 189). This Travel rule shares only the sixth-lord
fact family with Business; it has a different source passage, condition, rule
identity, and reviewed-interpretation identity, and exact-domain selection keeps
the two domains separate.

### Friends / Social Network Pack v1

The cumulative production release `jyotish.production.cumulative@v10` retains the
previous 21 rules and adds exactly one approved Friends / Social Network Pack v1 rule:
D1 tenth-house lord in 9. The active release contains 22 explicitly admitted rules.
The FactContract remains `jyotish.d1.structural.rule1@v5`; its required D1 house-lord
placement fact and UNKNOWN semantics are unchanged.

The pack is D1/Rashi, static, contextual natal evidence only. It makes no friend-count,
popularity, social-standing, loyalty, betrayal, social-media influence, professional-
networking, timing, scoring, or certainty claim. Jupiter in Gamana avastha, Jupiter in
Agamana avastha, and Sun in Sabha avastha remain HOLD; Mars in Sabha avastha with location
branches is REJECTED. The approved source is Bhavesha-phala / Karmeshas-phala v77 (PDF
p. 194), shared with Career and Spirituality only as provenance: the Friends rule and
reviewed interpretation have distinct immutable identities, and exact-domain selection
keeps the three domains separate.

### Career Part 0 natal completion (NEXT-ADMIT-01)

The cumulative production release `jyotish.production.cumulative@v11`
(`knowledge/career_part0_pack_v1.py`) retains the previous 22 rules and adds three Career
rules from review packet Part 0a (Bhavesha-phala / Karmeshas-phala, PDF p. 193): the D1
tenth-house lord in 1 (v.71), in 2, 3 or 7 (v.72), and in 8 (v.76). The active release
contains 25 rules. With these, every resolvable 10th-lord placement (1–12) has exactly one
natal Career rule. The FactContract stays `jyotish.d1.structural.rule1@v5`, and v10 is
unchanged (hash-pinned in tests).

All three rules are D1/Rashi, static, `CONTEXTUAL`, with no polarity. v.71 and v.72 use the
packet's proposed wording verbatim; v.71's childhood-illness clause is left out. v.76 is a
**calculated match only**: its reviewed statement says that a reviewed indication exists and
that its wording is withheld pending further review. v.76's text, including its lifespan
clause, is not reproduced in code or shown to users.

Review: a **general** expert approval, "approved as proposed" (reviewer "Pandit ji", full
name pending; Acharya; verbal, relayed, 2026-11-23). It is recorded in every required review
category, and every record's notes quote the statement verbatim and say that no item-level
readings, OCR issues or translations were individually addressed. Governance records:
`docs/admissions/`.

### Reviewer's Sitting 1 + 2 verdicts (NEXT-ADMIT-02)

The cumulative release `jyotish.production.cumulative@v12` (`knowledge/admit02_pack_v1.py`)
supersedes v11 (unchanged, hash-pinned). It has 26 rules. The 24 rules on the reviewer's
checklist are confirmed under his record (reviewer "Pandit ji (full name pending)", Acharya;
written verdicts relayed by Atul, 2026-11-24; admission instructed by the project owner;
authorship of the written verdicts not independently confirmed). Wording changes for items
4–7, 14 and 15. The Career 10th lord in 4/10 is split into two rules (4th and 10th, each
with its own wording). The Children rule "10th lord in 5/11" is no longer surfaced; it stays
in the source registry. The 7th-house part of v.72 is paused (`…in_2_or_3` keeps the 2nd/3rd
wording, and `…equals_7` states only that a reviewed indication exists, with wording pending
source verification). Timing production v3 carries his v.87 and v.140 wording; the rules and
conditions are those of v2. Record: `docs/admissions/jyotish.admit02.sitting-1-2.admission.v1.md`.

**Reviewer conventions** (Sitting 2; project conventions, not universal classical law):

- **Houses from the Lagna only** (item 18). For these D1 lordship/placement rules, ownership
  and placement are counted from the D1 Lagna. Chandra Lagna is not used unless a source
  explicitly calls for it.
- **Joined** (item 19): "Joined = same sign, with no separate degree-orb requirement for
  rule matching."
- **Dispositor** (item 24): the lord of the sign holding the 10th lord is a calculated fact
  only, never an admitted rule.
- **Śubha** (item 21): śubha (auspicious/favourable) is a modifier, never standalone
  evidence. It never triggers a Career claim by itself.
- **वित्त / लाभ / सम्पत्** (item 23): tagged finances/resources/wealth, gains/benefits and
  prosperity/wealth/resources (राज्य / नृपाश्रय: authority/status/position). The user's
  question chooses the domain (Career, Income, Wealth, Status); none is hard-coded as Income.
- **Several rules in one Dasha** (item 22): kept as separate evidence items; no super-rule.
- **Sanskrit → gloss → context** (item 20): the Sanskrit term is kept in the evidence, a
  controlled modern gloss is displayed, and interpretation follows from context; e.g. राज्य
  is authority/office/status, never "government job".
- **MD primary, AD secondary** (Sitting 1 item 27, Sitting 2 item 17): the Antardasha lord
  participates as secondary activation. Rules admitted for the Mahadasha (v.87) are never
  applied to the Antardasha. In Period themes, Antardasha lines are labelled "(secondary)".
- **Dignity is a modifier** (Sitting 1 item 26, X2): the rule lord's sign dignity (own,
  exaltation, debilitation: existing D1 facts) is shown as a calculated fact next to the
  rule. It is one strength factor, not a strength model, and never inverts, negates or
  changes a rule's result.
- **Weights** (Sitting 1): each admitted rule is primary or secondary (`rule_weights.py`).
  Secondary rules are shown as "Supporting" and after the primary ones. Display order only,
  never a score or a ranking.

**Source readings:** v.71 is recorded as printed, कर्मेशाधिपतौ (Sitting 2 item 27). The v.76
second-line reading and the अल्पायु discrepancy stay open (item 28); v.76 stays withheld.

**Held:** P1–P4 and P6 pending source verification, and P5 (no reviewer-approved wording
for the two Dashas). The 7th-house part of v.72 (मद) is paused.

### Provisional rule tier (NEXT-PROVISIONAL-01)

Project-owner decision (2026-11-24): build all domains first with PROVISIONAL rules, then hold
one final expert review. Provisional and reviewed content are never mixed:

- **Separate corpus.** `knowledge/provisional.py` (governance) and
  `knowledge/provisional_pack_v1.py` (`jyotish.provisional@v1`). A provisional rule never
  enters a `ProductionRelease`, a manifest, the governed evaluator, the evidence package, the
  claim ledger, `rule_review_types` or the reviewed answer text.
- **Admission** requires a justification record: source and verse/locator, original text,
  draft translation, interpretive reasoning, conventions used, confidence (high/medium/low;
  the author's own confidence in the reading, not a strength) and the author: "drafted_by: AI
  agent; adopted_by: project owner (pending)" for an AI-drafted rule (every rule so far, the
  three seed rules included), or "project owner, provisional" for one the owner wrote. The
  owner's adoption is not a review. Status is `ReviewStatus.PROVISIONAL`, which the existing
  admission flow never accepts as REVIEWED. Ids start with `provisional.` and may not collide
  with reviewed ids. Conditions use D1 house-lord placement facts only (D1, static,
  contextual; no polarity, weight or timing).
- **Guards.** The displayed statement passes the ranking and evaluative guards and may not
  call itself reviewed, approved, admitted, certified or verified, at admission and again at
  display (a failing sentence is dropped).
- **Display.** Only with the request flag `include_provisional` (default false; `/analyze` and
  `/consultation`), returned in `provisional_interpretations` on each answer. Web: the toggle
  "Show provisional interpretations (beta)", off by default and remembered per browser
  (`localStorage` `jyotai-show-provisional`); a separate "Provisional interpretations" block
  with a badge naming the author's confidence ("Provisional · medium confidence";
  NEXT-MARRIAGE-01, was "Provisional — pending expert review"), and the full justification in the
  evidence disclosure.
- **Promotion.** `promote_to_reviewed` needs four human review records (source,
  translation, interpretation, formalization; status REVIEWED), then runs the existing
  `AdmissionValidator.validate_production_active`. Neither provisional author is ever the
  reviewer; an AI agent never is.
- **Final review pack.** `cd apps/api && uv run python -m astrologer.knowledge.review_pack
  [--pdf]` writes `research/final-review/review-pack.md` (and the PDF to
  `~/Desktop/jyotai-review/`): every provisional rule, grouped by domain, with its
  justification and "☐ Approve ☐ Change ☐ Reject". A test keeps the committed pack current.

Seed corpus v1 (three rules, Bhavesha-phala, original text read from the local page images,
OCR corrections listed per rule): Education, 5th lord in the 4th (v.37, medium); Spirituality,
5th lord in the 7th (v.40, low: line 2 may add a Lagna-lord condition); Wealth, 7th lord in
the 5th (v.54, high).

### Marriage domain, provisional (NEXT-MARRIAGE-01)

No reviewed natal or timing rule exists for marriage. Marriage answers
(`application/marriage.py`, `marriage-answer-v1`) use the consultation layout and state only:

- **Outlook** ("What does my chart say about marriage?"): calculated chart factors: the D1 7th
  lord and its house, Venus and its house, and each one's sign dignity as a calculated
  modifier fact (X2 convention; it changes nothing). Sections: `direct`, `chart_factors`,
  `limit`.
- **Timing / year** ("When will I get married?", "marriage in 2027?"): no date prediction.
  The calculated Vimshottari MD/AD periods of the 7th lord and of Venus overlapping the asked
  range (an undated question: the next 20 dasha years from the as-of instant, a presentation
  window), the reviewed Period themes of those lords (X18 v2 compact form, one line per lord,
  "(secondary)" when only Antardashas are listed; the 7th lord's line carries the 7th house),
  and "No reviewed timing rule exists for marriage". For a range of at most a year every
  running MD/AD goes in Chart details. Two years are listed together and never ranked.
- **Out of scope**, one polite line each: compatibility / guna milan (needs the partner's
  chart), Mangal checks, predictions of a marriage ending, fatalistic questions (ever /
  never, delay, denial, destiny, "unhappy").
- **Wording guard** (`composition/marriage_guard.py`): no fear-based or fatalistic wording
  ("delay", "denial", "unhappy", "dosha", "doomed", "never marry" …) in marriage answers
  outside quoted source text; plus the ranking and evaluative guards (admitted signification
  terms excluded). A failing section is dropped.

**Provisional 7th-lord rules** (corpus `jyotish.provisional@v2` = v1 unchanged + 9 Marriage
rules; drafted by an AI agent, owner adoption pending). Source: BPHS Bhavesha-phala,
अथ सप्तमेशभावफलम्, vv. 50–56, PDF pp. 190–191 (printed 192–193), read from the page images.
All seven verses (all 12 houses) were located:

| House(s) | Verse | Used as | Confidence |
| --- | --- | --- | --- |
| 1 | 50 (तनौ) | wording held (conduct judgement) | high |
| 7 | 50 (चास्ते read as च अस्ते) | wording held | medium |
| 2, 9 | 51 | wording held (conduct judgement) | high |
| 4, 10 | 53 | wording held (spouse's fidelity); Hindi 2nd sentence is a v.54 carry-over | high |
| 6, 8 | 55 | wording held (health of spouse, absolute phrasing) | high |
| 12 | 56 | **shown**: "the text describes the spouse as beautiful (चारु)" | medium (निर्धनी referent) |
| 3, 11 | 52 | not drafted: children only, no marriage clause | — |
| 5 | 54 | not drafted: no marriage clause (already the Wealth rule) | — |

*Held wording*: the rule is recorded in full (justification, review pack) but the app shows
only "A provisional source verse exists for this placement; its wording is held for the
expert review." and never sends the draft translation. The badge names the author's
confidence ("Provisional · medium confidence"). The reviewed 7th-house signification is
"trade or business" only; no marriage term is admitted yet.

### Topic-tagged significations, provisional Marriage terms, D9 facts (NEXT-MARRIAGE-02)

**Domain tags.** Every signification term carries domain tags (Career, Marriage, Wealth, …),
each `reviewed` or `provisional`; an answer shows only the terms tagged for the asked domain
(`knowledge/signification_tags.py`).

- Reviewed terms are tagged in a separate versioned record,
  `jyotish.signification.domain-tags@v1`, keyed by (subject kind, subject, Sanskrit term). The
  admitted manifests are untouched (hashes still pinned). Tag set v1 tags **every** reviewed
  term **Career (reviewed)** and nothing else: the terms were the packet's "Proposed for
  Career" column and were admitted for Career. A reviewed tag set may carry reviewed tags only.
- `domain_view(corpus, domain, tags)` keeps only terms with a reviewed tag for the domain
  (entries left empty are dropped; the X18 record stays). The Career view is the corpus
  itself, so every Career answer is byte-identical. In a covered corpus an untagged term is
  shown in no domain (fail closed). A corpus the tag set does not cover (test fixtures)
  predates tagging and is treated as Career only.
- Marriage answers use the Marriage view, which is empty: a Marriage answer never shows
  "trade or business", "adviser or counsellor" or any other Career term. Period themes then
  list the periods only (one line per lord, "(secondary)" when only Antardashas) followed by
  "Reviewed marriage meanings for these periods are pending expert review." The reviewer's
  X18 closing is not used (no themes are shown); the direct line says the periods "are listed
  below" and the closing reads "These are calculated periods; they do not predict whether or
  when a marriage will happen."

**Provisional Marriage significations** (`knowledge/provisional_signification.py`, corpus
`jyotish.provisional.signification@v1`; drafted by an AI agent, owner adoption pending; the
same justification record as a provisional rule, read from the page images). Tags on the
term's own record, always `provisional`. Shown only with `include_provisional` as items of
kind `signification` in `provisional_interpretations` (badge = author's confidence; placement
line from calculated D1 facts: the house's sign and lord, or the graha's house). Never in the
reviewed text, evidence, ledger or review types.

| Subject | Term (display) | Source (selected edition) | Confidence |
| --- | --- | --- | --- |
| 7th house | जाया ("spouse") | द्वादशभावविचाराध्यायः v.7, PDF p. 147 (printed 149); corroborated by कारकाध्याय v.36 (दारा from the 7th) | high |
| Venus | कलत्र ("spouse (kāraka)") | कारकत्व v.6 (कलत्र…कारको भृगुः), PDF p. 109 (printed 111); corroborated by v.37 (सितः, bhāva-kāraka of the 7th, PDF p. 108) and v.33 (7th from Venus for the wife, PDF p. 107) | high |
| 2nd house | कुटुम्ब ("family") | द्वादशभावविचाराध्यायः v.2, PDF p. 146 (printed 148) | low (no spouse in the verse; v.35 calls the 2nd दारकारक but v.36 takes दारा from the 7th: unresolved, not used) |

Not drafted: "marriage" and "partnership" (not in the verses), व्यापार (stays Career), the
7th house's journeys, lost things and death. The verses address a male native (जाया, कलत्र:
wife); the display says "spouse" (convention recorded, for the expert review). The 7th- and
2nd-house verses also list death, so their draft translations stay in the review pack and
the app shows only the held-translation notice (owner decision: no fear-based text). The
held 7th-lord rule wording (NEXT-MARRIAGE-01) stays held.

**D9 calculated facts** (`application/marriage_d9.py`; section `d9_factors`, "Calculated D9
(Navamsa) factors", in every outlook, timing and year marriage answer). From the existing
Parashari Navamsa chart (`VargaEngine`) and `jyotish-d9-derived-facts-v1`: the D9 Lagna; the
D9 7th house's sign, its lord (classical seven-planet sign rulership, the D1 convention; a
JyotAI-v1 computational convention) and the lord's D9 house; Venus's D9 sign and house (when
Venus is the D9 7th lord, Venus's line carries its house); whether the D1 7th lord is
vargottama (its D1 sign, i.e. the sign of the D1 house it occupies, equals its D9 sign; TRUE
or FALSE, never guessed). Each sentence cites its fact ids; the section ends "These are
calculated D9 (Navamsa) positions; no reviewed interpretation of the D9 chart for marriage
exists yet, so JyotAI reads no meaning into them." **D9 interpretation is an open
methodology item** (reviewer method and wording needed; e.g. how a vargottama 7th lord or
the D9 7th lord's house would be read, if at all).

### Domain template, Wealth domain, provisional (NEXT-WEALTH-01)

**Carry-overs.** (A1) The sign-dignity line reads "Calculated fact (sign dignity): …" in every
domain (was "…, shown as a modifier only; it does not change the reviewed indication" in Career
and "…, shown as a modifier only" in Marriage). The meaning is unchanged: sign dignity is a
calculated X2 modifier only, it never changes a reviewed indication and never calls a planet
strong or weak. (A2) कुटुम्ब (2nd house) is no longer a Marriage term; it is a provisional Wealth
term (low). The v.35/v.36 conflict (2nd house दारकारक vs दारा from the 7th) is a question in the
review pack. (A3) `domain_view`: a corpus the tag set does not cover shows in **no** domain,
except the named legacy/test corpora (`jyotish.signification.production@v0-empty`,
`fixture.signification@v1`), which stay Career only. (A4) A listed or running dasha period that
ends after the asked window ends "(continues past the window)".

**Domain template** (`application/domain_pipeline.py`, `application/domains.py`). A
`DomainConfig` names the houses (their lords are the domain lords), the kārakas, the
signification tag, the fixed texts, the wording guard, out-of-scope patterns and an optional
divisional-fact builder. The generic pipeline states: calculated chart factors with sign
dignity; the reviewed natal rules of the domain (verbatim, exact domain only); for timing/year
questions the MD (primary) / AD ("secondary") periods of the domain lords and kārakas in the
window; Period themes from terms tagged for the domain, or the periods only and a pending line;
divisional facts where configured (Marriage: D9); timing status; one limit. Marriage runs on it
(byte-identical apart from A1/A4, benchmark v25). **Career is only partly on the template**: its
config supplies the 10th house and the Career tag, but its reviewed timing, year glance and
comparison composition remain the Career code (open item).

**Wealth answers** (`application/wealth.py`, `wealth-answer-v1`): D1 2nd and 11th houses, their
lords, Jupiter as kāraka. Reviewed natal rules shown: only Wealth-domain rules confirmed in
Sittings 1+2 (items 8–11: `bphs.d1.house_lord.11.in_1.wealth.v1`, `…11.in_2_or_5.wealth.v1`,
`…11.in_9_or_10.wealth.v1`, `…5.in_11.wealth.v1`). The General 11th-lord-in-9/10 rule is never
shown in Wealth: evidence selection is exact-domain (`evidence/selector.py`) and the pipeline
filters by domain again. No reviewed wealth timing rule exists: periods are listed only (no
date, no ranking); no reviewed term is tagged Wealth, so Period themes list the periods with
"Reviewed wealth meanings for these periods are pending expert review." No Career or Marriage
term is shown. No divisional chart is used (D2 is calculated but has no reviewed method).
Out of scope, one line each: investment/trading/gambling advice, amounts of money, fatalistic
questions. Wording guard `composition/wealth_guard.py` (no poverty, loss, debt, ruin …).

**Provisional Wealth** (toggle only; drafted by an AI agent, owner adoption pending; read from the
page images of the selected edition).

| Item | Term / statement shown | Source | Confidence |
| --- | --- | --- | --- |
| 2nd house | धन "wealth" | द्वादशभावविचाराध्यायः v.2, PDF p. 146 | high |
| 2nd house | कुटुम्ब "family" (A2) | same verse | low |
| 11th house | लाभ "gain" | द्वादशभावविचाराध्यायः v.11, PDF p. 148 | high |
| Jupiter | धन "wealth (kāraka)" | कारकत्व v.5, PDF p. 109; v.37, PDF p. 108 | high |
| 2nd lord in 1 / 2 | wealthy (धनवान्) | Dhanesha-phala v.9 / v.10, PDF pp. 183–184 | high |
| 2nd lord in 5 | wealth through a son (पुत्रतो धनवान्) | v.12, PDF p. 184 | high |
| 2nd lord in 8 | gain of wealth connected with land (भूमिद्रव्य) | v.15, PDF p. 184 | medium |
| 2nd lord in 9 / 11 | wealthy (धनवान्), enterprising (उद्यमी) | v.16, PDF pp. 184–185 | high |
| 2nd lord in 10 | wealth (धन) | v.17, PDF p. 185 | medium |
| 2nd lord in 6 | **held** (loss of wealth, वित्तनाश) | v.13, PDF p. 184 | high |
| 2nd lord in 12 | **held** (without wealth, धनवर्जित) | v.18, PDF p. 185 | high |

The 12 second-lord placements: 7 shown, 2 held, 3 not drafted (3rd/4th: v.11, 7th: v.14; no
wealth clause). Eleventh lord: 1, 2/5, 9/10 already have reviewed Wealth rules; 3/4, 6, 11, 12
have no wealth clause; 7/8 (v.82) has no wealth clause and predicts the wife's death; none is
drafted. Every Wealth item's translation stays in the review pack (the verses' other clauses are
not wealth themes); the app sends the reason instead. Corpora: `jyotish.provisional@v3`,
`jyotish.provisional.signification@v2`.

### Property domain, provisional (NEXT-PROPERTY-01)

**Carry-overs.** (1) Router: everyday wealth words (money, rich, income, savings; Hinglish
paisa, dhan, kamai, aamdani, bachat, amir) route to Wealth and everyday property words (flat,
land, plot, vehicle, car; Hinglish ghar, makaan, zameen, gaadi) to Property, but only when the
question names no other domain, so a Career question that mentions money, income or a car stays
Career. A numbered house ("my 7th house") is no longer a Property word; "kab" is a timing word.
Investment and amount questions (incl. "nivesh", "kitna") keep the one-line Wealth reply.
(3) Period themes: every Mahadasha line reads "(primary)" and every Antardasha line
"(secondary)" in every domain (a merged same-lord line: "Mahadasha (primary) and Antardasha
(secondary)"); the X18 v2 scope is unchanged, only its label is now shown for both roles.
(4) The NEXT-PROVISIONAL-01 Wealth rule v.54 (7th lord in the 5th) gets record v2: same
statement and justification, translation kept in the review pack like every other Wealth item.

**Property answers** (`application/property.py`, `property-answer-v1`, generic pipeline): the D1
4th house and its lord, and as kārakas the planets the text names for land, a house or vehicles
with a high-confidence reading (कारकाध्यायः, अथ सूर्यादिग्रहाणां कारकत्वमाह, PDF p. 109):
Mars (भूमि land, सद्म dwelling, v.3), Jupiter (गृह house, v.5), Venus (यान vehicles, v.6). The
Sun's क्षेत्र (v.1) is medium (it may mean a region), so the Sun is a provisional signification
only. The bhāva-kāraka list (v.37) gives the 4th house to सोमः (Hindi: Mercury) and names no
property matter; not used (reviewer question). No reviewed natal Property rule and no reviewed
property timing rule exist: outlook = calculated factors with sign dignity; timing/year = MD
(primary) / AD (secondary) periods of the 4th lord, Mars, Jupiter and Venus, no date, no ranking;
Period themes = the periods + "Reviewed property meanings for these periods are pending expert
review." No Career, Marriage or Wealth term. **D4 is not calculated** (JyotAI computes D1, D2, D9,
D10), so no divisional fact is shown (open item). Out of scope, one line each: prices/values;
buy, sell or invest advice; legal matters; fatalistic questions (losing a home, accidents, "will
I ever own"). Guard `composition/property_guard.py` (no loss, dispute, accident, ruin …, no "good
time to buy", no "will appreciate").

**Provisional Property** (toggle only; drafted by an AI agent, owner adoption pending; read from
the page images of the selected edition; every translation stays in the review pack).

| Item | Term / statement shown | Source | Confidence |
| --- | --- | --- | --- |
| 4th house | गृह "house or home" | द्वादशभावविचाराध्यायः v.4, PDF p. 147 | high |
| 4th house | क्षेत्र "fields or land" | same verse (Hindi: खेत) | high |
| 4th house | वाहन "vehicles" | same verse (Hindi: सवारी) | high |
| Mars | भूमि "land (kāraka)" | कारकत्व v.3, PDF p. 109 | high |
| Mars | सद्म "dwelling (kāraka)" | same verse (Hindi omits it) | medium |
| Jupiter | गृह "house (kāraka)" | कारकत्व v.5, PDF p. 109 | high |
| Venus | यान "vehicles (kāraka)" | कारकत्व v.6, PDF p. 109 | high |
| Sun | क्षेत्र "fields or land (kāraka)" | कारकत्व v.1, PDF p. 109 | medium |
| 4th lord in 2 | endowed with all kinds of possessions (सर्वसम्पद्युत) | Sukhesha-phala v.27, PDF p. 186 | low |

Not drafted from v.4: बन्धु (relatives) and मातृसौख्य (the mother's happiness), which belong to a
relatives/mother/happiness domain JyotAI does not have (so they are not tagged Property), and
निधि (treasure; a wealth matter). The 12 fourth-lord placements (Sukhesha-phala vv. 26–34,
PDF pp. 186–187): 1 shown (2nd, v.27), 0 held, 11 not drafted: 1st (v.26), 3rd/11th (v.28,
wealth by effort + illness), 4th (v.29, wealth: सर्वधनाधिप; the Hindi says संपत्ति, a reviewer
question), 5th/9th (v.30), 6th (v.31, accusatory), 7th (v.32), 8th/12th (v.33, fear-based and
accusatory), 10th (v.34); none has a land, house or vehicle clause. Corpora:
`jyotish.provisional@v4`, `jyotish.provisional.signification@v3`.

### Children hard guards (NEXT-CHILDREN-GUARD-01)

Owner decision; a product decision, not legal advice. The PCPNDT Act s.22 bans advertising sex
determination "by any means whatsoever, scientific or otherwise", which may reach a public app.

**One-line replies, in any domain and any wording** (`questions/children_scope.py`, language
only; English, Hinglish and Devanagari). The router sends a matched question to the Children
domain only (whatever else it names), and the answer is one fixed line
(`application/children.py`): no chart factors, no evidence, no provisional item, no language
model. Precedence: child sex first.

| Scope | Examples | Reply |
| --- | --- | --- |
| Child sex | "Will I have a son?", "boy or girl", "chances of a daughter", "how many sons", "wealth through a son", "putra yog", "beta hoga ya beti", "बेटा होगा?" | JyotAI does not predict a child's sex. |
| Fertility / pregnancy | pregnancy, conceiving, fertility, IVF, miscarriage | Questions about fertility and pregnancy are out of scope for JyotAI; for medical matters, please consult a doctor. |
| Whether / how many | "Will I have children?", "will I ever have a child", "childless", counts, "santan hogi?" | Whether or how many children someone will have is out of scope for JyotAI; for medical matters, please consult a doctor. |

Still answered as before: "What does my chart say about children?" and a plain timing question
("When will I have children?": "No reviewed timing rule is available for this area."). A
question about an existing child ("Will my son do well in exams?") is not a sex question. The
guard runs before the bare year comparison and on consultation follow-ups (a new turn).

**Wording guard** (`composition/children_guard.py`), in every domain: no child-sex word (son,
daughter, boy, girl, male child; beta, beti, ladka, ladki, putra; बेटा, बेटी, लड़का, लड़की) and
no childlessness or loss wording (childless, without children, barren, miscarriage, loss of a
child; पुत्रहीन, सुतहीन, निःसंतान …) outside quoted source text. It applies to every section
of every answer (generic pipeline and a final pass over every domain's sections and answer
line), to reviewed statements in the detailed answer, to every displayed field of a
provisional item (statement, placement, reasoning, conventions, notes, held reason, sent
translation), to the language-model narrative (rejected, deterministic fallback) and to
`promote_to_reviewed`.

**Held, never dropped.** Text the guard holds shows a notice instead of disappearing: a
section, the answer line or a reviewed statement shows `CHILD_HELD_NOTICE` ("This text is held
for the expert review under JyotAI's children wording rule."); a provisional statement shows
the held statement (`wording_held`, translation not sent); any other provisional field shows
`CHILD_HELD_NOTICE`; a held translation is not sent (the app's held-translation line). The
item or section stays. Admitted text is never reworded: a reviewed statement is held, not
changed (none of the 26 reviewed statements is held today).

**पुत्र and सुत.** Where the text says पुत्र or सुत, the term is shown as written with the gloss
"children (the text says 'son')"; it is a quoted term, never a prediction about the user. The
gloss is the only allowed "son", and it applies to सुत also where it names the fifth house
(सुतभाव, सुतेशे, सुते). A displayed field with पुत्र or सुत must carry the gloss, and every
record whose displayed text (the source verse included) has either term records the choice in
its justification conventions (`PUTRA_CONVENTION`); without it, the field (or the verse) is
held. New record versions, all PROVISIONAL (none was REVIEWED): provisional corpus
`jyotish.provisional@v5` (second-lord Wealth vv. 9, 10, 12, 13, 17, 18 → rule version v2; v.12
reads "the text describes wealth through children (the text says 'son'): पुत्रतो धनवान्" and
its reasoning "सुतभाव, the house of children (the text says 'son'), is the fifth house";
convention only: Education v.37 and Spirituality v.40 → v2, Wealth v.54 → v3) and
`jyotish.provisional.signification@v4` (Venus कलत्र, 11th-house लाभ, Jupiter धन and गृह, Mars
भूमि and सद्म → term v2). Conditions, originals, translations (kept in the review pack),
confidence and held/shown status are unchanged. Reviewer question Q7 asks to confirm the gloss
for both terms.

**Source verses.** A source verse (Sanskrit, or the edition's Hindi quoted in a note) whose
clause names a child's sex beyond the glossed term or denies children
(`children_guard.source_child_clause`: e.g. पुत्रहीन, सुतहीन, अपुत्र, अनपत्य, "पुत्रसुखं न",
पुत्री, पुत्रवान्, सुता, ज्येष्ठपुत्र, बेटा/बेटी) is not displayed: the evidence disclosure shows
`SOURCE_HELD_NOTICE` ("The source verse is held for the expert review under JyotAI's children
wording rule; the full verse is in the final review pack.") with `original_text_held: true`, and
the record and the review pack keep the verse verbatim (the pack marks each one "Source verse:
held in the app"). Held today: second-lord Wealth vv. 9 (पुत्री), 10 (पुत्रहीनः), 12
(पुत्रवान्), 17 (सुतहीनो), 18 (ज्येष्ठपुत्रसुखं न हि). A glossable term alone (पुत्रतो, the
kāraka lists' पुत्र) or सुत naming the fifth house is not such a clause.

### Task 10 deterministic context composition

Task 10 composes existing deterministic outputs for one explicit as-of instant:
D1, D9, D10, active Vimshottari Mahadasha/Antardasha, Jupiter/Saturn/true
Rahu/Ketu transit positions, and Task 09A D1 facts. It adds no interpretive
methodology. D2 remains available through the chart API but is intentionally
outside context-v1; Task 09A facts remain D1-only.

The dashboard insights API reuses this context only to evaluate the existing active governed
release for its fixed eight exact domains. It does not interpret Dasha, transits, D9, or D10;
does not use question routing; preserves unmatched and UNKNOWN evidence separately; and introduces
no new astrology doctrine, rule, FactContract, or release.

Each constituent output retains its own methodology and provider provenance.
Current PySwissEph provenance may report `Moshier internal ephemeris`; this is
preserved and is not external Swiss Ephemeris data-file validation.

### Divisional charts

Start with:

- D1
- D9
- D10
- D2

Do not implement every divisional chart in the first milestone.

## Timing

Primary:

- Mahadasha
- Antardasha
- Pratyantardasha when needed

Transits:

- Jupiter
- Saturn
- Rahu
- Ketu

### Dasha-lord chart linkage (`jyotish.dasha_linkage.v1`)

For each operating Vimshottari Mahadasha/Antardasha pair in a Career calendar-year answer, the
application projects existing `jyotish-derived-facts-v1` D1 facts onto the two lords. This
adds no doctrine and no evaluation.

- Reference point: the D1 Lagna only (Whole Sign). No Moon, Sun, Arudha, Dasha-lord or other
  reference point is used. The methodology records `reference_point = "d1_lagna"` and the
  user-facing framing line states it.
- Facts per lord: `ruled_houses`, `placement_house`, `sign`, `own_sign` and `exaltation_sign`
  (seven classical planets only; debilitation is computed but not source-admitted and is not
  surfaced), `is_tenth_lord`, `occupies_tenth`, `aspects_tenth_house`, `aspects_tenth_lord`,
  `same_sign_as_tenth_lord`. A lord's relation to itself as the 10th lord is
  `NOT_APPLICABLE`.
- `ad_house_from_md`: the inclusive count from the MD lord's sign to the AD lord's sign
  (1–12; same sign is 1; Pisces to Aries is 2). It is the only count not taken from the Lagna,
  it is reported as a plain number, and no relationship label is attached to it.
- Rahu and Ketu: under the classical seven-planet lordship convention they are assigned no
  sign rulership (empty `ruled_houses` with a convention note). Their aspects are unmodeled
  in the seven-planet graha-drishti convention, so their aspect facts are `UNKNOWN` — never
  `False` and never described as "no aspect". UNKNOWN is not FALSE.
- Conventions, not facts: the items below are methodology conventions recorded in
  `DashaLinkageMethodology` and in each affected fact's `note`. They are choices made by this
  methodology, not astrological facts about the chart, and must not be presented as facts:
  - Lordship: classical seven-planet sign rulers (`lordship_convention`). Rahu and Ketu are not
    treated as house lords (`rahu_ketu_ownership = "unmodeled"`).
  - Aspects: seven-planet graha drishti (`aspect_convention`). Rahu/Ketu aspects are unmodeled
    (`rahu_ketu_aspects = "unmodeled"`), so their aspect facts are `UNKNOWN`.
  - 10th lord's relation to itself: when the Dasha lord is the 10th lord, `aspects_tenth_lord`
    and `same_sign_as_tenth_lord` are treated as `NOT_APPLICABLE` (no self-aspect or
    self-conjunction is asserted).
  - Dignity of Rahu/Ketu: own-sign and exaltation-sign facts are `UNKNOWN` for the nodes,
    because node dignity is unmodeled; they are never `False`.
- Presentation: the `dasha_context` section contains only sentences generated from linkage
  fact IDs (plus one sentence naming the 10th lord, backed by the existing D1 fact
  `jyotish.d1.house.10.lord`), followed by exactly one fixed framing line: "These are
  calculated chart relationships, counted from your D1 Lagna; a reviewed Career
  interpretation of this Dasha is not yet available." Sentences are grouped by period: one
  block per Mahadasha and one per Antardasha, each opening with the lord and the period's
  local dates. A lord's calculated-`False` 10th-house relationships are collapsed into one
  sentence that cites every underlying fact ID; `UNKNOWN` facts are never folded into that
  negative sentence and keep their own explicit "is unknown" sentence. The per-fact
  breakdown remains in the evidence disclosure.
- Interpretation: a separate, review-gated `DashaInterpretationSlot` can be filled only by
  Career rules admitted through the production admission path. The production Dasha
  interpretation corpus is empty, so no Dasha interpretation is shown.

### Career year synthesis (`career-synthesis-v1`)

Structural synthesis, not new astrology: it adds no facts and no rules. For a Career year
answer it joins the plan's reviewed claims (approved natal and approved timing
interpretations) with the year's `jyotish.dasha_linkage.v1` facts using only three
deterministic co-reference links:

- `SAME_PLANET`: a claim's fact IDs resolve to a planet (for example
  `jyotish.d1.house_lord.10.placement_house` resolves through `jyotish.d1.house.10.lord`)
  that is also a Mahadasha or Antardasha lord of the year.
- `SAME_HOUSE`: a claim's fact IDs name a house that a period lord rules (`ruled_houses`) or
  occupies (`placement_house`), both `KNOWN`. Not emitted for a lord that is already a
  `SAME_PLANET` link for that claim.
- `SAME_PERIOD`: a claim's timing window (`timing_reference`) overlaps a planned MD/AD
  segment of the year. Static natal claims carry no window and never form this link.

Each link cites the claim's fact and rule IDs and the Dasha side's fact IDs. Admitted Dasha
interpretation rules, when any exist, are listed in `dasha_rule_ids` (empty otherwise). The
calculation methodology that produced the Dasha-side facts (`jyotish.dasha_linkage.v1`, or
`vimshottari-v1` for segments) is provenance, not a rule: it is carried in
`calc_method_ids` and never appears in a rule-ID field. Sentences state only the shared
reference. Causal or evaluative connectives are forbidden and enforced by a
blocklist test. When no link exists the answer says none was found among the calculated
links; that is not negative evidence. A claim whose fact IDs do not resolve to a planet or
house has no link, which is likewise not negative evidence.

Out of scope: agreement or conflict between claims. No admitted rule carries an approved
polarity, so claims are never combined, weighed, or set against each other.

Presentation (deterministic templates only; no ids in prose):

- Direct line, two or three sentences.
  - Exactly one reviewed timing rule matched: a framing sentence built only from calculated
    facts ("Your current Jupiter Mahadasha matches a reviewed BPHS timing rule."), then that
    rule's admitted meaning sentence, byte-identical to the admitted wording, then "The full
    reviewed text is quoted in the Reviewed Career timing section below." The full wording,
    its non-guarantee sentence included, stays verbatim in the timing section (NEXT-TONE-01).
    "current" is used only when `as_of` falls inside the matched Dasha window; otherwise
    "Your Jupiter Mahadasha in 2027". The framing cites the period's segment ids. (The
    lord's 10th lordship and placement are stated in the glance, not here.)
  - No reviewed timing rule matched: the year's calculated MD/AD periods, the reviewed natal
    indication by its plain label, then "No reviewed timing rule applies to 2027."
    Co-reference links
    (`SAME_HOUSE`/`SAME_PLANET`) are not stated in the direct line; they stay in `why`.
  - Several timing rules matched: the timing status, then the co-reference.
- `why` section: one line per period planet. Lines for the same planet and period role are
  merged across claims ("both reviewed indications concern your 10th lord, Jupiter"), and a
  planet that is both the Mahadasha and Antardasha lord gets one line. `SAME_PERIOD` lines
  are replaced by one sentence when the timing window spans the whole asked year; otherwise
  each is kept. The framing sentence ("Each line states only a shared calculated
  reference …") is carried in the section's `framing` field and shown in the evidence
  disclosure, not in the visible Why text (NEXT-TONE-01).
- **One template non-prediction sentence per answer** (NEXT-TONE-01): only the closing
  `limit` section ("What can be concluded") carries one, e.g. "These are reviewed themes and
  calculated periods for 2028, not a prediction of specific events." It names only what the
  answer shows: "reviewed themes" when Period themes are present, otherwise "reviewed
  indications" when a natal or timing rule matched, and always "calculated periods". A
  comparison likewise has one, in its limitations ("These are reviewed indications and
  calculated periods for 2027 and 2028, not a prediction of specific events."). Admitted and
  approved text is not counted and is never removed where quoted: the timing rule's
  non-guarantee in the timing section, the natal rule text, the X18 Period-themes closing
  "This does not predict an event or an outcome." (part of the approved `period-themes-v1`
  wording), and the v.76 withheld notice. UNKNOWN statements (Rahu/Ketu aspects) are facts
  and are unchanged.
- `natal` section: the admitted natal wording only, moved out of the direct line (the 10th
  lord's placement is stated in the glance).
- **The 10th lord is stated once per year answer**, in the glance. The direct line, the
  `natal` section and the year answer's `dasha_context` do not restate it; there the Dasha
  context refers to "your 10th lord" by role. The standalone "Which Dasha applies?" reply
  still opens with "Your 10th lord is …". In a comparison, the 10th lord and the natal
  indication appear once, in "Same in both years", never per column.

#### Year glance (`year-glance-v1`, presentation convention)

A Career year answer carries a `glance` section ("<Year> at a glance", rendered on top) of
three to four templated bullets, each a `SynthesisSentence` whose ids live in the mapping,
never in the prose:

1. **Periods**: the calculated MD/AD periods covering the year, on one line.
2. **Natal**: "your 10th lord is <planet>, in your <n> house" (the one place the 10th
   lord is named), then the reviewed natal indication by its plain label, or "no reviewed
   natal Career indication matched your chart".
3. **Calculated link** (omitted when none is found): one link between a period lord and the
   10th lord or 10th house, chosen by this **fixed display precedence**, first match wins:
   1. the period lord is the 10th lord (`is_tenth_lord`);
   2. it is in the same sign as the 10th lord (`same_sign_as_tenth_lord`);
   3. it occupies the 10th house (`occupies_tenth`);
   4. it aspects the 10th house (`aspects_tenth_house`);
   5. it aspects the 10th lord (`aspects_tenth_lord`);
   6. a `SAME_HOUSE` co-reference from `career-synthesis-v1`.

   Ties go to the Mahadasha lord, then the earlier period. Only `KNOWN` TRUE linkage facts
   count, so an UNKNOWN fact (such as an unmodeled Rahu/Ketu aspect) is never a link.
   **This precedence is a presentation convention for display order only. It is not a
   strength model and has no doctrinal standing.** The bullet never calls a link strong,
   weak, important or significant, and a missing bullet is not negative evidence.
   When the chosen period lord is the 10th lord, the bullet refers to it by role ("your 10th
   lord is also your Mahadasha lord throughout 2027") so the lord is not named twice.
4. **Timing**: the matched rule's plain label ("the reviewed timing indication for Jupiter
   Mahadasha applies"), or "no reviewed timing rule applies to <year>".

The glance never quotes or rewords admitted rule text. The web view places "Calculated Dasha
chronology" and "Calculated Dasha lord relationships" in a "Chart details" disclosure,
collapsed by default; the Why, natal and Reviewed timing sections stay visible. When no
reviewed timing rule matched, the web view hides the Overview (the direct section), which
only repeats the glance; the direct section stays in the data and the plain-text answer.
- Claims are named by plain labels derived from their fact IDs ("the reviewed indication
  about your 10th lord's placement"). Rule, claim and method IDs stay in the evidence
  disclosure (links, ledger) and in each section's `synthesis_sentences`, the
  sentence-to-fact mapping.

A bare "Why?" follow-up to a year answer with reviewed claims replies from that synthesis
directly and offers plain-language choices (sent as `claim_ids`, rendered as buttons) or a
named Dasha period; a clarifying question is asked only when the bound turn has no
synthesis. "Which claim?" and "which limitations?" prompts likewise offer plain-language
choices, never typed IDs, and the prompt text names each option with exactly its button
label.

### Signification corpus and "Period themes" (`signification-corpus-v1`, `period-themes-v1`/`-v2`)

**Active since NEXT-ADMIT-02:** `jyotish.signification.production@v3`
(`knowledge/signification_admit02_v1.py`). It carries the reviewer's Sitting 2 glosses as
displays (राजकुमारः "heir, successor or senior/deputy role", राज्य "authority or office", राजा
"head, authority or governing role", सेना "forces, personnel or organized workforce", सचिवः
"adviser or counsellor", भृत्य "employees or staff", नेता "leader", पराक्रमः "courage",
विक्रम "courage, initiative or enterprise"). The Sanskrit terms are unchanged, and the
6th-house शत्रु is restored as "adversaries, opposition, competition". X18 v2 approves
`period-themes-v2`: "<Lord> <period>[ (secondary)] (<span>): reviewed themes — <Lord>:
<terms>; houses it rules and occupies: <house> (<terms>); …", with one closing at the end of
the section: "These are the reviewed themes associated with this period; actual results
depend on the full chart and other active factors." Its scope is
`MAHADASHA_PRIMARY_ANTARDASHA_SECONDARY`. Its basis is labelled in the evidence as "Project
interpretive convention, reviewer-approved; no source verse identified". The text below
describes the NEXT-ADMIT-01 corpora (v1/v2) and `period-themes-v1`, which stay unchanged as
history.

Review-gated. **Production corpus** (NEXT-ADMIT-01): `knowledge/signification_part0b_v1.py`,
`jyotish.signification.production@v2` (NEXT-SIG-02). It holds the packet 0b "Proposed for
Career" terms for all nine grahas and for houses 1, 2, 3, 5, 7, 9, 10, 11 and 12, plus the X18 record (scope
Mahadasha **and** Antardasha, template `period-themes-v1`). Excluded: every [uncertain] term
(six in the packet), आकाशवृत्ति, वर्ण, राज्यापभ्रंश, and the terms proposed as not for Career
(क्रोध, वीर्य, दुःख). Houses 4, 6 and 8 have no entry. 6th-house शत्रु ("adversaries") was in
v1 by owner decision and is removed in v2: its proposal was conditional ("reviewer to confirm
Career use") and the general approval did not confirm it. This is an open item for the
reviewer, and v1 stays hash-pinned as `SIGNIFICATION_MANIFEST_V1`. All of this was admitted under the
same general approval as Part 0a. The empty NEXT-SIG-01 corpus remains available as `EMPTY_SIGNIFICATION_CORPUS`.

- **Corpus** (`knowledge/signification.py`): graha or bhava → approved terms (each with its
  source wording and an English display), a rule id and version, a source locator, a
  governance-record reference and a REVIEWED interpretation review by a named reviewer.
  Corpora exist only through admission, which rejects draft reviews, AI reviewers,
  duplicates, and terms carrying ranking, causal, evaluative or event words.
- **Lordship principle** (review packet X18): a separate record that approves the exact
  template version `period-themes-v1` and a scope (Mahadasha only, or Mahadasha and
  Antardasha).
- **Sentence**: for each period lord in scope, "During your <Lord> <Mahadasha|Antardasha>
  <span>, the reviewed significations associated with <Lord> (<terms>) and with the houses
  it rules and occupies (<n>th house: <terms>; …) are the themes the texts associate with
  this period.", then once: "This does not predict an event or an outcome." Houses come from
  the lord's `ruled_houses` and `placement_house` linkage facts (D1 Lagna, Whole Sign); only
  houses with an admitted entry are named, and the verb says "rules", "occupies" or both
  accordingly. When the Mahadasha and Antardasha lords are the same planet over exactly the
  same window in the year, its line is emitted once, labelled "<Lord> Mahadasha and
  Antardasha" (NEXT-THEMES-01, presentation only; the template's wording is unchanged).
- **Gate**: the section appears only when the X18 record **and** at least one relevant
  entry are admitted. Otherwise it is absent: UNKNOWN, no text, never "no themes".
- **Placement** (NEXT-ADMIT-01): directly after the year glance, before Why. The glance adds
  one bullet before Timing. Since NEXT-THEMES-01 it names each period lord once, with only
  the houses (admitted entries) it brings forward, in rules-then-occupies order: "Period
  themes: Saturn: 9th, 10th, 7th houses · Mercury: 2nd, 5th, 11th houses." A lord with an
  admitted own entry but no admitted house is named alone ("Period themes: Rahu."). The full
  terms stay in the Period themes section. It covers exactly the periods that have a
  sentence and cites the same entry and X18 rule ids. Rahu and Ketu rule no sign, so only
  their occupied house is used.
- **Review type** (NEXT-THEMES-01): every answer lists, per cited rule, its review type from
  the existing records: "Independent reviewer (Pandit ji, Acharya)" (Part 0 Career rules,
  0b significations, X18) or "Project-owner review (not independently certified)" (the
  earlier natal packs; the Career timing release, which records no reviewer). Shown only in
  the evidence disclosure, never in the answer text (`application/review_types.py`).
- Each sentence cites its segment and linkage fact ids, the entry and X18 rule ids with
  versions, and the template version. A guard hit drops the sentence (fail closed). Plans
  record the corpus consulted (`signification_corpus_version`).

## Important

The calculation library and methodology must be properly licensed for commercial use.

The exact calculation settings must be stored with each chart.

## Post-Kundli dashboard presentation

The JyotishAI frontend presents factual D1 with access to D9/D10, current factual Vimshottari
Dasha boundaries, factual transit positions, governed dashboard insights, and Ask JyotishAI. It
calls the fixed eight-domain endpoint once using the existing birth input and as-of value; it does
not evaluate rules. MATCH wording is reviewed deterministic wording, while no-match and UNKNOWN
remain distinct non-negative states. This presentation introduces no Dasha, transit, or divisional
chart interpretation, doctrine, rule, FactContract, or release change.

### Detailed answer justification

Detailed Ask presentation does not add a rule or interpretive method. It only renders the actual
resolved D1 house-lord placement that triggered an already selected governed rule, and presents the
approved reviewed statement unchanged. The accompanying domain framing and limitations are fixed
scope boundaries, not Jyotish conclusions. Multiple selected rules remain separate; UNKNOWN remains
distinct from FALSE; no-match is not negative evidence. Dasha, transit, D9, and D10 interpretation
remain outside this answer layer, so static natal evidence cannot answer timing.

## Career Timing v2 candidate methodology

BPHS *अथान्तर्दशादिफलविचाराध्यायः* v.140 is admitted only for Moon MD, Venus AD, and D1 Venus
own-sign OR exaltation. The reviewed locator is printed p. 468 / local PDF p. 466; the local
Hindi/OCR appears to omit the Sanskrit `lābha` term. Kendra/trikona/11th, vv.141–145, strength,
varga, aspect, conjunction, friendship, beneficence, and mūlatrikoṇa are excluded. The entire AD is
bounded context only, not an event guarantee; no PD or transit refinement is admitted.

## BPHS Dasha-phala v.89 candidate methodology

`bphs.timing.vimshottari.career.9th_lord.in_10.md.v1` is a separately governed,
non-production candidate. Its local selected-edition locator is printed p. 440 / PDF p. 438,
*अथ दशाफलाध्यायः / Dasha-phala* v.89:
`कर्मस्थानस्थ पञ्चमेशदशा सम्पत्करी भवेत् । दशमस्थ धर्मेशदशा राज्यप्रदायिनी ॥ ८९ ॥`.
The candidate admits only the second, grammatically independent clause: the Dasha of the D1
ninth-house lord when placed in the D1 tenth house is described as `rājya-pradāyinī`.

The predicate is `MD.lord == D1.house.9.lord AND D1.house_lord.9.placement_house == 10`.
It consumes existing deterministic D1 lord/placement facts and canonical Vimshottari MD intervals,
emits only `BROAD_PERIOD`, and preserves the complete MD as `source_interval` while clipping only
the requested-horizon `effective_window`. It remains outside the active v2 release, production API
selection, and Ask workflow.

The candidate does not admit v.89's separate fifth-lord prosperity clause, v.88's conjunction or
aspect extension, or vv.90–95's relative-house/adverse-condition clauses. Its bounded meaning is
status-related timing context only; it does not establish employment, promotion, a government
position, salary or wealth increase, authority acquisition, any exact event or date, or predictive
certainty.
