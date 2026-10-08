from collections import deque  # noqa: F401


def distances_from(graph: dict[int, list[int]], start: int) -> dict[int, int]:
    """Number of edges from start to every node it can reach (start itself: 0).
    Unreachable nodes are not in the result."""
    raise NotImplementedError


def shortest_path_length(graph: dict[int, list[int]], start: int, goal: int) -> int:
    """Fewest edges from start to goal, or -1 if goal cannot be reached."""
    raise NotImplementedError


def shortest_path(graph: dict[int, list[int]], start: int, goal: int) -> list[int] | None:
    """One shortest path as a list of nodes [start, ..., goal], or None if there is none.
    If several shortest paths exist, any one is fine."""
    raise NotImplementedError


def word_ladder_length(begin: str, end: str, words: list[str]) -> int:
    """Fewest words in a chain begin -> ... -> end where each step changes exactly ONE letter
    and every word after `begin` must be in `words`. Count both ends (begin, end alone = 2).
    Return 0 if there is no chain.

    Hint: the words are the nodes; neighbours differ by one letter. Do not compare every pair
    of words (the test has 5,000 words): try replacing each position with 'a'..'z' instead.
    """
    raise NotImplementedError
