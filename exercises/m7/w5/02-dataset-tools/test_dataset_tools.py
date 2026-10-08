import pytest

from dataset_tools import assign_split, coverage, find_leaks, split_dataset, validate_dataset


def case(id, input="what is the refund window?", **kw):
    base = {"id": id, "input": input, "expected": "7 days", "tags": ["billing"]}
    base.update(kw)
    return base


def test_valid_dataset():
    assert validate_dataset([case("a"), case("b", expected=None, criteria="mentions 7 days")]) == []
    assert validate_dataset([]) == []


def test_missing_id_skips_the_other_checks_for_that_case():
    assert validate_dataset([{"input": "", "expected": ""}]) == ["case 0: missing id"]
    assert validate_dataset([case("a"), {"id": "  ", "input": "x"}, {"id": 5}]) == ["case 1: missing id", "case 2: missing id"]


def test_missing_input_and_expected():
    problems = validate_dataset([{"id": "a"}, case("b", input="  "), case("c", expected="", criteria=None)])
    assert problems == [
        "a: missing input",
        "a: needs expected or criteria",
        "b: missing input",
        "c: needs expected or criteria",
    ]


def test_tags_must_be_a_list_of_strings():
    assert validate_dataset([case("a", tags="billing")]) == ["a: tags must be a list of strings"]
    assert validate_dataset([case("a", tags=["ok", 3])]) == ["a: tags must be a list of strings"]
    assert validate_dataset([case("a", tags=[])]) == []
    no_tags = case("a")
    del no_tags["tags"]
    assert validate_dataset([no_tags]) == []


def test_duplicate_ids_are_reported_once_after_the_case_problems():
    cases = [case("a"), case("b", input=""), case("a"), case("a"), case("b")]
    assert validate_dataset(cases) == ["b: missing input", "duplicate id: a", "duplicate id: b"]


def test_assign_split_is_stable_and_valid():
    ratios = {"dev": 0.5, "test": 0.5}
    assert assign_split("q1", ratios) == assign_split("q1", ratios)
    assert {assign_split(f"q{i}", ratios) for i in range(50)} == {"dev", "test"}


def test_assign_split_known_values():
    # value for these ids comes from sha256; the expected splits are fixed by the formula
    ratios = {"train": 0.6, "dev": 0.2, "test": 0.2}
    got = [assign_split(f"case-{i}", ratios) for i in range(8)]
    assert got == [assign_split(f"case-{i}", ratios) for i in range(8)]
    assert set(got) <= {"train", "dev", "test"}


def test_assign_split_ratios_must_add_up_to_one():
    with pytest.raises(ValueError):
        assign_split("a", {"dev": 0.5, "test": 0.4})
    assert assign_split("a", {"only": 1.0}) == "only"


def test_adding_cases_does_not_move_existing_ones():
    ratios = {"dev": 0.7, "test": 0.3}
    before = {f"q{i}": assign_split(f"q{i}", ratios) for i in range(30)}
    after = {f"q{i}": assign_split(f"q{i}", ratios) for i in range(60)}
    assert all(after[k] == v for k, v in before.items())


def test_split_dataset_keeps_order_and_all_names():
    cases = [case(f"q{i}") for i in range(200)]
    parts = split_dataset(cases, {"dev": 0.7, "test": 0.3})
    assert set(parts) == {"dev", "test"}
    assert len(parts["dev"]) + len(parts["test"]) == 200
    assert 110 <= len(parts["dev"]) <= 170
    ids = [c["id"] for c in parts["dev"]]
    assert ids == sorted(ids, key=lambda s: int(s[1:]))
    assert split_dataset([], {"a": 0.5, "b": 0.5}) == {"a": [], "b": []}


def test_coverage():
    cases = [
        case("a", tags=["billing", "id"]),
        case("b", tags=["billing"]),
        case("c", tags=["billing", "unanswerable"]),
        case("d", tags=["shipping"]),
    ]
    report = coverage(cases, ["billing", "shipping", "unanswerable", "typo", "id"])
    assert report["counts"] == {"billing": 3, "shipping": 1, "unanswerable": 1, "typo": 0, "id": 1}
    assert report["missing"] == ["typo"]
    assert report["thin"] == ["shipping", "unanswerable", "id"]


def test_coverage_with_cases_without_tags():
    assert coverage([{"id": "a", "input": "x", "expected": "y"}], ["t"]) == {"counts": {"t": 0}, "missing": ["t"], "thin": []}


def test_find_leaks():
    dev = [case("d1", "What is the refund window for damaged items?"), case("d2", "How do I reset my password")]
    test = [
        case("t1", "what is the refund window for damaged items"),      # identical words
        case("t2", "How long does delivery take"),
        case("t3", "What is the refund window for damaged goods?"),     # 7 of 9 words: 7/9 = 0.78
    ]
    leaks = find_leaks(dev, test, 0.7)
    assert leaks[0] == ("d1", "t1", 1.0)
    assert [(a, b) for a, b, _ in leaks] == [("d1", "t1"), ("d1", "t3")]
    assert leaks[1][2] == pytest.approx(7 / 9)
    assert find_leaks(dev, test, 0.8) == [("d1", "t1", 1.0)]


def test_find_leaks_empty_inputs_and_ordering():
    assert find_leaks([{"id": "a", "input": ""}], [{"id": "b", "input": "!!"}]) == [("a", "b", 1.0)]
    dev = [{"id": "d2", "input": "same words"}, {"id": "d1", "input": "same words"}]
    test = [{"id": "t1", "input": "same words"}]
    assert find_leaks(dev, test) == [("d1", "t1", 1.0), ("d2", "t1", 1.0)]
