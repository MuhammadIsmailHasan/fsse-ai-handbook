"""A tiny WSGI app (no framework) so the Docker exercise has something to run."""

import os


def app(environ, start_response):
    greeting = os.environ.get("GREETING", "Hello from a container!")
    body = f"{greeting}\n".encode()
    start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8"), ("Content-Length", str(len(body)))])
    return [body]
