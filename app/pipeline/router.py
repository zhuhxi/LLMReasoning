"""Simple rule-based router for strategy selection."""

from __future__ import annotations


class StrategyRouter:
    """Route questions to CoT or least-to-most using simple heuristics."""

    L2M_HINTS = (
        "first",
        "then",
        "after",
        "before",
        "remaining",
        "left",
        "twice",
        "each",
        "every",
        "altogether",
    )

    def choose(self, question: str) -> str:
        lowered = question.lower()
        has_sequence = any(token in lowered for token in self.L2M_HINTS)
        numeric_density = sum(ch.isdigit() for ch in question)
        if has_sequence or numeric_density >= 3 or len(question.split()) > 25:
            return "l2m"
        return "cot"
