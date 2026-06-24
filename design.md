# Design & Implementation Plan

AI Product Knowledge Assistant — full-stack RAG application.

This document is the single source of truth for the architecture, technology choices, build plan, and the UI design brief. It is written for two audiences: **engineers** (the implementation plan + API contract) and **Claude Design** (the UI brief at the end, which you will copy into Claude to generate the frontend).

---

## 1. Goal

A deployable, demoable GenAI product-search assistant. A user asks a natural-language question about a fashion/e-commerce catalog ("I need a breathable cotton shirt for everyday use"), and the app returns a grounded answer **plus the exact product chunks it retrieved** — visually proving the Retrieval-Augmented Generation (RAG) pipeline is real, not a generic chatbot.

**Resume positioning:** "Built and deployed a full-stack GenAI product-search assistant (RAG) — Next.js, FastAPI, Groq, ChromaDB — with a live demo and CI/CD."

**Hard constraint:** everything must run on **free tiers**. No paid cloud.

---

## 2. Architecture

### 2.1 High-level

```
┌─────────────────────────┐         HTTPS / JSON          ┌──────────────────────────────┐
│   Frontend (Next.js)    │  ───────────────────────────> │     Backend (FastAPI)        │
│   React + Tailwind      │   POST /ask  { question }     │     ProductRAGService        │
│   Deployed on Vercel    │ <───────────────────────────  │     Deployed on Render / HF  │
│                         │   { answer, sources[] }       │                              │
└─────────────────────────┘                               └───────────────┬──────────────┘
                                                                           │
                                          ┌────────────────────────────────┼───────────────────────────┐
                                          │                                │                           │
                                   ┌──────▼───────┐              ┌─────────▼─────────┐       ┌─────────▼─────────┐
                                   │  ChromaDB    │              │ sentence-         │       │   Groq API        │
                                   │ (vector DB,  │              │ transformers      │       │ (LLM generation,  │
                                   │  persistent) │              │ (query embedding) │       │  free tier)       │
                                   └──────────────┘              └───────────────────┘       └───────────────────┘
```

### 2.2 RAG pipeline (backend data flow)

This already exists in the codebase and is being upgraded (FAISS → ChromaDB, Ollama → Groq):

```
data/products.json
   → formatter.py        (product dict → text document)
   → chunker.py          (line-based chunks with overlap)
   → embedder.py         (sentence-transformers → vectors)
   → ChromaDB            (persistent vector store + similarity search)   [replaces FAISS+JSON]
   → search              (embed query → top-k chunks)
   → prompt_builder.py   (grounded prompt with retrieved context)
   → Groq API            (answer generation)                            [replaces Ollama]
```

`ProductRAGService` (`src/services/rag_service.py`) remains the orchestration core. The FastAPI `lifespan` hook builds and caches one service per process; routes read it from `app.state`.

### 2.3 Why these choices

- **Next.js + React + Tailwind** — modern full-stack signal; UAE market values React; deploys free on Vercel.
- **Groq** — free, fast hosted LLM so the public demo works for anyone (no local Ollama dependency).
- **ChromaDB** — a real persistent vector database instead of in-memory FAISS + JSON; production-shaped, still free and local to the backend container.
- **FastAPI** — already in place; gives free Swagger docs as a secondary demo.

---

## 3. Technology Stack

| Layer | Technology | Notes |
|---|---|---|
| Frontend | Next.js (App Router), React, TypeScript, Tailwind CSS | Generated via Claude Design |
| Backend | FastAPI, Pydantic, Uvicorn | Existing |
| LLM | Groq API (e.g. `llama-3.3-70b-versatile`) | Free tier; provider abstraction keeps Ollama as fallback |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) | Existing; cached after first download |
| Vector DB | ChromaDB (persistent client) | Replaces FAISS + JSON |
| Config | python-dotenv / `.env` | Existing |
| Containerization | Docker | Backend only |
| CI/CD | GitHub Actions | Lint + tests on push |
| Hosting (frontend) | Vercel free tier | `*.vercel.app` link |
| Hosting (backend) | Render free tier or Hugging Face Spaces (Docker) | Both free |

---

## 4. Implementation Plan (phased)

Work top-to-bottom. Each phase is independently shippable.

**Phase A — Groq LLM provider** ✅ implemented
- `src/llm/groq_client.py` calls Groq's chat completions API via the `groq` SDK (already pinned in `requirements.txt`).
- `src/llm/provider.py` is the selector — `generate_answer(prompt, provider, ...)` dispatches to `call_groq` or `call_ollama`. `ProductRAGService` calls it instead of `call_ollama` directly, so it stays provider-agnostic.
- `LLM_PROVIDER` (default `groq`), `GROQ_API_KEY`, `GROQ_MODEL` (default `llama-3.3-70b-versatile`) added to `config.py` and `.env.example`. Set `LLM_PROVIDER=ollama` to fall back to local Ollama.
- A missing `GROQ_API_KEY` raises a friendly `RuntimeError` pointing to `https://console.groq.com/keys`, surfaced through `/ask` as a 500 with that `detail` message — verified end-to-end against the live API.

**Phase B — ChromaDB vector store** ✅ implemented
- `retrieval/indexer.py`'s `build_chroma_collection()` replaces the FAISS `IndexFlatIP` builder with a `chromadb.PersistentClient` collection (cosine space) persisted under `data/chroma_db/` (gitignored — regenerated from `data/product_embeddings.json`).
- `retrieval/search.py`'s `search_similar_chunks()` now queries the collection (`collection.query(...)`) instead of a FAISS index; `score = 1 - distance` keeps the same 0..1 "higher is better" semantics. The `sources` shape (rank/score/chunk_id/product_id/product_name/text) is unchanged.
- Ingestion seeds the collection on startup only if empty (`collection.count() == 0`), mirroring the existing lazy-artifact behavior for the chunk/embedding JSON files.

**Phase C — API hardening for a public frontend**
- Add CORS middleware (allow the Vercel domain + localhost).
- Add structured logging (use existing `LOG_LEVEL`) and request timing.
- Confirm the `/ask` and `/health` contract (Section 5) is stable — the UI depends on it.

**Phase D — Frontend (Next.js)** ✅ implemented
- Built from the Claude Design prototype "Product Knowledge Assistant.dc.html" (Section 6 brief), imported via the `claude_design` MCP connector.
- Scaffolded with `create-next-app` → Next.js 16, React 19, TypeScript, Tailwind CSS v4 (CSS-first `@theme` tokens) under `frontend/`.
- The design's mocked client-side retrieval (`tokenize`/`scoreProduct`/`retrieve`/fixed `setTimeout` steps) was replaced with a real typed client (`frontend/lib/api.ts`) calling `POST /ask`, and a real `/health` poll for the "API connected" badge.
- `category`/`color` were added to the `/ask` response (`SourceItem`, populated from the product record in `ProductRAGService.retrieve_sources`) after testing showed a single chunk often doesn't contain those fields (chunker.py splits each product into multiple line-windows) — text-parsing them client-side was unreliable. `frontend/lib/chunk.ts` only does `colorToHex`/`luminance` now (color-name → swatch hex).
- Wired to the backend via `NEXT_PUBLIC_API_BASE_URL` (`frontend/.env.local.example`).

**Phase E — Containerize + deploy**
- Dockerfile for the backend; deploy to Render / HF Spaces.
- Deploy frontend to Vercel; set the API base URL env var.

**Phase F — Quality signals**
- Expand tests (retrieval + API layer). ✅ implemented — `tests/test_retrieval.py` (ChromaDB seeding/idempotency/ranking against a fake embedding model) and `tests/test_api.py` (FastAPI routes against a mocked `ProductRAGService`, covering 200/400/422/500 paths). See `requirements-dev.txt` for the one test-only dependency.
- RAG evaluation script (hit-rate / MRR over a small question set). Still open.
- GitHub Actions workflow (lint + tests). Still open.

---

## 5. API Contract (frozen — the UI builds against this)

The frontend integrates with these endpoints. Do not change shapes without updating the UI.

### `GET /health`
```json
{ "status": "ok" }
```

### `POST /ask`
Request:
```json
{ "question": "I need a breathable cotton shirt for everyday use." }
```
Response:
```json
{
  "question": "I need a breathable cotton shirt for everyday use.",
  "answer": "The Luna Everyday Cotton Shirt is a breathable 100% cotton...",
  "sources": [
    {
      "rank": 1,
      "score": 0.8123,
      "chunk_id": "SKU-1001_chunk_1",
      "product_id": "SKU-1001",
      "product_name": "Luna Everyday Cotton Shirt",
      "category": "Tops",
      "color": "White",
      "text": "Product Name: Luna Everyday Cotton Shirt\nCategory: Tops\n..."
    }
  ]
}
```
Errors: `400` (empty question) and `500` (pipeline failure), each `{ "detail": "<message>" }`.

---

## 6. Claude Design — UI Brief

> **How to use this section:** copy everything below the line into Claude (claude.ai) to generate the frontend. It is written as a direct, self-contained prompt. After Claude generates the UI, paste its output/prompt back to the engineering side for backend integration.

---

**Build a frontend for an AI Product Knowledge Assistant — a RAG-powered fashion/e-commerce product-search chat app.**

**Tech:** Next.js (App Router) + React + TypeScript + Tailwind CSS. Single-page experience. No backend code — this is UI only; it calls an existing API.

**Core concept:** the user types a natural-language question about clothing products. The app shows the AI's grounded answer AND the retrieved source product chunks side-by-side, so the retrieval is visible and trustworthy. This "answer + sources" split is the signature feature — make it prominent.

**Layout:**
- A clean, centered chat/search interface. Header with the app name "AI Product Knowledge Assistant" and a short tagline ("Ask anything about our catalog — answers grounded in real product data").
- A prominent input box at the top or bottom with a Send button; submit on Enter. Include 3–4 example-question chips users can click (e.g. "breathable cotton shirt for everyday use", "black slim-fit jeans", "a floral summer dress", "something warm for winter").
- Results area with two visually distinct parts:
  1. **Answer card** — the AI's text answer, clearly styled as the primary response.
  2. **Sources panel** — a list/grid of "source" cards, each showing: `product_name` (bold), a `rank` badge (#1, #2…), a relevance `score` rendered as a percentage or a small bar (score is 0–1, higher = better), `product_id`, and the chunk `text` (in a smaller, monospace-ish or muted style). Label this section "Retrieved Sources" with a subtitle like "The product data used to generate this answer."

**States:** empty/initial (show examples + a friendly hint), loading (skeleton or animated "Searching the catalog…" indicator), success (answer + sources), and error (friendly message, e.g. "Something went wrong — please try again").

**Style:** modern, premium, e-commerce/fashion feel. Clean typography, generous whitespace, rounded cards, soft shadows, subtle animations on result appearance. Support light and dark mode. Fully responsive (mobile-first). Tasteful accent color (suggest a deep indigo or emerald). Should look like a polished product, not a tutorial demo.

**API integration:** call `POST {NEXT_PUBLIC_API_BASE_URL}/ask` with JSON body `{ "question": string }`. The response is:
```ts
type Source = {
  rank: number;
  score: number;        // 0..1, display as percentage or bar
  chunk_id: string;
  product_id: string;
  product_name: string;
  text: string;
};
type AskResponse = {
  question: string;
  answer: string;
  sources: Source[];
};
```
Read the API base URL from `process.env.NEXT_PUBLIC_API_BASE_URL` (default to `http://127.0.0.1:8000` for local dev). Handle non-200 responses by reading `detail` and showing the error state. Keep the fetch logic in a small typed client (e.g. `lib/api.ts`).

**Deliverables from Claude Design:** the page component(s), the source-card and answer-card components, the typed API client, Tailwind styling, and loading/error states. Keep components modular and typed.

---

## 7. Open items / decisions still to make

- Final Groq model id (default `llama-3.3-70b-versatile`).
- Backend host: Render (sleeps when idle, true backend) vs Hugging Face Spaces (ML-recognized, Docker). Decide at Phase E.
- Whether to keep multi-turn history (Phase F stretch) or stay single-shot.
