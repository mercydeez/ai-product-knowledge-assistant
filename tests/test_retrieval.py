"""Tests for the ChromaDB-backed retrieval layer (retrieval/indexer.py, retrieval/search.py)."""

import shutil
import tempfile
import unittest

from src.retrieval.indexer import build_chroma_collection
from src.retrieval.search import embed_query_with_model, search_chroma_collection, search_similar_chunks

RECORDS = [
    {
        "chunk_id": "A1-chunk-1",
        "product_id": "A1",
        "product_name": "Red Shirt",
        "text": "A bold red cotton shirt.",
        "embedding": [1.0, 0.0, 0.0],
    },
    {
        "chunk_id": "B1-chunk-1",
        "product_id": "B1",
        "product_name": "Blue Jeans",
        "text": "Classic blue denim jeans.",
        "embedding": [0.0, 1.0, 0.0],
    },
    {
        "chunk_id": "C1-chunk-1",
        "product_id": "C1",
        "product_name": "Green Hat",
        "text": "A wide-brimmed green hat.",
        "embedding": [0.0, 0.0, 1.0],
    },
]


class FakeEmbeddingModel:
    """Stand-in for a sentence-transformers model with a fixed query vector."""

    def __init__(self, vector: list[float]) -> None:
        self.vector = vector

    def encode(self, texts, show_progress_bar=False, convert_to_numpy=True):
        return [self.vector for _ in texts]


class ChromaTestCase(unittest.TestCase):
    """Base class that gives each test its own persistent Chroma directory."""

    def setUp(self) -> None:
        self.persist_dir = tempfile.mkdtemp()
        # Windows keeps the sqlite/HNSW files open past process exit, so cleanup
        # failures here are expected and harmless — ignore rather than fail the test.
        self.addCleanup(shutil.rmtree, self.persist_dir, True)


class TestBuildChromaCollection(ChromaTestCase):
    def test_seeds_collection_with_records(self) -> None:
        collection = build_chroma_collection(
            embedded_records=RECORDS,
            persist_directory=self.persist_dir,
            collection_name="test-collection",
        )

        self.assertEqual(collection.count(), len(RECORDS))

    def test_is_idempotent_when_called_again(self) -> None:
        build_chroma_collection(RECORDS, self.persist_dir, "test-collection")
        collection = build_chroma_collection(RECORDS, self.persist_dir, "test-collection")

        self.assertEqual(collection.count(), len(RECORDS))

    def test_raises_for_empty_records(self) -> None:
        with self.assertRaises(ValueError):
            build_chroma_collection([], self.persist_dir, "test-collection")


class TestSearchSimilarChunks(ChromaTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.collection = build_chroma_collection(RECORDS, self.persist_dir, "test-collection")

    def test_closest_vector_ranks_first_with_expected_shape(self) -> None:
        model = FakeEmbeddingModel(vector=[0.9, 0.1, 0.1])

        results = search_similar_chunks(
            query="something red",
            collection=self.collection,
            model_name="unused",
            top_k=3,
            model_instance=model,
        )

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["chunk_id"], "A1-chunk-1")
        self.assertEqual(
            list(results[0].keys()),
            ["rank", "score", "chunk_id", "product_id", "product_name", "text"],
        )
        self.assertEqual([result["rank"] for result in results], [1, 2, 3])

    def test_scores_are_descending_and_within_unit_range(self) -> None:
        model = FakeEmbeddingModel(vector=[0.0, 0.9, 0.1])

        results = search_similar_chunks(
            query="something blue",
            collection=self.collection,
            model_name="unused",
            top_k=3,
            model_instance=model,
        )

        scores = [result["score"] for result in results]
        self.assertEqual(scores, sorted(scores, reverse=True))
        for score in scores:
            self.assertLessEqual(score, 1.0)

    def test_respects_top_k(self) -> None:
        model = FakeEmbeddingModel(vector=[0.0, 0.0, 1.0])

        results = search_similar_chunks(
            query="something green",
            collection=self.collection,
            model_name="unused",
            top_k=1,
            model_instance=model,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["chunk_id"], "C1-chunk-1")

    def test_rejects_non_positive_top_k(self) -> None:
        with self.assertRaises(ValueError):
            search_chroma_collection(self.collection, query_vector=[1.0, 0.0, 0.0], top_k=0)


class TestEmbedQuery(unittest.TestCase):
    def test_rejects_empty_query(self) -> None:
        with self.assertRaises(ValueError):
            embed_query_with_model(query="   ", model=FakeEmbeddingModel(vector=[0.0]))


if __name__ == "__main__":
    unittest.main()
