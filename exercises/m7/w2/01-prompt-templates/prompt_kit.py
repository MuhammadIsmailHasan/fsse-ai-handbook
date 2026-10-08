"""Module 7 · W2 — Prompts as code (no API key needed).

Prompts are part of your program: they have inputs, versions and tests.
This kit gives you a strict template, a safe way to include untrusted text,
a versioned registry and a tiny regression-test runner.
"""

import hashlib  # noqa: F401  (you will want it)
import re  # noqa: F401


class PromptError(ValueError):
    """Anything wrong with a template, its variables or a version."""


def render(template: str, variables: dict) -> str:
    """Fill {{name}} placeholders (letters, digits, underscore; spaces inside the braces are allowed: {{ name }}).

    Be STRICT, because a silent typo in a prompt is a bug nobody sees:
      - a placeholder with no value        -> PromptError("missing: a, b")   (names sorted, comma + space)
      - a value that no placeholder uses   -> PromptError("unused: x")       (names sorted)
      - check "missing" first, then "unused"
    Values are converted with str(). Single braces like {"a": 1} (JSON) are NOT placeholders and stay as they are.
    A value that itself contains {{...}} must NOT be filled again.
    """
    raise NotImplementedError


def wrap_untrusted(text: str, tag: str = "user_input") -> str:
    """Put untrusted text between tags so the model can tell it is DATA, not instructions:

        <user_input>
        ...text...
        </user_input>

    The text must not be able to close the tag early: replace every "<tag" and "</tag" (any letter case)
    that appears INSIDE the text by "&lt;tag" / "&lt;/tag" (keep the original letters after the "&lt;").
    """
    raise NotImplementedError


def fingerprint(template: str) -> str:
    """A short id for a prompt text: the first 12 hex characters of the SHA-256 of the template after
    (1) removing trailing spaces at the end of every line and (2) removing trailing blank lines at the end.
    Two templates that differ only in that kind of whitespace must give the same fingerprint."""
    raise NotImplementedError


class PromptRegistry:
    """Versioned prompts. Versions look like "1.2.0" (major.minor.patch, numbers only).

    register(name, version, template)   same (name, version) twice -> PromptError("already registered: name@version");
                                        a bad version string -> PromptError("bad version: ...")
    get(name, version=None)             version=None means the HIGHEST version (compare as numbers: 1.10.0 > 1.9.0);
                                        unknown name or version -> PromptError("unknown prompt: name@version") (use "latest" when version is None)
    versions(name)                      all versions of a name, oldest first (as strings); unknown name -> []
    """

    def __init__(self) -> None:
        raise NotImplementedError

    def register(self, name: str, version: str, template: str) -> None:
        raise NotImplementedError

    def get(self, name: str, version: str | None = None) -> str:
        raise NotImplementedError

    def versions(self, name: str) -> list[str]:
        raise NotImplementedError


def check_cases(render_fn, cases: list[dict]) -> list[str]:
    """Run regression cases against a prompt. Each case:
        {"name": str, "vars": dict, "must_contain": [str], "must_not_contain": [str], "max_chars": int}
    (all keys except name and vars are optional). Call render_fn(case["vars"]) to get the prompt text.
    Return a list of failure messages (empty = everything passed), in case order:
        "<name>: missing 'text'"            for every must_contain that is absent
        "<name>: found forbidden 'text'"    for every must_not_contain that is present
        "<name>: too long (N > M)"          when len(prompt) > max_chars
        "<name>: render failed: <error>"    when render_fn raises PromptError (then skip the other checks for that case)
    """
    raise NotImplementedError
