"""Tests for the provider-neutral ephemeris contract.

No test in this module asserts astronomical values. The fake provider returns no
positions and serves only as deterministic contract coverage.
"""

from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from astrologer.astrology.ephemeris import (
    Ayanamsa,
    CalculationFlags,
    EphemerisConfiguration,
    EphemerisProvenance,
    EphemerisRequest,
    LunarNodeDefinition,
    ProviderCapabilities,
    ProviderMetadata,
    UnsupportedProviderCapabilityError,
)
from astrologer.astrology.testing import (
    DeterministicFakeEphemerisProvider,
    is_ephemeris_provider,
)

UTC_INSTANT = datetime(1990, 1, 15, 4, 0, tzinfo=UTC)


def test_fake_provider_satisfies_contract_and_preserves_provenance() -> None:
    metadata = ProviderMetadata(
        provider_name="contract-test-provider",
        provider_version="test-version",
        library_version="test-library-version",
        ephemeris_data_version="test-data-version",
        ephemeris_data_hash="test-data-hash",
    )
    provider = DeterministicFakeEphemerisProvider(metadata=metadata)
    request = EphemerisRequest(calculation_instant=UTC_INSTANT)

    result = provider.calculate(request)

    assert is_ephemeris_provider(provider)
    assert result.positions == ()
    assert result.provenance.provider == metadata
    assert result.provenance.calculation_instant == UTC_INSTANT
    assert isinstance(result.provenance, EphemerisProvenance)


def test_default_configuration_represents_sidereal_lahiri_true_nodes() -> None:
    configuration = EphemerisConfiguration()

    assert configuration.zodiac.value == "sidereal"
    assert configuration.ayanamsa is Ayanamsa.LAHIRI
    assert configuration.ayanamsa_provider_mode is None
    assert configuration.lunar_node_definition is LunarNodeDefinition.TRUE


def test_utc_instant_is_preserved_and_non_utc_input_is_rejected() -> None:
    request = EphemerisRequest(calculation_instant=UTC_INSTANT)

    assert request.calculation_instant == UTC_INSTANT
    assert request.calculation_instant.tzinfo is UTC

    non_utc = datetime(1990, 1, 15, 9, 30, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    with pytest.raises(ValidationError, match="timezone-aware UTC"):
        EphemerisRequest(calculation_instant=non_utc)


@pytest.mark.parametrize(
    ("capabilities", "configuration", "expected_capability"),
    [
        (
            ProviderCapabilities(
                supported_ayanamsas=frozenset({Ayanamsa.LAHIRI}),
                supported_node_definitions=frozenset(),
                supports_motion_speed=True,
                supports_retrograde_input=True,
            ),
            EphemerisConfiguration(),
            "lunar_nodes:true",
        ),
        (
            ProviderCapabilities(
                supported_ayanamsas=frozenset({Ayanamsa.LAHIRI}),
                supported_node_definitions=frozenset({LunarNodeDefinition.TRUE}),
                supports_motion_speed=True,
                supports_retrograde_input=True,
            ),
            EphemerisConfiguration(
                flags=CalculationFlags(require_ecliptic_latitude=True),
            ),
            "ecliptic_latitude",
        ),
    ],
)
def test_unsupported_capabilities_fail_explicitly(
    capabilities: ProviderCapabilities,
    configuration: EphemerisConfiguration,
    expected_capability: str,
) -> None:
    provider = DeterministicFakeEphemerisProvider(capabilities=capabilities)
    request = EphemerisRequest(calculation_instant=UTC_INSTANT, configuration=configuration)

    with pytest.raises(UnsupportedProviderCapabilityError) as error:
        provider.calculate(request)

    assert error.value.capability == expected_capability
    assert "deterministic-test-fake" in str(error.value)


def test_domain_result_contains_no_provider_specific_objects() -> None:
    provider = DeterministicFakeEphemerisProvider()

    result = provider.calculate(EphemerisRequest(calculation_instant=UTC_INSTANT))

    assert set(result.model_dump()) == {"positions", "provenance"}
    assert result.model_dump()["positions"] == ()
    assert set(result.provenance.model_dump()) == {
        "provider",
        "calculation_instant",
        "configuration",
    }
