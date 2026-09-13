"""Per-request ids and one access log line per request."""

import logging
import re
import time
import uuid

from flask import Flask, g, request

from logging_setup import request_id_var

logger = logging.getLogger("http")
VALID_ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


def init_request_logging(app: Flask) -> None:
    @app.before_request
    def start():
        incoming = request.headers.get("X-Request-ID", "")
        request_id = incoming if VALID_ID.match(incoming) else uuid.uuid4().hex
        g.request_id_token = request_id_var.set(request_id)
        g.request_id = request_id
        g.started = time.perf_counter()

    @app.after_request
    def finish(response):
        response.headers["X-Request-ID"] = g.request_id
        duration_ms = round((time.perf_counter() - g.started) * 1000, 2)
        level = logging.ERROR if response.status_code >= 500 else logging.WARNING if response.status_code >= 400 else logging.INFO
        logger.log(
            level,
            "request completed",
            extra={"method": request.method, "path": request.path, "status": response.status_code, "duration_ms": duration_ms},
        )
        return response

    @app.teardown_request
    def reset(_error=None):
        token = g.pop("request_id_token", None)
        if token is not None:
            request_id_var.reset(token)
