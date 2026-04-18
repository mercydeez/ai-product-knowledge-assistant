"""Helpers for generating embeddings with sentence-transformers."""


def load_embedding_model(model_name: str):
    """Load a sentence-transformers model by name."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise ImportError(
            "sentence-transformers is not installed. Run: pip install -r requirements.txt"
        ) from exc

    # First try local cache only. This allows true offline use after first download.
    try:
        return SentenceTransformer(model_name, local_files_only=True)
    except Exception:
        pass

    # If model is not cached yet, this path downloads it once and caches it locally.
    try:
        return SentenceTransformer(model_name)
    except Exception as exc:
        raise RuntimeError(f"Failed to load embedding model '{model_name}': {exc}") from exc


def create_embedding_batch(
    model,
    texts: list[str],
    batch_size: int,
) -> list[list[float]]:
    """Generate embeddings for a batch of text strings."""
    try:
        # encode() converts each text string into a dense vector (list of floats).
        vectors = model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
    except Exception as exc:
        raise RuntimeError(f"Embedding generation failed: {exc}") from exc

    return vectors.tolist()


def generate_embeddings_for_chunks(
    chunks: list[dict],
    model: str = "all-MiniLM-L6-v2",
    batch_size: int = 10,
) -> list[dict]:
    """Generate and return embedded chunk records with metadata."""
    if not chunks:
        raise ValueError("No chunk data found. Run the chunking step first.")

    if batch_size <= 0:
        raise ValueError("EMBEDDING_BATCH_SIZE must be greater than 0.")

    model_instance = load_embedding_model(model)
    embedded_records = []

    for start_index in range(0, len(chunks), batch_size):
        # Process small batches to keep memory use predictable and code easy to follow.
        batch = chunks[start_index : start_index + batch_size]
        batch_texts = []

        for chunk in batch:
            text = chunk.get("text", "").strip()
            if not text:
                raise ValueError(f"Chunk {chunk.get('chunk_id', 'unknown')} has empty text.")
            batch_texts.append(text)

        batch_embeddings = create_embedding_batch(
            model=model_instance,
            texts=batch_texts,
            batch_size=batch_size,
        )

        for chunk, embedding in zip(batch, batch_embeddings):
            embedded_records.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "product_id": chunk["product_id"],
                    "product_name": chunk["product_name"],
                    "text": chunk["text"],
                    "embedding": embedding,
                }
            )

    return embedded_records
