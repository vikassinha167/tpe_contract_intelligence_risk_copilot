"""
Azure Document Intelligence service implementation.

Extracts structured data from documents using Azure Document Intelligence.
"""

from typing import Any, Dict

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

from contract_intelligence.config.settings import settings
from contract_intelligence.services.base import DocumentIntelligenceService
from contract_intelligence.utils.exceptions import AzureServiceError
from contract_intelligence.utils.logging import get_logger

logger = get_logger(__name__)


class AzureDocumentIntelligenceService(DocumentIntelligenceService):
    """Azure Document Intelligence service implementation."""

    def __init__(self) -> None:
        """Initialize the Document Intelligence client."""
        try:
            self.client = DocumentIntelligenceClient(
                endpoint=settings.document_intelligence.endpoint,
                credential=AzureKeyCredential(settings.document_intelligence.key.get_secret_value()),
            )
            logger.info("Azure Document Intelligence client initialized")
        except Exception as e:
            logger.error("Failed to initialize Document Intelligence client", error=str(e))
            raise AzureServiceError(f"Failed to initialize Document Intelligence client: {e}") from e

    def analyze_document(self, document_path: str) -> Dict[str, Any]:
        """
        Analyze a document and extract structured data.

        Args:
            document_path: Path to the document file.

        Returns:
            Dictionary containing extracted data including clauses, entities, etc.

        Raises:
            AzureServiceError: If document analysis fails.
        """
        try:
            logger.info("Analyzing document", document_path=document_path)

            with open(document_path, "rb") as f:
                document_content = f.read()

            # Analyze document with prebuilt contract model
            poller = self.client.begin_analyze_document(
                model_id="prebuilt-contract",
                analyze_request=document_content,
                content_type="application/octet-stream",
            )

            result = poller.result()

            # Extract structured data
            extracted_data = {
                "document_type": result.documents[0].doc_type if result.documents else None,
                "fields": {},
                "tables": [],
                "key_value_pairs": [],
            }

            if result.documents:
                doc = result.documents[0]
                extracted_data["fields"] = {
                    field_name: {
                        "value": field.value,
                        "confidence": field.confidence,
                    }
                    for field_name, field in doc.fields.items()
                }

            # Extract tables
            for table in result.tables:
                table_data = []
                for cell in table.cells:
                    table_data.append({
                        "row_index": cell.row_index,
                        "column_index": cell.column_index,
                        "content": cell.content,
                        "confidence": cell.confidence,
                    })
                extracted_data["tables"].append(table_data)

            # Extract key-value pairs
            for kvp in result.key_value_pairs:
                extracted_data["key_value_pairs"].append({
                    "key": kvp.key.content if kvp.key else None,
                    "value": kvp.value.content if kvp.value else None,
                    "confidence": kvp.confidence,
                })

            logger.info("Document analysis completed", document_path=document_path)
            return extracted_data

        except Exception as e:
            logger.error("Document analysis failed", document_path=document_path, error=str(e))
            raise AzureServiceError(f"Document analysis failed: {e}") from e