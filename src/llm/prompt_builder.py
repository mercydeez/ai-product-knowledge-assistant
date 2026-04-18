"""Helpers for building grounded prompts from retrieved chunks."""


def format_retrieved_chunks(results: list[dict]) -> str:
    """Convert retrieval results into readable context for the LLM."""
    formatted_chunks = []

    for result in results:
        formatted_chunks.append(
            "\n".join(
                [
                    f"Rank: {result['rank']}",
                    f"Score: {result['score']:.4f}",
                    f"Chunk ID: {result['chunk_id']}",
                    f"Product ID: {result['product_id']}",
                    f"Product Name: {result['product_name']}",
                    f"Text: {result['text']}",
                ]
            )
        )

    return "\n\n".join(formatted_chunks)


def build_rag_prompt(query: str, retrieved_chunks: list[dict]) -> str:
    """Build a simple grounded prompt for the local LLM."""
    context = format_retrieved_chunks(retrieved_chunks)

    return f"""You are an AI assistant for a fashion and e-commerce business.

Answer the user's question using only the retrieved context below.
If the answer is not clearly present in the context, say:
"I do not have enough information in the retrieved context to answer that."

Keep the answer concise, factual, and helpful.

User Question:
{query}

Retrieved Context:
{context}

Final Answer:
"""
