"""Reference solution. See README.md."""

import re

_BLANK = re.compile(r"\{\{\s*\.Values\.(\w+)\s*\}\}")


def render(template: str, values: dict) -> str:
    def fill(match: re.Match) -> str:
        name = match.group(1)
        if name not in values:
            raise KeyError(name)
        return str(values[name])

    return _BLANK.sub(fill, template)
