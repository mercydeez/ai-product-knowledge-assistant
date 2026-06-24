"""Tests for the off-topic relevance guardrail in ProductRAGService.answer_question."""

import unittest
from unittest.mock import MagicMock, patch

from src.services.rag_service import OFF_TOPIC_MESSAGE, ProductRAGService

SOURCE = {
    "rank": 1,
    "score": 0.0,
    "chunk_id": "SKU-1001_chunk_1",
    "product_id": "SKU-1001",
    "product_name": "Luna Everyday Cotton Shirt",
    "category": "Tops",
    "color": "White",
    "text": "Product Name: Luna Everyday Cotton Shirt",
}


class TestOffTopicGuardrail(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ProductRAGService(min_relevance_score=0.35)
        self.service.collection = MagicMock()
        self.service.embedding_model = MagicMock()
        self.service.records = [{"chunk_id": "placeholder"}]

    @patch("src.services.rag_service.generate_answer")
    @patch("src.services.rag_service.build_rag_prompt")
    def test_low_score_declines_without_calling_llm(self, mock_build_prompt, mock_generate) -> None:
        self.service.retrieve_sources = MagicMock(return_value=[{**SOURCE, "score": 0.1}])

        result = self.service.answer_question("What is the capital of France?")

        self.assertEqual(result, {
            "question": "What is the capital of France?",
            "answer": OFF_TOPIC_MESSAGE,
            "sources": [],
        })
        mock_build_prompt.assert_not_called()
        mock_generate.assert_not_called()

    @patch("src.services.rag_service.generate_answer")
    @patch("src.services.rag_service.build_rag_prompt")
    def test_no_sources_declines_without_calling_llm(self, mock_build_prompt, mock_generate) -> None:
        self.service.retrieve_sources = MagicMock(return_value=[])

        result = self.service.answer_question("asdkjasldkj")

        self.assertEqual(result["answer"], OFF_TOPIC_MESSAGE)
        self.assertEqual(result["sources"], [])
        mock_build_prompt.assert_not_called()
        mock_generate.assert_not_called()

    @patch("src.services.rag_service.generate_answer")
    @patch("src.services.rag_service.build_rag_prompt")
    def test_high_score_calls_llm_and_returns_sources(self, mock_build_prompt, mock_generate) -> None:
        sources = [{**SOURCE, "score": 0.8}]
        self.service.retrieve_sources = MagicMock(return_value=sources)
        mock_build_prompt.return_value = "a built prompt"
        mock_generate.return_value = "The Luna shirt is breathable cotton."

        result = self.service.answer_question("a breathable cotton shirt")

        self.assertEqual(result["answer"], "The Luna shirt is breathable cotton.")
        self.assertEqual(result["sources"], sources)
        mock_generate.assert_called_once()

    @patch("src.services.rag_service.generate_answer")
    @patch("src.services.rag_service.build_rag_prompt")
    def test_score_exactly_at_threshold_calls_llm(self, mock_build_prompt, mock_generate) -> None:
        self.service.retrieve_sources = MagicMock(return_value=[{**SOURCE, "score": 0.35}])
        mock_generate.return_value = "An answer."

        result = self.service.answer_question("right at the threshold")

        self.assertEqual(result["answer"], "An answer.")
        mock_generate.assert_called_once()


if __name__ == "__main__":
    unittest.main()
