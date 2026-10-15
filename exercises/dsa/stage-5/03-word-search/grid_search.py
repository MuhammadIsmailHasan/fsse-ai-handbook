def exists(board: list[list[str]], word: str) -> bool:
    """True if word can be spelled by walking the grid one step at a time.

    Steps go up, down, left or right — never diagonally — and the same cell may not be
    used twice in one word.

        board = [["C", "A", "T"],
                 ["X", "R", "E"],
                 ["Y", "Z", "D"]]

        exists(board, "CARED") -> True    # C(0,0) A(0,1) R(1,1) E(1,2) D(2,2)
        exists(board, "CRY")   -> False   # C and R only touch diagonally

    The method: start a search from every cell whose letter matches word[0], then walk.
    Mark the cell as visited before you step away and un-mark it when you come back —
    that un-mark is the backtracking. Leave the board as you found it.
    """
    raise NotImplementedError


def find_words(board: list[list[str]], words: list[str]) -> list[str]:
    """Every word from the list that `exists` in the board, sorted alphabetically, no repeats."""
    raise NotImplementedError


def count_routes(grid: list[list[str]]) -> int:
    """Count routes from 'S' to 'E' that step on every open cell exactly once.

    Cells: 'S' start, 'E' end, '.' open, '#' blocked. Steps are up/down/left/right.
    A route counts only if it covers **all** non-blocked cells with no repeats.

        [["S", "."],
         ["E", "."]] -> 1        # right, down, left: all four cells, ending on E

    Return 0 when no such route exists. This one has no clever shortcut — it is a full
    search, which is exactly why interviewers use it to watch you un-mark state correctly.
    """
    raise NotImplementedError
