"""Factual, timing-local D1 dignity projection tests."""

import inspect

import pytest
from pydantic import ValidationError

from astrologer.timing_rules.dignity import (
    TIMING_DIGNITY_CONTRACT_ID,
    TimingDignityFact,
    TimingDignityProjector,
    TimingDignityStatus,
)
from astrologer.timing_rules.registry import PRODUCTION_CAREER_TIMING_RELEASE


def _facts_by_id(
    values: dict[str, bool | int | str] | None = None,
) -> dict[str, TimingDignityFact]:
    projection = TimingDignityProjector().project(values or {})
    return {fact.fact_id: fact for fact in projection.facts}


def test_projects_own_sign_and_exaltation_true_and_false_without_interpretation() -> None:
    facts = _facts_by_id(
        {
            "jyotish.d1.planet.jupiter.own_sign": True,
            "jyotish.d1.planet.venus.own_sign": False,
            "jyotish.d1.planet.sun.exaltation_sign": True,
            "jyotish.d1.planet.moon.exaltation_sign": False,
        }
    )

    assert facts["jyotish.d1.planet.jupiter.own_sign"].status is TimingDignityStatus.TRUE
    assert facts["jyotish.d1.planet.venus.own_sign"].status is TimingDignityStatus.FALSE
    assert facts["jyotish.d1.planet.sun.exaltation_sign"].value is True
    assert facts["jyotish.d1.planet.moon.exaltation_sign"].value is False


def test_missing_or_non_boolean_dignity_input_remains_unknown() -> None:
    facts = _facts_by_id({"jyotish.d1.planet.sun.exaltation_sign": "missing"})

    assert facts["jyotish.d1.planet.jupiter.own_sign"].status is TimingDignityStatus.UNKNOWN
    assert facts["jyotish.d1.planet.jupiter.own_sign"].value is None
    assert facts["jyotish.d1.planet.sun.exaltation_sign"].status is TimingDignityStatus.UNKNOWN


def test_contract_is_factual_and_does_not_admit_moolatrikona() -> None:
    projection = TimingDignityProjector().project({})

    assert projection.contract_id == TIMING_DIGNITY_CONTRACT_ID
    assert projection.source_status == "reviewed_exact_locator"
    assert len(projection.facts) == 14
    assert not any("moolatrikona" in fact.fact_id for fact in projection.facts)


def test_known_status_must_match_boolean_value() -> None:
    with pytest.raises(ValidationError, match="must match"):
        TimingDignityFact(
            fact_id="jyotish.d1.planet.sun.exaltation_sign",
            status=TimingDignityStatus.TRUE,
            value=False,
        )


def test_projection_does_not_change_the_active_career_timing_release() -> None:
    release = PRODUCTION_CAREER_TIMING_RELEASE

    assert release.release_id == "jyotish.timing.production.career@v1"
    assert release.release_version == "v1"
    assert release.rules[0].required_fact_ids == (
        "jyotish.d1.house.10.lord",
        "jyotish.d1.house_lord.10.placement_house",
        "jyotish.timing.vimshottari.mahadasha.lord",
        "jyotish.timing.vimshottari.mahadasha.start",
        "jyotish.timing.vimshottari.mahadasha.end",
    )


def test_projection_does_not_change_static_contract_or_llm_path() -> None:
    from astrologer.application import analyze
    from astrologer.composition import composer
    from astrologer.knowledge import ACTIVE_PRODUCTION_RELEASE

    assert not any(
        ".own_sign" in fact_id or ".exaltation_sign" in fact_id
        for fact_id in ACTIVE_PRODUCTION_RELEASE.fact_contract.available_fact_ids
    )
    assert "timing_rules.dignity" not in inspect.getsource(analyze)
    assert "timing_rules.dignity" not in inspect.getsource(composer)
