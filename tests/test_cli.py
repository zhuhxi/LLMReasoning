from __future__ import annotations

import json

from app import main


class FakeAgent:
    def __init__(self, config):
        self.default_samples = 5

    def solve(self, question: str, strategy: str = "auto", samples: int | None = None):
        return {
            "chosen_strategy": strategy,
            "runs": [
                {
                    "strategy": "cot",
                    "sample_index": 0,
                    "trace": "Reasoning\nFinal Answer: 5",
                    "final_answer": "5",
                    "normalized_answer": "5",
                    "metadata": {},
                }
            ],
            "vote_counts": {"5": 1},
            "final_selected_answer": "5",
        }


def test_cli_question_mode_smoke(monkeypatch, capsys) -> None:
    monkeypatch.setattr(main, "ReasoningAgent", FakeAgent)
    exit_code = main.main(["--question", "What is 2+3?", "--strategy", "cot", "--samples", "1"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["final_selected_answer"] == "5"
