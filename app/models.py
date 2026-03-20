"""Shared data models for the reasoning agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class GenerationResult:
    """Raw output returned by Ollama."""

    text: str
    model: str
    prompt_tokens: int | None = None
    eval_tokens: int | None = None
    total_duration_ns: int | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StrategyRun:
    """A single strategy execution."""

    strategy_name: str
    sample_index: int
    trace: str
    final_answer: str
    normalized_answer: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class VoteResult:
    """Aggregated vote details."""

    selected_answer: str
    normalized_selected_answer: str
    counts: dict[str, int]
    raw_answers: list[str]


@dataclass(slots=True)
class BenchmarkExample:
    """A benchmark question/answer pair."""

    id: str
    question: str
    answer: str
    category: str
