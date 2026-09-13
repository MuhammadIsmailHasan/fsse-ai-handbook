"""Checks for settings.py and scan_secrets.py. Don't edit this file.

Fake secrets below are built by joining pieces, so this file itself doesn't look like a leak.
"""

import pytest

from scan_secrets import Finding, scan_directory, scan_text
from settings import Settings, SettingsError, load_settings

STRONG = "k" * 40
PROD = {"APP_ENV": "production", "DATABASE_URL": "postgresql://app:s3cr3t-pass@db:5432/careerpilot", "JWT_SECRET_KEY": STRONG, "CORS_ORIGINS": "https://careerpilot.id, https://www.careerpilot.id"}


def errors_for(env):
    with pytest.raises(SettingsError) as info:
        load_settings(env)
    return info.value.errors


def prefixes(errors):
    return sorted(error.split()[0] for error in errors)


# ---------- settings ----------

def test_production_settings_are_typed():
    settings = load_settings({**PROD, "PORT": "8080", "DEBUG": "False"})
    assert settings == Settings("production", PROD["DATABASE_URL"], STRONG, False, 8080, ("https://careerpilot.id", "https://www.careerpilot.id"))


def test_development_defaults():
    settings = load_settings({"DATABASE_URL": "postgresql://fsse:fsse@localhost:5491/fsse"})
    assert settings.app_env == "development"
    assert settings.debug is False and settings.port == 5091 and settings.cors_origins == ()
    assert len(settings.jwt_secret_key) >= 32, "development gets a clearly-labelled insecure default"
    assert "insecure" in settings.jwt_secret_key


@pytest.mark.parametrize(("raw", "expected"), [("true", True), ("1", True), ("YES", True), ("on", True), ("false", False), ("0", False), ("no", False), ("Off", False)])
def test_debug_parsing(raw, expected):
    assert load_settings({"DATABASE_URL": "x", "DEBUG": raw}).debug is expected


def test_production_requires_secret():
    env = {**PROD}
    del env["JWT_SECRET_KEY"]
    assert prefixes(errors_for(env)) == ["JWT_SECRET_KEY"]


@pytest.mark.parametrize("secret", ["short-secret", "super-secret-key-change-in-production", "CHANGE-ME"])
def test_production_rejects_weak_secret(secret):
    assert prefixes(errors_for({**PROD, "JWT_SECRET_KEY": secret})) == ["JWT_SECRET_KEY"]


def test_all_errors_are_reported_together():
    env = {"APP_ENV": "production", "DEBUG": "true", "PORT": "99999", "CORS_ORIGINS": "*"}
    assert prefixes(errors_for(env)) == ["CORS_ORIGINS", "DATABASE_URL", "DEBUG", "JWT_SECRET_KEY", "PORT"]


@pytest.mark.parametrize(("key", "value"), [("APP_ENV", "staging"), ("DEBUG", "maybe"), ("PORT", "abc"), ("PORT", "0")])
def test_invalid_values(key, value):
    assert prefixes(errors_for({"DATABASE_URL": "x", key: value})) == [key]


def test_secrets_never_appear_in_repr_or_summary():
    settings = load_settings(PROD)
    assert STRONG not in repr(settings) and "s3cr3t-pass" not in repr(settings)
    summary = settings.safe_summary()
    assert summary == {
        "app_env": "production",
        "database_url": "postgresql://app:***@db:5432/careerpilot",
        "jwt_secret_key": "***",
        "debug": False,
        "port": 5091,
        "cors_origins": ["https://careerpilot.id", "https://www.careerpilot.id"],
    }
    assert load_settings({"DATABASE_URL": "sqlite:///local.db"}).safe_summary()["database_url"] == "sqlite:///local.db"


def test_error_message_does_not_leak_values():
    error = SettingsError(errors_for({**PROD, "JWT_SECRET_KEY": "tiny-but-real"}))
    assert "tiny-but-real" not in str(error)


# ---------- scanner ----------

AWS = "AKIA" + "Q" * 8 + "7" * 8
GITHUB = "ghp" + "_" + "a1B2" * 9
KEY_HEADER = "-----BEGIN " + "RSA PRIVATE KEY-----"


def kinds(text):
    return [(f.line, f.kind) for f in scan_text(text, "file.py")]


def test_detects_known_token_formats():
    text = f"aws = '{AWS}'\n# nothing here\ntoken: {GITHUB}\n{KEY_HEADER}\n"
    assert kinds(text) == [(1, "aws_access_key"), (3, "github_token"), (4, "private_key")]


@pytest.mark.parametrize(
    "line",
    [
        'JWT_SECRET_KEY = "super-secret-key-change-in-production"',
        "DB_PASSWORD=hunter2hunter2",
        "  midtrans_server_key: 'SB-Mid-server-abc123XYZ'".replace("server_key", "api_key"),
        'config = {"token": "8f14e45fceea167a5a36dedd4bea2543"}',
    ],
)
def test_detects_hardcoded_secret_assignments(line):
    assert kinds(line) == [(1, "hardcoded_secret")]


@pytest.mark.parametrize(
    "line",
    [
        'JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]',
        "JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')",
        "JWT_SECRET_KEY=change-me",
        "JWT_SECRET_KEY=your-secret-here",
        "POSTGRES_PASSWORD=${POSTGRES_PASSWORD:?}",
        "API_KEY=<paste-your-key>",
        "PASSWORD=short",
        "password_hash = hash_password(password)",
        "MAX_TOKENS=4096",
    ],
)
def test_ignores_lookups_placeholders_and_short_values(line):
    assert kinds(line) == []


def test_scan_directory(tmp_path):
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "config.py").write_text(f'import os\nSECRET = os.environ["SECRET"]\nAWS_KEY = "{AWS}"\n')
    (tmp_path / ".env").write_text("JWT_SECRET_KEY=whatever-real-value\n")
    (tmp_path / ".env.production").write_text("X=1\n")
    (tmp_path / ".env.example").write_text("JWT_SECRET_KEY=change-me\nDATABASE_URL=postgresql://user:pass@localhost/db\n")
    (tmp_path / "logo.png").write_bytes(bytes(range(256)))
    for skipped in (".git", "node_modules", ".venv"):
        (tmp_path / skipped).mkdir()
        (tmp_path / skipped / "leak.txt").write_text(f"{GITHUB}\n")
    assert scan_directory(tmp_path) == [
        Finding(".env", 0, "env_file"),
        Finding(".env.production", 0, "env_file"),
        Finding("app/config.py", 3, "aws_access_key"),
    ]
