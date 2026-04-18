"""Application configuration helpers."""

from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

APP_NAME = os.getenv("APP_NAME", "AI Product Knowledge Assistant")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DATA_FILE = os.getenv("DATA_FILE", "data/products.json")
CHUNKS_OUTPUT_FILE = os.getenv("CHUNKS_OUTPUT_FILE", "data/product_chunks.json")
EMBEDDINGS_OUTPUT_FILE = os.getenv("EMBEDDINGS_OUTPUT_FILE", "data/product_embeddings.json")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "10"))
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
SAMPLE_QUERY = os.getenv(
    "SAMPLE_QUERY",
    "I need a breathable white cotton shirt for everyday use.",
)
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "3"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "4"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "1"))

DATA_PATH = str(BASE_DIR / DATA_FILE)
CHUNKS_OUTPUT_PATH = str(BASE_DIR / CHUNKS_OUTPUT_FILE)
EMBEDDINGS_OUTPUT_PATH = str(BASE_DIR / EMBEDDINGS_OUTPUT_FILE)
