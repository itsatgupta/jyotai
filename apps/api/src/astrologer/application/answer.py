"""Application orchestration for public, governed Ask JyotAI answers."""

from astrologer.application.analyze import (
    DeterministicAnalysisRequest,
    DeterministicAnalysisResult,
    DeterministicAnalysisService,
)
from astrologer.composition import AnswerComposer, ComposedAnswer
from astrologer.evidence import InterpretationEvidenceBuilder


class AskJyotAIResult(DeterministicAnalysisResult):
    """Existing analysis response plus validated composed answers, in intent order."""

    answers: tuple[ComposedAnswer, ...] = ()

    @classmethod
    def from_analysis(
        cls, analysis: DeterministicAnalysisResult, answers: tuple[ComposedAnswer, ...]
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
        answer_composer: AnswerComposer,
    ) -> None:
        self._analysis_service = analysis_service
        self._interpretation_evidence_builder = interpretation_evidence_builder
        self._answer_composer = answer_composer

    def answer(self, request: DeterministicAnalysisRequest) -> AskJyotAIResult:
        """Run deterministic analysis, then compose only validated evidence contracts."""
        analysis = self._analysis_service.analyze(request)
        answers = tuple(
            self._answer_composer.compose(
                request.question, self._interpretation_evidence_builder.build(selection)
            )
            for selection in analysis.selections
        )
        return AskJyotAIResult.from_analysis(analysis, answers)
