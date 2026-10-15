def combination_sum(candidates: list[int], target: int) -> list[list[int]]:
    """All combinations of candidates that add up to target. Each candidate may be reused.

    combination_sum([2, 3, 5], 8) -> [[2, 2, 2, 2], [2, 3, 3], [3, 5]]

    Candidates are distinct positive numbers. The order of the outer list does not matter,
    but each combination must be in non-decreasing order, so [3, 3, 2] and [2, 3, 3] are the
    same answer and must appear only once.

    To allow reuse, recurse with the *same* index instead of index + 1.
    """
    raise NotImplementedError


def combination_sum_once(candidates: list[int], target: int) -> list[list[int]]:
    """Same, but each element of candidates may be used at most once.

    candidates may contain repeated values, and the result must not repeat a combination.

    combination_sum_once([10, 1, 2, 7, 6, 1, 5], 8)
        -> [[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]

    Sort first, then skip a candidate equal to the previous one at the same level.
    """
    raise NotImplementedError


def can_split_into_equal_groups(nums: list[int], k: int) -> bool:
    """True if nums can be split into exactly k groups that all have the same sum.

    can_split_into_equal_groups([4, 3, 2, 3, 5, 2, 1], 4) -> True
        total 20, so each group must be 5:  [5] [4, 1] [3, 2] [3, 2]

    can_split_into_equal_groups([1, 2, 3, 4], 3) -> False
        total 10 does not divide by 3

    nums holds positive numbers. Pruning is the whole point here — a plain search is far
    too slow. Ideas: give up at once if the total does not divide by k, or if the largest
    number is bigger than one group's target; sort big-to-small so bad branches die early;
    fill one group at a time and only start the next group when the current one is exact;
    skip a number equal to one you already rejected at the same position.
    """
    raise NotImplementedError
