"""Tests for the LLM-judge eval helpers (scripts/evaluate_answers.py)."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from evaluate_answers import _extract_json, judge_answer, summarize  # noqa: E402


class TestExtractJson(unittest.TestCase):
    def test_parses_plain_json(self) -> None:
        raw = '{"faithfulness": 5, "relevance": 4, "reason": "Accurate and on-topic."}'

        result = _extract_json(raw)

        self.assertEqual(result, {"faithfulness": 5, "relevance": 4, "reason": "Accurate and on-topic."})

    def test_parses_fenced_json(self) -> None:
        raw = '```json\n{"faithfulness": 3, "relevance": 2, "reason": "Vague."}\n```'

        result = _extract_json(raw)

        self.assertEqual(result, {"faithfulness": 3, "relevance": 2, "reason": "Vague."})

    def test_parses_bare_fenced_json(self) -> None:
        raw = '```\n{"faithfulness": 1, "relevance": 1, "reason": "Off."}\n```'

        result = _extract_json(raw)

        self.assertEqual(result, {"faithfulness": 1, "relevance": 1, "reason": "Off."})


class TestJudgeAnswer(unittest.TestCase):
    @patch("evaluate_answers.call_groq")
    def test_calls_groq_with_zero_temperature_and_parses_result(self, mock_call_groq) -> None:
        mock_call_groq.return_value = '{"faithfulness": 4, "relevance": 5, "reason": "Good."}'

        result = judge_answer("a cotton shirt", "Product Name: Luna Shirt", "The Luna shirt is cotton.")

        self.assertEqual(result, {"faithfulness": 4, "relevance": 5, "reason": "Good."})
        self.assertEqual(mock_call_groq.call_args.kwargs["temperature"], 0.0)


class TestSummarize(unittest.TestCase):
    def test_averages_faithfulness_and_relevance(self) -> None:
        results = [
            {"question": "q1", "answer": "a1", "faithfulness": 5, "relevance": 3, "reason": "r1"},
            {"question": "q2", "answer": "a2", "faithfulness": 3, "relevance": 5, "reason": "r2"},
        ]

        avg_faithfulness, avg_relevance = summarize(results)

        self.assertEqual(avg_faithfulness, 4.0)
        self.assertEqual(avg_relevance, 4.0)


if __name__ == "__main__":
    unittest.main()
