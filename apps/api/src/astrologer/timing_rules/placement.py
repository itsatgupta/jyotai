"""Timing-local projection of canonical D1 relational placement facts.

This module only classifies the already-derived Whole Sign D1 placement house
for each classical planet.  It does not calculate a chart, evaluate a timing
rule, or attach predictive meaning to a house-set membership.
"""

from collections.abc import Mapping
from enum import StrEnum
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, model_validator

from astrologer.astrology.ephemeris import CelestialBody

TIMING_RELATIONAL_PLACEMENT_CONTRACT_ID: Final = "jyotish.timing.relational-placement@v1"
HOUSE_CLASSIFICATION_DEFINITIONS_ID: Final = "jyotish.d1.house-classifications@v1"
_CLASSICAL_BODIES: Final = tuple(CelestialBody)[:7]
_HOUSE_CLASSIFICATIONS: Final[tuple[tuple[str, frozenset[int]], ...]] = (
    ("kendra", frozenset({1, 4, 7, 10})),
    ("trikona", frozenset({1, 5, 9})),
    ("labha", frozenset({11})),
    ("dhana", frozenset({2})),
    ("sibling_house", frozenset({3})),
)


class TimingRelationalPlacementStatus(StrEnum):
    """Three-valued status for an available or unavailable placement fact."""

    TRUE = "TRUE"
    FALSE = "FALSE"
    UNKNOWN = "UNKNOWN"


class TimingRelationalPlacementFact(BaseModel):
    """One D1 placement-house fact or factual membership projection."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    fact_id: str
    status: TimingRelationalPlacementStatus
    value: bool | int | None

    @model_validator(mode="after")
    def status_and_value_must_agree(self) -> "TimingRelationalPlacementFact":
        is_placement = self.fact_id.endswith(".placement_house")
        if self.status is TimingRelationalPlacementStatus.UNKNOWN:
            if self.value is not None:
                raise ValueError("UNKNOWN placement facts must have no value")
        elif is_placement:
            if (
                self.status is not TimingRelationalPlacementStatus.TRUE
                or not isinstance(self.value, int)
                or isinstance(self.value, bool)
                or not 1 <= self.value <= 12
            ):
                raise ValueError(
                    "known placement-house facts require TRUE and a house from 1 to 12"
                )
        elif self.value is None or not isinstance(self.value, bool):
            raise ValueError("known membership facts require a boolean value")
        elif self.value is not (self.status is TimingRelationalPlacementStatus.TRUE):
            raise ValueError("known membership fact status must match its boolean value")
        return self


class TimingRelationalPlacementProvenance(BaseModel):
    """Provenance for this structural projection, without doctrinal attribution."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    canonical_input_methodology_id: Literal["jyotish-derived-facts-v1"] = "jyotish-derived-facts-v1"
    canonical_input_fact_id_template: Literal["jyotish.d1.planet.{planet}.placement_house"] = (
        "jyotish.d1.planet.{planet}.placement_house"
    )
    chart_scope: Literal["D1/Rashi"] = "D1/Rashi"
    house_system: Literal["whole_sign"] = "whole_sign"
    house_classification_definitions_id: Literal["jyotish.d1.house-classifications@v1"] = (
        HOUSE_CLASSIFICATION_DEFINITIONS_ID
    )
    source_status: Literal["deterministic_structural_definition"] = (
        "deterministic_structural_definition"
    )


class TimingRelationalPlacementFacts(BaseModel):
    """Versioned source-independent D1 relational inputs for future timing rules."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    contract_id: str = TIMING_RELATIONAL_PLACEMENT_CONTRACT_ID
    contract_version: str = "v1"
    provenance: TimingRelationalPlacementProvenance = TimingRelationalPlacementProvenance()
    facts: tuple[TimingRelationalPlacementFact, ...]


class TimingRelationalPlacementProjector:
    """Project explicit house-set memberships from canonical D1 placement facts."""

    def project(self, values: Mapping[str, bool | int | str]) -> TimingRelationalPlacementFacts:
        facts: list[TimingRelationalPlacementFact] = []
        for body in _CLASSICAL_BODIES:
            placement_fact_id = f"jyotish.d1.planet.{body.value}.placement_house"
            house_number = values.get(placement_fact_id)
            facts.append(_placement_fact(placement_fact_id, house_number))
            for classification, members in _HOUSE_CLASSIFICATIONS:
                facts.append(
                    _membership_fact(
                        f"jyotish.d1.planet.{body.value}.{classification}",
                        house_number,
                        members,
                    )
                )
        return TimingRelationalPlacementFacts(facts=tuple(facts))


def _placement_fact(
    fact_id: str, house_number: bool | int | str | None
) -> TimingRelationalPlacementFact:
    if (
        not isinstance(house_number, int)
        or isinstance(house_number, bool)
        or not 1 <= house_number <= 12
    ):
        return TimingRelationalPlacementFact(
            fact_id=fact_id, status=TimingRelationalPlacementStatus.UNKNOWN, value=None
        )
    return TimingRelationalPlacementFact(
        fact_id=fact_id, status=TimingRelationalPlacementStatus.TRUE, value=house_number
    )


def _membership_fact(
    fact_id: str, house_number: bool | int | str | None, members: frozenset[int]
) -> TimingRelationalPlacementFact:
    if not _is_valid_house_number(house_number):
        return TimingRelationalPlacementFact(
            fact_id=fact_id, status=TimingRelationalPlacementStatus.UNKNOWN, value=None
        )
    value = house_number in members
    return TimingRelationalPlacementFact(
        fact_id=fact_id,
        status=(
            TimingRelationalPlacementStatus.TRUE if value else TimingRelationalPlacementStatus.FALSE
        ),
        value=value,
    )


def _is_valid_house_number(value: bool | int | str | None) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 12
