"""Provided: a tiny in-memory job board to load test. Don't edit.

Run it yourself:  uv run python m2/w6/03-locust-performance/target_app.py --port 5092

POST /api/v1/login              {"email", "password"} → 200 {"token": "..."} (any non-empty values)
GET  /api/v1/jobs               → 200 {"data": [...50 jobs]}
                                  ⚠️ every 10th call is DEGRADED: still 200, but body {"error": {"code": "degraded"}}
GET  /api/v1/jobs/<id>          → 200 {"data": {...}} for ids 1..50, else 404
POST /api/v1/jobs/<id>/save     header "Authorization: Bearer <token>" → 201, else 401
GET  /health                    → 200
"""

import argparse
import itertools
import secrets
import threading

from flask import Flask, jsonify, request

app = Flask(__name__)
JOBS = {i: {"id": i, "title": f"Backend Engineer #{i}", "company": f"Company {i % 7}"} for i in range(1, 51)}
TOKENS: set[str] = set()
list_calls = itertools.count(1)
lock = threading.Lock()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/login")
def login():
    body = request.get_json(silent=True) or {}
    if not body.get("email") or not body.get("password"):
        return jsonify({"error": {"code": "invalid_credentials"}}), 401
    token = secrets.token_hex(16)
    with lock:
        TOKENS.add(token)
    return {"token": token}


@app.get("/api/v1/jobs")
def list_jobs():
    with lock:
        call = next(list_calls)
    if call % 10 == 0:
        return {"error": {"code": "degraded"}}
    return {"data": list(JOBS.values())}


@app.get("/api/v1/jobs/<int:job_id>")
def get_job(job_id: int):
    if job_id not in JOBS:
        return jsonify({"error": {"code": "not_found"}}), 404
    return {"data": JOBS[job_id]}


@app.post("/api/v1/jobs/<int:job_id>/save")
def save_job(job_id: int):
    token = request.headers.get("Authorization", "").removeprefix("Bearer ")
    with lock:
        valid = token in TOKENS
    if not valid:
        return jsonify({"error": {"code": "unauthorized"}}), 401
    return jsonify({"data": {"job_id": job_id, "saved": True}}), 201


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5092)
    args = parser.parse_args()
    app.run(host="127.0.0.1", port=args.port, threaded=True)
