"""Checks for bluegreen.py. Don't edit this file."""

import pytest

from bluegreen import Result, deploy

IMAGE = "ghcr.io/sari/revoshop@sha256:" + "a" * 64
IMAGE2 = "ghcr.io/sari/revoshop@sha256:" + "b" * 64
RELOAD = ["docker", "exec", "revoshop-proxy", "caddy", "reload", "--config", "/etc/caddy/Caddyfile"]


def compose(color, *args):
    return ["docker", "compose", "-p", f"revoshop-{color}", "-f", "compose.api.yaml", *args]


class FakeHost:
    def __init__(self, failures=None, health=None):
        self.calls, self.failures, self.health, self.checked, self.sleeps = [], failures or {}, health, [], []

    def runner(self, args, env):
        self.calls.append((args, env))
        return self.failures.get(tuple(args), 0)

    def is_healthy(self, url):
        self.checked.append(url)
        return True if self.health is None else self.health.pop(0)

    def sleep(self, seconds):
        self.sleeps.append(seconds)


def run(tmp_path, host, image=IMAGE, **kwargs):
    return deploy(image, state_dir=tmp_path, runner=host.runner, is_healthy=host.is_healthy, sleep=host.sleep, **kwargs)


def test_first_deploy_goes_blue(tmp_path):
    host = FakeHost()
    assert run(tmp_path, host) == Result(True, "blue", "deployed to blue")
    env = {"API_IMAGE": IMAGE, "PORT": "5001"}
    assert host.calls == [
        (compose("blue", "--profile", "ops", "run", "--rm", "migrate"), env),
        (compose("blue", "up", "-d"), env),
        (RELOAD, {}),
    ]
    assert host.checked == ["http://127.0.0.1:5001/api/v1/health"]
    assert (tmp_path / "active").read_text().strip() == "blue"
    assert (tmp_path / "upstream.caddy").read_text() == "reverse_proxy 127.0.0.1:5001\n"
    assert (tmp_path / "history").read_text() == f"blue {IMAGE}\n"
    assert host.sleeps == []


def test_second_deploy_goes_green_then_drains_blue(tmp_path):
    run(tmp_path, FakeHost())
    host = FakeHost(health=[False, False, True])
    assert run(tmp_path, host, image=IMAGE2, wait=2, drain=15) == Result(True, "green", "deployed to green")
    env = {"API_IMAGE": IMAGE2, "PORT": "5002"}
    assert host.calls == [
        (compose("green", "--profile", "ops", "run", "--rm", "migrate"), env),
        (compose("green", "up", "-d"), env),
        (RELOAD, {}),
        (compose("blue", "down"), {}),
    ]
    assert host.sleeps == [2, 2, 15]
    assert (tmp_path / "upstream.caddy").read_text() == "reverse_proxy 127.0.0.1:5002\n"
    assert (tmp_path / "history").read_text().splitlines() == [f"blue {IMAGE}", f"green {IMAGE2}"]
    third = FakeHost()
    assert run(tmp_path, third).active == "blue"
    assert third.calls[-1] == (compose("green", "down"), {})


def test_unhealthy_idle_is_stopped_and_old_color_keeps_serving(tmp_path):
    run(tmp_path, FakeHost())
    host = FakeHost(health=[False] * 5)
    assert run(tmp_path, host, image=IMAGE2, attempts=5, wait=1) == Result(False, "blue", "idle unhealthy")
    assert host.calls[-1] == (compose("green", "down"), {})
    assert RELOAD not in [args for args, _ in host.calls]
    assert host.sleeps == [1, 1, 1, 1]
    assert (tmp_path / "active").read_text().strip() == "blue"
    assert (tmp_path / "upstream.caddy").read_text() == "reverse_proxy 127.0.0.1:5001\n"
    assert (tmp_path / "history").read_text().splitlines() == [f"blue {IMAGE}"]


def test_migration_and_start_failures(tmp_path):
    host = FakeHost(failures={tuple(compose("blue", "--profile", "ops", "run", "--rm", "migrate")): 1})
    assert run(tmp_path, host) == Result(False, None, "migrations failed")
    assert len(host.calls) == 1 and not (tmp_path / "active").exists()

    host = FakeHost(failures={tuple(compose("blue", "up", "-d")): 17})
    assert run(tmp_path, host) == Result(False, None, "idle failed to start")
    assert host.calls[-1] == (compose("blue", "down"), {})
    assert host.checked == []


def test_proxy_reload_failure_restores_upstream(tmp_path):
    run(tmp_path, FakeHost())
    host = FakeHost(failures={tuple(RELOAD): 1})
    assert run(tmp_path, host, image=IMAGE2) == Result(False, "blue", "proxy reload failed")
    assert (tmp_path / "upstream.caddy").read_text() == "reverse_proxy 127.0.0.1:5001\n"
    assert host.calls[-1] == (compose("green", "down"), {})

    fresh = tmp_path / "fresh"
    fresh.mkdir()
    host = FakeHost(failures={tuple(RELOAD): 1})
    assert run(fresh, host).ok is False
    assert not (fresh / "upstream.caddy").exists()


def test_old_color_down_failure_does_not_fail_deploy(tmp_path):
    run(tmp_path, FakeHost())
    host = FakeHost(failures={tuple(compose("blue", "down")): 1})
    assert run(tmp_path, host, image=IMAGE2).ok is True


@pytest.mark.parametrize("bad", ["ghcr.io/sari/revoshop:latest", "ghcr.io/sari/revoshop@sha256:abc", "revoshop@sha256:" + "A" * 64, "x; rm -rf /@sha256:" + "a" * 64])
def test_requires_digest(tmp_path, bad):
    host = FakeHost()
    with pytest.raises(ValueError):
        run(tmp_path, host, image=bad)
    assert host.calls == []
