# Time O(rows × cols), space O(rows × cols) for the output.
def spiral_order(matrix: list[list[int]]) -> list[int]:
    if not matrix or not matrix[0]:
        return []
    top, bottom, left, right = 0, len(matrix) - 1, 0, len(matrix[0]) - 1
    result: list[int] = []
    while top <= bottom and left <= right:
        result.extend(matrix[top][c] for c in range(left, right + 1))
        top += 1
        result.extend(matrix[r][right] for r in range(top, bottom + 1))
        right -= 1
        if top <= bottom:
            result.extend(matrix[bottom][c] for c in range(right, left - 1, -1))
            bottom -= 1
        if left <= right:
            result.extend(matrix[r][left] for r in range(bottom, top - 1, -1))
            left += 1
    return result
