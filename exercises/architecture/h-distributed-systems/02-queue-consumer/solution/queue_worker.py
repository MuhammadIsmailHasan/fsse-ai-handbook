"""Architecture · H — FIFO queue, idempotent consumer, dead-letter (solution)."""


class Queue:
    def __init__(self):
        self.items: list = []

    def enqueue(self, message) -> None:
        self.items.append(message)

    def dequeue(self):
        if not self.items:
            return None
        return self.items.pop(0)

    def __len__(self) -> int:
        return len(self.items)


def consume_idempotently(processed: set, handler, message) -> str:
    if message["id"] in processed:
        return "duplicate"
    handler(message)
    processed.add(message["id"])
    return "processed"


def process_with_retries(handler, message, max_attempts: int) -> tuple[str, int]:
    attempts = 0
    for _ in range(max_attempts):
        attempts += 1
        try:
            handler(message)
            return "done", attempts
        except Exception:
            continue
    return "dead-letter", attempts
