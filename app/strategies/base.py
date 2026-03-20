"""Base interfaces for reasoning strategies."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from app.models import StrategyRun
from app.ollama_client import OllamaClient
from app.utils.parsing import extract_final_answer, normalize_answer


class BaseStrategy(ABC):
    """Common behavior for strategy implementations."""

    def __init__(self, client: OllamaClient) -> None:
        self.client = client

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the strategy identifier."""

    @abstractmethod
    def run(self, question: str, sample_index: int = 0) -> StrategyRun:
        """Run the strategy once for a given question."""

    def _prompt_text(self, filename: str) -> str:
        prompts_dir = Path(__file__).resolve().parent.parent / "prompts"
        return (prompts_dir / filename).read_text(encoding="utf-8")

    def _build_result(self, sample_index: int, trace: str, metadata: dict | None = None) -> StrategyRun:
        answer = extract_final_answer(trace)
        return StrategyRun(
            strategy_name=self.name,
            sample_index=sample_index,
            trace=trace.strip(),
            final_answer=answer,
            normalized_answer=normalize_answer(answer),
            metadata=metadata or {},
        )
