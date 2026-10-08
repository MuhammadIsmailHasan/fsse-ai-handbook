import heapq  # noqa: F401


def dijkstra(graph: dict[int, list[tuple[int, int]]], source: int) -> dict[int, int]:
    """Cheapest cost from source to every node it can reach (source: 0).

    graph: node -> list of (neighbour, weight). Weights are zero or positive. Directed.
    Use a min-heap of (cost_so_far, node). When you pop a node you have already finished,
    skip it ("lazy deletion").
    """
    raise NotImplementedError


def cheapest_route(graph: dict[int, list[tuple[int, int]]], start: int, goal: int) -> tuple[int, list[int]] | None:
    """(total cost, [start, ..., goal]) of one cheapest route, or None if goal is unreachable."""
    raise NotImplementedError


def network_delay_time(times: list[tuple[int, int, int]], n: int, k: int) -> int:
    """A signal starts at node k (nodes are 1..n). times has directed edges (u, v, travel_time).
    How long until ALL nodes have received it? Return -1 if some node never does."""
    raise NotImplementedError
