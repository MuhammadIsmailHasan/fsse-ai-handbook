import math


def block_tokens(block):
    return math.ceil(len(block) / 4)


def simulate_cache(requests, ttl_s=300, min_tokens=1024):
    store = {}
    results = []
    for request in requests:
        t, blocks, bp = request["t"], request["blocks"], request["breakpoint"]
        tokens = [block_tokens(b) for b in blocks]
        if bp is None:
            results.append({"read": 0, "write": 0, "uncached": sum(tokens)})
            continue
        key = tuple(blocks[: bp + 1])
        prefix_tokens = sum(tokens[: bp + 1])
        after = sum(tokens[bp + 1 :])
        last = store.get(key)
        if last is not None and t - last <= ttl_s:
            store[key] = t
            results.append({"read": prefix_tokens, "write": 0, "uncached": after})
        elif prefix_tokens >= min_tokens:
            store[key] = t
            results.append({"read": 0, "write": prefix_tokens, "uncached": after})
        else:
            results.append({"read": 0, "write": 0, "uncached": after + prefix_tokens})
    return results


def first_difference(previous, current):
    for i in range(max(len(previous), len(current))):
        if i >= len(previous) or i >= len(current) or previous[i] != current[i]:
            return i
    return None


def prompt_cost(usage, input_price_per_m, read_multiplier=0.1, write_multiplier=1.25):
    weighted = usage["read"] * read_multiplier + usage["write"] * write_multiplier + usage["uncached"]
    return weighted * input_price_per_m / 1_000_000


def cache_savings(requests, input_price_per_m, ttl_s=300, min_tokens=1024):
    plain = sum(sum(block_tokens(b) for b in r["blocks"]) for r in requests) * input_price_per_m / 1_000_000
    cached = sum(prompt_cost(u, input_price_per_m) for u in simulate_cache(requests, ttl_s, min_tokens))
    return plain - cached
