from app.utils.parsing import answers_match, extract_final_answer, extract_numbers, normalize_answer


def test_extract_final_answer_prefers_explicit_marker() -> None:
    trace = "We compute step by step.\nFinal Answer: 42."
    assert extract_final_answer(trace) == "42"


def test_extract_final_answer_falls_back_to_last_line() -> None:
    trace = "Reasoning here\n7"
    assert extract_final_answer(trace) == "7"


def test_normalize_answer_handles_numeric_variants() -> None:
    assert normalize_answer("42.0") == "42"
    assert normalize_answer("  $1,200  ") == "1200"


def test_normalize_answer_extracts_number_from_short_sentence() -> None:
    assert normalize_answer("Emma now has 12 coins") == "12"
    assert normalize_answer("There are 22 legs in total") == "22"


def test_normalize_answer_strips_simple_markup() -> None:
    assert normalize_answer("<answer>16</answer>") == "16"


def test_normalize_answer_handles_short_text() -> None:
    assert normalize_answer(" John ") == "john"
    assert normalize_answer("John is the oldest") == "john"


def test_extract_numbers_preserves_all_numeric_candidates() -> None:
    assert extract_numbers("Ben spends $21 on 3 toys") == ["21", "3"]


def test_answers_match_handles_numeric_sentence_answers() -> None:
    assert answers_match("21", "Ben spends $21 on 3 toys")
    assert answers_match("12", "Emma now has 12 coins")
    assert not answers_match("14", "5 oranges remain in total")


def test_answers_match_handles_textual_containment() -> None:
    assert answers_match("John", "Therefore, the oldest person among John, Mia, and Ava is John")
    assert not answers_match("John", "Ava is the oldest")
