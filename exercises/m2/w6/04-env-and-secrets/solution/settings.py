"""Typed, validated settings loaded from environment variables — fail fast at startup."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from urllib.parse import urlsplit

ENVIRONMENTS = ("development", "test", "production")
WEAK_SECRETS = {"secret", "changeme", "change-me", "dev", "password", "super-secret-key-change-in-production"}
DEV_SECRET = "dev-only-insecure-key-do-not-use-in-production"
TRUE, FALSE = {"true", "1", "yes", "on"}, {"false", "0", "no", "off"}


class SettingsError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("Invalid configuration:\n- " + "\n- ".join(errors))


@dataclass(frozen=True)
class Settings:
    app_env: str
    database_url: str = field(repr=False)
    jwt_secret_key: str = field(repr=False)
    debug: bool
    port: int
    cors_origins: tuple[str, ...]

    def safe_summary(self) -> dict:
        password = urlsplit(self.database_url).password
        database_url = self.database_url
        if password:
            database_url = database_url.replace(f":{password}@", ":***@", 1)
        return {
            "app_env": self.app_env,
            "database_url": database_url,
            "jwt_secret_key": "***",
            "debug": self.debug,
            "port": self.port,
            "cors_origins": list(self.cors_origins),
        }


def load_settings(env: Mapping[str, str]) -> Settings:
    errors: list[str] = []

    app_env = env.get("APP_ENV", "development")
    if app_env not in ENVIRONMENTS:
        errors.append(f"APP_ENV must be one of {', '.join(ENVIRONMENTS)}")
    production = app_env == "production"

    database_url = env.get("DATABASE_URL", "").strip()
    if not database_url:
        errors.append("DATABASE_URL is required")

    secret = env.get("JWT_SECRET_KEY", "")
    if not secret:
        if production:
            errors.append("JWT_SECRET_KEY is required in production")
        else:
            secret = DEV_SECRET
    elif production and (len(secret) < 32 or secret.lower() in WEAK_SECRETS):
        errors.append("JWT_SECRET_KEY must be at least 32 characters and not a known placeholder")

    debug = False
    raw_debug = env.get("DEBUG", "false").strip().lower()
    if raw_debug in TRUE:
        debug = True
    elif raw_debug not in FALSE:
        errors.append("DEBUG must be true or false")
    if production and debug:
        errors.append("DEBUG must be false in production")

    port = 5091
    raw_port = env.get("PORT", "5091").strip()
    if raw_port.isdigit() and 1 <= int(raw_port) <= 65535:
        port = int(raw_port)
    else:
        errors.append("PORT must be an integer between 1 and 65535")

    cors_origins = tuple(o.strip() for o in env.get("CORS_ORIGINS", "").split(",") if o.strip())
    if production and "*" in cors_origins:
        errors.append("CORS_ORIGINS must not contain * in production")

    if errors:
        raise SettingsError(errors)
    return Settings(app_env, database_url, secret, debug, port, cors_origins)
