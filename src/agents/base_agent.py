"""Base agent — defines the common contract for every agent in the system.

A multi-agent system benefits from a uniform shape: each agent receives a
`Contract` aggregate, mutates it (or fails it), and returns it. This makes
composition trivial and keeps the OrchestratorAgent agnostic of specifics.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from config import get_logger
from src.domain import Contract


class BaseAgent(ABC):
    """All agents must subclass this."""

    name: str = "BaseAgent"

    def __init__(self) -> None:
        self._log = get_logger(self.name)

    @abstractmethod
    def run(self, contract: Contract) -> Contract:
        """Process the contract aggregate and return it."""

    # -- shared helpers ---------------------------------------------------
    def _log_start(self, contract: Contract) -> None:
        self._log.info("agent.start", contract_id=contract.contract_id)

    def _log_done(self, contract: Contract) -> None:
        self._log.info(
            "agent.done", contract_id=contract.contract_id, stage=contract.stage.value
        )
