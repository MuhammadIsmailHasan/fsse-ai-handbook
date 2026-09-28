"""Architecture · F — Shard router and the resharding cost.

- shard_for: pick a shard for a key with a STABLE hash (same every run).
- route: writes go to the primary, reads go to a replica.
- keys_moved_on_resize: how many keys change shard when N -> new_N.
  Naive `hash % n` moves MOST keys on a resize — the reason real systems
  use consistent hashing instead.
"""

import hashlib


def stable_hash(key) -> int:
    """A deterministic integer hash of the key (unlike Python's salted hash())."""
    return int(hashlib.md5(str(key).encode()).hexdigest(), 16)


def shard_for(key, num_shards: int) -> int:
    """Return the shard index in range [0, num_shards) for this key."""
    # YOUR CODE HERE
    return -1


def route(operation: str) -> str:
    """Return "primary" for writes, "replica" for reads.

    Reads: "read", "select", "get".  Writes: "write", "insert", "update", "delete".
    """
    # YOUR CODE HERE
    return ""


def keys_moved_on_resize(keys: list, old_n: int, new_n: int) -> int:
    """Count how many keys land on a different shard when going old_n -> new_n."""
    # YOUR CODE HERE
    return -1
