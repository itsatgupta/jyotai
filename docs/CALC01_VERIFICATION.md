# CALC-01 calculation verification record

**Status: INTERNAL_VERIFIED for the added invariants; EXTERNAL_COMPARISON_UNRESOLVED
for two archived AstroSage Moon values; REFERENCE_UNAVAILABLE for six complete
synthetic chart candidates. No complete chart is INDEPENDENT_VERIFIED.**

This record applies to commit `3ce1c68e19b59bd28e8719436dac22cc3077dbb9`
before the CALC-01 changes. It verifies calculation behavior, not astrological
predictive accuracy. The new runner and fixtures live only under `apps/api/tests`.
No production calculation engine, interpretation rule, or provider interface was
changed.

## Current calculation contract

| Component | Observed implementation |
| --- | --- |
| Ephemeris | PySwissEph 2.10.3.2 binding, Swiss Ephemeris 2.10.03 native library. `calc_ut` uses `FLG_SIDEREAL | FLG_SPEED`; current returned source flags identify the Moshier internal ephemeris. No `.se1`, `.se2`, `.bsp`, or `.eph` file is present in the repository; no data-file version/hash is recorded. |
| Frame | Geocentric apparent ecliptic positions; Gregorian UTC-to-Julian-day conversion. Sidereal zodiac with Swiss `SIDM_LAHIRI`. True north node (`TRUE_NODE`) is Rahu; Ketu is exactly `(Rahu + 180°) mod 360`. |
| Ascendant and houses | Swiss `houses_ex(..., b"W", FLG_SIDEREAL)` supplies the ascendant longitude. The `W` call is used for the ascendant only; D1 houses are subsequently built as Whole Sign houses anchored to the ascendant sign. A body's house is its sign offset from that anchor plus one. Existing `SIGN_RULERS` identifies classical house lords; nodes do not rule signs. |
| D1 facts | Nine bodies/points, sidereal sign, degree in sign, nakshatra and pada from unrounded longitude; speed below zero means retrograde. Signs are 30° half-open intervals; nakshatras are 13°20′ half-open intervals. |
| D9 and D10 | Parashari Navamsa, factor 9: movable signs start in self, fixed in ninth, dual in fifth. Parashari Dasamsa, factor 10: odd signs start in self and even signs in ninth. Both advance one sign per division and map source degree `d` to `(d × factor) mod 30°`. Their longitudes are derived divisional coordinates, not ephemeris positions. Whole Sign varga houses use the derived varga ascendant. |
| Vimshottari | `vimshottari-v1` takes the D1 Moon. Nine lords repeat through 27 nakshatras: Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury; durations 7, 20, 6, 10, 7, 18, 16, 19, 17 years. Birth balance is the untraversed fraction of the Moon's nakshatra times its lord's full duration. A year is exactly 365.25 days. Decimal arithmetic rounds fractional microseconds half-even. Antardasha durations use the parent duration times child years / 120, with cumulative boundaries and the last child ending exactly with the parent. All intervals are UTC and half-open `[start, end)`. |
| Birth time and coordinates | A local date/time, IANA time zone, latitude and longitude are retained. `zoneinfo` converts to UTC and rejects ambiguous/nonexistent local times. Latitude/longitude feed the ascendant, while the configured planets are geocentric. The system IANA time-zone database is used; no `tzdata` Python package or time-zone database version is pinned. Historical conversion is therefore an identified reproducibility dependency. |

The source contract is in `apps/api/src/astrologer/astrology/{swiss_ephemeris,chart,vargas,dasha,derived_facts}.py`,
`apps/api/src/astrologer/birth/models.py`, and `docs/CALCULATION_CONVENTIONS.md`.
The provider's existing metadata has `ephemeris_data_hash = null` for Moshier.

## Reference-source inventory and evidence grades

| Source | Provenance and settings | Use and grade |
| --- | --- | --- |
| Installed Swiss Ephemeris called directly in existing tests | Same PySwissEph/native library and Moshier implementation as the adapter | Adapter and invariant checks only: `INTERNAL_VERIFIED`; it cannot independently certify positions. |
| `docs/VALIDATION_REPORT.md` AstroSage Benchmarks 1 and 2 | Archived displayed values for two Meerut births; original calculator artifact, precise birth coordinates, software version, all flags, node setting, and Dasha year convention are absent | Two Moon values can be screened numerically. `EXTERNAL_COMPARISON_UNRESOLVED`; the archived ascendants and Dasha statements cannot be reproduced as full comparisons. The report's causal phrase “methodology difference” is unproven without settings and exact boundary dates. |
| [NASA/JPL Horizons API documentation](https://ssd-api.jpl.nasa.gov/doc/horizons.html) | Independent astronomical service with documented observer center, UTC time, quantities, output format, and source identification | Candidate for independent *tropical* geocentric planetary checks after frame/time-scale matching; not, by itself, a Lahiri sidereal, node, ascendant, varga, or Dasha reference. No result was imported into CALC-01. |
| [Swiss Ephemeris programming documentation](https://www.astro.com/swisseph-download/doc/swephprg.pdf) | Provider flag and fallback documentation | Explains the existing implementation; not an independent numerical source. |
| Six synthetic profiles below | Fully specified input, but no external output/source yet | `REFERENCE_UNAVAILABLE`. Internal engine results and perturbations are observations, not fixture expectations. |

The archived report's “PASS WITH DOCUMENTED METHODOLOGY DIFFERENCES” and
“independent comparisons” labels are not CALC-01 verification grades. Missing
source artifacts and settings leave those comparisons unresolved.

## Fixture candidates

All six use the existing sidereal Lahiri, true node, Whole Sign, Parashari
D9/D10, `vimshottari-v1` profile. `tests/fixtures/calc01_profiles.json`
records the inputs, expected UTC conversion, status, and empty reference values.
The fixture schema reserves source/version, data and settings provenance,
artifact hash, and tolerances for a future real reference. The boundary candidates were
selected by scanning the current engine;
this selection is internal and supplies no expected astronomical value.

| ID | Local birth time and IANA zone | Latitude, longitude | UTC |
| --- | --- | --- | --- |
| `india_ordinary` | 1990-01-15 09:30:00 Asia/Kolkata | 19.076, 72.8777 | 1990-01-15 04:00:00Z |
| `dst_new_york` | 2024-07-01 12:00:00 America/New_York | 40.7128, -74.006 | 2024-07-01 16:00:00Z |
| `ascendant_sign_boundary` | 2000-01-01 13:12:00 Asia/Kolkata | 19.076, 72.8777 | 2000-01-01 07:42:00Z |
| `moon_nakshatra_boundary` | 2000-01-15 18:34:00 Asia/Kolkata | 19.076, 72.8777 | 2000-01-15 13:04:00Z |
| `southern_hemisphere` | 2001-08-12 09:45:00 Australia/Sydney | -33.8688, 151.2093 | 2001-08-11 23:45:00Z |
| `historical_kolkata_lmt` | 1900-01-15 09:30:00 Asia/Kolkata | 22.5726, 88.3639 | 1900-01-15 04:08:50Z |

The historical profile uses the system database's then-applicable +05:21:10
offset. This is a time-zone conversion test candidate, not a historical birth
record. For each candidate, Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn,
Rahu, Ketu, ascendant, sign, house, house lord, D9/D10, and Dasha reference
comparisons remain **unresolved**: expected value and numerical difference are
unavailable, so no tolerance or pass result is asserted.

## Numerical comparison results

The following are **archived external screening comparisons only**. The
AstroSage values are copied from `docs/VALIDATION_REPORT.md`; decimal degrees
are direct sexagesimal conversions. The UTC instants assume the archived Meerut
local times used Indian standard time; original input records are unavailable.
The 1″ screening threshold tests agreement at roughly the precision of the
archived whole-arcsecond display. This is a retrospective comparison of
already reported differences, not a pre-registered accuracy benchmark.
Differences use the shortest
signed angular separation, including 0°/360° wraparound. All actual values
below are current Swiss/Moshier results.

| Input UTC and field | Archived expected | Actual | Actual − expected | Tolerance | Numerical screen | Evidence status |
| --- | --- | ---: | ---: | ---: | --- | --- |
| 1975-04-12 17:00Z Moon | Aries 10°08′44″ = 10.145555556° | 10.151085550° | +19.90798″ | 1″ | fail | `EXTERNAL_COMPARISON_UNRESOLVED` |
| 2007-05-14 12:20Z Moon | Pisces 26°58′30″ = 356.975000000° | 356.984919157° | +35.70897″ | 1″ | fail | `EXTERNAL_COMPARISON_UNRESOLVED` |

The archived ascendant differences of +16.7″ and +14.903″ are not retested:
their exact input coordinates are missing. No assumption about those
coordinates is inserted into a fixture. There are no independently sourced
expected Sun/Mercury/Venus/Mars/Jupiter/Saturn/Rahu/Ketu, house, or house-lord
values. Ketu opposition and house/lord mapping are currently internal
invariants only.

## Dasha comparison and internal interval checks

The archived report records birth lords Ketu and Mercury and active chains
Rahu/Saturn and Venus/Rahu at 2026-10-02, but supplies no exact AstroSage
Mahadasha/Antardasha boundary timestamps. Its actual boundary gaps cannot be
quantified or attributed to ayanamsa, Moon longitude,
year convention, time zone, or rounding from the available evidence. Status:
`EXTERNAL_COMPARISON_UNRESOLVED`.

A bounded counterfactual isolates the archived Moon gaps under **JyotAI's own**
365.25-day-year formula: substituting AstroSage's displayed Moon while holding
the birth lord and every other v1 convention fixed would move the first
Mahadasha end later by 1.060410978 days (1975 Ketu case) and 4.619289604 days
(2007 Mercury case). These are arithmetic sensitivities, not AstroSage
boundary predictions or a demonstrated explanation. The actual AstroSage
boundary dates and year convention are needed before attributing any gap.

Internal tests cover all 27 nakshatra-to-lord positions, exact synthetic
nakshatra edges, full 120-year sequence, birth balance, each Antardasha's
ordering, UTC boundaries, cumulative duration, continuity, and `[start, end)`
lookup. CALC-01 adds a live-chart check across its generated timeline and its
birth-time boundary case. This is `INTERNAL_VERIFIED`, not an independent
Dasha reference. In the boundary candidate, a -5 minute shift gives Ashwini,
Ketu, and first Mahadasha end **2000-01-23 18:14:32.897728Z**; at supplied
time the Moon is Bharani, Venus, with first end **2020-01-12
10:25:16.296132Z**. These are engine outputs, with no external expected dates.

## Birth-time sensitivity observations

Run `cd apps/api && uv run python tests/calc01_report.py` to reproduce all
five snapshots per candidate, including numerical longitudes, D1/D9/D10
changed-body and house-lord lists, birth Mahadasha balance in integer microseconds, and UTC
Mahadasha/Antardasha ends. The table orders offsets as **-15/-5/0/+5/+15
minutes**, relative to the supplied UTC instant. Results are factual internal
observations. They do not rectify a birth time or attach meanings to changes.

| Candidate | D1 ascendant signs | Moon nakshatra | Birth Mahadasha lord | Notable changed facts |
| --- | --- | --- | --- | --- |
| India ordinary | Aquarius/Aquarius/Aquarius/Aquarius/Aquarius | Purva Phalguni throughout | Venus throughout | D1 sign/house unchanged; D9 and D10 ascendant signs and Whole Sign house assignments vary. |
| New York DST | Leo/Virgo/Virgo/Virgo/Virgo | Bharani throughout | Venus throughout | D1 houses change at -15 minutes; D9/D10 ascendant and houses vary. |
| Ascendant boundary | Pisces/Pisces/Pisces/Aries/Aries | Swati throughout | Rahu throughout | All nine D1 body house numbers and 11 of 12 house-lord identities change at +5/+15 minutes because the ascendant sign changes. D1 body signs do not. |
| Moon boundary | Cancer throughout | Ashwini/Ashwini/Bharani/Bharani/Bharani | Ketu/Ketu/Venus/Venus/Venus | Moon D9 sign changes across the boundary; Mars D10 sign changes at +15 minutes. D1 body signs and house numbers remain stable. |
| Southern hemisphere | Virgo/Libra/Libra/Libra/Libra | Bharani throughout | Venus throughout | D1 houses change at -15 minutes; varga ascendants/houses vary. |
| Historical Kolkata | Aquarius/Aquarius/Pisces/Pisces/Pisces | Punarvasu throughout | Jupiter throughout | D1 houses change at -15/-5 minutes; varga ascendants/houses vary. |

Every nonzero offset in the 30-run matrix changes the Moon longitude and first
Mahadasha balance/end relative to its baseline. The first Antardasha boundary
also changes. Planetary D1 signs
remain the same across all sampled perturbations; D1 house facts change when
the ascendant sign changes. D9 planet signs change only for the Moon in the
Moon-boundary candidate at -15/-5 minutes; D10 planet signs change only for
Mars in that candidate at +15 minutes. Other reported varga house changes
arise from movement of the varga ascendant. The runner retains the full
per-offset output so these statements can be checked without adding an API.

## D9/D10 and release status

The existing tests cover representative starts, sign wrap, and selected exact
edges. CALC-01 adds tests for exact representable 10°/20° D9 edges and every
3° D10 edge in all 12 source signs. These establish internal mapping behavior
only. No genuine independent D9/D10 reference chart with matching variant and
fully specified birth inputs was found, so D9/D10 remain unverified against an
external chart. No divisional interpretation is activated.

CALC-01 independent release blockers are: complete independent reference
outputs and their exact software/data/settings provenance; exact AstroSage
input artifacts and boundary dates if that discrepancy is to be diagnosed;
external Swiss data-file provenance/hash if data files are adopted; and a
pinned/reproducible historical IANA time-zone source. Existing ephemeris
production-license clearance remains a separate documented deployment gate.

**Next increment:** acquire legally reusable, timestamped outputs for these
six synthetic inputs from a genuinely separate calculation source. Record its
version, ephemeris data/kernel, coordinate origin, apparent/astrometric frame,
time scale, Lahiri definition, node choice, ascendant method, house system,
D9/D10 variant, Dasha year and rounding policy, then populate expected values
and predeclare tolerances. Compare each field with angular wraparound and
report every numeric difference. Preserve unresolved statuses where settings
cannot be matched. A JPL Horizons tropical comparison can independently
check part of the planetary layer but cannot alone certify the Jyotish
transforms or Dasha timeline.

## Validation execution

From `apps/api` on this working tree:

- `uv run pytest -q tests/test_calc01_verification.py` — 10 passed.
- `uv run ruff check .` — passed.
- `uv run mypy src` — passed, 80 source files.
- `uv run pytest -q` — 513 passed, 1 Starlette `httpx` deprecation warning.
- `uv run pytest -q tests/test_analyze_api.py::test_senior_provider_packet_contains_only_governed_display_evidence` — 1 passed; provider packet privacy contract retained.
- `uv run python tests/calc01_report.py` — generated the 30 internal sensitivity snapshots.
