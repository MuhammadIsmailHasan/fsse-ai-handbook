"""Configuration from SSM Parameter Store and Secrets Manager. See README.md."""

import time


def load_parameters(ssm, path: str) -> dict[str, str]:
    raise NotImplementedError


def resolve_references(config: dict[str, str], secrets) -> dict[str, str]:
    raise NotImplementedError


class CachedConfig:
    def __init__(self, load, *, ttl: float, max_stale: float, clock=time.monotonic):
        raise NotImplementedError

    def get(self) -> dict:
        raise NotImplementedError

    def invalidate(self) -> None:
        raise NotImplementedError
