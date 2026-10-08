from collections import deque  # noqa: F401  (you will want it)


def build_graph(edges: list[tuple[int, int]], directed: bool = False) -> dict[int, list[int]]:
    """Adjacency list: node -> sorted list of neighbours.

    Every node that appears in an edge must be a key (even if it has no outgoing edge).
    Duplicate edges count once. For an undirected graph add both directions.
    """
    raise NotImplementedError


def bfs_order(graph: dict[int, list[int]], start: int) -> list[int]:
    """Nodes in the order a breadth-first search reaches them (nearest first).
    Visit neighbours in the order they are listed (they are sorted)."""
    raise NotImplementedError


def dfs_order(graph: dict[int, list[int]], start: int) -> list[int]:
    """Nodes in the order a depth-first search (preorder) reaches them.
    Go to the SMALLEST unvisited neighbour first.

    Must NOT use recursion: the tests give it a path of 50,000 nodes. Use a stack.
    """
    raise NotImplementedError


def has_path(graph: dict[int, list[int]], source: int, target: int) -> bool:
    """Can you get from source to target by following edges? A node reaches itself."""
    raise NotImplementedError
