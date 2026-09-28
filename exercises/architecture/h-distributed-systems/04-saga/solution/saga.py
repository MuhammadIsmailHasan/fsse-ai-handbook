"""Architecture · H — A saga runner with compensations (solution)."""


def run_saga(steps: list[dict], ctx: dict) -> dict:
    committed: list[str] = []
    for step in steps:
        try:
            step["action"](ctx)
            committed.append(step["name"])
        except Exception:
            compensated: list[str] = []
            # Undo the already-completed steps, newest first.
            for done in reversed(steps[: len(committed)]):
                done["compensate"](ctx)
                compensated.append(done["name"])
            return {
                "status": "aborted",
                "committed": committed,
                "compensated": compensated,
                "failed_at": step["name"],
            }
    return {
        "status": "committed",
        "committed": committed,
        "compensated": [],
        "failed_at": None,
    }
