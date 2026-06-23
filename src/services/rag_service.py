"""Reusable service layer for the product knowledge assistant."""

from pathlib import Path

try:
    from src.config import (
        CHUNKS_OUTPUT_PATH,
        CHUNK_OVERLAP,
        CHUNK_SIZE,
        DATA_PATH,
        EMBEDDING_BATCH_SIZE,
        EMBEDDING_MODEL,
        EMBEDDINGS_OUTPUT_PATH,
        OLLAMA_HOST,
        OLLAMA_MODEL,
        TOP_K_RESULTS,
    )
    from src.embeddings.embedder import generate_embeddings_for_chunks, load_embedding_model
    from src.llm.ollama_client import call_ollama
    from src.llm.prompt_builder import build_rag_prompt
    from src.preprocessing.chunker import create_product_chunks
    from src.preprocessing.formatter import format_products_as_documents
    from src.retrieval.indexer import build_faiss_index
    from src.retrieval.search import search_similar_chunks
    from src.utils.data_loader import load_json, save_json
except ImportError:
    from config import (
        CHUNKS_OUTPUT_PATH,
        CHUNK_OVERLAP,
        CHUNK_SIZE,
        DATA_PATH,
        EMBEDDING_BATCH_SIZE,
        EMBEDDING_MODEL,
        EMBEDDINGS_OUTPUT_PATH,
        OLLAMA_HOST,
        OLLAMA_MODEL,
        TOP_K_RESULTS,
    )
    from embeddings.embedder import generate_embeddings_for_chunks, load_embedding_model
    from llm.ollama_client import call_ollama
    from llm.prompt_builder import build_rag_prompt
    from preprocessing.chunker import create_product_chunks
    from preprocessing.formatter import format_products_as_documents
    from retrieval.indexer import build_faiss_index
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
        ollama_host: str = OLLAMA_HOST,
        ollama_model: str = OLLAMA_MODEL,
        top_k_results: int = TOP_K_RESULTS,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP,
    ) -> None:
        self.data_path = data_path
        self.chunks_output_path = chunks_output_path
        self.embeddings_output_path = embeddings_output_path
        self.embedding_model_name = embedding_model_name
        self.embedding_batch_size = embedding_batch_size
        self.ollama_host = ollama_host
        self.ollama_model = ollama_model
        self.top_k_results = top_k_results
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.index = None
        self.records: list[dict] = []
        self.embedding_model = None

    def initialize(self) -> None:
        """Load everything needed for retrieval once at application startup."""
        self._ensure_rag_artifacts()

        # These objects are expensive enough that we want to reuse them.
        self.records = load_json(self.embeddings_output_path)
        self.index, self.records = build_faiss_index(self.records)
        self.embedding_model = load_embedding_model(self.embedding_model_name)

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

        if self.index is None or self.embedding_model is None or not self.records:
            raise RuntimeError("RAG service is not initialized.")

        result_count = top_k or self.top_k_results

        return search_similar_chunks(
            query=question,
            index=self.index,
            embedded_records=self.records,
            model_name=self.embedding_model_name,
            top_k=result_count,
            model_instance=self.embedding_model,
        )

    def answer_question(self, question: str, top_k: int | None = None) -> dict:
        """Run retrieval and grounded answer generation for one question."""
        sources = self.retrieve_sources(question=question, top_k=top_k)
        prompt = build_rag_prompt(query=question, retrieved_chunks=sources)
        answer = call_ollama(
            prompt=prompt,
            model=self.ollama_model,
            host=self.ollama_host,
        )

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
        }
