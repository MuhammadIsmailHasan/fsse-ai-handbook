import re


def contains_all(substrings):
    return lambda case, output: all(s.lower() in output.lower() for s in substrings)


def not_contains(substrings):
    return lambda case, output: not any(s.lower() in output.lower() for s in substrings)


def matches(pattern):
    return lambda case, output: re.search(pattern, output, re.IGNORECASE) is not None


def max_chars(limit):
    return lambda case, output: len(output) <= limit


def exact_match(case, output):
    return output.strip().lower() == case["expected"].strip().lower()


def run_eval(system, cases, graders):
    results = []
    for case in cases:
        error = None
        try:
            output = system(case["input"])
        except Exception as exc:  # noqa: BLE001
            output, error = "", f"{type(exc).__name__}: {exc}"
        passed = {name: bool(g(case, output)) for name, g in graders.items()}
        results.append({"id": case["id"], "output": output, "passed": passed, "error": error,
                        "ok": error is None and all(passed.values())})
    total = len(cases)
    ok_count = sum(r["ok"] for r in results)
    by_grader = {name: (sum(r["passed"][name] for r in results) / total if total else 0.0) for name in graders}
    tag_cases = {}
    for case, result in zip(cases, results):
        for tag in case.get("tags", []):
            tag_cases.setdefault(tag, []).append(result["ok"])
    by_tag = {tag: sum(v) / len(v) for tag, v in tag_cases.items()}
    return {
        "total": total,
        "passed": ok_count,
        "pass_rate": ok_count / total if total else 0.0,
        "by_grader": by_grader,
        "by_tag": by_tag,
        "failures": [r["id"] for r in results if not r["ok"]],
        "results": results,
    }


def compare_runs(old, new):
    before = {r["id"]: r["ok"] for r in old["results"]}
    fixed, broken, same_pass, same_fail = [], [], 0, 0
    for r in new["results"]:
        if r["id"] not in before:
            continue
        was, now = before[r["id"]], r["ok"]
        if now and not was:
            fixed.append(r["id"])
        elif was and not now:
            broken.append(r["id"])
        elif now:
            same_pass += 1
        else:
            same_fail += 1
    return {"fixed": fixed, "broken": broken, "same_pass": same_pass, "same_fail": same_fail}


def gate(old, new, min_pass_rate, max_broken=0):
    reasons = []
    if new["pass_rate"] < min_pass_rate:
        reasons.append(f"pass rate {new['pass_rate']:.2f} is below {min_pass_rate:.2f}")
    broken = compare_runs(old, new)["broken"]
    if len(broken) > max_broken:
        reasons.append(f"{len(broken)} cases broke: " + ", ".join(broken))
    return (not reasons, reasons)
