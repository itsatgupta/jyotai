# Admission record: reviewer's Sitting 1 + 2 written verdicts (NEXT-ADMIT-02)

| Field | Value |
| --- | --- |
| Record ID | `jyotish.admit02.sitting-1-2.admission.v1` |
| Status | `ADMITTED` (items listed below); `HELD` / `PAUSED` (items listed below) |
| Reviewer | Pandit ji (full name pending), Acharya |
| Channel | written verdicts relayed by Atul, 2026-11-24 |
| Note | Admission instructed by the project owner; authorship of the written verdicts not independently confirmed. |
| Source of decisions | `research/prereview/pandit-ji-verdicts-2026-11-24.md` (verbatim, 820 lines, SHA-256 `52f58fe5f779d9ca57128d7ca9839f1c6bc77f05d502c06bd5533fd590f0ac32`) answering `research/prereview/pandit-ji-checklist.md` (two sittings) |
| Releases | static `jyotish.production.cumulative@v12` (`knowledge/admit02_pack_v1.py`); timing `jyotish.timing.production.career@v3` (`timing_rules/registry.py`); signification `jyotish.signification.production@v3` with X18 `jyotish.lordship-principle.x18@v2` (`knowledge/signification_admit02_v1.py`); weights `knowledge/rule_weights.py` |
| Supersedes | Nothing is edited. v11, timing v1/v2, signification v1/v2 and X18 v1 and their records stay unchanged; this record adds superseding records only. |

Every new review record in code carries: reviewer `Pandit ji (full name pending)`, the
qualification Acharya, the channel above, the note above, the verdict item it implements and
a pointer to this record (`admit02_notes` in `admit02_pack_v1.py`).

## Sitting 1: existing rules (items 1–24)

All 24 confirmed. Each confirmed rule keeps its id, version and condition and points to a new
interpretation record (`…interpretation.admit02`, version `admit02-v1`). Its statement is the
v11 statement byte for byte unless the verdict changes it.

| # | Rule | Verdict | Done | Weight |
| --- | --- | --- | --- | --- |
| 1 | Timing v.87, 10th lord in 4th, its Mahadasha | Confirm, change wording | Timing v3: "…described as rājya-pradāyinī: the combination is associated with authority, position, office or status-related results during the lord's Dasha, subject to the overall strength and condition of the 10th lord and the chart." Non-guarantee clause kept verbatim. | — |
| 2 | Timing v.140, Moon MD + Venus AD + Venus own/exalted | Confirm | Timing v3: rājya-lābha glossed "gain or benefit connected with authority, position or status". Condition unchanged and conjunctive. | — |
| 3 | 11th lord in 9th/10th (General) | Confirm, supporting factor | Wording unchanged | secondary |
| 4 | 10th lord in 4th/10th (Career) | Confirm, separate the two placements | Split into `…10.equals_4.v1` and `…10.equals_10.v1`, each with its own wording (below); `…10.in_4_or_10.v1` leaves the manifest | primary |
| 5 | 10th lord in 5th/11th | Confirm; extract the career layer | Career-relevant wording only (intelligence, creativity, counsel, decision-making, merit / gains, fulfilment, networks); children, contentment etc. dropped | primary |
| 6 | 10th lord in 6th/12th | Confirm; expand; not "bad career" | His 6th- and 12th-house lists, plus "it is not by itself an adverse career indication" | primary |
| 7 | 10th lord in 9th | Confirm; add dharma–karma | "read as a dharma–karma relationship…" plus his list; the text's themes kept | primary |
| 8 | 11th lord in 1st (Wealth) | Confirm | Unchanged | primary |
| 9 | 11th lord in 2nd/5th (Wealth) | Confirm | Unchanged (it never mentioned speculation) | primary |
| 10 | 11th lord in 9th/10th (Wealth) | Confirm | Unchanged | primary |
| 11 | 5th lord in 11th (Wealth) | Confirm | Unchanged | primary |
| 12 | 4th lord in 1st/7th (Education) | Confirm, supporting factor | Unchanged | secondary |
| 13 | 5th lord in 11th (Education) | Confirm | Unchanged | primary |
| 14 | 11th lord in 11th (Education) | Confirm; "poetic or literary" too specific | "scholarship and broader learning or intellectual accomplishment" | primary |
| 15 | 6th lord in 9th (Business) | Change: not a business yoga | "a secondary commercial/trade-related indication" | secondary |
| 16 | 5th lord in 11th (Children) | Confirm, supporting evidence | Unchanged | secondary |
| 17 | 11th lord in 2nd/5th (Children) | Confirm, secondary | Unchanged | secondary |
| 18 | 10th lord in 5th/11th (Children) | Do not admit as a Children rule; keep in the ledger, secondary/low | Leaves the manifest (never surfaced in Children answers); its passage and interpretation stay in the registry | secondary (ledger) |
| 19 | 10th lord in 4th/10th (Spirituality) | Confirm, supporting factor | Unchanged (not split: item 4 is the Career rule) | secondary |
| 20 | 10th lord in 9th (Spirituality) | Confirm | Unchanged | primary |
| 21 | 11th lord in 2nd/5th (Spirituality) | Confirm, low/medium weight | Unchanged | secondary |
| 22 | 11th lord in 9th/10th (Spirituality) | Confirm | Unchanged | primary |
| 23 | 6th lord in 2nd/10th (Travel) | Confirm; rename the category | Domain label shown as "Residence away from birthplace" (routing id stays `travel`); wording unchanged | primary |
| 24 | 10th lord in 9th (Friends) | Confirm as secondary | Unchanged | secondary |

Item 4 wording:

- 10th: "…This placement indicates a strong connection with profession, status and public
  activity. The text also associates the placement with knowledge, comfort, courage, devotion
  or worship, and dharmic and truth-oriented qualities. These do not by themselves establish a
  specific profession, promotion, income, or timing."
- 4th: "…This placement connects karma or profession with property, homeland, the
  institutional environment, public position, education or administration, depending on the
  rest of the chart. [same text and non-guarantee sentences]"

**Weights** (`rule_weights.py`) are display order only. A secondary rule is shown after the
primary ones, and its "why it applies" line is labelled "Supporting:". A weight is never a
score, a weighted sum or a ranking, and it never hides, inverts or combines a result. Rules
the verdicts do not weigh (Part 0, item 23) are primary. No Career rule is secondary.

## Sitting 1: open items 25–28

| # | Verdict | Done |
| --- | --- | --- |
| 25 P6 दशाशुभा | Provisionally "auspicious", pending scan/expert confirmation; not live on that inference | **Held** (not admitted) |
| 26 X2 weak/debilitated lord | Dignity is one strength factor, a modifier; never "debilitated = negative" | The rule lord's sign dignity (own / exaltation / debilitation, existing D1 facts) is shown as a calculated fact next to the rule: Career year answers (natal section), every other domain's "why it applies" line, and `DetailedEvidence.lord_dignity`. It never inverts, negates or changes a result (`application/lord_dignity.py`). UNKNOWN gives no line. |
| 27 X17 10th/11th lord in AD | MD primary, AD secondary, unless the source restricts | X18 v2 scope `MAHADASHA_PRIMARY_ANTARDASHA_SECONDARY`: Antardasha Period-themes lines are labelled "(secondary)"; a merged same-lord MD/AD line is not. The MD-only timing rule v.87 is never applied to an Antardasha (evaluator takes the Mahadasha only; tested). P1/P2 remain held. |
| 28 शत्रु | Use "adversaries/opposition/competition"; not a Career rule | Signification v3 restores the 6th-house entry as "adversaries, opposition, competition" (Period-themes term only; no natal Career rule uses it) |

## Sitting 2

| # | Verdict | Done |
| --- | --- | --- |
| 1 राजकुमारः | Change | "heir, successor or senior/deputy role" |
| 2 राज्य | Confirm | "authority or office" |
| 3 राजा | Confirm with change | "head, authority or governing role" |
| 4 सेना | Change | "forces, personnel or organized workforce" |
| 5 सचिवः | Confirm | "adviser or counsellor" |
| 6 भृत्य | Confirm | "employees or staff" |
| 7 नेता | Confirm | "leader" |
| 8 पराक्रमः | Confirm | "courage" (the proposal he confirmed; his aside "courage/initiative may be better" is not a changed verdict) |
| 9 विक्रम | Change slightly | "courage, initiative or enterprise" |
| 10 X18 compact form | Change wording, keep architecture | Template `period-themes-v2`: `<Lord> <period>[ (secondary)] (<span>): reviewed themes — <Lord>: <terms>; houses it rules and occupies: <house> (<terms>); …`. ONE closing at the end of the section: "These are the reviewed themes associated with this period; actual results depend on the full chart and other active factors." The v1 closing "This does not predict an event or an outcome." is removed from Period themes. |
| 11 P1 | Hold pending source | **Held** |
| 12 P2 | Hold until 13 | **Held** |
| 13 v.78 frame over v.79 | Must be resolved before P1/P2 | Open |
| 14 P3 | Hold, high priority | **Held** (v.89 stays candidate-only) |
| 15 P4 | Conditional yes, if text confirmed | **Held** pending source verification |
| 16 P5 | Confirm amendment: separate claims, both placements; not "śubha = good career" | **Held, not admitted.** The packet (`research/next_dasha_01_review/review-packet.md`, P5) has no reviewed user wording, only an unreviewed draft translation whose sole result is "auspicious" (śubha). Item 21 rules śubha a modifier that "should not itself trigger a Career prediction", so a v.85 Career claim built from the packet would rest on śubha alone. Admission needs reviewer-approved wording for each lord's Dasha. |
| 17 X1 | MD primary, AD secondary | As item 27 above |
| 18 X3 Lagna only | Confirm | Convention recorded in `docs/ASTROLOGY_METHOD.md` (already the engine's behaviour) |
| 19 X4 "joined" | Change wording | Convention recorded: "Joined = same sign, with no separate degree-orb requirement for rule matching." Project convention, not a universal classical law. |
| 20 X5 | Confirm approach | Sanskrit → controlled modern gloss → contextual interpretation (recorded) |
| 21 X6 | Mostly agree; śubha a modifier | Convention recorded: śubha is a modifier, never standalone evidence |
| 22 X7 | Confirm: separate internally | Existing behaviour (each rule is its own evidence item); recorded |
| 23 X8 | Change: not all Income | Convention recorded: वित्त → finances/resources/wealth, लाभ → gains/benefits, सम्पत् → prosperity/wealth/resources, राज्य/नृपाश्रय → authority/status/position; the question chooses the domain. No current rule uses वित्त or सम्पत्; the 11th-house लाभ display stays "gain". |
| 24 X9 dispositor | Calculated fact only | Convention recorded; no rule admitted |
| 25 X10 plain v.87, P1–P6 | Confirm; don't pre-write P1–P6 | v.87 uses the Sitting 1 item 1 wording; no P1–P6 text |
| 26 v.76 | Confirm neutral treatment | Unchanged: the 10th lord in the 8th stays withheld |
| 27 v.71 reading | Keep the printed reading | New passage record `bphs.bhavesha-phala.10th-lord.1.printed-reading` records कर्मेशाधिपतौ as printed; the 10th-lord-in-1st rule cites it (wording unchanged) |
| 28 v.76 second line | Confirm source-critical approach | Unchanged (withheld); the द्व reading and the अल्पायु discrepancy stay open, not normalized |
| 29 v.72 मद | Hold for source verification | **Paused** in production: `…10.in_2_3_or_7.v1` leaves the manifest; `…10.in_2_or_3.v1` keeps the 2nd/3rd wording ("second or third house" replaces "second, third or seventh house"; nothing else changed); `…10.equals_7.v1` states only "With the D1 tenth-house lord in the seventh house, a reviewed indication exists; wording pending source verification. This does not by itself establish a profession, promotion, income, or timing." The glance says "a reviewed indication exists; wording pending source verification". |
| 30 X18 source verse | Do not invent; label as a convention | X18 v2 `source_locator` and the evidence disclosure label: "Project interpretive convention, reviewer-approved; no source verse identified" |

## Held / paused (summary)

- **Held pending source verification:** P1, P2, P3, P4, P6 (and the v.78/v.79 frame question).
- **Held, cannot meet the verdict with the packet's wording:** P5.
- **Paused:** the 7th-house part of v.72 (मद).
- **Unchanged / withheld:** v.76 (10th lord in the 8th).

## Engineering choices recorded for review

1. Item 23's verdict names the category "Residence away from birthplace / foreign-place comfort
   indication". The owner's instruction is "Residence away from birthplace", which is used.
2. Item 4's 10th-house wording keeps his word "strong" ("a strong connection with
   profession…"). It describes the house connection, not chart strength; admitted text is
   exempt from the evaluative guard.
3. Signification entries with a changed gloss get a whole-entry v2 record under this review.
   Unchanged terms in the same entry (Mercury वाणी, Jupiter ज्ञानम्, 3rd उपदेश, 10th मान)
   keep their NEXT-ADMIT-01 display.
4. Items 6 and 7 add the reviewer's reading to the rule's wording. Where the verse's own themes
   are kept, they are introduced as "The text also associates…", so his reading is never
   attributed to the verse.

## Tests and release binding

- `apps/api/tests/test_admit02.py`: records, wording, split, paused 7th, ledger-only item 18,
  travel label, weights, timing v3 (v2 unchanged; MD-only rule never applied to the AD),
  glosses, शत्रु, X18 v2, dignity modifier, compact Period themes, held items.
- Benchmark v20 (`consultation_quality_v20_results.json`): every v19 count and gate is unchanged;
  new `admit02_counts`. v19 stays frozen.

## Change history

| Date | Change | By |
| --- | --- | --- |
| 2026-11-24 | Record created (NEXT-ADMIT-02) | AI preparer (not a reviewer), on owner instruction |
