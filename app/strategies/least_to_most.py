"""Least-to-most strategy."""

from __future__ import annotations

from app.strategies.base import BaseStrategy


class LeastToMostStrategy(BaseStrategy):
    """Decompose the problem and solve subproblems sequentially."""

    @property
    def name(self) -> str:
        return "l2m"

    def run(self, question: str, sample_index: int = 0):
        decomposition_prompt = self._prompt_text("l2m_decompose.txt").format(question=question)
        decomposition = self.client.generate(decomposition_prompt).text.strip()
        subproblems = self._parse_subproblems(decomposition)

        context = []
        trace_parts = [f"Decomposition:\n{decomposition}"]
        latest_answer = ""

        for subproblem in subproblems:
            solve_prompt = self._prompt_text("l2m_solve.txt").format(
                question=question,
                context="\n".join(context) if context else "No prior work.",
                subproblem=subproblem,
            )
            solved = self.client.generate(solve_prompt).text.strip()
            trace_parts.append(f"Subproblem: {subproblem}\n{solved}")
            context.append(f"{subproblem}\n{solved}")
            latest_answer = solved

        return self._build_result(
            sample_index=sample_index,
            trace="\n\n".join(trace_parts) if trace_parts else latest_answer,
            metadata={"subproblems": subproblems},
        )

    @staticmethod
    def _parse_subproblems(decomposition: str) -> list[str]:
        items = []
        for line in decomposition.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped[0].isdigit() and "." in stripped:
                items.append(stripped.split(".", 1)[1].strip())
            else:
                items.append(stripped)
        return items or ["Solve the full problem directly."]
