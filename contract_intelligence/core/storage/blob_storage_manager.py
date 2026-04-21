"""
Blob storage manager for contract data.

Manages storage and retrieval of contract documents in blob storage.
"""

from typing import List, Optional

from contract_intelligence.services.base import BlobStorageService
from contract_intelligence.utils.exceptions import StorageError
from contract_intelligence.utils.logging import get_logger

logger = get_logger(__name__)


class BlobStorageManager:
    """
    Manages blob storage operations for contract documents.

    Provides high-level operations for document storage management.
    """

    def __init__(self, blob_storage: BlobStorageService) -> None:
        """
        Initialize the blob storage manager.

        Args:
            blob_storage: Blob storage service.
        """
        self.blob_storage = blob_storage
        logger.info("Blob storage manager initialized")

    def store_document(self, local_path: str, document_id: str, file_extension: str) -> str:
        """
        Store a document in blob storage.

        Args:
            local_path: Local path to the document file.
            document_id: Unique document identifier.
            file_extension: File extension (e.g., '.pdf').

        Returns:
            Blob URL of the stored document.

        Raises:
            StorageError: If storage fails.
        """
        try:
            logger.info("Storing document in blob storage", document_id=document_id)

            blob_name = f"{document_id}{file_extension}"
            blob_url = self.blob_storage.upload_file(local_path, blob_name)

            logger.info("Document stored successfully", document_id=document_id, blob_url=blob_url)
            return blob_url

        except Exception as e:
            logger.error("Document storage failed", document_id=document_id, error=str(e))
            raise StorageError(f"Document storage failed: {e}") from e

    def retrieve_document(self, document_id: str, file_extension: str, local_path: str) -> None:
        """
        Retrieve a document from blob storage.

        Args:
            document_id: Unique document identifier.
            file_extension: File extension.
            local_path: Local path to save the document.

        Raises:
            StorageError: If retrieval fails.
        """
        try:
            logger.info("Retrieving document from blob storage", document_id=document_id)

            blob_name = f"{document_id}{file_extension}"
            self.blob_storage.download_file(blob_name, local_path)

            logger.info("Document retrieved successfully", document_id=document_id, local_path=local_path)

        except Exception as e:
            logger.error("Document retrieval failed", document_id=document_id, error=str(e))
            raise StorageError(f"Document retrieval failed: {e}") from e

    def list_documents(self, prefix: Optional[str] = None) -> List[str]:
        """
        List documents in blob storage.

        Args:
            prefix: Optional prefix to filter documents.

        Returns:
            List of blob names.

        Note: This is a simplified implementation. In practice, you'd need
        to implement listing in the BlobStorageService interface.
        """
        # This would require extending the BlobStorageService interface
        # For now, return empty list
        logger.warning("List documents not fully implemented")
        return []