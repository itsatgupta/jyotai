"""Application orchestration for public, governed Ask JyotAI answers."""

from astrologer.application.analyze import (
    DeterministicAnalysisRequest,
    DeterministicAnalysisResult,
    DeterministicAnalysisService,
)
from astrologer.application.detailed_answer import DetailedAnswerBuilder
from astrologer.composition import (
    AnswerComposer,
    DetailedComposedAnswer,
    DeterministicAnswerComposer,
)
from astrologer.evidence import InterpretationEvidenceBuilder


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
        answer_composer: AnswerComposer | DeterministicAnswerComposer,
    ) -> None:
        self._analysis_service = analysis_service
        self._interpretation_evidence_builder = interpretation_evidence_builder
        self._answer_composer = answer_composer
        self._detailed_answer_builder = DetailedAnswerBuilder()

    def answer(self, request: DeterministicAnalysisRequest) -> AskJyotAIResult:
        """Run deterministic analysis, then compose only validated evidence contracts."""
        analysis = self._analysis_service.analyze(request)
        answers = tuple(
            self._detailed_answer_builder.build(
                self._interpretation_evidence_builder.build(selection)
            )
            for selection in analysis.selections
        )
        return AskJyotAIResult.from_analysis(analysis, answers)
