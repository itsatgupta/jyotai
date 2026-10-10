"""Focused factual tests for timing-local D1 relational placement projection."""

from datetime import date, time

import pytest
from pydantic import ValidationError

from astrologer.astrology.chart import ChartEngine
from astrologer.astrology.derived_facts import DerivedFactsEngine
from astrologer.astrology.ephemeris import CelestialBody
from astrologer.astrology.swiss_ephemeris import SwissEphemerisProvider
from astrologer.birth.models import BirthInput
from astrologer.timing_rules.placement import (
    HOUSE_CLASSIFICATION_DEFINITIONS_ID,
    TIMING_RELATIONAL_PLACEMENT_CONTRACT_ID,
    TimingRelationalPlacementFact,
    TimingRelationalPlacementProjector,
    TimingRelationalPlacementStatus,
)
from astrologer.timing_rules.registry import (
    ACTIVE_TIMING_RELEASE_POINTER,
    PRODUCTION_CAREER_TIMING_RELEASE_V2,
)


def _facts_by_id(
    values: dict[str, bool | int | str] | None = None,
) -> dict[str, TimingRelationalPlacementFact]:
    projected = TimingRelationalPlacementProjector().project(values or {})
    return {fact.fact_id: fact for fact in projected.facts}


@pytest.mark.parametrize(
    ("house", "classification"),
    [
        (1, "kendra"),
        (4, "kendra"),
        (7, "kendra"),
        (10, "kendra"),
        (1, "trikona"),
        (5, "trikona"),
        (9, "trikona"),
        (11, "labha"),
        (2, "dhana"),
        (3, "sibling_house"),
    ],
)
def test_every_requested_house_classification_has_explicit_membership(
    house: int, classification: str
) -> None:
    facts = _facts_by_id({"jyotish.d1.planet.venus.placement_house": house})

    placement = facts["jyotish.d1.planet.venus.placement_house"]
    membership = facts[f"jyotish.d1.planet.venus.{classification}"]
    assert placement.status is TimingRelationalPlacementStatus.TRUE
    assert placement.value == house
    assert membership.status is TimingRelationalPlacementStatus.TRUE
    assert membership.value is True


def test_nonmembership_and_first_house_overlap_are_preserved() -> None:
    facts = _facts_by_id({"jyotish.d1.planet.sun.placement_house": 1})

    assert facts["jyotish.d1.planet.sun.kendra"].value is True
    assert facts["jyotish.d1.planet.sun.trikona"].value is True
    assert facts["jyotish.d1.planet.sun.labha"].status is TimingRelationalPlacementStatus.FALSE
    assert facts["jyotish.d1.planet.sun.dhana"].value is False
    assert facts["jyotish.d1.planet.sun.sibling_house"].value is False


@pytest.mark.parametrize("invalid", [None, True, False, 0, 13, "11"])
def test_missing_or_invalid_placement_preserves_unknown(invalid: object) -> None:
    facts = _facts_by_id({"jyotish.d1.planet.moon.placement_house": invalid})  # type: ignore[dict-item]

    for suffix in ("placement_house", "kendra", "trikona", "labha", "dhana", "sibling_house"):
        fact = facts[f"jyotish.d1.planet.moon.{suffix}"]
        assert fact.status is TimingRelationalPlacementStatus.UNKNOWN
        assert fact.value is None


def test_projection_uses_existing_canonical_chart_fact_without_a_second_house_algorithm() -> None:
    birth = BirthInput(
        birth_date=date(1990, 1, 15),
        birth_time=time(9, 30),
        timezone="Asia/Kolkata",
        latitude=19.076,
        longitude=72.8777,
    )
    chart = ChartEngine(SwissEphemerisProvider()).calculate(birth)
    source_values = {
        fact.fact_id: fact.value for fact in DerivedFactsEngine().calculate(chart).facts
    }
    facts = _facts_by_id(source_values)

    for body in tuple(CelestialBody)[:7]:
        planet = next(item for item in chart.planets if item.body is body)
        projected = facts[f"jyotish.d1.planet.{body.value}.placement_house"]
        assert projected.value == planet.house_number
        assert facts[f"jyotish.d1.planet.{body.value}.kendra"].value is (
            planet.house_number in {1, 4, 7, 10}
        )


def test_contract_provenance_is_structural_and_excludes_nodes_and_interpretation() -> None:
    projected = TimingRelationalPlacementProjector().project({})

    assert projected.contract_id == TIMING_RELATIONAL_PLACEMENT_CONTRACT_ID
    assert (
        projected.provenance.house_classification_definitions_id
        == HOUSE_CLASSIFICATION_DEFINITIONS_ID
    )
    assert projected.provenance.source_status == "deterministic_structural_definition"
    assert len(projected.facts) == 42
    assert not any("rahu" in fact.fact_id or "ketu" in fact.fact_id for fact in projected.facts)
    assert not any(
        "strength" in fact.fact_id or "aspect" in fact.fact_id for fact in projected.facts
    )


def test_fact_model_rejects_known_status_value_mismatch() -> None:
    with pytest.raises(ValidationError, match="must match"):
        TimingRelationalPlacementFact(
            fact_id="jyotish.d1.planet.venus.kendra",
            status=TimingRelationalPlacementStatus.TRUE,
            value=False,
        )


def test_projection_does_not_change_active_production_v2() -> None:
    assert ACTIVE_TIMING_RELEASE_POINTER.release_id == "jyotish.timing.production.career@v2"
    assert PRODUCTION_CAREER_TIMING_RELEASE_V2.release_version == "v2"
    assert all(
        "kendra" not in fact_id
        and "trikona" not in fact_id
        and "labha" not in fact_id
        and "dhana" not in fact_id
        and "sibling_house" not in fact_id
        for rule in PRODUCTION_CAREER_TIMING_RELEASE_V2.rules
        for fact_id in rule.required_fact_ids
    )
