import math

MESSAGE_OVERHEAD = 4


def estimate_tokens(text):
    return math.ceil(len(text) / 4)


def request_cost(input_tokens, output_tokens, input_price_per_m, output_price_per_m):
    return input_tokens * input_price_per_m / 1_000_000 + output_tokens * output_price_per_m / 1_000_000


def _total(messages):
    return sum(estimate_tokens(m["content"]) + MESSAGE_OVERHEAD for m in messages)


def fit_history(messages, max_context, reserve_for_output):
    budget = max_context - reserve_for_output
    system = [messages[0]] if messages and messages[0]["role"] == "system" else []
    rest = list(messages[len(system):])
    while len(rest) > 1 and (_total(system + rest) > budget or rest[0]["role"] == "assistant"):
        rest.pop(0)
    if _total(system + rest) > budget:
        raise ValueError("the system message and the last message do not fit")
    return system + rest


def apply_temperature(logits, temperature):
    if temperature < 0:
        raise ValueError("temperature must be >= 0")
    if temperature == 0:
        best = max(logits, key=lambda k: logits[k])
        return {k: (1.0 if k == best else 0.0) for k in logits}
    top = max(logits.values())
    weights = {k: math.exp((v - top) / temperature) for k, v in logits.items()}
    total = sum(weights.values())
    return {k: w / total for k, w in weights.items()}
