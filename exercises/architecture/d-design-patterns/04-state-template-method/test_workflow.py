import ast
from pathlib import Path

import pytest

import workflow as w

ACTIONS = {
    "apply": lambda wf: wf.apply(),
    "schedule_interview": lambda wf: wf.schedule_interview(),
    "make_offer": lambda wf: wf.make_offer(20_000_000),
    "accept": lambda wf: wf.accept(),
    "reject": lambda wf: wf.reject(),
    "withdraw": lambda wf: wf.withdraw(),
}
PATHS = {
    "saved": [],
    "applied": ["apply"],
    "interviewing": ["apply", "schedule_interview"],
    "offered": ["apply", "schedule_interview", "make_offer"],
    "accepted": ["apply", "schedule_interview", "make_offer", "accept"],
    "rejected": ["apply", "reject"],
    "withdrawn": ["withdraw"],
}
ALLOWED = {
    "saved": {"apply": "applied", "withdraw": "withdrawn"},
    "applied": {"schedule_interview": "interviewing", "reject": "rejected", "withdraw": "withdrawn"},
    "interviewing": {"schedule_interview": "interviewing", "make_offer": "offered", "reject": "rejected", "withdraw": "withdrawn"},
    "offered": {"accept": "accepted", "reject": "rejected", "withdraw": "withdrawn"},
    "accepted": {},
    "rejected": {},
    "withdrawn": {},
}


def workflow_in(status):
    wf = w.ApplicationWorkflow()
    for action in PATHS[status]:
        ACTIONS[action](wf)
    assert wf.status == status
    return wf


@pytest.mark.parametrize(("status", "action"), [(s, a) for s in PATHS for a in ACTIONS], ids=lambda v: v)
def test_every_state_and_action(status, action):
    wf = workflow_in(status)
    if action in ALLOWED[status]:
        ACTIONS[action](wf)
        assert wf.status == ALLOWED[status][action]
    else:
        with pytest.raises(w.InvalidAction) as error:
            ACTIONS[action](wf)
        assert str(error.value) == f"cannot {action} when {status}"
        assert wf.status == status


def test_data_and_history():
    wf = w.ApplicationWorkflow()
    assert wf.history == ["saved"] and wf.interview_rounds == 0 and wf.offer_amount is None
    wf.apply()
    wf.schedule_interview()
    wf.schedule_interview()
    wf.make_offer(18_500_000)
    wf.accept()
    assert wf.interview_rounds == 2 and wf.offer_amount == 18_500_000
    assert wf.history == ["saved", "applied", "interviewing", "interviewing", "offered", "accepted"]


def test_workflow_delegates_instead_of_branching_on_status():
    tree = ast.parse(Path(w.__file__).read_text())
    workflow_class = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "ApplicationWorkflow")
    for node in ast.walk(workflow_class):
        if isinstance(node, ast.Compare):
            literals = [n for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
            assert not literals, f"ApplicationWorkflow compares strings: {ast.unparse(node)} — let state classes decide"
        assert not isinstance(node, ast.Match), "no match statement on status — use state objects"
    state_classes = {n.name for n in tree.body if isinstance(n, ast.ClassDef)}
    assert {"Saved", "Applied", "Interviewing", "Offered"} <= state_classes


APPS = [{"company": "Kopi Data", "role": "Backend Engineer", "status": "applied"}, {"company": "Awan", "role": "QA", "status": "saved"}]


def test_plain_text_report():
    assert w.PlainTextReport().generate(APPS) == "== Applications ==\n- Kopi Data: Backend Engineer (applied)\n- Awan: QA (saved)\nTotal: 2"
    assert w.PlainTextReport().generate([]) == "== Applications ==\nTotal: 0"


def test_markdown_report():
    assert w.MarkdownReport().generate(APPS) == (
        "# Job Hunt\n\n| Company | Role | Status |\n|---|---|---|\n"
        "| Kopi Data | Backend Engineer | applied |\n| Awan | QA | saved |\n"
        "\n_Total: 2 applications_"
    )


def test_template_is_abstract_and_reusable():
    with pytest.raises(TypeError):
        w.ApplicationReport()

    class CsvReport(w.ApplicationReport):
        def header(self):
            return "company,status"

        def row(self, app):
            return f"{app['company']},{app['status']}"

    assert CsvReport().generate(APPS) == "company,status\nKopi Data,applied\nAwan,saved\nTotal: 2"

    class Incomplete(w.ApplicationReport):
        def header(self):
            return "x"

    with pytest.raises(TypeError):
        Incomplete()
