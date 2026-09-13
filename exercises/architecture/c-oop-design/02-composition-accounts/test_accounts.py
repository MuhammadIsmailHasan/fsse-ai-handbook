import ast
from pathlib import Path

import accounts as acc


def test_predefined_roles_and_plans():
    assert acc.JOB_SEEKER.permissions == frozenset({"applications:read", "applications:write", "jobs:read"})
    assert acc.RECRUITER.name == "recruiter" and "jobs:write" in acc.RECRUITER.permissions
    assert acc.ADMIN.permissions == frozenset({"*"})
    assert acc.FREE.limits == {"applications": 20} and acc.PRO.features == frozenset({"tracker", "ai_match", "export"})


def test_account_defaults():
    siti = acc.Account("siti@example.com")
    assert siti.roles == set() and siti.plan is acc.FREE
    assert siti.can("jobs:read") is False and siti.has_feature("tracker") is True


def test_roles_combine_and_change_at_runtime():
    siti = acc.Account("siti@example.com", roles={acc.JOB_SEEKER})
    same_object = siti
    assert siti.can("applications:write") and not siti.can("jobs:write")
    siti.grant(acc.RECRUITER)
    assert siti is same_object
    assert siti.can("applications:write") and siti.can("jobs:write")
    siti.revoke(acc.JOB_SEEKER)
    siti.revoke(acc.ADMIN)
    assert not siti.can("applications:write") and siti.can("candidates:read")


def test_wildcards():
    admin = acc.Account("root@example.com", roles={acc.ADMIN})
    assert admin.can("anything:at-all")
    jobs_manager = acc.Account("jobs@example.com", roles={acc.Role("jobs_manager", frozenset({"jobs:*"}))})
    assert jobs_manager.can("jobs:write") and jobs_manager.can("jobs:delete")
    assert not jobs_manager.can("candidates:read")
    assert not jobs_manager.can("jobsx:read"), "a resource wildcard must match the whole resource name"


def test_plans_change_without_replacing_the_account():
    budi = acc.Account("budi@example.com", roles={acc.JOB_SEEKER})
    assert budi.limit("applications") == 20 and not budi.has_feature("ai_match")
    budi.change_plan(acc.PRO)
    assert budi.limit("applications") == 1000 and budi.has_feature("ai_match")
    assert budi.limit("unknown") == 0
    assert budi.can("applications:write"), "changing plan doesn't touch roles"


def test_roles_are_immutable_values():
    assert acc.Role("x", frozenset({"a"})) == acc.Role("x", frozenset({"a"}))
    assert len({acc.Role("x", frozenset({"a"})), acc.Role("x", frozenset({"a"}))}) == 1


def test_no_inheritance_between_classes():
    tree = ast.parse(Path(acc.__file__).read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            assert not node.bases, f"class {node.name} inherits from {[ast.unparse(b) for b in node.bases]} — compose instead"
