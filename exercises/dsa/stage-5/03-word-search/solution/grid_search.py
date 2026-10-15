def exists(board: list[list[str]], word: str) -> bool:
    if not word:
        return True
    if not board or not board[0]:
        return False
    rows, cols = len(board), len(board[0])

    def walk(row: int, col: int, index: int) -> bool:
        if index == len(word):
            return True
        if not (0 <= row < rows and 0 <= col < cols):
            return False
        if board[row][col] != word[index]:
            return False
        board[row][col] = "\0"                       # mark: this cell is on the current path
        found = (
            walk(row + 1, col, index + 1)
            or walk(row - 1, col, index + 1)
            or walk(row, col + 1, index + 1)
            or walk(row, col - 1, index + 1)
        )
        board[row][col] = word[index]                # un-mark on the way back
        return found

    return any(walk(r, c, 0) for r in range(rows) for c in range(cols))


def find_words(board: list[list[str]], words: list[str]) -> list[str]:
    return sorted({word for word in words if exists(board, word)})


def count_routes(grid: list[list[str]]) -> int:
    rows, cols = len(grid), len(grid[0])
    start = end = None
    open_cells = 0
    for r in range(rows):
        for c in range(cols):
            cell = grid[r][c]
            if cell != "#":
                open_cells += 1
            if cell == "S":
                start = (r, c)
            elif cell == "E":
                end = (r, c)
    if start is None or end is None:
        return 0

    visited = [[False] * cols for _ in range(rows)]
    total = 0

    def walk(row: int, col: int, stepped: int) -> None:
        nonlocal total
        if not (0 <= row < rows and 0 <= col < cols):
            return
        if grid[row][col] == "#" or visited[row][col]:
            return
        if (row, col) == end:
            if stepped + 1 == open_cells:             # reached the end having covered everything
                total += 1
            return
        visited[row][col] = True
        walk(row + 1, col, stepped + 1)
        walk(row - 1, col, stepped + 1)
        walk(row, col + 1, stepped + 1)
        walk(row, col - 1, stepped + 1)
        visited[row][col] = False

    walk(start[0], start[1], 0)
    return total
