"""Tests for grounded prompt construction in src/llm/prompt_builder.py."""

import unittest

from src.llm.prompt_builder import build_rag_prompt, format_retrieved_chunks


def _make_result(**overrides) -> dict:
    result = {
        "rank": 1,
        "score": 0.8123,
        "chunk_id": "SKU-1001_chunk_1",
        "product_id": "SKU-1001",
        "product_name": "Luna Everyday Cotton Shirt",
        "category": "Tops",
        "color": "White",
        "text": "Product Name: Luna Everyday Cotton Shirt\nCategory: Tops",
    }
    result.update(overrides)
    return result


class TestFormatRetrievedChunks(unittest.TestCase):
    def test_empty_results_produce_an_empty_string(self) -> None:
        self.assertEqual(format_retrieved_chunks([]), "")

    def test_single_result_includes_every_enriched_field(self) -> None:
        formatted = format_retrieved_chunks([_make_result()])

        self.assertIn("Rank: 1", formatted)
        self.assertIn("Score: 0.8123", formatted)
        self.assertIn("Chunk ID: SKU-1001_chunk_1", formatted)
        self.assertIn("Product ID: SKU-1001", formatted)
        self.assertIn("Product Name: Luna Everyday Cotton Shirt", formatted)
        self.assertIn("Category: Tops", formatted)
        self.assertIn("Color: White", formatted)
        self.assertIn("Text: Product Name: Luna Everyday Cotton Shirt\nCategory: Tops", formatted)

    def test_multiple_results_are_separated_by_a_blank_line(self) -> None:
        results = [_make_result(rank=1), _make_result(rank=2, chunk_id="SKU-1002_chunk_1")]

        formatted = format_retrieved_chunks(results)

        chunks = formatted.split("\n\n")
        self.assertEqual(len(chunks), 2)
        self.assertIn("Rank: 1", chunks[0])
        self.assertIn("Rank: 2", chunks[1])


class TestBuildRagPrompt(unittest.TestCase):
    def test_prompt_embeds_the_user_query_verbatim(self) -> None:
        prompt = build_rag_prompt("a breathable cotton shirt", [_make_result()])

        self.assertIn("User Question:\na breathable cotton shirt", prompt)

    def test_prompt_embeds_the_formatted_retrieved_context(self) -> None:
        results = [_make_result()]
        context = format_retrieved_chunks(results)

        prompt = build_rag_prompt("any question", results)

        self.assertIn(f"Retrieved Context:\n{context}", prompt)

    def test_prompt_instructs_against_overgeneralizing_about_the_whole_catalog(self) -> None:
        prompt = build_rag_prompt("any question", [_make_result()])

        # Regression guard for the Phase G fix: the model must not claim the
        # full catalog lacks something just because the top-k chunks do.
        self.assertIn("only the top few retrieved matches", prompt)

    def test_prompt_includes_the_fixed_decline_phrase(self) -> None:
        prompt = build_rag_prompt("any question", [_make_result()])

        self.assertIn(
            "I do not have enough information in the retrieved context to answer that.",
            prompt,
        )

    def test_prompt_handles_no_retrieved_chunks(self) -> None:
        prompt = build_rag_prompt("any question", [])

        self.assertIn("User Question:\nany question", prompt)
        self.assertIn("Retrieved Context:\n\n", prompt)


if __name__ == "__main__":
    unittest.main()
