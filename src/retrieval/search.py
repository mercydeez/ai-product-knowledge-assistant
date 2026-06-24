"""Helpers for semantic similarity search against a ChromaDB collection."""

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


def search_chroma_collection(
    collection,
    query_vector: np.ndarray,
    top_k: int = 3,
) -> list[dict]:
    """Query a ChromaDB collection and return top_k results with metadata."""
    if top_k <= 0:
        raise ValueError("top_k must be greater than 0.")

    result = collection.query(
        query_embeddings=[query_vector.tolist()],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    results = []

    for rank, (chunk_id, text, metadata, distance) in enumerate(
        zip(result["ids"][0], result["documents"][0], result["metadatas"][0], result["distances"][0]),
        start=1,
    ):
        results.append(
            {
                "rank": rank,
                # Cosine space distances are 1 - cosine_similarity, so undo that
                # to keep the same 0..1 "higher is better" score the API returns.
                "score": 1.0 - float(distance),
                "chunk_id": chunk_id,
                "product_id": metadata["product_id"],
                "product_name": metadata["product_name"],
                "text": text,
            }
        )

    return results


def search_similar_chunks(
    query: str,
    collection,
    model_name: str,
    top_k: int = 3,
    model_instance=None,
) -> list[dict]:
    """Embed the query and search for the most similar product chunks."""
    if model_instance is None:
        query_vector = embed_query(query=query, model_name=model_name)
    else:
        query_vector = embed_query_with_model(query=query, model=model_instance)

    return search_chroma_collection(
        collection=collection,
        query_vector=query_vector,
        top_k=top_k,
    )
