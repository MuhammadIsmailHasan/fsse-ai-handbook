def subsets(nums: list[int]) -> list[list[int]]:
    """Every subset of nums (the power set). Order of the result does not matter.

    [1, 2] -> [[], [1], [1, 2], [2]]  (4 subsets, 2**n in total)

    At each index you make one decision: take this number, or skip it.
    Remember to append a *copy* of the current path, not the path itself.
    """
    raise NotImplementedError


def subsets_no_duplicates(nums: list[int]) -> list[list[int]]:
    """Every *distinct* subset when nums can contain repeated numbers.

    [1, 2, 2] -> [[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]  (6, not 8)

    Sort first. Inside the loop, skip a candidate that equals the previous one
    at the same level, so the same shape is never built twice.
    """
    raise NotImplementedError


def permutations(nums: list[int]) -> list[list[int]]:
    """Every order of all the numbers. n! results.

    [1, 2, 3] -> 6 lists, each containing 1, 2 and 3 exactly once.

    Track which positions you already used.
    """
    raise NotImplementedError


def permutations_no_duplicates(nums: list[int]) -> list[list[int]]:
    """Every *distinct* order when nums can contain repeated numbers.

    [1, 1, 2] -> [[1, 1, 2], [1, 2, 1], [2, 1, 1]]  (3, not 6)
    """
    raise NotImplementedError
