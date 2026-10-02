# Astrology Methodology

## Initial configuration

The MVP starts with:

- Vedic/Jyotish
- Sidereal zodiac
- Lahiri ayanamsa
- Vimshottari Dasha

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

### Task 10 deterministic context composition

Task 10 composes existing deterministic outputs for one explicit as-of instant:
D1, D9, D10, active Vimshottari Mahadasha/Antardasha, Jupiter/Saturn/true
Rahu/Ketu transit positions, and Task 09A D1 facts. It adds no interpretive
methodology. D2 remains available through the chart API but is intentionally
outside context-v1; Task 09A facts remain D1-only.

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
