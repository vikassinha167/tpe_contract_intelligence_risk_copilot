"""Indexing agent — pushes the contract into Azure AI Search."""
from __future__ import annotations

from src.domain import Contract, PipelineStage
from src.interfaces import ISearchIndexer

from .base_agent import BaseAgent


class IndexingAgent(BaseAgent):
    name = "IndexingAgent"

    def __init__(self, indexer: ISearchIndexer) -> None:
        super().__init__()
        self._indexer = indexer

    def run(self, contract: Contract) -> Contract:
        self._log_start(contract)
        self._indexer.ensure_index()
        self._indexer.upsert_document(
            {
                "id": contract.contract_id,
                "title": contract.title or contract.source_blob,
                "content": contract.raw_text or "",
                "entities": [e.text for e in contract.entities][:200],
                "risk_level": contract.overall_risk_level.value
                if contract.overall_risk_level
                else "Unknown",
                "risk_score": float(contract.overall_risk_score or 0.0),
            }
        )
        contract.advance(PipelineStage.INDEXED)
        self._log_done(contract)
        return contract
