"""
Azure service factory implementation.

Creates instances of Azure services following the Factory pattern.
"""

from contract_intelligence.services.azure_blob import AzureBlobStorageService
from contract_intelligence.services.azure_document_intelligence import AzureDocumentIntelligenceService
from contract_intelligence.services.azure_key_vault import AzureKeyVaultService
from contract_intelligence.services.azure_language import AzureLanguageService
from contract_intelligence.services.azure_openai import AzureOpenAIService
from contract_intelligence.services.azure_search import AzureSearchService
from contract_intelligence.services.azure_sql import AzureSQLService
from contract_intelligence.services.base import AIServiceFactory
from contract_intelligence.utils.logging import get_logger

logger = get_logger(__name__)


class AzureServiceFactory(AIServiceFactory):
    """Factory for creating Azure AI service instances."""

    def __init__(self) -> None:
        """Initialize the factory."""
        logger.info("Azure Service Factory initialized")

    def create_document_intelligence_service(self):
        """Create document intelligence service instance."""
        return AzureDocumentIntelligenceService()

    def create_language_service(self):
        """Create language service instance."""
        return AzureLanguageService()

    def create_search_service(self):
        """Create search service instance."""
        return AzureSearchService()

    def create_blob_storage_service(self):
        """Create blob storage service instance."""
        return AzureBlobStorageService()

    def create_sql_service(self):
        """Create SQL service instance."""
        return AzureSQLService()

    def create_key_vault_service(self):
        """Create key vault service instance."""
        return AzureKeyVaultService()

    def create_openai_service(self):
        """Create OpenAI service instance."""
        return AzureOpenAIService()