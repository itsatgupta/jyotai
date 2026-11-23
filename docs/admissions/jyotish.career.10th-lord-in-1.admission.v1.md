# Rule admission record: 10th lord in the 1st (v.71)

| Field | Value |
| --- | --- |
| Record ID | `jyotish.career.10th-lord-in-1.admission.v1` |
| Status | `ADMITTED` |
| Rule ID / version | `bphs.d1.house_lord.10.equals_1.v1` @ `v1` |
| Domain(s) | Career |
| Supersedes / superseded by | — |

## 1. Source
- Work, attribution: *Bṛhat Parāśara Horā Śāstra* (बृहत्पाराशरहोराशास्त्रम्), attributed to Parāśara.
- Edition: ed. (late) Gaṇeśadatta Pāṭhaka, with Hindi rendering; Sāvitrī Ṭhākura Prakāśana, Vārāṇasī; revised edition. Year: title verso OCR "२००९" (CE or Vikrama Saṃvat unconfirmed; not addressed at review).
- Artifact file + SHA-256: `पराशरहोराशास्त्र Brihat Parashar Hora Shastra _text.pdf` (repo root), `d333ebe1a4c6ab16ba2ed18bf87ea3d02966a393e2dc2c04d5ccdd9107a66108`.
- Section / verse / printed page / PDF page: भावेशफलाध्यायः, अथ कर्मेशभावफलम्, v.71; printed p. 195 = PDF p. 193. Packet item 0a-1.
- Page images examined by reviewer: the reviewer has seen the review packet PDF (Part 0). Specific pages examined and hash confirmation: not recorded.

## 2. Text
- Authenticated original (transcribed by reviewer from page image): not provided. The packet's OCR text and the preparer's probable reading (packet §0a-1) were approved as proposed, not individually confirmed.
- Variants / OCR corrections recorded: the packet's OCR verse number "७९" (read as 71) and the probable reading कर्माधिपतौ for OCR "कर्मेशाधिपतौ". Neither was individually addressed.
- Approved translation: the preparer's draft translation (packet §0a-1), approved as proposed.
- Edition's own rendering (if any) and agreement: the edition's Hindi on PDF p. 193, as the preparer read it (packet §0a-1). Agreement not individually addressed.

## 3. Approved rule
- Formal condition: `jyotish.d1.house_lord.10.placement_house == 1`
- Reference point: D1 Lagna only.
- Dasha scope: not applicable (natal rule).
- Conventions relied on: Whole Sign houses from the D1 Lagna; seven classical sign rulers.
- Three-valued behaviour: UNKNOWN when the 10th-lord placement fact is unresolved; NO_MATCH (FALSE) for any other house; natal, `CONTEXTUAL`, no polarity.
- Modifiers explicitly **not** applied: v.80 strength, polarity (X11), dimensions (X12).

## 4. Approved user-facing wording
- Exact `permitted_wording` (packet §0a-1 proposed wording, verbatim): "With the D1 tenth-house lord in the first house, this is contextual evidence for career matters. The text associates this placement with poetic or literary ability, more comfort later in life, and wealth that grows over time. These broader life themes do not by themselves establish a profession, promotion, income, or timing."
- Required non-guarantee statements: the final sentence above.
- Prohibited claims: profession, promotion, income, timing; the childhood-illness clause is left out of user wording (health, high-stakes), as proposed.

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
- Open questions deliberately left UNKNOWN: the packet's questions on leaving out the childhood-illness clause (kept as proposed: left out) and on the reading कर्माधिपतौ (not addressed).

## 6. Calculation dependencies
- D1 (sidereal Lahiri, Whole Sign houses from the D1 Lagna, seven classical sign rulers).
- Status at signing (2026-11-23): CALC-01 internal checks pass; **CALC-02 independent numerical certification NO-GO** (unchanged). CALC-03 (`docs/validation/CALC-03-expert-check.md`) records the same reviewer's general confirmation of chart and Dasha calculations; it is not numerical certification.

## 7. Tests and release binding
- Test fixture IDs: T0a.1.1 (house 1, MATCH), T0a.1.2 (house 10, NO_MATCH), T0a.1.3 (unresolved, UNKNOWN); every resolvable house 1–12 has exactly one natal Career rule.
- Test file(s): `apps/api/tests/test_part0_admission.py`, `apps/api/tests/test_interpretation_evidence.py`, `apps/api/tests/test_career_consultation.py`; passing commit: the NEXT-ADMIT-01 feature commit on `next-admit-01` (see `git log -- apps/api/src/astrologer/knowledge/career_part0_pack_v1.py`).
- Production release: `jyotish.production.cumulative@v11` (`apps/api/src/astrologer/knowledge/career_part0_pack_v1.py`). Activation timestamp (UTC): not yet deployed; activation needs an owner-approved deploy.

## 8. Change history
| Date | Change | By |
| --- | --- | --- |
| 2026-11-23 | Record created from the project owner's expert record (NEXT-ADMIT-01) | AI preparer (not a reviewer), on owner instruction |
| (pending) | Reviewer's full name to be added | project owner |
