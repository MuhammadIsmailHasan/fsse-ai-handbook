"""Blue/green deploys on a single Docker host. See README.md."""

import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

PORTS = {"blue": 5001, "green": 5002}
DIGEST = re.compile(r"^[a-z0-9./:-]+@sha256:[a-f0-9]{64}$")


@dataclass(frozen=True)
class Result:
    ok: bool
    active: str | None
    message: str


def _compose(color: str, *args: str) -> list[str]:
    return ["docker", "compose", "-p", f"revoshop-{color}", "-f", "compose.api.yaml", *args]


def deploy(image, *, state_dir: Path, runner, is_healthy, attempts=20, wait=3, drain=10, sleep: Callable[[float], None] = time.sleep) -> Result:
    if not DIGEST.match(image):
        raise ValueError("deploy by digest: <repository>@sha256:<64 hex>")

    active_file, upstream_file, history_file = state_dir / "active", state_dir / "upstream.caddy", state_dir / "history"
    active = active_file.read_text().strip() if active_file.exists() else None
    idle = "green" if active == "blue" else "blue"
    port = PORTS[idle]
    env = {"API_IMAGE": image, "PORT": str(port)}

    def stop_idle() -> None:
        runner(_compose(idle, "down"), {})

    if runner(_compose(idle, "--profile", "ops", "run", "--rm", "migrate"), env) != 0:
        return Result(False, active, "migrations failed")

    if runner(_compose(idle, "up", "-d"), env) != 0:
        stop_idle()
        return Result(False, active, "idle failed to start")

    healthy = False
    for attempt in range(attempts):
        if attempt:
            sleep(wait)
        if is_healthy(f"http://127.0.0.1:{port}/api/v1/health"):
            healthy = True
            break
    if not healthy:
        stop_idle()  # the old color never stopped serving traffic
        return Result(False, active, "idle unhealthy")

    previous_upstream = upstream_file.read_text() if upstream_file.exists() else None
    upstream_file.write_text(f"reverse_proxy 127.0.0.1:{port}\n")
    if runner(["docker", "exec", "revoshop-proxy", "caddy", "reload", "--config", "/etc/caddy/Caddyfile"], {}) != 0:
        if previous_upstream is None:
            upstream_file.unlink()
        else:
            upstream_file.write_text(previous_upstream)
        stop_idle()
        return Result(False, active, "proxy reload failed")

    active_file.write_text(idle)
    with history_file.open("a") as history:
        history.write(f"{idle} {image}\n")

    if active:
        sleep(drain)  # let in-flight requests on the old color finish
        runner(_compose(active, "down"), {})

    return Result(True, idle, f"deployed to {idle}")
