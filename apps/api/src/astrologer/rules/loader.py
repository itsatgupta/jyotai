"""Format-neutral validation boundary for declarative rule definitions."""

from collections.abc import Iterable, Mapping
from typing import Any

from pydantic import ValidationError

from astrologer.rules.models import RuleDefinition, RuleSet


class RuleLoadError(ValueError):
    """Raised when untrusted structured rule data cannot form a valid ruleset."""


class RuleLoader:
    """Load already-parsed JSON-compatible data without executing any content."""

    def load(
        self,
        ruleset_version: str,
        definitions: Iterable[RuleDefinition | Mapping[str, Any]],
    ) -> RuleSet:
        """Validate, deduplicate, and deterministically order rule definitions."""
        loaded: list[RuleDefinition] = []
        for index, definition in enumerate(definitions):
            try:
                rule = (
                    definition
                    if isinstance(definition, RuleDefinition)
                    else RuleDefinition.model_validate(definition)
                )
            except ValidationError as error:
                raise RuleLoadError(f"invalid rule definition at index {index}: {error}") from error
            loaded.append(rule)
        try:
            return RuleSet(
                ruleset_version=ruleset_version,
                rules=tuple(sorted(loaded, key=lambda rule: (rule.rule_id, rule.rule_version))),
            )
        except ValidationError as error:
            raise RuleLoadError(f"invalid ruleset: {error}") from error
