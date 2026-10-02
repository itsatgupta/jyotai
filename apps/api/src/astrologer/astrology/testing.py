"""Test-only ephemeris provider implementations.

These providers never calculate or fabricate astronomical positions. They exist
solely to exercise the provider-neutral contract without a licensed ephemeris.
"""

from astrologer.astrology.ephemeris import (
    Ayanamsa,
    EphemerisProvenance,
    EphemerisProvider,
    EphemerisRequest,
    EphemerisResult,
    LunarNodeDefinition,
    ProviderCapabilities,
    ProviderMetadata,
    validate_provider_capabilities,
)


class DeterministicFakeEphemerisProvider:
    """A contract fake that returns no astronomical values."""

    def __init__(
        self,
        metadata: ProviderMetadata | None = None,
        capabilities: ProviderCapabilities | None = None,
    ) -> None:
        self._metadata = metadata or ProviderMetadata(
            provider_name="deterministic-test-fake",
            provider_version="1.0.0",
        )
        self._capabilities = capabilities or ProviderCapabilities(
            supported_ayanamsas=frozenset({Ayanamsa.LAHIRI}),
            supported_node_definitions=frozenset({LunarNodeDefinition.TRUE}),
            supports_motion_speed=True,
            supports_retrograde_input=True,
        )

    @property
    def metadata(self) -> ProviderMetadata:
        """Return deterministic test metadata."""
        return self._metadata

    @property
    def capabilities(self) -> ProviderCapabilities:
        """Return declared test capabilities."""
        return self._capabilities

    def calculate(self, request: EphemerisRequest) -> EphemerisResult:
        """Validate the contract and return an intentionally empty result."""
        validate_provider_capabilities(self, request)
        return EphemerisResult(
            positions=(),
            provenance=EphemerisProvenance(
                provider=self.metadata,
                calculation_instant=request.calculation_instant,
                configuration=request.configuration,
            ),
        )


def is_ephemeris_provider(provider: object) -> bool:
    """Expose a runtime Protocol check for tests and dependency wiring."""
    return isinstance(provider, EphemerisProvider)
