"""Provider-neutral deterministic transit positions and event searches."""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict

from astrologer.astrology.chart import (
    Nakshatra,
    ZodiacSign,
    degree_in_sign,
    nakshatra_for_longitude,
    sign_for_longitude,
)
from astrologer.astrology.ephemeris import (
    CelestialBody,
    EphemerisConfiguration,
    EphemerisProvenance,
    EphemerisProvider,
    EphemerisRequest,
    PlanetaryPosition,
)

_BODIES = (
    CelestialBody.JUPITER,
    CelestialBody.SATURN,
    CelestialBody.RAHU,
    CelestialBody.KETU,
)
_SCAN_INTERVAL = timedelta(hours=1)
_SECOND = timedelta(seconds=1)


class TransitEventKind(StrEnum):
    """The strictly astronomical state transitions supported by transit-v1."""

    SIGN_INGRESS = "sign_ingress"
    STATION_RETROGRADE = "station_retrograde"
    STATION_DIRECT = "station_direct"


class TransitMethodology(BaseModel):
    """Frozen numerical and astronomical conventions for transit-v1."""

    model_config = ConfigDict(frozen=True)

    methodology_id: Literal["transit-v1"] = "transit-v1"
    requested_bodies: tuple[CelestialBody, ...] = _BODIES
    zodiac: Literal["sidereal"] = "sidereal"
    ayanamsa: Literal["lahiri"] = "lahiri"
    ayanamsa_provider_mode: Literal["SIDM_LAHIRI"] = "SIDM_LAHIRI"
    coordinate_origin: Literal["geocentric"] = "geocentric"
    position_reference: Literal["apparent"] = "apparent"
    lunar_node_definition: Literal["true"] = "true"
    ketu_derivation: Literal["rahu_plus_180_mod_360"] = "rahu_plus_180_mod_360"
    retrograde_definition: Literal["motion_speed_lt_zero"] = "motion_speed_lt_zero"
    zero_speed_is_retrograde: Literal[False] = False
    utc_normalization: Literal["aware_inputs_normalized_to_utc"] = "aware_inputs_normalized_to_utc"
    scan_interval_seconds: Literal[3600] = 3600
    event_boundary_resolution: Literal["one_second"] = "one_second"
    event_inclusion: Literal["(start,end]"] = "(start,end]"
    event_ordering: tuple[str, ...] = (
        "instant",
        "jupiter_saturn_rahu_ketu",
        "sign_ingress_station_retrograde_station_direct",
    )


class TransitPosition(BaseModel):
    """One factual sidereal transit position; it contains no interpretation."""

    model_config = ConfigDict(frozen=True)

    body: CelestialBody
    longitude: Decimal
    sign: ZodiacSign
    degree_in_sign: Decimal
    nakshatra: Nakshatra
    pada: int
    ecliptic_latitude: Decimal
    distance: Decimal
    motion_speed: Decimal
    retrograde: bool


class TransitSnapshot(BaseModel):
    """The four transit positions at one explicit requested instant."""

    model_config = ConfigDict(frozen=True)

    requested_instant: datetime
    normalized_utc_instant: datetime
    positions: tuple[TransitPosition, ...]
    methodology: TransitMethodology
    ephemeris_provenance: EphemerisProvenance


class TransitEvent(BaseModel):
    """A deterministic astronomical state transition at one UTC second."""

    model_config = ConfigDict(frozen=True)

    body: CelestialBody
    kind: TransitEventKind
    instant: datetime
    from_sign: ZodiacSign | None = None
    to_sign: ZodiacSign | None = None
    from_retrograde: bool | None = None
    to_retrograde: bool | None = None


class TransitRange(BaseModel):
    """Snapshots and all transit-v1 events in the half-open-by-start range."""

    model_config = ConfigDict(frozen=True)

    requested_start: datetime
    requested_end: datetime
    normalized_utc_start: datetime
    normalized_utc_end: datetime
    start_snapshot: TransitSnapshot
    end_snapshot: TransitSnapshot
    events: tuple[TransitEvent, ...]
    methodology: TransitMethodology
    ephemeris_provenance: EphemerisProvenance


class TransitProviderResultError(RuntimeError):
    """Raised when a provider result cannot safely support transit-v1."""


class TransitEngine:
    """Calculate transit-v1 facts entirely through an EphemerisProvider."""

    def __init__(
        self,
        provider: EphemerisProvider,
        configuration: EphemerisConfiguration | None = None,
    ) -> None:
        self._provider = provider
        self._configuration = configuration or EphemerisConfiguration()
        self._validate_requested_configuration(self._configuration)
        self._methodology = TransitMethodology()

    def positions_at(self, instant: datetime) -> TransitSnapshot:
        """Return four deterministic positions at an explicit aware instant."""
        normalized = _as_utc(instant, "instant")
        positions, provenance = self._calculate(normalized)
        return TransitSnapshot(
            requested_instant=instant,
            normalized_utc_instant=normalized,
            positions=positions,
            methodology=self._methodology,
            ephemeris_provenance=provenance,
        )

    def calculate_range(self, start: datetime, end: datetime) -> TransitRange:
        """Return snapshots and all events in ``(start, end]``.

        Every consecutive fixed one-hour interval is evaluated independently.
        Event boundaries are the first whole UTC second with the post-state.
        """
        normalized_start = _as_utc(start, "start")
        normalized_end = _as_utc(end, "end")
        if normalized_end <= normalized_start:
            raise ValueError("end must be after start")

        cache: dict[datetime, tuple[tuple[TransitPosition, ...], EphemerisProvenance]] = {}

        def snapshot_at(instant: datetime) -> TransitSnapshot:
            if instant not in cache:
                cache[instant] = self._calculate(instant)
            positions, provenance = cache[instant]
            return TransitSnapshot(
                requested_instant=instant,
                normalized_utc_instant=instant,
                positions=positions,
                methodology=self._methodology,
                ephemeris_provenance=provenance,
            )

        start_snapshot = snapshot_at(normalized_start)
        end_snapshot = snapshot_at(normalized_end)
        canonical_provenance = start_snapshot.ephemeris_provenance
        _require_same_provenance(canonical_provenance, end_snapshot.ephemeris_provenance)

        events: list[TransitEvent] = []
        left = normalized_start
        left_snapshot = start_snapshot
        while left < normalized_end:
            right = min(left + _SCAN_INTERVAL, normalized_end)
            right_snapshot = end_snapshot if right == normalized_end else snapshot_at(right)
            _require_same_provenance(canonical_provenance, right_snapshot.ephemeris_provenance)
            for body in _BODIES:
                before = _position_for(left_snapshot, body)
                after = _position_for(right_snapshot, body)
                for kind in _changed_kinds(before, after):
                    event = self._refine_event(kind, body, left, right, before, after, snapshot_at)
                    if normalized_start < event.instant <= normalized_end:
                        events.append(event)
            left = right
            left_snapshot = right_snapshot

        ordered_events = tuple(sorted(set(events), key=_event_sort_key))
        for _, provenance in cache.values():
            _require_same_provenance(canonical_provenance, provenance)
        return TransitRange(
            requested_start=start,
            requested_end=end,
            normalized_utc_start=normalized_start,
            normalized_utc_end=normalized_end,
            start_snapshot=start_snapshot.model_copy(update={"requested_instant": start}),
            end_snapshot=end_snapshot.model_copy(update={"requested_instant": end}),
            events=ordered_events,
            methodology=self._methodology,
            ephemeris_provenance=canonical_provenance,
        )

    def _calculate(
        self, instant: datetime
    ) -> tuple[tuple[TransitPosition, ...], EphemerisProvenance]:
        result = self._provider.calculate(
            EphemerisRequest(
                calculation_instant=instant,
                configuration=self._configuration,
                requested_bodies=_BODIES,
            )
        )
        if result.provenance.calculation_instant != instant:
            raise TransitProviderResultError(
                "provider returned an inconsistent calculation instant"
            )
        self._validate_returned_configuration(result.provenance.configuration)
        by_body: dict[CelestialBody, PlanetaryPosition] = {}
        for position in result.positions:
            if position.body not in _BODIES:
                raise TransitProviderResultError("provider returned an unexpected transit body")
            if position.body in by_body:
                raise TransitProviderResultError(
                    f"provider returned duplicate body: {position.body.value}"
                )
            by_body[position.body] = position
        missing = set(_BODIES) - set(by_body)
        if missing:
            names = ", ".join(body.value for body in _BODIES if body in missing)
            raise TransitProviderResultError(f"provider omitted required transit bodies: {names}")
        positions = tuple(_transit_position(by_body[body]) for body in _BODIES)
        rahu, ketu = positions[2:]
        if (rahu.longitude + 180) % 360 != ketu.longitude:
            raise TransitProviderResultError("Ketu must be exactly opposite true Rahu")
        return positions, result.provenance

    def _refine_event(
        self,
        kind: TransitEventKind,
        body: CelestialBody,
        left: datetime,
        right: datetime,
        before: TransitPosition,
        after: TransitPosition,
        snapshot_at: Callable[[datetime], TransitSnapshot],
    ) -> TransitEvent:
        expected_post = _event_state(kind, after)
        low, high = left, right
        while high - low > _SECOND:
            midpoint = low + (high - low) / 2
            midpoint_position = _position_for(snapshot_at(midpoint), body)
            if _event_state(kind, midpoint_position) == expected_post:
                high = midpoint
            else:
                low = midpoint
        candidate = _ceil_to_second(high)
        while _event_state(kind, _position_for(snapshot_at(candidate), body)) != expected_post:
            candidate += _SECOND
        if kind is TransitEventKind.SIGN_INGRESS:
            return TransitEvent(
                body=body, kind=kind, instant=candidate, from_sign=before.sign, to_sign=after.sign
            )
        return TransitEvent(
            body=body,
            kind=kind,
            instant=candidate,
            from_retrograde=before.retrograde,
            to_retrograde=after.retrograde,
        )

    @staticmethod
    def _validate_requested_configuration(configuration: EphemerisConfiguration) -> None:
        flags = configuration.flags
        if (
            configuration.zodiac.value != "sidereal"
            or configuration.ayanamsa.value != "lahiri"
            or configuration.lunar_node_definition.value != "true"
            or flags.coordinate_origin.value != "geocentric"
            or flags.position_reference.value != "apparent"
            or not flags.require_motion_speed
        ):
            raise ValueError("transit-v1 requires sidereal Lahiri true-node speed configuration")

    def _validate_returned_configuration(self, configuration: EphemerisConfiguration) -> None:
        self._validate_requested_configuration(configuration)
        if configuration != self._configuration.model_copy(
            update={"ayanamsa_provider_mode": configuration.ayanamsa_provider_mode}
        ):
            raise TransitProviderResultError(
                "provider returned an inconsistent transit configuration"
            )
        if configuration.ayanamsa_provider_mode != "SIDM_LAHIRI":
            raise TransitProviderResultError("transit-v1 requires SIDM_LAHIRI provenance")


def _transit_position(position: PlanetaryPosition) -> TransitPosition:
    if (
        position.ecliptic_latitude is None
        or position.distance is None
        or position.motion_speed is None
    ):
        raise TransitProviderResultError("provider omitted required transit position data")
    nakshatra = nakshatra_for_longitude(position.longitude)
    return TransitPosition(
        body=position.body,
        longitude=position.longitude,
        sign=sign_for_longitude(position.longitude),
        degree_in_sign=degree_in_sign(position.longitude),
        nakshatra=nakshatra.nakshatra,
        pada=nakshatra.pada,
        ecliptic_latitude=position.ecliptic_latitude,
        distance=position.distance,
        motion_speed=position.motion_speed,
        retrograde=position.motion_speed < 0,
    )


def _position_for(snapshot: TransitSnapshot, body: CelestialBody) -> TransitPosition:
    return next(position for position in snapshot.positions if position.body is body)


def _changed_kinds(before: TransitPosition, after: TransitPosition) -> tuple[TransitEventKind, ...]:
    kinds: list[TransitEventKind] = []
    if before.sign is not after.sign:
        kinds.append(TransitEventKind.SIGN_INGRESS)
    if not before.retrograde and after.retrograde:
        kinds.append(TransitEventKind.STATION_RETROGRADE)
    if before.retrograde and not after.retrograde:
        kinds.append(TransitEventKind.STATION_DIRECT)
    return tuple(kinds)


def _event_state(kind: TransitEventKind, position: TransitPosition) -> object:
    return position.sign if kind is TransitEventKind.SIGN_INGRESS else position.retrograde


def _as_utc(value: datetime, name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


def _ceil_to_second(value: datetime) -> datetime:
    if value.microsecond == 0:
        return value
    return value.replace(microsecond=0) + _SECOND


def _require_same_provenance(expected: EphemerisProvenance, candidate: EphemerisProvenance) -> None:
    if candidate.provider != expected.provider or candidate.configuration != expected.configuration:
        raise TransitProviderResultError("provider provenance changed during transit calculation")


def _event_sort_key(event: TransitEvent) -> tuple[datetime, int, int]:
    return (
        event.instant,
        _BODIES.index(event.body),
        tuple(TransitEventKind).index(event.kind),
    )
