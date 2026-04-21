"""
Base service interfaces and abstract classes.

Defines contracts for Azure service integrations following the Dependency Inversion Principle.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol

from contract_intelligence.utils.exceptions import AzureServiceError


class DocumentIntelligenceService(Protocol):
    """Protocol for document intelligence operations."""

    def analyze_document(self, document_path: str) -> Dict[str, Any]:
        """
        Analyze a document and extract structured data.

        Args:
            document_path: Path to the document file.

        Returns:
            Dictionary containing extracted data.
        """
        ...


class LanguageService(Protocol):
    """Protocol for language processing operations."""

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for entities, sentiment, and key phrases.

        Args:
            text: The text to analyze.

        Returns:
            Dictionary containing analysis results.
        """
        ...


class SearchService(Protocol):
    """Protocol for search operations."""

    def index_document(self, document_id: str, content: Dict[str, Any]) -> None:
        """
        Index a document in the search service.

        Args:
            document_id: Unique identifier for the document.
            content: Document content to index.
        """
        ...

    def search_documents(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for documents matching the query.

        Args:
            query: Search query string.
            filters: Optional filters to apply.

        Returns:
            List of matching documents.
        """
        ...


class BlobStorageService(Protocol):
    """Protocol for blob storage operations."""

    def upload_file(self, file_path: str, blob_name: str) -> str:
        """
        Upload a file to blob storage.

        Args:
            file_path: Local path to the file.
            blob_name: Name for the blob.

        Returns:
            URL of the uploaded blob.
        """
        ...

    def download_file(self, blob_name: str, local_path: str) -> None:
        """
        Download a file from blob storage.

        Args:
            blob_name: Name of the blob.
            local_path: Local path to save the file.
        """
        ...


class SQLService(Protocol):
    """Protocol for SQL database operations."""

    def insert_contract(self, contract_data: Dict[str, Any]) -> int:
        """
        Insert contract data into the database.

        Args:
            contract_data: Contract data to insert.

        Returns:
            ID of the inserted record.
        """
        ...

    def get_contract(self, contract_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve contract data by ID.

        Args:
            contract_id: Contract ID.

        Returns:
            Contract data if found, None otherwise.
        """
        ...


class KeyVaultService(Protocol):
    """Protocol for key vault operations."""

    def get_secret(self, secret_name: str) -> str:
        """
        Retrieve a secret from key vault.

        Args:
            secret_name: Name of the secret.

        Returns:
            Secret value.
        """
        ...


class OpenAIService(Protocol):
    """Protocol for OpenAI operations."""

    def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a response using OpenAI.

        Args:
            prompt: The prompt for generation.
            context: Optional context information.

        Returns:
            Generated response.
        """
        ...


class AIServiceFactory(ABC):
    """Abstract factory for creating AI services."""

    @abstractmethod
    def create_document_intelligence_service(self) -> DocumentIntelligenceService:
        """Create document intelligence service instance."""
        pass

    @abstractmethod
    def create_language_service(self) -> LanguageService:
        """Create language service instance."""
        pass

    @abstractmethod
    def create_search_service(self) -> SearchService:
        """Create search service instance."""
        pass

    @abstractmethod
    def create_blob_storage_service(self) -> BlobStorageService:
        """Create blob storage service instance."""
        pass

    @abstractmethod
    def create_sql_service(self) -> SQLService:
        """Create SQL service instance."""
        pass

    @abstractmethod
    def create_key_vault_service(self) -> KeyVaultService:
        """Create key vault service instance."""
        pass

    @abstractmethod
    def create_openai_service(self) -> OpenAIService:
        """Create OpenAI service instance."""
        pass