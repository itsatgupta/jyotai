# Rule admission record — TEMPLATE

> Copy this file per admitted rule as `docs/admissions/<record-id>.md`. Once signed, the record
> is **immutable**: changes require a new record that supersedes it. A rule may enter a
> production release only if a signed record with status `ADMITTED` exists for its exact
> rule ID and version.

| Field | Value |
| --- | --- |
| Record ID | `jyotish.<domain>.<rule-slug>.admission.v<N>` |
| Status | `DRAFT` · `ADMITTED` · `REJECTED` · `SUPERSEDED` |
| Rule ID / version | `<rule_id>` @ `<version>` |
| Domain(s) | Career · Wealth · … (as approved; no others) |
| Supersedes / superseded by | — |

## 1. Source
- Work, attribution:
- Edition (editor, publisher, place, year):
- Artifact file + SHA-256:
- Section / verse / printed page / PDF page:
- Page images examined by reviewer (pages, hash confirmed Y/N):

## 2. Text
- Authenticated original (transcribed by reviewer from page image):
- Variants / OCR corrections recorded:
- Approved translation:
- Edition's own rendering (if any) and agreement:

## 3. Approved rule
- Formal condition (in fact IDs only, e.g. `jyotish.d1.house_lord.9.placement_house == 10`):
- Reference point (e.g. D1 Lagna only):
- Dasha scope: MD only · MD and AD · other:
- Conventions relied on (houses, rulers, conjunction, aspects):
- Three-valued behaviour: when UNKNOWN, when NO_MATCH, when not applicable:
- Modifiers explicitly **not** applied (e.g. v.80 strength):

## 4. Approved user-facing wording
- Exact `permitted_wording` (verbatim; code must match byte-for-byte):
- Required non-guarantee statements:
- Prohibited claims (dates, amounts, promotion, diagnosis, …):

## 5. Review
| Role | Name | Qualification | Independent of the project? | Decision | Date |
| --- | --- | --- | --- | --- | --- |
| Sanskrit / source fidelity | | | Y/N | Approve / Reject / Amend | |
| Jyotish methodology | | | Y/N | | |
| Wording / user-safety | | | Y/N | | |

- Reasons (per reviewer):
- Amendments made to the proposal:
- Open questions deliberately left UNKNOWN:

## 6. Calculation dependencies
- Calculations used (D1, Vimshottari, …) and their validation status. **As of 2026-11-23:
  CALC-01 internal checks pass; CALC-02 independent certification NO-GO.** Record the
  status current at signing.

## 7. Tests and release binding
- Test fixture IDs (MATCH / NO_MATCH / UNKNOWN / edge cases, one per reviewed case):
- Test file(s) and passing commit SHA:
- Production release ID / version that binds this record, and activation timestamp (UTC):

## 8. Change history
| Date | Change | By |
| --- | --- | --- |
| | Record created | |
