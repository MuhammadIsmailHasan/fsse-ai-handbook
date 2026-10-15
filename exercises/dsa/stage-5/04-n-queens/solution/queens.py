def count_queen_placements(n: int) -> int:
    if n <= 0:
        return 0
    columns: set[int] = set()
    rising: set[int] = set()        # row + col is the same along one diagonal
    falling: set[int] = set()       # row - col is the same along the other

    def place(row: int) -> int:
        if row == n:
            return 1                # all rows filled: one complete solution
        found = 0
        for col in range(n):
            if col in columns or row + col in rising or row - col in falling:
                continue            # attacked, so this branch is dead
            columns.add(col)
            rising.add(row + col)
            falling.add(row - col)
            found += place(row + 1)
            columns.remove(col)     # un-choose
            rising.remove(row + col)
            falling.remove(row - col)
        return found

    return place(0)


def first_queen_board(n: int) -> list[str] | None:
    if n <= 0:
        return None
    columns: set[int] = set()
    rising: set[int] = set()
    falling: set[int] = set()
    chosen: list[int] = []

    def place(row: int) -> bool:
        if row == n:
            return True
        for col in range(n):        # left to right, so the first answer found is the standard one
            if col in columns or row + col in rising or row - col in falling:
                continue
            columns.add(col)
            rising.add(row + col)
            falling.add(row - col)
            chosen.append(col)
            if place(row + 1):
                return True         # stop at the first full board
            chosen.pop()
            columns.remove(col)
            rising.remove(row + col)
            falling.remove(row - col)
        return False

    if not place(0):
        return None
    return ["." * col + "Q" + "." * (n - col - 1) for col in chosen]
