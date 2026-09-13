import ast
from datetime import UTC, datetime
from pathlib import Path

import pytest

import adapters
from domain import InvalidTransition

HERE = Path(__file__).parent
T0 = datetime(2026, 9, 13, 9, 0, tzinfo=UTC)


class Clock:
    def __init__(self):
        self.now = T0

    def __call__(self):
        return self.now


class RecordingPublisher:
    def __init__(self, uow):
        self.uow, self.events = uow, []

    def publish(self, name, payload):
        self.events.append((name, payload, self.uow.commits))  # records how many commits had happened


@pytest.fixture
def parts():
    uow = adapters.InMemoryUnitOfWork()
    return uow, RecordingPublisher(uow), Clock()


@pytest.fixture
def service(parts):
    from services import ApplicationService

    uow, publisher, clock = parts
    return ApplicationService(uow, publisher, clock, max_active_free=2)


def test_add_application_commits_then_publishes(service, parts):
    uow, publisher, _ = parts
    dto = service.add_application(7, "free", "  Kopi Data ", " Backend Engineer ")
    assert dto == {"id": 1, "company": "Kopi Data", "role": "Backend Engineer", "status": "saved", "updated_at": "2026-09-13T09:00:00+00:00"}
    assert uow.commits == 1 and uow.committed_rows[1].company == "Kopi Data"
    assert publisher.events == [("application_added", {"application_id": 1, "user_id": 7}, 1)], "publish after commit"


@pytest.mark.parametrize(("company", "role", "field"), [("", "Dev", "company"), ("   ", "Dev", "company"), ("Kopi", " ", "role")])
def test_validation(service, parts, company, role, field):
    from services import ValidationFailed

    with pytest.raises(ValidationFailed) as error:
        service.add_application(7, "free", company, role)
    assert error.value.field == field and parts[0].commits == 0 and parts[1].events == []


def test_free_plan_limit_counts_active_only(service, parts):
    from services import LimitReached

    first = service.add_application(7, "free", "A", "Dev")
    service.add_application(7, "free", "B", "Dev")
    with pytest.raises(LimitReached):
        service.add_application(7, "free", "C", "Dev")
    assert service.add_application(7, "pro", "C", "Dev")["id"] == 3, "pro plan has no limit"
    assert service.add_application(8, "free", "Other user", "Dev")["id"] == 4
    service.move(7, first["id"], "withdrawn")
    # A is withdrawn (not active), but B and C are active → a free add is still over the limit of 2
    with pytest.raises(LimitReached):
        service.add_application(7, "free", "E", "Dev")


def test_move_updates_status_timestamp_and_publishes(service, parts):
    uow, publisher, clock = parts
    added = service.add_application(7, "free", "Kopi Data", "Dev")
    clock.now = datetime(2026, 9, 14, 10, 30, tzinfo=UTC)
    dto = service.move(7, added["id"], "applied")
    assert dto["status"] == "applied" and dto["updated_at"] == "2026-09-14T10:30:00+00:00"
    assert uow.committed_rows[added["id"]].status == "applied"
    assert publisher.events[-1] == ("application_status_changed", {"application_id": 1, "user_id": 7, "from": "saved", "to": "applied"}, 2)


def test_move_failures_change_nothing(service, parts):
    from services import ApplicationNotFound

    uow, publisher, _ = parts
    added = service.add_application(7, "free", "Kopi Data", "Dev")
    with pytest.raises(ApplicationNotFound):
        service.move(8, added["id"], "applied")
    with pytest.raises(ApplicationNotFound):
        service.move(7, 999, "applied")
    with pytest.raises(InvalidTransition):
        service.move(7, added["id"], "offer")
    assert uow.commits == 1 and len(publisher.events) == 1
    assert uow.committed_rows[added["id"]].status == "saved"


def test_list_returns_dtos_not_domain_objects(service):
    service.add_application(7, "free", "A", "Dev")
    service.add_application(8, "free", "B", "Dev")
    service.add_application(7, "pro", "C", "Dev")
    result = service.list_applications(7)
    assert [r["company"] for r in result] == ["A", "C"] and all(type(r) is dict for r in result)


def test_bootstrap_defaults_and_overrides(parts):
    from bootstrap import Container, bootstrap

    default = bootstrap()
    assert isinstance(default, Container)
    assert isinstance(default.applications.uow, adapters.InMemoryUnitOfWork)
    assert default.applications.clock is adapters.system_clock
    assert default.applications.add_application(1, "free", "Kopi", "Dev")["status"] == "saved"
    uow, publisher, clock = parts
    custom = bootstrap(uow=uow, publisher=publisher, clock=clock, max_active_free=1)
    assert custom.applications.uow is uow and custom.applications.max_active_free == 1


@pytest.fixture
def client(parts):
    from api import create_app
    from bootstrap import bootstrap

    uow, publisher, clock = parts
    return create_app(bootstrap(uow=uow, publisher=publisher, clock=clock, max_active_free=1)).test_client()


def test_api_translates_http(client):
    created = client.post("/users/7/applications", json={"company": "Kopi Data", "role": "Dev", "plan": "free"})
    assert created.status_code == 201 and created.get_json()["id"] == 1
    moved = client.post("/users/7/applications/1/status", json={"status": "applied"})
    assert moved.status_code == 200 and moved.get_json()["status"] == "applied"
    assert client.get("/users/7/applications").get_json()["data"][0]["status"] == "applied"


def test_api_maps_errors(client):
    assert client.post("/users/7/applications", json={"company": "", "role": "Dev"}).get_json() == {"error": {"code": "validation_failed", "field": "company"}}
    client.post("/users/7/applications", json={"company": "A", "role": "Dev", "plan": "free"})
    limit = client.post("/users/7/applications", json={"company": "B", "role": "Dev", "plan": "free"})
    assert limit.status_code == 403 and limit.get_json()["error"]["code"] == "limit_reached"
    assert client.post("/users/8/applications/1/status", json={"status": "applied"}).status_code == 404
    invalid = client.post("/users/7/applications/1/status", json={"status": "offer"})
    assert invalid.status_code == 409 and invalid.get_json()["error"]["code"] == "invalid_transition"


def imported_modules(path):
    tree = ast.parse(path.read_text())
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            names.add(node.module)
            names |= {f"{node.module}.{a.name}" for a in node.names}
    return names, tree


def test_dependency_rules():
    service_imports, _ = imported_modules(HERE / "services.py")
    assert not {"adapters", "flask", "api", "bootstrap"} & {n.split(".")[0] for n in service_imports}, "services depend on domain + ports only"
    api_imports, api_tree = imported_modules(HERE / "api.py")
    assert "adapters" not in {n.split(".")[0] for n in api_imports} and "domain.Application" not in api_imports
    assert not any(isinstance(n, ast.Attribute) and n.attr in {"uow", "applications_repository", "commit"} for n in ast.walk(api_tree)), "routes must not touch persistence"
    for module in ("services.py", "api.py"):
        _, tree = imported_modules(HERE / module)
        assert "adapters" not in ast.unparse(tree), f"{module} must not know adapters"
