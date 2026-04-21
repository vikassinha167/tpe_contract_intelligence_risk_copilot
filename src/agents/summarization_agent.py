"""Summarization agent — produces an executive brief and runs evaluation."""
from __future__ import annotations

from src.domain import Contract, PipelineStage

from .base_agent import BaseAgent
from .guarded_llm_invoker import GuardedLlmInvoker

_SYSTEM_PROMPT = """You are an executive assistant.
Write a crisp 5-bullet executive brief for the supplied contract analysis.
Focus on commercial obligations, top risks, compliance gaps, and recommendations.
Plain text only — no markdown, no preamble."""


class SummarizationAgent(BaseAgent):
    name = "SummarizationAgent"

    def __init__(self, invoker: GuardedLlmInvoker) -> None:
        super().__init__()
        self._invoker = invoker

    def run(self, contract: Contract) -> Contract:
        self._log_start(contract)
        prompt = self._build_prompt(contract)
        summary, scores = self._invoker.invoke(
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=prompt,
            evaluation_context=contract.raw_text or "",
            max_tokens=400,
        )
        contract.executive_summary = summary
        contract.evaluation = scores
        contract.advance(PipelineStage.SUMMARIZED)
        self._log_done(contract)
        return contract

    @staticmethod
    def _build_prompt(contract: Contract) -> str:
        clause_lines = [
            f"- [{c.risk_level.value if c.risk_level else 'N/A'}] "
            f"{c.clause_type.value}: {(c.rationale or '')[:180]}"
            for c in contract.clauses
        ]
        compliance_lines = [
            f"- {f.rule_id} {'PASS' if f.passed else 'FAIL'}: {f.rule_description}"
            for f in contract.compliance_findings
        ]
        return (
            f"Source: {contract.source_blob}\n"
            f"Overall risk: {contract.overall_risk_level.value if contract.overall_risk_level else 'N/A'} "
            f"(score {contract.overall_risk_score})\n\n"
            "Clauses:\n" + "\n".join(clause_lines) + "\n\n"
            "Compliance:\n" + "\n".join(compliance_lines)
        )
