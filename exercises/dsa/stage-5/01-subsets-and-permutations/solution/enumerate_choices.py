def subsets(nums: list[int]) -> list[list[int]]:
    result: list[list[int]] = []
    path: list[int] = []

    def explore(start: int) -> None:
        result.append(path[:])              # every node of the tree is a valid subset
        for i in range(start, len(nums)):
            path.append(nums[i])            # choose
            explore(i + 1)                  # explore
            path.pop()                      # un-choose

    explore(0)
    return result


def subsets_no_duplicates(nums: list[int]) -> list[list[int]]:
    ordered = sorted(nums)
    result: list[list[int]] = []
    path: list[int] = []

    def explore(start: int) -> None:
        result.append(path[:])
        for i in range(start, len(ordered)):
            if i > start and ordered[i] == ordered[i - 1]:
                continue                    # same value, same level -> same subset shape
            path.append(ordered[i])
            explore(i + 1)
            path.pop()

    explore(0)
    return result


def permutations(nums: list[int]) -> list[list[int]]:
    result: list[list[int]] = []
    path: list[int] = []
    used = [False] * len(nums)

    def explore() -> None:
        if len(path) == len(nums):
            result.append(path[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True
            path.append(nums[i])
            explore()
            path.pop()
            used[i] = False

    explore()
    return result


def permutations_no_duplicates(nums: list[int]) -> list[list[int]]:
    ordered = sorted(nums)
    result: list[list[int]] = []
    path: list[int] = []
    used = [False] * len(ordered)

    def explore() -> None:
        if len(path) == len(ordered):
            result.append(path[:])
            return
        for i in range(len(ordered)):
            if used[i]:
                continue
            if i > 0 and ordered[i] == ordered[i - 1] and not used[i - 1]:
                continue                    # the equal twin before me has not been placed yet
            used[i] = True
            path.append(ordered[i])
            explore()
            path.pop()
            used[i] = False

    explore()
    return result
