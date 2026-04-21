"""
Azure Search service implementation.

Provides document indexing and search capabilities.
"""

from typing import Any, Dict, List, Optional

from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SearchableField,
    SimpleField,
)
from azure.core.credentials import AzureKeyCredential

from contract_intelligence.config.settings import settings
from contract_intelligence.services.base import SearchService
from contract_intelligence.utils.exceptions import AzureServiceError
from contract_intelligence.utils.logging import get_logger

logger = get_logger(__name__)


class AzureSearchService(SearchService):
    """Azure Search service implementation."""

    def __init__(self) -> None:
        """Initialize the Search clients."""
        try:
            credential = AzureKeyCredential(settings.search.key.get_secret_value())

            self.search_client = SearchClient(
                endpoint=settings.search.endpoint,
                index_name=settings.search.index_name,
                credential=credential,
            )

            self.index_client = SearchIndexClient(
                endpoint=settings.search.endpoint,
                credential=credential,
            )

            # Ensure index exists
            self._create_index_if_not_exists()

            logger.info("Azure Search service initialized", index_name=settings.search.index_name)
        except Exception as e:
            logger.error("Failed to initialize Search service", error=str(e))
            raise AzureServiceError(f"Failed to initialize Search service: {e}") from e

    def _create_index_if_not_exists(self) -> None:
        """Create the search index if it doesn't exist."""
        try:
            # Check if index exists
            try:
                self.index_client.get_index(settings.search.index_name)
                logger.info("Search index already exists", index_name=settings.search.index_name)
                return
            except Exception:
                pass  # Index doesn't exist, create it

            # Define index schema
            fields = [
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                SearchableField(name="content", type=SearchFieldDataType.String),
                SimpleField(name="document_type", type=SearchFieldDataType.String),
                SimpleField(name="entities", type=SearchFieldDataType.Collection(SearchFieldDataType.String)),
                SimpleField(name="key_phrases", type=SearchFieldDataType.Collection(SearchFieldDataType.String)),
                SimpleField(name="sentiment", type=SearchFieldDataType.String),
                SimpleField(name="risk_score", type=SearchFieldDataType.Double),
                SimpleField(name="created_at", type=SearchFieldDataType.DateTimeOffset),
            ]

            index = SearchIndex(name=settings.search.index_name, fields=fields)
            self.index_client.create_index(index)
            logger.info("Search index created", index_name=settings.search.index_name)

        except Exception as e:
            logger.error("Failed to create search index", error=str(e))
            raise AzureServiceError(f"Failed to create search index: {e}") from e

    def index_document(self, document_id: str, content: Dict[str, Any]) -> None:
        """
        Index a document in the search service.

        Args:
            document_id: Unique identifier for the document.
            content: Document content to index.

        Raises:
            AzureServiceError: If indexing fails.
        """
        try:
            logger.info("Indexing document", document_id=document_id)

            # Prepare document for indexing
            search_document = {
                "id": document_id,
                "content": content.get("content", ""),
                "document_type": content.get("document_type"),
                "entities": [entity["text"] for entity in content.get("entities", [])],
                "key_phrases": content.get("key_phrases", []),
                "sentiment": content.get("sentiment", {}).get("overall") if content.get("sentiment") else None,
                "risk_score": content.get("risk_score"),
                "created_at": content.get("created_at"),
            }

            # Upload document
            documents = [search_document]
            result = self.search_client.upload_documents(documents)

            if result[0].succeeded:
                logger.info("Document indexed successfully", document_id=document_id)
            else:
                raise AzureServiceError(f"Indexing failed: {result[0].error_message}")

        except Exception as e:
            logger.error("Document indexing failed", document_id=document_id, error=str(e))
            raise AzureServiceError(f"Document indexing failed: {e}") from e

    def search_documents(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for documents matching the query.

        Args:
            query: Search query string.
            filters: Optional filters to apply.

        Returns:
            List of matching documents.

        Raises:
            AzureServiceError: If search fails.
        """
        try:
            logger.info("Searching documents", query=query, filters=filters)

            # Build search options
            search_options = {
                "search_text": query,
                "select": ["id", "content", "document_type", "entities", "key_phrases", "sentiment", "risk_score"],
                "top": 50,  # Limit results
            }

            if filters:
                filter_conditions = []
                if "document_type" in filters:
                    filter_conditions.append(f"document_type eq '{filters['document_type']}'")
                if "min_risk_score" in filters:
                    filter_conditions.append(f"risk_score ge {filters['min_risk_score']}")
                if "max_risk_score" in filters:
                    filter_conditions.append(f"risk_score le {filters['max_risk_score']}")

                if filter_conditions:
                    search_options["filter"] = " and ".join(filter_conditions)

            # Perform search
            results = self.search_client.search(**search_options)

            # Format results
            documents = []
            for result in results:
                documents.append(dict(result))

            logger.info("Search completed", query=query, results_count=len(documents))
            return documents

        except Exception as e:
            logger.error("Document search failed", query=query, error=str(e))
            raise AzureServiceError(f"Document search failed: {e}") from e