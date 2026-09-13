class RateLimiter:
    def __init__(self, limit: int, window: float):
        raise NotImplementedError

    def allow(self, user_id: str, now: float) -> bool:
        raise NotImplementedError
