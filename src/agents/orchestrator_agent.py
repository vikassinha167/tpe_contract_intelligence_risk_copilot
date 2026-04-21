"""Orchestrator agent — sequences sub-agents.

Open/Closed Principle in action: the orchestrator does not know any agent's
implementation; it just walks an injected list. New agent? Add to the list.
"""
from __future__ import annotations

from src.domain import Contract

from .base_agent import BaseAgent


class OrchestratorAgent(BaseAgent):
    name = "OrchestratorAgent"

    def __init__(self, agents: list[BaseAgent]) -> None:
        super().__init__()
        self._agents = agents

    def run(self, contract: Contract) -> Contract:
        self._log.info(
            "orchestrator.start",
            contract_id=contract.contract_id,
            agents=[a.name for a in self._agents],
        )
        for agent in self._agents:
            try:
                contract = agent.run(contract)
            except Exception as exc:  # noqa: BLE001 — top-level boundary
                self._log.error(
                    "agent.failed",
                    agent=agent.name,
                    contract_id=contract.contract_id,
                    error=str(exc),
                )
                contract.fail(f"{agent.name}: {exc}")
                break
        self._log.info(
            "orchestrator.done",
            contract_id=contract.contract_id,
            stage=contract.stage.value,
        )
        return contract
