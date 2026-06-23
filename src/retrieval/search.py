"""Helpers for semantic similarity search on a FAISS index."""

import numpy as np


def embed_query_with_model(query: str, model) -> np.ndarray:
    """Convert a user query string into an embedding vector with a loaded model."""
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    query_vector = model.encode(
        [query],
        show_progress_bar=False,
        convert_to_numpy=True,
    )[0]

    return np.array(query_vector, dtype="float32")


def embed_query(query: str, model_name: str) -> np.ndarray:
    """Convert a user query string into an embedding vector."""
    try:
        from src.embeddings.embedder import load_embedding_model
    except ImportError:
        from embeddings.embedder import load_embedding_model

    model = load_embedding_model(model_name)
    return embed_query_with_model(query=query, model=model)


def search_faiss_index(
    index,
    embedded_records: list[dict],
    query_vector: np.ndarray,
    top_k: int = 3,
) -> list[dict]:
    """Search a FAISS index and return top_k results with metadata."""
    if top_k <= 0:
        raise ValueError("top_k must be greater than 0.")

    try:
        import faiss
    except ImportError as exc:
        raise ImportError("faiss-cpu is not installed. Run: pip install -r requirements.txt") from exc

    query_matrix = np.array([query_vector], dtype="float32")
    faiss.normalize_L2(query_matrix)

    scores, indices = index.search(query_matrix, top_k)
    results = []

    for rank, (score, record_index) in enumerate(zip(scores[0], indices[0]), start=1):
        if record_index < 0:
            continue

        record = embedded_records[int(record_index)]
        results.append(
            {
                "rank": rank,
                "score": float(score),
                "chunk_id": record["chunk_id"],
                "product_id": record["product_id"],
                "product_name": record["product_name"],
                "text": record["text"],
            }
        )

    return results


def search_similar_chunks(
    query: str,
    index,
    embedded_records: list[dict],
    model_name: str,
    top_k: int = 3,
    model_instance=None,
) -> list[dict]:
    """Embed the query and search for the most similar product chunks."""
    if model_instance is None:
        query_vector = embed_query(query=query, model_name=model_name)
    else:
        query_vector = embed_query_with_model(query=query, model=model_instance)

    return search_faiss_index(
        index=index,
        embedded_records=embedded_records,
        query_vector=query_vector,
        top_k=top_k,
    )
