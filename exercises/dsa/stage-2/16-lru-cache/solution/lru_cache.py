class _Node:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key=None, value=None):
        self.key, self.value = key, value
        self.prev: _Node | None = None
        self.next: _Node | None = None


class LRUCache:
    """dict: key -> node (O(1) find). Doubly linked list: most recent next to head, least recent next to tail (O(1) move/remove)."""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self._nodes: dict = {}
        self._head, self._tail = _Node(), _Node()  # sentinels: no None checks at the edges
        self._head.next, self._tail.prev = self._tail, self._head

    def _unlink(self, node: _Node) -> None:
        node.prev.next, node.next.prev = node.next, node.prev  # type: ignore[union-attr]

    def _push_front(self, node: _Node) -> None:
        node.prev, node.next = self._head, self._head.next
        self._head.next.prev = node  # type: ignore[union-attr]
        self._head.next = node

    def get(self, key):
        node = self._nodes.get(key)
        if node is None:
            return None
        self._unlink(node)
        self._push_front(node)
        return node.value

    def put(self, key, value) -> None:
        node = self._nodes.get(key)
        if node is not None:
            node.value = value
            self._unlink(node)
            self._push_front(node)
            return
        if len(self._nodes) == self.capacity:
            oldest = self._tail.prev
            self._unlink(oldest)  # type: ignore[arg-type]
            del self._nodes[oldest.key]  # type: ignore[union-attr]
        node = _Node(key, value)
        self._nodes[key] = node
        self._push_front(node)

    def __len__(self) -> int:
        return len(self._nodes)
