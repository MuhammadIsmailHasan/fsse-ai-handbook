from collections import deque  # noqa: F401


def two_color(n: int, edges: list[tuple[int, int]]) -> list[int] | None:
    """Give each node 0..n-1 the colour 0 or 1 so that every edge joins DIFFERENT colours.
    Return the list of colours, or None if that is impossible (the graph is not bipartite).

    In each connected group, the node with the smallest number gets colour 0.
    A self-loop (u, u) makes it impossible.
    """
    raise NotImplementedError


def is_bipartite(n: int, edges: list[tuple[int, int]]) -> bool:
    raise NotImplementedError


def can_split_into_two_teams(n: int, dislikes: list[tuple[int, int]]) -> bool:
    """People are numbered 1..n. Each pair in `dislikes` cannot be on the same team.
    Can everybody be split into two teams? """
    raise NotImplementedError


def has_odd_cycle(n: int, edges: list[tuple[int, int]]) -> bool:
    """True if the graph contains a cycle with an odd number of nodes (a triangle, a 5-cycle...).
    A graph is bipartite exactly when it has no odd cycle."""
    raise NotImplementedError
