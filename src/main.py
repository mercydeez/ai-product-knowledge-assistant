"""Local CLI smoke test for the reusable RAG service."""

try:
    from src.config import SAMPLE_QUERY
    from src.services.rag_service import ProductRAGService
except ImportError:
    from config import SAMPLE_QUERY
    from services.rag_service import ProductRAGService


def main() -> None:
    """Run one local sample question using the shared RAG service."""
    rag_service = ProductRAGService()

    try:
        rag_service.initialize()
        result = rag_service.answer_question(SAMPLE_QUERY)
    except Exception as exc:
        raise SystemExit(f"Local RAG demo failed: {exc}") from exc

    print(f"Question: {result['question']}")
    print("\nSources:")

    for source in result["sources"]:
        print(f"\nRank: {source['rank']}")
        print(f"Score: {source['score']:.4f}")
        print(f"Product Name: {source['product_name']}")
        print(f"Chunk ID: {source['chunk_id']}")
        print(f"Text: {source['text']}")

    print("\nAnswer:")
    print(result["answer"])


if __name__ == "__main__":
    main()
