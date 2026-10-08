import pytest

from chunkers import expand_to_parents, parent_child, sentence_chunks, split_markdown, split_sentences

DOC = """Intro before any heading.

# Returns

You can return items within 14 days.

## Refunds

Refunds are paid back in 7 days.

Shipping costs are not refunded.

## Exchanges

Exchanges depend on stock.

# Shipping

We ship to all islands.
"""


def test_heading_paths_and_indexes():
    chunks = split_markdown(DOC, 100)
    assert [(c["path"], c["index"]) for c in chunks] == [
        ("", 0), ("Returns", 1), ("Returns > Refunds", 2), ("Returns > Exchanges", 3), ("Shipping", 4),
    ]
    assert chunks[0]["text"] == "Intro before any heading."
    assert chunks[2]["text"] == "Refunds are paid back in 7 days.\n\nShipping costs are not refunded."


def test_heading_line_is_not_part_of_the_text():
    assert all("#" not in c["text"] for c in split_markdown(DOC, 100))


def test_a_heading_with_no_body_makes_no_chunk():
    text = "# A\n\n## B\n\nbody of b\n"
    chunks = split_markdown(text, 50)
    assert [(c["path"], c["text"]) for c in chunks] == [("A > B", "body of b")]


def test_long_sections_are_cut_between_paragraphs():
    text = "# T\n\n" + "\n\n".join(["one two three four five"] * 4)        # 4 paragraphs of 5 words
    chunks = split_markdown(text, 10)
    assert [len(c["text"].split()) for c in chunks] == [10, 10]
    assert all(c["path"] == "T" for c in chunks)
    assert [c["index"] for c in chunks] == [0, 1]
    assert chunks[0]["text"] == "one two three four five\n\none two three four five"


def test_a_huge_paragraph_is_cut_by_words():
    text = "# T\n\n" + " ".join(f"w{i}" for i in range(25))
    chunks = split_markdown(text, 10)
    assert [len(c["text"].split()) for c in chunks] == [10, 10, 5]


def test_level_jumps_and_resets():
    text = "# A\n\n### C\n\nx\n\n# D\n\n## E\n\ny\n"
    assert [c["path"] for c in split_markdown(text, 10)] == ["A > C", "D > E"]


def test_split_markdown_bad_argument_and_empty_text():
    with pytest.raises(ValueError):
        split_markdown("# A\n\nx", 0)
    assert split_markdown("", 10) == []


def test_split_sentences():
    assert split_sentences("Hello world. How are you? Fine!  Thanks.") == ["Hello world.", "How are you?", "Fine!", "Thanks."]
    assert split_sentences("It costs 3.5 dollars. Or 10.000 rupiah.") == ["It costs 3.5 dollars.", "Or 10.000 rupiah."]
    assert split_sentences("   ") == []


def test_sentence_chunks_never_split_a_sentence():
    text = "One two three. Four five six. Seven eight nine. Ten eleven twelve."
    assert sentence_chunks(text, 6) == ["One two three. Four five six.", "Seven eight nine. Ten eleven twelve."]
    assert sentence_chunks(text, 7) == ["One two three. Four five six.", "Seven eight nine. Ten eleven twelve."]


def test_a_long_sentence_gets_its_own_chunk():
    text = "Short one. " + "word " * 12 + "end. Tail here."
    chunks = sentence_chunks(text, 5)
    assert chunks[0] == "Short one."
    assert chunks[1].startswith("word") and len(chunks[1].split()) == 13
    assert chunks[2] == "Tail here."


def test_sentence_overlap():
    text = "A a a. B b b. C c c. D d d."
    assert sentence_chunks(text, 6, overlap_sentences=1) == ["A a a. B b b.", "B b b. C c c.", "C c c. D d d."]


def test_overlap_is_dropped_when_it_leaves_no_room():
    text = "A a a. B b b. C c c."
    assert sentence_chunks(text, 3, overlap_sentences=1) == ["A a a.", "B b b.", "C c c."]


def test_sentence_chunks_empty():
    assert sentence_chunks("", 10) == []


def test_parent_child_ids_and_mapping():
    parents = [{"id": "p1", "text": "a b c d e f g"}, {"id": "p2", "text": "x y"}, {"id": "p3", "text": "   "}]
    children, parent_of = parent_child(parents, 3)
    assert children == [
        {"id": "p1#0", "text": "a b c"}, {"id": "p1#1", "text": "d e f"}, {"id": "p1#2", "text": "g"},
        {"id": "p2#0", "text": "x y"},
    ]
    assert parent_of == {"p1#0": "p1", "p1#1": "p1", "p1#2": "p1", "p2#0": "p2"}


def test_expand_to_parents_keeps_order_and_dedupes():
    parent_of = {"p1#0": "p1", "p1#1": "p1", "p2#0": "p2", "p3#0": "p3"}
    parents = {"p1": "full one", "p2": "full two", "p3": "full three"}
    hits = ["p2#0", "p1#1", "p2#0", "zzz#9", "p1#0", "p3#0"]
    assert expand_to_parents(hits, parent_of, parents) == [
        {"id": "p2", "text": "full two"}, {"id": "p1", "text": "full one"}, {"id": "p3", "text": "full three"},
    ]
    assert expand_to_parents([], parent_of, parents) == []
