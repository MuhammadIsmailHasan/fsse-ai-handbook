import json


class StreamError(Exception):
    pass


class Conversation:
    def __init__(self, system=None):
        self.system = system
        self.messages = []

    def _add(self, role, text):
        if role == "assistant" and not self.messages:
            raise ValueError("the first message must come from the user")
        if self.messages and self.messages[-1]["role"] == role:
            raise ValueError(f"two {role} messages in a row")
        self.messages.append({"role": role, "content": text})

    def add_user(self, text):
        self._add("user", text)

    def add_assistant(self, text):
        self._add("assistant", text)

    def to_request(self, model, max_tokens):
        request = {"model": model, "max_tokens": max_tokens, "messages": [dict(m) for m in self.messages]}
        if self.system:
            request["system"] = self.system
        return request


def collect_stream(events):
    text, stop_reason, in_tokens, out_tokens, finished = [], None, 0, 0, False
    for event in events:
        kind = event.get("type")
        if kind == "message_start":
            in_tokens = event["message"].get("usage", {}).get("input_tokens", 0)
        elif kind == "content_block_delta" and event["delta"].get("type") == "text_delta":
            text.append(event["delta"]["text"])
        elif kind == "message_delta":
            stop_reason = event["delta"].get("stop_reason", stop_reason)
            out_tokens = event.get("usage", {}).get("output_tokens", out_tokens)
        elif kind == "message_stop":
            finished = True
        elif kind == "error":
            err = event["error"]
            raise StreamError(f"{err['type']}: {err['message']}")
    if not finished:
        raise StreamError("stream ended early")
    return {"text": "".join(text), "stop_reason": stop_reason, "input_tokens": in_tokens, "output_tokens": out_tokens}


def to_sse(events):
    stop_reason, finished = None, False
    for event in events:
        kind = event.get("type")
        if kind == "content_block_delta" and event["delta"].get("type") == "text_delta":
            yield f"data: {json.dumps({'token': event['delta']['text']})}\n\n"
        elif kind == "message_delta":
            stop_reason = event["delta"].get("stop_reason", stop_reason)
        elif kind == "message_stop":
            finished = True
            break
        elif kind == "error":
            yield f"data: {json.dumps({'error': event['error']['type']})}\n\n"
            return
    if not finished:
        yield f"data: {json.dumps({'error': 'stream_ended_early'})}\n\n"
        return
    if stop_reason == "max_tokens":
        yield f"data: {json.dumps({'truncated': True})}\n\n"
    yield "data: [DONE]\n\n"
