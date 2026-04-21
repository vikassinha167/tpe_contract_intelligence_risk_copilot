"""
SQL storage manager for contract metadata.

Manages storage and retrieval of contract metadata in SQL database.
"""

from typing import Dict, Any, Optional

from contract_intelligence.services.base import SQLService
from contract_intelligence.utils.exceptions import StorageError
from contract_intelligence.utils.logging import get_logger

logger = get_logger(__name__)


class SQLStorageManager:
    """
    Manages SQL database operations for contract metadata.

    Provides high-level operations for contract metadata storage.
    """

    def __init__(self, sql_service: SQLService) -> None:
        """
        Initialize the SQL storage manager.

        Args:
            sql_service: SQL service.
        """
        self.sql_service = sql_service
        logger.info("SQL storage manager initialized")

    def store_contract_metadata(self, contract_data: Dict[str, Any]) -> int:
        """
        Store contract metadata in the database.

        Args:
            contract_data: Contract metadata to store.

        Returns:
            Database ID of the stored contract.

        Raises:
            StorageError: If storage fails.
        """
        try:
            logger.info("Storing contract metadata", document_id=contract_data.get("document_id"))

            # Prepare data for storage
            metadata = {
                "document_id": contract_data["document_id"],
                "blob_url": contract_data.get("blob_url"),
                "document_type": contract_data.get("document_type"),
                "content_summary": self._generate_content_summary(contract_data),
                "risk_score": contract_data.get("risk_score"),
            }

            contract_id = self.sql_service.insert_contract(metadata)

            logger.info("Contract metadata stored successfully", contract_id=contract_id)
            return contract_id

        except Exception as e:
            logger.error("Contract metadata storage failed", document_id=contract_data.get("document_id"), error=str(e))
            raise StorageError(f"Contract metadata storage failed: {e}") from e

    def retrieve_contract_metadata(self, contract_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve contract metadata from the database.

        Args:
            contract_id: Database ID of the contract.

        Returns:
            Contract metadata if found, None otherwise.

        Raises:
            StorageError: If retrieval fails.
        """
        try:
            logger.info("Retrieving contract metadata", contract_id=contract_id)

            metadata = self.sql_service.get_contract(contract_id)

            if metadata:
                logger.info("Contract metadata retrieved successfully", contract_id=contract_id)
            else:
                logger.info("Contract metadata not found", contract_id=contract_id)

            return metadata

        except Exception as e:
            logger.error("Contract metadata retrieval failed", contract_id=contract_id, error=str(e))
            raise StorageError(f"Contract metadata retrieval failed: {e}") from e

    def _generate_content_summary(self, contract_data: Dict[str, Any]) -> str:
        """
        Generate a content summary from contract data.

        Args:
            contract_data: Contract data.

        Returns:
            Content summary string.
        """
        summary_parts = []

        document_type = contract_data.get("document_type")
        if document_type:
            summary_parts.append(f"Document Type: {document_type}")

        clauses = contract_data.get("clauses", {})
        if clauses:
            clause_count = len(clauses)
            summary_parts.append(f"Clauses: {clause_count}")

            # Add key clauses
            key_clauses = ["party_one", "party_two", "effective_date", "governing_law"]
            for clause in key_clauses:
                if clause in clauses and clauses[clause].get("content"):
                    summary_parts.append(f"{clause.replace('_', ' ').title()}: {clauses[clause]['content'][:100]}...")

        risk_score = contract_data.get("risk_score")
        if risk_score is not None:
            summary_parts.append(f"Risk Score: {risk_score:.2f}")

        return " | ".join(summary_parts)