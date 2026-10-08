"""Module 7 · W1 — Choosing a model with numbers (no API key needed).

A model is described by a dict:
    {"name": str, "quality": int (1-10), "input_price": float, "output_price": float,
     "latency_s": float, "context": int}
Prices are dollars per 1,000,000 tokens.
"""


def call_cost(model: dict, input_tokens: int, output_tokens: int) -> float:
    """Dollar cost of one call with this model."""
    raise NotImplementedError


def choose_model(
    models: list[dict], *, min_quality: int, max_latency_s: float, input_tokens: int, output_tokens: int
) -> str | None:
    """Name of the CHEAPEST model (per call) that is good enough, fast enough and big enough.

    - quality >= min_quality
    - latency_s <= max_latency_s
    - context >= input_tokens + output_tokens
    Ties on cost: the faster model wins; then the name that comes first alphabetically.
    Return None if no model qualifies.
    """
    raise NotImplementedError


def monthly_cost(
    model: dict,
    requests_per_day: int,
    input_tokens: int,
    output_tokens: int,
    cache_hit_rate: float = 0.0,
    days: int = 30,
) -> float:
    """Cost over `days` days.

    A cached input token costs 10% of the normal input price. `cache_hit_rate` (0 to 1) is the
    share of input tokens served from the cache. Output tokens are never cached.
    """
    raise NotImplementedError


def run_cascade(models_cheapest_first: list[str], ask, is_good) -> tuple[str, str, float] | None:
    """Try the cheap model first and move to a stronger one only if the answer is not good.

    ask(model_name)  -> (answer, cost_in_dollars)
    is_good(answer)  -> bool
    Return (model_name, answer, total_cost) for the first good answer. total_cost adds up EVERY
    attempt, including the failed ones. If no model gives a good answer, return None.
    """
    raise NotImplementedError
