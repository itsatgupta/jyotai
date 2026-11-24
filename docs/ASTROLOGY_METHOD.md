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

### Signification corpus and "Period themes" (`signification-corpus-v1`, `period-themes-v1`)

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
  accordingly.
- **Gate**: the section appears only when the X18 record **and** at least one relevant
  entry are admitted. Otherwise it is absent: UNKNOWN, no text, never "no themes".
- **Placement** (NEXT-ADMIT-01): directly after the year glance, before Why. The glance adds
  one bullet before Timing, "Period themes: <Lord> <Mahadasha|Antardasha> (<terms>); …",
  listing each period's terms (own and house terms, deduplicated) for exactly the periods
  that have a sentence. It cites the same entry and X18 rule ids. Rahu and Ketu rule no sign,
  so only their occupied house is used.
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
