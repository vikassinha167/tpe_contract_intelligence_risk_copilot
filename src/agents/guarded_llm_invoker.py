"""Reusable helper that guards every LLM call with input/output content safety
and (optionally) emits Foundry evaluation scores.

This keeps every LLM-using agent thin and consistent — and is the natural place
to enforce enterprise responsible-AI policy.
"""
from __future__ import annotations

from src.domain import EvaluationScores
from src.interfaces import ChatMessage, IGuardrail, ILlmClient, IResponseEvaluator
from src.utils import GuardrailViolationError


class GuardedLlmInvoker:
    def __init__(
        self,
        llm: ILlmClient,
        guardrail: IGuardrail,
        evaluator: IResponseEvaluator | None = None,
    ) -> None:
        self._llm = llm
        self._guardrail = guardrail
        self._evaluator = evaluator

    def invoke(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        json_mode: bool = False,
        temperature: float = 0.0,
        max_tokens: int | None = None,
        evaluation_context: str | None = None,
    ) -> tuple[str, EvaluationScores | None]:
        in_verdict = self._guardrail.check_input(user_prompt)
        if not in_verdict.allowed:
            raise GuardrailViolationError(
                f"Input blocked by guardrail: {in_verdict.reason}"
            )

        response = self._llm.complete(
            messages=[
                ChatMessage("system", system_prompt),
                ChatMessage("user", user_prompt),
            ],
            temperature=temperature,
            json_mode=json_mode,
            max_tokens=max_tokens,
        )

        out_verdict = self._guardrail.check_output(response)
        if not out_verdict.allowed:
            raise GuardrailViolationError(
                f"Output blocked by guardrail: {out_verdict.reason}"
            )

        scores = None
        if self._evaluator is not None:
            scores = self._evaluator.evaluate(
                query=user_prompt, response=response, context=evaluation_context
            )
        return response, scores
