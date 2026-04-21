"""Azure OpenAI adapter implementing `ILlmClient`.

We authenticate with Entra ID via `DefaultAzureCredential` — no API keys in code.
"""
from __future__ import annotations

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
from openai import OpenAIError

from src.interfaces import ChatMessage, ILlmClient
from src.utils import LlmInvocationError, with_retry

_SCOPE = "https://cognitiveservices.azure.com/.default"


class AzureOpenAILlmClient(ILlmClient):
    def __init__(self, endpoint: str, deployment: str, api_version: str) -> None:
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), _SCOPE
        )
        self._client = AzureOpenAI(
            azure_endpoint=endpoint,
            azure_ad_token_provider=token_provider,
            api_version=api_version,
        )
        self._deployment = deployment

    @with_retry(OpenAIError)
    def complete(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.0,
        json_mode: bool = False,
        max_tokens: int | None = None,
    ) -> str:
        kwargs: dict = {
            "model": self._deployment,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
        }
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            resp = self._client.chat.completions.create(**kwargs)
        except OpenAIError as exc:
            raise LlmInvocationError(str(exc)) from exc

        return (resp.choices[0].message.content or "").strip()
