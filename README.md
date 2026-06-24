# AI Product Knowledge Assistant

Phase 1 foundation for a fashion and e-commerce product knowledge assistant. This setup is intentionally simple, modular, and ready for a future Retrieval-Augmented Generation (RAG) workflow without using LangChain.

## Project Goal

Build a production-minded Python project that will later support:

- product knowledge ingestion
- text chunking and embeddings
- vector search
- question answering over product data

This phase only prepares the project structure, configuration, and sample dataset.
Phase 2 adds a FastAPI backend around the same local retrieval and Ollama pipeline.

## Project Structure

```text
ai-product-assistant/
├── data/
│   ├── product_chunks.json
│   ├── product_embeddings.json
│   └── products.json
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── config.py
│   ├── embeddings/
│   ├── llm/
│   ├── main.py
│   ├── preprocessing/
│   ├── retrieval/
│   ├── services/
│   └── utils/
├── tests/
│   └── test_data_loader.py
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## API Run

Start the API server:

```bash
uvicorn src.api.app:app --reload
```

Test the endpoint in PowerShell:

```powershell
$body = @{ question = "I need a breathable cotton shirt for everyday use." } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/ask" -Method Post -ContentType "application/json" -Body $body
```

## Frontend

A Next.js (App Router, TypeScript, Tailwind) UI lives in `frontend/`. It calls the FastAPI `/ask` endpoint and renders the grounded answer alongside the retrieved source chunks.

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open `http://localhost:3000`. The backend must be running (see above) and `CORS_ORIGINS` in `.env` must include `http://localhost:3000` (it does by default).

## Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd ai-product-assistant
```

### 2. Create virtual environment

```bash
py -3.11 -m venv .venv
```

Activate it:

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Mac/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables

Copy `.env.example` to `.env`:

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Mac/Linux:

```bash
cp .env.example .env
```

Then update the values if needed:

```env
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_PROVIDER=groq
GROQ_API_KEY=your-key-here
GROQ_MODEL=llama-3.3-70b-versatile
```

Note: the first run will download the embedding model from Hugging Face. Internet access is needed once, then it is cached locally.

For the final answer-generation step, the default provider is **Groq** (hosted, free tier) — get a key at https://console.groq.com/keys and set `GROQ_API_KEY` in `.env`. To use a local model instead, set `LLM_PROVIDER=ollama` and start Ollama locally with a pulled model such as `llama3.2:3b`.

### 5. Run the project

```bash
python src/main.py
```

Expected output:

```text
Loaded 12 products

First product:
Luna Everyday Cotton Shirt
```

### 6. Run tests

```bash
python -m unittest discover -s tests
```

## Current Scope

What this project does now:

- stores product knowledge in JSON
- loads configuration from environment variables
- prepares chunks for retrieval
- creates local embeddings
- runs FAISS similarity search
- generates a grounded final answer through Ollama
- exposes the pipeline through a FastAPI backend
- ships a Next.js frontend for asking questions and viewing cited sources

What this project does not do yet:

- no database
- no authentication
- no frontend

## Why This Structure

- `src/` keeps application code separate from data and documentation
- `config.py` centralizes environment-based settings
- `utils/data_loader.py` isolates JSON reading logic from application flow
- `data/products.json` gives us realistic business data for future RAG steps
- `tests/` prepares us for production-style development from day one

## Next Phase Direction

In the next step, we can start building the first RAG-ready components manually:

1. load product records
2. normalize text fields
3. create document text representations
4. prepare for chunking and embeddings

This keeps the project easy to understand while still following real-world engineering structure.
