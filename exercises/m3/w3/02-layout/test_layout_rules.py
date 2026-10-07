from layout_rules import find_cycle, find_violations, layer_of


def test_layer_of():
    assert layer_of("app.routers.users") == "routers"
    assert layer_of("app.main") == "main"
    assert layer_of("app.core.config") == "core"


GOOD = {
    "app.main": ["app.routers.users", "app.core.config", "fastapi"],
    "app.routers.users": ["app.services.users", "app.schemas.users", "fastapi"],
    "app.services.users": ["app.repositories.users", "app.schemas.users"],
    "app.repositories.users": ["app.models.user", "sqlalchemy"],
    "app.models.user": ["sqlalchemy"],
    "app.schemas.users": ["pydantic"],
}


def test_clean_layout_has_no_violations():
    assert find_violations(GOOD) == []


def test_router_must_not_import_repository():
    bad = {"app.routers.users": ["app.repositories.users"]}
    assert find_violations(bad) == [("app.routers.users", "app.repositories.users")]


def test_service_must_not_import_router():
    bad = {"app.services.users": ["app.routers.users"]}
    assert find_violations(bad) == [("app.services.users", "app.routers.users")]


def test_model_must_not_import_service():
    bad = {"app.models.user": ["app.services.users"]}
    assert find_violations(bad) == [("app.models.user", "app.services.users")]


def test_same_layer_and_core_are_always_allowed():
    ok = {
        "app.services.users": ["app.services.emails", "app.core.config"],
        "app.models.user": ["app.core.config"],
    }
    assert find_violations(ok) == []


def test_third_party_imports_are_ignored():
    assert find_violations({"app.models.user": ["fastapi", "requests"]}) == []


def test_violations_are_sorted():
    bad = {
        "app.services.b": ["app.routers.x"],
        "app.models.a": ["app.services.y"],
    }
    assert find_violations(bad) == [
        ("app.models.a", "app.services.y"),
        ("app.services.b", "app.routers.x"),
    ]


def test_no_cycle_in_a_clean_graph():
    assert find_cycle(GOOD) is None


def test_two_module_cycle():
    graph = {"a": ["b"], "b": ["a"]}
    cycle = find_cycle(graph)
    assert cycle is not None
    assert cycle[0] == cycle[-1]
    assert set(cycle) == {"a", "b"}


def test_longer_cycle_found_through_a_tail():
    graph = {"x": ["a"], "a": ["b"], "b": ["c"], "c": ["a"]}
    cycle = find_cycle(graph)
    assert cycle is not None
    assert cycle[0] == cycle[-1]
    assert set(cycle) == {"a", "b", "c"}   # the tail "x" is not part of the loop
