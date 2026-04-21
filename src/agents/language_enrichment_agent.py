"""Language enrichment agent — NER, key phrases, PII detection."""
from __future__ import annotations

from src.domain import Contract, PipelineStage
from src.interfaces import ILanguageAnalyzer

from .base_agent import BaseAgent


class LanguageEnrichmentAgent(BaseAgent):
    name = "LanguageEnrichmentAgent"

    def __init__(self, analyzer: ILanguageAnalyzer) -> None:
        super().__init__()
        self._analyzer = analyzer

    def run(self, contract: Contract) -> Contract:
        self._log_start(contract)
        if not contract.raw_text:
            raise ValueError("LanguageEnrichmentAgent requires raw_text")
        result = self._analyzer.analyze(contract.raw_text)
        contract.entities = result.entities
        contract.key_phrases = result.key_phrases
        contract.pii_detected = result.pii_entities
        contract.advance(PipelineStage.LANGUAGE_ENRICHED)
        self._log_done(contract)
        return contract
