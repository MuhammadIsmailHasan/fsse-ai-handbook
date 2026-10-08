import json


class JudgeError(ValueError):
    pass


def judge_prompt(question, answer, reference, rubric):
    return "\n".join([
        "You are grading an answer to a customer question.",
        f"Rubric: {rubric}",
        "",
        "<question>",
        question,
        "</question>",
        "",
        "<reference>",
        reference,
        "</reference>",
        "",
        "<answer>",
        answer,
        "</answer>",
        "",
        'Reply with JSON only: {"score": <integer 1-5>, "reasoning": "<one short sentence>"}',
    ])


def _first_object(text):
    for i, ch in enumerate(text):
        if ch != "{":
            continue
        depth, in_string, escaped = 0, False, False
        for j in range(i, len(text)):
            c = text[j]
            if in_string:
                if escaped:
                    escaped = False
                elif c == "\\":
                    escaped = True
                elif c == '"':
                    in_string = False
                continue
            if c == '"':
                in_string = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    try:
                        value = json.loads(text[i : j + 1])
                    except json.JSONDecodeError:
                        break
                    if isinstance(value, dict):
                        return value
                    break
    return None


def parse_judge(reply):
    data = _first_object(reply)
    if data is None:
        raise JudgeError("no JSON object in the judge reply")
    score = data.get("score")
    if isinstance(score, bool) or not isinstance(score, int) or not 1 <= score <= 5:
        raise JudgeError("score must be an integer from 1 to 5")
    reasoning = data.get("reasoning", "")
    if not isinstance(reasoning, str):
        raise JudgeError("reasoning must be a string")
    return {"score": score, "reasoning": reasoning}


def _check(a, b):
    if len(a) != len(b):
        raise ValueError("different lengths")


def accuracy(a, b):
    _check(a, b)
    if not a:
        return 1.0
    return sum(x == y for x, y in zip(a, b)) / len(a)


def cohens_kappa(a, b):
    _check(a, b)
    if not a:
        return 1.0
    po = accuracy(a, b)
    n = len(a)
    pe = sum((a.count(label) / n) * (b.count(label) / n) for label in set(a) | set(b))
    if pe == 1:
        return 1.0 if po == 1 else 0.0
    return (po - pe) / (1 - pe)


def confusion_matrix(human, judge, labels):
    matrix = {h: {j: 0 for j in labels} for h in labels}
    for h, j in zip(human, judge):
        matrix[h][j] += 1
    return matrix


def swap_consistency(pairs, judge_fn):
    if not pairs:
        return 1.0
    consistent = 0
    for question, a, b in pairs:
        first = judge_fn(question, a, b)
        second = judge_fn(question, b, a)
        pick1 = {"first": "a", "second": "b", "tie": "tie"}[first]
        pick2 = {"first": "b", "second": "a", "tie": "tie"}[second]
        consistent += pick1 == pick2
    return consistent / len(pairs)


def best_threshold(scores, human_pass, candidates=(1, 2, 3, 4, 5)):
    _check(scores, human_pass)
    best, best_acc = None, -1.0
    for t in candidates:
        acc = sum((s >= t) == h for s, h in zip(scores, human_pass)) / len(scores) if scores else 1.0
        if acc > best_acc or (acc == best_acc and t > best):
            best, best_acc = t, acc
    return best
