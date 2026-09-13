import copy

from mutation import add_tag, apply_raise, make_grid


def test_add_tag_returns_new_list():
    tags = ["python"]
    result = add_tag(tags, "sql")
    assert result == ["python", "sql"]
    assert tags == ["python"]
    assert result is not tags


def test_make_grid_rows_are_independent():
    grid = make_grid(3, 2)
    grid[0][0] = 9
    assert grid == [[9, 0], [0, 0], [0, 0]]


def test_apply_raise_does_not_touch_inputs():
    employees = [{"name": "Ana", "salary": 10_000_000}, {"name": "Budi", "salary": 8_000_001}]
    before = copy.deepcopy(employees)
    raised = apply_raise(employees, 10)
    assert [e["salary"] for e in raised] == [11_000_000, 8_800_001]
    assert employees == before
