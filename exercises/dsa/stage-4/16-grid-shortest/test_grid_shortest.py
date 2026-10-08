import random
import time

from grid_shortest import maze_steps, nearest_zero, rotting_oranges

MAZE = [
    "..#....",
    ".##.##.",
    "....#..",
    ".##...#",
    "...#...",
]


def test_maze_examples():
    assert maze_steps(MAZE, (0, 0), (0, 0)) == 0
    assert maze_steps(MAZE, (0, 0), (2, 3)) == 5
    assert maze_steps(MAZE, (0, 0), (4, 6)) == 10


def test_maze_unreachable_and_walls():
    blocked = ["..#.", "..#.", "..#."]
    assert maze_steps(blocked, (0, 0), (0, 3)) == -1
    assert maze_steps(MAZE, (0, 2), (0, 0)) == -1       # start is a wall
    assert maze_steps(MAZE, (0, 0), (0, 2)) == -1       # end is a wall


def test_maze_matches_brute_force():
    rng = random.Random(131)
    for _ in range(100):
        rows, cols = rng.randint(1, 6), rng.randint(1, 6)
        maze = ["".join(rng.choice("..#") for _ in range(cols)) for _ in range(rows)]
        start = (rng.randrange(rows), rng.randrange(cols))
        end = (rng.randrange(rows), rng.randrange(cols))
        # Bellman-Ford style relaxation as an independent check
        INF = 10**9
        d = {(r, c): INF for r in range(rows) for c in range(cols) if maze[r][c] != "#"}
        if start in d:
            d[start] = 0
        for _ in range(rows * cols):
            for (r, c), v in list(d.items()):
                for n in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                    if n in d and d[n] + 1 < v:
                        v = d[n] + 1
                d[(r, c)] = v
        expected = d.get(end, INF)
        assert maze_steps(maze, start, end) == (expected if expected < INF else -1)


def test_maze_big_open_grid():
    maze = ["." * 400 for _ in range(400)]
    started = time.perf_counter()
    assert maze_steps(maze, (0, 0), (399, 399)) == 798
    assert time.perf_counter() - started < 3.0


def test_rotting_oranges_examples():
    assert rotting_oranges([[2, 1, 1], [1, 1, 0], [0, 1, 1]]) == 4
    assert rotting_oranges([[2, 1, 1], [0, 1, 1], [1, 0, 1]]) == -1
    assert rotting_oranges([[0, 2]]) == 0
    assert rotting_oranges([[0]]) == 0


def test_rotting_starts_from_all_rotten_oranges_at_once():
    assert rotting_oranges([[2, 1, 1, 1, 2]]) == 2
    assert rotting_oranges([[2, 1, 1, 1, 1, 1, 2]]) == 3


def test_rotting_does_not_change_the_input():
    grid = [[2, 1], [1, 1]]
    rotting_oranges(grid)
    assert grid == [[2, 1], [1, 1]]


def test_fresh_oranges_with_no_rotten_one():
    assert rotting_oranges([[1, 1]]) == -1


def test_nearest_zero_examples():
    assert nearest_zero([[0, 0, 0], [0, 1, 0], [1, 1, 1]]) == [[0, 0, 0], [0, 1, 0], [1, 2, 1]]
    assert nearest_zero([[0]]) == [[0]]
    assert nearest_zero([[1, 1, 0]]) == [[2, 1, 0]]


def test_nearest_zero_matches_brute_force():
    rng = random.Random(132)
    for _ in range(150):
        rows, cols = rng.randint(1, 7), rng.randint(1, 7)
        m = [[rng.choice([0, 1, 1]) for _ in range(cols)] for _ in range(rows)]
        m[rng.randrange(rows)][rng.randrange(cols)] = 0
        zeros = [(r, c) for r in range(rows) for c in range(cols) if m[r][c] == 0]
        expected = [[min(abs(r - zr) + abs(c - zc) for zr, zc in zeros) for c in range(cols)] for r in range(rows)]
        assert nearest_zero(m) == expected


def test_nearest_zero_big_matrix():
    n = 300
    m = [[1] * n for _ in range(n)]
    m[0][0] = 0
    started = time.perf_counter()
    result = nearest_zero(m)
    assert result[n - 1][n - 1] == 2 * (n - 1)
    assert time.perf_counter() - started < 3.0
