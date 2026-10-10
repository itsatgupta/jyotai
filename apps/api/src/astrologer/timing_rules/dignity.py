"""Timing-local projection of already-calculated D1 dignity facts.

This module is deliberately factual: it neither evaluates a timing rule nor
assigns strength, benefit, or an outcome.  It is not wired into the active
Career timing release.
"""

from collections.abc import Mapping
from enum import StrEnum
from typing import Final

from pydantic import BaseModel, ConfigDict, model_validator

from astrologer.astrology.ephemeris import CelestialBody

TIMING_DIGNITY_CONTRACT_ID: Final = "jyotish.timing.dignity@v1"
_CLASSICAL_BODIES: Final = tuple(CelestialBody)[:7]
_DIGNITY_NAMES: Final = ("own_sign", "exaltation_sign")


class TimingDignityStatus(StrEnum):
    """Three-valued availability state for one deterministic dignity fact."""

    TRUE = "TRUE"
    FALSE = "FALSE"
    UNKNOWN = "UNKNOWN"


class TimingDignityFact(BaseModel):
    """One timing-local projection of an existing D1 structural fact."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    fact_id: str
    status: TimingDignityStatus
    value: bool | None

    @model_validator(mode="after")
    def status_and_value_must_agree(self) -> "TimingDignityFact":
        if self.status is TimingDignityStatus.UNKNOWN:
            if self.value is not None:
                raise ValueError("UNKNOWN dignity facts must have no boolean value")
        elif self.value is None or self.value is not (self.status is TimingDignityStatus.TRUE):
            raise ValueError("known dignity fact status must match its boolean value")
        return self


class TimingDignityFacts(BaseModel):
    """Versioned factual D1 dignity input reserved for future governed timing rules."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    contract_id: str = TIMING_DIGNITY_CONTRACT_ID
    contract_version: str = "v1"
    chart_scope: str = "D1/Rashi"
    source_register_version: str = "task09a-v1-approved-conventions"
    source_status: str = "reviewed_exact_locator"
    facts: tuple[TimingDignityFact, ...]


class TimingDignityProjector:
    """Project sign-level dignity values without treating missing input as false."""

    def project(self, values: Mapping[str, bool | int | str]) -> TimingDignityFacts:
        facts = tuple(
            _project_fact(f"jyotish.d1.planet.{body.value}.{dignity_name}", values)
            for dignity_name in _DIGNITY_NAMES
            for body in _CLASSICAL_BODIES
        )
        return TimingDignityFacts(facts=facts)


def _project_fact(fact_id: str, values: Mapping[str, bool | int | str]) -> TimingDignityFact:
    value = values.get(fact_id)
    if not isinstance(value, bool):
        return TimingDignityFact(fact_id=fact_id, status=TimingDignityStatus.UNKNOWN, value=None)
    return TimingDignityFact(
        fact_id=fact_id,
        status=TimingDignityStatus.TRUE if value else TimingDignityStatus.FALSE,
        value=value,
    )
