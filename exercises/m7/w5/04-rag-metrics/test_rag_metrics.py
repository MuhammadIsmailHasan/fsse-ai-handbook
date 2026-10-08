import pytest

from rag_metrics import (
    answer_coverage, claim_supported, content_words, context_precision, context_recall, faithfulness,
    split_claims,
)

CONTEXTS = [
    "Refunds are paid back within 7 days after we receive the returned item.",
    "Shipping is free for orders above Rp 200.000 within Java.",
]


def test_split_claims_removes_citation_markers():
    assert split_claims("Refunds take 7 days [1]. Shipping is free [2, 3]! Really?") == [
        "Refunds take 7 days.", "Shipping is free!", "Really?"
    ]
    assert split_claims("") == []
    assert split_claims("  [1]  ") == []


def test_content_words_drops_stopwords_and_case():
    assert content_words("The Refund is PAID in 7 days") == {"refund", "paid", "7", "days"}
    assert content_words("the of a") == set()


def test_claim_supported():
    assert claim_supported("Refunds are paid within 7 days", CONTEXTS) is True
    assert claim_supported("Refunds are instant and unconditional", CONTEXTS) is False
    assert claim_supported("The", CONTEXTS) is True                         # no content words


def test_support_can_come_from_several_contexts_together():
    assert claim_supported("Free shipping and refunds within 7 days", CONTEXTS) is True


def test_threshold():
    claim = "Refunds are paid within 14 days"            # content words: refunds, paid, within, 14, days → 4/5 supported
    assert claim_supported(claim, CONTEXTS, 0.8) is True
    assert claim_supported(claim, CONTEXTS, 0.9) is False


def test_faithfulness_counts_supported_claims():
    answer = "Refunds are paid within 7 days [1]. Delivery to Papua takes 30 days [2]."
    assert faithfulness(answer, CONTEXTS) == pytest.approx(0.5)
    assert faithfulness("Refunds are paid within 7 days.", CONTEXTS) == 1.0


def test_faithfulness_edge_cases():
    assert faithfulness("", CONTEXTS) == 1.0
    assert faithfulness("Anything specific here.", []) == 0.0


def test_context_precision_examples():
    assert context_precision([True, False, True]) == pytest.approx((1 / 1 + 2 / 3) / 2)
    assert context_precision([False, True]) == pytest.approx(0.5)
    assert context_precision([True, True, True]) == pytest.approx(1.0)
    assert context_precision([False, False]) == 0.0
    assert context_precision([]) == 0.0


def test_ranking_matters_for_context_precision():
    assert context_precision([True, False, False]) > context_precision([False, False, True])


def test_context_recall():
    assert context_recall(["7 days", "Rp 200.000"], CONTEXTS) == 1.0
    assert context_recall(["7 days", "14 days"], CONTEXTS) == 0.5
    assert context_recall([], CONTEXTS) == 1.0
    assert context_recall(["free"], []) == 0.0


def test_answer_coverage():
    assert answer_coverage(["7 days", "free"], "Refunds take 7 days.") == 0.5
    assert answer_coverage([], "anything") == 1.0


def test_the_metrics_point_at_different_stages():
    facts = ["7 days"]
    good_ctx, bad_ctx = ["Refunds take 7 days."], ["Shipping is free."]
    # retrieval failed: low recall, and an answer from memory is low on faithfulness
    assert context_recall(facts, bad_ctx) == 0.0
    assert faithfulness("Refunds take 7 days.", bad_ctx) == 0.0
    # retrieval fine, generation unfaithful
    assert context_recall(facts, good_ctx) == 1.0
    assert faithfulness("Refunds take 30 days.", good_ctx) < 1.0
