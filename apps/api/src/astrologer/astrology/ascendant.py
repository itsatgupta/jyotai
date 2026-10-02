"""Provider-neutral ascendant calculation contracts."""

from datetime import datetime
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

from astrologer.astrology.ephemeris import (
    EphemerisConfiguration,
    EphemerisProvenance,
    Longitude,
)


class AscendantRequest(BaseModel):
    """Inputs required to calculate an ascendant without provider-specific types."""

    model_config = ConfigDict(frozen=True)

    calculation_instant: datetime
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    configuration: EphemerisConfiguration


class AscendantResult(BaseModel):
    """A provider-neutral ascendant result and its calculation provenance."""

    model_config = ConfigDict(frozen=True)

    longitude: Longitude
    provenance: EphemerisProvenance


@runtime_checkable
class AscendantProvider(Protocol):
    """Optional provider capability required by the D1 chart engine."""

    def calculate_ascendant(self, request: AscendantRequest) -> AscendantResult:
        """Calculate an ascendant for a geographic observer."""
        ...
