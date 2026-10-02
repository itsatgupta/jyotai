"""Provider-neutral contracts for deterministic ephemeris calculations.

This module intentionally contains no astronomical algorithm or third-party
ephemeris integration. Concrete providers must translate their own API values
into these models at the boundary.
"""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ZodiacSystem(StrEnum):
    """Zodiac systems recognized by the initial deterministic contract."""

    SIDEREAL = "sidereal"


class Ayanamsa(StrEnum):
    """Ayanamsa selected by the provisional MVP methodology."""

    LAHIRI = "lahiri"


class LunarNodeDefinition(StrEnum):
    """Supported lunar-node definitions."""

    TRUE = "true"
    MEAN = "mean"


class HouseSystem(StrEnum):
    """House-system provenance; no house calculation occurs in this module."""

    WHOLE_SIGN = "whole_sign"


class CoordinateOrigin(StrEnum):
    """Observer origin for returned positions."""

    GEOCENTRIC = "geocentric"
    TOPOCENTRIC = "topocentric"


class PositionReference(StrEnum):
    """Astronomical reference style for returned positions."""

    APPARENT = "apparent"
    ASTROMETRIC = "astrometric"


class TimeScale(StrEnum):
    """Time scale of the provider-neutral input instant."""

    UTC = "utc"


class CelestialBody(StrEnum):
    """Bodies and node points required by the initial methodology."""

    SUN = "sun"
    MOON = "moon"
    MARS = "mars"
    MERCURY = "mercury"
    JUPITER = "jupiter"
    VENUS = "venus"
    SATURN = "saturn"
    RAHU = "rahu"
    KETU = "ketu"


Longitude = Annotated[Decimal, Field(ge=Decimal("0"), lt=Decimal("360"))]
EclipticLatitude = Annotated[Decimal, Field(ge=Decimal("-90"), le=Decimal("90"))]
NonNegativeDecimal = Annotated[Decimal, Field(ge=Decimal("0"))]


class CalculationFlags(BaseModel):
    """Explicit calculation choices that affect reproducibility."""

    model_config = ConfigDict(frozen=True)

    coordinate_origin: CoordinateOrigin = CoordinateOrigin.GEOCENTRIC
    position_reference: PositionReference = PositionReference.APPARENT
    time_scale: TimeScale = TimeScale.UTC
    require_ecliptic_latitude: bool = False
    require_distance: bool = False
    require_motion_speed: bool = True
    require_retrograde_input: bool = True


class EphemerisConfiguration(BaseModel):
    """Provider-neutral implementation of the provisional MVP conventions."""

    model_config = ConfigDict(frozen=True)

    zodiac: ZodiacSystem = ZodiacSystem.SIDEREAL
    ayanamsa: Ayanamsa = Ayanamsa.LAHIRI
    ayanamsa_provider_mode: str | None = None
    lunar_node_definition: LunarNodeDefinition = LunarNodeDefinition.TRUE
    house_system: HouseSystem = HouseSystem.WHOLE_SIGN
    flags: CalculationFlags = Field(default_factory=CalculationFlags)


class EphemerisRequest(BaseModel):
    """A UTC calculation request with no provider-specific objects."""

    model_config = ConfigDict(frozen=True)

    calculation_instant: datetime
    configuration: EphemerisConfiguration = Field(default_factory=EphemerisConfiguration)
    requested_bodies: tuple[CelestialBody, ...] = ()

    @field_validator("calculation_instant")
    @classmethod
    def calculation_instant_must_be_utc(cls, value: datetime) -> datetime:
        """Accept only an aware UTC instant and normalize its UTC tzinfo."""
        if value.tzinfo is None or value.utcoffset() != timedelta(0):
            msg = "calculation_instant must be timezone-aware UTC"
            raise ValueError(msg)
        return value.astimezone(UTC)


class PlanetaryPosition(BaseModel):
    """A typed, provider-neutral position returned by an ephemeris provider."""

    model_config = ConfigDict(frozen=True)

    body: CelestialBody
    longitude: Longitude
    ecliptic_latitude: EclipticLatitude | None = None
    distance: NonNegativeDecimal | None = None
    motion_speed: Decimal | None = None
    retrograde_input: bool | None = None


class ProviderMetadata(BaseModel):
    """Versioned provider and ephemeris-data provenance."""

    model_config = ConfigDict(frozen=True)

    provider_name: str = Field(min_length=1)
    provider_version: str = Field(min_length=1)
    library_version: str | None = None
    ephemeris_data_version: str | None = None
    ephemeris_data_hash: str | None = None


class ProviderCapabilities(BaseModel):
    """Capabilities used to fail unsupported requests explicitly."""

    model_config = ConfigDict(frozen=True)

    supports_sidereal_zodiac: bool = True
    supported_ayanamsas: frozenset[Ayanamsa] = Field(default_factory=frozenset)
    supported_node_definitions: frozenset[LunarNodeDefinition] = Field(default_factory=frozenset)
    supported_bodies: frozenset[CelestialBody] = Field(default_factory=frozenset)
    supports_ecliptic_latitude: bool = False
    supports_distance: bool = False
    supports_motion_speed: bool = False
    supports_retrograde_input: bool = False


class EphemerisProvenance(BaseModel):
    """Provider-neutral provenance for one deterministic calculation result."""

    model_config = ConfigDict(frozen=True)

    provider: ProviderMetadata
    calculation_instant: datetime
    configuration: EphemerisConfiguration


class EphemerisResult(BaseModel):
    """Provider-neutral calculation result; it contains no library objects."""

    model_config = ConfigDict(frozen=True)

    positions: tuple[PlanetaryPosition, ...]
    provenance: EphemerisProvenance


class UnsupportedProviderCapabilityError(ValueError):
    """Raised when a provider cannot satisfy an explicit request requirement."""

    def __init__(self, provider_name: str, capability: str) -> None:
        self.provider_name = provider_name
        self.capability = capability
        super().__init__(f"Provider '{provider_name}' does not support capability: {capability}")


@runtime_checkable
class EphemerisProvider(Protocol):
    """Boundary implemented by any deterministic ephemeris integration."""

    @property
    def metadata(self) -> ProviderMetadata:
        """Return version and data provenance for this provider."""
        ...

    @property
    def capabilities(self) -> ProviderCapabilities:
        """Return the explicit capabilities of this provider."""
        ...

    def calculate(self, request: EphemerisRequest) -> EphemerisResult:
        """Calculate positions for a validated request."""
        ...


def validate_provider_capabilities(provider: EphemerisProvider, request: EphemerisRequest) -> None:
    """Fail explicitly when a request needs unsupported provider features."""
    capabilities = provider.capabilities
    provider_name = provider.metadata.provider_name

    if (
        request.configuration.zodiac is ZodiacSystem.SIDEREAL
        and not capabilities.supports_sidereal_zodiac
    ):
        raise UnsupportedProviderCapabilityError(provider_name, "sidereal_zodiac")
    if request.configuration.ayanamsa not in capabilities.supported_ayanamsas:
        raise UnsupportedProviderCapabilityError(provider_name, "ayanamsa:lahiri")
    if request.configuration.lunar_node_definition not in capabilities.supported_node_definitions:
        node_definition = request.configuration.lunar_node_definition.value
        raise UnsupportedProviderCapabilityError(provider_name, f"lunar_nodes:{node_definition}")
    if not set(request.requested_bodies).issubset(capabilities.supported_bodies):
        raise UnsupportedProviderCapabilityError(provider_name, "requested_bodies")
    if (
        request.configuration.flags.require_ecliptic_latitude
        and not capabilities.supports_ecliptic_latitude
    ):
        raise UnsupportedProviderCapabilityError(provider_name, "ecliptic_latitude")
    if request.configuration.flags.require_distance and not capabilities.supports_distance:
        raise UnsupportedProviderCapabilityError(provider_name, "distance")
    if request.configuration.flags.require_motion_speed and not capabilities.supports_motion_speed:
        raise UnsupportedProviderCapabilityError(provider_name, "motion_speed")
    if (
        request.configuration.flags.require_retrograde_input
        and not capabilities.supports_retrograde_input
    ):
        raise UnsupportedProviderCapabilityError(provider_name, "retrograde_input")
