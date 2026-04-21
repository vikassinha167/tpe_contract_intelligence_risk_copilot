"""Concrete Azure adapters. Imported lazily by the DI container."""
from .azure_blob_storage import AzureBlobStorage
from .azure_document_intelligence import AzureDocumentIntelligenceProcessor
from .azure_evaluator import AzureFoundryEvaluator
from .azure_guardrails import AzureContentSafetyGuardrail
from .azure_key_vault import AzureKeyVaultSecretProvider
from .azure_language_service import AzureLanguageAnalyzer
from .azure_openai_client import AzureOpenAILlmClient
from .azure_search_index import AzureSearchIndexer
from .azure_sql_repository import AzureSqlContractRepository

__all__ = [
    "AzureBlobStorage",
    "AzureDocumentIntelligenceProcessor",
    "AzureFoundryEvaluator",
    "AzureContentSafetyGuardrail",
    "AzureKeyVaultSecretProvider",
    "AzureLanguageAnalyzer",
    "AzureOpenAILlmClient",
    "AzureSearchIndexer",
    "AzureSqlContractRepository",
]
