def count_islands(grid: list[str]) -> int:
    """Count the islands in a map. '1' is land, '0' is water.
    Land cells touching up, down, left or right (not diagonally) belong to the same island.

    Must NOT use recursion: the tests give it a 500 x 500 grid that is all land.
    Do not change the input.
    """
    raise NotImplementedError


def max_island_area(grid: list[str]) -> int:
    """Size (number of cells) of the biggest island. 0 if there is no land."""
    raise NotImplementedError


def flood_fill(image: list[list[int]], row: int, col: int, color: int) -> list[list[int]]:
    """Paint-bucket tool: change the cell at (row, col) and every connected cell (up/down/left/right)
    that has the SAME starting colour to `color`. Return a NEW image; do not change the input.
    If the colour is already `color`, return a copy unchanged."""
    raise NotImplementedError
