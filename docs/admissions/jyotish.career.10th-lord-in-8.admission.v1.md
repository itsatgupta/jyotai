# Rule admission record: 10th lord in the 8th (v.76), calculated match only

| Field | Value |
| --- | --- |
| Record ID | `jyotish.career.10th-lord-in-8.admission.v1` |
| Status | `ADMITTED` |
| Rule ID / version | `bphs.d1.house_lord.10.equals_8.v1` @ `v1` |
| Domain(s) | Career |
| Supersedes / superseded by | — |

## 1. Source
- Work, attribution: *Bṛhat Parāśara Horā Śāstra* (बृहत्पाराशरहोराशास्त्रम्), attributed to Parāśara.
- Edition: ed. (late) Gaṇeśadatta Pāṭhaka, with Hindi rendering; Sāvitrī Ṭhākura Prakāśana, Vārāṇasī; revised edition. Year: title verso OCR "२००९" (CE or Vikrama Saṃvat unconfirmed; not addressed at review).
- Artifact file + SHA-256: `पराशरहोराशास्त्र Brihat Parashar Hora Shastra _text.pdf` (repo root), `d333ebe1a4c6ab16ba2ed18bf87ea3d02966a393e2dc2c04d5ccdd9107a66108`.
- Section / verse / printed page / PDF page: भावेशफलाध्यायः, अथ कर्मेशभावफलम्, v.76; printed p. 195 = PDF p. 193. Packet item 0a-3.
- Page images examined by reviewer: the reviewer has seen the review packet PDF (Part 0). Specific pages examined and hash confirmation: not recorded.

## 2. Text
- Authenticated original (transcribed by reviewer from page image): not provided. The second line of the verse is marked **uncertain** in the packet and was **not** resolved by the reviewer.
- Variants / OCR corrections recorded: none confirmed. The packet's uncertain reading of line 2 stays uncertain.
- Approved translation: the preparer's draft translation (packet §0a-3), approved as proposed under the general approval. It is **not** reproduced here or in code, and is never shown to users.
- Edition's own rendering (if any) and agreement: not individually addressed.

## 3. Approved rule
- Formal condition: `jyotish.d1.house_lord.10.placement_house == 8`
- Reference point: D1 Lagna only.
- Dasha scope: not applicable (natal rule).
- Conventions relied on: Whole Sign houses from the D1 Lagna; seven classical sign rulers.
- Three-valued behaviour: UNKNOWN when the placement fact is unresolved; NO_MATCH (FALSE) for any other house; natal, `CONTEXTUAL` pending X11 (polarity), no polarity applied.
- Modifiers explicitly **not** applied: v.80 strength, polarity (X11), dimensions (X12).

## 4. Approved user-facing wording
- **Calculated match only.** The text's wording is withheld pending further review (project-owner decision, NEXT-ADMIT-01). The lifespan clause is never shown.
- The rule model requires a non-empty reviewed statement, and that model was **not** loosened. The statement is the owner-specified withheld notice, not the verse's content: "With the D1 tenth-house lord in the eighth house, a reviewed indication exists for this placement; its wording is withheld pending further review. This does not by itself establish a profession, promotion, income, or timing."
- Year glance: "a reviewed indication exists for this placement; its wording is withheld pending further review".
- Required non-guarantee statements: the final sentence of the statement above.
- Prohibited claims: any character, conduct, lifespan, health or outcome claim; any quotation or paraphrase of v.76.

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
- Amendments made to the proposal: none given by the reviewer. The withheld-wording treatment is the project owner's decision, not the reviewer's.
- Approved as proposed; no item-level readings, OCR issues or translations individually addressed. The reviewer did not resolve any specific reading, OCR question or term. Where the packet asked a specific question (listed below), it remains as the packet proposed it, unanswered by the reviewer.
- Open questions deliberately left UNKNOWN: the packet's choice between (a) admit with adverse wording withheld and (b) hold until X11 (the owner chose to admit with the wording withheld); the reading of line 2 (असदुक्ति / alpāyu): not addressed; user wording for v.76: withheld pending further review.

## 6. Calculation dependencies
- D1 (sidereal Lahiri, Whole Sign houses from the D1 Lagna, seven classical sign rulers).
- Status at signing (2026-11-23): CALC-01 internal checks pass; **CALC-02 independent numerical certification NO-GO** (unchanged). CALC-03 (`docs/validation/CALC-03-expert-check.md`) records the same reviewer's general confirmation of chart and Dasha calculations; it is not numerical certification.

## 7. Tests and release binding
- Test fixture IDs: T0a.3.1 (house 8, MATCH), T0a.3.2 (house 9, NO_MATCH); unresolved placement UNKNOWN; withheld-notice and no-lifespan-text checks; glance withheld clause.
- Test file(s): `apps/api/tests/test_part0_admission.py`, `apps/api/tests/test_year_glance.py`; passing commit: the NEXT-ADMIT-01 feature commit on `next-admit-01` (see `git log -- apps/api/src/astrologer/knowledge/career_part0_pack_v1.py`).
- Production release: `jyotish.production.cumulative@v11` (`apps/api/src/astrologer/knowledge/career_part0_pack_v1.py`). Activation timestamp (UTC): not yet deployed; activation needs an owner-approved deploy.

## 8. Change history
| Date | Change | By |
| --- | --- | --- |
| 2026-11-23 | Record created from the project owner's expert record (NEXT-ADMIT-01) | AI preparer (not a reviewer), on owner instruction |
| (pending) | Reviewer's full name to be added | project owner |
