"""Module 7 · W2 — The tool-calling loop (no API key needed).

The model never runs your code. It ASKS for a tool call; YOUR program runs it and sends back the result.
This exercise builds that loop around a fake model, with the real message shapes.

Model reply (what `llm(messages)` returns):
    {"stop_reason": "end_turn" | "tool_use" | ..., "content": [ block, ... ]}
  text block      {"type": "text", "text": "..."}
  tool call block {"type": "tool_use", "id": "toolu_1", "name": "get_order", "input": {"order_id": "A1"}}

What you send back after tool calls (ONE user message with ALL the results, in the same order):
    {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": "toolu_1", "content": "<text>"},
        {"type": "tool_result", "tool_use_id": "toolu_2", "content": "<text>", "is_error": True},
    ]}
"""

import json  # noqa: F401  (you will want it)
from collections.abc import Callable


class TooManySteps(RuntimeError):
    """The model kept asking for tools and never gave a final answer."""


class Tool:
    """A tool the model may call.

    name, description, required (list of input keys that must be present), fn.
    fn(ctx, **input) -> str | dict | list    `ctx` is data from YOUR app (for example the logged-in user),
    NEVER from the model. fn may raise; that is not a crash, it becomes an error result.
    """

    def __init__(self, name: str, description: str, required: list[str], fn: Callable) -> None:
        self.name, self.description, self.required, self.fn = name, description, required, fn

    def schema(self) -> dict:
        """The definition you would send to the API:
        {"name", "description", "input_schema": {"type": "object", "required": [...]}}"""
        raise NotImplementedError


def run_tool_call(tools: dict[str, Tool], call: dict, ctx: dict) -> dict:
    """Run ONE tool_use block and return its tool_result block.

    - unknown tool name            -> is_error result with content "unknown tool: <name>"
    - a required key is missing    -> is_error result with content "missing required input: a, b" (sorted)
    - fn raised an exception       -> is_error result with content "tool failed: <ExceptionClass>: <message>"
    - success: content is fn's return value as text: a str stays as it is, anything else becomes json.dumps(value)
    A successful result has NO "is_error" key. Never let an exception escape.
    The result always has "type": "tool_result" and "tool_use_id": call["id"].
    """
    raise NotImplementedError


def run_agent(llm: Callable[[list[dict]], dict], tools: list[Tool], user_message: str, ctx: dict, max_steps: int = 5) -> dict:
    """Run the loop until the model gives a final answer.

    messages starts as [{"role": "user", "content": user_message}].
    Each step: reply = llm(messages) (give the model a COPY of the list so later changes to `messages` do not rewrite history it saw)
      - append {"role": "assistant", "content": reply["content"]}
      - if reply["stop_reason"] != "tool_use": finish.
      - otherwise run EVERY tool_use block (in order) with run_tool_call and append ONE user message
        {"role": "user", "content": [all the tool_result blocks]}.
    Return {"text": <the text blocks of the final reply joined with "">, "messages": messages, "steps": number of llm calls}.
    If the model has not finished after max_steps llm calls, raise TooManySteps.
    """
    raise NotImplementedError
