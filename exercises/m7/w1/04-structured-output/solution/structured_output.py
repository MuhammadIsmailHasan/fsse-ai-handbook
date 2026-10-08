import json


class BadModelOutput(ValueError):
    pass


def _balanced_end(text, start):
    opener = text[start]
    closer = "}" if opener == "{" else "]"
    depth, in_string, escaped = 0, False, False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == opener:
            depth += 1
        elif ch == closer:
            depth -= 1
            if depth == 0:
                return i
    return -1


def extract_json(text):
    for i, ch in enumerate(text):
        if ch in "{[":
            end = _balanced_end(text, i)
            if end == -1:
                continue
            try:
                return json.loads(text[i : end + 1])
            except json.JSONDecodeError:
                continue
    raise BadModelOutput("no JSON found in the reply")


_TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


def validate(data, schema, path="$"):
    problems = []
    expected = schema.get("type")
    if expected and not _TYPES[expected](data):
        return [f"{path}: expected {expected}"]
    if "enum" in schema and data not in schema["enum"]:
        problems.append(f"{path}: must be one of {schema['enum']}")
    if isinstance(data, (int, float)) and not isinstance(data, bool):
        if "minimum" in schema and data < schema["minimum"]:
            problems.append(f"{path}: must be >= {schema['minimum']}")
        if "maximum" in schema and data > schema["maximum"]:
            problems.append(f"{path}: must be <= {schema['maximum']}")
    if isinstance(data, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in data:
                problems.append(f"{path}.{key}: is required")
        for key, value in data.items():
            if key in props:
                problems += validate(value, props[key], f"{path}.{key}")
            elif schema.get("additionalProperties") is False:
                problems.append(f"{path}.{key}: unknown key")
    if isinstance(data, list) and "items" in schema:
        for i, item in enumerate(data):
            problems += validate(item, schema["items"], f"{path}[{i}]")
    return problems


def extract_with_retry(ask, prompt, schema, max_attempts=3):
    current = prompt
    problems = []
    for _ in range(max_attempts):
        reply = ask(current)
        try:
            data = extract_json(reply)
            problems = validate(data, schema)
        except BadModelOutput as error:
            problems = [str(error)]
        else:
            if not problems:
                return data
        current = prompt + "\n\nYour previous answer was invalid: " + "; ".join(problems) + "\nReply with valid JSON only."
    raise BadModelOutput("; ".join(problems))
