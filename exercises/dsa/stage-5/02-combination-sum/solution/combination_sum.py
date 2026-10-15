def combination_sum(candidates: list[int], target: int) -> list[list[int]]:
    ordered = sorted(candidates)
    result: list[list[int]] = []
    path: list[int] = []

    def explore(start: int, remaining: int) -> None:
        if remaining == 0:
            result.append(path[:])
            return
        for i in range(start, len(ordered)):
            if ordered[i] > remaining:
                break                        # sorted, so everything after is too big as well
            path.append(ordered[i])
            explore(i, remaining - ordered[i])   # same i: the candidate may be reused
            path.pop()

    explore(0, target)
    return result


def combination_sum_once(candidates: list[int], target: int) -> list[list[int]]:
    ordered = sorted(candidates)
    result: list[list[int]] = []
    path: list[int] = []

    def explore(start: int, remaining: int) -> None:
        if remaining == 0:
            result.append(path[:])
            return
        for i in range(start, len(ordered)):
            if ordered[i] > remaining:
                break
            if i > start and ordered[i] == ordered[i - 1]:
                continue                     # same value, same level -> duplicate combination
            path.append(ordered[i])
            explore(i + 1, remaining - ordered[i])
            path.pop()

    explore(0, target)
    return result


def can_split_into_equal_groups(nums: list[int], k: int) -> bool:
    if k <= 0 or len(nums) < k:
        return False
    total = sum(nums)
    if total % k:
        return False
    group_target = total // k
    ordered = sorted(nums, reverse=True)     # big numbers first: dead ends appear sooner
    if ordered[0] > group_target:
        return False

    groups = [0] * k

    def place(index: int) -> bool:
        if index == len(ordered):
            return True                      # every number found a group
        value = ordered[index]
        seen: set[int] = set()
        for g in range(k):
            if groups[g] in seen:
                continue                     # a group with the same load was already tried
            if groups[g] + value > group_target:
                continue
            seen.add(groups[g])
            groups[g] += value
            if place(index + 1):
                return True
            groups[g] -= value
            if groups[g] == 0:
                break                        # putting it in any other empty group is the same
        return False

    return place(0)
