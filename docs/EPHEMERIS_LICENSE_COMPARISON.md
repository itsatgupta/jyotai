# Ephemeris and License Comparison

**Status:** PySwissEph 2.10.3.2 is installed for Task 04 local hobby
development only; this document's production licensing cautions remain in
force.  
**Reviewed:** 2026-10-02.  
**Scope:** a commercial, server-hosted Jyotish product using sidereal positions,
Lahiri ayanamsa, Rahu/Ketu, nakshatra, and reproducible historical charts.

## 1. Executive summary

### Verified facts

- Swiss Ephemeris is explicitly dual-licensed under AGPL or the Swiss
  Ephemeris Professional License. Its publisher says this choice must be made
  before operating a public service that uses it. [Swiss Ephemeris license
  notice](https://github.com/aloistr/swisseph/blob/master/LICENSE), [official
  programmer documentation](https://www.astro.com/swisseph-download/doc/swephprg.pdf)
- The common `pyswisseph` Python binding declares AGPL-3.0. It is therefore
  **not safe to treat a Swiss Ephemeris professional license as automatically
  licensing the binding**. Written confirmation or a separately acceptable
  binding is required for a closed-source SaaS.
  [PySwissEph package metadata](https://github.com/astrorigin/pyswisseph/blob/master/setup.py)
- Swiss Ephemeris is the only reviewed candidate with directly documented
  Lahiri/sidereal facilities and a mature astrology-oriented API. Its official
  documentation also explicitly covers planets, lunar nodes, and sidereal
  calculation. [Sidereal modes](https://github.com/astrorigin/pyswisseph/blob/master/docs/programmers_manual/sidereal_mode.rst), [official
  documentation](https://www.astro.com/swisseph/swisseph.pdf)
- Skyfield and Astronomy Engine use permissive MIT licenses. They can be used,
  modified, and redistributed commercially provided their copyright/license
  notices accompany copies. Neither reviewed source documents built-in Lahiri
  ayanamsa or a Jyotish/Rahu-Ketu API.
- Kerykeion v6 documents Lahiri, nakshatra, true/mean nodes and retrograde
  support, but its library and default backend are AGPL-3.0. Its project directs
  closed-source commercial users to its hosted API rather than local import.
  [Kerykeion README](https://github.com/g-battaglia/kerykeion/blob/main/README.md)

### Conclusion

For local hobby development, Task 04 uses PySwissEph/Swiss Ephemeris behind the
provider abstraction. The strongest functional fit, Swiss Ephemeris, still has
a commercial-licensing decision that must be closed before production use.
The strongest permissive options, Skyfield and SpiceyPy/CSPICE, require a
substantial, independently tested Jyotish layer for sidereal coordinates,
Lahiri, nodes, and houses. Astronomy Engine is attractive operationally but its
documented one-arcminute accuracy target is weak for a primary chart engine.

This is technical due diligence, not legal advice. Obtain counsel and, for
Swiss Ephemeris/PySwissEph, written confirmation from the relevant licensors.

## 2. Candidate comparison table

Legend: **Yes** = documented in reviewed primary material; **No documented
support** = not found in the reviewed official material, not proof of absence;
**External** = feasible only through project-owned code or data outside the
candidate.

| Candidate / official project | License and commercial posture | Vedic capability | Accuracy, dates, reproducibility | Python / operations / SaaS fit |
|---|---|---|---|---|
| [Astronomy Engine](https://github.com/cosinekitty/astronomy) | **MIT**. Commercial use, modification and redistribution are permitted; retain the copyright and license notice. No commercial license requirement. | Sun, Moon and major planets: **Yes**. Retrograde: **External** (derive from velocity/longitude samples). Rahu/Ketu, Lahiri/sidereal, nakshatra: **No documented support**; all would be product code. | Project target is within **1 arcminute** of NOVAS; it supports millennia before/after present. Fixed version plus fixtures is reproducible. This accuracy is unsuitable without boundary testing when a planet is close to a sign/nakshatra/pada cusp. | Official Python support; pure standard-library implementation and no external data files. Low deployment risk. Good only if the product accepts owning and validating all Jyotish transforms and node algorithms. |
| [Skyfield](https://github.com/skyfielders/python-skyfield) + JPL kernels | **MIT** for Skyfield. Commercial use/modification/redistribution permitted with license notice. JPL/NAIF kernel terms separately allow commercial use without fees; unmodified NAIF kernels may be redistributed, acknowledgement is encouraged. | Planet/Sun/Moon: **Yes**, using selected JPL kernel. Retrograde: **External** from state/vector. Rahu/Ketu, sidereal/Lahiri, nakshatra: **External**; no reviewed Jyotish API. | High-precision JPL-backed positions. Coverage is kernel-specific: DE440s 1849–2150; DE440 1550–2650; DE441 -13200–17191, with major storage trade-offs. Pin kernel file, SHA-256 and time-scale/leap-second data. | Mature pure-Python package with NumPy; pre-bundle/pin kernels to avoid runtime downloads. Strong permissive foundation, but high implementation and validation burden for Jyotish. |
| [Flatlib](https://github.com/flatangle/flatlib) | Flatlib is **MIT**, but its own documentation says it relies on Swiss Ephemeris and commercial users must comply with that dependency or obtain a Swiss commercial license. Current upstream Swiss/PySwissEph terms must govern, not Flatlib's older wording. | Astrology wrapper, but reviewed sources do not establish explicit Lahiri/nakshatra/Rahu-Ketu completeness for this MVP. Its Swiss dependency is the important calculation path. | Inherits Swiss Ephemeris data behavior when configured. Flatlib release cadence/documentation has historically been limited; verify current Python 3.12+ compatibility and regression accuracy before considering it. | Python-native, but adds abstraction and transitive-license risk without removing Swiss licensing. Poor fit as the primary adapter dependency. |
| [Kerykeion](https://github.com/g-battaglia/kerykeion) | **AGPL-3.0** for Kerykeion and its default libephemeris backend. Modification and redistribution are permitted under AGPL; network users must receive corresponding source. Commercial closed-source users are directed to a hosted API. Attribution/license notices must be preserved. | Sidereal modes including **Lahiri**, Vedic nakshatra/pada/lord, true and mean lunar nodes, planetary positions, houses, and retrograde fields are documented. | Documentation describes provenance and precision modes but an independent Jyotish regression comparison is still required. Historical/future coverage depends on its selected backend/data tier; exact production range must be verified. | Modern typed Python, active v6 project. Excellent feature fit for AGPL deployment; unsuitable for a proprietary local SaaS unless a separate commercial arrangement is verified. Hosted API introduces vendor/data-processing dependency. |
| [Swiss Ephemeris](https://www.astro.com/swisseph/) / [PySwissEph](https://github.com/astrorigin/pyswisseph) | Swiss: **AGPL-3.0 or Professional License**. PySwissEph: **AGPL-3.0 declared**. AGPL permits modification/redistribution but obliges network source availability. The official Professional License enables commercial proprietary use of Swiss Ephemeris, but the wrapper's independent license status needs written confirmation. Preserve notices; Swiss license limits promotional use of author names. | Explicit sidereal modes, including Lahiri; Sun, Moon, planets and lunar nodes; houses; position speed for retrograde; ideal input for deterministic nakshatra (a 27-way division of the returned sidereal longitude). | Official site states compressed data reproduce JPL data to 0.001 arcsecond and cover 13201 BCE–17191 CE; near-current details differ by data/EOP availability. Pin library version, ephemeris files, flags, ayanamsa, node mode, time scale and fixtures. | Native Python binding involves compiled/native build and ephemeris data deployment. Best functional fit, contingent on a resolved commercial license and a supportable binding. |
| [SpiceyPy](https://github.com/AndrewAnnex/SpiceyPy) + [NAIF CSPICE](https://naif.jpl.nasa.gov/naif/rules.html) | SpiceyPy: **MIT**. CSPICE/NAIF terms allow commercial use without fee; kernel redistribution is allowed when unmodified and acknowledgement is encouraged. Modification/redistribution conditions for individual kernels must be preserved. | SPICE exposes astronomical geometry and selected kernel data, not Jyotish concepts. Planets/Sun/Moon: **Yes** with proper kernels. Rahu/Ketu, sidereal/Lahiri, nakshatra, retrograde semantics: **External**. | High quality is possible with selected JPL kernels, but date range, frames, time conversions and data provenance are entirely product-configured. Reproducible only with pinned kernel set/checksums. | Python wrapper has C/CMake/CSPICE build/binary concerns and NumPy dependency. A serious permissive alternative, but considerably more implementation work than Skyfield and no Vedic advantage. |

## 3. License analysis

### Permissive candidates: Astronomy Engine, Skyfield, SpiceyPy

**Verified facts.** Each reviewed project declares MIT. MIT allows commercial
SaaS use, modification, sublicensing, sale and redistribution; the obligation
is to include the copyright and permission notice in copies or substantial
portions. There is no recurring commercial-license requirement in MIT itself.
[Astronomy Engine license](https://github.com/cosinekitty/astronomy/blob/master/LICENSE),
[Skyfield license](https://github.com/skyfielders/python-skyfield/blob/master/LICENSE),
[SpiceyPy metadata](https://github.com/AndrewAnnex/SpiceyPy/blob/main/pyproject.toml)

**Important qualification.** Skyfield and SpiceyPy are software wrappers, not
the ephemeris data. JPL/NAIF data terms must be recorded for every chosen data
file. NAIF says commercial use is allowed without fees; it permits
redistribution of its unmodified kernels and encourages acknowledgement.
[NAIF rules](https://naif.jpl.nasa.gov/naif/rules.html) Any non-NAIF kernel,
or a modified kernel, needs its own terms review.

### AGPL and dual-license candidates: Swiss Ephemeris, PySwissEph, Kerykeion

**Verified facts.** AGPL permits use, modification and redistribution but adds
network-source obligations. A private SaaS cannot assume it may import AGPL
code without providing the corresponding source to network users. Swiss
Ephemeris states that a public service must choose AGPL or its Professional
License before activation. Its Professional License contract expressly covers
server use and distributed apps. [Official Swiss programming license
text](https://www.astro.com/swisseph-download/doc/swephprg.pdf), [Professional
License contract](https://www.astro.com/swisseph/secont_e.pdf?nho2=51)

**Manual verification required.** Before any proprietary implementation:

1. Obtain a current written quote/contract from Astrodienst for this project's
   backend and any client distribution.
2. Ask PySwissEph's copyright holder whether a Swiss Professional License is
   sufficient for its AGPL Python binding, or use a separately licensed/direct
   binding to the official Swiss library.
3. Inventory all ephemeris data files included in a container/image and retain
   their notices.
4. Have qualified counsel review the final deployment model. This document does
   not decide the legal question.

### Flatlib's transitive issue

**Verified fact.** Flatlib's own FAQ calls out Swiss Ephemeris as the
commercial-use caveat despite Flatlib being MIT. Thus wrapping a copyleft
ephemeris in MIT application code does not remove the underlying obligations.
[Flatlib FAQ](https://github.com/flatangle/flatlib/blob/master/docs/source/faq.rst)

## 4. Vedic astrology capability analysis

### Direct fit: Swiss Ephemeris

**Verified facts.** Swiss Ephemeris documents sidereal operation and Lahiri
variants, lunar-node calculations, and long-range Lahiri ephemeris tables.
The project methodology can explicitly request its standard Lahiri mode and
record the exact mode identifier. Nakshatra and pada should still be owned by
this project as a simple, tested deterministic division of the **returned
sidereal longitude**; this prevents an opaque, library-specific interpretation
rule from entering the calculation layer.

**Assumption requiring a product decision.** Jyotish implementations vary
between mean and true nodes. Neither AGENTS.md nor the methodology document
specifies which definition should represent Rahu/Ketu. The eventual provider
must expose the selected definition, and the decision/version must be persisted.

### Direct feature fit but AGPL: Kerykeion

**Verified facts.** Kerykeion v6 documents sidereal `LAHIRI`, nakshatra,
nakshatra pada/lord, retrograde values, and both true and mean north/south
lunar nodes. [Vedic nakshatra documentation](https://kerykeion.net/python-library/docs/v6/vedic_nakshatras),
[active points](https://kerykeion.net/python-library/docs/v6/active_points),
[schema reference](https://kerykeion.net/python-library/docs/v6/schemas)

This makes it useful as a **regression-comparison reference** if licensing and
test-data terms permit, but it does not remove the licensing gate for local use.

### Permissive astronomy foundations: Skyfield, Astronomy Engine, SpiceyPy

**Verified facts.** They deliver astronomical positions, not a Vedic
methodology. Sidereal conversion, Lahiri definition, ecliptic frame choices,
node derivation/selection, retrograde convention, and nakshatra/pada are all
project responsibilities.

**Assumption.** A carefully implemented Lahiri subtraction plus a fixed
sidereal division can be made deterministic on these foundations. It must not
be assumed equivalent to Swiss Ephemeris without corpus regression tests,
especially near sign/nakshatra/pada boundaries and for historical dates.

### Flatlib

Its Swiss Ephemeris dependency makes its astronomical capability plausible, but
its suitability for the specified Lahiri/nakshatra/node conventions is not
verified here. Do not select it on the basis of the wrapper alone.

## 5. Accuracy and reproducibility considerations

### Verified facts

- Astronomy Engine states a design target of one arcminute accuracy and uses
  compact algorithms without external dependencies. [Project
  README](https://github.com/cosinekitty/astronomy)
- Skyfield says its results agree with USNO/Astronomical Almanac positions to
  0.00001 arcseconds, but the actual result depends on the selected JPL kernel
  and time data. [Skyfield documentation](https://rhodesmill.org/skyfield/)
- Skyfield's documented kernel ranges make long historical support a deliberate
  deployment choice, not a library default. DE441 reaches -13200 to 17191 but
  is roughly 3.1 GB. [Skyfield kernel guide](https://rhodesmill.org/skyfield/planets.html)
- Swiss Ephemeris states a 13201 BCE–17191 CE range and 0.001-arcsecond
  reproduction of its JPL-based compressed data. [Swiss Ephemeris range and
  precision](https://www.astro.com/swisseph/sweph_g.htm?lang=t&nhor=2)

### Required reproducibility contract, regardless of provider

Persist with every chart:

- provider name, package/library version and native-library version;
- ephemeris/kernel filenames, source, hash and coverage range;
- calculation flags: geocentric/topocentric, apparent/astrometric, speed,
  tropical/sidereal, ayanamsa identifier, house system and node definition;
- UTC input instant, original IANA timezone, latitude/longitude and calendar
  convention;
- time-scale and Earth-orientation/leap-second data versions where applicable.

Commit known-chart fixtures from independently generated, legally usable
reference material before treating any provider as correct. Test sign,
longitude, node, nakshatra and pada boundaries separately.

## 6. Commercial SaaS implications

| Deployment choice | Implication |
|---|---|
| Closed-source SaaS with local Swiss calculations | License the Swiss library commercially **and** resolve the Python binding's separate AGPL status in writing. Do not deploy on an assumption. |
| AGPL-compatible SaaS | Swiss/PySwissEph or Kerykeion can be technically viable, but the product must satisfy AGPL source-offer obligations for network users and preserve notices. |
| Closed-source SaaS with Skyfield or SpiceyPy | Permissive application licensing is feasible, subject to kernel/data terms. Budget engineering and test effort for the entire Vedic transform/node/house layer. |
| Closed-source SaaS with Astronomy Engine | Simplest supply chain but only consider after proving angular accuracy against agreed fixtures, particularly at astrological boundaries. |
| Hosted Kerykeion/Astrologer API | Avoids importing AGPL code locally but creates vendor, pricing, availability, data-processing and API-version dependencies. Contract terms need separate product/legal review. |

## 7. Recommendation criteria

Do not rank a final provider until all candidates are evaluated against these
pass/fail criteria:

1. **License clearance:** written approval for the exact SaaS deployment,
   wrapper and data files.
2. **Methodology support:** explicit sidereal Lahiri output, documented node
   options, required bodies, and suitable house/ascendant primitives.
3. **Regression accuracy:** agreement against an approved fixture corpus within
   a documented tolerance, including historical births and all cusp boundaries.
4. **Reproducibility:** pin-able code/data/time-scale artifacts with no runtime
   internet dependency.
5. **Operational fit:** supported Python version, container builds, CPU/memory,
   offline behavior, vulnerability and update policy.
6. **Architecture fit:** provider remains behind `EphemerisProvider`; no
   library-specific domain types leak into chart, timing, rules or AI modules.

## 8. Open questions / items requiring manual verification

1. **Product owner:** Will this be proprietary/closed source, or AGPL
   compatible? This is the gating licensing decision.
2. **Product owner / domain reviewer:** Should Rahu/Ketu use mean or true
   nodes? Define it before fixtures are approved.
3. **Domain reviewer:** Which exact Lahiri variant is required (the project
   states Lahiri, but upstream exposes several Lahiri-related modes)? Record the
   authoritative definition, not only a display label.
4. **Legal counsel/licensors:** Is `pyswisseph` usable in a proprietary service
   after purchasing Swiss Ephemeris Professional, or is a distinct binding
   license/direct integration required?
5. **Legal counsel:** Review JPL/NAIF terms for the exact kernels and any
   bundled non-NAIF data—not only the wrapper package license.
6. **Engineering:** Define supported birth-date range. Long-range kernels/data
   have significant image size and historical time-scale uncertainty.
7. **Engineering/domain reviewer:** Define exact calculation flags: geocentric
   versus topocentric planets/nodes, apparent versus astrometric positions,
   ephemeris source, calendar treatment before Gregorian adoption, and house
   system.
8. **Engineering:** Obtain a licensed, independent fixture corpus before Task
   03; do not use an LLM or unsourced web calculator as a calculation oracle.

## Sources consulted

Primary project/publisher sources consulted during this review:

- [Swiss Ephemeris official site and precision/range](https://www.astro.com/swisseph/sweph_g.htm?lang=t&nhor=2)
- [Swiss Ephemeris programmer/license documentation](https://www.astro.com/swisseph-download/doc/swephprg.pdf)
- [Swiss Ephemeris Professional License contract](https://www.astro.com/swisseph/secont_e.pdf?nho2=51)
- [PySwissEph repository/package metadata](https://github.com/astrorigin/pyswisseph/blob/master/setup.py)
- [Astronomy Engine repository and license](https://github.com/cosinekitty/astronomy)
- [Skyfield repository/license](https://github.com/skyfielders/python-skyfield/blob/master/LICENSE)
- [Skyfield planetary-kernel documentation](https://rhodesmill.org/skyfield/planets.html)
- [NAIF/SPICE usage rules](https://naif.jpl.nasa.gov/naif/rules.html)
- [Flatlib FAQ](https://github.com/flatangle/flatlib/blob/master/docs/source/faq.rst)
- [Kerykeion repository/license statement](https://github.com/g-battaglia/kerykeion/blob/main/README.md)
- [Kerykeion Vedic nakshatra documentation](https://kerykeion.net/python-library/docs/v6/vedic_nakshatras)
