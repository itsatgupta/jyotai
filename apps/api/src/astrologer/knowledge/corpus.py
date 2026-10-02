"""Versioned, allowlisted production corpus loading for admitted rule envelopes."""

import hashlib
import json
from collections.abc import Iterable, Mapping
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from astrologer.knowledge.admission import AdmissionError, AdmissionValidator
from astrologer.knowledge.models import FactContract, ProductionRuleEnvelope, SourceRegistry
from astrologer.rules.models import RuleDefinition

_IDENTIFIER = r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$"
_SHA256 = r"^[a-f0-9]{64}$"


class CorpusReleaseStatus(StrEnum):
    APPROVED = "approved"


class ManifestRule(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    rule_id: str = Field(pattern=_IDENTIFIER)
    rule_version: str = Field(min_length=1, max_length=64)
    envelope_sha256: str = Field(pattern=_SHA256)


class ProductionCorpusManifest(BaseModel):
    """An immutable, approved release allowlist; an empty release is valid."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    manifest_id: str = Field(pattern=_IDENTIFIER)
    manifest_version: str = Field(min_length=1, max_length=64)
    status: CorpusReleaseStatus = CorpusReleaseStatus.APPROVED
    governance_version: str = Field(
        default="jyotish-knowledge-governance-v1", min_length=1, max_length=64
    )
    registry_version: str = Field(min_length=1, max_length=64)
    fact_contract_id: str = Field(pattern=_IDENTIFIER)
    fact_contract_version: str = Field(min_length=1, max_length=64)
    rules: tuple[ManifestRule, ...] = ()

    @model_validator(mode="after")
    def rules_must_be_stably_ordered_and_unique(self) -> "ProductionCorpusManifest":
        keys = tuple((rule.rule_id, rule.rule_version) for rule in self.rules)
        if len(keys) != len(set(keys)):
            raise ValueError("manifest rule revisions must be unique")
        ordered = tuple(sorted(self.rules, key=lambda item: (item.rule_id, item.rule_version)))
        if ordered != self.rules:
            raise ValueError("manifest rules must use deterministic rule ID/version order")
        return self

    def content_sha256(self) -> str:
        return _sha256(self.model_dump(mode="json"))


EMPTY_PRODUCTION_MANIFEST = ProductionCorpusManifest(
    manifest_id="jyotish.production.empty",
    manifest_version="v1",
    registry_version="jyotish-source-registry-v1",
    fact_contract_id="jyotish.d1.structural",
    fact_contract_version="v1",
)


class ProductionCorpusLoadError(ValueError):
    """Raised when untrusted data or invalid governance cannot enter runtime."""


class ProductionCorpusLoader:
    """Load only manifest-allowlisted, admitted envelopes; never execute rule content."""

    def load(
        self,
        manifest: ProductionCorpusManifest,
        definitions: Iterable[ProductionRuleEnvelope | Mapping[str, Any]],
        registry: SourceRegistry,
        contract: FactContract,
    ) -> tuple[RuleDefinition, ...]:
        if manifest.status is not CorpusReleaseStatus.APPROVED:
            raise ProductionCorpusLoadError("production manifest must be approved")
        if manifest.registry_version != registry.registry_version:
            raise ProductionCorpusLoadError(
                "manifest registry version does not match source registry"
            )
        if (
            manifest.fact_contract_id != contract.contract_id
            or manifest.fact_contract_version != contract.contract_version
        ):
            raise ProductionCorpusLoadError(
                "manifest fact contract does not match supplied contract"
            )
        envelopes = tuple(
            self._parse(definition, index) for index, definition in enumerate(definitions)
        )
        manifest_keys = {(item.rule_id, item.rule_version): item for item in manifest.rules}
        envelope_keys = {(item.rule.rule_id, item.rule.rule_version) for item in envelopes}
        if envelope_keys != set(manifest_keys):
            raise ProductionCorpusLoadError(
                "manifest membership does not exactly match supplied rules"
            )
        validator = AdmissionValidator()
        admitted: list[RuleDefinition] = []
        for envelope in envelopes:
            key = (envelope.rule.rule_id, envelope.rule.rule_version)
            member = manifest_keys[key]
            if envelope_sha256(envelope) != member.envelope_sha256:
                raise ProductionCorpusLoadError(
                    "manifest hash does not match production rule envelope"
                )
            try:
                validator.validate_production_active(envelope, registry, contract)
            except AdmissionError as error:
                raise ProductionCorpusLoadError(
                    f"unadmitted production rule {key[0]}: {error}"
                ) from error
            admitted.append(envelope.rule)
        return tuple(sorted(admitted, key=lambda rule: (rule.rule_id, rule.rule_version)))

    @staticmethod
    def _parse(
        definition: ProductionRuleEnvelope | Mapping[str, Any], index: int
    ) -> ProductionRuleEnvelope:
        if isinstance(definition, ProductionRuleEnvelope):
            return definition
        _reject_unsafe_content(definition)
        try:
            return ProductionRuleEnvelope.model_validate(definition)
        except ValidationError as error:
            raise ProductionCorpusLoadError(
                f"invalid production rule definition at index {index}: {error}"
            ) from error


def envelope_sha256(envelope: ProductionRuleEnvelope) -> str:
    return _sha256(envelope.model_dump(mode="json"))


def _sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def _reject_unsafe_content(value: object) -> None:
    """Reject executable or YAML-tagged data before Pydantic can ignore unknown keys."""
    if callable(value):
        raise ProductionCorpusLoadError("production rule content must not contain callables")
    if isinstance(value, Mapping):
        for key, child in value.items():
            if not isinstance(key, str):
                raise ProductionCorpusLoadError("production rule mapping keys must be strings")
            normalized = key.lower().replace("-", "_")
            prohibited = {
                "script",
                "code",
                "python",
                "eval",
                "exec",
                "dynamic_import",
                "import",
            }
            if normalized in prohibited or key.startswith("!"):
                raise ProductionCorpusLoadError(
                    "production rule content must not contain executable content"
                )
            _reject_unsafe_content(child)
    elif isinstance(value, (tuple, list)):
        for child in value:
            _reject_unsafe_content(child)
