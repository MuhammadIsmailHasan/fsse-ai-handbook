import logging
from datetime import date

import behaviors as b

TODAY = date(2026, 9, 13)
JOBS = [
    {"id": "c", "salary_max": 15_000_000, "posted_on": date(2026, 9, 1), "skills": ["Python", "SQL"]},
    {"id": "a", "salary_max": None, "posted_on": date(2026, 9, 12), "skills": ["python", "react", "aws", "sql"]},
    {"id": "b", "salary_max": 15_000_000, "posted_on": date(2026, 9, 10), "skills": []},
]


def ids(jobs):
    return [job["id"] for job in jobs]


def test_strategies():
    assert ids(b.rank_jobs(JOBS, b.BySalary())) == ["b", "c", "a"]
    assert ids(b.rank_jobs(JOBS, b.ByRecency(TODAY))) == ["a", "b", "c"]
    assert ids(b.rank_jobs(JOBS, b.BySkillMatch(["PYTHON", "sql"]))) == ["c", "a", "b"]
    assert b.BySkillMatch(["python"]).score(JOBS[1]) == 0.25 and b.BySkillMatch(["python"]).score(JOBS[2]) == 0.0
    assert ids(JOBS) == ["c", "a", "b"], "return a new list"


def test_any_strategy_object_works():
    class ShortestId:
        def score(self, job):
            return -len(job["id"])

    assert ids(b.rank_jobs([{"id": "zz"}, {"id": "b"}, {"id": "a"}], ShortestId())) == ["a", "b", "zz"]


def test_event_bus_order_unsubscribe_and_isolation(caplog):
    bus = b.EventBus()
    calls = []
    bus.subscribe("status_changed", lambda p: calls.append(("audit", p["id"])))

    def broken(payload):
        raise RuntimeError("email provider down")

    bus.subscribe("status_changed", broken)
    unsubscribe_stats = bus.subscribe("status_changed", lambda p: calls.append(("stats", p["id"])))
    bus.subscribe("note_added", lambda p: calls.append(("notes", p["id"])))

    with caplog.at_level(logging.ERROR, logger="events"):
        errors = bus.publish("status_changed", {"id": 7})
    assert calls == [("audit", 7), ("stats", 7)]
    assert len(errors) == 1 and isinstance(errors[0], RuntimeError)
    assert any(record.name == "events" and record.exc_info for record in caplog.records)

    unsubscribe_stats()
    unsubscribe_stats()  # calling twice is harmless
    calls.clear()
    assert bus.publish("status_changed", {"id": 8}) != [] and calls == [("audit", 8)]
    assert bus.publish("unknown", {}) == []


def test_commands_with_undo_redo():
    board = b.Board(statuses={1: "saved"})
    history = b.History()
    assert history.undo() is False and history.redo() is False
    history.run(b.ChangeStatus(board, 1, "applied"))
    history.run(b.AddNote(board, 1, "Sent CV"))
    history.run(b.ChangeStatus(board, 1, "interview"))
    assert board.statuses[1] == "interview" and board.notes[1] == ["Sent CV"]

    assert history.undo() and board.statuses[1] == "applied"
    assert history.undo() and board.notes[1] == []
    assert history.redo() and board.notes[1] == ["Sent CV"]
    assert history.redo() and board.statuses[1] == "interview"
    assert history.redo() is False

    history.undo()
    history.run(b.AddNote(board, 1, "Recruiter called"))
    assert history.redo() is False, "a new command clears the redo stack"
    assert board.statuses[1] == "applied" and board.notes[1] == ["Sent CV", "Recruiter called"]


def test_change_status_undo_for_new_application():
    board = b.Board()
    command = b.ChangeStatus(board, 5, "saved")
    command.execute()
    command.undo()
    assert 5 not in board.statuses
