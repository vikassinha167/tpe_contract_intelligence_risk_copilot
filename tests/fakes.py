"""In-memory fake adapters that satisfy the same interfaces as Azure ones.

These let the entire pipeline run **without any Azure dependency** — the
ultimate test of the Liskov & Dependency-Inversion principles.
"""
from __future__ import annotations

import json
from typing import Any

from src.domain import Contract, Entity, EvaluationScores
from src.interfaces import (
    ChatMessage,
    ExtractedDocument,
    GuardrailVerdict,
    IBlobStorage,
    IContractRepository,
    IDocumentProcessor,
    IGuardrail,
    ILanguageAnalyzer,
    ILlmClient,
    IResponseEvaluator,
    ISearchIndexer,
    LanguageAnalysisResult,
)


class FakeBlobStorage(IBlobStorage):
    def __init__(self, blobs: dict[str, bytes]) -> None:
        self._blobs = blobs

    def download_bytes(self, blob_name: str) -> bytes:
        return self._blobs[blob_name]

    def upload_bytes(self, blob_name: str, data: bytes, content_type: str) -> str:
        self._blobs[blob_name] = data
        return f"fake://{blob_name}"

    def list_blobs(self, prefix: str | None = None) -> list[str]:
        return [n for n in self._blobs if not prefix or n.startswith(prefix)]


class FakeDocumentProcessor(IDocumentProcessor):
    def extract(self, content: bytes) -> ExtractedDocument:
        return ExtractedDocument(text=content.decode("utf-8"), page_count=1)


class FakeLanguageAnalyzer(ILanguageAnalyzer):
    def analyze(self, text: str) -> LanguageAnalysisResult:
        return LanguageAnalysisResult(
            entities=[Entity(text="Acme Corp", category="Organization", confidence=0.99)],
            key_phrases=["payment", "termination"],
            pii_entities=[],
        )


class FakeSearchIndexer(ISearchIndexer):
    def __init__(self) -> None:
        self.docs: dict[str, dict[str, Any]] = {}

    def ensure_index(self) -> None:
        return

    def upsert_document(self, document: dict[str, Any]) -> None:
        self.docs[document["id"]] = document

    def search(self, query: str, top: int = 5) -> list[dict[str, Any]]:
        return list(self.docs.values())[:top]


class FakeGuardrail(IGuardrail):
    def check_input(self, text: str) -> GuardrailVerdict:
        return GuardrailVerdict(allowed=True)

    def check_output(self, text: str) -> GuardrailVerdict:
        return GuardrailVerdict(allowed=True)


class FakeEvaluator(IResponseEvaluator):
    def evaluate(self, *, query: str, response: str, context: str | None = None) -> EvaluationScores:
        return EvaluationScores(
            groundedness=4.5, relevance=4.7, coherence=4.8, fluency=4.9
        )


class FakeRepository(IContractRepository):
    def __init__(self) -> None:
        self.store: dict[str, Contract] = {}

    def save(self, contract: Contract) -> None:
        self.store[contract.contract_id] = contract

    def get(self, contract_id: str) -> Contract | None:
        return self.store.get(contract_id)


class ScriptedLlmClient(ILlmClient):
    """Returns canned responses based on the system prompt content."""

    def complete(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.0,
        json_mode: bool = False,
        max_tokens: int | None = None,
    ) -> str:
        system = next((m.content for m in messages if m.role == "system"), "")
        if "Identify the most important clauses" in system:
            return json.dumps(
                {
                    "clauses": [
                        {"clause_type": "Termination", "text": "Either party may terminate with 30 days notice."},
                        {"clause_type": "Liability", "text": "Liability is capped at fees paid in 12 months."},
                        {"clause_type": "Confidentiality", "text": "Both parties shall keep info confidential."},
                        {"clause_type": "Governing Law", "text": "Governed by the laws of England."},
                        {"clause_type": "Data Protection / GDPR", "text": "Parties shall comply with GDPR."},
                    ]
                }
            )
        if "score the supplied clause" in system.lower():
            return json.dumps(
                {
                    "risk_level": "Medium",
                    "risk_score": 0.45,
                    "rationale": "Standard clause but with limited carve-outs.",
                    "recommendation": "Add mutual termination-for-convenience symmetry.",
                }
            )
        # Summarization
        return "- Bullet 1\n- Bullet 2\n- Bullet 3\n- Bullet 4\n- Bullet 5"
