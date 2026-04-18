# AI Product Knowledge Assistant

Phase 1 foundation for a fashion and e-commerce product knowledge assistant. This setup is intentionally simple, modular, and ready for a future Retrieval-Augmented Generation (RAG) workflow without using LangChain.

## Project Goal

Build a production-minded Python project that will later support:

- product knowledge ingestion
- text chunking and embeddings
- vector search
- question answering over product data

This phase only prepares the project structure, configuration, and sample dataset.

## Project Structure

```text
ai-product-assistant/
├── data/
│   └── products.json
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   └── utils/
│       ├── __init__.py
│       └── data_loader.py
├── tests/
│   └── test_data_loader.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

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
OLLAMA_MODEL=llama3.2:3b
```

Note: the first run will download the embedding model from Hugging Face. Internet access is needed once, then it is cached locally.
For the final answer-generation step, start Ollama locally and pull a model such as `llama3.2:3b`.

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

What this project does not do yet:

- no FastAPI

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
