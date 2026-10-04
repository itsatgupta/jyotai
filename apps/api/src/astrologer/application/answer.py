"""Application orchestration for public, governed Ask JyotAI answers."""

import logging

from astrologer.application.analyze import (
    DeterministicAnalysisRequest,
    DeterministicAnalysisResult,
    DeterministicAnalysisService,
)
from astrologer.application.detailed_answer import DetailedAnswerBuilder
from astrologer.composition import (
    AnswerComposer,
    AnswerCompositionError,
    DetailedComposedAnswer,
    DeterministicAnswerComposer,
    LanguageModelTransportError,
    SeniorAstrologerComposer,
)
from astrologer.evidence import InterpretationEvidenceBuilder
from astrologer.evidence.selection_models import EvidenceSelectionResult


class AskJyotAIResult(DeterministicAnalysisResult):
    """Existing analysis response plus validated composed answers, in intent order."""

    answers: tuple[DetailedComposedAnswer, ...] = ()

    @classmethod
    def from_analysis(
        cls, analysis: DeterministicAnalysisResult, answers: tuple[DetailedComposedAnswer, ...]
    ) -> "AskJyotAIResult":
        return cls(
            context=analysis.context,
            routing=analysis.routing,
            evidence_package=analysis.evidence_package,
            selections=analysis.selections,
            answers=answers,
        )


class AskJyotAIService:
    """Compose answers from approved analyzer selections without router-side rule work."""

    def __init__(
        self,
        analysis_service: DeterministicAnalysisService,
        interpretation_evidence_builder: InterpretationEvidenceBuilder,
        answer_composer: AnswerComposer | DeterministicAnswerComposer | SeniorAstrologerComposer,
    ) -> None:
        self._analysis_service = analysis_service
        self._interpretation_evidence_builder = interpretation_evidence_builder
        self._answer_composer = answer_composer
        self._detailed_answer_builder = DetailedAnswerBuilder()
        self._logger = logging.getLogger(__name__)

    def answer(self, request: DeterministicAnalysisRequest) -> AskJyotAIResult:
        """Run deterministic analysis, then compose only validated evidence contracts."""
        analysis = self._analysis_service.analyze(request)
        answers = tuple(
            self._answer_one(request.question, selection) for selection in analysis.selections
        )
        return AskJyotAIResult.from_analysis(analysis, answers)

    def _answer_one(
        self, question: str, selection: EvidenceSelectionResult
    ) -> DetailedComposedAnswer:
        evidence = self._interpretation_evidence_builder.build(selection)
        deterministic = self._detailed_answer_builder.build(evidence)
        if not isinstance(self._answer_composer, SeniorAstrologerComposer):
            return deterministic
        if deterministic.corpus_limitation or evidence.relevant_unknown:
            self._logger.info("senior_narrative_composition_skipped reason=corpus_limit_or_unknown")
            return deterministic
        self._logger.info("senior_narrative_composition_attempted")
        try:
            narrative = self._answer_composer.compose(question, deterministic, evidence)
        except (LanguageModelTransportError, AnswerCompositionError) as error:
            self._logger.warning(
                "senior_narrative_composition_fallback category=%s reason_code=%s",
                error.category,
                error.reason_code
                if isinstance(error, AnswerCompositionError)
                else "provider_failed",
            )
            return deterministic
        if narrative is None:
            self._logger.info("senior_narrative_composition_fallback reason=not_composable")
            return deterministic
        self._logger.info("senior_narrative_composition_succeeded")
        return deterministic.model_copy(update={"narrative": narrative})
