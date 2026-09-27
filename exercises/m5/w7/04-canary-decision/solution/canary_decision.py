"""Reference solution. See README.md."""


def canary_decision(error_rate: float, threshold: float, percent: int) -> str:
    if error_rate > threshold:
        return "rollback"       # unhealthy — safety first
    if percent >= 100:
        return "done"           # healthy and fully rolled out
    return "promote"            # healthy — send it more traffic
