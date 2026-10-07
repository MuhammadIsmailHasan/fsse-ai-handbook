"""Module 3 · W3 — Check a FastAPI project layout.

Modules are named like "app.routers.users". The *layer* is the folder right
after "app": "routers", "schemas", "services", "repositories", "models",
"core" — or "main" for "app.main".

Rules (a layer may import ITS OWN layer, "core", and the layers listed here):

    routers       → services, schemas
    services      → repositories, schemas, models
    repositories  → models
    schemas       → (nothing)
    models        → (nothing)
    core          → (nothing)
    main          → everything

Imports of anything that does not start with "app." (fastapi, sqlalchemy…)
are ignored.
"""

ALLOWED: dict[str, set[str]] = {
    "routers": {"services", "schemas"},
    "services": {"repositories", "schemas", "models"},
    "repositories": {"models"},
    "schemas": set(),
    "models": set(),
    "core": set(),
}


def layer_of(module: str) -> str:
    """'app.routers.users' -> 'routers'; 'app.main' -> 'main'."""
    # YOUR CODE HERE
    return ""


def find_violations(imports: dict[str, list[str]]) -> list[tuple[str, str]]:
    """Return (importer, imported) pairs that break the rules, sorted.

    `imports` maps a module to the modules it imports.
    """
    # YOUR CODE HERE
    return []


def find_cycle(imports: dict[str, list[str]]) -> list[str] | None:
    """Return one circular import as a path like ['a', 'b', 'a'], or None.

    Only follow modules that appear as keys in `imports`.
    """
    # YOUR CODE HERE
    return None
