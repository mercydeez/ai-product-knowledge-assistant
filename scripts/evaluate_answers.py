"""LLM-judge evaluation: scores generated answers for faithfulness and relevance.

Unlike evaluate_rag.py (retrieval-only), this calls the real LLM provider
twice per question (once to answer, once to grade), so it needs a real
GROQ_API_KEY and is not run in CI. Expect ~2x len(EVAL_QUESTIONS) live Groq
calls and real API quota usage.

Usage:
    python scripts/evaluate_answers.py
    python scripts/evaluate_answers.py --min-score 3.5
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eval_questions import EVAL_QUESTIONS  # noqa: E402

from src.config import GROQ_API_KEY, GROQ_MODEL  # noqa: E402
from src.llm.groq_client import call_groq  # noqa: E402
from src.llm.prompt_builder import format_retrieved_chunks  # noqa: E402
from src.services.rag_service import ProductRAGService  # noqa: E402

JUDGE_PROMPT_TEMPLATE = """You are grading an AI shopping assistant's answer for faithfulness and relevance.

Question: {question}

Retrieved catalog context the assistant was given:
{context}

Assistant's answer:
{answer}

Score the answer on two dimensions, each from 1 (worst) to 5 (best):
- faithfulness: does the answer only state facts present in the retrieved context, with no invented details?
- relevance: does the answer actually address the user's question?

Respond with ONLY a JSON object, no other text, in this exact shape:
{{"faithfulness": <int>, "relevance": <int>, "reason": "<one sentence>"}}
"""


def _extract_json(raw: str) -> dict:
    """Parse a judge response, tolerating a ```json fence around the object."""
    text = raw.strip()

    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    return json.loads(text)


def judge_answer(question: str, context: str, answer: str) -> dict:
    """Ask Groq to grade one answer for faithfulness/relevance, as strict JSON."""
    prompt = JUDGE_PROMPT_TEMPLATE.format(question=question, context=context, answer=answer)
    raw = call_groq(prompt=prompt, model=GROQ_MODEL, api_key=GROQ_API_KEY, temperature=0.0)
    return _extract_json(raw)


def evaluate(top_k: int) -> list[dict]:
    """Generate a real answer for every eval question and have Groq grade it."""
    rag_service = ProductRAGService()
    rag_service.initialize()

    results = []

    for case in EVAL_QUESTIONS:
        outcome = rag_service.answer_question(case["question"], top_k=top_k)
        context = format_retrieved_chunks(outcome["sources"])
        judged = judge_answer(case["question"], context, outcome["answer"])

        results.append(
            {
                "question": case["question"],
                "answer": outcome["answer"],
                "faithfulness": judged["faithfulness"],
                "relevance": judged["relevance"],
                "reason": judged.get("reason", ""),
            }
        )

    return results


def summarize(results: list[dict]) -> tuple[float, float]:
    """Print a results table plus average faithfulness/relevance, and return the averages."""
    avg_faithfulness = sum(r["faithfulness"] for r in results) / len(results)
    avg_relevance = sum(r["relevance"] for r in results) / len(results)

    print(f"{'Question':<55} {'Faith':<6} {'Relev':<6} {'Reason'}")
    print("-" * 100)
    for r in results:
        question = r["question"] if len(r["question"]) <= 53 else r["question"][:50] + "..."
        reason = r["reason"] if len(r["reason"]) <= 35 else r["reason"][:32] + "..."
        print(f"{question:<55} {r['faithfulness']:<6} {r['relevance']:<6} {reason}")
    print("-" * 100)
    print(f"avg faithfulness: {avg_faithfulness:.2f}/5  avg relevance: {avg_relevance:.2f}/5")

    return avg_faithfulness, avg_relevance


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate RAG answer quality via an LLM judge.")
    parser.add_argument("--top-k", type=int, default=3, help="Number of chunks to retrieve per question.")
    parser.add_argument(
        "--min-score",
        type=float,
        default=4.0,
        help="Exit with a non-zero status if either average score falls below this (1-5 scale).",
    )
    args = parser.parse_args()

    results = evaluate(top_k=args.top_k)
    avg_faithfulness, avg_relevance = summarize(results)

    if avg_faithfulness < args.min_score or avg_relevance < args.min_score:
        raise SystemExit(
            f"Average score below {args.min_score:.2f} "
            f"(faithfulness={avg_faithfulness:.2f}, relevance={avg_relevance:.2f})."
        )


if __name__ == "__main__":
    main()
