"""Swiss Ephemeris adapter for local deterministic chart testing.

All Swiss/PySwissEph types, flags, and global state are contained in this
module. The rest of the application consumes only provider-neutral models.
"""

from datetime import UTC, datetime
from decimal import Decimal
from importlib.metadata import version
from threading import Lock
from typing import cast

import swisseph as swe  # type: ignore[import-not-found]

from astrologer.astrology.ascendant import AscendantRequest, AscendantResult
from astrologer.astrology.ephemeris import (
    Ayanamsa,
    CelestialBody,
    CoordinateOrigin,
    EphemerisConfiguration,
    EphemerisProvenance,
    EphemerisRequest,
    EphemerisResult,
    LunarNodeDefinition,
    PlanetaryPosition,
    PositionReference,
    ProviderCapabilities,
    ProviderMetadata,
    UnsupportedProviderCapabilityError,
    validate_provider_capabilities,
)

SWISS_LAHIRI_MODE = "SIDM_LAHIRI"

_BODY_CODES: dict[CelestialBody, int] = {
    CelestialBody.SUN: swe.SUN,
    CelestialBody.MOON: swe.MOON,
    CelestialBody.MARS: swe.MARS,
    CelestialBody.MERCURY: swe.MERCURY,
    CelestialBody.JUPITER: swe.JUPITER,
    CelestialBody.VENUS: swe.VENUS,
    CelestialBody.SATURN: swe.SATURN,
}
_SWISS_GLOBAL_STATE_LOCK = Lock()


class SwissEphemerisCalculationError(RuntimeError):
    """Raised when the Swiss adapter cannot produce a deterministic result."""


class SwissEphemerisProvider:
    """Translate Swiss Ephemeris values into the provider-neutral contract."""

    def __init__(self) -> None:
        self._metadata = ProviderMetadata(
            provider_name="pyswisseph",
            provider_version=version("pyswisseph"),
            library_version=str(swe.version),
        )
        self._capabilities = ProviderCapabilities(
            supported_ayanamsas=frozenset({Ayanamsa.LAHIRI}),
            supported_node_definitions=frozenset({LunarNodeDefinition.TRUE}),
            supported_bodies=frozenset(CelestialBody),
            supports_ecliptic_latitude=True,
            supports_distance=True,
            supports_motion_speed=True,
            supports_retrograde_input=True,
        )

    @property
    def metadata(self) -> ProviderMetadata:
        """Return installed binding and native-library version metadata."""
        return self._metadata

    @property
    def capabilities(self) -> ProviderCapabilities:
        """Return the supported deterministic calculation features."""
        return self._capabilities

    def calculate(self, request: EphemerisRequest) -> EphemerisResult:
        """Calculate requested geocentric sidereal positions with Swiss Ephemeris."""
        validate_provider_capabilities(self, request)
        configuration = self._validate_configuration(request.configuration)
        julian_day_ut = _utc_datetime_to_julian_day_ut(request.calculation_instant)

        try:
            with _SWISS_GLOBAL_STATE_LOCK:
                swe.set_sid_mode(swe.SIDM_LAHIRI)
                positions, return_flags = self._calculate_positions(
                    julian_day_ut,
                    request.requested_bodies,
                )
        except swe.Error as error:
            raise SwissEphemerisCalculationError(str(error)) from error

        provenance = EphemerisProvenance(
            provider=self._metadata_for_return_flags(return_flags),
            calculation_instant=request.calculation_instant,
            configuration=configuration,
        )
        return EphemerisResult(positions=positions, provenance=provenance)

    def calculate_ascendant(self, request: AscendantRequest) -> AscendantResult:
        """Calculate a sidereal ascendant while keeping Swiss details internal."""
        if not isinstance(request.calculation_instant, datetime):
            msg = "calculation_instant must be a datetime"
            raise ValueError(msg)
        ephemeris_request = EphemerisRequest(
            calculation_instant=request.calculation_instant,
            configuration=request.configuration,
        )
        validate_provider_capabilities(self, ephemeris_request)
        configuration = self._validate_configuration(request.configuration)
        julian_day_ut = _utc_datetime_to_julian_day_ut(ephemeris_request.calculation_instant)

        try:
            with _SWISS_GLOBAL_STATE_LOCK:
                swe.set_sid_mode(swe.SIDM_LAHIRI)
                _, ascmc = cast(
                    tuple[tuple[float, ...], tuple[float, ...]],
                    swe.houses_ex(
                        julian_day_ut,
                        request.latitude,
                        request.longitude,
                        b"W",
                        swe.FLG_SIDEREAL,
                    ),
                )
        except swe.Error as error:
            raise SwissEphemerisCalculationError(str(error)) from error

        return AscendantResult(
            longitude=_decimal_longitude(ascmc[0]),
            provenance=EphemerisProvenance(
                provider=self.metadata,
                calculation_instant=ephemeris_request.calculation_instant,
                configuration=configuration,
            ),
        )

    def _validate_configuration(
        self, configuration: EphemerisConfiguration
    ) -> EphemerisConfiguration:
        if configuration.ayanamsa_provider_mode not in (None, SWISS_LAHIRI_MODE):
            raise UnsupportedProviderCapabilityError(
                self.metadata.provider_name, "ayanamsa_provider_mode"
            )
        if configuration.flags.coordinate_origin is not CoordinateOrigin.GEOCENTRIC:
            raise UnsupportedProviderCapabilityError(
                self.metadata.provider_name, "coordinate_origin"
            )
        if configuration.flags.position_reference is not PositionReference.APPARENT:
            raise UnsupportedProviderCapabilityError(
                self.metadata.provider_name, "position_reference"
            )
        return configuration.model_copy(update={"ayanamsa_provider_mode": SWISS_LAHIRI_MODE})

    def _calculate_positions(
        self,
        julian_day_ut: float,
        requested_bodies: tuple[CelestialBody, ...],
    ) -> tuple[tuple[PlanetaryPosition, ...], int]:
        positions: list[PlanetaryPosition] = []
        return_flags: int | None = None
        regular_bodies = [body for body in requested_bodies if body in _BODY_CODES]

        for body in regular_bodies:
            values, flags = _calculate_swiss_body(julian_day_ut, _BODY_CODES[body])
            return_flags = _consistent_return_flags(return_flags, flags)
            positions.append(_position_from_swiss_values(body, values))

        if CelestialBody.RAHU in requested_bodies or CelestialBody.KETU in requested_bodies:
            values, flags = _calculate_swiss_body(julian_day_ut, swe.TRUE_NODE)
            return_flags = _consistent_return_flags(return_flags, flags)
            rahu = _position_from_swiss_values(CelestialBody.RAHU, values)
            if CelestialBody.RAHU in requested_bodies:
                positions.append(rahu)
            if CelestialBody.KETU in requested_bodies:
                positions.append(_ketu_from_rahu(rahu))

        if return_flags is None:
            msg = "at least one celestial body must be requested"
            raise SwissEphemerisCalculationError(msg)
        return tuple(positions), return_flags

    def _metadata_for_return_flags(self, return_flags: int) -> ProviderMetadata:
        if return_flags & swe.FLG_MOSEPH:
            data_source = "Moshier internal ephemeris"
        elif return_flags & swe.FLG_SWIEPH:
            data_source = "Swiss Ephemeris data files"
        elif return_flags & swe.FLG_JPLEPH:
            data_source = "JPL ephemeris data files"
        else:
            data_source = "Swiss Ephemeris data source not identified"
        return self.metadata.model_copy(update={"ephemeris_data_version": data_source})


def _utc_datetime_to_julian_day_ut(instant: datetime) -> float:
    utc_instant = instant.astimezone(UTC)
    hour = (
        utc_instant.hour
        + utc_instant.minute / 60
        + utc_instant.second / 3600
        + utc_instant.microsecond / 3_600_000_000
    )
    return float(
        swe.julday(
            utc_instant.year,
            utc_instant.month,
            utc_instant.day,
            hour,
            swe.GREG_CAL,
        )
    )


def _calculate_swiss_body(julian_day_ut: float, body_code: int) -> tuple[tuple[float, ...], int]:
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
    values, return_flags = cast(
        tuple[tuple[float, ...], int],
        swe.calc_ut(julian_day_ut, body_code, flags),
    )
    return values, return_flags


def _position_from_swiss_values(
    body: CelestialBody,
    values: tuple[float, ...],
) -> PlanetaryPosition:
    return PlanetaryPosition(
        body=body,
        longitude=_decimal_longitude(values[0]),
        ecliptic_latitude=Decimal(str(values[1])),
        distance=Decimal(str(values[2])),
        motion_speed=Decimal(str(values[3])),
        retrograde_input=values[3] < 0,
    )


def _ketu_from_rahu(rahu: PlanetaryPosition) -> PlanetaryPosition:
    """Derive Ketu as the mathematically opposite point of the true north node."""
    return PlanetaryPosition(
        body=CelestialBody.KETU,
        longitude=(rahu.longitude + Decimal("180")) % Decimal("360"),
        ecliptic_latitude=-rahu.ecliptic_latitude if rahu.ecliptic_latitude is not None else None,
        distance=rahu.distance,
        motion_speed=rahu.motion_speed,
        retrograde_input=rahu.retrograde_input,
    )


def _decimal_longitude(value: float) -> Decimal:
    return Decimal(str(value)) % Decimal("360")


def _consistent_return_flags(current: int | None, candidate: int) -> int:
    if current is not None and current != candidate:
        msg = "Swiss Ephemeris returned inconsistent source flags for one request"
        raise SwissEphemerisCalculationError(msg)
    return candidate
