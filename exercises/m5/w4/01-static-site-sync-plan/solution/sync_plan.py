"""Static site deploy planner. See README.md."""

import hashlib
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Upload:
    key: str
    content_type: str
    cache_control: str


@dataclass(frozen=True)
class Plan:
    uploads: list[Upload]
    deletes: list[str]
    invalidations: list[str]


IMMUTABLE = "public, max-age=31536000, immutable"
REVALIDATE = "public, max-age=0, must-revalidate"
DEFAULT = "public, max-age=3600"
HASHED = re.compile(r"\.[0-9a-f]{8,}\.[a-z0-9]+$", re.IGNORECASE)
TYPES = {
    "html": "text/html; charset=utf-8",
    "css": "text/css; charset=utf-8",
    "js": "text/javascript; charset=utf-8",
    "mjs": "text/javascript; charset=utf-8",
    "json": "application/json",
    "map": "application/json",
    "svg": "image/svg+xml",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
    "avif": "image/avif",
    "ico": "image/x-icon",
    "woff2": "font/woff2",
    "txt": "text/plain; charset=utf-8",
    "xml": "application/xml",
}


def _immutable(path: str) -> bool:
    return path.startswith(("_next/static/", "assets/")) or bool(HASHED.search(path.rsplit("/", 1)[-1]))


def cache_control(path: str) -> str:
    if _immutable(path):
        return IMMUTABLE  # content-addressed: the URL changes when the content does
    if path.endswith(".html") or path.rsplit("/", 1)[-1] == "sw.js":
        return REVALIDATE  # entry points must always be fresh
    return DEFAULT


def content_type(path: str) -> str:
    extension = path.rsplit(".", 1)[-1].lower() if "." in path.rsplit("/", 1)[-1] else ""
    return TYPES.get(extension, "application/octet-stream")


def _validate(path: str) -> None:
    if not path or path.startswith("/") or "\\" in path or ".." in path.split("/"):
        raise ValueError(f"invalid path: {path!r}")


def _group(path: str) -> int:
    if _immutable(path):
        return 0
    return 2 if path.endswith(".html") else 1


def plan(local: dict[str, bytes], remote: dict[str, str], *, delete: bool = True) -> Plan:
    for path in local:
        _validate(path)

    changed = [path for path, content in local.items() if remote.get(path, "").strip('"') != hashlib.md5(content).hexdigest()]
    changed.sort(key=lambda path: (_group(path), path))
    uploads = [Upload(path, content_type(path), cache_control(path)) for path in changed]
    deletes = sorted(set(remote) - set(local)) if delete else []

    paths: set[str] = set()
    for path in [*changed, *deletes]:
        if _immutable(path):
            continue
        paths.add("/" + path)
        if path == "index.html" or path.endswith("/index.html"):
            paths.add("/" + path[: -len("index.html")])
    invalidations = ["/*"] if len(paths) > 15 else sorted(paths)
    return Plan(uploads, deletes, invalidations)
