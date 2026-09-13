"""Reference solution."""


def flatten(items: list) -> list:
    result = []
    for item in items:
        if isinstance(item, list):
            result.extend(flatten(item))  # the same problem on a smaller list
        else:
            result.append(item)
    return result


def max_depth(items: list) -> int:
    child_depths = [max_depth(item) for item in items if isinstance(item, list)]
    return 1 + max(child_depths, default=0)
