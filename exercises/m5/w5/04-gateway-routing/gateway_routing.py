"""Route a request path to the right backend. See README.md."""


def pick_backend(path: str, routes: list[tuple[str, str]]) -> str | None:
    raise NotImplementedError
