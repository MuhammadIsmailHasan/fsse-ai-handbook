def count_queen_placements(n: int) -> int:
    """How many ways can n queens stand on an n x n board without attacking each other?

    A queen attacks along her row, her column and both diagonals.

        n=1 -> 1,  n=2 -> 0,  n=3 -> 0,  n=4 -> 2,  n=8 -> 92

    Place one queen per row, so rows can never clash. For columns and diagonals, keep
    three sets instead of scanning the board — a cell (row, col) is attacked when
    col, row + col or row - col is already in one of them. That is what makes n=9 instant.
    """
    raise NotImplementedError


def first_queen_board(n: int) -> list[str] | None:
    """One valid board, or None if there is none.

    Return the solution you find by trying columns left to right in every row, top row
    first — the standard first answer:

        first_queen_board(4) -> [".Q..",
                                 "...Q",
                                 "Q...",
                                 "..Q."]

        first_queen_board(1) -> ["Q"]
        first_queen_board(3) -> None

    Each string is one row: "Q" where the queen stands, "." everywhere else.
    """
    raise NotImplementedError
