"""Module 7 · W1 — Talking to a local model (Ollama) and falling back to the cloud.

Ollama runs open models on your own machine and has a small HTTP API. This exercise builds the
client WITHOUT needing Ollama installed: the network call is passed in as a function, so tests
can fake it.

Ollama's chat API (POST {host}/api/chat):
  request : {"model": "llama3.2", "messages": [...], "stream": true, "options": {"temperature": 0.2}}
  response: one JSON object per line (NDJSON), for example
      {"model": "llama3.2", "message": {"role": "assistant", "content": "Hel"}, "done": false}
      {"model": "llama3.2", "message": {"role": "assistant", "content": "lo"}, "done": false}
      {"model": "llama3.2", "message": {"role": "assistant", "content": ""}, "done": true,
       "done_reason": "stop", "prompt_eval_count": 14, "eval_count": 6}
  errors  : {"error": "model 'x' not found"}
"""

import json  # noqa: F401  (you will want it)
from collections.abc import Callable, Iterable


class LocalModelError(Exception):
    """The local model server returned an error or an unusable answer."""


def build_chat_payload(model: str, messages: list[dict], *, stream: bool = True, options: dict | None = None) -> dict:
    """{"model", "messages", "stream"} — plus "options" ONLY when options is not empty/None.
    messages is copied, not shared."""
    raise NotImplementedError


def collect_ollama_stream(lines: Iterable[str]) -> dict:
    """Read the NDJSON lines and return
        {"text": str, "done_reason": str, "prompt_tokens": int, "completion_tokens": int}

    - skip blank lines
    - join message.content of every line
    - the last line has "done": true: read done_reason, prompt_eval_count, eval_count from it
    - a line with an "error" key: raise LocalModelError(<the error text>)
    - a line that is not valid JSON: raise LocalModelError("bad line from the model server")
    - the stream ends without a done line: raise LocalModelError("stream ended early")
    """
    raise NotImplementedError


class OllamaClient:
    """complete(messages) -> str

    post(url, payload) -> iterable of NDJSON lines (the real one would use an HTTP library; tests pass a fake).
    The URL is host (without a trailing slash) + "/api/chat". Send the payload from build_chat_payload.
    If post raises ConnectionError, raise LocalModelError("local model server is not running").
    """

    def __init__(self, model: str, post: Callable[[str, dict], Iterable[str]], host: str = "http://localhost:11434",
                 options: dict | None = None) -> None:
        raise NotImplementedError

    def complete(self, messages: list[dict]) -> str:
        raise NotImplementedError


class FallbackClient:
    """Try the primary client (for example the local model); if it raises LocalModelError or
    ConnectionError, use the secondary (for example a cloud API).

    complete(messages) -> str
    self.last_used is "primary" or "secondary" after each call (None before the first call).
    If both fail, raise the SECONDARY's error.
    A different kind of error (for example ValueError) is a bug: do NOT hide it, let it pass up.
    """

    def __init__(self, primary, secondary) -> None:
        raise NotImplementedError

    def complete(self, messages: list[dict]) -> str:
        raise NotImplementedError
