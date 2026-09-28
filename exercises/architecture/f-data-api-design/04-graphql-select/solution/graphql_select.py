"""Architecture · F — A tiny GraphQL-style field selector (solution)."""


def graphql_select(obj, selection: dict):
    result = {}
    for field, sub in selection.items():
        value = obj[field]
        if sub is True:
            result[field] = value
        elif isinstance(value, list):
            result[field] = [graphql_select(item, sub) for item in value]
        else:
            result[field] = graphql_select(value, sub)
    return result


def count_leaves(obj) -> int:
    if isinstance(obj, dict):
        return sum(count_leaves(v) for v in obj.values())
    if isinstance(obj, list):
        return sum(count_leaves(item) for item in obj)
    return 1


def over_fetch_count(full_obj, selection: dict) -> int:
    return count_leaves(full_obj) - count_leaves(graphql_select(full_obj, selection))
