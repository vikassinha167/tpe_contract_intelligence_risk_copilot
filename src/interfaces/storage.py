"""Blob storage abstraction."""
from __future__ import annotations

from abc import ABC, abstractmethod


class IBlobStorage(ABC):
    @abstractmethod
    def download_bytes(self, blob_name: str) -> bytes:
        """Download a blob's binary content."""

    @abstractmethod
    def upload_bytes(self, blob_name: str, data: bytes, content_type: str) -> str:
        """Upload bytes; return blob URL."""

    @abstractmethod
    def list_blobs(self, prefix: str | None = None) -> list[str]:
        """List blob names."""
