# Time O(n): each index enters and leaves the window once. Space O(1).
def longest_affordable(costs: list[int], budget: int) -> int:
    left = total = best = 0
    for right, cost in enumerate(costs):
        total += cost
        while total > budget and left <= right:
            total -= costs[left]
            left += 1
        best = max(best, right - left + 1)
    return best
