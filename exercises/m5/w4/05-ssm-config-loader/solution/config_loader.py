"""Configuration from SSM Parameter Store and Secrets Manager. See README.md."""

import json
import logging
import re
import time

logger = logging.getLogger(__name__)
KEY = re.compile(r"^[A-Z][A-Z0-9_]*$")


def load_parameters(ssm, path: str) -> dict[str, str]:
    if not (path.startswith("/") and path.endswith("/")):
        raise ValueError("path must start and end with '/'")
    config: dict[str, str] = {}
    paginator = ssm.get_paginator("get_parameters_by_path")
    for page in paginator.paginate(Path=path, Recursive=True, WithDecryption=True):
        for parameter in page["Parameters"]:
            key = parameter["Name"][len(path):].replace("/", "_").upper()
            if not KEY.match(key):
                raise ValueError(f"unexpected parameter name: {parameter['Name']}")
            if key in config:
                raise ValueError(f"two parameters map to {key}")
            config[key] = parameter["Value"]
    return config


def resolve_references(config: dict[str, str], secrets) -> dict[str, str]:
    fetched: dict[str, dict] = {}
    resolved = {}
    for key, value in config.items():
        if not value.startswith("secretsmanager:"):
            resolved[key] = value
            continue
        secret_id, _, json_key = value.removeprefix("secretsmanager:").rpartition("#")
        if secret_id not in fetched:
            fetched[secret_id] = json.loads(secrets.get_secret_value(SecretId=secret_id)["SecretString"])
        resolved[key] = str(fetched[secret_id][json_key])  # KeyError when the JSON key is missing
    return resolved


class CachedConfig:
    def __init__(self, load, *, ttl: float, max_stale: float, clock=time.monotonic):
        self._load, self._ttl, self._max_stale, self._clock = load, ttl, max_stale, clock
        self._value: dict | None = None
        self._loaded_at: float | None = None

    def get(self) -> dict:
        now = self._clock()
        if self._value is not None and self._loaded_at is not None and now - self._loaded_at < self._ttl:
            return self._value
        try:
            self._value, self._loaded_at = self._load(), now
        except Exception:
            if self._value is not None and self._loaded_at is not None and now - self._loaded_at < self._max_stale:
                logger.warning("config refresh failed; serving values from %.0fs ago", now - self._loaded_at)
                return self._value
            raise
        return self._value

    def invalidate(self) -> None:
        self._loaded_at = None
