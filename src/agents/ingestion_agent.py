"""Ingestion agent — pulls a blob from storage into the Contract aggregate."""
from __future__ import annotations

from src.domain import Contract, PipelineStage
from src.interfaces import IBlobStorage

from .base_agent import BaseAgent

class IngestionAgent(BaseAgent):
    name = "IngestionAgent"

    def __init__(self, storage: IBlobStorage) -> None:
        super().__init__()
        self._storage = storage

    def run(self, contract: Contract) -> Contract:
        self._log_start(contract)
        data = self._storage.download_bytes(contract.source_blob)
        contract.metadata["raw_size_bytes"] = len(data)
        contract.metadata["_raw_bytes"] = data  # passed to next agent in-memory
        contract.advance(PipelineStage.INGESTED)
        self._log_done(contract)
        return contract
