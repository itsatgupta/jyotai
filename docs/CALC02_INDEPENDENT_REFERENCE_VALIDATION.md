# CALC-02 independent reference validation

**Acquisition date:** 2026-10-30. **Baseline:** `1927f908b1ac6186dbf9ce3c1be7e31cbe863002` on `main`. **Result:** no new independent numerical output was obtainable. No D1, D9, D10, or Dasha component is `INDEPENDENT_VERIFIED`. This record concerns calculated values, not the separate review required for Jyotish interpretation or real-world prediction.

## Reused inputs and calculation contract

CALC-01's six synthetic inputs remain in `apps/api/tests/fixtures/calc01_profiles.json`; no new input or expected value was created. The first two acquisition targets were:

| ID | Local input and zone | Latitude, longitude | UTC instant |
| --- | --- | --- | --- |
| `india_ordinary` | 1990-01-15 09:30:00, Asia/Kolkata | 19.076, 72.8777 | 1990-01-15 04:00:00Z |
| `dst_new_york` | 2024-07-01 12:00:00, America/New_York | 40.7128, -74.006 | 2024-07-01 16:00:00Z |

The other four remain `ascendant_sign_boundary`, `moon_nakshatra_boundary`, `southern_hemisphere`, and `historical_kolkata_lmt`, with inputs and UTC instants documented in [CALC-01](CALC01_VERIFICATION.md). The current calculation contract is PySwissEph 2.10.3.2 / Swiss Ephemeris 2.10.03 with returned Moshier internal ephemeris flags, geocentric apparent positions, sidereal Lahiri (`SIDM_LAHIRI`), true north node, Whole Sign D1 houses, Parashari D9 and D10 variants, and `vimshottari-v1`. The Dasha year is exactly 365.25 days; intervals are UTC and half-open `[start, end)`. No convention was adjusted for a candidate source.

## Reference acquisition and provenance

| Candidate | Fields and settings available | Acquisition result and evidence grade |
| --- | --- | --- |
| [NASA/JPL Horizons API](https://ssd-api.jpl.nasa.gov/doc/horizons.html) and [manual](https://ssd.jpl.nasa.gov/horizons/manual.html) | API version 1.3 (2025 June); Horizons manual version 4.98e (2026-08-25). Documented observer table can request target 10 (Sun), center `500@399` (Earth geocenter), `TIME_TYPE=UT`, Gregorian calendar, `TLIST`, and quantity 31 (`ObsEcLon`, apparent IAU76/80 ecliptic-of-date longitude in degrees). The API documentation and manual were accessible. | A single Sun request for `india_ordinary` was attempted with the exact UTC instant, in the sandbox and then through the required escalation path. Both returned `curl: (6) Could not resolve host: ssd.jpl.nasa.gov`. No result, kernel/data version, EOP file identifier, numerical precision, or output artifact was acquired. `REFERENCE_UNAVAILABLE` for both target profiles. No further calls were made. The API documentation describes a possible independent **tropical planetary** comparison only; it cannot certify sidereal Lahiri, true nodes, houses, vargas, or Dasha. |
| Repository-local reference search | `docs/VALIDATION_REPORT.md`, CALC-01 artifacts, and files matching Horizons/JPL/DE/VSOP/AstroSage/ephemeris/reference were checked while excluding the protected research note and `research/next_08d`. | No original independently generated output for either synthetic profile was found. `REFERENCE_UNAVAILABLE`. |
| Archived AstroSage values in `docs/VALIDATION_REPORT.md` | Two Meerut Moon display values, ascendant displays, one ayanamsa display, nakshatra/pada, birth lord, and active chain on 2026-10-02. Original calculator output, exact coordinates, version, ephemeris/data, node/house/varga flags, Dasha year, exact Dasha boundaries, and acquisition timestamp are unavailable. | These are **different inputs** from the six synthetic profiles. The source implementation's independence from Swiss Ephemeris is unproven. Retain `EXTERNAL_COMPARISON_UNRESOLVED`; they are not the requested two suitable reference records. |

No external numerical source was used for a new CALC-02 comparison. The JPL documentation is a source for *how to acquire* a reference, not a reference output. The local AstroSage report is the only pre-existing external numerical comparison. Horizons usage and reuse conditions must be recorded from the applicable service terms with any eventual raw output; none is redistributed here. AstroSage output reuse rights are unknown. No artifact hash or stable output locator can be assigned to an output that was not obtained.

### Input and settings compatibility matrix

| Setting | JyotAI | Horizons candidate | Archived AstroSage |
| --- | --- | --- | --- |
| Input date/time, location, UTC | Fully specified for six synthetic fixtures | Query parameters fully specified for first target; no returned output | Local Meerut times stated; exact coordinates and original timezone selection absent |
| Software and data version | PySwissEph 2.10.3.2 / Swiss 2.10.03; Moshier return flags; no data-file hash | API/manual versions known; actual output's dynamical solution, kernel, and EOP version unknown | Unknown |
| Coordinate frame | Geocentric apparent, sidereal Lahiri | Geocentric apparent tropical IAU76/80 ecliptic-of-date quantity 31 if returned | Displayed sidereal values; frame and Lahiri variant not proven |
| Node, houses, D9/D10 | True node, Whole Sign, Parashari variants | Not provided by quantity 31 | Unknown |
| Dasha | 365.25-day Vimshottari-v1, UTC microseconds | Not provided | Birth lord and active chain only; year/boundary/roundoff unknown |
| Precision and rights | Internal Decimal output; code/fixture under repository | Output precision, output-specific rights and reuse record unavailable | Whole-arcsecond displays; reuse rights unknown |

## Staged verification and comparison policy

CALC-01's `angular_difference`, `compare_longitude`, and `compare_utc_boundary` remain the numeric core. CALC-02 adds an arcsecond display wrapper and exact categorical/order comparison, with both expected and actual values retained. Status is a **result**, never inferred from a populated fixture. A genuine raw artifact must first be stored with source locator, acquisition time, SHA-256, version/data/settings, precision, and reuse terms; then selected fields may be ingested into the existing fixture schema or a source-specific tropical intake. Ordinary regression tests use saved artifacts only and make no network calls.

Prospective tolerances, declared before new reference values are available:

| Comparable field | Tolerance and unit | Qualification |
| --- | --- | --- |
| UTC input conversion | exact to 1 second | Same local input, IANA zone and historical time-zone database rules required. Normalize both instants to UTC. |
| Tropical or sidereal body longitude; ascendant | shortest circular separation ≤5 arcseconds (1 arcminute = 60 arcseconds; 1 degree = 3600 arcseconds) | Only after matching origin, apparent/astrometric treatment, ecliptic/equinox, time scale, ayanamsa definition where relevant, and full input precision. A frame mismatch is unresolved, not a pass. |
| D1 sign and Whole Sign house/lord; D9/D10 sign | exact equality | Full-precision longitude and matching variant required. If a rounded source value straddles a division edge, mark unresolved. |
| Birth nakshatra, starting lord, MD order and AD order | exact equality | Compatible Moon, nakshatra boundaries and Dasha scheme required. |
| Birth balance and MD/AD UTC boundaries | ≤1 second | Exact 365.25-day year and rounding policy required. Day-only reference dates cannot establish this tolerance. Half-open boundary behavior must be checked separately. |

The comparison also records source precision; a displayed whole arcsecond carries up to ±0.5 arcsecond of rounding uncertainty. A field that fails the threshold after complete compatibility review becomes `REFERENCE_MISMATCH_INVESTIGATION_REQUIRED`; missing or incompatible settings remain `EXTERNAL_COMPARISON_UNRESOLVED`. Internal invariant tests alone remain `INTERNAL_VERIFIED`.

| Layer | Available independent evidence | Current status |
| --- | --- | --- |
| A. UTC conversion and time zone | Exact synthetic input/UTC pairs, checked internally; no external time-zone artifact | `INTERNAL_VERIFIED`; historical tzdb reproducibility pending |
| B. Tropical planetary longitude | Horizons method documented, no output | `REFERENCE_UNAVAILABLE` |
| C. Sidereal/Lahiri transformation | None with a versioned independent ayanamsa definition | `REFERENCE_UNAVAILABLE` |
| D. Ascendant and Whole Sign mapping | Internal tests; archived ascendants lack exact coordinates | `INTERNAL_VERIFIED` mapping; external comparison unresolved |
| E. D1 body signs, houses and lords | Internal tests; no matching complete external chart | `INTERNAL_VERIFIED` rules; external reference unavailable |
| F. Parashari D9/D10 | Internal edge tests; no matching external variant output | `INTERNAL_VERIFIED` mapping; external reference unavailable |
| G. Moon nakshatra and birth Dasha balance | Internal edge tests; archived birth lords lack reproducible settings/balance | `INTERNAL_VERIFIED` rules; external comparison unresolved |
| H. MD/AD order and UTC boundaries | Internal continuity/half-open tests; no complete external timeline | `INTERNAL_VERIFIED` rules; external reference unavailable |

There are **zero** new independent longitude differences for the six fixtures; reporting numeric zeroes would invent a comparison. No complete Kundli is verified. No `REFERENCE_MISMATCH_INVESTIGATION_REQUIRED` finding is assigned without a compatible reproducible reference.

## Archived Moon differences and Dasha

The original AstroSage artifacts, settings, exact coordinates and calculation timestamps are absent. CALC-01's existing screening comparison gives **+19.90798 arcseconds** for 1975-04-12 17:00Z and **+35.70897 arcseconds** for 2007-05-14 12:20Z (JyotAI minus archived display), both beyond its retrospective 1-arcsecond screen. Whole-arcsecond rounding alone cannot account for either displayed gap. The 2007 report's displayed Lahiri ayanamsa gap is +1.902 arcseconds; that number alone does not explain a +35.70897-arcsecond Moon gap if the underlying tropical position and frame were identical. Those assumptions are unverified. Different ephemeris sources, ayanamsa definitions, time-zone or input precision, and frame remain hypotheses, not findings. No offset is applied.

The report gives Ketu and Mercury as birth lords and Rahu/Saturn and Venus/Rahu as active chains on 2026-10-02. It gives no exact balance or MD/AD UTC boundary, complete order, year convention or rounding behavior. Dasha external verification is pending. CALC-01's computed counterfactual boundary shifts are internal arithmetic sensitivities, not AstroSage predictions.

## Birth-time sensitivity and product metadata design

CALC-01's ±15/±5-minute report was rerun for all six inputs (30 snapshots). Relative to each zero-minute baseline, the ascendant sign differs at -15 minutes for `dst_new_york` and `southern_hemisphere`, at +5/+15 for `ascendant_sign_boundary`, and at -15/-5 for `historical_kolkata_lmt`. `moon_nakshatra_boundary` differs in both Moon nakshatra and starting Dasha lord at -15/-5 minutes; its zero-minute lord is Venus and the earlier lord is Ketu. The report also retains D1 house, D9/D10 sign and house differences at every sampled offset. None has a corresponding independent perturbation series; external boundary verification remains unavailable. No interpretive outcome is inferred.

An eventual **internal** calculation-verification summary can use this shape (illustrative metadata, not a new API or certification badge):

```json
{
  "calculation_engine": "PySwissEph 2.10.3.2 / Swiss Ephemeris 2.10.03; Moshier",
  "conventions": "sidereal Lahiri; true node; Whole Sign; Parashari D9/D10; vimshottari-v1; 365.25-day year; UTC half-open",
  "reference_scope": "no independent numerical output acquired for six CALC-01 synthetic profiles",
  "internally_verified": ["UTC input conversion", "D1 house mapping", "D9/D10 mapping", "Dasha interval invariants"],
  "independently_verified": [],
  "birth_time_sensitivity": "internal ±15/±5-minute snapshots only",
  "unresolved": ["two archived AstroSage Moon gaps", "historical tzdb provenance", "independent planetary and Dasha reference artifacts"]
}
```

This is a proposed metadata contract only. The actual calculation and methodology versions must be read from provenance at generation time, not hardcoded from this example.

## Exact external handoff

An independent reviewer can acquire one **raw, unedited reference export per input** on their own computer. Keep the original export alongside a machine-readable transcription; never fill absent fields with JyotAI output.

| Reference | Enter these exact inputs | Required output from an independent implementation |
| --- | --- | --- |
| `india_ordinary` | Local `1990-01-15 09:30:00`, `Asia/Kolkata`; latitude `19.076`, east longitude `72.8777`; UTC `1990-01-15T04:00:00Z` | Full-precision tropical and Lahiri sidereal longitudes for Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn and both nodes; ascendant, D1 signs/houses/lords, D9 and D10 signs; birth nakshatra and lord; exact birth MD balance and MD/AD UTC start/end boundaries. |
| `dst_new_york` | Local `2024-07-01 12:00:00`, `America/New_York`; latitude `40.7128`, east longitude `-74.006`; UTC `2024-07-01T16:00:00Z` | The same numerical and categorical fields and exact MD/AD UTC boundaries. Preserve the source's local-time and daylight-saving settings in the export. |

For **each** row, follow this acquisition checklist:

1. Identify the calculator name, implementation/version and calculation lineage. Obtain its source documentation or an archived versioned methods page. Establish that its planetary and Dasha calculations do not reuse Swiss Ephemeris before calling the comparison independent; another interface to Swiss Ephemeris is a shared-foundation comparison.
2. Save the source's ephemeris or kernel name/version and data-file checksums; time scale, leap-second and EOP provenance; observer origin; apparent versus astrometric treatment; and ecliptic/equinox epoch. Record the precise sidereal Lahiri definition, true versus mean node, Whole Sign house rule, Parashari D9/D10 variants, Vimshottari year length, rounding policy, and whether intervals are half-open. Record each incompatibility or undocumented setting explicitly.
3. Export the original response as supplied by the source (for example, PDF, CSV, JSON, or screenshots if that is all it offers). Preserve digits, units, timezone offsets, and display precision. Include all nine MDs and their ADs with exact UTC start/end instants if claiming complete Dasha verification; a date-only timeline cannot pass the one-second boundary test. Transcribe comparable fields to UTF-8 JSON or CSV with source field names and units, linked to the original export.
4. Record the source URL or stable locator, applicable documentation URL/version, acquisition date and UTC time, and license/reuse conditions. Compute SHA-256 for **each original export and transcription** and retain both files. If a source omits data provenance or exact settings, label the affected fields unresolved rather than supplying assumed values.
5. Compare only convention-compatible fields against the declared tolerances above. Record expected, actual, signed difference, unit, precision, and result per field. Keep `EXTERNAL_COMPARISON_UNRESOLVED` for incompatible or incomplete evidence; reserve `REFERENCE_MISMATCH_INVESTIGATION_REQUIRED` for a reproducible, compatible failed comparison. Neither target currently has an acquired reference artifact or hash.

A JPL Horizons quantity-31 export may independently check only compatible **tropical planetary** longitudes. It does not establish the sidereal Lahiri transformation, nodes, ascendant, Whole Sign houses, vargas, or Vimshottari Dasha; obtain separate independent implementations and artifacts for claims about those layers. For sensitivity, acquire the same fields at -15, -5, +5 and +15 minutes around a boundary input before making an external boundary claim.

For the archived Moon investigation, provide the original AstroSage input screenshots/exports for both Meerut cases, exact coordinates, timezone selection, product/version and settings, the generated chart output, and the full birth-to-current Dasha table with exact dates/times. Record original capture timestamps and provenance. Ingest original files under test-only fixtures with hashes and rights notes, map only fields genuinely compatible with the calculation contract, then run the CALC-01/CALC-02 comparisons with the predeclared tolerances. Until then the two archived cases remain `EXTERNAL_COMPARISON_UNRESOLVED`.

**GO/NO-GO for independent accuracy claims:** NO-GO for tropical positions, sidereal D1, D9, D10, ascendant, nodes, and Dasha. Internal rule/invariant coverage may be described as such; it is not an independent chart certification. No production engine, active rule, source manifest, provider privacy contract, or user-facing claim was changed.
