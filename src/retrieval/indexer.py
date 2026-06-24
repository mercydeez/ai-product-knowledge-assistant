"""Helpers for building a ChromaDB collection from stored chunk embeddings."""


def build_chroma_collection(
    embedded_records: list[dict],
    persist_directory: str,
    collection_name: str = "product_chunks",
):
    """Get or create a persistent ChromaDB collection, seeding it if empty."""
    if not embedded_records:
        raise ValueError("No embedded records found. Run the embedding step first.")

    try:
        import chromadb
        from chromadb.config import Settings
    except ImportError as exc:
        raise ImportError("chromadb is not installed. Run: pip install -r requirements.txt") from exc

    client = chromadb.PersistentClient(
        path=persist_directory,
        settings=Settings(anonymized_telemetry=False),
    )

    # Cosine space matches the normalized inner-product similarity the rest of
    # the pipeline (and the API's "score") was built around.
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    if collection.count() == 0:
        collection.add(
            ids=[record["chunk_id"] for record in embedded_records],
            embeddings=[record["embedding"] for record in embedded_records],
            documents=[record["text"] for record in embedded_records],
            metadatas=[
                {
                    "product_id": record["product_id"],
                    "product_name": record["product_name"],
                }
                for record in embedded_records
            ],
        )

    return collection
