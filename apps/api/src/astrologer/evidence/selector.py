"""Pure deterministic selection of already-built governed evidence."""

from astrologer.evidence.models import EvidenceItem, EvidencePackage
from astrologer.evidence.selection_models import (
    EXACT_DOMAIN_SELECTION_POLICY_V1,
    EvidenceSelectionPolicy,
    EvidenceSelectionResult,
    ExcludedEvidenceReference,
    SelectionCapabilitySummary,
)
from astrologer.knowledge.models import EvidenceDirection, RulePosture
from astrologer.questions.models import QuestionIntent
from astrologer.rules.models import EvaluationStatus

SELECTOR_VERSION = "evidence-selector-v1"


class EvidenceSelector:
    """Select exact-domain package items without evaluating or interpreting them."""

    selector_version = SELECTOR_VERSION

    def select(
        self,
        intent: QuestionIntent,
        package: EvidencePackage,
        policy: EvidenceSelectionPolicy = EXACT_DOMAIN_SELECTION_POLICY_V1,
    ) -> EvidenceSelectionResult:
        """Return status-preserving evidence for one atomic question intent."""
        relevant: list[EvidenceItem] = []
        excluded: list[ExcludedEvidenceReference] = []
        for item in self._all_items(package):
            if item.domain.value == intent.domain.value:
                relevant.append(item)
            else:
                excluded.append(ExcludedEvidenceReference.from_item(item))

        ordered_relevant = tuple(sorted(relevant, key=self._item_key))
        matched = tuple(
            item for item in ordered_relevant if item.evaluation_status is EvaluationStatus.TRUE
        )
        unmatched = tuple(
            item for item in ordered_relevant if item.evaluation_status is EvaluationStatus.FALSE
        )
        unknown = tuple(
            item for item in ordered_relevant if item.evaluation_status is EvaluationStatus.UNKNOWN
        )
        ordered_excluded = tuple(
            sorted(excluded, key=lambda item: (item.rule_id, item.rule_version))
        )
        capability_summary = self._capabilities(intent, matched)
        provisional = EvidenceSelectionResult.model_construct(
            policy=policy,
            question_intent=intent,
            evidence_package_content_sha256=package.package_content_sha256,
            manifest_id=package.corpus_release.manifest_id,
            manifest_version=package.corpus_release.manifest_version,
            manifest_content_sha256=package.manifest_content_sha256,
            selected_matched=matched,
            relevant_unmatched=unmatched,
            relevant_unknown=unknown,
            excluded=ordered_excluded,
            capability_summary=capability_summary,
            selection_content_sha256="0" * 64,
        )
        return EvidenceSelectionResult(
            policy=policy,
            question_intent=intent,
            evidence_package_content_sha256=package.package_content_sha256,
            manifest_id=package.corpus_release.manifest_id,
            manifest_version=package.corpus_release.manifest_version,
            manifest_content_sha256=package.manifest_content_sha256,
            selected_matched=matched,
            relevant_unmatched=unmatched,
            relevant_unknown=unknown,
            excluded=ordered_excluded,
            capability_summary=capability_summary,
            selection_content_sha256=provisional.content_sha256(),
        )

    @staticmethod
    def _all_items(package: EvidencePackage) -> tuple[EvidenceItem, ...]:
        return (
            package.matched_evidence + package.unmatched_evaluations + package.unknown_evaluations
        )

    @staticmethod
    def _item_key(item: EvidenceItem) -> tuple[str, str]:
        return (item.rule_id, item.rule_version)

    @staticmethod
    def _capabilities(
        intent: QuestionIntent, matched: tuple[EvidenceItem, ...]
    ) -> SelectionCapabilitySummary:
        directions = {item.evidence_direction for item in matched}
        postures = {item.posture for item in matched}
        has_corroboration_required_match = RulePosture.CORROBORATION_REQUIRED in postures
        return SelectionCapabilitySummary(
            has_matched_evidence=bool(matched),
            has_supporting_match=EvidenceDirection.SUPPORTING in directions,
            has_challenging_match=EvidenceDirection.CHALLENGING in directions,
            has_contextual_match=EvidenceDirection.CONTEXTUAL in directions,
            timing_requested=intent.requires_timing,
            has_static_match=RulePosture.STATIC in postures,
            has_timing_required_match=RulePosture.TIMING_REQUIRED in postures,
            has_corroboration_required_match=has_corroboration_required_match,
            timing_answerability_established=False,
            corroboration_handling_deferred=has_corroboration_required_match,
        )
