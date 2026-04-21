"""Clause analysis agent — uses the LLM to identify and classify clauses."""
from __future__ import annotations

import json

from src.domain import Clause, ClauseType, Contract, PipelineStage

from .base_agent import BaseAgent
from .guarded_llm_invoker import GuardedLlmInvoker

_SYSTEM_PROMPT = """You are an expert contract attorney.
Identify the most important clauses in the supplied contract text.

Return ONLY a JSON object of the form:
{
  "clauses": [
    {"clause_type": "<one of: Termination, Liability, Indemnity, Intellectual Property, Payment, Service Level Agreement, Confidentiality, Data Protection / GDPR, Governing Law, Force Majeure, Auto Renewal, Other>",
     "text": "<verbatim clause text, max 600 chars>"}
  ]
}
Only include clauses that are clearly present. Do NOT invent clauses.
"""

# Truncate to keep token usage predictable; production code should chunk + map-reduce.
_MAX_CHARS = 16000


class ClauseAnalysisAgent(BaseAgent):
    name = "ClauseAnalysisAgent"

    def __init__(self, invoker: GuardedLlmInvoker) -> None:
        super().__init__()
        self._invoker = invoker

    def run(self, contract: Contract) -> Contract:
        self._log_start(contract)
        text = (contract.raw_text or "")[:_MAX_CHARS]
        if not text:
            raise ValueError("ClauseAnalysisAgent requires raw_text")

        response, _ = self._invoker.invoke(
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=text,
            json_mode=True,
        )
        contract.clauses = self._parse(response)
        contract.advance(PipelineStage.CLAUSES_ANALYZED)
        self._log_done(contract)
        return contract

    @staticmethod
    def _parse(payload: str) -> list[Clause]:
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            return []
        clauses: list[Clause] = []
        for item in data.get("clauses", []):
            try:
                ctype = ClauseType(item["clause_type"])
            except (KeyError, ValueError):
                ctype = ClauseType.OTHER
            text = (item.get("text") or "").strip()
            if text:
                clauses.append(Clause(clause_type=ctype, text=text))
        return clauses
