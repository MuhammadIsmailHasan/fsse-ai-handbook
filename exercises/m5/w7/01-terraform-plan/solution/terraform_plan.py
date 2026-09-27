"""Reference solution. See README.md."""


def plan(current: dict, desired: dict) -> dict:
    create = [name for name in desired if name not in current]
    destroy = [name for name in current if name not in desired]
    change = [
        name
        for name in desired
        if name in current and current[name] != desired[name]
    ]
    return {
        "create": sorted(create),
        "change": sorted(change),
        "destroy": sorted(destroy),
    }
