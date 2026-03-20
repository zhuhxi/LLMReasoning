"""Sampling helpers for self-consistency."""

from __future__ import annotations

from app.models import StrategyRun
from app.strategies.base import BaseStrategy


def sample_runs(strategy: BaseStrategy, question: str, samples: int) -> list[StrategyRun]:
    """Run a strategy multiple times."""

    return [strategy.run(question, sample_index=index) for index in range(samples)]
