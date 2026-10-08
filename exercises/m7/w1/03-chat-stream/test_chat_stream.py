import json
import types

import pytest

from chat_stream import Conversation, StreamError, collect_stream, to_sse


def make_stream(chunks=("Hel", "lo"), stop="end_turn", in_tokens=12, out_tokens=5, extra=()):
    events = [
        {"type": "message_start", "message": {"usage": {"input_tokens": in_tokens}}},
        {"type": "ping"},
        {"type": "content_block_start", "index": 0, "content_block": {"type": "text"}},
        *extra,
    ]
    for chunk in chunks:
        events.append({"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": chunk}})
    events += [
        {"type": "content_block_stop", "index": 0},
        {"type": "message_delta", "delta": {"stop_reason": stop}, "usage": {"output_tokens": out_tokens}},
        {"type": "message_stop"},
    ]
    return events


# ---- Conversation

def test_conversation_builds_a_request():
    chat = Conversation()
    chat.add_user("Hi")
    chat.add_assistant("Hello!")
    chat.add_user("What is a token?")
    assert chat.to_request("some-model", 500) == {
        "model": "some-model",
        "max_tokens": 500,
        "messages": [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
            {"role": "user", "content": "What is a token?"},
        ],
    }


def test_system_prompt_goes_in_its_own_key():
    chat = Conversation(system="You are a help-desk bot.")
    chat.add_user("Hi")
    request = chat.to_request("m", 100)
    assert request["system"] == "You are a help-desk bot."
    assert all(m["role"] != "system" for m in request["messages"])
    assert "system" not in (lambda c: (c.add_user("x"), c.to_request("m", 1))[1])(Conversation())


def test_first_message_must_be_user():
    with pytest.raises(ValueError):
        Conversation().add_assistant("I speak first")


def test_roles_must_alternate():
    chat = Conversation()
    chat.add_user("a")
    with pytest.raises(ValueError):
        chat.add_user("b")
    chat.add_assistant("c")
    with pytest.raises(ValueError):
        chat.add_assistant("d")


def test_request_messages_are_a_copy():
    chat = Conversation()
    chat.add_user("a")
    request = chat.to_request("m", 1)
    request["messages"].append({"role": "assistant", "content": "x"})
    request["messages"][0]["content"] = "changed"
    assert chat.to_request("m", 1)["messages"] == [{"role": "user", "content": "a"}]


# ---- collect_stream

def test_collect_stream():
    assert collect_stream(make_stream()) == {
        "text": "Hello", "stop_reason": "end_turn", "input_tokens": 12, "output_tokens": 5
    }


def test_thinking_and_unknown_events_are_ignored():
    extra = [
        {"type": "content_block_delta", "index": 0, "delta": {"type": "thinking_delta", "thinking": "hmm"}},
        {"type": "something_new", "x": 1},
    ]
    assert collect_stream(make_stream(extra=extra))["text"] == "Hello"


def test_collect_stream_accepts_any_iterable_including_a_generator():
    gen = (e for e in make_stream(chunks=("a", "b", "c")))
    assert collect_stream(gen)["text"] == "abc"


def test_max_tokens_stop_reason_is_reported():
    assert collect_stream(make_stream(stop="max_tokens"))["stop_reason"] == "max_tokens"


def test_error_event_raises():
    events = make_stream()[:4] + [{"type": "error", "error": {"type": "overloaded_error", "message": "Overloaded"}}]
    with pytest.raises(StreamError, match="overloaded_error: Overloaded"):
        collect_stream(events)


def test_stream_that_stops_early_raises():
    with pytest.raises(StreamError, match="ended early"):
        collect_stream(make_stream()[:-1])


# ---- to_sse

def parse(lines):
    out = []
    for line in lines:
        assert line.startswith("data: ") and line.endswith("\n\n")
        body = line[len("data: "):-2]
        out.append(body if body == "[DONE]" else json.loads(body))
    return out


def test_to_sse_normal_stream():
    assert parse(to_sse(make_stream())) == [{"token": "Hel"}, {"token": "lo"}, "[DONE]"]


def test_to_sse_keeps_newlines_inside_json():
    lines = list(to_sse(make_stream(chunks=("a\nb\n\nc",))))
    assert parse(lines) == [{"token": "a\nb\n\nc"}, "[DONE]"]
    assert lines[0].count("\n\n") == 1


def test_to_sse_marks_truncated_answers():
    assert parse(to_sse(make_stream(stop="max_tokens"))) == [
        {"token": "Hel"}, {"token": "lo"}, {"truncated": True}, "[DONE]"
    ]


def test_to_sse_error_event_ends_without_done():
    events = make_stream()[:4] + [{"type": "error", "error": {"type": "overloaded_error", "message": "x"}}]
    assert parse(to_sse(events)) == [{"token": "Hel"}, {"error": "overloaded_error"}]


def test_to_sse_early_end_is_an_error_event():
    assert parse(to_sse(make_stream()[:-1]))[-1] == {"error": "stream_ended_early"}


def test_to_sse_is_lazy():
    pulled = []

    def source():
        for event in make_stream(chunks=("a", "b", "c")):
            pulled.append(event["type"])
            yield event

    sse = to_sse(source())
    assert isinstance(sse, types.GeneratorType)
    assert pulled == []                       # nothing read yet
    first = next(sse)
    assert json.loads(first[6:-2]) == {"token": "a"}
    assert pulled.count("content_block_delta") == 1     # only as far as the first token
