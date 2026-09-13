# Time O(n) in one pass, space O(1).
# Invariant: tasks[:low] == "high", tasks[low:mid] == "medium", tasks[mid:high + 1] unknown, tasks[high + 1:] == "low".
def sort_priorities(tasks: list[str]) -> None:
    low, mid, high = 0, 0, len(tasks) - 1
    while mid <= high:
        if tasks[mid] == "high":
            tasks[low], tasks[mid] = tasks[mid], tasks[low]
            low += 1
            mid += 1
        elif tasks[mid] == "medium":
            mid += 1
        else:
            tasks[mid], tasks[high] = tasks[high], tasks[mid]
            high -= 1  # don't advance mid: the swapped-in item is still unknown
