"""Reusable service layer for the product knowledge assistant."""

from pathlib import Path

try:
    from src.config import (
        CHROMA_COLLECTION_NAME,
        CHROMA_PERSIST_PATH,
        CHUNK_OVERLAP,
        CHUNK_SIZE,
        CHUNKS_OUTPUT_PATH,
        DATA_PATH,
        EMBEDDING_BATCH_SIZE,
        EMBEDDING_MODEL,
        EMBEDDINGS_OUTPUT_PATH,
        GROQ_API_KEY,
        GROQ_MODEL,
        LLM_PROVIDER,
        OLLAMA_HOST,
        OLLAMA_MODEL,
        TOP_K_RESULTS,
    )
    from src.embeddings.embedder import generate_embeddings_for_chunks, load_embedding_model
    from src.llm.prompt_builder import build_rag_prompt
    from src.llm.provider import generate_answer
    from src.preprocessing.chunker import create_product_chunks
    from src.preprocessing.formatter import format_products_as_documents
    from src.retrieval.indexer import build_chroma_collection
    from src.retrieval.search import search_similar_chunks
    from src.utils.data_loader import load_json, save_json
except ImportError:
    from config import (
        CHROMA_COLLECTION_NAME,
        CHROMA_PERSIST_PATH,
        CHUNK_OVERLAP,
        CHUNK_SIZE,
        CHUNKS_OUTPUT_PATH,
        DATA_PATH,
        EMBEDDING_BATCH_SIZE,
        EMBEDDING_MODEL,
        EMBEDDINGS_OUTPUT_PATH,
        GROQ_API_KEY,
        GROQ_MODEL,
        LLM_PROVIDER,
        OLLAMA_HOST,
        OLLAMA_MODEL,
        TOP_K_RESULTS,
    )
    from embeddings.embedder import generate_embeddings_for_chunks, load_embedding_model
    from llm.prompt_builder import build_rag_prompt
    from llm.provider import generate_answer
    from preprocessing.chunker import create_product_chunks
    from preprocessing.formatter import format_products_as_documents
    from retrieval.indexer import build_chroma_collection
    from retrieval.search import search_similar_chunks
    from utils.data_loader import load_json, save_json


class ProductRAGService:
    """Service object that owns the full RAG pipeline and cached resources."""

    def __init__(
        self,
        data_path: str = DATA_PATH,
        chunks_output_path: str = CHUNKS_OUTPUT_PATH,
        embeddings_output_path: str = EMBEDDINGS_OUTPUT_PATH,
        embedding_model_name: str = EMBEDDING_MODEL,
        embedding_batch_size: int = EMBEDDING_BATCH_SIZE,
        chroma_persist_path: str = CHROMA_PERSIST_PATH,
        chroma_collection_name: str = CHROMA_COLLECTION_NAME,
        llm_provider: str = LLM_PROVIDER,
        ollama_host: str = OLLAMA_HOST,
        ollama_model: str = OLLAMA_MODEL,
        groq_api_key: str = GROQ_API_KEY,
        groq_model: str = GROQ_MODEL,
        top_k_results: int = TOP_K_RESULTS,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP,
    ) -> None:
        self.data_path = data_path
        self.chunks_output_path = chunks_output_path
        self.embeddings_output_path = embeddings_output_path
        self.embedding_model_name = embedding_model_name
        self.embedding_batch_size = embedding_batch_size
        self.chroma_persist_path = chroma_persist_path
        self.chroma_collection_name = chroma_collection_name
        self.llm_provider = llm_provider
        self.ollama_host = ollama_host
        self.ollama_model = ollama_model
        self.groq_api_key = groq_api_key
        self.groq_model = groq_model
        self.top_k_results = top_k_results
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.collection = None
        self.records: list[dict] = []
        self.embedding_model = None
        self.product_lookup: dict[str, dict] = {}

    def initialize(self) -> None:
        """Load everything needed for retrieval once at application startup."""
        self._ensure_rag_artifacts()

        # These objects are expensive enough that we want to reuse them.
        self.records = load_json(self.embeddings_output_path)
        self.collection = build_chroma_collection(
            embedded_records=self.records,
            persist_directory=self.chroma_persist_path,
            collection_name=self.chroma_collection_name,
        )
        self.embedding_model = load_embedding_model(self.embedding_model_name)

        # A single chunk only covers a few product fields (see chunker.py), so
        # sources are enriched from the full product record for display.
        products = load_json(self.data_path)
        self.product_lookup = {product["id"]: product for product in products}

    def _create_chunk_records(self) -> list[dict]:
        """Create chunk records from raw product data and save them to disk."""
        products = load_json(self.data_path)
        documents = format_products_as_documents(products)
        chunks = create_product_chunks(
            documents=documents,
            chunk_size=self.chunk_size,
            overlap=self.chunk_overlap,
        )
        save_json(chunks, self.chunks_output_path)
        return chunks

    def _create_embedding_records(self) -> list[dict]:
        """Create embeddings from saved chunk records and write them to disk."""
        chunk_records = load_json(self.chunks_output_path)
        embedded_records = generate_embeddings_for_chunks(
            chunks=chunk_records,
            model=self.embedding_model_name,
            batch_size=self.embedding_batch_size,
        )
        save_json(embedded_records, self.embeddings_output_path)
        return embedded_records

    def _ensure_rag_artifacts(self) -> None:
        """Make sure chunk and embedding files exist before startup completes."""
        if not Path(self.chunks_output_path).exists():
            self._create_chunk_records()

        if not Path(self.embeddings_output_path).exists():
            self._create_embedding_records()

    def retrieve_sources(self, question: str, top_k: int | None = None) -> list[dict]:
        """Return the top matching chunks for a user question."""
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        if self.collection is None or self.embedding_model is None or not self.records:
            raise RuntimeError("RAG service is not initialized.")

        result_count = top_k or self.top_k_results

        sources = search_similar_chunks(
            query=question,
            collection=self.collection,
            model_name=self.embedding_model_name,
            top_k=result_count,
            model_instance=self.embedding_model,
        )

        for source in sources:
            product = self.product_lookup.get(source["product_id"], {})
            source["category"] = product.get("category", "")
            source["color"] = product.get("color", "")

        return sources

    def answer_question(self, question: str, top_k: int | None = None) -> dict:
        """Run retrieval and grounded answer generation for one question."""
        sources = self.retrieve_sources(question=question, top_k=top_k)
        prompt = build_rag_prompt(query=question, retrieved_chunks=sources)
        answer = generate_answer(
            prompt=prompt,
            provider=self.llm_provider,
            ollama_host=self.ollama_host,
            ollama_model=self.ollama_model,
            groq_api_key=self.groq_api_key,
            groq_model=self.groq_model,
        )

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
        }
