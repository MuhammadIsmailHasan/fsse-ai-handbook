# M2 · W1 · 07 — Fix a Bad Dockerfile

> 🚫🤖 **No-AI** · ⏱️ ~40 min · Docker optional (tests are static)

`app.py` is a tiny web app (standard library only) that responds with a greeting from the `GREETING` environment variable. `requirements.txt` lists `gunicorn`.

Fix `Dockerfile` and create `.dockerignore`. The tests require:

| # | Rule |
|---|---|
| 1 | `FROM` a pinned, slim Python image (e.g. `python:3.12-slim`) — no `latest`, no untagged image |
| 2 | `WORKDIR` is set |
| 3 | `requirements.txt` is copied and installed **before** the rest of the code is copied |
| 4 | `pip install` uses `--no-cache-dir` |
| 5 | A non-root `USER` is set (not `root`) before `CMD` |
| 6 | No `ENV`/`ARG` containing secret-like names (`SECRET`, `PASSWORD`, `TOKEN`, `KEY`) |
| 7 | `EXPOSE 8000` |
| 8 | `CMD` uses exec form (a JSON array) |
| 9 | `.dockerignore` excludes `.env`, `.venv`, `.git`, `__pycache__` |

```bash
cd exercises
uv run pytest m2/w1/07-docker-basics
```

With Docker installed:

```bash
docker build -t toy-api .
docker run --rm -p 8091:8000 -e GREETING="Halo dari Docker" toy-api
# open http://localhost:8091
```
