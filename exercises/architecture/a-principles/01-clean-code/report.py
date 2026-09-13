"""Architecture · A — Refactor me. Behavior tests pass already; keep them green."""

from datetime import date


def status_report(applications, today):
    c = {}
    s = []
    for a in applications:
        k = a["status"]
        if k in c:
            c[k] = c[k] + 1
        else:
            c[k] = 1
        if a["status"] == "applied":
            d = (today - a["applied_on"]).days
            if d > 14:
                s.append(a)
    l = []
    l.append("Application report for " + today.isoformat())
    for k in sorted(c):
        l.append("- " + k + ": " + str(c[k]))
    if len(s) > 0:
        l.append("")
        l.append("Follow up (applied > 14 days ago, no response):")
        s.sort(key=lambda a: a["applied_on"])
        for a in s:
            d = (today - a["applied_on"]).days
            l.append("- " + a["company"] + " · " + a["role"] + " (" + str(d) + " days)")
    t = 0
    for k in c:
        t = t + c[k]
    o = c.get("offer", 0)
    if t > 0:
        p = o * 100 // t
    else:
        p = 0
    l.append("")
    l.append("Offer rate: " + str(p) + "%")
    return "\n".join(l)


if __name__ == "__main__":
    print(status_report([{"company": "A", "role": "Dev", "status": "applied", "applied_on": date(2026, 8, 1)}], date(2026, 9, 1)))
