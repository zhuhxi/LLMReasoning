from app.pipeline.voter import majority_vote


def test_majority_vote_returns_most_common_answer() -> None:
    result = majority_vote(["7", "7.0", "8"])
    assert result.normalized_selected_answer == "7"
    assert result.counts["7"] == 2


def test_majority_vote_uses_first_seen_on_tie() -> None:
    result = majority_vote(["blue", "red"])
    assert result.selected_answer == "blue"
