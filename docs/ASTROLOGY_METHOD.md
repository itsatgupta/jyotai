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

## Career Timing Pack v1 production methodology

The only governed production timing release is `jyotish.timing.production.career@v1`, containing
exactly one rule: `bphs.timing.vimshottari.career.10th_lord.in_4.md.v1`. It is selected through a
dedicated active timing-release pointer, separate from the static release. The historical candidate
`jyotish.timing.career.candidate.v1` remains immutable. Its immutable reviewed provenance is *Brihat
Parāśara Horā Śāstra*, *अथ दशाफलाध्यायः / Dasha-phala*, verse 87; printed p. 439, local artifact PDF
p. 437, with adjacent Hindi continuation PDF p. 438. The reviewed translation says: “The Dasha of
the tenth-house lord situated in the fourth house is described as giving rājya-related results.”

Its bounded interpretation is broad Career context only: if the deterministic D1 tenth-house lord
is in house four, only a matching Vimshottari Mahadasha qualifies. `rājya` is not formalized as a
claim of employment, promotion, office, authority, income, government work, or a specific event.
There is no Antardasha, Pratyantardasha, or transit refinement, no exact-date prediction, and no LLM
date selection. The application preserves both canonical MD dates and a requested-horizon intersection
using `[start,end)` semantics; output precision is exclusively `BROAD_PERIOD`.

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
