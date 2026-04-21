"""
Azure Blob Storage service implementation.

Provides file upload and download capabilities.
"""

from typing import Any, Dict

from azure.storage.blob import BlobServiceClient

from contract_intelligence.config.settings import settings
from contract_intelligence.services.base import BlobStorageService
from contract_intelligence.utils.exceptions import AzureServiceError
from contract_intelligence.utils.logging import get_logger

logger = get_logger(__name__)


class AzureBlobStorageService(BlobStorageService):
    """Azure Blob Storage service implementation."""

    def __init__(self) -> None:
        """Initialize the Blob Service client."""
        try:
            account_url = f"https://{settings.storage.account}.blob.core.windows.net"
            self.blob_service_client = BlobServiceClient(
                account_url=account_url,
                credential=settings.storage.key.get_secret_value(),
            )

            # Ensure container exists
            self._create_container_if_not_exists()

            logger.info("Azure Blob Storage service initialized", container=settings.storage.container)
        except Exception as e:
            logger.error("Failed to initialize Blob Storage service", error=str(e))
            raise AzureServiceError(f"Failed to initialize Blob Storage service: {e}") from e

    def _create_container_if_not_exists(self) -> None:
        """Create the container if it doesn't exist."""
        try:
            container_client = self.blob_service_client.get_container_client(settings.storage.container)
            container_client.create_container()
            logger.info("Blob container created", container=settings.storage.container)
        except Exception as e:
            if "ContainerAlreadyExists" in str(e):
                logger.info("Blob container already exists", container=settings.storage.container)
            else:
                logger.error("Failed to create blob container", error=str(e))
                raise AzureServiceError(f"Failed to create blob container: {e}") from e

    def upload_file(self, file_path: str, blob_name: str) -> str:
        """
        Upload a file to blob storage.

        Args:
            file_path: Local path to the file.
            blob_name: Name for the blob.

        Returns:
            URL of the uploaded blob.

        Raises:
            AzureServiceError: If upload fails.
        """
        try:
            logger.info("Uploading file to blob storage", file_path=file_path, blob_name=blob_name)

            blob_client = self.blob_service_client.get_blob_client(
                container=settings.storage.container,
                blob=blob_name,
            )

            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)

            blob_url = blob_client.url
            logger.info("File uploaded successfully", blob_url=blob_url)
            return blob_url

        except Exception as e:
            logger.error("File upload failed", file_path=file_path, blob_name=blob_name, error=str(e))
            raise AzureServiceError(f"File upload failed: {e}") from e

    def download_file(self, blob_name: str, local_path: str) -> None:
        """
        Download a file from blob storage.

        Args:
            blob_name: Name of the blob.
            local_path: Local path to save the file.

        Raises:
            AzureServiceError: If download fails.
        """
        try:
            logger.info("Downloading file from blob storage", blob_name=blob_name, local_path=local_path)

            blob_client = self.blob_service_client.get_blob_client(
                container=settings.storage.container,
                blob=blob_name,
            )

            with open(local_path, "wb") as download_file:
                download_stream = blob_client.download_blob()
                download_file.write(download_stream.readall())

            logger.info("File downloaded successfully", blob_name=blob_name, local_path=local_path)

        except Exception as e:
            logger.error("File download failed", blob_name=blob_name, local_path=local_path, error=str(e))
            raise AzureServiceError(f"File download failed: {e}") from e