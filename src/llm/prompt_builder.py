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
                    f"Category: {result['category']}",
                    f"Color: {result['color']}",
                    f"Text: {result['text']}",
                ]
            )
        )

    return "\n\n".join(formatted_chunks)


def build_rag_prompt(query: str, retrieved_chunks: list[dict]) -> str:
    """Build a simple grounded prompt for the local LLM."""
    context = format_retrieved_chunks(retrieved_chunks)

    return f"""You are an AI assistant for a fashion and e-commerce business. You only
answer questions about the products in this catalog — never general knowledge,
coding, math, or any other topic unrelated to the catalog, even if asked directly.

Answer the user's question using only facts explicitly stated in the retrieved
context below. Do not infer, guess, or imply that a product satisfies a use
case, occasion, or property the context does not explicitly mention — for
example, if the user asks for something the catalog does not carry (e.g. "a
night dress" when the context only describes day dresses), say plainly that
the catalog does not have that exact item, then offer the closest retrieved
products as alternatives rather than claiming they meet the request.

The context below is only the top few retrieved matches, not the entire
catalog — never claim the catalog "only has" or "only features" certain
categories just because that's all you were shown. Phrase it as what the
retrieved results don't include (e.g. "the closest matches don't include
shoes"), not as a statement about the whole catalog's contents.

If the answer is not clearly present in the context, or the question is not
about a catalog product, say:
"I do not have enough information in the retrieved context to answer that."

Keep the answer concise, factual, and helpful.

User Question:
{query}

Retrieved Context:
{context}

Final Answer:
"""
