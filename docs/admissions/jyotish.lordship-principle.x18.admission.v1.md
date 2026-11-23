# Principle admission record: X18 lordship principle (Period themes)

| Field | Value |
| --- | --- |
| Record ID | `jyotish.lordship-principle.x18.admission.v1` |
| Status | `ADMITTED` |
| Rule ID / version | `jyotish.lordship-principle.x18` @ `v1`, approving template `period-themes-v1` |
| Domain(s) | Career (Period themes) |
| Supersedes / superseded by | — |

## 1. Source
- Work: *Bṛhat Parāśara Horā Śāstra*, same edition and artifact as the other Part 0 records (SHA-256 `d333ebe1a4c6ab16ba2ed18bf87ea3d02966a393e2dc2c04d5ccdd9107a66108`).
- Section / verse: **none cited.** The packet records that no single verse stating the principle in general form was located in this edition. The reviewer cited no verse.
- Page images examined by reviewer: the reviewer has seen the review packet PDF (Part 0). Specific pages: not recorded.

## 2. Text
- Not applicable (no verse cited). The packet's X18 question and proposed template were approved as proposed.

## 3. Approved rule
- Principle: a Dasha lord may be described with the reviewed significations of itself and of the houses it rules and occupies (D1 Lagna, Whole Sign). Rahu and Ketu rule no sign, so only their occupied house is used.
- Dasha scope: **Mahadasha and Antardasha** (owner's record: "X18 scope: Mahadasha AND Antardasha"; the reviewer's statement: "Mahadasha and Antardasha are both good").
- Three-valued behaviour: with no admitted entry for a lord or its houses, no sentence (UNKNOWN, never "no themes").
- Modifiers explicitly **not** applied: strength, polarity, weighting, ranking.

## 4. Approved user-facing wording
- Template `period-themes-v1`, the packet's proposed wording, verbatim: "During your <Lord> <Mahadasha/Antardasha>, the reviewed significations associated with <Lord> (<terms>) and with the houses it rules and occupies (<house>: <terms>; …) are the themes the texts associate with this period. This does not predict an event or an outcome."
- The owner asked for a more natural rewrite. It was **not** adopted: it would be wording the reviewer did not approve, and its verb ("brings") is in the forbidden-word guard. The approved template is used unchanged.
- Placement: the Period-themes section follows the year glance, and the glance has one bullet listing each period's admitted terms.
- Required non-guarantee: the fixed closing sentence above.

## 5. Review

**General approval, recorded as given. Not an item-level review.**

| Field | Value (as given by the project owner) |
| --- | --- |
| Reviewer | Pandit ji (**full name pending**; open item) |
| Qualification | Acharya |
| Independent of the project? | not recorded |
| Date | 2026-11-23 |
| Channel | verbal, relayed by Atul, 2026-11-23 |
| Statement (verbatim, as relayed) | "All data points look good. The app is giving good calculation results. Mahadasha and Antardasha are both good, including their calculations and results. Proceed." |
| Packet seen | Reviewer has seen the review packet PDF (`research/next_dasha_01_review/review-packet.md`, Part 0). |
| Decision | **Approved as proposed** (general). |

| Role | Name | Qualification | Independent of the project? | Decision | Date |
| --- | --- | --- | --- | --- | --- |
| Sanskrit / source fidelity | Pandit ji (full name pending) | Acharya | not recorded | Approve: general, as proposed | 2026-11-23 |
| Jyotish methodology | Pandit ji (full name pending) | Acharya | not recorded | Approve: general, as proposed | 2026-11-23 |
| Wording / user-safety | Pandit ji (full name pending) | Acharya | not recorded | Approve: general, as proposed | 2026-11-23 |

The one general approval is recorded against each role, as the project owner instructed. The roles were not addressed separately.

- Reasons (per reviewer): not recorded beyond the statement above.
- Amendments made to the proposal: none given by the reviewer. 
- Approved as proposed; no item-level readings, OCR issues or translations individually addressed. The reviewer did not resolve any specific reading, OCR question or term. Where the packet asked a specific question (listed below), it remains as the packet proposed it, unanswered by the reviewer.
- Open questions deliberately left UNKNOWN: a source verse for the principle (none located or cited).

## 6. Calculation dependencies
- D1 (sidereal Lahiri, Whole Sign houses from the D1 Lagna, seven classical sign rulers); Vimshottari (365.25-day year) for Mahadasha and Antardasha; `jyotish.dasha_linkage.v1`.
- Status at signing (2026-11-23): CALC-01 internal checks pass; **CALC-02 independent numerical certification NO-GO** (unchanged). CALC-03 (`docs/validation/CALC-03-expert-check.md`) records the same reviewer's general confirmation of chart and Dasha calculations; it is not numerical certification.

## 7. Tests and release binding
- Test fixture IDs: MD and AD sentences for a synthetic Rahu MD / Saturn AD / Mercury AD year; Rahu occupied-house-only; placement after the glance; glance bullet citations.
- Test file(s): `apps/api/tests/test_part0_admission.py`, `apps/api/tests/test_period_themes.py`, `apps/api/tests/test_year_glance.py`; passing commit: the NEXT-ADMIT-01 feature commit on `next-admit-01` (see `git log -- apps/api/src/astrologer/knowledge/signification_part0b_v1.py`).
- Production release: `jyotish.signification.production@v1` (`apps/api/src/astrologer/knowledge/signification_part0b_v1.py`). Activation timestamp (UTC): not yet deployed; activation needs an owner-approved deploy.

## 8. Change history
| Date | Change | By |
| --- | --- | --- |
| 2026-11-23 | Record created from the project owner's expert record (NEXT-ADMIT-01) | AI preparer (not a reviewer), on owner instruction |
| (pending) | Reviewer's full name to be added | project owner |
