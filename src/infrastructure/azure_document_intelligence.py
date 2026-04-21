"""Azure Document Intelligence adapter implementing `IDocumentProcessor`."""
from __future__ import annotations

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential

from src.interfaces import ExtractedDocument, IDocumentProcessor
from src.utils import DocumentProcessingError, with_retry


class AzureDocumentIntelligenceProcessor(IDocumentProcessor):
    """Uses the prebuilt **layout** model — best general-purpose OCR + structure."""

    MODEL_ID = "prebuilt-layout"

    def __init__(self, endpoint: str) -> None:
        self._client = DocumentIntelligenceClient(
            endpoint=endpoint, credential=DefaultAzureCredential()
        )

    @with_retry(HttpResponseError)
    def extract(self, content: bytes) -> ExtractedDocument:
        try:
            poller = self._client.begin_analyze_document(
                model_id=self.MODEL_ID,
                body=AnalyzeDocumentRequest(bytes_source=content),
            )
            result = poller.result()
        except HttpResponseError as exc:
            raise DocumentProcessingError(str(exc)) from exc

        text = "\n".join(p.content for p in (result.paragraphs or []))
        page_count = len(result.pages or [])
        return ExtractedDocument(
            text=text, page_count=page_count, raw=result.as_dict()
        )
