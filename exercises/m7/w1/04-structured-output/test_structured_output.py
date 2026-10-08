import pytest

from structured_output import BadModelOutput, extract_json, extract_with_retry, validate


def test_plain_json():
    assert extract_json('{"a": 1}') == {"a": 1}
    assert extract_json("[1, 2, 3]") == [1, 2, 3]


def test_fenced_json():
    reply = 'Sure!\n```json\n{"name": "Sari", "age": 30}\n```\nAnything else?'
    assert extract_json(reply) == {"name": "Sari", "age": 30}


def test_prose_around_the_json():
    assert extract_json('Here you go: {"ok": true} — hope that helps') == {"ok": True}


def test_braces_inside_strings_do_not_confuse_it():
    assert extract_json('{"text": "a } b { c", "n": 2} trailing } text') == {"text": "a } b { c", "n": 2}


def test_escaped_quote_inside_a_string():
    assert extract_json(r'{"q": "she said \"hi\" }"}') == {"q": 'she said "hi" }'}


def test_nested_structures():
    assert extract_json('x {"a": {"b": [1, {"c": 2}]}} y') == {"a": {"b": [1, {"c": 2}]}}


def test_first_valid_value_wins():
    assert extract_json('{"first": 1} and {"second": 2}') == {"first": 1}


def test_skips_a_broken_candidate_and_finds_a_later_one():
    assert extract_json('{not json} then {"ok": 1}') == {"ok": 1}


def test_no_json_raises():
    with pytest.raises(BadModelOutput):
        extract_json("I am sorry, I cannot do that.")
    with pytest.raises(BadModelOutput):
        extract_json('{"unclosed": ')
    with pytest.raises(BadModelOutput):
        extract_json("")


SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer", "minimum": 0, "maximum": 150},
        "plan": {"type": "string", "enum": ["free", "pro"]},
        "tags": {"type": "array", "items": {"type": "string"}},
        "active": {"type": "boolean"},
        "score": {"type": "number"},
    },
    "required": ["name", "age"],
    "additionalProperties": False,
}


def test_valid_data_has_no_problems():
    assert validate({"name": "Sari", "age": 30, "plan": "pro", "tags": ["a"], "active": True, "score": 1.5}, SCHEMA) == []
    assert validate({"name": "Sari", "age": 0}, SCHEMA) == []


def test_missing_required_key():
    problems = validate({"name": "Sari"}, SCHEMA)
    assert len(problems) == 1 and problems[0].startswith("$.age")


def test_wrong_types():
    problems = validate({"name": 5, "age": "30"}, SCHEMA)
    assert len(problems) == 2
    assert any(p.startswith("$.name") for p in problems) and any(p.startswith("$.age") for p in problems)


def test_a_bool_is_not_an_integer_or_a_number():
    assert validate({"name": "x", "age": True}, SCHEMA)
    assert validate({"name": "x", "age": 1, "score": False}, SCHEMA)


def test_an_integer_is_a_number_but_a_float_is_not_an_integer():
    assert validate({"name": "x", "age": 1, "score": 3}, SCHEMA) == []
    assert validate({"name": "x", "age": 1.5}, SCHEMA)


def test_enum_minimum_maximum():
    assert validate({"name": "x", "age": 1, "plan": "gold"}, SCHEMA)
    assert validate({"name": "x", "age": -1}, SCHEMA)
    assert validate({"name": "x", "age": 200}, SCHEMA)


def test_unknown_keys_are_rejected_only_when_asked():
    assert validate({"name": "x", "age": 1, "admin": True}, SCHEMA)[0].startswith("$.admin")
    assert validate({"anything": 1}, {"type": "object"}) == []


def test_array_items_have_indexed_paths():
    problems = validate({"name": "x", "age": 1, "tags": ["a", 2, "c", None]}, SCHEMA)
    assert [p.split(":")[0] for p in problems] == ["$.tags[1]", "$.tags[3]"]


def test_top_level_type_mismatch():
    assert validate([1], {"type": "object"})[0].startswith("$:")
    assert validate("x", {"type": "null"})


def test_retry_succeeds_on_the_second_try_and_sends_the_problems():
    prompts = []
    replies = iter(['{"name": "Sari"}', '{"name": "Sari", "age": 30}'])

    def ask(prompt):
        prompts.append(prompt)
        return next(replies)

    data = extract_with_retry(ask, "Extract the person.", SCHEMA)
    assert data == {"name": "Sari", "age": 30}
    assert prompts[0] == "Extract the person."
    assert prompts[1].startswith("Extract the person.\n\nYour previous answer was invalid: $.age")
    assert prompts[1].endswith("\nReply with valid JSON only.")


def test_retry_also_covers_text_without_json():
    replies = iter(["Sorry, no.", '```json\n{"name": "A", "age": 1}\n```'])
    assert extract_with_retry(lambda p: next(replies), "go", SCHEMA) == {"name": "A", "age": 1}


def test_gives_up_after_max_attempts():
    calls = []

    def ask(prompt):
        calls.append(prompt)
        return "never json"

    with pytest.raises(BadModelOutput):
        extract_with_retry(ask, "go", SCHEMA, max_attempts=3)
    assert len(calls) == 3


def test_a_valid_first_answer_asks_only_once():
    calls = []
    extract_with_retry(lambda p: calls.append(p) or '{"name": "A", "age": 1}', "go", SCHEMA)
    assert len(calls) == 1


def test_each_retry_starts_from_the_original_prompt_not_a_growing_one():
    prompts = []
    replies = iter(["bad", "worse", '{"name": "A", "age": 1}'])

    def ask(prompt):
        prompts.append(prompt)
        return next(replies)

    extract_with_retry(ask, "ORIGINAL", SCHEMA)
    assert prompts[2].count("ORIGINAL") == 1
