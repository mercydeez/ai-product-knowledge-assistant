"""FastAPI app entrypoint."""

import logging
import time
from contextlib import asynccontextmanager
from typing import Any, Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

try:
    from src.api.rate_limit import limiter
    from src.api.routes import router
    from src.config import APP_NAME, CORS_ORIGINS, LOG_LEVEL
    from src.services.rag_service import ProductRAGService
except ImportError:
    from api.rate_limit import limiter
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

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Keep the same `{"detail": ...}` error shape the rest of the API uses."""
    return JSONResponse({"detail": f"Rate limit exceeded: {exc.detail}"}, status_code=429)


class RequestTimingMiddleware:
    """Raw ASGI middleware that logs request timing without buffering the response body.

    `@app.middleware("http")` compiles to Starlette's BaseHTTPMiddleware, which
    fully buffers a streaming response before forwarding it — that silently
    broke real-time token delivery on /ask/stream while looking fine on /ask
    (whose body is already complete before the response starts). A plain ASGI
    middleware only wraps `send`, so streamed chunks still reach the client as
    they're produced.
    """

    def __init__(self, app: Callable) -> None:
        self.app = app

    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()
        status_code = 500

        async def send_wrapper(message: dict[str, Any]) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                time_to_first_byte_ms = (time.perf_counter() - start) * 1000
                headers = list(message.get("headers", []))
                headers.append(
                    (b"x-process-time-ms", f"{time_to_first_byte_ms:.2f}".encode())
                )
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_wrapper)

        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "method=%s path=%s status=%s duration_ms=%.2f",
            scope["method"],
            scope["path"],
            status_code,
            duration_ms,
        )


app.add_middleware(RequestTimingMiddleware)

app.include_router(router)
