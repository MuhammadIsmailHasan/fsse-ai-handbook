# Time O(n), space O(n).
def longest_balanced(visits: list[int]) -> int:
    first_index = {0: -1}  # prefix sum -> earliest index where it occurred (before any element: -1)
    prefix = best = 0
    for i, visit in enumerate(visits):
        prefix += 1 if visit == 1 else -1
        if prefix in first_index:
            best = max(best, i - first_index[prefix])
        else:
            first_index[prefix] = i
    return best
