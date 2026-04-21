"""
Azure Language service implementation.

Provides text analysis capabilities including entity recognition, sentiment analysis, and key phrase extraction.
"""

from typing import Any, Dict, List

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

from contract_intelligence.config.settings import settings
from contract_intelligence.services.base import LanguageService
from contract_intelligence.utils.exceptions import AzureServiceError
from contract_intelligence.utils.logging import get_logger

logger = get_logger(__name__)


class AzureLanguageService(LanguageService):
    """Azure Language service implementation."""

    def __init__(self) -> None:
        """Initialize the Text Analytics client."""
        try:
            self.client = TextAnalyticsClient(
                endpoint=settings.language.endpoint,
                credential=AzureKeyCredential(settings.language.key.get_secret_value()),
            )
            logger.info("Azure Language service client initialized")
        except Exception as e:
            logger.error("Failed to initialize Language service client", error=str(e))
            raise AzureServiceError(f"Failed to initialize Language service client: {e}") from e

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for entities, sentiment, and key phrases.

        Args:
            text: The text to analyze.

        Returns:
            Dictionary containing analysis results.

        Raises:
            AzureServiceError: If text analysis fails.
        """
        try:
            logger.info("Analyzing text", text_length=len(text))

            # Prepare documents for analysis
            documents = [text]

            # Perform entity recognition
            entity_results = self.client.recognize_entities(documents)
            entities = []
            if not entity_results[0].is_error:
                entities = [
                    {
                        "text": entity.text,
                        "category": entity.category,
                        "subcategory": entity.subcategory,
                        "confidence_score": entity.confidence_score,
                    }
                    for entity in entity_results[0].entities
                ]

            # Perform sentiment analysis
            sentiment_results = self.client.analyze_sentiment(documents)
            sentiment = None
            if not sentiment_results[0].is_error:
                sentiment = {
                    "overall": sentiment_results[0].sentiment,
                    "confidence_scores": {
                        "positive": sentiment_results[0].confidence_scores.positive,
                        "neutral": sentiment_results[0].confidence_scores.neutral,
                        "negative": sentiment_results[0].confidence_scores.negative,
                    },
                }

            # Extract key phrases
            key_phrase_results = self.client.extract_key_phrases(documents)
            key_phrases = []
            if not key_phrase_results[0].is_error:
                key_phrases = key_phrase_results[0].key_phrases

            analysis_result = {
                "entities": entities,
                "sentiment": sentiment,
                "key_phrases": key_phrases,
            }

            logger.info("Text analysis completed", entities_count=len(entities), key_phrases_count=len(key_phrases))
            return analysis_result

        except Exception as e:
            logger.error("Text analysis failed", error=str(e))
            raise AzureServiceError(f"Text analysis failed: {e}") from e