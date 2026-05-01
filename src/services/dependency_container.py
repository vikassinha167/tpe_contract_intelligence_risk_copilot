"""Dependency Injection container — the **only** place that knows about Azure
concretes. Everything else depends on interfaces.

This realises the **Dependency Inversion Principle**: high-level policy (agents,
pipeline) is wired with low-level details here at the composition root.
"""
from __future__ import annotations

from functools import cached_property

from config import AzureSettings, get_settings
from src.agents import (
    ClauseAnalysisAgent,
    ComplianceAgent,
    ExtractionAgent,
    GuardedLlmInvoker,
    IngestionAgent,
    LanguageEnrichmentAgent,
    OrchestratorAgent,
    RiskScoringAgent,
    SummarizationAgent,
)
from src.infrastructure import (
    AzureBlobStorage,
    AzureContentSafetyGuardrail,
    AzureDocumentIntelligenceProcessor,
    AzureFoundryEvaluator,
    AzureKeyVaultSecretProvider,
    AzureLanguageAnalyzer,
    AzureOpenAILlmClient,
)
from src.interfaces import (
    IBlobStorage,
    IDocumentProcessor,
    IGuardrail,
    ILanguageAnalyzer,
    ILlmClient,
    IResponseEvaluator,
    ISecretProvider,
)


class DependencyContainer:
    """Lazy singleton container — instantiates each adapter only once on demand."""

    def __init__(self, settings: AzureSettings | None = None) -> None:
        self._settings = settings or get_settings()

    # -------- Infrastructure singletons (cached_property) ---------------
    @cached_property
    def blob_storage(self) -> IBlobStorage:
        return AzureBlobStorage(
            self._settings.storage_account_url, self._settings.blob_container
        )

    @cached_property
    def document_processor(self) -> IDocumentProcessor:
        return AzureDocumentIntelligenceProcessor(self._settings.docintel_endpoint)

    @cached_property
    def language_analyzer(self) -> ILanguageAnalyzer:
        return AzureLanguageAnalyzer(self._settings.language_endpoint)

    @cached_property
    def llm_client(self) -> ILlmClient:
        return AzureOpenAILlmClient(
            endpoint=self._settings.openai_endpoint,
            deployment=self._settings.openai_deployment,
            api_version=self._settings.openai_api_version,
        )

    @cached_property
    def guardrail(self) -> IGuardrail:
        return AzureContentSafetyGuardrail(self._settings.content_safety_endpoint)

    @cached_property
    def evaluator(self) -> IResponseEvaluator:
        return AzureFoundryEvaluator(
            endpoint=self._settings.openai_endpoint,
            deployment=self._settings.openai_deployment,
            api_version=self._settings.openai_api_version,
        )

    @cached_property
    def guarded_invoker(self) -> GuardedLlmInvoker:
        return GuardedLlmInvoker(self.llm_client, self.guardrail, self.evaluator)

    # -------- Orchestration ---------------------------------------------
    def build_orchestrator(self) -> OrchestratorAgent:
        return OrchestratorAgent(
            agents=[
                IngestionAgent(self.blob_storage),
                ExtractionAgent(self.document_processor),
                LanguageEnrichmentAgent(self.language_analyzer),
                ClauseAnalysisAgent(self.guarded_invoker),
                RiskScoringAgent(self.guarded_invoker),
                ComplianceAgent(),
                SummarizationAgent(self.guarded_invoker),
            ]
        )
