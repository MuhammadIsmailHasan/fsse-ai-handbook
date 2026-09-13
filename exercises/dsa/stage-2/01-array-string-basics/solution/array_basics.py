"""Array & string basics — reference solution."""


# Time O(n), space O(n) for the new list.
def rotate_right(nums: list[int], k: int) -> list[int]:
    if not nums:
        return []
    k %= len(nums)
    return nums[-k:] + nums[:-k] if k else nums[:]


# Time O(n), space O(1): a "write" pointer marks where the next non-zero goes.
def move_zeros(nums: list[int]) -> None:
    write = 0
    for read in range(len(nums)):
        if nums[read] != 0:
            nums[write], nums[read] = nums[read], nums[write]
            write += 1


# Time O(n), space O(n).
def compress(text: str) -> str:
    parts: list[str] = []
    i = 0
    while i < len(text):
        j = i
        while j < len(text) and text[j] == text[i]:
            j += 1
        run = j - i
        parts.append(text[i] if run == 1 else f"{text[i]}{run}")
        i = j
    return "".join(parts)
