import json

import pytest

from local_llm import FallbackClient, LocalModelError, OllamaClient, build_chat_payload, collect_ollama_stream


def line(content="", done=False, **extra):
    return json.dumps({"model": "m", "message": {"role": "assistant", "content": content}, "done": done, **extra})


GOOD = [
    line("Hel"),
    line("lo"),
    line("", True, done_reason="stop", prompt_eval_count=14, eval_count=6),
]


def test_payload_without_options():
    messages = [{"role": "user", "content": "Hi"}]
    assert build_chat_payload("llama3.2", messages) == {"model": "llama3.2", "messages": messages, "stream": True}


def test_payload_with_options_and_no_stream():
    payload = build_chat_payload("llama3.2", [], stream=False, options={"temperature": 0.2})
    assert payload["stream"] is False and payload["options"] == {"temperature": 0.2}
    assert "options" not in build_chat_payload("m", [], options={})
    assert "options" not in build_chat_payload("m", [], options=None)


def test_payload_copies_the_messages():
    messages = [{"role": "user", "content": "Hi"}]
    payload = build_chat_payload("m", messages)
    payload["messages"][0]["content"] = "changed"
    payload["messages"].append({})
    assert messages == [{"role": "user", "content": "Hi"}]


def test_collect_stream():
    assert collect_ollama_stream(GOOD) == {
        "text": "Hello", "done_reason": "stop", "prompt_tokens": 14, "completion_tokens": 6
    }


def test_blank_lines_are_skipped_and_generators_work():
    lines = (x for x in [line("A"), "", "   ", line("B"), line("", True, done_reason="length", eval_count=2)])
    result = collect_ollama_stream(lines)
    assert result["text"] == "AB" and result["done_reason"] == "length"
    assert result["completion_tokens"] == 2 and result["prompt_tokens"] == 0


def test_error_line():
    with pytest.raises(LocalModelError, match="model 'x' not found"):
        collect_ollama_stream([json.dumps({"error": "model 'x' not found"})])


def test_bad_json_line():
    with pytest.raises(LocalModelError, match="bad line"):
        collect_ollama_stream([line("A"), "{not json"])


def test_stream_without_a_done_line():
    with pytest.raises(LocalModelError, match="ended early"):
        collect_ollama_stream([line("A"), line("B")])


def test_client_sends_the_request_and_returns_the_text():
    seen = {}

    def post(url, payload):
        seen["url"], seen["payload"] = url, payload
        return GOOD

    client = OllamaClient("llama3.2", post, host="http://localhost:11491/", options={"temperature": 0})
    assert client.complete([{"role": "user", "content": "Hi"}]) == "Hello"
    assert seen["url"] == "http://localhost:11491/api/chat"
    assert seen["payload"] == {
        "model": "llama3.2",
        "messages": [{"role": "user", "content": "Hi"}],
        "stream": True,
        "options": {"temperature": 0},
    }


def test_default_host():
    seen = {}
    OllamaClient("m", lambda url, payload: seen.setdefault("url", url) and GOOD).complete([])
    assert seen["url"] == "http://localhost:11434/api/chat"


def test_server_not_running_becomes_a_clear_error():
    def post(url, payload):
        raise ConnectionError("refused")

    with pytest.raises(LocalModelError, match="not running"):
        OllamaClient("m", post).complete([])


class Fake:
    def __init__(self, answer=None, error=None):
        self.answer, self.error, self.calls = answer, error, 0

    def complete(self, messages):
        self.calls += 1
        if self.error:
            raise self.error
        return self.answer


def test_fallback_uses_the_primary_when_it_works():
    primary, secondary = Fake("local"), Fake("cloud")
    client = FallbackClient(primary, secondary)
    assert client.last_used is None
    assert client.complete([]) == "local"
    assert client.last_used == "primary" and secondary.calls == 0


def test_fallback_switches_on_local_errors():
    for error in (LocalModelError("down"), ConnectionError("refused")):
        client = FallbackClient(Fake(error=error), Fake("cloud"))
        assert client.complete([]) == "cloud"
        assert client.last_used == "secondary"


def test_fallback_with_both_failing_raises_the_secondary_error():
    client = FallbackClient(Fake(error=LocalModelError("local down")), Fake(error=RuntimeError("cloud down")))
    with pytest.raises(RuntimeError, match="cloud down"):
        client.complete([])


def test_bugs_are_not_hidden():
    secondary = Fake("cloud")
    client = FallbackClient(Fake(error=ValueError("a bug in my code")), secondary)
    with pytest.raises(ValueError):
        client.complete([])
    assert secondary.calls == 0


def test_the_next_call_tries_the_primary_again():
    primary = Fake("local")
    client = FallbackClient(primary, Fake("cloud"))
    primary.error = LocalModelError("down")
    client.complete([])
    primary.error = None
    assert client.complete([]) == "local"
    assert client.last_used == "primary"
