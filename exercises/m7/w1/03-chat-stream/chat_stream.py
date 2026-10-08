"""Module 7 · W1 — Chat messages and streaming events (no API key needed).

The Messages API is stateless: you send the whole conversation every time. A streaming reply
arrives as a series of small events. This exercise builds the two pieces around that:
a Conversation and a stream reader, using the real event shapes.
"""

import json  # noqa: F401  (you will want it)
from collections.abc import Iterable, Iterator


class StreamError(Exception):
    """The stream ended with an error event."""


class Conversation:
    """Keeps the message list for a chat.

    add_user(text) / add_assistant(text) append {"role": ..., "content": text}.
    Rules: the first message must be a user message (adding an assistant message first: ValueError);
    two messages in a row from the same role: ValueError.

    to_request(model, max_tokens) -> {"model": ..., "max_tokens": ..., "messages": [...]}
        - add a "system" key ONLY if a system prompt was given
        - "messages" is a COPY: changing it must not change the conversation
    """

    def __init__(self, system: str | None = None) -> None:
        raise NotImplementedError

    def add_user(self, text: str) -> None:
        raise NotImplementedError

    def add_assistant(self, text: str) -> None:
        raise NotImplementedError

    def to_request(self, model: str, max_tokens: int) -> dict:
        raise NotImplementedError


def collect_stream(events: Iterable[dict]) -> dict:
    """Read a whole stream and return
        {"text": str, "stop_reason": str | None, "input_tokens": int, "output_tokens": int}

    Event shapes (like the real API):
      {"type": "message_start", "message": {"usage": {"input_tokens": 12}}}
      {"type": "content_block_start", "index": 0, "content_block": {"type": "text"}}
      {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "Hel"}}
      {"type": "content_block_delta", "index": 0, "delta": {"type": "thinking_delta", "thinking": "..."}}
      {"type": "content_block_stop", "index": 0}
      {"type": "message_delta", "delta": {"stop_reason": "end_turn"}, "usage": {"output_tokens": 5}}
      {"type": "message_stop"}
      {"type": "ping"}
      {"type": "error", "error": {"type": "overloaded_error", "message": "Overloaded"}}

    - join the text deltas; IGNORE thinking deltas and event types you do not know
    - raise StreamError("<error type>: <message>") on an error event
    - if the stream ends without a message_stop, raise StreamError("stream ended early")
    """
    raise NotImplementedError


def to_sse(events: Iterable[dict]) -> Iterator[str]:
    """Forward a model stream to a browser as Server-Sent Events (the format from Module 3).

    - for each text delta:        'data: {"token": "<text>"}\\n\\n'   (use json.dumps)
    - if the stop reason is "max_tokens", before the end:  'data: {"truncated": true}\\n\\n'
    - normal end:                 'data: [DONE]\\n\\n'
    - on an error event OR a stream that ends early: 'data: {"error": "<error type or stream_ended_early>"}\\n\\n'
      and then STOP (no [DONE]).
    Thinking deltas and unknown events produce nothing. This must be a generator (lazy).
    """
    raise NotImplementedError
