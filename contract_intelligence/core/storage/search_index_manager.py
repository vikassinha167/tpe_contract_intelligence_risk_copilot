"""
Search index manager for contract data.

Manages indexing and searching of contract knowledge.
"""

from typing import Dict, List, Any, Optional

from contract_intelligence.services.base import SearchService
from contract_intelligence.utils.exceptions import StorageError
from contract_intelligence.utils.logging import get_logger

logger = get_logger(__name__)


class SearchIndexManager:
    """
    Manages search indexing operations for contract data.

    Provides high-level operations for document indexing and search.
    """

    def __init__(self, search_service: SearchService) -> None:
        """
        Initialize the search index manager.

        Args:
            search_service: Search service.
        """
        self.search_service = search_service
        logger.info("Search index manager initialized")

    def index_contract(self, document_id: str, contract_data: Dict[str, Any]) -> None:
        """
        Index a contract document.

        Args:
            document_id: Unique document identifier.
            contract_data: Processed contract data to index.

        Raises:
            StorageError: If indexing fails.
        """
        try:
            logger.info("Indexing contract", document_id=document_id)

            # Prepare content for indexing
            index_content = {
                "document_id": document_id,
                "content": contract_data.get("content", ""),
                "document_type": contract_data.get("document_type"),
                "entities": contract_data.get("entities", []),
                "key_phrases": contract_data.get("key_phrases", []),
                "sentiment": contract_data.get("sentiment"),
                "risk_score": contract_data.get("risk_score"),
                "created_at": contract_data.get("created_at"),
            }

            # Add clause information
            clauses = contract_data.get("clauses", {})
            for clause_name, clause_data in clauses.items():
                if clause_name not in index_content:
                    index_content[f"clause_{clause_name}"] = clause_data.get("content", "")

            self.search_service.index_document(document_id, index_content)

            logger.info("Contract indexed successfully", document_id=document_id)

        except Exception as e:
            logger.error("Contract indexing failed", document_id=document_id, error=str(e))
            raise StorageError(f"Contract indexing failed: {e}") from e

    def search_contracts(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for contracts matching the query.

        Args:
            query: Search query string.
            filters: Optional filters to apply.

        Returns:
            List of matching contracts.

        Raises:
            StorageError: If search fails.
        """
        try:
            logger.info("Searching contracts", query=query, filters=filters)

            results = self.search_service.search_documents(query, filters)

            logger.info("Contract search completed", result_count=len(results))
            return results

        except Exception as e:
            logger.error("Contract search failed", query=query, error=str(e))
            raise StorageError(f"Contract search failed: {e}") from e

    def search_by_risk_level(self, min_risk: float = 0.0, max_risk: float = 1.0) -> List[Dict[str, Any]]:
        """
        Search contracts by risk score range.

        Args:
            min_risk: Minimum risk score (0.0 to 1.0).
            max_risk: Maximum risk score (0.0 to 1.0).

        Returns:
            List of contracts within risk range.
        """
        filters = {
            "min_risk_score": min_risk,
            "max_risk_score": max_risk,
        }
        return self.search_contracts("*", filters)

    def search_by_document_type(self, document_type: str) -> List[Dict[str, Any]]:
        """
        Search contracts by document type.

        Args:
            document_type: Type of document to search for.

        Returns:
            List of contracts of the specified type.
        """
        filters = {"document_type": document_type}
        return self.search_contracts("*", filters)