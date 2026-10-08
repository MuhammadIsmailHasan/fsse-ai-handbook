import heapq  # noqa: F401  (you may use it)
from collections import deque  # noqa: F401


def topo_order(n: int, edges: list[tuple[int, int]]) -> list[int] | None:
    """Order the nodes 0..n-1 so that for every edge (a, b), a comes BEFORE b.
    (a -> b means "a must be done first".)

    If several nodes are ready at the same time, take the SMALLEST number first.
    If the graph has a cycle there is no valid order: return None.

    Kahn's algorithm: count the incoming edges (in-degree) of each node; start with the nodes
    that have none; each time you take a node, lower the count of the nodes it points to.
    """
    raise NotImplementedError


def can_finish(num_courses: int, prerequisites: list[tuple[int, int]]) -> bool:
    """prerequisites has pairs (course, needs) meaning "to take `course` you must first take `needs`".
    True if all the courses can be taken (there is no circular requirement)."""
    raise NotImplementedError


def min_semesters(n: int, edges: list[tuple[int, int]]) -> int:
    """If you can do any number of ready tasks at the same time, how many ROUNDS are needed?
    Edge (a, b): a must be done in an earlier round than b. Return -1 if there is a cycle.
    No tasks (n = 0): 0."""
    raise NotImplementedError
