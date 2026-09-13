"""Per-request ids and one access log line per request. See README.md."""

from flask import Flask


def init_request_logging(app: Flask) -> None:
    raise NotImplementedError
