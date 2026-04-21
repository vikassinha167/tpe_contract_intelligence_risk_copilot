"""Document processing abstraction (Document Intelligence)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractedDocument:
    text: str
    page_count: int
    raw: dict | None = None  # full Azure response if caller needs it


class IDocumentProcessor(ABC):
    @abstractmethod
    def extract(self, content: bytes) -> ExtractedDocument:
        """Run OCR + layout extraction on raw document bytes."""
