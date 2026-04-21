"""Enumerations used throughout the domain."""
from __future__ import annotations

from enum import Enum


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ClauseType(str, Enum):
    TERMINATION = "Termination"
    LIABILITY = "Liability"
    INDEMNITY = "Indemnity"
    INTELLECTUAL_PROPERTY = "Intellectual Property"
    PAYMENT = "Payment"
    SLA = "Service Level Agreement"
    CONFIDENTIALITY = "Confidentiality"
    DATA_PROTECTION = "Data Protection / GDPR"
    GOVERNING_LAW = "Governing Law"
    FORCE_MAJEURE = "Force Majeure"
    AUTO_RENEWAL = "Auto Renewal"
    OTHER = "Other"


class PipelineStage(str, Enum):
    INGESTED = "ingested"
    EXTRACTED = "extracted"
    LANGUAGE_ENRICHED = "language_enriched"
    INDEXED = "indexed"
    CLAUSES_ANALYZED = "clauses_analyzed"
    RISK_SCORED = "risk_scored"
    COMPLIANCE_CHECKED = "compliance_checked"
    SUMMARIZED = "summarized"
    PERSISTED = "persisted"
    FAILED = "failed"
