"""Architecture · F — Shard router and the resharding cost (solution)."""

import hashlib

READS = {"read", "select", "get"}
WRITES = {"write", "insert", "update", "delete"}


def stable_hash(key) -> int:
    return int(hashlib.md5(str(key).encode()).hexdigest(), 16)


def shard_for(key, num_shards: int) -> int:
    return stable_hash(key) % num_shards


def route(operation: str) -> str:
    op = operation.lower()
    if op in WRITES:
        return "primary"
    if op in READS:
        return "replica"
    raise ValueError(f"unknown operation: {operation}")


def keys_moved_on_resize(keys: list, old_n: int, new_n: int) -> int:
    return sum(1 for key in keys if shard_for(key, old_n) != shard_for(key, new_n))
