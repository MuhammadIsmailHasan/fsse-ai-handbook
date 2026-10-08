import json


class LocalModelError(Exception):
    pass


def build_chat_payload(model, messages, *, stream=True, options=None):
    payload = {"model": model, "messages": [dict(m) for m in messages], "stream": stream}
    if options:
        payload["options"] = dict(options)
    return payload


def collect_ollama_stream(lines):
    text, done = [], None
    for line in lines:
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            raise LocalModelError("bad line from the model server") from None
        if "error" in obj:
            raise LocalModelError(obj["error"])
        text.append(obj.get("message", {}).get("content", ""))
        if obj.get("done"):
            done = obj
            break
    if done is None:
        raise LocalModelError("stream ended early")
    return {
        "text": "".join(text),
        "done_reason": done.get("done_reason", ""),
        "prompt_tokens": done.get("prompt_eval_count", 0),
        "completion_tokens": done.get("eval_count", 0),
    }


class OllamaClient:
    def __init__(self, model, post, host="http://localhost:11434", options=None):
        self.model, self.post, self.host, self.options = model, post, host.rstrip("/"), options

    def complete(self, messages):
        payload = build_chat_payload(self.model, messages, options=self.options)
        try:
            lines = self.post(self.host + "/api/chat", payload)
            return collect_ollama_stream(lines)["text"]
        except ConnectionError:
            raise LocalModelError("local model server is not running") from None


class FallbackClient:
    def __init__(self, primary, secondary):
        self.primary, self.secondary, self.last_used = primary, secondary, None

    def complete(self, messages):
        try:
            answer = self.primary.complete(messages)
            self.last_used = "primary"
            return answer
        except (LocalModelError, ConnectionError):
            answer = self.secondary.complete(messages)
            self.last_used = "secondary"
            return answer
