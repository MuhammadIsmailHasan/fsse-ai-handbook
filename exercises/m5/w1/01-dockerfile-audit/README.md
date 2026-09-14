# M5 · W1 · 01 — Build a Dockerfile auditor

> 🚫🤖 **No-AI** · ⏱️ ~2 h

The best way to *remember* Dockerfile best practices is to write the tool that enforces them. Build a tiny linter (like `hadolint`) in `dockerfile_audit.py`, then run it on your own RevoShop `Dockerfile`.

## 1. `parse(text) -> list[Instruction]`
`Instruction(line: int, keyword: str, args: str)` — `line` is the 1-based line where the instruction **starts**.
- skip blank lines and comments (`# ...`)
- join line continuations (`\` at the end of a line) with a single space; comment lines inside a continuation are ignored
- `keyword` upper-cased; `args` stripped

## 2. `audit(text) -> list[Finding]`
`Finding(rule: str, line: int, severity: "error" | "warning", message: str)`, sorted by `line` then `rule`.

| Rule | Severity | Report when | Line |
|---|---|---|---|
| **DF001** | error | a `FROM` image has no tag or uses `:latest` — except `scratch`, digests (`@sha256:`), and names of earlier stages (`FROM builder`) | the FROM |
| **DF002** | error | the **final** stage has no `USER`, or its last `USER` is `root` or `0` | final FROM (no USER) or that USER |
| **DF003** | error | `CMD` or `ENTRYPOINT` in **shell form** (args not starting with `[`) | the instruction |
| **DF004** | warning | inside one stage, a `COPY`/`ADD` whose sources include `.` appears **before** a `RUN` that installs dependencies (`pip install`, `uv sync`, `npm ci`, `npm install`, `poetry install`) | the RUN |
| **DF005** | warning | `apt-get install` without `--no-install-recommends`, **or** without `rm -rf /var/lib/apt/lists` in the same `RUN` (one finding per RUN) | the RUN |
| **DF006** | error | `ENV` or `ARG` defines a name containing `SECRET`, `PASSWORD`, `TOKEN`, `API_KEY` or `PRIVATE_KEY` **with a value** (`ENV A=b`, `ENV A b`, `ARG A=b`; `ARG A` without a value is fine) | the instruction |
| **DF007** | warning | `ADD` with an `http://` or `https://` source | the ADD |
| **DF008** | warning | the final stage has no `HEALTHCHECK` | final FROM |

Stages start at each `FROM`. `FROM image AS name` names a stage (case-insensitive `AS`). Flags like `FROM --platform=$BUILDPLATFORM python:3.13-slim AS build` must work.

## 3. `main(argv) -> int`
`python dockerfile_audit.py path/to/Dockerfile` prints one line per finding, `Dockerfile:12 DF003 error: <message>`, then `N error(s), M warning(s)`. Exit code `1` if there is any **error**, else `0`.

```bash
cd exercises
uv run pytest m5/w1/01-dockerfile-audit
uv run python m5/w1/01-dockerfile-audit/dockerfile_audit.py ~/path/to/revoshop/Dockerfile
```
