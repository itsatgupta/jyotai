"""Factual, bounded Vimshottari timing timelines separate from governed evidence."""

from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from astrologer.astrology.chart import ChartEngine
from astrologer.astrology.dasha import (
    AntardashaPeriod,
    DashaChain,
    DashaLord,
    DashaProvenance,
    MahadashaPeriod,
    VimshottariDashaEngine,
)
from astrologer.astrology.ephemeris import EphemerisProvider
from astrologer.birth.models import BirthInput

TIMING_FACT_CONTRACT_ID: Literal["jyotish.timing.vimshottari@v1"] = "jyotish.timing.vimshottari@v1"
_MAX_HORIZON = timedelta(days=365.25 * 120)


class TimingEvidenceLevel(StrEnum):
    """Availability of factual timing inputs; this is never an outcome assessment."""

    TIMING_NOT_ESTABLISHED = "TIMING_NOT_ESTABLISHED"
    MAHADASHA_AVAILABLE = "MAHADASHA_AVAILABLE"
    MAHADASHA_ANTARDASHA_AVAILABLE = "MAHADASHA_ANTARDASHA_AVAILABLE"
    DASHA_AND_TRANSIT_AVAILABLE = "DASHA_AND_TRANSIT_AVAILABLE"


class TimingPrecision(StrEnum):
    """Maximum factual interval granularity, not a prediction confidence level."""

    NONE = "NONE"
    BROAD_PERIOD = "BROAD_PERIOD"
    SUB_PERIOD = "SUB_PERIOD"
    REFINED_WINDOW = "REFINED_WINDOW"


class TimingFactContract(BaseModel):
    """Versioned factual contract intentionally independent of static FactContract."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    contract_id: Literal["jyotish.timing.vimshottari@v1"] = TIMING_FACT_CONTRACT_ID
    contract_version: Literal["v1"] = "v1"
    calculation_system: Literal["vimshottari-v1"] = "vimshottari-v1"
    interval_boundary_convention: Literal["[start,end)"] = "[start,end)"
    timezone_normalization: Literal["aware_inputs_normalized_to_utc"] = (
        "aware_inputs_normalized_to_utc"
    )
    pratyantardasha_status: Literal["deferred"] = "deferred"


class TimingEvidenceStatus(BaseModel):
    """A future-pack extension point that deliberately establishes no answerability."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    level: TimingEvidenceLevel
    precision: TimingPrecision
    timing_answerability_established: Literal[False] = False


class TimingMahadashaInterval(BaseModel):
    """One complete source MD interval and its complete nested AD intervals."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    planet: DashaLord
    start: datetime
    end: datetime
    antardashas: tuple["TimingAntardashaInterval", ...]


class TimingAntardashaInterval(BaseModel):
    """One complete source AD interval nested inside its parent MD."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    mahadasha_lord: DashaLord
    antardasha_lord: DashaLord
    start: datetime
    end: datetime


class CurrentTimingFacts(BaseModel):
    """The factual MD/AD selected by the supplied explicit as-of instant."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    mahadasha_lord: DashaLord
    mahadasha_start: datetime
    mahadasha_end: datetime
    antardasha_lord: DashaLord
    antardasha_start: datetime
    antardasha_end: datetime


class VimshottariTimingRequest(BaseModel):
    """Request an explicitly bounded factual timing timeline."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    birth_input: BirthInput
    as_of: datetime
    horizon_end: datetime

    @field_validator("as_of", "horizon_end")
    @classmethod
    def instants_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("as_of and horizon_end must be timezone-aware")
        return value

    @model_validator(mode="after")
    def horizon_must_be_bounded_future(self) -> "VimshottariTimingRequest":
        as_of = self.as_of.astimezone(UTC)
        horizon_end = self.horizon_end.astimezone(UTC)
        if horizon_end <= as_of:
            raise ValueError("horizon_end must be after as_of")
        if horizon_end - as_of > _MAX_HORIZON:
            raise ValueError("horizon_end must not be more than 120 dasha years after as_of")
        return self


class VimshottariTimingFacts(BaseModel):
    """Complete factual MD/AD source intervals intersecting a requested horizon."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    timing_fact_contract: TimingFactContract = TimingFactContract()
    requested_as_of: datetime
    normalized_as_of_utc: datetime
    requested_horizon_end: datetime
    normalized_horizon_end_utc: datetime
    current: CurrentTimingFacts
    timeline: tuple[TimingMahadashaInterval, ...]
    evidence_status: TimingEvidenceStatus
    dasha_provenance: DashaProvenance


class VimshottariTimingService:
    """Build factual Vimshottari timing contracts without evidence or interpretation."""

    def __init__(
        self,
        provider: EphemerisProvider,
        chart_engine: ChartEngine | None = None,
        dasha_engine: VimshottariDashaEngine | None = None,
    ) -> None:
        self._chart_engine = chart_engine or ChartEngine(provider)
        self._dasha_engine = dasha_engine or VimshottariDashaEngine()

    def build(self, request: VimshottariTimingRequest) -> VimshottariTimingFacts:
        """Return complete canonical intervals intersecting ``[as_of, horizon_end)``."""
        as_of = request.as_of.astimezone(UTC)
        horizon_end = request.horizon_end.astimezone(UTC)
        if as_of < request.birth_input.utc_datetime:
            raise ValueError("as_of must not be before the birth instant")
        chart = self._chart_engine.calculate(request.birth_input)
        chain = self._dasha_engine.at(chart, as_of)
        complete = self._dasha_engine.calculate(chart, horizon_end)
        timeline = tuple(
            _timing_mahadasha(period)
            for period in complete.mahadashas
            if period.end > as_of and period.start < horizon_end
        )
        return VimshottariTimingFacts(
            requested_as_of=request.as_of,
            normalized_as_of_utc=as_of,
            requested_horizon_end=request.horizon_end,
            normalized_horizon_end_utc=horizon_end,
            current=_current_facts(chain),
            timeline=timeline,
            evidence_status=TimingEvidenceStatus(
                level=TimingEvidenceLevel.MAHADASHA_ANTARDASHA_AVAILABLE,
                precision=TimingPrecision.SUB_PERIOD,
            ),
            dasha_provenance=complete.provenance,
        )


def _timing_mahadasha(period: MahadashaPeriod) -> TimingMahadashaInterval:
    return TimingMahadashaInterval(
        planet=period.lord,
        start=period.start,
        end=period.end,
        antardashas=tuple(_timing_antardasha(item) for item in period.antardashas),
    )


def _timing_antardasha(period: AntardashaPeriod) -> TimingAntardashaInterval:
    return TimingAntardashaInterval(
        mahadasha_lord=period.mahadasha_lord,
        antardasha_lord=period.lord,
        start=period.start,
        end=period.end,
    )


def _current_facts(chain: DashaChain) -> CurrentTimingFacts:
    return CurrentTimingFacts(
        mahadasha_lord=chain.mahadasha.lord,
        mahadasha_start=chain.mahadasha.start,
        mahadasha_end=chain.mahadasha.end,
        antardasha_lord=chain.antardasha.lord,
        antardasha_start=chain.antardasha.start,
        antardasha_end=chain.antardasha.end,
    )
