"""Helpers for building a FAISS index from stored chunk embeddings."""

import numpy as np


def build_faiss_index(embedded_records: list[dict]):
    """Build and return a FAISS index plus the original metadata records."""
    if not embedded_records:
        raise ValueError("No embedded records found. Run the embedding step first.")

    try:
        import faiss
    except ImportError as exc:
        raise ImportError("faiss-cpu is not installed. Run: pip install -r requirements.txt") from exc

    embedding_matrix = np.array(
        [record["embedding"] for record in embedded_records],
        dtype="float32",
    )

    if embedding_matrix.ndim != 2:
        raise ValueError("Embedding matrix must be 2-dimensional.")

    # Normalize vectors so inner product works like cosine similarity.
    faiss.normalize_L2(embedding_matrix)

    dimension = embedding_matrix.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embedding_matrix)

    return index, embedded_records
