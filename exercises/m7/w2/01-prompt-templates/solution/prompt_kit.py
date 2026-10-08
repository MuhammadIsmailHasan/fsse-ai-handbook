import hashlib
import re


class PromptError(ValueError):
    pass


_PLACEHOLDER = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")


def render(template, variables):
    names = set(_PLACEHOLDER.findall(template))
    missing = sorted(names - set(variables))
    if missing:
        raise PromptError("missing: " + ", ".join(missing))
    unused = sorted(set(variables) - names)
    if unused:
        raise PromptError("unused: " + ", ".join(unused))
    return _PLACEHOLDER.sub(lambda m: str(variables[m.group(1)]), template)


def wrap_untrusted(text, tag="user_input"):
    safe = re.sub(r"<(/?)(" + re.escape(tag) + ")", lambda m: "&lt;" + m.group(1) + m.group(2), text, flags=re.IGNORECASE)
    return f"<{tag}>\n{safe}\n</{tag}>"


def fingerprint(template):
    lines = [line.rstrip() for line in template.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()[:12]


def _parse(version):
    if not re.fullmatch(r"\d+\.\d+\.\d+", version or ""):
        raise PromptError(f"bad version: {version}")
    return tuple(int(p) for p in version.split("."))


class PromptRegistry:
    def __init__(self):
        self._items = {}

    def register(self, name, version, template):
        key = _parse(version)
        versions = self._items.setdefault(name, {})
        if key in versions:
            raise PromptError(f"already registered: {name}@{version}")
        versions[key] = template

    def get(self, name, version=None):
        versions = self._items.get(name, {})
        if version is None:
            if not versions:
                raise PromptError(f"unknown prompt: {name}@latest")
            return versions[max(versions)]
        key = _parse(version)
        if key not in versions:
            raise PromptError(f"unknown prompt: {name}@{version}")
        return versions[key]

    def versions(self, name):
        return [".".join(map(str, k)) for k in sorted(self._items.get(name, {}))]


def check_cases(render_fn, cases):
    failures = []
    for case in cases:
        name = case["name"]
        try:
            prompt = render_fn(case["vars"])
        except PromptError as error:
            failures.append(f"{name}: render failed: {error}")
            continue
        for text in case.get("must_contain", []):
            if text not in prompt:
                failures.append(f"{name}: missing {text!r}")
        for text in case.get("must_not_contain", []):
            if text in prompt:
                failures.append(f"{name}: found forbidden {text!r}")
        if "max_chars" in case and len(prompt) > case["max_chars"]:
            failures.append(f"{name}: too long ({len(prompt)} > {case['max_chars']})")
    return failures
