"""Stack & queue basics — reference solution."""

PAIRS = {")": "(", "]": "[", "}": "{"}


# Time O(n), space O(n).
def is_balanced(text: str) -> bool:
    stack: list[str] = []
    for char in text:
        if char in "([{":
            stack.append(char)
        elif char in PAIRS:
            if not stack or stack.pop() != PAIRS[char]:
                return False
    return not stack


# Time O(n), space O(n).
def apply_backspaces(text: str) -> str:
    kept: list[str] = []
    for char in text:
        if char == "#":
            if kept:
                kept.pop()
        else:
            kept.append(char)
    return "".join(kept)


class MinStack:
    """Each entry stores (value, minimum so far) — so the minimum is always at the top. All O(1)."""

    def __init__(self) -> None:
        self._items: list[tuple[int, int]] = []

    def push(self, value: int) -> None:
        current_min = min(value, self._items[-1][1]) if self._items else value
        self._items.append((value, current_min))

    def pop(self) -> int:
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()[0]

    def top(self) -> int:
        if not self._items:
            raise IndexError("top of empty stack")
        return self._items[-1][0]

    def get_min(self) -> int:
        if not self._items:
            raise IndexError("min of empty stack")
        return self._items[-1][1]
