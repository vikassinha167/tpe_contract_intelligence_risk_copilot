"""
Document ingestor for contract intelligence.

Handles ingestion of contract documents from various sources.
"""

import os
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from contract_intelligence.services.base import BlobStorageService
from contract_intelligence.utils.exceptions import IngestionError
from contract_intelligence.utils.logging import get_logger

logger = get_logger(__name__)


class DocumentIngestor:
    """
    Handles document ingestion from various sources.

    Follows Single Responsibility Principle by focusing only on ingestion.
    """

    def __init__(self, blob_storage: BlobStorageService) -> None:
        """
        Initialize the document ingestor.

        Args:
            blob_storage: Blob storage service for uploading documents.
        """
        self.blob_storage = blob_storage
        logger.info("Document ingestor initialized")

    def ingest_file(self, file_path: str) -> Dict[str, str]:
        """
        Ingest a single document file.

        Args:
            file_path: Path to the document file.

        Returns:
            Dictionary containing document metadata.

        Raises:
            IngestionError: If ingestion fails.
        """
        try:
            logger.info("Ingesting document file", file_path=file_path)

            # Validate file exists
            if not os.path.exists(file_path):
                raise IngestionError(f"File does not exist: {file_path}")

            # Validate file type
            allowed_extensions = {'.pdf', '.docx', '.txt', '.jpg', '.jpeg', '.png'}
            file_extension = Path(file_path).suffix.lower()
            if file_extension not in allowed_extensions:
                raise IngestionError(f"Unsupported file type: {file_extension}")

            # Generate unique document ID
            document_id = str(uuid.uuid4())

            # Upload to blob storage
            blob_name = f"{document_id}{file_extension}"
            blob_url = self.blob_storage.upload_file(file_path, blob_name)

            # Create metadata
            metadata = {
                "document_id": document_id,
                "original_filename": os.path.basename(file_path),
                "file_extension": file_extension,
                "blob_url": blob_url,
                "blob_name": blob_name,
            }

            logger.info("Document ingested successfully", document_id=document_id, blob_url=blob_url)
            return metadata

        except Exception as e:
            logger.error("Document ingestion failed", file_path=file_path, error=str(e))
            raise IngestionError(f"Document ingestion failed: {e}") from e

    def ingest_batch(self, file_paths: List[str]) -> List[Dict[str, str]]:
        """
        Ingest multiple document files.

        Args:
            file_paths: List of paths to document files.

        Returns:
            List of document metadata dictionaries.

        Raises:
            IngestionError: If any ingestion fails.
        """
        logger.info("Ingesting batch of documents", count=len(file_paths))

        results = []
        errors = []

        for file_path in file_paths:
            try:
                metadata = self.ingest_file(file_path)
                results.append(metadata)
            except IngestionError as e:
                errors.append(f"{file_path}: {str(e)}")
                logger.warning("Failed to ingest document", file_path=file_path, error=str(e))

        if errors:
            error_message = f"Batch ingestion completed with errors: {errors}"
            logger.warning(error_message)
            if len(errors) == len(file_paths):
                raise IngestionError("All documents failed to ingest")

        logger.info("Batch ingestion completed", success_count=len(results), error_count=len(errors))
        return results

    def validate_document(self, file_path: str) -> bool:
        """
        Validate if a document can be ingested.

        Args:
            file_path: Path to the document file.

        Returns:
            True if valid, False otherwise.
        """
        try:
            # Check file exists
            if not os.path.exists(file_path):
                return False

            # Check file size (max 50MB)
            max_size = 50 * 1024 * 1024  # 50MB
            if os.path.getsize(file_path) > max_size:
                return False

            # Check file extension
            allowed_extensions = {'.pdf', '.docx', '.txt', '.jpg', '.jpeg', '.png'}
            file_extension = Path(file_path).suffix.lower()
            if file_extension not in allowed_extensions:
                return False

            return True

        except Exception:
            return False