"""Tests for flow.py. Don't edit this file."""

import ast
from pathlib import Path

import pytest

from flow import InvalidTransition, allowed_next, describe_event, next_status, parse_command

ALLOWED = {
    "wishlist": ["applied", "withdrawn"],
    "applied": ["interview", "rejected", "withdrawn"],
    "interview": ["interview", "offer", "rejected", "withdrawn"],
    "offer": ["offer_accepted", "offer_declined"],
    "rejected": [],
    "withdrawn": [],
    "offer_accepted": [],
    "offer_declined": [],
}
ALL = list(ALLOWED)


@pytest.mark.parametrize(("current", "target"), [(c, t) for c in ALL for t in ALL])
def test_every_transition(current, target):
    if target in ALLOWED[current]:
        assert next_status(current, target) == target
    else:
        with pytest.raises(InvalidTransition):
            next_status(current, target)


@pytest.mark.parametrize("current", ALL)
def test_allowed_next_sorted(current):
    assert allowed_next(current) == sorted(ALLOWED[current])


def test_unknown_status():
    with pytest.raises(InvalidTransition):
        next_status("hired", "offer")
    with pytest.raises(InvalidTransition):
        allowed_next("hired")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("add Kopi Data Analyst", {"action": "add", "company": "Kopi", "role": "Data Analyst"}),
        ("  add   Garuda   Backend   Engineer ", {"action": "add", "company": "Garuda", "role": "Backend Engineer"}),
        ("move 12 interview", {"action": "move", "id": 12, "status": "interview"}),
        ("MOVE 3 offer", {"action": "move", "id": 3, "status": "offer"}),
        ("list", {"action": "list", "status": None}),
        ("list offer", {"action": "list", "status": "offer"}),
        ("help", {"action": "help"}),
    ],
)
def test_parse_command(text, expected):
    assert parse_command(text) == expected


@pytest.mark.parametrize("text", ["", "add Kopi", "move x interview", "move 3", "list a b", "delete 3", "help me"])
def test_parse_command_invalid(text):
    with pytest.raises(ValueError):
        parse_command(text)


@pytest.mark.parametrize(
    ("event", "expected"),
    [
        ({"type": "application.created", "company": "Kopi Data", "id": 9}, "New application at Kopi Data"),
        ({"type": "status.changed", "to": "offer", "id": 9}, "🎉 Offer!"),
        ({"type": "status.changed", "to": "offer_accepted"}, "🎉 Offer!"),
        ({"type": "status.changed", "to": "interview"}, "Status changed to interview"),
        ({"type": "user.deleted"}, "Ignored event user.deleted"),
    ],
)
def test_describe_event(event, expected):
    assert describe_event(event) == expected


@pytest.mark.parametrize("event", [{}, {"type": 42}, {"kind": "x"}])
def test_describe_event_invalid(event):
    with pytest.raises(ValueError):
        describe_event(event)


def test_uses_match_statements():
    tree = ast.parse(Path(__file__).with_name("flow.py").read_text())
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    for name in ("parse_command", "describe_event"):
        assert any(isinstance(n, ast.Match) for n in ast.walk(functions[name])), f"Use `match` in {name}"
