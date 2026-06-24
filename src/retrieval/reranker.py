"""Cross-encoder reranking for a pool of vector-search candidates."""


def load_cross_encoder_model(model_name: str):
    """Load a sentence-transformers CrossEncoder model by name."""
    try:
        from sentence_transformers import CrossEncoder
    except ImportError as exc:
        raise ImportError(
            "sentence-transformers is not installed. Run: pip install -r requirements.txt"
        ) from exc

    # First try local cache only. This allows true offline use after first download.
    try:
        return CrossEncoder(model_name, local_files_only=True)
    except Exception:
        pass

    # If model is not cached yet, this path downloads it once and caches it locally.
    try:
        return CrossEncoder(model_name)
    except Exception as exc:
        raise RuntimeError(f"Failed to load cross-encoder model '{model_name}': {exc}") from exc


def rerank_results(query: str, results: list[dict], model, top_k: int) -> list[dict]:
    """Reorder candidate results by cross-encoder relevance and slice to top_k."""
    if not results:
        return []

    pairs = [[query, result["text"]] for result in results]
    scores = model.predict(pairs)

    order = sorted(range(len(results)), key=lambda i: scores[i], reverse=True)[:top_k]

    reranked = []
    for new_rank, index in enumerate(order, start=1):
        reranked.append({**results[index], "rank": new_rank})

    return reranked
