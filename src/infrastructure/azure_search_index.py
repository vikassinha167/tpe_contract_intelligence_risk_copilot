"""Azure AI Search adapter implementing `ISearchIndexer`."""
from __future__ import annotations

from typing import Any

from azure.core.exceptions import HttpResponseError, ResourceExistsError
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
)

from src.interfaces import ISearchIndexer
from src.utils import IndexingError, with_retry


class AzureSearchIndexer(ISearchIndexer):
    def __init__(self, endpoint: str, index_name: str) -> None:
        cred = DefaultAzureCredential()
        self._index_name = index_name
        self._index_client = SearchIndexClient(endpoint=endpoint, credential=cred)
        self._search_client = SearchClient(
            endpoint=endpoint, index_name=index_name, credential=cred
        )

    def ensure_index(self) -> None:
        fields = [
            SimpleField(
                name="id",
                type=SearchFieldDataType.String,
                key=True,
                filterable=True,
            ),
            SearchableField(name="title", type=SearchFieldDataType.String),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SearchField(
                name="entities",
                type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                filterable=True,
                facetable=True,
            ),
            SimpleField(
                name="risk_level",
                type=SearchFieldDataType.String,
                filterable=True,
                facetable=True,
            ),
            SimpleField(
                name="risk_score",
                type=SearchFieldDataType.Double,
                filterable=True,
                sortable=True,
            ),
        ]
        try:
            self._index_client.create_index(
                SearchIndex(name=self._index_name, fields=fields)
            )
        except ResourceExistsError:
            return  # Idempotent
        except HttpResponseError as exc:
            raise IndexingError(str(exc)) from exc

    @with_retry(HttpResponseError)
    def upsert_document(self, document: dict[str, Any]) -> None:
        try:
            self._search_client.merge_or_upload_documents(documents=[document])
        except HttpResponseError as exc:
            raise IndexingError(str(exc)) from exc

    @with_retry(HttpResponseError)
    def search(self, query: str, top: int = 5) -> list[dict[str, Any]]:
        results = self._search_client.search(search_text=query, top=top)
        return [dict(r) for r in results]
