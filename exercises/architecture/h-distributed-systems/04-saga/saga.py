"""Architecture · H — A saga runner with compensations.

A saga runs a sequence of local steps. If one fails, the steps that already
completed are undone by their compensations, in reverse order.

Each step is a dict:
    {"name": str, "action": callable(ctx), "compensate": callable(ctx)}
A failing action raises an exception.
"""


def run_saga(steps: list[dict], ctx: dict) -> dict:
    """Run the saga over a shared context `ctx`.

    On full success return:
        {"status": "committed", "committed": [names in order],
         "compensated": [], "failed_at": None}

    If step N's action raises, stop, run compensations for the already-completed
    steps in REVERSE order, and return:
        {"status": "aborted", "committed": [names that ran before the failure],
         "compensated": [names in the order they were undone], "failed_at": <name>}
    """
    # YOUR CODE HERE
    return {}
