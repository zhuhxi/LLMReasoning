"""Chain-of-thought strategy."""

from __future__ import annotations

from app.strategies.base import BaseStrategy


class ChainOfThoughtStrategy(BaseStrategy):
    """Direct reasoning with a single prompt."""

    @property
    def name(self) -> str:
        return "cot"

    def run(self, question: str, sample_index: int = 0):
        prompt = self._prompt_text("cot.txt").format(question=question)
        result = self.client.generate(prompt)
        return self._build_result(
            sample_index=sample_index,
            trace=result.text,
            metadata={"model": result.model, "raw": result.raw},
        )
