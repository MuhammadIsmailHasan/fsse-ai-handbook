from citations import extract_citations, find_fake_quotes, normalize, quote_supported, render_sources, validate_citations


def test_extract_citations():
    assert extract_citations("A [2]. B [1, 2]. C [3].") == [2, 1, 3]
    assert extract_citations("Refunds take 7 days [1].") == [1]
    assert extract_citations("Both [1,3] agree [3][12].") == [1, 3, 12]
    assert extract_citations("No sources here.") == []


def test_other_brackets_are_ignored():
    assert extract_citations("See [note] and [1a] and [] and [1 2].") == []
    assert extract_citations("list[0] is fine") == [0]          # [0] is a number in brackets, it is reported


def test_validate_ok():
    assert validate_citations("Refunds take 7 days [1]. Shipping is free [2].", 2) == []


def test_unknown_source_numbers():
    problems = validate_citations("A [3]. B [0]. C [1].", 2)
    assert problems == ["unknown source [3]", "unknown source [0]"]


def test_no_citations_at_all():
    assert validate_citations("Refunds take 7 days.", 3) == ["no citations"]
    assert validate_citations("", 3) == []
    assert validate_citations("Anything.", 0) == []             # no sources were given, nothing to cite


def test_uncited_sentences_are_reported():
    answer = "Refunds take 7 days [1]. They are paid by transfer. Shipping is free [2]."
    assert validate_citations(answer, 2) == ["uncited sentence: They are paid by transfer."]


def test_refusals_do_not_need_citations():
    assert validate_citations("I do not know. Refunds take 7 days [1].", 1) == []
    assert validate_citations("I could not find that in the documents. Shipping is free [1].", 1) == []
    assert validate_citations("I don't know the price. It may vary [1].", 1) == []


def test_unknown_source_and_uncited_sentence_together():
    problems = validate_citations("A [5]. B.", 2)
    assert problems == ["unknown source [5]", "uncited sentence: B."]


def test_normalize():
    assert normalize('  Hello,\n\n  "World"  ') == "hello, world"
    assert normalize("It’s  “fine”") == "its fine"


def test_quote_supported():
    source = "Refunds are paid back within 7 days\nafter we receive the item."
    assert quote_supported("paid back within 7 DAYS after we receive", source)
    assert not quote_supported("paid back within 14 days", source)
    assert not quote_supported("   ", source)


def test_find_fake_quotes():
    sources = ["Refunds are paid back within 7 days.", "Shipping is free for orders above Rp 200.000."]
    answer = 'The policy says "paid back within 7 days" and also "refunds are instant and unconditional" [1]. Say "free" too.'
    assert find_fake_quotes(answer, sources) == ["refunds are instant and unconditional"]


def test_quotes_can_come_from_any_source():
    sources = ["alpha beta gamma", "delta epsilon zeta"]
    assert find_fake_quotes('"delta epsilon zeta" and "alpha beta gamma"', sources) == []


def test_render_sources():
    sources = [
        {"title": "Shipping", "url": "https://x.test/ship"},
        {"title": "Refund policy", "url": "https://x.test/refund"},
    ]
    out = render_sources("Free shipping [1]. Refund in 7 days [2]. Odd [9]. Again [2].", sources)
    assert out == (
        "Free shipping [1]. Refund in 7 days [2]. Odd [9]. Again [2].\n\n"
        "Sources:\n"
        "[1] Shipping - https://x.test/ship\n"
        "[2] Refund policy - https://x.test/refund"
    )


def test_render_sources_in_citation_order_and_unchanged_when_nothing_valid():
    sources = [{"title": "A", "url": "u1"}, {"title": "B", "url": "u2"}]
    assert render_sources("x [2] y [1]", sources).endswith("[2] B - u2\n[1] A - u1")
    assert render_sources("No citations.", sources) == "No citations."
    assert render_sources("Only bad [7].", sources) == "Only bad [7]."
