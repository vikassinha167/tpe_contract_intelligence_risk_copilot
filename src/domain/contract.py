"""Core domain entities for a Contract.

Pure Pydantic models — no SDK imports. This keeps the domain testable and
portable (Liskov-friendly: swap any infrastructure without touching domain).
"""
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from .enums import ClauseType, PipelineStage, RiskLevel


class Entity(BaseModel):
    """Named entity recognised in the contract (org, person, money, date…)."""

    text: str
    category: str
    subcategory: str | None = None
    confidence: float = 0.0


class Clause(BaseModel):
    """A single contract clause + its analysis output."""

    clause_id: str = Field(default_factory=lambda: str(uuid4()))
    clause_type: ClauseType
    text: str
    page_number: int | None = None
    risk_level: RiskLevel | None = None
    risk_score: float | None = None  # 0.0 - 1.0
    rationale: str | None = None
    recommendation: str | None = None


class ComplianceFinding(BaseModel):
    rule_id: str
    rule_description: str
    passed: bool
    evidence: str | None = None


class EvaluationScores(BaseModel):
    """Output of Azure AI Foundry Evaluators for an LLM response."""

    groundedness: float | None = None
    relevance: float | None = None
    coherence: float | None = None
    fluency: float | None = None


class Contract(BaseModel):
    """Aggregate root — represents one contract moving through the pipeline."""

    contract_id: str = Field(default_factory=lambda: str(uuid4()))
    source_blob: str
    title: str | None = None

    raw_text: str | None = None
    page_count: int | None = None

    entities: list[Entity] = Field(default_factory=list)
    key_phrases: list[str] = Field(default_factory=list)
    pii_detected: list[Entity] = Field(default_factory=list)

    clauses: list[Clause] = Field(default_factory=list)
    compliance_findings: list[ComplianceFinding] = Field(default_factory=list)

    overall_risk_level: RiskLevel | None = None
    overall_risk_score: float | None = None
    executive_summary: str | None = None

    evaluation: EvaluationScores | None = None

    stage: PipelineStage = PipelineStage.INGESTED
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def advance(self, stage: PipelineStage) -> None:
        self.stage = stage
        self.updated_at = datetime.now()

    def fail(self, message: str) -> None:
        self.stage = PipelineStage.FAILED
        self.error = message
        self.updated_at = datetime.now()
