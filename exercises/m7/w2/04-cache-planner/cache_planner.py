"""Module 7 · W2 — How prompt caching behaves (no API key needed).

Prompt caching is a PREFIX match: the provider remembers the beginning of a prompt, and a later request
that starts with exactly the same text can reuse it at a lower price. One changed byte in the prefix
and everything after it is a miss. This exercise simulates that.

A request is:  {"t": seconds_since_start, "blocks": ["tools text", "system text", "context", "question"],
                "breakpoint": index_of_the_last_block_to_cache}   (or "breakpoint": None for no caching)
The prompt is the blocks in order. The cached prefix is blocks[0..breakpoint] (inclusive).
Token count of a block: ceil(len(block) / 4).
"""

import math  # noqa: F401  (you will want it)


def block_tokens(block: str) -> int:
    """ceil(len(block) / 4); an empty block is 0 tokens."""
    raise NotImplementedError


def simulate_cache(requests: list[dict], ttl_s: int = 300, min_tokens: int = 1024) -> list[dict]:
    """Return one dict per request: {"read": n, "write": n, "uncached": n}  (token counts).

    Rules for a request that has a breakpoint:
      prefix = blocks[0..breakpoint]; prefix_tokens = the sum of its block tokens
      - if the SAME prefix (all those blocks, exactly equal) is in the cache and was last used at most ttl_s seconds ago
        (time since its last write OR read; use `t - last_used <= ttl_s`):
            read = prefix_tokens, write = 0, and the entry's last_used becomes t (a read refreshes the timer)
      - else if prefix_tokens >= min_tokens:
            write = prefix_tokens, read = 0, and the prefix is stored with last_used = t
      - else (too short to cache):  read = 0, write = 0
      uncached = the tokens of all blocks AFTER the breakpoint, plus the prefix tokens if the prefix was too short to cache
    A request with breakpoint None: read = write = 0 and uncached = all tokens.
    Requests are given in time order.
    """
    raise NotImplementedError


def first_difference(previous: list[str], current: list[str]) -> int | None:
    """The index of the first block where two prompts differ (a missing block counts as different),
    or None if they are identical. This is where a silent cache invalidator hides:
    everything from this block on cannot be a cache hit."""
    raise NotImplementedError


def prompt_cost(usage: dict, input_price_per_m: float, read_multiplier: float = 0.1, write_multiplier: float = 1.25) -> float:
    """Dollar cost of one request given {"read", "write", "uncached"} tokens:
    read tokens cost read_multiplier x the input price, write tokens write_multiplier x, uncached 1 x.
    Output tokens are not part of this exercise. input_price_per_m is dollars per million tokens."""
    raise NotImplementedError


def cache_savings(requests: list[dict], input_price_per_m: float, ttl_s: int = 300, min_tokens: int = 1024) -> float:
    """Dollars saved by caching: (cost if NOTHING were cached, every token at the normal price)
    minus (cost with the simulated cache). Can be negative when caching does not pay off."""
    raise NotImplementedError
