"""Tests for the FastAPI routes, isolated from the real RAG pipeline via a mocked service.

The app's lifespan (which loads the embedding model and builds the Chroma
collection) only runs if TestClient is used as a context manager, so plain
`TestClient(app)` lets us skip it entirely and inject a mock service instead.
"""

import json
import unittest
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from src.api.app import app


class TestApiRoutes(unittest.TestCase):
    def setUp(self) -> None:
        self.rag_service = MagicMock()
        app.state.rag_service = self.rag_service
        self.client = TestClient(app)

    def test_health_check(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_ask_returns_answer_and_sources(self) -> None:
        self.rag_service.answer_question.return_value = {
            "question": "a floral summer dress",
            "answer": "The Sienna Floral Summer Dress is a great fit.",
            "sources": [
                {
                    "rank": 1,
                    "score": 0.91,
                    "chunk_id": "SKU-1003_chunk_1",
                    "product_id": "SKU-1003",
                    "product_name": "Sienna Floral Summer Dress",
                    "category": "Dresses",
                    "color": "Coral",
                    "text": "A lightweight midi dress with floral print.",
                }
            ],
        }

        response = self.client.post("/ask", json={"question": "a floral summer dress"})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["answer"], "The Sienna Floral Summer Dress is a great fit.")
        self.assertEqual(body["sources"][0]["product_id"], "SKU-1003")
        self.rag_service.answer_question.assert_called_once_with("a floral summer dress")

    def test_ask_rejects_empty_question_with_422(self) -> None:
        response = self.client.post("/ask", json={"question": ""})

        self.assertEqual(response.status_code, 422)
        self.rag_service.answer_question.assert_not_called()

    def test_ask_returns_400_for_value_error(self) -> None:
        self.rag_service.answer_question.side_effect = ValueError("Question cannot be empty.")

        response = self.client.post("/ask", json={"question": "   "})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Question cannot be empty.")

    def test_ask_returns_500_for_unexpected_error(self) -> None:
        self.rag_service.answer_question.side_effect = RuntimeError(
            "GROQ_API_KEY is not set. Add it to your .env file."
        )

        response = self.client.post("/ask", json={"question": "breathable cotton shirt"})

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["detail"], "GROQ_API_KEY is not set. Add it to your .env file.")

    def test_ask_handles_no_sources_found(self) -> None:
        self.rag_service.answer_question.return_value = {
            "question": "black slim-fit jeans",
            "answer": "No exact match found.",
            "sources": [],
        }

        response = self.client.post("/ask", json={"question": "black slim-fit jeans"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["sources"], [])

    def test_ask_stream_emits_sources_then_tokens_then_done(self) -> None:
        sources = [
            {
                "rank": 1,
                "score": 0.91,
                "top_match_score": 0.91,
                "chunk_id": "SKU-1003_chunk_1",
                "product_id": "SKU-1003",
                "product_name": "Sienna Floral Summer Dress",
                "category": "Dresses",
                "color": "Coral",
                "text": "A lightweight midi dress with floral print.",
            }
        ]
        self.rag_service.answer_question_stream.return_value = iter(
            [
                {"type": "sources", "sources": sources},
                {"type": "token", "text": "The Sienna "},
                {"type": "token", "text": "dress is a great fit."},
                {"type": "done"},
            ]
        )

        response = self.client.post("/ask/stream", json={"question": "a floral summer dress"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "text/event-stream; charset=utf-8")

        lines = [line for line in response.text.split("\n\n") if line]
        events = [json.loads(line.removeprefix("data: ")) for line in lines]
        self.assertEqual(
            events,
            [
                {"type": "sources", "sources": sources},
                {"type": "token", "text": "The Sienna "},
                {"type": "token", "text": "dress is a great fit."},
                {"type": "done"},
            ],
        )

    def test_ask_stream_emits_error_event_on_exception(self) -> None:
        def raise_error():
            raise RuntimeError("GROQ_API_KEY is not set.")
            yield  # pragma: no cover - makes this a generator function

        self.rag_service.answer_question_stream.return_value = raise_error()

        response = self.client.post("/ask/stream", json={"question": "a floral summer dress"})

        self.assertEqual(response.status_code, 200)
        event = json.loads(response.text.strip().removeprefix("data: "))
        self.assertEqual(event, {"type": "error", "message": "GROQ_API_KEY is not set."})


if __name__ == "__main__":
    unittest.main()
