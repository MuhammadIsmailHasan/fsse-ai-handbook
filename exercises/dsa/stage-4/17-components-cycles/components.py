class UnionFind:
    """Groups of nodes 0..n-1. Start with every node alone.

    find(x)      the representative ("leader") of x's group; use PATH COMPRESSION
    union(a, b)  merge the groups of a and b; return True if they were different groups,
                 False if they were already together
    count        how many groups there are right now

    Must be fast for 200,000 nodes in a long chain: no recursion in find.
    """

    def __init__(self, n: int) -> None:
        raise NotImplementedError

    def find(self, x: int) -> int:
        raise NotImplementedError

    def union(self, a: int, b: int) -> bool:
        raise NotImplementedError


def count_components(n: int, edges: list[tuple[int, int]]) -> int:
    """Number of connected groups in an undirected graph with nodes 0..n-1.
    A node with no edges is its own group."""
    raise NotImplementedError


def has_cycle(n: int, edges: list[tuple[int, int]]) -> bool:
    """Does an undirected graph contain a cycle? A self-loop (u, u) and a repeated edge
    (the same pair twice) both count as cycles."""
    raise NotImplementedError


def is_valid_tree(n: int, edges: list[tuple[int, int]]) -> bool:
    """A tree is connected and has no cycle. (n = 0 is not a tree; n = 1 with no edges is.)"""
    raise NotImplementedError
