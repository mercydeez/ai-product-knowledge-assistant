"""API route definitions for the product knowledge assistant."""

from fastapi import APIRouter, HTTPException, Request

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
