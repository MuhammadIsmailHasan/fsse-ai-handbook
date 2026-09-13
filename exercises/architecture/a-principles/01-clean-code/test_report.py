import ast
from datetime import date
from pathlib import Path

from report import status_report

TODAY = date(2026, 9, 13)
APPLICATIONS = [
    {"company": "Nusantara Tech", "role": "Backend Dev", "status": "applied", "applied_on": date(2026, 8, 20)},
    {"company": "Kopi Data", "role": "Data Analyst", "status": "interview", "applied_on": date(2026, 8, 25)},
    {"company": "Awan Cloud", "role": "SRE", "status": "applied", "applied_on": date(2026, 9, 5)},
    {"company": "Lintas AI", "role": "ML Engineer", "status": "offer", "applied_on": date(2026, 8, 1)},
    {"company": "Batik Soft", "role": "QA", "status": "applied", "applied_on": date(2026, 8, 10)},
]

EXPECTED = """Application report for 2026-09-13
- applied: 3
- interview: 1
- offer: 1

Follow up (applied > 14 days ago, no response):
- Batik Soft · QA (34 days)
- Nusantara Tech · Backend Dev (24 days)

Offer rate: 20%"""


# ---- Behavior: must stay green during the whole refactor ----------------------

def test_full_report():
    assert status_report(APPLICATIONS, TODAY) == EXPECTED


def test_no_follow_ups_and_no_applications():
    assert status_report([], TODAY) == "Application report for 2026-09-13\n\nOffer rate: 0%"
    fresh = [{"company": "X", "role": "Dev", "status": "applied", "applied_on": date(2026, 9, 1)}]
    assert "Follow up" not in status_report(fresh, TODAY)


def test_input_list_is_not_reordered():
    applications = list(APPLICATIONS)
    status_report(applications, TODAY)
    assert applications == APPLICATIONS


# ---- Structure: your refactoring target --------------------------------------

TREE = ast.parse(Path(__file__).with_name("report.py").read_text())
FUNCTIONS = [node for node in ast.walk(TREE) if isinstance(node, ast.FunctionDef)]


def test_has_helper_functions():
    assert len(FUNCTIONS) >= 4, "Extract helpers: at least 4 functions in total"


def test_functions_are_short():
    for func in FUNCTIONS:
        body_lines = func.body[-1].end_lineno - func.body[0].lineno + 1
        assert body_lines <= 15, f"{func.name} is {body_lines} lines — split it"


def test_no_single_letter_names():
    names = {node.id for node in ast.walk(TREE) if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)}
    names |= {arg.arg for func in FUNCTIONS for arg in func.args.args}
    names |= {node.args.args[0].arg for node in ast.walk(TREE) if isinstance(node, ast.Lambda) and node.args.args}
    short = sorted(name for name in names if len(name) == 1 and name != "_")
    assert not short, f"Rename: {short}"
