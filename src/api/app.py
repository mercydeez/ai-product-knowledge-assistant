"""FastAPI app entrypoint."""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

try:
    from src.api.routes import router
    from src.config import APP_NAME, CORS_ORIGINS, LOG_LEVEL
    from src.services.rag_service import ProductRAGService
except ImportError:
    from api.routes import router
    from config import APP_NAME, CORS_ORIGINS, LOG_LEVEL
    from services.rag_service import ProductRAGService


logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("api.requests")


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


@app.middleware("http")
async def log_request_timing(request: Request, call_next):
    """Log method/path/status/duration for every request and expose it as a header."""
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000

    response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"
    logger.info(
        "method=%s path=%s status=%s duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


app.include_router(router)
