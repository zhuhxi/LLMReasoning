"""Benchmark evaluation helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.models import BenchmarkExample
from app.utils.parsing import answers_match, normalize_answer


def load_benchmark(path: str) -> list[BenchmarkExample]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [BenchmarkExample(**item) for item in data]


def evaluate_benchmark(agent: Any, benchmark_path: str, output_path: str) -> dict[str, Any]:
    examples = load_benchmark(benchmark_path)
    modes = [
        ("cot_single", "cot", 1),
        ("cot_self_consistency", "cot", agent.default_samples),
        ("l2m_single", "l2m", 1),
        ("l2m_self_consistency", "l2m", agent.default_samples),
    ]

    results: dict[str, Any] = {"benchmark_path": benchmark_path, "runs": {}}
    for label, strategy, samples in modes:
        correct = 0
        cases = []
        for example in examples:
            outcome = agent.solve(example.question, strategy=strategy, samples=samples)
            predicted = outcome["final_selected_answer"]
            expected = example.answer
            is_correct = answers_match(expected, predicted)
            correct += int(is_correct)
            cases.append(
                {
                    "id": example.id,
                    "question": example.question,
                    "expected": expected,
                    "predicted": predicted,
                    "is_correct": is_correct,
                    "normalized_expected": normalize_answer(expected),
                    "normalized_predicted": normalize_answer(predicted),
                }
            )
        results["runs"][label] = {
            "strategy": strategy,
            "samples": samples,
            "accuracy": correct / len(examples) if examples else 0.0,
            "correct": correct,
            "total": len(examples),
            "cases": cases,
        }

    Path(output_path).write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results
