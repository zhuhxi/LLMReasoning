"""Majority voting over sampled answers."""

from __future__ import annotations

from collections import Counter

from app.models import VoteResult
from app.utils.parsing import normalize_answer


def majority_vote(answers: list[str]) -> VoteResult:
    """Vote on normalized answers with first-seen deterministic tie-break."""

    if not answers:
        return VoteResult(selected_answer="", normalized_selected_answer="", counts={}, raw_answers=[])

    normalized = [normalize_answer(answer) for answer in answers]
    counts = Counter(normalized)
    first_seen = {}
    for index, answer in enumerate(normalized):
        first_seen.setdefault(answer, index)
    winner = sorted(counts.items(), key=lambda item: (-item[1], first_seen[item[0]], item[0]))[0][0]
    raw_selected = next(raw for raw, norm in zip(answers, normalized) if norm == winner)
    return VoteResult(
        selected_answer=raw_selected,
        normalized_selected_answer=winner,
        counts=dict(counts),
        raw_answers=answers,
    )
