"""JSON logs to stdout, with request ids and secret redaction. See README.md."""

import logging
from contextvars import ContextVar

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


def redact(value):
    raise NotImplementedError


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        raise NotImplementedError


def configure_logging(level: str = "INFO", stream=None) -> None:
    raise NotImplementedError
