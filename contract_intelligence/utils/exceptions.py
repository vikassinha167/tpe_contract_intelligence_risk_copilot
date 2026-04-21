"""
Custom exceptions for the Contract Intelligence application.

Defines specific exception types for different error scenarios.
"""


class ContractIntelligenceError(Exception):
    """Base exception for all contract intelligence errors."""
    pass


class IngestionError(ContractIntelligenceError):
    """Raised when document ingestion fails."""
    pass


class ProcessingError(ContractIntelligenceError):
    """Raised when document processing fails."""
    pass


class StorageError(ContractIntelligenceError):
    """Raised when data storage operations fail."""
    pass


class QueryError(ContractIntelligenceError):
    """Raised when query operations fail."""
    pass


class RiskScoringError(ContractIntelligenceError):
    """Raised when risk scoring operations fail."""
    pass


class AzureServiceError(ContractIntelligenceError):
    """Raised when Azure service calls fail."""
    pass


class ConfigurationError(ContractIntelligenceError):
    """Raised when configuration is invalid."""
    pass