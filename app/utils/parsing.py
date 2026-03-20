"""Answer extraction and normalization helpers."""

from __future__ import annotations

import re


FINAL_PATTERNS = [
    re.compile(r"final answer\s*:\s*(.+)", re.IGNORECASE),
    re.compile(r"answer\s*:\s*(.+)", re.IGNORECASE),
    re.compile(r"therefore[, ]+the answer is\s+(.+)", re.IGNORECASE),
]

TEXT_PREFIX_PATTERNS = [
    re.compile(r"^(?:therefore|thus|so)[, ]+", re.IGNORECASE),
]

UNIT_SUFFIXES = (
    "apples",
    "books",
    "muffins",
    "pages",
    "passengers",
    "marbles",
    "pencils",
    "candies",
    "birds",
    "dollars",
    "meters",
    "stickers",
    "legs",
    "cookies",
    "pens",
    "coins",
    "oranges",
    "students",
    "ribbons",
    "toys",
    "pieces",
    "boxes",
)


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
    cleaned = _strip_markup(cleaned)

    numeric = _extract_numeric_answer(cleaned)
    if numeric is not None:
        return numeric

    cleaned = _normalize_text_answer(cleaned)
    return cleaned.strip(" .")


def answers_match(expected: str, predicted: str) -> bool:
    """Compare answers with type-aware rules for benchmark scoring."""

    expected_norm = normalize_answer(expected)
    predicted_norm = normalize_answer(predicted)
    if expected_norm == predicted_norm:
        return True

    expected_numbers = extract_numbers(expected)
    predicted_numbers = extract_numbers(predicted)
    if expected_numbers:
        return expected_numbers[0] in predicted_numbers

    expected_text = _normalize_text_answer(_strip_markup(_clean_answer(expected).lower()))
    predicted_text = _normalize_text_answer(_strip_markup(_clean_answer(predicted).lower()))
    if expected_text == predicted_text:
        return True

    pattern = re.compile(rf"\b{re.escape(expected_text)}\b", re.IGNORECASE)
    return bool(pattern.search(predicted_text))


def extract_numbers(text: str) -> list[str]:
    """Return normalized numeric mentions in appearance order."""

    cleaned = _strip_markup(_clean_answer(text).lower()).replace("$", "").replace(",", "")
    return [_normalize_number(match) for match in re.findall(r"-?\d+(?:\.\d+)?", cleaned)]


def _clean_answer(answer: str) -> str:
    answer = answer.strip()
    answer = re.sub(r"^[\"'`]+|[\"'`]+$", "", answer)
    answer = re.sub(r"\*+", "", answer)
    answer = re.sub(r"\s+", " ", answer)
    answer = re.sub(r"[.]+$", "", answer)
    return answer.strip()


def _strip_markup(text: str) -> str:
    text = re.sub(r"</?answer>", " ", text)
    text = re.sub(r"[<>{}\[\]()]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _extract_numeric_answer(text: str) -> str | None:
    if re.fullmatch(r"-?\d+(?:\.0+)?", text):
        return str(int(float(text)))

    candidates = extract_numbers(text)
    if len(candidates) == 1:
        return candidates[0]
    return None


def _normalize_number(value: str) -> str:
    number = float(value)
    if number.is_integer():
        return str(int(number))
    return str(number)


def _normalize_text_answer(text: str) -> str:
    text = re.sub(r"\b(the final answer is|final answer|answer is|the answer is)\b", " ", text)
    for pattern in TEXT_PREFIX_PATTERNS:
        text = pattern.sub("", text)
    text = re.sub(r"\s+", " ", text).strip(" .")

    if text.endswith(" is the oldest"):
        text = text[: -len(" is the oldest")]

    if text.endswith(UNIT_SUFFIXES):
        words = text.split()
        if words and re.fullmatch(r"-?\d+(?:\.\d+)?", words[0]):
            text = words[0]

    return text.strip(" .")
