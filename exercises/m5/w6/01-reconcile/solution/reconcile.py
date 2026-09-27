"""Reference solution. See README.md."""


def reconcile(desired: int, actual: int) -> dict:
    if actual < desired:
        return {"action": "start", "count": desired - actual}
    if actual > desired:
        return {"action": "stop", "count": actual - desired}
    return {"action": "none", "count": 0}
