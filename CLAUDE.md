# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the FastAPI backend (serves /health and /ask)
uvicorn src.api.app:app --reload

# Run the local CLI smoke test (single sample question end-to-end)
python src/main.py

# Run all tests
python -m unittest discover -s tests

# Run a single test
python -m unittest tests.test_data_loader.TestDataLoader.test_products_can_be_loaded
```

Test the running API (PowerShell):

```powershell
$body = @{ question = "I need a breathable cotton shirt for everyday use." } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/ask" -Method Post -ContentType "application/json" -Body $body
```

```bash
# Run the Next.js frontend (separate terminal, requires the backend running)
cd frontend && npm install && npm run dev   # http://localhost:3000

# Build/lint the frontend
cd frontend && npm run build
cd frontend && npm run lint
```

## Architecture

This is a no-LangChain RAG (Retrieval-Augmented Generation) pipeline over a static JSON product catalog. It runs fully locally: sentence-transformers for embeddings, FAISS for vector search, and Ollama for answer generation.

**Pipeline (data flow):**
`data/products.json` → `preprocessing/formatter.py` (product dict → text document) → `preprocessing/chunker.py` (line-based chunks with overlap) → `embeddings/embedder.py` (sentence-transformers vectors) → `retrieval/indexer.py` (FAISS `IndexFlatIP`, L2-normalized so inner product == cosine similarity) → `retrieval/search.py` (embed query, top-k search) → `llm/prompt_builder.py` (grounded prompt) → `llm/provider.py` (dispatches to `llm/groq_client.py` or `llm/ollama_client.py` based on `LLM_PROVIDER`).

**LLM provider is pluggable.** `LLM_PROVIDER` (`groq` by default, or `ollama`) controls which client `generate_answer()` in `llm/provider.py` calls. Groq needs `GROQ_API_KEY` set in `.env` (free key at console.groq.com) — without it, `/ask` returns a clear 500 telling you so. Ollama needs a local server running with the model pulled. `ProductRAGService` just calls `generate_answer(...)`; it doesn't know which provider is active.

**`ProductRAGService` (`src/services/rag_service.py`) is the orchestration core.** Both entrypoints (`main.py` CLI and the FastAPI app) construct one service, call `initialize()`, then `answer_question()`. Everything else is stateless helper functions wired together here.

**Lazy artifact generation:** `initialize()` calls `_ensure_rag_artifacts()`, which generates `data/product_chunks.json` and `data/product_embeddings.json` on disk only if they are missing. Deleting these files forces a rebuild on next startup (e.g., after changing `products.json`, chunk settings, or the embedding model). The FAISS index and embedding model are loaded once at startup and cached on the service instance — they are expensive and meant to be reused across requests.

**FastAPI wiring:** `api/app.py` builds the service in the `lifespan` startup hook and stores it on `app.state.rag_service`. Routes (`api/routes.py`) read it back via the `get_rag_service` dependency — there is one shared, pre-warmed service per process, not one per request.

**Frontend (`frontend/`):** a separate Next.js 16 (App Router, TypeScript, Tailwind v4) app, scaffolded independently of the Python backend — it has its own `package.json`/`node_modules` and does not use the dual-import pattern below. It calls `POST /ask` via `frontend/lib/api.ts`, reading the backend URL from `NEXT_PUBLIC_API_BASE_URL` (see `frontend/.env.local.example`). The UI was ported from a Claude Design prototype (`design.md` §6); the design's mocked client-side retrieval/timers were replaced with real fetch calls and a real `/health` poll (`components/ApiStatusBadge.tsx`).

**Each source carries `category`/`color` from the product record, not the chunk text.** A retrieved chunk only covers a few lines of a product's formatted document (see "Chunking is line-based" below), so it often lacks the `Category`/`Color` lines entirely. `ProductRAGService.retrieve_sources` (`services/rag_service.py`) enriches each result by looking up `product_id` against `self.product_lookup` (built from `products.json` in `initialize()`) before returning it. Don't go back to parsing these out of `text` client-side.

## Conventions and gotchas

- **Dual-import pattern:** nearly every module under `src/` does `try: from src.X ... except ImportError: from X ...`. This lets the same file work both as a package (`uvicorn src.api.app:app`, run from project root) and when run with `src/` on the path. Preserve this pattern when adding modules.
- **Config is centralized in `src/config.py`**, loaded from `.env` (copy `.env.example` → `.env`). All tunables — `EMBEDDING_MODEL`, `OLLAMA_MODEL`, `TOP_K_RESULTS`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, etc. — flow through here and are passed as constructor defaults to `ProductRAGService`. Don't hardcode these elsewhere.
- **External dependencies the pipeline assumes at runtime:** the sentence-transformers model is downloaded from Hugging Face on first use then cached (offline thereafter via `local_files_only=True` fast path); a local Ollama server must be running with the configured model pulled (e.g. `ollama pull llama3.2:3b`).
- **Chunking is line-based**, not token-based: `CHUNK_SIZE`/`CHUNK_OVERLAP` count lines of the formatted product document, and each product field is one line (see `formatter.py`).
- `requirements.txt` is trimmed to the 8 packages actually imported by `src/` (`fastapi`, `uvicorn`, `pydantic`, `python-dotenv`, `sentence-transformers`, `faiss-cpu`, `numpy`, `groq`). If you add a new direct import, add it here too — don't let it drift back into a full env dump.
