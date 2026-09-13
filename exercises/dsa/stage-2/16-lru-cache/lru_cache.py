class LRUCache:
    def __init__(self, capacity: int):
        raise NotImplementedError

    def get(self, key: str) -> int | None:
        raise NotImplementedError

    def put(self, key: str, value: int) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError
