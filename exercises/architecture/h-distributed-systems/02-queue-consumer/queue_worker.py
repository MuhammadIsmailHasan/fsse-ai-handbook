"""Architecture · H — A FIFO queue, an idempotent consumer, and a dead-letter queue.

Messages are dicts with at least an "id" key.
"""


class Queue:
    """A simple first-in, first-out queue."""

    def __init__(self):
        self.items: list = []

    def enqueue(self, message) -> None:
        # YOUR CODE HERE
        return None

    def dequeue(self):
        """Remove and return the oldest message, or None if empty."""
        # YOUR CODE HERE
        return None

    def __len__(self) -> int:
        return len(self.items)


def consume_idempotently(processed: set, handler, message) -> str:
    """Run handler(message) at most once per message id.

    - If message["id"] is already in `processed`: return "duplicate" (do NOT call handler).
    - Otherwise: call handler(message), add the id to `processed`, return "processed".
    """
    # YOUR CODE HERE
    return ""


def process_with_retries(handler, message, max_attempts: int) -> tuple[str, int]:
    """Call handler(message), retrying if it raises an exception.

    Return ("done", attempts) as soon as it succeeds, or ("dead-letter", attempts)
    if it still fails after max_attempts. `attempts` is how many times handler ran.
    """
    # YOUR CODE HERE
    return "", 0
