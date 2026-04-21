"""Compliance agent — checks the contract against a configurable policy set.

Policies are simple, declarative rules: required clause-types must be present.
Open/Closed: add a new rule by extending `DEFAULT_RULES` (or injecting custom).
"""
from __future__ import annotations

from dataclasses import dataclass

from src.domain import ClauseType, ComplianceFinding, Contract, PipelineStage

from .base_agent import BaseAgent


@dataclass(frozen=True)
class ComplianceRule:
    rule_id: str
    description: str
    required_clause: ClauseType


DEFAULT_RULES: tuple[ComplianceRule, ...] = (
    ComplianceRule(
        "POL-001", "Contract must define termination terms.", ClauseType.TERMINATION
    ),
    ComplianceRule(
        "POL-002", "Contract must include a liability clause.", ClauseType.LIABILITY
    ),
    ComplianceRule(
        "POL-003",
        "Contract must include a confidentiality clause.",
        ClauseType.CONFIDENTIALITY,
    ),
    ComplianceRule(
        "POL-004",
        "Contract must include a data protection / GDPR clause.",
        ClauseType.DATA_PROTECTION,
    ),
    ComplianceRule(
        "POL-005",
        "Contract must specify governing law.",
        ClauseType.GOVERNING_LAW,
    ),
)


class ComplianceAgent(BaseAgent):
    name = "ComplianceAgent"

    def __init__(self, rules: tuple[ComplianceRule, ...] = DEFAULT_RULES) -> None:
        super().__init__()
        self._rules = rules

    def run(self, contract: Contract) -> Contract:
        self._log_start(contract)
        present_types = {c.clause_type for c in contract.clauses}
        findings: list[ComplianceFinding] = []
        for rule in self._rules:
            passed = rule.required_clause in present_types
            findings.append(
                ComplianceFinding(
                    rule_id=rule.rule_id,
                    rule_description=rule.description,
                    passed=passed,
                    evidence=None
                    if passed
                    else f"Missing clause type: {rule.required_clause.value}",
                )
            )
        contract.compliance_findings = findings
        contract.advance(PipelineStage.COMPLIANCE_CHECKED)
        self._log_done(contract)
        return contract
