"""Deterministic admission checks for governed, non-executable rule data."""

from collections.abc import Iterable

from astrologer.knowledge.models import (
    FactContract,
    ProductionRuleEnvelope,
    ReviewCategory,
    ReviewRecord,
    ReviewStatus,
    RuleLifecycle,
    SourceRegistry,
)
from astrologer.rules.models import ConditionDefinition


class AdmissionError(ValueError):
    """Raised when a rule cannot be admitted to a production corpus."""


_NEXT_STATES: dict[RuleLifecycle, frozenset[RuleLifecycle]] = {
    RuleLifecycle.DRAFT: frozenset(
        {RuleLifecycle.SOURCE_IDENTIFIED, RuleLifecycle.REJECTED, RuleLifecycle.ON_HOLD}
    ),
    RuleLifecycle.SOURCE_IDENTIFIED: frozenset(
        {RuleLifecycle.SOURCE_VERIFIED, RuleLifecycle.REJECTED, RuleLifecycle.ON_HOLD}
    ),
    RuleLifecycle.SOURCE_VERIFIED: frozenset(
        {RuleLifecycle.INTERPRETATION_REVIEWED, RuleLifecycle.DISPUTED, RuleLifecycle.ON_HOLD}
    ),
    RuleLifecycle.INTERPRETATION_REVIEWED: frozenset(
        {RuleLifecycle.FORMALIZED, RuleLifecycle.DISPUTED, RuleLifecycle.ON_HOLD}
    ),
    RuleLifecycle.FORMALIZED: frozenset(
        {RuleLifecycle.TESTED, RuleLifecycle.DISPUTED, RuleLifecycle.ON_HOLD}
    ),
    RuleLifecycle.TESTED: frozenset(
        {RuleLifecycle.APPROVED, RuleLifecycle.DISPUTED, RuleLifecycle.ON_HOLD}
    ),
    RuleLifecycle.APPROVED: frozenset(
        {
            RuleLifecycle.PRODUCTION_ACTIVE,
            RuleLifecycle.DISPUTED,
            RuleLifecycle.DEPRECATED,
            RuleLifecycle.SUPERSEDED,
        }
    ),
    RuleLifecycle.PRODUCTION_ACTIVE: frozenset(
        {RuleLifecycle.DISPUTED, RuleLifecycle.DEPRECATED, RuleLifecycle.SUPERSEDED}
    ),
    RuleLifecycle.ON_HOLD: frozenset({RuleLifecycle.SOURCE_IDENTIFIED, RuleLifecycle.REJECTED}),
    RuleLifecycle.DISPUTED: frozenset(
        {RuleLifecycle.ON_HOLD, RuleLifecycle.DEPRECATED, RuleLifecycle.SUPERSEDED}
    ),
    RuleLifecycle.REJECTED: frozenset(),
    RuleLifecycle.DEPRECATED: frozenset({RuleLifecycle.SUPERSEDED}),
    RuleLifecycle.SUPERSEDED: frozenset(),
}


def can_transition(current: RuleLifecycle, target: RuleLifecycle) -> bool:
    return target in _NEXT_STATES[current]


def require_transition(current: RuleLifecycle, target: RuleLifecycle) -> None:
    if not can_transition(current, target):
        raise AdmissionError(f"invalid lifecycle transition: {current.value} -> {target.value}")


class AdmissionValidator:
    """Validate an envelope against a reviewed source register and fact contract."""

    def validate_production_active(
        self,
        envelope: ProductionRuleEnvelope,
        registry: SourceRegistry,
        contract: FactContract,
    ) -> None:
        if envelope.lifecycle is not RuleLifecycle.PRODUCTION_ACTIVE:
            raise AdmissionError("only production_active rules may enter a production corpus")
        if envelope.rule.is_synthetic_demo:
            raise AdmissionError("synthetic/demo rules cannot be production-active")
        if envelope.rule.source is not None:
            raise AdmissionError("production source provenance must use the governance registry")
        if (
            envelope.fact_contract_id != contract.contract_id
            or envelope.fact_contract_version != contract.contract_version
        ):
            raise AdmissionError("rule fact contract does not match the supplied contract")
        if envelope.chart_scope is not contract.chart_scope:
            raise AdmissionError("rule chart scope is incompatible with its fact contract")
        if envelope.fact_contract_methodology_id != contract.methodology_id:
            raise AdmissionError("rule methodology is incompatible with its fact contract")
        interpretation = next(
            (
                item
                for item in registry.interpretations
                if item.interpretation_id == envelope.interpretation_id
            ),
            None,
        )
        if interpretation is None:
            raise AdmissionError("rule references an unknown reviewed interpretation")
        _require_review(
            interpretation.review,
            ReviewCategory.INTERPRETATION_REVIEW,
            "production rule requires a reviewed interpretation",
        )
        passage = next(
            (item for item in registry.passages if item.passage_id == interpretation.passage_id),
            None,
        )
        if passage is None:
            raise AdmissionError("interpretation references an unknown source passage")
        _require_review(
            passage.review,
            ReviewCategory.SOURCE_VERIFICATION,
            "production rule requires a verified source passage",
        )
        if interpretation.translation_id is not None:
            translation = next(
                (
                    item
                    for item in registry.translations
                    if item.translation_id == interpretation.translation_id
                ),
                None,
            )
            if translation is None:
                raise AdmissionError("referenced translation must be reviewed")
            _require_review(
                translation.review,
                ReviewCategory.TRANSLATION_VERIFICATION,
                "referenced translation must be reviewed",
            )
            if translation.passage_id != interpretation.passage_id:
                raise AdmissionError(
                    "translation and interpretation must reference the same passage"
                )
        _require_review(
            envelope.formalization_review,
            ReviewCategory.FORMALIZATION_REVIEW,
            "production rule requires a reviewed formalization",
        )
        self._validate_fact_dependencies(envelope, contract)

    def _validate_fact_dependencies(
        self, envelope: ProductionRuleEnvelope, contract: FactContract
    ) -> None:
        declared = tuple(dependency.key for dependency in envelope.fact_dependencies)
        for dependency in envelope.fact_dependencies:
            if (
                dependency.fact_id is not None
                and dependency.fact_id not in contract.available_fact_ids
            ):
                raise AdmissionError(f"unsupported fact dependency: {dependency.fact_id}")
            if (
                dependency.fact_family_prefix is not None
                and dependency.fact_family_prefix not in contract.available_fact_family_prefixes
            ):
                raise AdmissionError(
                    f"unsupported fact family dependency: {dependency.fact_family_prefix}"
                )
        for fact_id in _referenced_facts(envelope):
            if fact_id not in contract.available_fact_ids and not any(
                fact_id.startswith(prefix) for prefix in contract.available_fact_family_prefixes
            ):
                raise AdmissionError(f"rule references a fact outside its contract: {fact_id}")
            if fact_id not in declared and not any(
                dependency.endswith(".") and fact_id.startswith(dependency)
                for dependency in declared
            ):
                raise AdmissionError(
                    f"rule condition fact is not declared as a dependency: {fact_id}"
                )


def _referenced_facts(envelope: ProductionRuleEnvelope) -> tuple[str, ...]:
    definitions: list[ConditionDefinition] = [envelope.rule.condition]
    if envelope.applicability is not None:
        definitions.append(envelope.applicability.condition)
    definitions.extend(clause.condition for clause in envelope.prerequisites)
    definitions.extend(clause.condition for clause in envelope.exceptions)
    referenced: list[str] = []
    for definition in definitions:
        referenced.extend(_condition_fact_ids(definition))
    return tuple(dict.fromkeys(referenced))


def _condition_fact_ids(definition: ConditionDefinition) -> Iterable[str]:
    if definition.fact_id is not None:
        yield definition.fact_id
    for child in definition.children:
        yield from _condition_fact_ids(child)


def _require_review(
    review: ReviewRecord | None,
    category: ReviewCategory,
    message: str,
) -> None:
    if review is None:
        raise AdmissionError(message)
    if review.status is not ReviewStatus.REVIEWED:
        raise AdmissionError(message)
    if review.category is not category:
        raise AdmissionError(f"{message}: wrong review category")
