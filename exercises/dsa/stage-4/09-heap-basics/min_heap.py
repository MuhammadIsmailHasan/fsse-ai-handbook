class MinHeap:
    """A min-heap stored in a plain list called `items`.

    For the node at index i:  parent = (i - 1) // 2,  children = 2*i + 1 and 2*i + 2.
    Rule: every parent is <= both of its children. So items[0] is always the smallest.

    Do NOT use the heapq module — build the heap yourself.
    """

    def __init__(self) -> None:
        self.items: list[int] = []

    def __len__(self) -> int:
        raise NotImplementedError

    def peek(self) -> int:
        """Smallest value without removing it. IndexError if empty."""
        raise NotImplementedError

    def push(self, value: int) -> None:
        """Add at the end, then move it UP while it is smaller than its parent. O(log n)."""
        raise NotImplementedError

    def pop(self) -> int:
        """Remove and return the smallest. IndexError if empty.

        Move the last item to the front, then move it DOWN, swapping with the SMALLER child,
        while it is larger than a child. O(log n).
        """
        raise NotImplementedError


def heap_sort(values: list[int]) -> list[int]:
    """Return the values sorted ascending, using MinHeap (push all, pop all)."""
    raise NotImplementedError
