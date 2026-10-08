import random

import pytest

from vector_store import LSHIndex, VectorStore, recall_at_k


def make_store(metric="cosine"):
    store = VectorStore(2, metric)
    store.add("a", [1.0, 0.0], {"lang": "id", "type": "faq"})
    store.add("b", [0.9, 0.1], {"lang": "en", "type": "faq"})
    store.add("c", [0.0, 1.0], {"lang": "id", "type": "doc"})
    store.add("d", [-1.0, 0.0])
    return store


def test_add_get_len_delete():
    store = make_store()
    assert len(store) == 4
    assert store.get("a") == ([1.0, 0.0], {"lang": "id", "type": "faq"})
    assert store.get("zzz") is None
    assert store.delete("a") is True and store.delete("a") is False
    assert len(store) == 3


def test_add_replaces_an_existing_id():
    store = make_store()
    store.add("a", [0.0, 1.0], {"lang": "en"})
    assert len(store) == 4
    assert store.get("a") == ([0.0, 1.0], {"lang": "en"})


def test_wrong_dimension():
    store = make_store()
    with pytest.raises(ValueError, match="expected 2 dimensions"):
        store.add("x", [1.0, 2.0, 3.0])
    with pytest.raises(ValueError):
        store.search([1.0])


def test_exact_search():
    store = make_store()
    result = store.search([1.0, 0.0], k=2)
    assert [i for i, _ in result] == ["a", "b"]
    assert result[0][1] == pytest.approx(1.0)
    assert [i for i, _ in store.search([1.0, 0.0], k=10)] == ["a", "b", "c", "d"]


def test_metadata_filter_is_applied_before_ranking():
    store = make_store()
    assert [i for i, _ in store.search([1.0, 0.0], k=5, where={"lang": "id"})] == ["a", "c"]
    assert [i for i, _ in store.search([1.0, 0.0], k=5, where={"lang": "id", "type": "doc"})] == ["c"]
    assert store.search([1.0, 0.0], k=5, where={"lang": "fr"}) == []


def test_vectors_without_metadata_never_match_a_filter():
    store = make_store()
    assert "d" not in [i for i, _ in store.search([-1.0, 0.0], k=5, where={"lang": "id"})]
    assert "d" in [i for i, _ in store.search([-1.0, 0.0], k=5)]


def test_filter_can_hide_the_best_match():
    store = make_store()
    # the best match for [1, 0] is "a", but the filter removes it: the best remaining is returned
    assert store.search([1.0, 0.0], k=1, where={"lang": "en"})[0][0] == "b"


def test_other_metrics():
    store = VectorStore(2, "euclidean")
    store.add("near", [1.0, 1.0])
    store.add("far", [9.0, 9.0])
    assert store.search([0.0, 0.0], k=1) == [("near", pytest.approx(-(2 ** 0.5)))]
    dot_store = VectorStore(2, "dot")
    dot_store.add("short", [1.0, 0.0])
    dot_store.add("long", [5.0, 5.0])
    assert dot_store.search([1.0, 0.0], k=1)[0][0] == "long"


def test_ties_are_broken_by_id():
    store = VectorStore(2)
    for name in ("b", "c", "a"):
        store.add(name, [1.0, 0.0])
    assert [i for i, _ in store.search([1.0, 0.0], k=3)] == ["a", "b", "c"]


def clustered_store(n_clusters=20, per_cluster=50, dim=16, seed=5):
    rng = random.Random(seed)
    centers = [[rng.gauss(0, 1) for _ in range(dim)] for _ in range(n_clusters)]
    store = VectorStore(dim)
    for c, center in enumerate(centers):
        for j in range(per_cluster):
            store.add(f"c{c:02d}-{j:02d}", [x + rng.gauss(0, 0.15) for x in center])
    return store, centers, rng


def test_lsh_is_deterministic_for_a_seed():
    store, centers, _ = clustered_store()
    a = LSHIndex(store, planes=8, seed=1).search(centers[3], 5)
    b = LSHIndex(store, planes=8, seed=1).search(centers[3], 5)
    assert a == b


def test_lsh_scores_only_a_part_of_the_data():
    store, centers, _ = clustered_store()
    index = LSHIndex(store, planes=8, seed=1)
    results, candidates = index.search(centers[3], 5)
    assert 0 < candidates < len(store) // 2
    assert len(results) <= 5


def test_lsh_results_are_exactly_scored_and_sorted():
    store, centers, _ = clustered_store()
    index = LSHIndex(store, planes=6, seed=2)
    results, _ = index.search(centers[7], 5, probe_neighbors=True)
    exact = dict(store.search(centers[7], k=len(store)))
    for id, score in results:
        assert score == pytest.approx(exact[id])
    assert [s for _, s in results] == sorted([s for _, s in results], reverse=True)


def test_lsh_with_probing_finds_most_true_neighbours():
    store, centers, rng = clustered_store()
    index = LSHIndex(store, planes=6, seed=3)
    recalls = []
    for center in centers:
        query = [x + rng.gauss(0, 0.05) for x in center]
        exact = [i for i, _ in store.search(query, k=10)]
        approx = [i for i, _ in index.search(query, k=10, probe_neighbors=True)[0]]
        recalls.append(recall_at_k(approx, exact))
    assert sum(recalls) / len(recalls) >= 0.8


def test_probing_neighbours_scores_more_candidates_and_never_loses_recall():
    store, centers, _ = clustered_store()
    index = LSHIndex(store, planes=10, seed=4)
    _, narrow = index.search(centers[2], 10, probe_neighbors=False)
    _, wide = index.search(centers[2], 10, probe_neighbors=True)
    assert wide >= narrow


def test_recall_at_k():
    assert recall_at_k(["a", "b"], ["a", "b"]) == 1.0
    assert recall_at_k(["a", "x"], ["a", "b"]) == 0.5
    assert recall_at_k([], ["a", "b"]) == 0.0
    assert recall_at_k(["a"], []) == 1.0
    assert recall_at_k(["b", "a", "z"], ["a", "b"]) == 1.0
