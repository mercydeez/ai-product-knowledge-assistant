"""API route definitions for the product knowledge assistant."""

import json

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

try:
    from src.api.schemas import AskRequest, AskResponse
    from src.services.rag_service import ProductRAGService
except ImportError:
    from api.schemas import AskRequest, AskResponse
    from services.rag_service import ProductRAGService


router = APIRouter()


def get_rag_service(request: Request) -> ProductRAGService:
    """Read the shared service instance that was created during app startup."""
    return request.app.state.rag_service


@router.get("/health")
def health_check() -> dict:
    """Simple health endpoint for quick API checks."""
    return {"status": "ok"}


@router.post("/ask", response_model=AskResponse)
def ask_product_question(request: AskRequest, http_request: Request) -> AskResponse:
    """Answer a product question using retrieval and the local Ollama model."""
    rag_service = get_rag_service(http_request)

    try:
        result = rag_service.answer_question(request.question)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return AskResponse(**result)


@router.post("/ask/stream")
def ask_product_question_stream(request: AskRequest, http_request: Request) -> StreamingResponse:
    """Stream a grounded answer as Server-Sent Events: sources, then tokens, then done."""
    rag_service = get_rag_service(http_request)

    def event_stream():
        try:
            for event in rag_service.answer_question_stream(request.question):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
