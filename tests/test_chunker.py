"""Tests for the line-based chunking logic in src/preprocessing/chunker.py."""

import unittest

from src.preprocessing.chunker import chunk_text, create_product_chunks


class TestChunkText(unittest.TestCase):
    def test_empty_text_produces_no_chunks(self) -> None:
        self.assertEqual(chunk_text(""), [])

    def test_whitespace_only_text_produces_no_chunks(self) -> None:
        self.assertEqual(chunk_text("   \n\t\n   "), [])

    def test_text_shorter_than_chunk_size_produces_one_chunk(self) -> None:
        text = "Line A\nLine B\nLine C"

        chunks = chunk_text(text, chunk_size=4, overlap=1)

        self.assertEqual(chunks, ["Line A\nLine B\nLine C"])

    def test_text_exactly_one_chunk_size_does_not_overflow_into_a_second_chunk(self) -> None:
        text = "L1\nL2\nL3\nL4"

        chunks = chunk_text(text, chunk_size=4, overlap=1)

        self.assertEqual(chunks, ["L1\nL2\nL3\nL4"])

    def test_longer_text_splits_into_overlapping_chunks(self) -> None:
        text = "\n".join(f"L{i}" for i in range(1, 7))  # L1..L6

        chunks = chunk_text(text, chunk_size=4, overlap=1)

        self.assertEqual(chunks, ["L1\nL2\nL3\nL4", "L4\nL5\nL6"])
        # The overlapping line ("L4") must appear at the end of one chunk and
        # the start of the next, or the configured overlap isn't real.
        self.assertTrue(chunks[0].endswith("L4"))
        self.assertTrue(chunks[1].startswith("L4"))

    def test_blank_lines_are_stripped_before_chunking(self) -> None:
        text = "L1\n\n  \nL2\nL3"

        chunks = chunk_text(text, chunk_size=4, overlap=1)

        self.assertEqual(chunks, ["L1\nL2\nL3"])


class TestCreateProductChunks(unittest.TestCase):
    def test_chunk_ids_are_numbered_per_product_starting_at_one(self) -> None:
        documents = [
            {
                "product_id": "SKU-1",
                "product_name": "Shirt",
                "text": "\n".join(f"L{i}" for i in range(1, 7)),  # L1..L6
            }
        ]

        chunks = create_product_chunks(documents, chunk_size=4, overlap=1)

        self.assertEqual([c["chunk_id"] for c in chunks], ["SKU-1_chunk_1", "SKU-1_chunk_2"])

    def test_product_metadata_is_propagated_to_every_chunk(self) -> None:
        documents = [
            {
                "product_id": "SKU-1",
                "product_name": "Shirt",
                "text": "\n".join(f"L{i}" for i in range(1, 7)),
            }
        ]

        chunks = create_product_chunks(documents, chunk_size=4, overlap=1)

        for chunk in chunks:
            self.assertEqual(chunk["product_id"], "SKU-1")
            self.assertEqual(chunk["product_name"], "Shirt")

    def test_numbering_resets_for_each_document(self) -> None:
        documents = [
            {"product_id": "SKU-1", "product_name": "Shirt", "text": "L1\nL2"},
            {"product_id": "SKU-2", "product_name": "Jeans", "text": "L1\nL2"},
        ]

        chunks = create_product_chunks(documents, chunk_size=4, overlap=1)

        self.assertEqual([c["chunk_id"] for c in chunks], ["SKU-1_chunk_1", "SKU-2_chunk_1"])

    def test_no_documents_produces_no_chunks(self) -> None:
        self.assertEqual(create_product_chunks([]), [])


if __name__ == "__main__":
    unittest.main()
