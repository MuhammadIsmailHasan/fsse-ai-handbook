import json


class TooManySteps(RuntimeError):
    pass


class Tool:
    def __init__(self, name, description, required, fn):
        self.name, self.description, self.required, self.fn = name, description, required, fn

    def schema(self):
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {"type": "object", "required": list(self.required)},
        }


def run_tool_call(tools, call, ctx):
    def result(content, error=False):
        block = {"type": "tool_result", "tool_use_id": call["id"], "content": content}
        if error:
            block["is_error"] = True
        return block

    tool = tools.get(call["name"])
    if tool is None:
        return result(f"unknown tool: {call['name']}", True)
    missing = sorted(set(tool.required) - set(call.get("input", {})))
    if missing:
        return result("missing required input: " + ", ".join(missing), True)
    try:
        value = tool.fn(ctx, **call.get("input", {}))
    except Exception as error:  # noqa: BLE001
        return result(f"tool failed: {type(error).__name__}: {error}", True)
    return result(value if isinstance(value, str) else json.dumps(value))


def run_agent(llm, tools, user_message, ctx, max_steps=5):
    registry = {t.name: t for t in tools}
    messages = [{"role": "user", "content": user_message}]
    for step in range(1, max_steps + 1):
        reply = llm([dict(m) for m in messages])
        messages.append({"role": "assistant", "content": reply["content"]})
        if reply["stop_reason"] != "tool_use":
            text = "".join(b["text"] for b in reply["content"] if b["type"] == "text")
            return {"text": text, "messages": messages, "steps": step}
        results = [run_tool_call(registry, b, ctx) for b in reply["content"] if b["type"] == "tool_use"]
        messages.append({"role": "user", "content": results})
    raise TooManySteps(f"no final answer after {max_steps} steps")
