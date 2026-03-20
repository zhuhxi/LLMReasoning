"""Minimal Ollama HTTP client with retries."""

from __future__ import annotations

from dataclasses import dataclass
import json
import time
from urllib import error, request

from app.config import AppConfig
from app.models import GenerationResult


class OllamaError(RuntimeError):
    """Raised when the Ollama backend cannot produce a response."""


@dataclass(slots=True)
class OllamaClient:
    """Small wrapper around the Ollama generate endpoint."""

    config: AppConfig

    def generate(self, prompt: str, temperature: float | None = None) -> GenerationResult:
        payload = {
            "model": self.config.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature if temperature is None else temperature,
            },
        }
        url = f"{self.config.ollama_base_url.rstrip('/')}/api/generate"
        body = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        last_error: Exception | None = None

        for attempt in range(1, self.config.max_retries + 1):
            req = request.Request(url, data=body, headers=headers, method="POST")
            try:
                with request.urlopen(req, timeout=self.config.timeout_seconds) as response:
                    raw = json.loads(response.read().decode("utf-8"))
                    return GenerationResult(
                        text=raw.get("response", "").strip(),
                        model=raw.get("model", self.config.model_name),
                        prompt_tokens=raw.get("prompt_eval_count"),
                        eval_tokens=raw.get("eval_count"),
                        total_duration_ns=raw.get("total_duration"),
                        raw=raw,
                    )
            except (error.HTTPError, error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt == self.config.max_retries:
                    break
                time.sleep(min(2 ** (attempt - 1), 4))

        raise OllamaError(
            f"Failed to call Ollama at {url} after {self.config.max_retries} attempts: {last_error}"
        )
