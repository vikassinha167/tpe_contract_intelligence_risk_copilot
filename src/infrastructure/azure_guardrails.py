"""Azure AI Content Safety adapter implementing `IGuardrail`.

This is the "Guardrails" layer — every LLM call is sandwiched between a
`check_input` and `check_output` to enforce responsible AI policies.
"""
from __future__ import annotations

from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential

from src.interfaces import GuardrailVerdict, IGuardrail
from src.utils import GuardrailViolationError, with_retry

_BLOCK_THRESHOLD = 4  # Azure severities: 0,2,4,6 — block if >= 4


class AzureContentSafetyGuardrail(IGuardrail):
    def __init__(self, endpoint: str) -> None:
        self._client = ContentSafetyClient(
            endpoint=endpoint, credential=DefaultAzureCredential()
        )

    @with_retry(HttpResponseError)
    def check_input(self, text: str) -> GuardrailVerdict:
        return self._analyse(text)

    @with_retry(HttpResponseError)
    def check_output(self, text: str) -> GuardrailVerdict:
        return self._analyse(text)

    # ----------------------- internal -----------------------
    def _analyse(self, text: str) -> GuardrailVerdict:
        if not text.strip():
            return GuardrailVerdict(allowed=True)
        try:
            resp = self._client.analyze_text(AnalyzeTextOptions(text=text))
        except HttpResponseError as exc:
            raise GuardrailViolationError(str(exc)) from exc

        cats: dict[str, int] = {}
        worst = 0
        for c in resp.categories_analysis:
            sev = int(c.severity or 0)
            cats[str(c.category)] = sev
            worst = max(worst, sev)

        allowed = worst < _BLOCK_THRESHOLD
        reason = None if allowed else f"Blocked: max severity {worst}"
        return GuardrailVerdict(allowed=allowed, reason=reason, categories=cats)
