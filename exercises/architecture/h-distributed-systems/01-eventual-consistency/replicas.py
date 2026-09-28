"""Architecture · H — Diverge during a partition, then converge.

Two replicas take writes independently while they can't talk (a partition),
then merge when the network heals.

- Values use last-write-wins (LWW): the newer timestamp wins. Simple, but a
  concurrent edit on the other side can be lost.
- Counters use an ADDITIVE merge: both sides' increments are summed, so no
  increment is ever lost.

A value entry is a tuple: (value, timestamp).
"""


def apply(state: dict, key: str, value, ts: int) -> None:
    """Write (value, ts) into state[key] only if ts is newer than what's there."""
    # YOUR CODE HERE
    return None


def merge_lww(a: dict, b: dict) -> dict:
    """Merge two value-stores with last-write-wins.

    For each key present in either store, keep the entry with the larger ts.
    Tie-break deterministically: on equal ts, keep the larger value.
    Return a NEW dict; don't mutate a or b.
    """
    # YOUR CODE HERE
    return {}


def merge_counter(a: dict[str, int], b: dict[str, int]) -> dict[str, int]:
    """Merge two counter-stores by SUMMING each key's increments.

    a and b map key -> increments recorded on that replica during the partition.
    The converged value for a key is the sum from both sides.
    """
    # YOUR CODE HERE
    return {}
