from __future__ import annotations

from collections import deque

from app.models import GenerationResult
from app.strategies.least_to_most import LeastToMostStrategy


class FakeClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = deque(responses)

    def generate(self, prompt: str):
        return GenerationResult(text=self.responses.popleft(), model="fake")


def test_l2m_runs_decompose_then_solves_subproblems() -> None:
    client = FakeClient(
        [
            "1. Add the apples Elsa bought.\n2. Subtract the apples she gave away.",
            "Elsa has 7 apples after buying more.",
            "Subtract 2 from 7.\nFinal Answer: 5",
        ]
    )
    strategy = LeastToMostStrategy(client)
    result = strategy.run("Elsa has 3 apples and buys 4 more. Then she gives away 2.")
    assert result.final_answer == "5"
    assert result.metadata["subproblems"] == [
        "Add the apples Elsa bought.",
        "Subtract the apples she gave away.",
    ]
