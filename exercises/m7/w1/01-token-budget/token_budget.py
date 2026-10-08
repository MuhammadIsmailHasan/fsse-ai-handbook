"""Module 7 · W1 — Tokens, context and temperature (no API key needed).

Helpers every LLM app needs: a rough token count, the price of a call, a way to keep a
long chat inside the context window, and the maths behind `temperature`.
"""

import math  # noqa: F401  (you will want it)

MESSAGE_OVERHEAD = 4   # each message costs a few extra tokens for its role and framing


def estimate_tokens(text: str) -> int:
    """Rough token count: about 4 characters per token, rounded UP. Empty text: 0."""
    raise NotImplementedError


def request_cost(input_tokens: int, output_tokens: int, input_price_per_m: float, output_price_per_m: float) -> float:
    """Price of one call in dollars. Prices are dollars per 1,000,000 tokens."""
    raise NotImplementedError


def fit_history(messages: list[dict], max_context: int, reserve_for_output: int) -> list[dict]:
    """Trim a chat so it fits in the context window.

    messages: [{"role": "system"|"user"|"assistant", "content": str}, ...] (a system message, if any, is first)
    A message costs estimate_tokens(content) + MESSAGE_OVERHEAD.
    Budget = max_context - reserve_for_output (room kept for the answer).

    Rules:
      - keep the system message (if there is one) and ALWAYS keep the last message
      - drop the OLDEST other messages first, one at a time
      - after the system message the chat must start with a "user" message, so if the oldest kept
        message is an "assistant" message, drop it too
      - if the system message + the last message alone are still over budget, raise ValueError
      - do not change the list you were given; return a new list in the original order
    """
    raise NotImplementedError


def apply_temperature(logits: dict[str, float], temperature: float) -> dict[str, float]:
    """Turn raw scores (logits) into probabilities: softmax(logit / temperature).

    - the probabilities add up to 1
    - temperature 0 means "always the best": 1.0 for the highest logit (the first one on a tie), 0.0 for the rest
    - temperature below 0: ValueError
    - must not overflow on large logits (subtract the maximum first)
    """
    raise NotImplementedError
