"""Search index abstraction (Azure AI Search)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ISearchIndexer(ABC):
    @abstractmethod
    def ensure_index(self) -> None:
        """Create the index if missing — idempotent."""

    @abstractmethod
    def upsert_document(self, document: dict[str, Any]) -> None:
        """Insert / update a document keyed by `id`."""

    @abstractmethod
    def search(self, query: str, top: int = 5) -> list[dict[str, Any]]:
        """Hybrid / keyword search returning top documents."""
