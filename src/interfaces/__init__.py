"""Abstract Ports (Interface Segregation + Dependency Inversion).

Every adapter in `infrastructure/` implements one of these tiny, focused
interfaces. Agents/services depend only on these abstractions.
"""
from .document_processor import ExtractedDocument, IDocumentProcessor
from .evaluator import IResponseEvaluator
from .guardrail import GuardrailVerdict, IGuardrail
from .language_analyzer import ILanguageAnalyzer, LanguageAnalysisResult
from .llm_client import ChatMessage, ILlmClient
from .repository import IContractRepository
from .search_indexer import ISearchIndexer
from .secret_provider import ISecretProvider
from .storage import IBlobStorage

__all__ = [
    "IDocumentProcessor",
    "ExtractedDocument",
    "IResponseEvaluator",
    "IGuardrail",
    "GuardrailVerdict",
    "ILanguageAnalyzer",
    "LanguageAnalysisResult",
    "ILlmClient",
    "ChatMessage",
    "IContractRepository",
    "ISearchIndexer",
    "ISecretProvider",
    "IBlobStorage",
]
