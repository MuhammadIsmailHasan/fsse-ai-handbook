"""Architecture · I — Resumable chunked upload tracker.

A big file is uploaded as numbered chunks (0 .. total-1). Chunks can arrive out
of order, and a flaky connection may re-send one — that must be harmless. When
every chunk is present, the upload is complete and can be assembled in order.
"""


class ChunkedUpload:
    def __init__(self, total_chunks: int):
        self.total = total_chunks
        self.received: dict[int, object] = {}

    def receive(self, index: int, data) -> str:
        """Store chunk `index`. Return "stored", or "duplicate" if already received.

        Raise IndexError if index is out of range [0, total).
        """
        # YOUR CODE HERE
        return ""

    def missing(self) -> list[int]:
        """Sorted list of chunk indices not yet received."""
        # YOUR CODE HERE
        return []

    def is_complete(self) -> bool:
        """True once every chunk has been received."""
        # YOUR CODE HERE
        return False

    def assemble(self) -> list:
        """Return chunk data in order 0..total-1. Raise ValueError if incomplete."""
        # YOUR CODE HERE
        return []
