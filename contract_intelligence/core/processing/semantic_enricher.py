"""
Semantic enricher for contract processing.

Enriches contract clauses with semantic understanding using language services.
"""

from typing import Dict, Any, List

from contract_intelligence.services.base import LanguageService
from contract_intelligence.utils.exceptions import ProcessingError
from contract_intelligence.utils.logging import get_logger

logger = get_logger(__name__)


class SemanticEnricher:
    """
    Enriches contract clauses with semantic understanding.

    Uses Azure Language services to analyze text for entities, sentiment, and key phrases.
    """

    def __init__(self, language_service: LanguageService) -> None:
        """
        Initialize the semantic enricher.

        Args:
            language_service: Language service for text analysis.
        """
        self.language_service = language_service
        logger.info("Semantic enricher initialized")

    def enrich_clauses(self, clauses: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Enrich contract clauses with semantic information.

        Args:
            clauses: Dictionary of extracted clauses.

        Returns:
            Dictionary containing enriched clauses with semantic analysis.

        Raises:
            ProcessingError: If enrichment fails.
        """
        try:
            logger.info("Enriching clauses with semantic analysis", clause_count=len(clauses))

            enriched_clauses = {}

            for clause_name, clause_data in clauses.items():
                content = clause_data.get("content", "")
                if not content:
                    enriched_clauses[clause_name] = clause_data
                    continue

                # Analyze text
                analysis = self.language_service.analyze_text(content)

                # Enrich clause data
                enriched_clause = clause_data.copy()
                enriched_clause.update({
                    "entities": analysis.get("entities", []),
                    "sentiment": analysis.get("sentiment"),
                    "key_phrases": analysis.get("key_phrases", []),
                    "semantic_score": self._calculate_semantic_score(analysis),
                })

                enriched_clauses[clause_name] = enriched_clause

            result = {
                "enriched_clauses": enriched_clauses,
                "overall_sentiment": self._calculate_overall_sentiment(enriched_clauses),
                "risk_indicators": self._identify_risk_indicators(enriched_clauses),
            }

            logger.info("Clauses enriched successfully")
            return result

        except Exception as e:
            logger.error("Clause enrichment failed", error=str(e))
            raise ProcessingError(f"Clause enrichment failed: {e}") from e

    def _calculate_semantic_score(self, analysis: Dict[str, Any]) -> float:
        """
        Calculate semantic score based on analysis results.

        Args:
            analysis: Text analysis results.

        Returns:
            Semantic score between 0 and 1.
        """
        score = 0.0

        # Entity recognition quality
        entities = analysis.get("entities", [])
        if entities:
            avg_confidence = sum(e.get("confidence_score", 0) for e in entities) / len(entities)
            score += avg_confidence * 0.4

        # Sentiment analysis
        sentiment = analysis.get("sentiment")
        if sentiment:
            # Higher score for neutral sentiment (less risky)
            sentiment_scores = sentiment.get("confidence_scores", {})
            neutral_score = sentiment_scores.get("neutral", 0)
            score += neutral_score * 0.3

        # Key phrases
        key_phrases = analysis.get("key_phrases", [])
        if key_phrases:
            score += min(len(key_phrases) / 10, 1.0) * 0.3

        return min(score, 1.0)

    def _calculate_overall_sentiment(self, enriched_clauses: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall sentiment across all clauses.

        Args:
            enriched_clauses: Dictionary of enriched clauses.

        Returns:
            Overall sentiment analysis.
        """
        sentiments = []
        for clause in enriched_clauses.values():
            sentiment = clause.get("sentiment")
            if sentiment:
                sentiments.append(sentiment)

        if not sentiments:
            return {"overall": "unknown", "confidence": 0.0}

        # Simple aggregation - could be more sophisticated
        overall_sentiments = [s.get("overall", "neutral") for s in sentiments]
        neutral_count = overall_sentiments.count("neutral")
        positive_count = overall_sentiments.count("positive")
        negative_count = overall_sentiments.count("negative")

        if neutral_count >= positive_count and neutral_count >= negative_count:
            overall = "neutral"
        elif positive_count > negative_count:
            overall = "positive"
        else:
            overall = "negative"

        confidence = max(neutral_count, positive_count, negative_count) / len(sentiments)

        return {
            "overall": overall,
            "confidence": confidence,
            "distribution": {
                "neutral": neutral_count,
                "positive": positive_count,
                "negative": negative_count,
            }
        }

    def _identify_risk_indicators(self, enriched_clauses: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify potential risk indicators in clauses.

        Args:
            enriched_clauses: Dictionary of enriched clauses.

        Returns:
            List of identified risk indicators.
        """
        risk_indicators = []

        # Define risk keywords and patterns
        risk_keywords = {
            "high": ["penalty", "liquidated damages", "termination", "breach", "liability"],
            "medium": ["confidentiality", "non-compete", "indemnification", "warranty"],
            "low": ["payment terms", "governing law", "force majeure"],
        }

        for clause_name, clause_data in enriched_clauses.items():
            content = clause_data.get("content", "").lower()
            entities = clause_data.get("entities", [])
            key_phrases = clause_data.get("key_phrases", [])

            # Check for risk keywords
            for risk_level, keywords in risk_keywords.items():
                for keyword in keywords:
                    if keyword in content:
                        risk_indicators.append({
                            "clause": clause_name,
                            "risk_level": risk_level,
                            "indicator": keyword,
                            "type": "keyword_match",
                        })

            # Check entities for risk
            for entity in entities:
                entity_text = entity.get("text", "").lower()
                if any(keyword in entity_text for keywords in risk_keywords.values() for keyword in keywords):
                    risk_indicators.append({
                        "clause": clause_name,
                        "risk_level": "medium",
                        "indicator": entity.get("text"),
                        "type": "entity_match",
                    })

        return risk_indicators