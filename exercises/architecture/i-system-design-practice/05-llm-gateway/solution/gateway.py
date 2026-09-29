"""Architecture · I — A mini LLM gateway: cache, fallback, cost (solution)."""


def estimate_cost(tokens: int, price_per_1k: float) -> float:
    return tokens / 1000 * price_per_1k


class LLMGateway:
    def __init__(self, providers: list, price_per_1k: float):
        self.providers = providers
        self.price_per_1k = price_per_1k
        self.cache: dict = {}
        self.total_cost = 0.0

    def complete(self, prompt: str) -> dict:
        if prompt in self.cache:
            hit = self.cache[prompt]
            return {"text": hit["text"], "provider": hit["provider"], "cached": True, "cost": 0.0}

        for name, fn in self.providers:
            try:
                result = fn(prompt)
            except Exception:
                continue
            cost = estimate_cost(result["tokens"], self.price_per_1k)
            self.total_cost += cost
            self.cache[prompt] = {"text": result["text"], "provider": name, "tokens": result["tokens"]}
            return {"text": result["text"], "provider": name, "cached": False, "cost": cost}

        raise RuntimeError("all providers failed")
