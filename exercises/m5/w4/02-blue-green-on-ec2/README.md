# M5 · W4 · 02 — Zero-downtime blue/green deploys on one EC2 host

> 🚫🤖 **No-AI** · ⏱️ ~2 h · no AWS account needed

Lab 3's `deploy.sh` **recreates** the API container: every deploy has a few seconds of downtime, and a bad image causes an outage until rollback. Blue/green fixes that on a single host: start the new version **next to** the old one, check it, switch Caddy's upstream, and only then stop the old version. Write the orchestrator in `bluegreen.py`; it talks to the host through an injected `runner` so it can be tested without Docker.

## Setup
- two colors: `blue` → port **5001**, `green` → port **5002**
- `state_dir/active` contains the active color (missing file → nothing active yet)
- `state_dir/upstream.caddy` is imported by the Caddyfile and contains exactly `reverse_proxy 127.0.0.1:<port>\n`
- `state_dir/history` gets one line per **successful** deploy: `<color> <image>\n`

## `deploy(image, *, state_dir, runner, is_healthy, attempts=20, wait=3, drain=10, sleep=time.sleep) -> Result`
`runner(args: list[str], env: dict[str, str]) -> int` runs a command and returns its exit code; `is_healthy(url) -> bool`.
`Result(ok: bool, active: str | None, message: str)`.

Steps (stop at the first failure):
1. `image` must be a digest reference (`…@sha256:<64 hex>`) → else `ValueError` (nothing runs)
2. `idle` = the color that isn't active (`blue` when nothing is active); `env = {"API_IMAGE": image, "PORT": "<idle port>"}`
3. migrations: `["docker", "compose", "-p", "revoshop-<idle>", "-f", "compose.api.yaml", "--profile", "ops", "run", "--rm", "migrate"]` — non-zero → `Result(False, active, "migrations failed")`
4. start idle: `["docker", "compose", "-p", "revoshop-<idle>", "-f", "compose.api.yaml", "up", "-d"]` — non-zero → stop idle (step 8's `down` command for the idle color) and `Result(False, active, "idle failed to start")`
5. poll `http://127.0.0.1:<idle port>/api/v1/health` up to `attempts` times, `sleep(wait)` **between** checks — never healthy → stop idle, `Result(False, active, "idle unhealthy")`
6. switch: write `upstream.caddy` for the idle port, then run `["docker", "exec", "revoshop-proxy", "caddy", "reload", "--config", "/etc/caddy/Caddyfile"]` — non-zero → restore the previous `upstream.caddy` content (or delete the file if there was none), stop idle, `Result(False, active, "proxy reload failed")`
7. record: write the idle color to `active`, append to `history`
8. if there was a previous active color: `sleep(drain)`, then `["docker", "compose", "-p", "revoshop-<old>", "-f", "compose.api.yaml", "down"]` (env `{}`); a failure here doesn't fail the deploy
9. `Result(True, idle, "deployed to <idle>")`

`env` for steps 3–4 is the one from step 2; `down` and `reload` use `{}`.

```bash
cd exercises
uv run pytest m5/w4/02-blue-green-on-ec2
```
