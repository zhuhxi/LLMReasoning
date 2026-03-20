from app.utils.parsing import extract_final_answer, normalize_answer


def test_extract_final_answer_prefers_explicit_marker() -> None:
    trace = "We compute step by step.\nFinal Answer: 42."
    assert extract_final_answer(trace) == "42"


def test_extract_final_answer_falls_back_to_last_line() -> None:
    trace = "Reasoning here\n7"
    assert extract_final_answer(trace) == "7"


def test_normalize_answer_handles_numeric_variants() -> None:
    assert normalize_answer("42.0") == "42"
    assert normalize_answer("  $1,200  ") == "1200"


def test_normalize_answer_handles_short_text() -> None:
    assert normalize_answer(" John ") == "john"
