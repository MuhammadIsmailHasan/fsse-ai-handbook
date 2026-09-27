"""Reference solution. See README.md."""


def pick_backend(path: str, routes: list[tuple[str, str]]) -> str | None:
    best_prefix = None
    best_backend = None

    for prefix, backend in routes:
        if path.startswith(prefix):
            if best_prefix is None or len(prefix) > len(best_prefix):
                best_prefix = prefix
                best_backend = backend

    return best_backend
