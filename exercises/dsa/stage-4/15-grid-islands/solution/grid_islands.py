def _components(grid):
    rows, cols = len(grid), len(grid[0]) if grid else 0
    seen = [[False] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and not seen[r][c]:
                seen[r][c] = True
                stack, size = [(r, c)], 0
                while stack:
                    x, y = stack.pop()
                    size += 1
                    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                        if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] == "1" and not seen[nx][ny]:
                            seen[nx][ny] = True
                            stack.append((nx, ny))
                yield size


def count_islands(grid):
    return sum(1 for _ in _components(grid))


def max_island_area(grid):
    return max(_components(grid), default=0)


def flood_fill(image, row, col, color):
    result = [list(r) for r in image]
    old = result[row][col]
    if old == color:
        return result
    stack = [(row, col)]
    result[row][col] = color
    while stack:
        x, y = stack.pop()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < len(result) and 0 <= ny < len(result[0]) and result[nx][ny] == old:
                result[nx][ny] = color
                stack.append((nx, ny))
    return result
