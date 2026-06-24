"""FastAPI app entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from src.api.routes import router
    from src.config import APP_NAME, CORS_ORIGINS
    from src.services.rag_service import ProductRAGService
except ImportError:
    from api.routes import router
    from config import APP_NAME, CORS_ORIGINS
    from services.rag_service import ProductRAGService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create and cache the RAG service once when the API starts."""
    rag_service = ProductRAGService()
    rag_service.initialize()
    app.state.rag_service = rag_service
    yield


app = FastAPI(
    title=APP_NAME,
    version="0.2.0",
    description="FastAPI backend for the AI Product Knowledge Assistant.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
