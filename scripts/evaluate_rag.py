"""Retrieval-only RAG evaluation: hit-rate@k and MRR over a small question set.

Runs the real embedding model + ChromaDB collection but never calls the LLM
provider, so it needs no GROQ_API_KEY and works offline in CI.

Usage:
    python scripts/evaluate_rag.py
    python scripts/evaluate_rag.py --top-k 5 --min-hit-rate 0.9
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.services.rag_service import ProductRAGService  # noqa: E402


# Each question is phrased to clearly match exactly one product's formatted
# document (see src/preprocessing/formatter.py), mirroring data/products.json.
def _case(question: str, expected_product_id: str) -> dict:
    return {"question": question, "expected_product_id": expected_product_id}


EVAL_QUESTIONS = [
    _case("I need a breathable white cotton shirt for everyday wear.", "SKU-1001"),
    _case("Looking for black slim-fit stretch denim jeans for smart casual wear.", "SKU-1002"),
    _case("Show me a lightweight floral midi dress for warm weather.", "SKU-1003"),
    _case("I want a lightweight linen overshirt for layering.", "SKU-1004"),
    _case("Recommend a moisture-wicking navy polo for travel or active days.", "SKU-1005"),
    _case("I need tailored olive straight-leg trousers for the office.", "SKU-1006"),
    _case("Looking for a soft lavender knit cardigan for transitional weather.", "SKU-1007"),
    _case("Show me charcoal cargo joggers with utility pockets.", "SKU-1008"),
    _case("I want an elegant emerald satin blouse for a dressy occasion.", "SKU-1009"),
    _case("Recommend a water-resistant forest green hooded jacket for hiking.", "SKU-1010"),
    _case("I need a relaxed-fit heather grey graphic t-shirt for weekends.", "SKU-1011"),
    _case("Show me a flowing dusty rose pleated midi skirt.", "SKU-1012"),
    _case("I want a relaxed chambray shirt with roll-up sleeves for the weekend.", "SKU-1013"),
    _case("Show me a ribbed tank top for layering in warm weather.", "SKU-1014"),
    _case("I need flowing wide-leg palazzo pants with a high-rise waist.", "SKU-1015"),
    _case("Looking for tailored chino shorts with a bit of stretch.", "SKU-1016"),
    _case("Recommend a mustard wrap dress with three-quarter sleeves.", "SKU-1017"),
    _case("Show me a sleeveless shift dress for easy day-to-evening wear.", "SKU-1018"),
    _case("I want a lightweight quilted puffer vest for extra warmth.", "SKU-1019"),
    _case("Looking for a classic washed denim jacket with chest pockets.", "SKU-1020"),
    _case("I need a fitted sage turtleneck pullover to layer under jackets.", "SKU-1021"),
    _case("Show me an oversized chunky knit sweater for cold weather.", "SKU-1022"),
    _case("Recommend a mustard A-line denim skirt with a button-front placket.", "SKU-1023"),
    _case("I want a flirty pleated mini skirt with a chiffon overlay.", "SKU-1024"),
]


def evaluate(top_k: int) -> list[dict]:
    """Run retrieval for every eval question and record hit/rank against the expected product."""
    rag_service = ProductRAGService()
    rag_service.initialize()

    results = []

    for case in EVAL_QUESTIONS:
        sources = rag_service.retrieve_sources(case["question"], top_k=top_k)
        product_ids = [source["product_id"] for source in sources]

        hit = case["expected_product_id"] in product_ids
        rank = product_ids.index(case["expected_product_id"]) + 1 if hit else None

        results.append(
            {
                "question": case["question"],
                "expected_product_id": case["expected_product_id"],
                "hit": hit,
                "rank": rank,
            }
        )

    return results


def summarize(results: list[dict], top_k: int) -> float:
    """Print a results table plus aggregate hit-rate/MRR, and return the hit-rate."""
    hit_count = sum(1 for r in results if r["hit"])
    hit_rate = hit_count / len(results)
    mrr = sum((1 / r["rank"]) for r in results if r["hit"]) / len(results)

    print(f"{'Question':<60} {'Expected':<10} {'Hit':<5} {'Rank'}")
    print("-" * 85)
    for r in results:
        question = r["question"] if len(r["question"]) <= 58 else r["question"][:55] + "..."
        hit_marker = "Y" if r["hit"] else "N"
        print(f"{question:<60} {r['expected_product_id']:<10} {hit_marker:<5} {r['rank'] or '-'}")
    print("-" * 85)
    print(f"top_k={top_k}  hit-rate@k: {hit_rate:.2%} ({hit_count}/{len(results)})  MRR: {mrr:.3f}")

    return hit_rate


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate RAG retrieval quality (hit-rate/MRR).")
    parser.add_argument("--top-k", type=int, default=3, help="Number of chunks to retrieve per question.")
    parser.add_argument(
        "--min-hit-rate",
        type=float,
        default=0.8,
        help="Exit with a non-zero status if hit-rate falls below this fraction.",
    )
    args = parser.parse_args()

    results = evaluate(top_k=args.top_k)
    hit_rate = summarize(results, top_k=args.top_k)

    if hit_rate < args.min_hit_rate:
        raise SystemExit(f"Hit-rate {hit_rate:.2%} is below the {args.min_hit_rate:.2%} threshold.")


if __name__ == "__main__":
    main()
