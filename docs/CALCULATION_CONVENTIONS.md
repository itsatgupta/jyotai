# Calculation Conventions

**Status:** MVP provisional methodology decisions.  
**Scope:** deterministic chart and timing calculations only.  
**Provider status:** Task 04 uses PySwissEph/Swiss Ephemeris only for local
hobby development. It is not approved for proprietary or production deployment;
see `EPHEMERIS_LICENSE_COMPARISON.md`.

These conventions are explicit so implementations and stored charts can
reproduce the same result. They do not override the requirement to verify the
chosen provider, its data, and its license before production deployment.

## 1. Astrology system

**MVP provisional decision:**

- Tradition: Vedic/Jyotish.
- Zodiac: sidereal.

No calculation module may silently substitute tropical positions.

## 2. Ayanamsa

**MVP provisional decision:** use Lahiri ayanamsa.

**Task 04 local implementation:** Swiss Ephemeris `SIDM_LAHIRI`, persisted as
`ayanamsa_provider_mode`. The label `Lahiri` alone is not sufficient
provenance. This selection still needs independent fixture validation and
production license clearance.

## 3. Rahu and Ketu

**MVP provisional product methodology decision:** use **true lunar nodes** for
Rahu (north node) and Ketu (south node).

The node definition must be a configuration value and persisted with chart
metadata. The design must support mean lunar nodes later without changing the
meaning of existing charts. The implementation must not infer the opposite node
or its longitude using an LLM.

## 4. Houses

**MVP provisional decision:** use Whole Sign houses.

House calculation must remain behind an abstraction. A future house-system
implementation can be added only as an explicit, versioned choice; it must not
silently reinterpret existing charts.

## 5. Time and location

For every birth input and chart:

- retain the original IANA timezone identifier;
- retain the canonical UTC instant;
- retain latitude and longitude;
- do not silently resolve nonexistent or ambiguous civil times.

Ambiguous or nonexistent local times must produce a validation error until an
explicit, versioned disambiguation policy and input are introduced. This avoids
silently producing a different astronomical instant.

## 6. Nakshatra

Nakshatra must be derived deterministically from the verified **sidereal
longitude**:

- 27 nakshatras;
- 4 padas per nakshatra.

The LLM must never calculate or infer a nakshatra or pada. The calculation and
its boundary behavior must be covered by deterministic tests.

## 7. Retrograde

Retrograde status must be derived deterministically from provider motion or
velocity data using a documented convention. The LLM must never infer or assign
retrograde status.

**Task 04 convention:** a body is retrograde when its returned geocentric,
sidereal ecliptic longitudinal speed is strictly less than zero. A zero speed
is not classified as retrograde. The raw speed and derived boolean are both
recorded in the D1 chart.

## 8. Reproducibility metadata

Every generated chart must eventually record, at minimum:

- provider name;
- provider/library version;
- ephemeris-data version and cryptographic hash;
- ayanamsa name and exact provider mode/identifier;
- node definition (true or mean);
- house system;
- UTC birth instant;
- original IANA timezone;
- latitude and longitude;
- relevant calculation flags, including coordinate/frame, observer,
  apparent/astrometric, sidereal, speed/velocity, and time-scale settings.

This metadata is part of the chart's calculation provenance, not AI
interpretation context. It must be retained with generated answers where the
answer depends on that chart.

## 9. Divisional charts / Vargas

**Task 05 MVP decision:** derive only D1/Rashi, D2/Hora, D9/Navamsa, and
D10/Dasamsa. A Varga is a deterministic transformation of an already verified
sidereal D1 longitude. It is not a second ephemeris calculation and its derived
longitude must not be represented as an astronomical position returned by the
ephemeris provider.

For a D1 sign ordinal `i` (Aries = 0 through Pisces = 11), D1 degree within
the sign `d`, and factor `N`, the division index is
`floor(d * N / 30)`. The derived degree is `(d * N) mod 30`. Exact boundaries
belong to the following division. Each Varga applies the same transformation to
the D1 ascendant and uses the derived ascendant as the Whole Sign house anchor.

- **D1/Rashi:** factor 1; identity transformation.
- **D2/Hora:** Parashari Sun/Moon Hora. In odd-numbered signs, 0°–15° is Leo
  (Sun Hora) and 15°–30° is Cancer (Moon Hora). In even-numbered signs this is
  reversed.
- **D9/Navamsa:** Parashari Navamsa. Movable signs start from the same sign,
  fixed signs start from the ninth sign, and dual signs start from the fifth
  sign. The remaining eight Navamsas advance zodiacally one sign at a time.
- **D10/Dasamsa:** Parashari Dasamsa. Odd-numbered signs start from the same
  sign; even-numbered signs start from the ninth sign. The remaining divisions
  advance zodiacally one sign at a time.

The Varga result stores its chart factor and mapping variant, source D1
methodology, birth input, calculation instant, and ephemeris provenance. D1
nakshatra/pada, motion speed, and retrograde are not recalculated from a
synthetic Varga longitude. If motion facts are included, they are explicitly
marked as inherited D1 facts.

## 10. Vimshottari Dasha — `vimshottari-v1`

**Task 06 MVP decision:** calculate Vimshottari Mahadasha and Antardasha only
from the already-calculated canonical D1 Moon. The engine does not call an
ephemeris provider, use a Varga, or use an LLM. It inherits and retains the
source D1 chart's methodology and ephemeris provenance; it does not represent
itself as an ephemeris calculation.

The birth nakshatra is derived from the D1 Moon's exact, unrounded sidereal
longitude using the existing 27-nakshatra convention. Its lord follows this
fixed order: Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury.
Their Mahadasha durations are respectively 7, 20, 6, 10, 7, 18, 16, 19, and
17 years, for a 120-year cycle.

Birth balance is calculated without using pada. Let `f` equal longitude elapsed
within the birth nakshatra divided by its width (13°20′). The remaining birth
Mahadasha is `full_mahadasha_duration * (1 - f)`. Antardashas begin with the
Mahadasha lord and follow the same cyclic order. Their duration is
`mahadasha_duration * antardasha_lord_years / 120`.

For this version only, one dasha year is exactly 365.25 days: 31,557,600
seconds or 31,557,600,000,000 microseconds. This is a JyotAI computational
convention, not a claim that it is the sole universal Jyotish convention.
Arithmetic uses `Decimal` until conversion to integer microseconds, with
`ROUND_HALF_EVEN` for fractional microseconds. Antardasha boundaries are
calculated from cumulative parent proportions and the final child end is forced
to the parent end, preventing rounding drift.

All boundaries are timezone-aware UTC datetimes. No local civil-time calendar
arithmetic or implicit current time is used. Periods are half-open `[start,
end)`: an instant at an end belongs to the following period. Results record the
`vimshottari-v1` methodology, Moon/nakshatra inputs, all fixed constants and
rounding policy, source birth timezone, source chart methodology, calculation
instant, and complete inherited ephemeris provenance.

## Remaining decisions before production implementation

1. Obtain commercial/licensing clearance for the chosen provider and binding.
2. Confirm that `SIDM_LAHIRI` is the accepted Lahiri definition against an
   independent fixture corpus.
3. Specify the full production calculation-flag policy: geocentric versus topocentric,
   apparent versus astrometric, ephemeris data set, time scale, and historical
   calendar handling.
4. Establish a legally usable known-chart fixture corpus and acceptance
   tolerances before approving the adapter.
