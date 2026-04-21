"""Azure Language Service adapter implementing `ILanguageAnalyzer`."""
from __future__ import annotations

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential

from src.domain import Entity
from src.interfaces import ILanguageAnalyzer, LanguageAnalysisResult
from src.utils import LanguageAnalysisError, with_retry

# Azure caps requests at 5,120 chars per document — chunk safely.
_CHUNK = 5000


def _chunks(text: str, size: int = _CHUNK) -> list[str]:
    return [text[i : i + size] for i in range(0, len(text), size)] or [""]


class AzureLanguageAnalyzer(ILanguageAnalyzer):
    def __init__(self, endpoint: str) -> None:
        self._client = TextAnalyticsClient(
            endpoint=endpoint, credential=DefaultAzureCredential()
        )

    @with_retry(HttpResponseError)
    def analyze(self, text: str) -> LanguageAnalysisResult:
        try:
            docs = _chunks(text)
            ner = self._client.recognize_entities(documents=docs)
            kp = self._client.extract_key_phrases(documents=docs)
            pii = self._client.recognize_pii_entities(documents=docs)
        except HttpResponseError as exc:
            raise LanguageAnalysisError(str(exc)) from exc

        entities: list[Entity] = []
        for d in ner:
            if d.is_error:  # type: ignore[union-attr]
                continue
            for e in d.entities:  # type: ignore[union-attr]
                entities.append(
                    Entity(
                        text=e.text,
                        category=str(e.category),
                        subcategory=str(e.subcategory) if e.subcategory else None,
                        confidence=float(e.confidence_score),
                    )
                )

        key_phrases: list[str] = []
        for d in kp:
            if not d.is_error:  # type: ignore[union-attr]
                key_phrases.extend(d.key_phrases)  # type: ignore[union-attr]

        pii_entities: list[Entity] = []
        for d in pii:
            if d.is_error:  # type: ignore[union-attr]
                continue
            for e in d.entities:  # type: ignore[union-attr]
                pii_entities.append(
                    Entity(
                        text=e.text,
                        category=str(e.category),
                        confidence=float(e.confidence_score),
                    )
                )

        return LanguageAnalysisResult(
            entities=entities,
            key_phrases=sorted(set(key_phrases)),
            pii_entities=pii_entities,
        )
