"""Checks for terraform_plan.py. Don't edit this file."""

from terraform_plan import plan


def test_create_change_destroy_together():
    current = {"web": {"type": "t3.micro"}, "old": {"type": "t3.nano"}}
    desired = {"web": {"type": "t3.small"}, "db": {"engine": "postgres"}}
    assert plan(current, desired) == {
        "create": ["db"],
        "change": ["web"],
        "destroy": ["old"],
    }


def test_no_changes():
    state = {"web": {"type": "t3.micro"}}
    assert plan(state, state) == {"create": [], "change": [], "destroy": []}


def test_only_creates_from_empty():
    desired = {"b": {}, "a": {}}
    assert plan({}, desired) == {"create": ["a", "b"], "change": [], "destroy": []}


def test_only_destroys_to_empty():
    current = {"b": {}, "a": {}}
    assert plan(current, {}) == {"create": [], "change": [], "destroy": ["a", "b"]}


def test_identical_attributes_are_not_a_change():
    current = {"web": {"type": "t3.micro", "count": 2}}
    desired = {"web": {"count": 2, "type": "t3.micro"}}  # same, different order
    assert plan(current, desired) == {"create": [], "change": [], "destroy": []}
