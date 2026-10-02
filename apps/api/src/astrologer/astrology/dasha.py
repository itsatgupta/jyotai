"""Deterministic Vimshottari Dasha calculations derived solely from a D1 chart."""

from datetime import UTC, datetime, timedelta
from decimal import ROUND_HALF_EVEN, Decimal
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from astrologer.astrology.chart import (
    Chart,
    ChartMethodology,
    ChartPlanet,
    Nakshatra,
    nakshatra_for_longitude,
)
from astrologer.astrology.ephemeris import (
    Ayanamsa,
    CelestialBody,
    EphemerisProvenance,
    Longitude,
    ZodiacSystem,
)

_NAKSHATRA_WIDTH = Decimal("40") / Decimal("3")
_TOTAL_DASHA_YEARS = 120
_DASHA_YEAR_DAYS = Decimal("365.25")
_DASHA_YEAR_MICROSECONDS = 31_557_600_000_000


class DashaLord(StrEnum):
    """The nine Vimshottari lords in their fixed cyclic order."""

    KETU = "ketu"
    VENUS = "venus"
    SUN = "sun"
    MOON = "moon"
    MARS = "mars"
    RAHU = "rahu"
    JUPITER = "jupiter"
    SATURN = "saturn"
    MERCURY = "mercury"


_LORD_SEQUENCE = tuple(DashaLord)
_MAHADASHA_YEARS: dict[DashaLord, int] = {
    DashaLord.KETU: 7,
    DashaLord.VENUS: 20,
    DashaLord.SUN: 6,
    DashaLord.MOON: 10,
    DashaLord.MARS: 7,
    DashaLord.RAHU: 18,
    DashaLord.JUPITER: 16,
    DashaLord.SATURN: 19,
    DashaLord.MERCURY: 17,
}


class DashaLordDuration(BaseModel):
    """One fixed lord-to-Mahadasha-year mapping in the v1 methodology."""

    model_config = ConfigDict(frozen=True)

    lord: DashaLord
    years: int = Field(gt=0)


class VimshottariMethodology(BaseModel):
    """Frozen inputs and arithmetic policy for ``vimshottari-v1``."""

    model_config = ConfigDict(frozen=True)

    methodology_id: Literal["vimshottari-v1"] = "vimshottari-v1"
    source_d1_moon_longitude: Longitude
    birth_nakshatra: Nakshatra
    birth_nakshatra_lord: DashaLord
    nakshatra_count: Literal[27] = 27
    lord_sequence: tuple[DashaLord, ...] = _LORD_SEQUENCE
    mahadasha_years: tuple[DashaLordDuration, ...] = tuple(
        DashaLordDuration(lord=lord, years=_MAHADASHA_YEARS[lord]) for lord in _LORD_SEQUENCE
    )
    total_cycle_years: Literal[120] = 120
    dasha_year_days: Decimal = _DASHA_YEAR_DAYS
    dasha_year_microseconds: int = _DASHA_YEAR_MICROSECONDS
    timestamp_resolution: Literal["microsecond"] = "microsecond"
    fractional_microsecond_rounding: Literal["ROUND_HALF_EVEN"] = "ROUND_HALF_EVEN"


class DashaProvenance(BaseModel):
    """The frozen method plus complete provenance inherited from the D1 chart."""

    model_config = ConfigDict(frozen=True)

    methodology: VimshottariMethodology
    source_chart_calculation_instant: datetime
    source_chart_methodology: ChartMethodology
    inherited_ephemeris_provenance: EphemerisProvenance
    source_birth_timezone: str


class AntardashaPeriod(BaseModel):
    """A half-open Antardasha interval contained by one Mahadasha."""

    model_config = ConfigDict(frozen=True)

    mahadasha_lord: DashaLord
    lord: DashaLord
    start: datetime
    end: datetime


class MahadashaPeriod(BaseModel):
    """A half-open Mahadasha interval and its Antardasha subdivision."""

    model_config = ConfigDict(frozen=True)

    lord: DashaLord
    start: datetime
    end: datetime
    antardashas: tuple[AntardashaPeriod, ...]


class DashaTimeline(BaseModel):
    """Mahadashas intersecting the interval from birth through an explicit instant."""

    model_config = ConfigDict(frozen=True)

    source_birth_instant: datetime
    requested_through: datetime
    mahadashas: tuple[MahadashaPeriod, ...]
    provenance: DashaProvenance


class DashaChain(BaseModel):
    """The active Mahadasha and Antardasha at one explicit instant."""

    model_config = ConfigDict(frozen=True)

    instant: datetime
    mahadasha: MahadashaPeriod
    antardasha: AntardashaPeriod
    provenance: DashaProvenance


class VimshottariDashaEngine:
    """Calculate Vimshottari v1 periods from a canonical D1 chart only."""

    def calculate(self, chart: Chart, through: datetime) -> DashaTimeline:
        """Return every Mahadasha intersecting ``[birth, through)``.

        An explicit end avoids any dependency on a wall-clock "now" value.
        Aware non-UTC inputs are normalized to UTC; naive inputs and ranges not
        after birth are rejected.
        """
        birth_instant = chart.birth_input.utc_datetime
        requested_through = _as_utc(through, "through")
        if requested_through <= birth_instant:
            raise ValueError("through must be after the source birth instant")

        state = _initial_state(chart)
        periods: list[MahadashaPeriod] = []
        while state.start < requested_through:
            period = _mahadasha_period(state.lord, state.start)
            if period.end > birth_instant:
                periods.append(period)
            state = _DashaState(lord=_next_lord(state.lord), start=period.end)

        return DashaTimeline(
            source_birth_instant=birth_instant,
            requested_through=requested_through,
            mahadashas=tuple(periods),
            provenance=_provenance(chart),
        )

    def at(self, chart: Chart, instant: datetime) -> DashaChain:
        """Look up the active half-open Mahadasha and Antardasha at ``instant``."""
        birth_instant = chart.birth_input.utc_datetime
        requested_instant = _as_utc(instant, "instant")
        if requested_instant < birth_instant:
            raise ValueError("instant must not be before the source birth instant")

        state = _initial_state(chart)
        while True:
            mahadasha = _mahadasha_period(state.lord, state.start)
            if requested_instant < mahadasha.end:
                antardasha = next(
                    period
                    for period in mahadasha.antardashas
                    if period.start <= requested_instant < period.end
                )
                return DashaChain(
                    instant=requested_instant,
                    mahadasha=mahadasha,
                    antardasha=antardasha,
                    provenance=_provenance(chart),
                )
            state = _DashaState(lord=_next_lord(state.lord), start=mahadasha.end)


class _DashaState(BaseModel):
    """Internal immutable cursor for forward Mahadasha generation."""

    model_config = ConfigDict(frozen=True)

    lord: DashaLord
    start: datetime


def lord_for_nakshatra(nakshatra: Nakshatra) -> DashaLord:
    """Return the v1 Vimshottari lord for one of the 27 ordered nakshatras."""
    return _LORD_SEQUENCE[list(Nakshatra).index(nakshatra) % len(_LORD_SEQUENCE)]


def _initial_state(chart: Chart) -> _DashaState:
    moon = _moon_from_chart(chart)
    birth_instant = chart.birth_input.utc_datetime
    birth_lord = lord_for_nakshatra(moon.nakshatra.nakshatra)
    elapsed_fraction = (moon.longitude % _NAKSHATRA_WIDTH) / _NAKSHATRA_WIDTH
    remaining_microseconds = _quantize_microseconds(
        Decimal(_full_mahadasha_microseconds(birth_lord)) * (Decimal("1") - elapsed_fraction)
    )
    full_microseconds = _full_mahadasha_microseconds(birth_lord)
    elapsed_microseconds = full_microseconds - remaining_microseconds
    start = birth_instant - timedelta(microseconds=elapsed_microseconds)
    if remaining_microseconds == 0:
        return _DashaState(lord=_next_lord(birth_lord), start=birth_instant)
    return _DashaState(lord=birth_lord, start=start)


def _mahadasha_period(lord: DashaLord, start: datetime) -> MahadashaPeriod:
    duration = _full_mahadasha_microseconds(lord)
    end = start + timedelta(microseconds=duration)
    return MahadashaPeriod(
        lord=lord,
        start=start,
        end=end,
        antardashas=_antardasha_periods(lord, start, end, duration),
    )


def _antardasha_periods(
    mahadasha_lord: DashaLord,
    start: datetime,
    end: datetime,
    parent_microseconds: int,
) -> tuple[AntardashaPeriod, ...]:
    cumulative_years = 0
    periods: list[AntardashaPeriod] = []
    period_start = start
    lords = _cycle_from(mahadasha_lord)
    for index, lord in enumerate(lords):
        cumulative_years += _MAHADASHA_YEARS[lord]
        if index == len(lords) - 1:
            period_end = end
        else:
            offset = _quantize_microseconds(
                Decimal(parent_microseconds)
                * Decimal(cumulative_years)
                / Decimal(_TOTAL_DASHA_YEARS)
            )
            period_end = start + timedelta(microseconds=offset)
        periods.append(
            AntardashaPeriod(
                mahadasha_lord=mahadasha_lord,
                lord=lord,
                start=period_start,
                end=period_end,
            )
        )
        period_start = period_end
    return tuple(periods)


def _moon_from_chart(chart: Chart) -> ChartPlanet:
    if chart.methodology.chart_type != "D1/Rashi":
        raise ValueError("Vimshottari requires a canonical D1/Rashi source chart")
    configuration = chart.methodology.configuration
    if (
        configuration.zodiac is not ZodiacSystem.SIDEREAL
        or configuration.ayanamsa is not Ayanamsa.LAHIRI
    ):
        raise ValueError("Vimshottari v1 requires a sidereal Lahiri source chart")
    if chart.calculation_instant != chart.birth_input.utc_datetime:
        raise ValueError("source chart calculation instant must equal the birth instant")
    moons = tuple(planet for planet in chart.planets if planet.body is CelestialBody.MOON)
    if len(moons) != 1:
        raise ValueError("source chart must contain exactly one D1 Moon fact")
    moon = moons[0]
    if moon.nakshatra != nakshatra_for_longitude(moon.longitude):
        raise ValueError("source chart Moon nakshatra is inconsistent with its longitude")
    return moon


def _provenance(chart: Chart) -> DashaProvenance:
    moon = _moon_from_chart(chart)
    birth_nakshatra = moon.nakshatra.nakshatra
    return DashaProvenance(
        methodology=VimshottariMethodology(
            source_d1_moon_longitude=moon.longitude,
            birth_nakshatra=birth_nakshatra,
            birth_nakshatra_lord=lord_for_nakshatra(birth_nakshatra),
        ),
        source_chart_calculation_instant=chart.calculation_instant,
        source_chart_methodology=chart.methodology,
        inherited_ephemeris_provenance=chart.provenance,
        source_birth_timezone=chart.birth_input.timezone,
    )


def _as_utc(value: datetime, name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


def _full_mahadasha_microseconds(lord: DashaLord) -> int:
    return _MAHADASHA_YEARS[lord] * _DASHA_YEAR_MICROSECONDS


def _quantize_microseconds(value: Decimal) -> int:
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_EVEN))


def _next_lord(lord: DashaLord) -> DashaLord:
    return _LORD_SEQUENCE[(_LORD_SEQUENCE.index(lord) + 1) % len(_LORD_SEQUENCE)]


def _cycle_from(lord: DashaLord) -> tuple[DashaLord, ...]:
    index = _LORD_SEQUENCE.index(lord)
    return _LORD_SEQUENCE[index:] + _LORD_SEQUENCE[:index]
