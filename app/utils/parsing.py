"""Answer extraction and normalization helpers."""

from __future__ import annotations

import re


FINAL_PATTERNS = [
    re.compile(r"final answer\s*:\s*(.+)", re.IGNORECASE),
    re.compile(r"answer\s*:\s*(.+)", re.IGNORECASE),
    re.compile(r"therefore[, ]+the answer is\s+(.+)", re.IGNORECASE),
]


def extract_final_answer(trace: str) -> str:
    """Extract the final answer from a reasoning trace."""

    lines = [line.strip() for line in trace.splitlines() if line.strip()]
    for line in reversed(lines):
        for pattern in FINAL_PATTERNS:
            match = pattern.search(line)
            if match:
                return _clean_answer(match.group(1))

    if lines:
        return _clean_answer(lines[-1])
    return ""


def normalize_answer(answer: str) -> str:
    """Normalize for robust voting and evaluation."""

    cleaned = _clean_answer(answer).lower()
    cleaned = cleaned.replace("$", "").replace(",", "")
    if re.fullmatch(r"-?\d+(?:\.0+)?", cleaned):
        return str(int(float(cleaned)))
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip(" .")


def _clean_answer(answer: str) -> str:
    answer = answer.strip()
    answer = re.sub(r"^[\"'`]+|[\"'`]+$", "", answer)
    answer = re.sub(r"\s+", " ", answer)
    answer = re.sub(r"[.]+$", "", answer)
    return answer.strip()
