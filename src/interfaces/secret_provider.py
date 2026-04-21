"""Secret-management abstraction (DIP).

Agents/adapters never call Key Vault directly — they request a named secret
through this small interface. This lets us substitute env-vars / fakes in tests.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class ISecretProvider(ABC):
    @abstractmethod
    def get_secret(self, name: str) -> str:
        """Return the secret value for `name` or raise `SecretNotFoundError`."""
