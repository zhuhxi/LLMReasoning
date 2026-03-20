from app.pipeline.router import StrategyRouter


def test_router_prefers_l2m_for_multi_step_word_problem() -> None:
    router = StrategyRouter()
    question = "A bus has 18 passengers. At the first stop, 6 get off and 4 get on. How many passengers are on the bus now?"
    assert router.choose(question) == "l2m"


def test_router_prefers_cot_for_short_direct_question() -> None:
    router = StrategyRouter()
    assert router.choose("What is 3 plus 4?") == "cot"
