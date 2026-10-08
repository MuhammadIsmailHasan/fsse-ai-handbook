import hashlib
import re


def _blank(value):
    return not isinstance(value, str) or not value.strip()


def validate_dataset(cases):
    problems, ids = [], []
    for i, case in enumerate(cases):
        case_id = case.get("id")
        if _blank(case_id):
            problems.append(f"case {i}: missing id")
            continue
        ids.append(case_id)
        if _blank(case.get("input")):
            problems.append(f"{case_id}: missing input")
        if _blank(case.get("expected")) and _blank(case.get("criteria")):
            problems.append(f"{case_id}: needs expected or criteria")
        tags = case.get("tags")
        if "tags" in case and not (isinstance(tags, list) and all(isinstance(t, str) for t in tags)):
            problems.append(f"{case_id}: tags must be a list of strings")
    for case_id in dict.fromkeys(ids):
        if ids.count(case_id) > 1:
            problems.append(f"duplicate id: {case_id}")
    return problems


def assign_split(case_id, ratios):
    if abs(sum(ratios.values()) - 1) > 1e-9:
        raise ValueError("ratios must add up to 1")
    value = (int(hashlib.sha256(case_id.encode()).hexdigest(), 16) % 10000) / 10000
    total = 0.0
    last = None
    for name, share in ratios.items():
        total += share
        last = name
        if value < total:
            return name
    return last


def split_dataset(cases, ratios):
    out = {name: [] for name in ratios}
    for case in cases:
        out[assign_split(case["id"], ratios)].append(case)
    return out


def coverage(cases, required_tags):
    counts = {tag: sum(1 for c in cases if tag in c.get("tags", [])) for tag in required_tags}
    return {
        "counts": counts,
        "missing": [t for t in required_tags if counts[t] == 0],
        "thin": [t for t in required_tags if 1 <= counts[t] <= 2],
    }


def _words(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def find_leaks(dev, test, threshold=0.8):
    leaks = []
    for d in dev:
        wd = _words(d["input"])
        for t in test:
            wt = _words(t["input"])
            sim = 1.0 if not wd and not wt else len(wd & wt) / len(wd | wt)
            if sim >= threshold:
                leaks.append((d["id"], t["id"], sim))
    leaks.sort(key=lambda x: (-x[2], x[0], x[1]))
    return leaks
