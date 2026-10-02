"""Deterministic Parashari divisional-chart derivation from a D1 chart.

Vargas transform already-calculated sidereal D1 longitudes.  They do not call
an ephemeris provider and their synthetic longitudes are not astronomical
positions returned by a provider.
"""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from astrologer.astrology.chart import (
    Chart,
    ChartMethodology,
    ChartPlanet,
    WholeSignHouse,
    ZodiacSign,
    _whole_sign_houses,
    degree_in_sign,
    sign_for_longitude,
)
from astrologer.astrology.ephemeris import CelestialBody, EphemerisProvenance, Longitude
from astrologer.birth.models import BirthInput

_SIGN_SIZE = Decimal("30")
_SIGNS = tuple(ZodiacSign)
_MOVABLE_SIGN_INDICES = frozenset({0, 3, 6, 9})
_FIXED_SIGN_INDICES = frozenset({1, 4, 7, 10})
_DUAL_SIGN_INDICES = frozenset({2, 5, 8, 11})


class DivisionalChartType(StrEnum):
    """The explicitly supported initial divisional charts."""

    D1 = "d1"
    D2 = "d2"
    D9 = "d9"
    D10 = "d10"


class VargaMappingVariant(StrEnum):
    """Versioned mapping convention used for an initial Varga."""

    RASHI_IDENTITY = "rashi_identity"
    PARASHARI_SUN_MOON_HORA = "parashari_sun_moon_hora"
    PARASHARI_NAVAMSA = "parashari_navamsa"
    PARASHARI_DASAMSA = "parashari_dasamsa"


class VargaMethodology(BaseModel):
    """Traceable methodology for a Varga derived from a canonical D1 chart."""

    model_config = ConfigDict(frozen=True)

    tradition: str = "vedic/jyotish"
    chart_type: DivisionalChartType
    division_factor: int = Field(ge=1)
    mapping_variant: VargaMappingVariant
    source_chart_methodology: ChartMethodology


class VargaAscendant(BaseModel):
    """A divisional ascendant derived from the D1 ascendant longitude."""

    model_config = ConfigDict(frozen=True)

    source_d1_longitude: Longitude
    longitude: Longitude
    sign: ZodiacSign
    degree_in_sign: Decimal = Field(ge=Decimal("0"), lt=_SIGN_SIZE)


class VargaPlanet(BaseModel):
    """A divisional placement derived from one D1 planetary longitude.

    Inherited motion facts are copied from D1 and are not recalculated for the
    synthetic divisional longitude.
    """

    model_config = ConfigDict(frozen=True)

    body: CelestialBody
    source_d1_longitude: Longitude
    longitude: Longitude
    sign: ZodiacSign
    degree_in_sign: Decimal = Field(ge=Decimal("0"), lt=_SIGN_SIZE)
    house_number: int = Field(ge=1, le=12)
    inherited_motion_speed: Decimal | None = None
    inherited_retrograde: bool | None = None


class DivisionalChart(BaseModel):
    """Immutable facts for a Varga derived exclusively from a D1 chart."""

    model_config = ConfigDict(frozen=True)

    methodology: VargaMethodology
    birth_input: BirthInput
    calculation_instant: datetime
    ascendant: VargaAscendant
    houses: tuple[WholeSignHouse, ...]
    planets: tuple[VargaPlanet, ...]
    provenance: EphemerisProvenance


class VargaEngine:
    """Build initial Varga facts without provider access or ephemeris calls."""

    def calculate(self, source_chart: Chart, chart_type: DivisionalChartType) -> DivisionalChart:
        """Derive one requested divisional chart from the supplied D1 chart."""
        factor, variant = _methodology_for(chart_type)
        ascendant_longitude = derive_varga_longitude(source_chart.ascendant.longitude, chart_type)
        ascendant_sign = sign_for_longitude(ascendant_longitude)
        ascendant = VargaAscendant(
            source_d1_longitude=source_chart.ascendant.longitude,
            longitude=ascendant_longitude,
            sign=ascendant_sign,
            degree_in_sign=degree_in_sign(ascendant_longitude),
        )
        planets = tuple(
            _varga_planet(planet, ascendant_sign, chart_type) for planet in source_chart.planets
        )
        return DivisionalChart(
            methodology=VargaMethodology(
                chart_type=chart_type,
                division_factor=factor,
                mapping_variant=variant,
                source_chart_methodology=source_chart.methodology,
            ),
            birth_input=source_chart.birth_input,
            calculation_instant=source_chart.calculation_instant,
            ascendant=ascendant,
            houses=_whole_sign_houses(ascendant_sign),
            planets=planets,
            provenance=source_chart.provenance,
        )

    def calculate_all(self, source_chart: Chart) -> tuple[DivisionalChart, ...]:
        """Derive every Varga explicitly supported by this initial milestone."""
        return tuple(self.calculate(source_chart, chart_type) for chart_type in DivisionalChartType)


def derive_varga_longitude(
    source_d1_longitude: Longitude,
    chart_type: DivisionalChartType,
) -> Longitude:
    """Transform one normalized D1 longitude using the selected fixed convention."""
    sign_index = _SIGNS.index(sign_for_longitude(source_d1_longitude))
    source_degree = degree_in_sign(source_d1_longitude)
    factor, _ = _methodology_for(chart_type)
    division_index = int(source_degree * factor // _SIGN_SIZE)
    target_sign_index = _target_sign_index(sign_index, division_index, chart_type)
    varga_degree = (source_degree * factor) % _SIGN_SIZE
    return Decimal(target_sign_index) * _SIGN_SIZE + varga_degree


def _methodology_for(chart_type: DivisionalChartType) -> tuple[int, VargaMappingVariant]:
    return {
        DivisionalChartType.D1: (1, VargaMappingVariant.RASHI_IDENTITY),
        DivisionalChartType.D2: (2, VargaMappingVariant.PARASHARI_SUN_MOON_HORA),
        DivisionalChartType.D9: (9, VargaMappingVariant.PARASHARI_NAVAMSA),
        DivisionalChartType.D10: (10, VargaMappingVariant.PARASHARI_DASAMSA),
    }[chart_type]


def _target_sign_index(
    source_sign_index: int,
    division_index: int,
    chart_type: DivisionalChartType,
) -> int:
    if chart_type is DivisionalChartType.D1:
        return source_sign_index
    if chart_type is DivisionalChartType.D2:
        return _hora_target_sign_index(source_sign_index, division_index)
    if chart_type is DivisionalChartType.D9:
        return (_navamsa_start_sign_index(source_sign_index) + division_index) % 12
    if chart_type is DivisionalChartType.D10:
        return (_dasamsa_start_sign_index(source_sign_index) + division_index) % 12
    msg = f"Unsupported divisional chart type: {chart_type}"
    raise ValueError(msg)


def _hora_target_sign_index(source_sign_index: int, division_index: int) -> int:
    """Apply Parashari Sun/Moon Hora: Leo/Cancer for odd signs, reversed for even."""
    leo_index = _SIGNS.index(ZodiacSign.LEO)
    cancer_index = _SIGNS.index(ZodiacSign.CANCER)
    if source_sign_index % 2 == 0:
        return (leo_index, cancer_index)[division_index]
    return (cancer_index, leo_index)[division_index]


def _navamsa_start_sign_index(source_sign_index: int) -> int:
    """Use the explicit Parashari movable/fixed/dual Navamsa starting signs."""
    if source_sign_index in _MOVABLE_SIGN_INDICES:
        return source_sign_index
    if source_sign_index in _FIXED_SIGN_INDICES:
        return (source_sign_index + 8) % 12
    if source_sign_index in _DUAL_SIGN_INDICES:
        return (source_sign_index + 4) % 12
    msg = f"Invalid zodiac sign index: {source_sign_index}"
    raise ValueError(msg)


def _dasamsa_start_sign_index(source_sign_index: int) -> int:
    """Use same-sign starts for odd signs and ninth-sign starts for even signs."""
    if source_sign_index % 2 == 0:
        return source_sign_index
    return (source_sign_index + 8) % 12


def _varga_planet(
    source_planet: ChartPlanet,
    ascendant_sign: ZodiacSign,
    chart_type: DivisionalChartType,
) -> VargaPlanet:
    """Derive one Varga placement while retaining only explicitly inherited motion facts."""
    source_longitude = source_planet.longitude
    longitude = derive_varga_longitude(source_longitude, chart_type)
    sign = sign_for_longitude(longitude)
    house_number = ((_SIGNS.index(sign) - _SIGNS.index(ascendant_sign)) % 12) + 1
    return VargaPlanet(
        body=source_planet.body,
        source_d1_longitude=source_longitude,
        longitude=longitude,
        sign=sign,
        degree_in_sign=degree_in_sign(longitude),
        house_number=house_number,
        inherited_motion_speed=source_planet.motion_speed,
        inherited_retrograde=source_planet.retrograde,
    )
