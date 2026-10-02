# Validation Report

**Status:** PASS WITH DOCUMENTED METHODOLOGY DIFFERENCES.

This report records two independent comparisons between JyotAI and AstroSage.
It documents observed compatibility and differences; it does not introduce a
calculation correction, offset, or compatibility adjustment.

## JyotAI methodology under test

- PySwissEph 2.10.3.2 / Swiss Ephemeris 2.10.03.
- Current calculations use the Moshier internal ephemeris.
- Sidereal zodiac with Swiss Ephemeris `SIDM_LAHIRI`.
- `vimshottari-v1` uses exactly 365.25 days per Dasha year.

AstroSage's exact ephemeris configuration and Dasha calendar convention are
not known. Consequently, this comparison does not treat small positional or
Dasha-boundary differences as an error in either system.

## Benchmark 1 — 12-Apr-1975 22:30, Meerut

| Factor | AstroSage | JyotAI | Difference |
| --- | --- | --- | --- |
| Moon | Aries 10°08'44\" | Aries 10°09'04\" | +19.9 arcseconds |
| Ascendant | Scorpio 17°57'41\" | Scorpio 17°57'58\" | +16.7 arcseconds |
| Nakshatra / pada | Ashvini pada 4 | Ashwini pada 4 | Agreement |
| Birth Mahadasha | Ketu | Ketu | Agreement |
| Active Dasha on 02-Oct-2026 | Rahu/Saturn | Rahu/Saturn | Agreement |

The alternate spellings “Ashvini” and “Ashwini” refer to the same nakshatra.

## Benchmark 2 — 14-May-2007 17:50, Meerut

| Factor | AstroSage | JyotAI | Difference |
| --- | --- | --- | --- |
| Ascendant | Libra 14°48'04\" | Libra 14°48'18.902618\" | +14.903 arcseconds |
| Moon | Pisces 26°58'30\" | Pisces 26°59'05.708967\" | +35.709 arcseconds |
| Lahiri ayanamsa | 23°57'34\" | 23°57'35.902131\" | +1.902 arcseconds |
| Nakshatra / pada | Revati pada 4 | Revati pada 4 | Agreement |
| Birth Mahadasha | Mercury | Mercury | Agreement |
| Active Dasha on 02-Oct-2026 | Venus/Rahu | Venus/Rahu | Agreement |

## Findings and limits

Both benchmarks agree on sign, nakshatra/pada, birth Mahadasha lord, and the
tested current Mahadasha/Antardasha. JyotAI Dasha boundaries differ from
AstroSage by several days in these benchmarks. This is documented as a
methodology difference, consistent with the known uncertainty about AstroSage's
exact ephemeris configuration and Dasha calendar convention.

No correction or offset has been introduced to force compatibility. Independent
validation should continue as the engine evolves. External Swiss Ephemeris
data-file validation remains outstanding.
