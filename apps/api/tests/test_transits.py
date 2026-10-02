"""Deterministic unit and Swiss-adapter invariant tests for transit-v1."""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from astrologer.astrology.chart import Nakshatra
from astrologer.astrology.ephemeris import (
    Ayanamsa,
    CelestialBody,
    EphemerisProvenance,
    EphemerisRequest,
    EphemerisResult,
    LunarNodeDefinition,
    PlanetaryPosition,
    ProviderCapabilities,
    ProviderMetadata,
)
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.astrology.transits import (
    TransitEngine,
    TransitEventKind,
    TransitProviderResultError,
)

_START = datetime(2025, 1, 1, tzinfo=UTC)
_BODIES = (
    CelestialBody.JUPITER,
    CelestialBody.SATURN,
    CelestialBody.RAHU,
    CelestialBody.KETU,
)
LongitudeFunction = Callable[[CelestialBody, int], Decimal]
SpeedFunction = Callable[[CelestialBody, int], Decimal]


class ProgrammableTransitProvider:
    """A deterministic non-astronomical provider used only for transit tests."""

    def __init__(
        self,
        longitude: LongitudeFunction | None = None,
        speed: SpeedFunction | None = None,
        *,
        missing: CelestialBody | None = None,
        duplicate: bool = False,
        changed_provenance_at: int | None = None,
        changed_configuration_at: int | None = None,
    ) -> None:
        self.longitude = longitude or (lambda body, seconds: Decimal("10"))
        self.speed = speed or (lambda body, seconds: Decimal("1"))
        self.missing = missing
        self.duplicate = duplicate
        self.changed_provenance_at = changed_provenance_at
        self.changed_configuration_at = changed_configuration_at
        self._metadata = ProviderMetadata(
            provider_name="programmable-transit-test-provider", provider_version="1"
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
        return self._metadata

    @property
    def capabilities(self) -> ProviderCapabilities:
        return self._capabilities

    def calculate(self, request: EphemerisRequest) -> EphemerisResult:
        seconds = int((request.calculation_instant - _START).total_seconds())
        configuration = request.configuration.model_copy(
            update={"ayanamsa_provider_mode": "SIDM_LAHIRI"}
        )
        if self.changed_configuration_at is not None and seconds >= self.changed_configuration_at:
            configuration = configuration.model_copy(update={"house_system": "changed"})
        metadata = self._metadata
        if self.changed_provenance_at is not None and seconds >= self.changed_provenance_at:
            metadata = metadata.model_copy(update={"provider_version": "2"})
        positions: list[PlanetaryPosition] = []
        for body in _BODIES:
            if body is self.missing:
                continue
            longitude = (
                (self.longitude(CelestialBody.RAHU, seconds) + Decimal("180")) % Decimal("360")
                if body is CelestialBody.KETU
                else self.longitude(body, seconds) % Decimal("360")
            )
            if longitude < 0:
                longitude += Decimal("360")
            motion_speed = (
                self.speed(CelestialBody.RAHU, seconds)
                if body is CelestialBody.KETU
                else self.speed(body, seconds)
            )
            positions.append(
                PlanetaryPosition(
                    body=body,
                    longitude=longitude,
                    ecliptic_latitude=Decimal("0"),
                    distance=Decimal("1"),
                    motion_speed=motion_speed,
                    retrograde_input=motion_speed < 0,
                )
            )
        if self.duplicate:
            positions.append(positions[0])
        return EphemerisResult(
            positions=tuple(positions),
            provenance=EphemerisProvenance(
                provider=metadata,
                calculation_instant=request.calculation_instant,
                configuration=configuration,
            ),
        )


def _engine(provider: ProgrammableTransitProvider | None = None) -> TransitEngine:
    return TransitEngine(provider or ProgrammableTransitProvider())


def _linear(body: CelestialBody, seconds: int) -> Decimal:
    if body is CelestialBody.JUPITER:
        return Decimal("29.5") + Decimal(seconds) / Decimal(3600)
    if body is CelestialBody.SATURN:
        return Decimal("0.5") - Decimal(seconds) / Decimal(3600)
    if body is CelestialBody.RAHU:
        return Decimal("359.5") + Decimal(seconds) / Decimal(3600)
    return Decimal("10")


def test_point_in_time_normalizes_and_has_only_stable_transit_bodies() -> None:
    instant = datetime(2025, 1, 1, 5, 30, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    snapshot = _engine().positions_at(instant)

    assert snapshot.requested_instant == instant
    assert snapshot.normalized_utc_instant == _START
    assert tuple(position.body for position in snapshot.positions) == _BODIES
    assert snapshot.positions[0].sign.value == "aries"
    assert snapshot.positions[0].degree_in_sign == Decimal("10")
    assert snapshot.positions[0].nakshatra is Nakshatra.ASHWINI
    assert snapshot.positions[0].pada == 4
    assert not snapshot.positions[0].retrograde
    assert snapshot.methodology.methodology_id == "transit-v1"


def test_transit_nakshatra_and_pada_use_the_canonical_d1_boundary_convention() -> None:
    boundary = Decimal("40") / Decimal("3")

    def longitude(body: CelestialBody, seconds: int) -> Decimal:
        return boundary if body is CelestialBody.JUPITER else Decimal("10")

    snapshot = _engine(ProgrammableTransitProvider(longitude=longitude)).positions_at(_START)
    jupiter = snapshot.positions[0]

    assert jupiter.nakshatra is Nakshatra.BHARANI
    assert jupiter.pada == 1


def test_naive_and_invalid_ranges_are_rejected() -> None:
    engine = _engine()
    with pytest.raises(ValueError, match="timezone-aware"):
        engine.positions_at(datetime(2025, 1, 1))
    with pytest.raises(ValueError, match="after"):
        engine.calculate_range(_START, _START)
    with pytest.raises(ValueError, match="after"):
        engine.calculate_range(_START + timedelta(seconds=1), _START)


def test_direct_and_retrograde_sign_ingresses_are_detected() -> None:
    transit_range = _engine(ProgrammableTransitProvider(longitude=_linear)).calculate_range(
        _START, _START + timedelta(hours=1)
    )
    ingress = next(event for event in transit_range.events if event.body is CelestialBody.JUPITER)
    assert ingress.kind is TransitEventKind.SIGN_INGRESS
    assert ingress.to_sign.value == "taurus"
    assert ingress.instant.microsecond == 0
    retrograde = next(event for event in transit_range.events if event.body is CelestialBody.SATURN)
    assert retrograde.kind is TransitEventKind.SIGN_INGRESS
    assert retrograde.to_sign.value == "pisces"


def test_pisces_to_aries_and_aries_to_pisces_wraparounds_are_detected() -> None:
    result = _engine(ProgrammableTransitProvider(longitude=_linear)).calculate_range(
        _START, _START + timedelta(hours=1)
    )
    assert any(
        event.body is CelestialBody.RAHU
        and event.from_sign.value == "pisces"
        and event.to_sign.value == "aries"
        for event in result.events
    )
    result = _engine(ProgrammableTransitProvider(longitude=_linear)).calculate_range(
        _START, _START + timedelta(hours=1)
    )
    assert any(
        event.body is CelestialBody.SATURN
        and event.from_sign.value == "aries"
        and event.to_sign.value == "pisces"
        for event in result.events
    )


def test_exact_boundary_start_is_excluded_and_end_is_included_at_whole_second() -> None:
    def longitude(body: CelestialBody, seconds: int) -> Decimal:
        return Decimal("29") + Decimal(seconds) / Decimal(3600)

    engine = _engine(ProgrammableTransitProvider(longitude=longitude))
    excluded = engine.calculate_range(_START + timedelta(hours=1), _START + timedelta(hours=2))
    included = engine.calculate_range(_START, _START + timedelta(hours=1))
    assert not any(event.body is CelestialBody.JUPITER for event in excluded.events)
    event = next(event for event in included.events if event.body is CelestialBody.JUPITER)
    assert event.instant == _START + timedelta(hours=1)


def test_station_events_and_zero_speed_convention() -> None:
    def speed(body: CelestialBody, seconds: int) -> Decimal:
        return Decimal("-1") if seconds >= 1800 else Decimal("0")

    retrograde = _engine(ProgrammableTransitProvider(speed=speed)).calculate_range(
        _START, _START + timedelta(hours=1)
    )
    assert retrograde.start_snapshot.positions[0].retrograde is False
    assert any(event.kind is TransitEventKind.STATION_RETROGRADE for event in retrograde.events)

    def direct_speed(body: CelestialBody, seconds: int) -> Decimal:
        return Decimal("0") if seconds >= 1800 else Decimal("-1")

    direct = _engine(ProgrammableTransitProvider(speed=direct_speed)).calculate_range(
        _START, _START + timedelta(hours=1)
    )
    assert any(event.kind is TransitEventKind.STATION_DIRECT for event in direct.events)


def test_results_are_deterministic_ordered_and_rahu_ketu_are_opposite() -> None:
    engine = _engine(ProgrammableTransitProvider(longitude=_linear))
    first = engine.calculate_range(_START, _START + timedelta(hours=1))
    second = engine.calculate_range(_START, _START + timedelta(hours=1))
    assert first.model_dump(mode="json") == second.model_dump(mode="json")
    assert list(first.events) == sorted(
        first.events,
        key=lambda event: (
            event.instant,
            _BODIES.index(event.body),
            tuple(TransitEventKind).index(event.kind),
        ),
    )
    rahu = first.start_snapshot.positions[2]
    ketu = first.start_snapshot.positions[3]
    assert (rahu.longitude + Decimal("180")) % Decimal("360") == ketu.longitude


@pytest.mark.parametrize(
    "provider",
    [
        ProgrammableTransitProvider(missing=CelestialBody.SATURN),
        ProgrammableTransitProvider(duplicate=True),
        ProgrammableTransitProvider(changed_provenance_at=3600),
        ProgrammableTransitProvider(changed_configuration_at=3600),
    ],
)
def test_invalid_or_inconsistent_provider_results_fail(
    provider: ProgrammableTransitProvider,
) -> None:
    with pytest.raises((TransitProviderResultError, ValueError)):
        _engine(provider).calculate_range(_START, _START + timedelta(hours=1))


def test_swiss_provider_positions_provenance_and_node_relationship_are_deterministic() -> None:
    engine = TransitEngine(SwissEphemerisProvider())
    first = engine.positions_at(datetime(2026, 10, 2, 12, tzinfo=UTC))
    second = engine.positions_at(datetime(2026, 10, 2, 12, tzinfo=UTC))
    direct = SwissEphemerisProvider().calculate(
        EphemerisRequest(
            calculation_instant=first.normalized_utc_instant,
            requested_bodies=_BODIES,
        )
    )
    assert first.model_dump(mode="json") == second.model_dump(mode="json")
    assert tuple(position.longitude for position in first.positions) == tuple(
        position.longitude for position in direct.positions
    )
    assert first.ephemeris_provenance.configuration.ayanamsa_provider_mode == "SIDM_LAHIRI"
    assert first.ephemeris_provenance.configuration.lunar_node_definition.value == "true"
    assert first.ephemeris_provenance.provider.ephemeris_data_version is not None
