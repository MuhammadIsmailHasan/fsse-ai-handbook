class RegionSums:
    """2D prefix sums: O(rows × cols) to build, O(1) per query."""

    def __init__(self, grid: list[list[int]]):
        rows = len(grid)
        cols = len(grid[0]) if grid else 0
        self._prefix = [[0] * (cols + 1) for _ in range(rows + 1)]
        for r in range(rows):
            for c in range(cols):
                self._prefix[r + 1][c + 1] = grid[r][c] + self._prefix[r][c + 1] + self._prefix[r + 1][c] - self._prefix[r][c]

    def total(self, r1: int, c1: int, r2: int, c2: int) -> int:
        p = self._prefix
        return p[r2 + 1][c2 + 1] - p[r1][c2 + 1] - p[r2 + 1][c1] + p[r1][c1]
