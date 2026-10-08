def call_cost(model, input_tokens, output_tokens):
    return input_tokens * model["input_price"] / 1_000_000 + output_tokens * model["output_price"] / 1_000_000


def choose_model(models, *, min_quality, max_latency_s, input_tokens, output_tokens):
    ok = [
        m
        for m in models
        if m["quality"] >= min_quality
        and m["latency_s"] <= max_latency_s
        and m["context"] >= input_tokens + output_tokens
    ]
    if not ok:
        return None
    best = min(ok, key=lambda m: (call_cost(m, input_tokens, output_tokens), m["latency_s"], m["name"]))
    return best["name"]


def monthly_cost(model, requests_per_day, input_tokens, output_tokens, cache_hit_rate=0.0, days=30):
    price_in = model["input_price"] * ((1 - cache_hit_rate) + cache_hit_rate * 0.1)
    per_call = input_tokens * price_in / 1_000_000 + output_tokens * model["output_price"] / 1_000_000
    return per_call * requests_per_day * days


def run_cascade(models_cheapest_first, ask, is_good):
    total = 0.0
    for name in models_cheapest_first:
        answer, cost = ask(name)
        total += cost
        if is_good(answer):
            return name, answer, total
    return None
