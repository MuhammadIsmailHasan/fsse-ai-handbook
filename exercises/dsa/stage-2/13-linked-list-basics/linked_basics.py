"""Linked list basics. See README.md."""

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


def reverse_list(head: ListNode | None) -> ListNode | None:
    raise NotImplementedError


def middle_node(head: ListNode | None) -> ListNode | None:
    raise NotImplementedError


def has_cycle(head: ListNode | None) -> bool:
    raise NotImplementedError
