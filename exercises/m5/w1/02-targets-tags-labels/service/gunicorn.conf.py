"""Gunicorn settings, all overridable with environment variables.

Run:  gunicorn -c gunicorn.conf.py wsgi:app
"""

import multiprocessing
import os

port = int(os.environ.get("PORT", "5091"))
bind = f"0.0.0.0:{port}"

# Workers: processes. Default (2 × CPU) + 1, capped so we don't exhaust DB connections.
workers = int(os.environ.get("WEB_CONCURRENCY", min(multiprocessing.cpu_count() * 2 + 1, 8)))
threads = int(os.environ.get("GUNICORN_THREADS", "1"))
worker_class = "gthread" if threads > 1 else "sync"

timeout = int(os.environ.get("GUNICORN_TIMEOUT", "30"))  # kill a worker stuck on one request
graceful_timeout = 30  # time to finish in-flight requests on SIGTERM
keepalive = 5

# Recycle workers periodically to contain slow memory leaks; jitter avoids all restarting together.
max_requests = 1000
max_requests_jitter = 100

# Logs to stdout/stderr — the platform collects them.
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("LOG_LEVEL", "info").lower()

# Only trust X-Forwarded-* from the proxy's address.
forwarded_allow_ips = os.environ.get("FORWARDED_ALLOW_IPS", "127.0.0.1")
