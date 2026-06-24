# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the FastAPI backend (serves /health and /ask)
uvicorn src.api.app:app --reload

# Run the local CLI smoke test (single sample question end-to-end)
python src/main.py

# Install test-only deps once (httpx, pinned for fastapi.testclient — see requirements-dev.txt)
pip install -r requirements-dev.txt

# Run all tests
python -m unittest discover -s tests

# Run a single test
python -m unittest tests.test_retrieval.TestSearchSimilarChunks.test_closest_vector_ranks_first_with_expected_shape
```

Test the running API (PowerShell):

```powershell
$body = @{ question = "I need a breathable cotton shirt for everyday use." } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/ask" -Method Post -ContentType "application/json" -Body $body
```

```bash
# Build and run the backend container locally (mirrors the Render deploy)
docker build -t product-knowledge-assistant .
docker run -p 8000:8000 -e GROQ_API_KEY=your-key-here product-knowledge-assistant

# Run the Next.js frontend (separate terminal, requires the backend running)
cd frontend && npm install && npm run dev   # http://localhost:3000

# Build/lint the frontend
cd frontend && npm run build
cd frontend && npm run lint
```

## Architecture

This is a no-LangChain RAG (Retrieval-Augmented Generation) pipeline over a static JSON product catalog. It runs fully locally: sentence-transformers for embeddings, a persistent ChromaDB collection for vector search, and Groq (or local Ollama) for answer generation.

**Pipeline (data flow):**
`data/products.json` → `preprocessing/formatter.py` (product dict → text document) → `preprocessing/chunker.py` (line-based chunks with overlap) → `embeddings/embedder.py` (sentence-transformers vectors) → `retrieval/indexer.py` (`build_chroma_collection` — a persistent ChromaDB collection in cosine space, seeded from `data/product_embeddings.json` once on first startup) → `retrieval/search.py` (embed query, `collection.query(...)` for top-k, score = `1 - distance`) → `llm/prompt_builder.py` (grounded prompt) → `llm/provider.py` (dispatches to `llm/groq_client.py` or `llm/ollama_client.py` based on `LLM_PROVIDER`).

**LLM provider is pluggable.** `LLM_PROVIDER` (`groq` by default, or `ollama`) controls which client `generate_answer()` in `llm/provider.py` calls. Groq needs `GROQ_API_KEY` set in `.env` (free key at console.groq.com) — without it, `/ask` returns a clear 500 telling you so. Ollama needs a local server running with the model pulled. `ProductRAGService` just calls `generate_answer(...)`; it doesn't know which provider is active.

**`ProductRAGService` (`src/services/rag_service.py`) is the orchestration core.** Both entrypoints (`main.py` CLI and the FastAPI app) construct one service, call `initialize()`, then `answer_question()`. Everything else is stateless helper functions wired together here.

**Lazy artifact generation:** `initialize()` calls `_ensure_rag_artifacts()`, which generates `data/product_chunks.json` and `data/product_embeddings.json` on disk only if they are missing. Deleting these files forces a rebuild on next startup (e.g., after changing `products.json`, chunk settings, or the embedding model). The ChromaDB collection (persisted under `data/chroma_db/`, gitignored) is seeded from `product_embeddings.json` only when empty (`collection.count() == 0`) — deleting `data/chroma_db/` also forces a re-seed. The collection and embedding model are loaded/connected once at startup and cached on the service instance — they are expensive and meant to be reused across requests.

**FastAPI wiring:** `api/app.py` builds the service in the `lifespan` startup hook and stores it on `app.state.rag_service`. Routes (`api/routes.py`) read it back via the `get_rag_service` dependency — there is one shared, pre-warmed service per process, not one per request.

**Frontend (`frontend/`):** a separate Next.js 16 (App Router, TypeScript, Tailwind v4) app, scaffolded independently of the Python backend — it has its own `package.json`/`node_modules` and does not use the dual-import pattern below. It calls `POST /ask` via `frontend/lib/api.ts`, reading the backend URL from `NEXT_PUBLIC_API_BASE_URL` (see `frontend/.env.local.example`). The UI was ported from a Claude Design prototype (`design.md` §6); the design's mocked client-side retrieval/timers were replaced with real fetch calls and a real `/health` poll (`components/ApiStatusBadge.tsx`).

**Each source carries `category`/`color` from the product record, not the chunk text.** A retrieved chunk only covers a few lines of a product's formatted document (see "Chunking is line-based" below), so it often lacks the `Category`/`Color` lines entirely. `ProductRAGService.retrieve_sources` (`services/rag_service.py`) enriches each result by looking up `product_id` against `self.product_lookup` (built from `products.json` in `initialize()`) before returning it. Don't go back to parsing these out of `text` client-side. **`llm/prompt_builder.py`'s `format_retrieved_chunks` includes these enriched `Category`/`Color` fields in the LLM's context too** (not just the raw chunk `Text`) — without this, a strict "use only the retrieved facts" instruction makes the model wrongly claim a product doesn't match when the matching field (e.g. color) simply landed in a different chunk window than the one retrieved.

**Off-topic questions are rejected before the LLM is ever called.** `ProductRAGService.answer_question` checks the top retrieval score against `MIN_RELEVANCE_SCORE` (default `0.35`); if it's below that (or there are no sources), it returns a fixed `OFF_TOPIC_MESSAGE` with `sources: []` without building a prompt or hitting Groq/Ollama. This is a deterministic guardrail, not LLM-judgment-based — calibrated empirically (off-topic queries score ≤0.26, even weak on-topic matches score ≥0.44 on the 24-product catalog). `prompt_builder.py`'s instructions also tell the model to decline borderline cases as defense-in-depth, but the score gate is what actually saves the API call. The frontend (`SuccessView.tsx`) hides the sources panel and `AnswerCard.tsx` swaps its "Grounded in N sources" badge for "Outside catalog scope" when `sources` is empty.

## Conventions and gotchas

- **Dual-import pattern:** nearly every module under `src/` does `try: from src.X ... except ImportError: from X ...`. This lets the same file work both as a package (`uvicorn src.api.app:app`, run from project root) and when run with `src/` on the path. Preserve this pattern when adding modules.
- **Config is centralized in `src/config.py`**, loaded from `.env` (copy `.env.example` → `.env`). All tunables — `EMBEDDING_MODEL`, `OLLAMA_MODEL`, `TOP_K_RESULTS`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, etc. — flow through here and are passed as constructor defaults to `ProductRAGService`. Don't hardcode these elsewhere.
- **External dependencies the pipeline assumes at runtime:** the sentence-transformers model is downloaded from Hugging Face on first use then cached (offline thereafter via `local_files_only=True` fast path); a local Ollama server must be running with the configured model pulled (e.g. `ollama pull llama3.2:3b`).
- **Chunking is line-based**, not token-based: `CHUNK_SIZE`/`CHUNK_OVERLAP` count lines of the formatted product document, and each product field is one line (see `formatter.py`).
- `requirements.txt` is trimmed to the packages actually imported by `src/` (`fastapi`, `uvicorn`, `pydantic`, `python-dotenv`, `sentence-transformers`, `chromadb`, `numpy`, `groq`). If you add a new direct import, add it here too — don't let it drift back into a full env dump.
- **`tests/test_api.py` never runs the real FastAPI `lifespan`** (which would load the embedding model and build the Chroma collection) — Starlette's `TestClient` only triggers `lifespan` when used as a context manager (`with TestClient(app)`). Tests construct it plainly and set `app.state.rag_service` to a `MagicMock()` directly, so route tests are pure and fast. Don't switch to the `with` form unless you actually want the real pipeline to run.
- **`requirements-dev.txt` holds test-only deps** (currently just `httpx`, pinned to `0.27.2`) — `fastapi==0.109.0` pulls in `starlette==0.35.1`, whose `TestClient` still uses the `app=` shortcut that `httpx` removed in `0.28.0`; a bare `pip install httpx` will break `tests/test_api.py`.
- **`tests/test_retrieval.py` builds throwaway ChromaDB collections in `tempfile.mkdtemp()` dirs**, not `data/chroma_db/`. Cleanup uses `shutil.rmtree(path, ignore_errors=True)` because Chroma's Rust bindings keep `chroma.sqlite3`/HNSW files open past the test on Windows — a plain `tempfile.TemporaryDirectory()` would raise `PermissionError` on `__exit__`.
- **`Dockerfile` installs CPU-only `torch` *before* `requirements.txt`** (`pip install torch --index-url https://download.pytorch.org/whl/cpu`). Without this, `sentence-transformers` pulls plain `torch`, which defaults to the CUDA build and drags in ~2GB of unused NVIDIA wheels — wasteful (and slow to build) for Render's CPU-only free tier. If you ever bump the `torch`/`sentence-transformers` versions, keep this line ahead of the main install.
- **Deployment is documented in `README.md` § Deployment** (Render for the backend via `render.yaml`, Vercel for `frontend/`). `GROQ_API_KEY` and `CORS_ORIGINS` are set as real environment variables in each dashboard, not baked into the image or committed anywhere.
