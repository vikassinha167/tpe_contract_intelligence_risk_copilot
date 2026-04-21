"""Persistence agent — final stage, saves the contract via the repository port."""
from __future__ import annotations

from src.domain import Contract, PipelineStage
from src.interfaces import IContractRepository

from .base_agent import BaseAgent


class PersistenceAgent(BaseAgent):
    name = "PersistenceAgent"

    def __init__(self, repo: IContractRepository) -> None:
        super().__init__()
        self._repo = repo

    def run(self, contract: Contract) -> Contract:
        self._log_start(contract)
        self._repo.save(contract)
        contract.advance(PipelineStage.PERSISTED)
        self._log_done(contract)
        return contract
