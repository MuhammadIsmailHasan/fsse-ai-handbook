"""Architecture · I — A mini LLM gateway: cache, fallback, and cost.

One entry point for AI calls that:
- caches identical prompts (skip the paid call),
- falls back through a list of providers until one succeeds,
- tracks total spend.

Providers are (name, fn) pairs tried in order. fn(prompt) returns
{"text": str, "tokens": int} or raises an exception to simulate a failure.
"""


def estimate_cost(tokens: int, price_per_1k: float) -> float:
    """Cost of a call: tokens / 1000 * price_per_1k."""
    # YOUR CODE HERE
    return -1.0


class LLMGateway:
    def __init__(self, providers: list, price_per_1k: float):
        self.providers = providers          # [(name, fn), ...] in fallback order
        self.price_per_1k = price_per_1k
        self.cache: dict = {}               # prompt -> {"text", "provider", "tokens"}
        self.total_cost = 0.0

    def complete(self, prompt: str) -> dict:
        """Return {"text", "provider", "cached", "cost"}.

        - Cache hit: return the stored answer with cached=True and cost=0.0;
          do NOT call any provider.
        - Cache miss: try providers in order; the first that succeeds wins.
          Add estimate_cost(tokens, price) to self.total_cost, cache the result,
          and return cached=False with that cost.
        - If every provider fails, raise RuntimeError.
        """
        # YOUR CODE HERE
        return {}
