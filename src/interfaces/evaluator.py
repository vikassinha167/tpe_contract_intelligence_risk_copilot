"""Evaluation abstraction (Azure AI Foundry Evaluators)."""
from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain import EvaluationScores


class IResponseEvaluator(ABC):
    @abstractmethod
    def evaluate(
        self, *, query: str, response: str, context: str | None = None
    ) -> EvaluationScores:
        """Evaluate an LLM response for groundedness/relevance/coherence/fluency."""
