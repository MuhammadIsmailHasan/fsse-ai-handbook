"""Checks for sync_plan.py. Don't edit this file."""

import hashlib

import pytest

from sync_plan import Plan, Upload, cache_control, content_type, plan


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("_next/static/chunks/app-3f9a.js", "public, max-age=31536000, immutable"),
        ("assets/logo.svg", "public, max-age=31536000, immutable"),
        ("js/app.3f9a1c2b.js", "public, max-age=31536000, immutable"),
        ("css/site.3F9A1C2B77.css", "public, max-age=31536000, immutable"),
        ("js/app.3f9a1c.js", "public, max-age=3600"),
        ("index.html", "public, max-age=0, must-revalidate"),
        ("docs/index.html", "public, max-age=0, must-revalidate"),
        ("sw.js", "public, max-age=0, must-revalidate"),
        ("robots.txt", "public, max-age=3600"),
        ("images/logo.png", "public, max-age=3600"),
    ],
)
def test_cache_control(path, expected):
    assert cache_control(path) == expected


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("index.html", "text/html; charset=utf-8"),
        ("a/b/site.CSS", "text/css; charset=utf-8"),
        ("app.mjs", "text/javascript; charset=utf-8"),
        ("data.json", "application/json"),
        ("app.js.map", "application/json"),
        ("logo.svg", "image/svg+xml"),
        ("photo.JPG", "image/jpeg"),
        ("favicon.ico", "image/x-icon"),
        ("font.woff2", "font/woff2"),
        ("sitemap.xml", "application/xml"),
        ("README", "application/octet-stream"),
        ("archive.tar.gz", "application/octet-stream"),
    ],
)
def test_content_type(path, expected):
    assert content_type(path) == expected


def test_first_deploy_orders_uploads_safely():
    local = {
        "index.html": b"<html>v1</html>",
        "about/index.html": b"<html>about</html>",
        "_next/static/chunks/main-a1.js": b"console.log(1)",
        "robots.txt": b"User-agent: *",
        "assets/logo.svg": b"<svg/>",
    }
    result = plan(local, {})
    assert [u.key for u in result.uploads] == ["_next/static/chunks/main-a1.js", "assets/logo.svg", "robots.txt", "about/index.html", "index.html"]
    assert result.uploads[0] == Upload("_next/static/chunks/main-a1.js", "text/javascript; charset=utf-8", "public, max-age=31536000, immutable")
    assert result.deletes == []
    assert result.invalidations == ["/", "/about/", "/about/index.html", "/index.html", "/robots.txt"]


def test_incremental_deploy_with_deletes():
    local = {
        "index.html": b"<html>v2</html>",
        "_next/static/chunks/main-b2.js": b"console.log(2)",
        "robots.txt": b"User-agent: *",
    }
    remote = {
        "index.html": f'"{md5(b"<html>v1</html>")}"',
        "_next/static/chunks/main-a1.js": md5(b"console.log(1)"),
        "robots.txt": f'"{md5(b"User-agent: *")}"',
        "old-page.html": md5(b"old"),
    }
    result = plan(local, remote)
    assert result == Plan(
        uploads=[
            Upload("_next/static/chunks/main-b2.js", "text/javascript; charset=utf-8", "public, max-age=31536000, immutable"),
            Upload("index.html", "text/html; charset=utf-8", "public, max-age=0, must-revalidate"),
        ],
        deletes=["_next/static/chunks/main-a1.js", "old-page.html"],
        invalidations=["/", "/index.html", "/old-page.html"],
    )
    assert plan(local, remote, delete=False).deletes == []
    assert plan(local, remote, delete=False).invalidations == ["/", "/index.html"]


def test_many_changes_invalidate_everything():
    local = {f"page{i}.html": f"<p>{i}</p>".encode() for i in range(20)}
    assert plan(local, {}).invalidations == ["/*"]
    assert plan({"x.html": b"1", **{f"_next/static/c{i}.js": b"x" for i in range(40)}}, {}).invalidations == ["/x.html"]


@pytest.mark.parametrize("bad", ["/index.html", "../secret.txt", "a/../../b.html", "a\\b.html", ""])
def test_rejects_unsafe_paths(bad):
    with pytest.raises(ValueError):
        plan({bad: b"x"}, {})
