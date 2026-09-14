"""Checks for env_parity.py. Don't edit this file."""

from textwrap import dedent

import pytest

from env_parity import Issue, check, main, parse_env

STRONG = "k9Q2vX7mL4pR8sT1wY6zB3nC5dF0gH2jK4"
STRONG2 = "Zx8Wv6Ut4Sr2Qp0On9Ml7Kj5Ih3Gf1Ed9Cb"


def test_parse_env():
    text = dedent(
        """\
        # database
        export DATABASE_URL=postgresql://app:pw@db:5432/app   # inline comment
        EMPTY=
        SINGLE='literal \\n # not a comment'
        DOUBLE="line1\\nline2 \\"quoted\\" # still value"
          SPACED =ignored-line-below
        """
    )
    with pytest.raises(ValueError, match="line 6"):
        parse_env(text)
    assert parse_env("\n".join(text.splitlines()[:5])) == {
        "DATABASE_URL": "postgresql://app:pw@db:5432/app",
        "EMPTY": "",
        "SINGLE": "literal \\n # not a comment",
        "DOUBLE": 'line1\nline2 "quoted" # still value',
    }
    with pytest.raises(ValueError, match="line 1"):
        parse_env('A="unterminated')


def codes(issues):
    return [(i.environment, i.key, i.code) for i in issues]


def test_clean_environments():
    base = {"DATABASE_URL": "postgresql://app@db/app", "JWT_SECRET_KEY": STRONG, "MIDTRANS_IS_PRODUCTION": "true", "MIDTRANS_CLIENT_KEY": "Mid-client-abc"}
    staging = {**base, "JWT_SECRET_KEY": STRONG2, "MIDTRANS_IS_PRODUCTION": "false"}
    assert check({"staging": staging, "production": base}, required={"DATABASE_URL", "JWT_SECRET_KEY"}) == []


def test_all_rules():
    staging = {
        "DATABASE_URL": "postgresql://app@db/app",
        "JWT_SECRET_KEY": STRONG,
        "POSTGRES_PASSWORD": "change-me-please-change-me-please!",
        "SENTRY_DSN": "https://sentry.example",
        "MIDTRANS_SERVER_KEY": "SB-Mid-server-123",
    }
    production = {
        "DATABASE_URL": "postgresql://app@localhost:5432/app",
        "JWT_SECRET_KEY": STRONG,
        "POSTGRES_PASSWORD": "",
        "FLASK_DEBUG": "True",
        "MIDTRANS_SERVER_KEY": "SB-Mid-server-123",
        "MIDTRANS_CLIENT_KEY": "short",
        "API_TOKEN": "tok",
    }
    issues = check({"staging": staging, "production": production}, required={"DATABASE_URL", "JWT_SECRET_KEY", "POSTGRES_PASSWORD"})
    assert codes(issues) == [
        ("production", "API_TOKEN", "WEAK_SECRET"),
        ("production", "DATABASE_URL", "LOCALHOST_IN_PRODUCTION"),
        ("production", "FLASK_DEBUG", "DEBUG_IN_PRODUCTION"),
        ("production", "JWT_SECRET_KEY", "SHARED_SECRET"),
        ("production", "MIDTRANS_IS_PRODUCTION", "SANDBOX_IN_PRODUCTION"),
        ("production", "MIDTRANS_SERVER_KEY", "SANDBOX_IN_PRODUCTION"),
        ("production", "POSTGRES_PASSWORD", "MISSING"),
        ("production", "SENTRY_DSN", "DRIFT"),
        ("staging", "API_TOKEN", "DRIFT"),
        ("staging", "FLASK_DEBUG", "DRIFT"),
        ("staging", "MIDTRANS_CLIENT_KEY", "DRIFT"),
        ("staging", "POSTGRES_PASSWORD", "WEAK_SECRET"),
    ]
    assert all(isinstance(i, Issue) and i.message for i in issues)
    for secret in (STRONG, "change-me-please-change-me-please!", "tok", "SB-Mid-server-123"):
        assert all(secret not in i.message for i in issues), "never print secret values"


def test_development_is_not_held_to_production_rules():
    dev = {"DATABASE_URL": "postgresql://localhost/app", "JWT_SECRET_KEY": "dev", "DEBUG": "1"}
    assert check({"development": dev}, required={"DATABASE_URL"}) == []
    prod = {"DATABASE_URL": "postgresql://db/app", "DEBUG": "off", "MIDTRANS_IS_PRODUCTION": "TRUE"}
    assert check({"production": prod}, required=set()) == []


def test_cli(tmp_path, capsys):
    (tmp_path / "staging.env").write_text(f"DATABASE_URL=postgresql://db/app\nJWT_SECRET_KEY={STRONG2}\n")
    (tmp_path / "prod.env").write_text("DATABASE_URL=postgresql://db/app\nMIDTRANS_IS_PRODUCTION=true\n")
    code = main([f"staging={tmp_path / 'staging.env'}", f"production={tmp_path / 'prod.env'}", "--require", "DATABASE_URL,JWT_SECRET_KEY"])
    out = capsys.readouterr().out.splitlines()
    assert code == 1
    assert out[0].startswith("production JWT_SECRET_KEY MISSING: ")
    assert any(line.startswith("staging MIDTRANS_IS_PRODUCTION DRIFT: ") for line in out)
    (tmp_path / "prod.env").write_text(f"DATABASE_URL=postgresql://db/app\nJWT_SECRET_KEY={STRONG}\nMIDTRANS_IS_PRODUCTION=true\n")
    (tmp_path / "staging.env").write_text(f"DATABASE_URL=postgresql://db/app\nJWT_SECRET_KEY={STRONG2}\nMIDTRANS_IS_PRODUCTION=false\n")
    assert main([f"staging={tmp_path / 'staging.env'}", f"production={tmp_path / 'prod.env'}", "--require", "DATABASE_URL"]) == 0
