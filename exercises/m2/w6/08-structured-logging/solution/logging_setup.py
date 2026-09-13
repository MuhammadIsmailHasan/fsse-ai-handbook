"""JSON logs to stdout, with request ids and secret redaction."""

import json
import logging
import sys
import traceback
from contextvars import ContextVar
from datetime import UTC, datetime

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

SENSITIVE = ("password", "secret", "token", "authorization", "api_key", "apikey", "cookie")
REDACTED = "[REDACTED]"
# Attributes every LogRecord has — anything else came from `extra=`.
STANDARD_ATTRS = set(vars(logging.LogRecord("", 0, "", 0, "", (), None))) | {"message", "asctime", "taskName"}


def redact(value):
    if isinstance(value, dict):
        return {k: REDACTED if any(s in str(k).lower() for s in SENSITIVE) else redact(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact(v) for v in value]
    return value


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        request_id = request_id_var.get()
        if request_id is not None:
            entry["request_id"] = request_id
        extras = {k: v for k, v in vars(record).items() if k not in STANDARD_ATTRS and not k.startswith("_")}
        entry.update(redact(extras))
        if record.exc_info and record.exc_info[0] is not None:
            exc_type, exc, tb = record.exc_info
            entry["exc_type"] = exc_type.__name__
            entry["exc_message"] = str(exc)
            entry["stack"] = "".join(traceback.format_exception(exc_type, exc, tb))
        return json.dumps(entry, default=str, ensure_ascii=False)


def configure_logging(level: str = "INFO", stream=None) -> None:
    root = logging.getLogger()
    for handler in list(root.handlers):
        if getattr(handler, "_fsse_json", False):
            root.removeHandler(handler)
    handler = logging.StreamHandler(stream or sys.stdout)
    handler.setFormatter(JsonFormatter())
    handler._fsse_json = True  # type: ignore[attr-defined]
    root.addHandler(handler)
    root.setLevel(level.upper())
