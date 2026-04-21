"""Risk scoring agent — scores each clause AND aggregates a contract-level risk."""
from __future__ import annotations

import json

from src.domain import Contract, PipelineStage, RiskLevel

from .base_agent import BaseAgent
from .guarded_llm_invoker import GuardedLlmInvoker

_SYSTEM_PROMPT = """You are a senior contract risk analyst.
Score the supplied clause for risk to the BUYER.

Return ONLY JSON:
{
  "risk_level": "Low|Medium|High|Critical",
  "risk_score": <float 0.0-1.0>,
  "rationale": "<2-3 sentence justification>",
  "recommendation": "<concrete mitigation suggestion>"
}
"""

_LEVEL_WEIGHT = {
    RiskLevel.LOW: 0.15,
    RiskLevel.MEDIUM: 0.4,
    RiskLevel.HIGH: 0.7,
    RiskLevel.CRITICAL: 1.0,
}


class RiskScoringAgent(BaseAgent):
    name = "RiskScoringAgent"

    def __init__(self, invoker: GuardedLlmInvoker) -> None:
        super().__init__()
        self._invoker = invoker

    def run(self, contract: Contract) -> Contract:
        self._log_start(contract)
        for clause in contract.clauses:
            response, _ = self._invoker.invoke(
                system_prompt=_SYSTEM_PROMPT,
                user_prompt=f"Clause type: {clause.clause_type.value}\n\nText:\n{clause.text}",
                json_mode=True,
            )
            self._apply(clause, response)

        contract.overall_risk_score, contract.overall_risk_level = self._aggregate(
            contract
        )
        contract.advance(PipelineStage.RISK_SCORED)
        self._log_done(contract)
        return contract

    # --------------------- helpers ---------------------
    @staticmethod
    def _apply(clause, payload: str) -> None:
        try:
            data = json.loads(payload)
            clause.risk_level = RiskLevel(data.get("risk_level", "Low"))
            clause.risk_score = float(data.get("risk_score", 0.0))
            clause.rationale = data.get("rationale")
            clause.recommendation = data.get("recommendation")
        except (json.JSONDecodeError, ValueError):
            clause.risk_level = RiskLevel.LOW
            clause.risk_score = 0.0
            clause.rationale = "Could not parse model output."

    @staticmethod
    def _aggregate(contract: Contract) -> tuple[float, RiskLevel]:
        if not contract.clauses:
            return 0.0, RiskLevel.LOW
        # Weighted average using both model score and severity-band weight.
        scores = [
            (c.risk_score or 0.0) * _LEVEL_WEIGHT.get(c.risk_level or RiskLevel.LOW, 0.1)
            for c in contract.clauses
        ]
        agg = sum(scores) / len(scores)
        if agg >= 0.75:
            level = RiskLevel.CRITICAL
        elif agg >= 0.5:
            level = RiskLevel.HIGH
        elif agg >= 0.25:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW
        return round(agg, 4), level
