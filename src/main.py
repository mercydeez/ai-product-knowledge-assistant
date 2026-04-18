"""Entry point for the project foundation."""

try:
    from src.config import (
        CHUNKS_OUTPUT_PATH,
        CHUNK_OVERLAP,
        CHUNK_SIZE,
        DATA_PATH,
        EMBEDDING_BATCH_SIZE,
        EMBEDDING_MODEL,
        EMBEDDINGS_OUTPUT_PATH,
        OLLAMA_HOST,
        OLLAMA_MODEL,
        SAMPLE_QUERY,
        TOP_K_RESULTS,
    )
    from src.embeddings.embedder import generate_embeddings_for_chunks
    from src.llm.ollama_client import call_ollama
    from src.llm.prompt_builder import build_rag_prompt
    from src.preprocessing.chunker import create_product_chunks
    from src.preprocessing.formatter import format_products_as_documents
    from src.retrieval.indexer import build_faiss_index
    from src.retrieval.search import search_similar_chunks
    from src.utils.data_loader import load_json, save_json
except ImportError:
    from config import (
        CHUNKS_OUTPUT_PATH,
        CHUNK_OVERLAP,
        CHUNK_SIZE,
        DATA_PATH,
        EMBEDDING_BATCH_SIZE,
        EMBEDDING_MODEL,
        EMBEDDINGS_OUTPUT_PATH,
        OLLAMA_HOST,
        OLLAMA_MODEL,
        SAMPLE_QUERY,
        TOP_K_RESULTS,
    )
    from embeddings.embedder import generate_embeddings_for_chunks
    from llm.ollama_client import call_ollama
    from llm.prompt_builder import build_rag_prompt
    from preprocessing.chunker import create_product_chunks
    from preprocessing.formatter import format_products_as_documents
    from retrieval.indexer import build_faiss_index
    from retrieval.search import search_similar_chunks
    from utils.data_loader import load_json, save_json


def run_chunking_pipeline() -> list[dict]:
    """Create chunk records from the raw product dataset and save them."""
    products = load_json(DATA_PATH)
    documents = format_products_as_documents(products)
    chunks = create_product_chunks(
        documents=documents,
        chunk_size=CHUNK_SIZE,
        overlap=CHUNK_OVERLAP,
    )
    save_json(chunks, CHUNKS_OUTPUT_PATH)

    print(f"Loaded {len(products)} products")
    print(f"Created {len(documents)} formatted product documents")
    print(f"Created {len(chunks)} chunks")
    print(f"Saved chunked output to: {CHUNKS_OUTPUT_PATH}")

    return chunks


def run_embeddings_pipeline() -> list[dict]:
    """Read chunk records from disk, generate embeddings, and save them."""
    chunk_records = load_json(CHUNKS_OUTPUT_PATH)
    embedded_records = generate_embeddings_for_chunks(
        chunks=chunk_records,
        model=EMBEDDING_MODEL,
        batch_size=EMBEDDING_BATCH_SIZE,
    )
    save_json(embedded_records, EMBEDDINGS_OUTPUT_PATH)

    print(f"Read {len(chunk_records)} chunks from: {CHUNKS_OUTPUT_PATH}")
    print(f"Generated {len(embedded_records)} embeddings")
    print(f"Saved embeddings to: {EMBEDDINGS_OUTPUT_PATH}")

    return embedded_records


def run_retrieval_demo(query: str, top_k: int = 3) -> list[dict]:
    """Build a FAISS index from stored embeddings and run one sample search."""
    embedded_records = load_json(EMBEDDINGS_OUTPUT_PATH)
    index, metadata_records = build_faiss_index(embedded_records)
    results = search_similar_chunks(
        query=query,
        index=index,
        embedded_records=metadata_records,
        model_name=EMBEDDING_MODEL,
        top_k=top_k,
    )

    print("\nRetrieval demo")
    print(f"Query: {query}")
    print(f"Top {top_k} results:")

    for result in results:
        print(f"\nRank: {result['rank']}")
        print(f"Score: {result['score']:.4f}")
        print(f"Chunk ID: {result['chunk_id']}")
        print(f"Product ID: {result['product_id']}")
        print(f"Product Name: {result['product_name']}")
        print(f"Text: {result['text']}")

    return results


def run_generation_pipeline(query: str, retrieved_chunks: list[dict]) -> str:
    """Build a grounded prompt and ask the local Ollama model for an answer."""
    prompt = build_rag_prompt(query=query, retrieved_chunks=retrieved_chunks)
    answer = call_ollama(
        prompt=prompt,
        model=OLLAMA_MODEL,
        host=OLLAMA_HOST,
    )

    print("\nFinal answer")
    print(answer)

    return answer


def main() -> None:
    """Run chunking, embedding, retrieval, and final answer generation."""
    chunks = run_chunking_pipeline()

    if chunks:
        print("\nSample chunk:")
        print(f"Chunk ID: {chunks[0]['chunk_id']}")
        print(f"Product: {chunks[0]['product_name']}")
        print(f"Text: {chunks[0]['text']}")

    try:
        embedded_records = run_embeddings_pipeline()
    except Exception as exc:
        raise SystemExit(
            f"\nEmbedding pipeline failed: {exc}\n"
            "Chunk file was created successfully. "
            "Check your model install, dependency setup, and local environment."
        ) from exc

    if embedded_records:
        print("\nSample embedded record:")
        print(f"Chunk ID: {embedded_records[0]['chunk_id']}")
        print(f"Product: {embedded_records[0]['product_name']}")
        print(f"Embedding length: {len(embedded_records[0]['embedding'])}")

    try:
        retrieved_chunks = run_retrieval_demo(query=SAMPLE_QUERY, top_k=TOP_K_RESULTS)
    except Exception as exc:
        raise SystemExit(
            f"\nRetrieval step failed: {exc}\n"
            "Embeddings were created, but search could not run. "
            "Check FAISS install and local model setup."
        ) from exc

    try:
        run_generation_pipeline(query=SAMPLE_QUERY, retrieved_chunks=retrieved_chunks)
    except Exception as exc:
        raise SystemExit(
            f"\nAnswer generation failed: {exc}\n"
            "Retrieval worked, but the local LLM step could not complete. "
            "Make sure Ollama is running and the model is available locally."
        ) from exc


if __name__ == "__main__":
    main()
