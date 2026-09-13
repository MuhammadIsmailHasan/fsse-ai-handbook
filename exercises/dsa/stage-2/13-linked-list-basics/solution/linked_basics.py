"""Linked list basics — reference solution."""

from dataclasses import dataclass


@dataclass(eq=False)
class ListNode:
    val: int
    next: "ListNode | None" = None


def from_list(values: list[int]) -> ListNode | None:
    """Provided: [1, 2, 3] -> 1 -> 2 -> 3."""
    head: ListNode | None = None
    for value in reversed(values):
        head = ListNode(value, head)
    return head


def to_list(head: ListNode | None, limit: int = 1_000_000) -> list[int]:
    """Provided: 1 -> 2 -> 3 -> [1, 2, 3]. Raises if the list looks cyclic."""
    values = []
    while head is not None:
        values.append(head.val)
        if len(values) > limit:
            raise RuntimeError("list is longer than limit — is there a cycle?")
        head = head.next
    return values


# Time O(n), space O(1).
def reverse_list(head: ListNode | None) -> ListNode | None:
    previous = None
    current = head
    while current is not None:
        following = current.next
        current.next = previous
        previous = current
        current = following
    return previous


# Time O(n), space O(1): fast moves 2 steps for every 1 step of slow.
def middle_node(head: ListNode | None) -> ListNode | None:
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next  # type: ignore[union-attr]
        fast = fast.next.next
    return slow


# Time O(n), space O(1): Floyd's tortoise and hare.
def has_cycle(head: ListNode | None) -> bool:
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next  # type: ignore[union-attr]
        fast = fast.next.next
        if slow is fast:
            return True
    return False
