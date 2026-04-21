"""Azure Blob Storage adapter implementing `IBlobStorage`."""
from __future__ import annotations

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContentSettings

from src.interfaces import IBlobStorage
from src.utils import with_retry


class AzureBlobStorage(IBlobStorage):
    def __init__(self, account_url: str, container: str) -> None:
        self._service = BlobServiceClient(
            account_url=account_url, credential=DefaultAzureCredential()
        )
        self._container = self._service.get_container_client(container)
        if not self._container.exists():
            self._container.create_container()

    @with_retry()
    def download_bytes(self, blob_name: str) -> bytes:
        return self._container.get_blob_client(blob_name).download_blob().readall()

    @with_retry()
    def upload_bytes(self, blob_name: str, data: bytes, content_type: str) -> str:
        client = self._container.get_blob_client(blob_name)
        client.upload_blob(
            data,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
        )
        return client.url

    @with_retry()
    def list_blobs(self, prefix: str | None = None) -> list[str]:
        return [b.name for b in self._container.list_blobs(name_starts_with=prefix)]
