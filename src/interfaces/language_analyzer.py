"""Language analysis abstraction (NER, key-phrases, PII)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from src.domain import Entity


@dataclass(frozen=True)
class LanguageAnalysisResult:
    entities: list[Entity] = field(default_factory=list)
    key_phrases: list[str] = field(default_factory=list)
    pii_entities: list[Entity] = field(default_factory=list)


class ILanguageAnalyzer(ABC):
    @abstractmethod
    def analyze(self, text: str) -> LanguageAnalysisResult:
        """Run NER, key-phrase, and PII detection on the text."""
