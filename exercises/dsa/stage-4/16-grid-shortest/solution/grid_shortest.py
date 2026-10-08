from collections import deque

DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def maze_steps(maze, start, end):
    rows, cols = len(maze), len(maze[0]) if maze else 0
    (sr, sc), (er, ec) = start, end
    if maze[sr][sc] == "#" or maze[er][ec] == "#":
        return -1
    dist = {start: 0}
    queue = deque([start])
    while queue:
        r, c = queue.popleft()
        if (r, c) == end:
            return dist[(r, c)]
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] != "#" and (nr, nc) not in dist:
                dist[(nr, nc)] = dist[(r, c)] + 1
                queue.append((nr, nc))
    return -1


def rotting_oranges(grid):
    g = [list(r) for r in grid]
    queue = deque((r, c) for r in range(len(g)) for c in range(len(g[0])) if g[r][c] == 2)
    fresh = sum(row.count(1) for row in g)
    minutes = 0
    while queue and fresh:
        for _ in range(len(queue)):
            r, c = queue.popleft()
            for dr, dc in DIRS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < len(g) and 0 <= nc < len(g[0]) and g[nr][nc] == 1:
                    g[nr][nc] = 2
                    fresh -= 1
                    queue.append((nr, nc))
        minutes += 1
    return -1 if fresh else minutes


def nearest_zero(matrix):
    rows, cols = len(matrix), len(matrix[0])
    dist = [[-1] * cols for _ in range(rows)]
    queue = deque()
    for r in range(rows):
        for c in range(cols):
            if matrix[r][c] == 0:
                dist[r][c] = 0
                queue.append((r, c))
    while queue:
        r, c = queue.popleft()
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                queue.append((nr, nc))
    return dist
