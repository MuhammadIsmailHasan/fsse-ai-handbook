"""Typed, validated settings loaded from environment variables — fail fast at startup. See README.md."""

from collections.abc import Mapping
from dataclasses import dataclass


class SettingsError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("Invalid configuration:\n- " + "\n- ".join(errors))


@dataclass(frozen=True)
class Settings:
    app_env: str
    database_url: str
    jwt_secret_key: str
    debug: bool
    port: int
    cors_origins: tuple[str, ...]

    def safe_summary(self) -> dict:
        raise NotImplementedError


def load_settings(env: Mapping[str, str]) -> Settings:
    raise NotImplementedError
