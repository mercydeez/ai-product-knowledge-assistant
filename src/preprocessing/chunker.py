"""Helpers for splitting formatted product documents into simple chunks."""


def chunk_text(text: str, chunk_size: int = 40, overlap: int = 10) -> list[str]:
    """Split text into small line-based chunks with a little overlap."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    if not lines:
        return []

    chunks = []
    start = 0
    step = max(chunk_size - overlap, 1)

    # We move through the document by groups of lines to keep product fields readable.
    while start < len(lines):
        end = start + chunk_size
        chunk_lines = lines[start:end]
        chunks.append("\n".join(chunk_lines))

        if end >= len(lines):
            break

        start += step

    return chunks


def create_product_chunks(
    documents: list[dict],
    chunk_size: int = 40,
    overlap: int = 10,
) -> list[dict]:
    """Create chunk records with product metadata for future embeddings."""
    all_chunks = []

    for document in documents:
        text_chunks = chunk_text(
            text=document["text"],
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for index, text_chunk in enumerate(text_chunks, start=1):
            all_chunks.append(
                {
                    "chunk_id": f"{document['product_id']}_chunk_{index}",
                    "product_id": document["product_id"],
                    "product_name": document["product_name"],
                    "text": text_chunk,
                }
            )

    return all_chunks
