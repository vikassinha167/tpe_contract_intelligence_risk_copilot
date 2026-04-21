"""Guardrails abstraction (Azure AI Content Safety)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class GuardrailVerdict:
    allowed: bool
    reason: str | None = None
    categories: dict[str, int] | None = None  # category -> severity


class IGuardrail(ABC):
    @abstractmethod
    def check_input(self, text: str) -> GuardrailVerdict:
        """Validate user / system input before sending it to the LLM."""

    @abstractmethod
    def check_output(self, text: str) -> GuardrailVerdict:
        """Validate LLM output before persisting / returning it."""
