"""Architecture · F — A tiny GraphQL-style field selector.

The core idea behind GraphQL, by hand: instead of returning a whole object
(REST style, which over-fetches), return ONLY the fields the client asked for.

A selection is a dict:
    {"name": True, "orders": {"total": True}}
- True at a leaf means "include this field".
- A nested dict means "recurse into this object (or each item of this list)".
"""


def graphql_select(obj, selection: dict):
    """Return a copy of obj containing only the fields named in `selection`.

    - For a nested dict selection on an object field, recurse into that object.
    - For a nested dict selection on a LIST field, apply it to each item.
    """
    # YOUR CODE HERE
    return {}


def count_leaves(obj) -> int:
    """Count leaf values in a nested object/list (how many actual fields it carries)."""
    # YOUR CODE HERE
    return -1


def over_fetch_count(full_obj, selection: dict) -> int:
    """How many extra leaf fields a 'return everything' response sends
    compared to a field-selected one: leaves(full) - leaves(selected)."""
    # YOUR CODE HERE
    return -1
