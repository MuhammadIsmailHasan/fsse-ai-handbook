import random
import time

from grid_islands import count_islands, flood_fill, max_island_area

MAP = [
    "11000",
    "11000",
    "00100",
    "00011",
]


def test_count_islands_examples():
    assert count_islands(MAP) == 3
    assert count_islands(["111", "010", "111"]) == 1
    assert count_islands(["101", "010", "101"]) == 5        # diagonals do NOT connect
    assert count_islands(["000"]) == 0


def test_empty_inputs():
    assert count_islands([]) == 0
    assert max_island_area([]) == 0
    assert max_island_area(["000", "000"]) == 0


def test_max_island_area():
    assert max_island_area(MAP) == 4
    assert max_island_area(["1"]) == 1


def test_max_island_area_exact():
    grid = ["1011", "1001", "0111"]
    # land: (0,0),(1,0) | (0,2),(0,3),(1,3),(2,3),(2,2),(2,1)
    assert max_island_area(grid) == 6


def test_input_is_not_changed():
    grid = list(MAP)
    count_islands(grid)
    max_island_area(grid)
    assert grid == MAP


def brute_islands(grid):
    cells = {(r, c) for r, row in enumerate(grid) for c, ch in enumerate(row) if ch == "1"}
    sizes = []
    while cells:
        stack = [cells.pop()]
        size = 1
        while stack:
            x, y = stack.pop()
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if n in cells:
                    cells.remove(n)
                    stack.append(n)
                    size += 1
        sizes.append(size)
    return sizes


def test_random_grids():
    rng = random.Random(121)
    for _ in range(200):
        rows, cols = rng.randint(1, 8), rng.randint(1, 8)
        grid = ["".join(rng.choice("0011") for _ in range(cols)) for _ in range(rows)]
        sizes = brute_islands(grid)
        assert count_islands(grid) == len(sizes)
        assert max_island_area(grid) == max(sizes, default=0)


def test_huge_all_land_grid_needs_no_recursion():
    grid = ["1" * 500 for _ in range(500)]
    started = time.perf_counter()
    assert count_islands(grid) == 1
    assert max_island_area(grid) == 250_000
    assert time.perf_counter() - started < 3.0


def test_flood_fill_example():
    image = [[1, 1, 1], [1, 1, 0], [1, 0, 1]]
    assert flood_fill(image, 1, 1, 2) == [[2, 2, 2], [2, 2, 0], [2, 0, 1]]


def test_flood_fill_does_not_change_the_input():
    image = [[1, 1], [1, 0]]
    result = flood_fill(image, 0, 0, 5)
    assert image == [[1, 1], [1, 0]]
    assert result == [[5, 5], [5, 0]]


def test_flood_fill_same_colour_is_a_copy():
    image = [[3, 3], [0, 3]]
    result = flood_fill(image, 0, 0, 3)
    assert result == image and result is not image


def test_flood_fill_stays_inside_its_region():
    image = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
    assert flood_fill(image, 0, 0, 9) == [[9, 1, 0], [1, 0, 1], [0, 1, 0]]


def test_flood_fill_on_a_big_image():
    image = [[0] * 400 for _ in range(400)]
    started = time.perf_counter()
    result = flood_fill(image, 200, 200, 1)
    assert all(v == 1 for row in result for v in row)
    assert time.perf_counter() - started < 3.0
