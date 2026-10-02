"""Provider-neutral deterministic D1/Rashi chart facts."""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from astrologer.astrology.ascendant import AscendantProvider, AscendantRequest
from astrologer.astrology.ephemeris import (
    CelestialBody,
    EphemerisConfiguration,
    EphemerisProvenance,
    EphemerisProvider,
    EphemerisRequest,
    HouseSystem,
    Longitude,
    PlanetaryPosition,
)
from astrologer.birth.models import BirthInput

_SIGN_SIZE = Decimal("30")
_NAKSHATRA_SIZE = Decimal("40") / Decimal("3")
_PADA_SIZE = _NAKSHATRA_SIZE / Decimal("4")


class ZodiacSign(StrEnum):
    """The twelve sidereal zodiac signs in ordinal order."""

    ARIES = "aries"
    TAURUS = "taurus"
    GEMINI = "gemini"
    CANCER = "cancer"
    LEO = "leo"
    VIRGO = "virgo"
    LIBRA = "libra"
    SCORPIO = "scorpio"
    SAGITTARIUS = "sagittarius"
    CAPRICORN = "capricorn"
    AQUARIUS = "aquarius"
    PISCES = "pisces"


_SIGNS = tuple(ZodiacSign)
_REQUIRED_BODIES = tuple(CelestialBody)


class Nakshatra(StrEnum):
    """The 27 nakshatras in sidereal longitude order from Aries zero."""

    ASHWINI = "ashwini"
    BHARANI = "bharani"
    KRITTIKA = "krittika"
    ROHINI = "rohini"
    MRIGASHIRSHA = "mrigashirsha"
    ARDRA = "ardra"
    PUNARVASU = "punarvasu"
    PUSHYA = "pushya"
    ASHLESHA = "ashlesha"
    MAGHA = "magha"
    PURVA_PHALGUNI = "purva_phalguni"
    UTTARA_PHALGUNI = "uttara_phalguni"
    HASTA = "hasta"
    CHITRA = "chitra"
    SWATI = "swati"
    VISHAKHA = "vishakha"
    ANURADHA = "anuradha"
    JYESHTHA = "jyeshtha"
    MULA = "mula"
    PURVA_ASHADHA = "purva_ashadha"
    UTTARA_ASHADHA = "uttara_ashadha"
    SHRAVANA = "shravana"
    DHANISHTHA = "dhanishtha"
    SHATABHISHA = "shatabhisha"
    PURVA_BHADRAPADA = "purva_bhadrapada"
    UTTARA_BHADRAPADA = "uttara_bhadrapada"
    REVATI = "revati"


_NAKSHATRAS = tuple(Nakshatra)


class NakshatraPlacement(BaseModel):
    """Deterministic nakshatra and pada derived from a sidereal longitude."""

    model_config = ConfigDict(frozen=True)

    nakshatra: Nakshatra
    pada: int = Field(ge=1, le=4)


class ChartMethodology(BaseModel):
    """Versioned methodology facts used to produce a D1 chart."""

    model_config = ConfigDict(frozen=True)

    tradition: str = "vedic/jyotish"
    chart_type: str = "D1/Rashi"
    configuration: EphemerisConfiguration


class Ascendant(BaseModel):
    """Sidereal ascendant fact used as the Whole Sign house anchor."""

    model_config = ConfigDict(frozen=True)

    longitude: Longitude
    sign: ZodiacSign
    degree_in_sign: Decimal = Field(ge=Decimal("0"), lt=_SIGN_SIZE)
    nakshatra: NakshatraPlacement


class WholeSignHouse(BaseModel):
    """One Whole Sign house; no quadrant-house calculation is represented."""

    model_config = ConfigDict(frozen=True)

    number: int = Field(ge=1, le=12)
    sign: ZodiacSign


class ChartPlanet(BaseModel):
    """Provider-neutral D1 fact for one requested body or lunar node."""

    model_config = ConfigDict(frozen=True)

    body: CelestialBody
    longitude: Longitude
    sign: ZodiacSign
    degree_in_sign: Decimal = Field(ge=Decimal("0"), lt=_SIGN_SIZE)
    nakshatra: NakshatraPlacement
    house_number: int = Field(ge=1, le=12)
    ecliptic_latitude: Decimal | None = None
    distance: Decimal | None = None
    motion_speed: Decimal | None = None
    retrograde_input: bool | None = None
    retrograde: bool | None = None


class Chart(BaseModel):
    """Canonical deterministic D1/Rashi chart containing facts only."""

    model_config = ConfigDict(frozen=True)

    methodology: ChartMethodology
    birth_input: BirthInput
    calculation_instant: datetime
    ascendant: Ascendant
    houses: tuple[WholeSignHouse, ...]
    planets: tuple[ChartPlanet, ...]
    provenance: EphemerisProvenance


class IncompleteEphemerisResultError(RuntimeError):
    """Raised when a provider omits a required D1 body."""


class ChartEngine:
    """Build a D1 chart from provider-neutral deterministic calculations."""

    def __init__(self, provider: EphemerisProvider) -> None:
        if not isinstance(provider, AscendantProvider):
            msg = "The D1 chart engine requires a provider with ascendant capability"
            raise TypeError(msg)
        self._provider = provider
        self._ascendant_provider = provider

    def calculate(
        self,
        birth_input: BirthInput,
        configuration: EphemerisConfiguration | None = None,
    ) -> Chart:
        """Calculate deterministic D1 facts using the approved MVP conventions."""
        requested_configuration = configuration or EphemerisConfiguration()
        if requested_configuration.house_system is not HouseSystem.WHOLE_SIGN:
            msg = "Only Whole Sign houses are supported by the D1 chart engine"
            raise ValueError(msg)

        position_result = self._provider.calculate(
            EphemerisRequest(
                calculation_instant=birth_input.utc_datetime,
                configuration=requested_configuration,
                requested_bodies=_REQUIRED_BODIES,
            )
        )
        ascendant_result = self._ascendant_provider.calculate_ascendant(
            AscendantRequest(
                calculation_instant=birth_input.utc_datetime,
                latitude=birth_input.latitude,
                longitude=birth_input.longitude,
                configuration=requested_configuration,
            )
        )
        positions_by_body = {position.body: position for position in position_result.positions}
        missing_bodies = set(_REQUIRED_BODIES) - set(positions_by_body)
        if missing_bodies:
            missing = ", ".join(sorted(body.value for body in missing_bodies))
            raise IncompleteEphemerisResultError(
                f"Ephemeris provider omitted required bodies: {missing}"
            )

        ascendant_sign = sign_for_longitude(ascendant_result.longitude)
        ascendant = Ascendant(
            longitude=ascendant_result.longitude,
            sign=ascendant_sign,
            degree_in_sign=degree_in_sign(ascendant_result.longitude),
            nakshatra=nakshatra_for_longitude(ascendant_result.longitude),
        )
        houses = _whole_sign_houses(ascendant_sign)
        planets = tuple(
            _chart_planet(positions_by_body[body], ascendant_sign) for body in _REQUIRED_BODIES
        )
        return Chart(
            methodology=ChartMethodology(configuration=position_result.provenance.configuration),
            birth_input=birth_input,
            calculation_instant=birth_input.utc_datetime,
            ascendant=ascendant,
            houses=houses,
            planets=planets,
            provenance=position_result.provenance,
        )


def sign_for_longitude(longitude: Decimal) -> ZodiacSign:
    """Map a normalized longitude to its zero-based sidereal zodiac sign."""
    return _SIGNS[int(longitude // _SIGN_SIZE)]


def degree_in_sign(longitude: Decimal) -> Decimal:
    """Return the unrounded degree offset within a zodiac sign."""
    return longitude % _SIGN_SIZE


def nakshatra_for_longitude(longitude: Decimal) -> NakshatraPlacement:
    """Derive the 27-nakshatra position and four-pada position from longitude."""
    normalized_longitude = longitude % Decimal("360")
    nakshatra_index = int(normalized_longitude // _NAKSHATRA_SIZE)
    degree_in_nakshatra = normalized_longitude % _NAKSHATRA_SIZE
    return NakshatraPlacement(
        nakshatra=_NAKSHATRAS[nakshatra_index],
        pada=int(degree_in_nakshatra // _PADA_SIZE) + 1,
    )


def _whole_sign_houses(ascendant_sign: ZodiacSign) -> tuple[WholeSignHouse, ...]:
    ascendant_index = _SIGNS.index(ascendant_sign)
    return tuple(
        WholeSignHouse(number=number, sign=_SIGNS[(ascendant_index + number - 1) % 12])
        for number in range(1, 13)
    )


def _chart_planet(position: PlanetaryPosition, ascendant_sign: ZodiacSign) -> ChartPlanet:
    sign = sign_for_longitude(position.longitude)
    house_number = ((_SIGNS.index(sign) - _SIGNS.index(ascendant_sign)) % 12) + 1
    return ChartPlanet(
        body=position.body,
        longitude=position.longitude,
        sign=sign,
        degree_in_sign=degree_in_sign(position.longitude),
        nakshatra=nakshatra_for_longitude(position.longitude),
        house_number=house_number,
        ecliptic_latitude=position.ecliptic_latitude,
        distance=position.distance,
        motion_speed=position.motion_speed,
        retrograde_input=position.retrograde_input,
        retrograde=position.retrograde_input,
    )
