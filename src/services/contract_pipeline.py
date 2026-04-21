"""High-level pipeline service — the public API of the application."""
from __future__ import annotations

from src.agents import OrchestratorAgent
from src.domain import Contract


class ContractIntelligencePipeline:
    """Thin façade so callers (CLI, API, Function App) never touch agents directly."""

    def __init__(self, orchestrator: OrchestratorAgent) -> None:
        self._orchestrator = orchestrator

    def process(self, blob_name: str, *, title: str | None = None) -> Contract:
        contract = Contract(source_blob=blob_name, title=title)
        return self._orchestrator.run(contract)
