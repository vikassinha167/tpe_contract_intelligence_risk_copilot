"""Azure AI Foundry Evaluator adapter implementing `IResponseEvaluator`.

Uses the `azure-ai-evaluation` SDK with built-in evaluators powered by the
same Azure OpenAI deployment we already use.
"""
from __future__ import annotations

from typing import Any

from src.domain import EvaluationScores
from src.interfaces import IResponseEvaluator


class AzureFoundryEvaluator(IResponseEvaluator):
    """Lazy-imports the SDK so unit tests don't need it installed."""

    def __init__(self, *, endpoint: str, deployment: str, api_version: str) -> None:
        # Local import keeps import-time cost low and avoids hard dep in tests.
        from azure.ai.evaluation import (
            CoherenceEvaluator,
            FluencyEvaluator,
            GroundednessEvaluator,
            RelevanceEvaluator,
        )

        model_config: dict[str, Any] = {
            "azure_endpoint": endpoint,
            "azure_deployment": deployment,
            "api_version": api_version,
        }
        self._groundedness = GroundednessEvaluator(model_config=model_config)
        self._relevance = RelevanceEvaluator(model_config=model_config)
        self._coherence = CoherenceEvaluator(model_config=model_config)
        self._fluency = FluencyEvaluator(model_config=model_config)

    def evaluate(
        self, *, query: str, response: str, context: str | None = None
    ) -> EvaluationScores:
        scores = EvaluationScores()
        try:
            if context:
                g = self._groundedness(
                    query=query, response=response, context=context
                )
                scores.groundedness = float(g.get("groundedness", 0.0))
            r = self._relevance(query=query, response=response)
            scores.relevance = float(r.get("relevance", 0.0))
            c = self._coherence(query=query, response=response)
            scores.coherence = float(c.get("coherence", 0.0))
            f = self._fluency(query=query, response=response)
            scores.fluency = float(f.get("fluency", 0.0))
        except Exception:  # noqa: BLE001 — evaluation must never fail the pipeline
            pass
        return scores
