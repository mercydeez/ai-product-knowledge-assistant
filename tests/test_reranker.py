"""Tests for cross-encoder reranking (src/retrieval/reranker.py)."""

import unittest

from src.retrieval.reranker import rerank_results

RESULTS = [
    {"rank": 1, "score": 0.9, "chunk_id": "A", "text": "a bold red cotton shirt"},
    {"rank": 2, "score": 0.6, "chunk_id": "B", "text": "classic blue denim jeans"},
    {"rank": 3, "score": 0.5, "chunk_id": "C", "text": "a wide-brimmed green hat"},
]


class FakeCrossEncoder:
    """Stand-in for a sentence-transformers CrossEncoder with fixed scores per text."""

    def __init__(self, scores_by_text: dict[str, float]) -> None:
        self.scores_by_text = scores_by_text

    def predict(self, pairs):
        return [self.scores_by_text[text] for _query, text in pairs]


SCORES_BY_CHUNK_ID = {"A": 0.1, "B": 0.9, "C": 0.3}
SCORES_BY_TEXT = {result["text"]: SCORES_BY_CHUNK_ID[result["chunk_id"]] for result in RESULTS}


class TestRerankResults(unittest.TestCase):
    def test_reorders_by_cross_encoder_score(self) -> None:
        model = FakeCrossEncoder(SCORES_BY_TEXT)

        reranked = rerank_results(query="blue jeans", results=RESULTS, model=model, top_k=3)

        self.assertEqual([r["chunk_id"] for r in reranked], ["B", "C", "A"])

    def test_reassigns_rank_after_reordering(self) -> None:
        model = FakeCrossEncoder(SCORES_BY_TEXT)

        reranked = rerank_results(query="blue jeans", results=RESULTS, model=model, top_k=3)

        self.assertEqual([r["rank"] for r in reranked], [1, 2, 3])

    def test_slices_to_top_k(self) -> None:
        model = FakeCrossEncoder(SCORES_BY_TEXT)

        reranked = rerank_results(query="blue jeans", results=RESULTS, model=model, top_k=2)

        self.assertEqual(len(reranked), 2)
        self.assertEqual([r["chunk_id"] for r in reranked], ["B", "C"])

    def test_preserves_original_score_field(self) -> None:
        model = FakeCrossEncoder(SCORES_BY_TEXT)

        reranked = rerank_results(query="blue jeans", results=RESULTS, model=model, top_k=3)

        scores_by_chunk_id = {r["chunk_id"]: r["score"] for r in reranked}
        self.assertEqual(scores_by_chunk_id, {"A": 0.9, "B": 0.6, "C": 0.5})

    def test_empty_results_returns_empty_list(self) -> None:
        model = FakeCrossEncoder({})

        reranked = rerank_results(query="anything", results=[], model=model, top_k=3)

        self.assertEqual(reranked, [])


if __name__ == "__main__":
    unittest.main()
