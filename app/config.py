"""Configuration helpers for the reasoning agent."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(slots=True)
class AppConfig:
    """Runtime configuration loaded from the environment."""

    ollama_base_url: str = "http://localhost:11434"
    model_name: str = "llama3.1:8b"
    temperature: float = 0.2
    timeout_seconds: int = 90
    max_retries: int = 3
    default_samples: int = 5

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model_name=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
            temperature=float(os.getenv("OLLAMA_TEMPERATURE", "0.2")),
            timeout_seconds=int(os.getenv("OLLAMA_TIMEOUT", "90")),
            max_retries=int(os.getenv("OLLAMA_MAX_RETRIES", "3")),
            default_samples=int(os.getenv("REASONING_AGENT_DEFAULT_SAMPLES", "5")),
        )
