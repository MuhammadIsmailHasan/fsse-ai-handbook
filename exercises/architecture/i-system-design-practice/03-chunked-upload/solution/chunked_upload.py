"""Architecture · I — Resumable chunked upload tracker (solution)."""


class ChunkedUpload:
    def __init__(self, total_chunks: int):
        self.total = total_chunks
        self.received: dict[int, object] = {}

    def receive(self, index: int, data) -> str:
        if index < 0 or index >= self.total:
            raise IndexError(f"chunk {index} out of range 0..{self.total - 1}")
        if index in self.received:
            return "duplicate"
        self.received[index] = data
        return "stored"

    def missing(self) -> list[int]:
        return [i for i in range(self.total) if i not in self.received]

    def is_complete(self) -> bool:
        return len(self.received) == self.total

    def assemble(self) -> list:
        if not self.is_complete():
            raise ValueError(f"upload incomplete: missing {self.missing()}")
        return [self.received[i] for i in range(self.total)]
