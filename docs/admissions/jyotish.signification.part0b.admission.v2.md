# Signification admission record v2: packet 0b terms, शत्रु removed

| Field | Value |
| --- | --- |
| Record ID | `jyotish.signification.part0b.admission.v2` |
| Status | `ADMITTED` |
| Rule ID / version | `bphs.signification.graha.<graha>` (9 entries) and `bphs.signification.bhava.<n>` (9 entries) @ `v1`, released as `jyotish.signification.production@v2` |
| Domain(s) | Career (Period themes) |
| Supersedes / superseded by | Supersedes `jyotish.signification.part0b.admission.v1`. That record is not edited. |

## Change from v1

**Removed:** the 6th-house entry `bphs.signification.bhava.6@v1`. Its only term was शत्रु
("adversaries").

**Why:** in the review packet (`research/next_dasha_01_review/review-packet.md`, Bhavas
table), the 6th-house row proposes शत्रु only conditionally. The row reads, verbatim:

> `| 6 | v.6 (147) | मातुल, अन्तकशङ्का, शत्रु, व्रण, सपत्नीमातृ | maternal uncle, fear of death, enemies, wounds, stepmother | शत्रु, as "adversaries" (reviewer to confirm Career use) | ________ |`

The general approval recorded in v1 ("approved as proposed"; statement as relayed: "All data
points look good. The app is giving good calculation results. Mahadasha and Antardasha are
both good, including their calculations and results. Proceed.") did **not** confirm the
Career use of शत्रु. v1 included it by project-owner decision. On 2026-11-23 (NEXT-SIG-02) the
project owner reversed that decision, and the term is removed until a reviewer confirms it.

**Effect:** the 6th house has no admitted entry. A period lord that rules or occupies the 6th
house gets no 6th-house text in Period themes (UNKNOWN, never "no themes"). No other entry,
term, display or the X18 record changes; v2 is v1 minus exactly this entry.

## Unchanged from v1

Sections 1–4 and 6 of v1 (source, text, kept terms other than the 6th house, exclusions,
wording, calculation dependencies) and its review record (reviewer "Pandit ji", full name
pending; Acharya; independence not recorded; verbal, relayed by Atul, 2026-11-23; approved as
proposed; no item-level readings, OCR issues or translations individually addressed) apply
unchanged.

## Open item for the reviewer

- **6th house, शत्रु ("adversaries"):** confirm or reject its Career use. If confirmed, a new
  record (v3) may restore the entry.

## Tests and release binding

- `apps/api/tests/test_part0_admission.py`: `test_v2_removes_shatru_and_keeps_v1_hash_pinned`
  (v2 = v1 minus the 6th-house entry; v1 manifest hash `bb3aae6b…19bfa6` pinned) and
  `test_a_sixth_house_period_shows_no_shatru_or_adversaries` (synthetic Mercury Mahadasha
  ruling the 6th house, 2028).
- Benchmark v15 (`consultation_quality_v15_results.json`): identical to v14 except the recorded
  corpus version.
- Release: `jyotish.signification.production@v2`
  (`apps/api/src/astrologer/knowledge/signification_part0b_v1.py`). The historical v1 manifest is
  `SIGNIFICATION_MANIFEST_V1`.

## Change history

| Date | Change | By |
| --- | --- | --- |
| 2026-11-23 | Record created; शत्रु removed (NEXT-SIG-02) | AI preparer (not a reviewer), on owner instruction |
