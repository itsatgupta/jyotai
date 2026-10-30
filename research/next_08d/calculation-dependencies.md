# Calculation gap assessment

The current stack is `sidereal` / Lahiri, Whole Sign D1, and Parashari D9. [CALC-01](/Users/atul/projects/ai-astrologer-codex-starter/docs/CALC01_VERIFICATION.md) internally verifies selected invariants only; no full chart or D9 result is independently certified. The research probe uses the current PySwissEph 2.10.3.2 binding, Swiss 2.10.03 library and Moshier internal ephemeris. It is a reproduction of current behavior, not a reference oracle.

| Candidate input | Existing deterministic supply | Exact gap |
| --- | --- | --- |
| D1 Lagna, Moon and Sun signs | `ChartEngine` supplies all three with unrounded sidereal longitudes and provenance. | No independent CALC-02 comparison for complete synthetic charts. Birth-time uncertainty is not represented as a range. |
| Relative strength of Lagna, Moon and Sun | D1 derived facts provide selected structural dignity booleans for planets. | No comparable Lagna/Moon/Sun score or approved selector. Shadbala is explicitly deferred in `derived_facts.py`. Lagna is a point/house, so a shared comparator cannot be presumed from planetary dignity. Source-specific strength meaning, comparison units and tie tolerance need expert approval. |
| Tenth from selected reference | `ChartEngine` supplies Whole Sign houses from Lagna only. The signs of Moon/Sun are available, and research can compute a sign offset. | No versioned tenth-from-arbitrary-reference fact or reviewed convention for whether this verse intends sign-based tenth, bhava cusp, or another convention. Do not reuse Lagna's `house.10` for Moon/Sun. |
| Tenth lord and D1 placement | D1 derived facts expose sign rulers and lord placement for Lagna-anchored houses; `SIGN_RULERS` maps seven classical planets. | A selected Moon/Sun-relative tenth needs its own sign-ruler projection with explicit provenance. Nodes are not modeled as sign owners. |
| Tenth lord's navamsa and navamsa ruler | `VargaEngine` derives the Parashari D9 sign from unrounded D1 longitude; D9 fact service exposes each planet's sign. | D9 sign **ruler** is not an emitted D9 fact. Research probe derives it using D1's classical `SIGN_RULERS`; source-compatible ownership and navamsa mapping still need review and CALC-02 comparison. D9 house placement is not a substitute for the D9 sign occupied by the D1 tenth lord. |
| Verse 5.9 strength and place | Some D1 aspect booleans exist. | Navamsa-ruler strength, source-specific sign aspect/occupancy semantics, fixed sign check, and historical `own country` meaning are not a validated contract. This clause is outside candidate output. |
| Birth-time uncertainty | A single exact local timestamp is normalized; ambiguous/nonexistent civil times are rejected. | No interval input, stability sweep or withholding rule when Lagna or relevant D9 sign changes across plausible times. Historical IANA timezone database is unpinned. |

## CALC-02 focused dependencies

1. Obtain independent, settings-matched reference outputs for the existing six synthetic CALC-01 profiles, including ascendant and seven classical longitudes, D1 signs and D9 signs. Record source, version, data files/kernel, coordinates, time scale, Lahiri definition, house convention, D9 variant, hash, tolerance and observed differences.
2. Add independent boundary checks for tenth-from-Moon/Sun sign counting and the selected tenth lord's D9 sign, including exact half-open navamsa boundaries and sign wrap. These checks can precede any production implementation.
3. Have a Sanskrit/Jyotish reviewer decide the house and navamsa conventions actually required by PD 5.1 before asserting source compatibility. Current implementation follows project conventions, which are not independently proven to be the historical author's conventions.
4. Define and approve a *comparable* Lagna/Moon/Sun strength method, including unknowns and ties. Implement and validate it as a later calculation increment; do not derive it from current dignity booleans or invent a score here.
5. Specify birth-time uncertainty input and a deterministic stability check for the selected reference, tenth lord and D9 sign. Withhold interpretation when any required branch changes within the documented input interval.

The full candidate cannot execute today. A D1/D9 projection is available for reviewer demonstration, but selection and source-compatible mapping remain unresolved.
