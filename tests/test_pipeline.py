"""End-to-end pipeline test using only fakes — no Azure required."""
from __future__ import annotations

from src.agents import (
    ClauseAnalysisAgent,
    ComplianceAgent,
    ExtractionAgent,
    GuardedLlmInvoker,
    IndexingAgent,
    IngestionAgent,
    LanguageEnrichmentAgent,
    OrchestratorAgent,
    PersistenceAgent,
    RiskScoringAgent,
    SummarizationAgent,
)
from src.domain import PipelineStage, RiskLevel
from src.services import ContractIntelligencePipeline
from tests.fakes import (
    FakeBlobStorage,
    FakeDocumentProcessor,
    FakeEvaluator,
    FakeGuardrail,
    FakeLanguageAnalyzer,
    FakeRepository,
    FakeSearchIndexer,
    ScriptedLlmClient,
)

SAMPLE_TEXT = b"""MASTER SERVICES AGREEMENT
This agreement is between Acme Corp and Beta Ltd.
Either party may terminate with 30 days notice.
Liability is capped at fees paid in the prior 12 months.
The parties shall keep confidential information confidential.
Governed by the laws of England. Parties shall comply with GDPR.
"""


def _build_pipeline() -> tuple[ContractIntelligencePipeline, FakeRepository, FakeSearchIndexer]:
    storage = FakeBlobStorage({"sample.txt": SAMPLE_TEXT})
    repo = FakeRepository()
    search = FakeSearchIndexer()
    invoker = GuardedLlmInvoker(ScriptedLlmClient(), FakeGuardrail(), FakeEvaluator())

    orchestrator = OrchestratorAgent(
        agents=[
            IngestionAgent(storage),
            ExtractionAgent(FakeDocumentProcessor()),
            LanguageEnrichmentAgent(FakeLanguageAnalyzer()),
            ClauseAnalysisAgent(invoker),
            RiskScoringAgent(invoker),
            ComplianceAgent(),
            SummarizationAgent(invoker),
            IndexingAgent(search),
            PersistenceAgent(repo),
        ]
    )
    return ContractIntelligencePipeline(orchestrator), repo, search


def test_full_pipeline_runs_end_to_end():
    pipeline, repo, search = _build_pipeline()
    result = pipeline.process("sample.txt", title="Acme MSA")

    assert result.stage == PipelineStage.PERSISTED
    assert result.error is None
    assert result.page_count == 1
    assert len(result.clauses) == 5
    assert all(c.risk_level is not None for c in result.clauses)
    assert result.overall_risk_level in {
        RiskLevel.LOW,
        RiskLevel.MEDIUM,
        RiskLevel.HIGH,
        RiskLevel.CRITICAL,
    }
    assert result.executive_summary and "Bullet" in result.executive_summary
    assert result.evaluation and result.evaluation.relevance and result.evaluation.relevance > 0
    # Persistence + indexing happened
    assert repo.get(result.contract_id) is not None
    assert result.contract_id in search.docs
    # All compliance rules pass for the seeded text
    assert all(f.passed for f in result.compliance_findings)


def test_pipeline_fails_gracefully_when_blob_missing():
    pipeline, _, _ = _build_pipeline()
    result = pipeline.process("does-not-exist.pdf")
    assert result.stage == PipelineStage.FAILED
    assert result.error and "IngestionAgent" in result.error
