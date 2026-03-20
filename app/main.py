"""CLI entry point for the reasoning agent."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from app.config import AppConfig
from app.ollama_client import OllamaClient, OllamaError
from app.pipeline.evaluator import evaluate_benchmark
from app.pipeline.router import StrategyRouter
from app.pipeline.sampler import sample_runs
from app.pipeline.voter import majority_vote
from app.strategies.cot import ChainOfThoughtStrategy
from app.strategies.least_to_most import LeastToMostStrategy
from app.utils.logging import configure_logging


class ReasoningAgent:
    """Coordinate routing, strategy execution, and self-consistency voting."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.default_samples = config.default_samples
        self.client = OllamaClient(config)
        self.router = StrategyRouter()
        self.strategies = {
            "cot": ChainOfThoughtStrategy(self.client),
            "l2m": LeastToMostStrategy(self.client),
        }

    def solve(self, question: str, strategy: str = "auto", samples: int | None = None) -> dict[str, Any]:
        samples = samples or self.default_samples
        if strategy == "auto":
            selected_strategy = self.router.choose(question)
            return self._run_single_strategy(question, selected_strategy, samples)
        if strategy == "both":
            combined_runs = []
            strategy_results = {}
            for name in ("cot", "l2m"):
                outcome = self._run_single_strategy(question, name, samples)
                strategy_results[name] = outcome
                combined_runs.extend(outcome["runs"])
            vote = majority_vote([run["final_answer"] for run in combined_runs])
            return {
                "chosen_strategy": "both",
                "strategy_results": strategy_results,
                "runs": combined_runs,
                "vote_counts": vote.counts,
                "final_selected_answer": vote.selected_answer,
            }
        return self._run_single_strategy(question, strategy, samples)

    def _run_single_strategy(self, question: str, strategy: str, samples: int) -> dict[str, Any]:
        runs = sample_runs(self.strategies[strategy], question, samples)
        vote = majority_vote([run.final_answer for run in runs])
        return {
            "chosen_strategy": strategy,
            "runs": [
                {
                    "strategy": run.strategy_name,
                    "sample_index": run.sample_index,
                    "trace": run.trace,
                    "final_answer": run.final_answer,
                    "normalized_answer": run.normalized_answer,
                    "metadata": run.metadata,
                }
                for run in runs
            ],
            "vote_counts": vote.counts,
            "final_selected_answer": vote.selected_answer,
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reasoning-focused Ollama agent for multi-step problem solving.")
    parser.add_argument("--question", help="A single reasoning question to solve.")
    parser.add_argument(
        "--strategy",
        choices=["auto", "cot", "l2m", "both"],
        default="auto",
        help="Reasoning strategy to run. 'auto' uses the rule-based router.",
    )
    parser.add_argument("--samples", type=int, help="Number of self-consistency samples to draw.")
    parser.add_argument("--benchmark", help="Run benchmark evaluation from the given JSON file.")
    parser.add_argument(
        "--output",
        default="benchmark_results.json",
        help="Output JSON path for benchmark runs.",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.verbose)
    config = AppConfig.from_env()
    agent = ReasoningAgent(config)

    try:
        if args.benchmark:
            results = evaluate_benchmark(agent, args.benchmark, args.output)
            print(json.dumps(results, indent=2))
            return 0

        if not args.question:
            parser.error("Provide --question or --benchmark.")

        outcome = agent.solve(args.question, strategy=args.strategy, samples=args.samples)
        print(json.dumps(outcome, indent=2))
        return 0
    except OllamaError as exc:
        print(f"Ollama backend error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
