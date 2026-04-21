"""
Clause extractor for contract processing.

Extracts structured clauses from contract documents.
"""

from typing import Dict, List, Any

from contract_intelligence.services.base import DocumentIntelligenceService
from contract_intelligence.utils.exceptions import ProcessingError
from contract_intelligence.utils.logging import get_logger

logger = get_logger(__name__)


class ClauseExtractor:
    """
    Extracts structured clauses from contract documents.

    Uses Azure Document Intelligence to identify and extract contract clauses.
    """

    def __init__(self, document_intelligence: DocumentIntelligenceService) -> None:
        """
        Initialize the clause extractor.

        Args:
            document_intelligence: Document intelligence service.
        """
        self.document_intelligence = document_intelligence
        logger.info("Clause extractor initialized")

    def extract_clauses(self, document_path: str) -> Dict[str, Any]:
        """
        Extract clauses from a contract document.

        Args:
            document_path: Path to the contract document.

        Returns:
            Dictionary containing extracted clauses and metadata.

        Raises:
            ProcessingError: If clause extraction fails.
        """
        try:
            logger.info("Extracting clauses from document", document_path=document_path)

            # Analyze document
            analysis_result = self.document_intelligence.analyze_document(document_path)

            # Extract clauses from fields
            clauses = {}
            if "fields" in analysis_result:
                fields = analysis_result["fields"]

                # Common contract clauses
                clause_mappings = {
                    "PartyOne": "party_one",
                    "PartyTwo": "party_two",
                    "EffectiveDate": "effective_date",
                    "ExpirationDate": "expiration_date",
                    "GoverningLaw": "governing_law",
                    "PaymentTerms": "payment_terms",
                    "TerminationClause": "termination_clause",
                    "Confidentiality": "confidentiality",
                    "Liability": "liability",
                    "IntellectualProperty": "intellectual_property",
                }

                for field_key, field_info in fields.items():
                    if field_key in clause_mappings:
                        clause_name = clause_mappings[field_key]
                        clauses[clause_name] = {
                            "content": field_info.get("value"),
                            "confidence": field_info.get("confidence"),
                        }

            # Extract from tables if available
            table_clauses = self._extract_from_tables(analysis_result.get("tables", []))
            clauses.update(table_clauses)

            result = {
                "document_type": analysis_result.get("document_type"),
                "clauses": clauses,
                "confidence_score": self._calculate_overall_confidence(clauses),
            }

            logger.info("Clauses extracted successfully", clause_count=len(clauses))
            return result

        except Exception as e:
            logger.error("Clause extraction failed", document_path=document_path, error=str(e))
            raise ProcessingError(f"Clause extraction failed: {e}") from e

    def _extract_from_tables(self, tables: List[List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
        """
        Extract clauses from document tables.

        Args:
            tables: List of tables from document analysis.

        Returns:
            Dictionary of extracted table clauses.
        """
        clauses = {}

        for table in tables:
            # Look for common clause patterns in tables
            # This is a simplified implementation
            for cell in table:
                content = cell.get("content", "").lower()
                if "termination" in content and "clause" in content:
                    clauses["termination_table"] = {
                        "content": cell.get("content"),
                        "confidence": cell.get("confidence", 0.5),
                    }
                elif "payment" in content and "term" in content:
                    clauses["payment_terms_table"] = {
                        "content": cell.get("content"),
                        "confidence": cell.get("confidence", 0.5),
                    }

        return clauses

    def _calculate_overall_confidence(self, clauses: Dict[str, Dict[str, Any]]) -> float:
        """
        Calculate overall confidence score for extracted clauses.

        Args:
            clauses: Dictionary of extracted clauses.

        Returns:
            Overall confidence score between 0 and 1.
        """
        if not clauses:
            return 0.0

        confidences = [clause.get("confidence", 0.5) for clause in clauses.values()]
        return sum(confidences) / len(confidences)