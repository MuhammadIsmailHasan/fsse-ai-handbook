"""Module 3 · W3 — Check a FastAPI project layout (solution)."""

ALLOWED: dict[str, set[str]] = {
    "routers": {"services", "schemas"},
    "services": {"repositories", "schemas", "models"},
    "repositories": {"models"},
    "schemas": set(),
    "models": set(),
    "core": set(),
}


def layer_of(module: str) -> str:
    parts = module.split(".")
    return parts[1] if len(parts) > 1 else ""


def find_violations(imports: dict[str, list[str]]) -> list[tuple[str, str]]:
    found = []
    for importer, imported_list in imports.items():
        if not importer.startswith("app."):
            continue
        src = layer_of(importer)
        if src == "main":
            continue
        for imported in imported_list:
            if not imported.startswith("app."):
                continue
            dst = layer_of(imported)
            if dst == src or dst == "core":
                continue
            if dst not in ALLOWED.get(src, set()):
                found.append((importer, imported))
    return sorted(found)


def find_cycle(imports: dict[str, list[str]]) -> list[str] | None:
    visiting: list[str] = []
    done: set[str] = set()

    def visit(node: str) -> list[str] | None:
        if node in visiting:
            return visiting[visiting.index(node):] + [node]
        if node in done or node not in imports:
            return None
        visiting.append(node)
        for nxt in imports[node]:
            cycle = visit(nxt)
            if cycle:
                return cycle
        visiting.pop()
        done.add(node)
        return None

    for start in imports:
        cycle = visit(start)
        if cycle:
            return cycle
    return None
