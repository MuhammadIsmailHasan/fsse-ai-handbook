"""Module 7 · W1 — Getting JSON you can trust out of a model (no API key needed).

Even when a model "usually" returns JSON, you must check it. This exercise builds the
three safety nets: pull the JSON out of the text, validate it against a schema,
and re-ask the model with the errors when it is wrong.
"""

import json  # noqa: F401  (you will want it)
from collections.abc import Callable
from typing import Any


class BadModelOutput(ValueError):
    """The model's answer could not be turned into valid data."""


def extract_json(text: str) -> Any:
    """Find and parse the JSON value in a model reply.

    Handle:  plain JSON  |  ```json fenced blocks ```  |  prose before or after the JSON.
    Take the FIRST complete top-level object {...} or array [...] you can parse.
    Careful: braces inside strings ("a } b") must not confuse you.
    Raise BadModelOutput if there is no JSON or it does not parse.
    """
    raise NotImplementedError


def validate(data: Any, schema: dict, path: str = "$") -> list[str]:
    """Return a list of problems (empty = valid). Each problem starts with the path, e.g. "$.age: ...".

    Support this small subset of JSON Schema:
      type: "object" | "array" | "string" | "integer" | "number" | "boolean" | "null"
            (a bool is NOT an integer or a number; an integer IS a number)
      properties, required, additionalProperties (False = no unknown keys)
      enum, items, minimum, maximum
    """
    raise NotImplementedError


def extract_with_retry(ask: Callable[[str], str], prompt: str, schema: dict, max_attempts: int = 3) -> Any:
    """Ask the model; if the answer is not valid, ask again with the problems listed.

    ask(prompt_text) -> reply_text
    Attempt 1 uses `prompt` as it is. Every retry sends:
        prompt + "\\n\\nYour previous answer was invalid: " + "; ".join(problems) + "\\nReply with valid JSON only."
    Return the valid data. After max_attempts failures raise BadModelOutput.
    """
    raise NotImplementedError
