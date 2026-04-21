"""Repository abstraction for persistence (Repository Pattern)."""
from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain import Contract


class IContractRepository(ABC):
    @abstractmethod
    def save(self, contract: Contract) -> None:
        """Insert or update the contract aggregate."""

    @abstractmethod
    def get(self, contract_id: str) -> Contract | None:
        """Return the contract or `None` if missing."""
