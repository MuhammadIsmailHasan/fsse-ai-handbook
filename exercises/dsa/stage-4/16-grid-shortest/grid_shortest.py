from collections import deque  # noqa: F401


def maze_steps(maze: list[str], start: tuple[int, int], end: tuple[int, int]) -> int:
    """Fewest moves (up/down/left/right) from start to end in a maze, or -1 if you cannot get there.
    '#' is a wall, '.' is free. start and end are (row, col). start == end -> 0.
    A wall at start or end -> -1."""
    raise NotImplementedError


def rotting_oranges(grid: list[list[int]]) -> int:
    """0 = empty, 1 = fresh orange, 2 = rotten orange.
    Every minute, a fresh orange next to (up/down/left/right) a rotten one becomes rotten.
    Return the minutes until no fresh orange is left, or -1 if some fresh orange can never rot.
    No fresh oranges at the start: 0.

    Idea: start the BFS from ALL rotten oranges at once ("multi-source" BFS).
    Do not change the input.
    """
    raise NotImplementedError


def nearest_zero(matrix: list[list[int]]) -> list[list[int]]:
    """For every cell, the distance (up/down/left/right moves) to the nearest 0.
    Matrix of 0s and 1s with at least one 0. Return a new matrix.

    Do NOT run a BFS from every cell (the test matrix is 300 x 300). Start ONE BFS from all the
    zeros at the same time.
    """
    raise NotImplementedError
