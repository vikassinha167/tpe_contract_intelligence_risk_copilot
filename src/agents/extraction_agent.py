"""Extraction agent — runs Document Intelligence to extract text + structure."""
from __future__ import annotations

from src.domain import Contract, PipelineStage
from src.interfaces import IDocumentProcessor

from .base_agent import BaseAgent


class ExtractionAgent(BaseAgent):
    name = "ExtractionAgent"

    def __init__(self, processor: IDocumentProcessor) -> None:
        super().__init__()
        self._processor = processor

    def run(self, contract: Contract) -> Contract:
        self._log_start(contract)
        raw = contract.metadata.pop("_raw_bytes", None)
        if raw is None:
            raise ValueError("ExtractionAgent requires _raw_bytes from IngestionAgent")
        extracted = self._processor.extract(raw)
        contract.raw_text = extracted.text
        contract.page_count = extracted.page_count
        contract.advance(PipelineStage.EXTRACTED)
        self._log_done(contract)
        return contract
