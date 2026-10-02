"""Stateless deterministic composition of approved astrology engine outputs."""

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

from astrologer.astrology.chart import Chart, ChartEngine, ChartMethodology
from astrologer.astrology.dasha import DashaChain, VimshottariDashaEngine, VimshottariMethodology
from astrologer.astrology.derived_facts import (
    DerivedFactBundle,
    DerivedFactsEngine,
    DerivedFactsMethodology,
)
from astrologer.astrology.ephemeris import EphemerisProvider, ProviderMetadata
from astrologer.astrology.transits import TransitEngine, TransitMethodology, TransitSnapshot
from astrologer.astrology.vargas import (
    DivisionalChart,
    DivisionalChartType,
    VargaEngine,
    VargaMethodology,
)
from astrologer.birth.models import BirthInput

CONTEXT_VERSION: Literal["deterministic-astrology-context-v1"] = (
    "deterministic-astrology-context-v1"
)


class DeterministicContextInputError(ValueError):
    """Raised when an explicit context instant cannot be applied to the birth input."""


class DeterministicContextRequest(BaseModel):
    """One birth input and one explicit, timezone-aware instant for a context snapshot."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    birth_input: BirthInput
    as_of: datetime

    @field_validator("as_of")
    @classmethod
    def as_of_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("as_of must be timezone-aware")
        return value


class DeterministicAstrologyContextProvenance(BaseModel):
    """Compact methodology and provider references for a composed context result."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    context_version: Literal["deterministic-astrology-context-v1"] = CONTEXT_VERSION
    requested_as_of: datetime
    normalized_as_of_utc: datetime
    d1_methodology: ChartMethodology
    d9_methodology: VargaMethodology
    d10_methodology: VargaMethodology
    vimshottari_methodology: VimshottariMethodology
    transit_methodology: TransitMethodology
    derived_facts_methodology: DerivedFactsMethodology
    d1_ephemeris_provider: ProviderMetadata
    transit_ephemeris_provider: ProviderMetadata


class DeterministicAstrologyContext(BaseModel):
    """Immutable deterministic context; it deliberately contains no interpretation or evidence."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    context_version: Literal["deterministic-astrology-context-v1"] = CONTEXT_VERSION
    birth_input: BirthInput
    calculation_instant: datetime
    requested_as_of: datetime
    normalized_as_of_utc: datetime
    d1: Chart
    d9: DivisionalChart
    d10: DivisionalChart
    active_dasha: DashaChain
    transit_snapshot: TransitSnapshot
    derived_facts: DerivedFactBundle
    provenance: DeterministicAstrologyContextProvenance


class DeterministicAstrologyContextService:
    """Compose existing deterministic engines once per explicit context request."""

    def __init__(
        self,
        provider: EphemerisProvider,
        chart_engine: ChartEngine | None = None,
        varga_engine: VargaEngine | None = None,
        dasha_engine: VimshottariDashaEngine | None = None,
        transit_engine: TransitEngine | None = None,
        derived_facts_engine: DerivedFactsEngine | None = None,
    ) -> None:
        self._chart_engine = chart_engine or ChartEngine(provider)
        self._varga_engine = varga_engine or VargaEngine()
        self._dasha_engine = dasha_engine or VimshottariDashaEngine()
        self._transit_engine = transit_engine or TransitEngine(provider)
        self._derived_facts_engine = derived_facts_engine or DerivedFactsEngine()

    def build(self, request: DeterministicContextRequest) -> DeterministicAstrologyContext:
        """Return one context from a shared D1 chart and an explicit normalized instant."""
        normalized_as_of = request.as_of.astimezone(UTC)
        if normalized_as_of < request.birth_input.utc_datetime:
            raise DeterministicContextInputError("as_of must not be before the birth instant")

        d1 = self._chart_engine.calculate(request.birth_input)
        vargas = {
            chart.methodology.chart_type: chart for chart in self._varga_engine.calculate_all(d1)
        }
        d9 = vargas[DivisionalChartType.D9]
        d10 = vargas[DivisionalChartType.D10]
        active_dasha = self._dasha_engine.at(d1, normalized_as_of)
        transit_snapshot = self._transit_engine.positions_at(normalized_as_of)
        derived_facts = self._derived_facts_engine.calculate(d1)

        return DeterministicAstrologyContext(
            birth_input=request.birth_input,
            calculation_instant=d1.calculation_instant,
            requested_as_of=request.as_of,
            normalized_as_of_utc=normalized_as_of,
            d1=d1,
            d9=d9,
            d10=d10,
            active_dasha=active_dasha,
            transit_snapshot=transit_snapshot,
            derived_facts=derived_facts,
            provenance=DeterministicAstrologyContextProvenance(
                requested_as_of=request.as_of,
                normalized_as_of_utc=normalized_as_of,
                d1_methodology=d1.methodology,
                d9_methodology=d9.methodology,
                d10_methodology=d10.methodology,
                vimshottari_methodology=active_dasha.provenance.methodology,
                transit_methodology=transit_snapshot.methodology,
                derived_facts_methodology=derived_facts.provenance.methodology,
                d1_ephemeris_provider=d1.provenance.provider,
                transit_ephemeris_provider=transit_snapshot.ephemeris_provenance.provider,
            ),
        )
