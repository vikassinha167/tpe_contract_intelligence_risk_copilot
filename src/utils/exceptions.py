"""Project-specific exceptions — never leak SDK exception types out of adapters."""
from __future__ import annotations


class ContractIntelligenceError(Exception):
    """Base class for all domain/application errors."""


class SecretNotFoundError(ContractIntelligenceError):
    pass


class DocumentProcessingError(ContractIntelligenceError):
    pass


class LanguageAnalysisError(ContractIntelligenceError):
    pass


class IndexingError(ContractIntelligenceError):
    pass


class LlmInvocationError(ContractIntelligenceError):
    pass


class GuardrailViolationError(ContractIntelligenceError):
    pass


class PersistenceError(ContractIntelligenceError):
    pass
