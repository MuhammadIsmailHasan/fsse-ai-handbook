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


# Time O(L) in a single pass, space O(1).
def remove_nth_from_end(head: ListNode | None, n: int) -> ListNode | None:
    dummy = ListNode(0, head)
    lead: ListNode | None = dummy
    for _ in range(n):
        lead = lead.next  # type: ignore[union-attr]
    trail = dummy
    while lead.next is not None:  # type: ignore[union-attr]
        lead = lead.next  # type: ignore[union-attr]
        trail = trail.next  # type: ignore[assignment]
    trail.next = trail.next.next  # type: ignore[union-attr]
    return dummy.next
