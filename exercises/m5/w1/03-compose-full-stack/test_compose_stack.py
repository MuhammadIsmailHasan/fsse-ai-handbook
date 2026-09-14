"""Checks stack/compose.yaml and stack/compose.override.yaml with `docker compose config`. Don't edit this file."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

STACK = Path(__file__).parent / "stack"
ENV = {"JWT_SECRET_KEY": "test-secret-value-0123456789", "POSTGRES_PASSWORD": "pw-for-tests"}

pytestmark = pytest.mark.skipif(not shutil.which("docker"), reason="Docker is required for this exercise")


def compose_config(*files: str, env: dict | None = None, profiles: tuple[str, ...] = ()) -> subprocess.CompletedProcess[str]:
    args = ["docker", "compose", "--project-directory", str(STACK)]
    for file in files:
        args += ["-f", str(STACK / file)]
    for profile in profiles:
        args += ["--profile", profile]
    args += ["config", "--format", "json"]
    base_env = {k: v for k, v in __import__("os").environ.items() if k not in ("JWT_SECRET_KEY", "POSTGRES_PASSWORD", "HTTP_PORT", "COMPOSE_PROFILES", "COMPOSE_FILE")}
    return subprocess.run(args, capture_output=True, text=True, env={**base_env, **(env if env is not None else ENV)}, timeout=60)


def load(*files: str, profiles: tuple[str, ...] = ()) -> dict:
    result = compose_config(*files, profiles=profiles)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def prod() -> dict:
    return load("compose.yaml")


def published(service: dict) -> list[tuple[str, int]]:
    return [(str(p.get("published")), int(p["target"])) for p in service.get("ports", [])]


def deps(service: dict) -> dict:
    return {name: value["condition"] for name, value in service.get("depends_on", {}).items()}


def env(service: dict) -> dict:
    return service.get("environment", {})


def test_services_networks_volumes():
    config = prod()
    assert config["name"] == "shop"
    assert set(config["services"]) == {"proxy", "api", "migrate", "worker", "db", "redis"}, "mailpit must only exist in the tools profile"
    assert {"frontend", "backend"} <= set(config["networks"])
    assert {"pgdata", "redisdata"} <= set(config["volumes"])
    assert "mailpit" in load("compose.yaml", profiles=("tools",))["services"]


def test_required_secrets_fail_fast():
    for missing in ENV:
        result = compose_config("compose.yaml", env={k: v for k, v in ENV.items() if k != missing})
        assert result.returncode != 0, f"compose should refuse to start without {missing}"
        assert f"set {missing}" in result.stderr


def test_only_the_proxy_is_published():
    services = prod()["services"]
    assert published(services["proxy"]) == [("8080", 80)]
    for name in ("api", "migrate", "worker", "db", "redis"):
        assert published(services[name]) == [], f"{name} must not publish ports in production"
    proxy = services["proxy"]
    assert proxy["image"] == "caddy:2-alpine"
    mount = [v for v in proxy["volumes"] if v["target"] == "/etc/caddy/Caddyfile"]
    assert mount and mount[0]["read_only"] is True and mount[0]["source"].endswith("Caddyfile")
    assert deps(proxy) == {"api": "service_healthy"}
    assert list(proxy["networks"]) == ["frontend"]
    assert proxy["restart"] == "unless-stopped"


def test_api_service():
    api = prod()["services"]["api"]
    assert api["build"]["target"] == "prod" and api["build"]["context"].endswith("api")
    assert api["image"] == "shop-api:local"
    assert env(api) == {
        "JWT_SECRET_KEY": ENV["JWT_SECRET_KEY"],
        "DATABASE_URL": f"postgresql+psycopg://shop:{ENV['POSTGRES_PASSWORD']}@db:5432/shop",
        "REDIS_URL": "redis://redis:6379/0",
    }
    assert "/health/live" in " ".join(api["healthcheck"]["test"]) and "5091" in " ".join(api["healthcheck"]["test"])
    assert deps(api) == {"db": "service_healthy", "redis": "service_healthy", "migrate": "service_completed_successfully"}
    assert set(api["networks"]) == {"frontend", "backend"}
    assert api["read_only"] is True and "/tmp" in api["tmpfs"]
    assert int(api["deploy"]["resources"]["limits"]["memory"]) == 512 * 1024 * 1024
    assert api["restart"] == "unless-stopped"


def test_migrate_and_worker_reuse_the_image():
    services = prod()["services"]
    migrate, worker = services["migrate"], services["worker"]
    for service in (migrate, worker):
        assert service["image"] == "shop-api:local" and "build" not in service
        assert list(service["networks"]) == ["backend"]
    assert migrate["command"] == ["flask", "--app", "wsgi:app", "db", "upgrade"]
    assert env(migrate)["DATABASE_URL"].endswith("@db:5432/shop")
    assert deps(migrate) == {"db": "service_healthy"}
    assert migrate.get("restart") == "no"
    assert worker["command"] == ["python", "-m", "worker"]
    assert {"DATABASE_URL", "REDIS_URL"} <= set(env(worker))
    assert deps(worker) == {"db": "service_healthy", "redis": "service_healthy", "migrate": "service_completed_successfully"}
    assert worker["restart"] == "unless-stopped"


def test_data_services():
    services = prod()["services"]
    db, redis = services["db"], services["redis"]
    assert db["image"] == "postgres:17-alpine"
    assert env(db) == {"POSTGRES_USER": "shop", "POSTGRES_DB": "shop", "POSTGRES_PASSWORD": ENV["POSTGRES_PASSWORD"]}
    assert any(v["type"] == "volume" and v["source"] == "pgdata" and v["target"] == "/var/lib/postgresql/data" for v in db["volumes"])
    assert "pg_isready" in " ".join(db["healthcheck"]["test"])
    assert redis["image"] == "redis:8-alpine"
    assert redis["command"] == ["redis-server", "--appendonly", "yes"]
    assert any(v["type"] == "volume" and v["source"] == "redisdata" and v["target"] == "/data" for v in redis["volumes"])
    assert "ping" in " ".join(redis["healthcheck"]["test"])
    for service in (db, redis):
        assert list(service["networks"]) == ["backend"]


def test_mailpit_tool_profile():
    mailpit = load("compose.yaml", profiles=("tools",))["services"]["mailpit"]
    image, _, tag = mailpit["image"].partition(":")
    assert image == "axllent/mailpit" and tag and tag != "latest"
    assert mailpit["profiles"] == ["tools"]
    assert published(mailpit) == [("8025", 8025)]


def test_http_port_is_configurable():
    result = compose_config("compose.yaml", env={**ENV, "HTTP_PORT": "9090"})
    assert result.returncode == 0, result.stderr
    assert published(json.loads(result.stdout)["services"]["proxy"]) == [("9090", 80)]


def test_development_override():
    services = load("compose.yaml", "compose.override.yaml")["services"]
    api = services["api"]
    assert api["build"]["target"] == "dev"
    assert any(v["type"] == "bind" and v["source"].endswith("api") and v["target"] == "/app" for v in api["volumes"])
    assert env(api)["FLASK_DEBUG"] == "1" and "JWT_SECRET_KEY" in env(api)
    assert published(api) == [("5092", 5091)]
    assert published(services["db"]) == [("5493", 5432)]
    assert published(services["redis"]) == [("6392", 6379)]
    assert published(services["proxy"]) == [("8080", 80)]
