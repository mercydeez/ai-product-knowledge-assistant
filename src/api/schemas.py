"""Pydantic request and response models for the API."""

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """Incoming request body for the ask endpoint."""

    question: str = Field(..., min_length=1, description="User question to ask the assistant.")


class SourceItem(BaseModel):
    """One retrieved source chunk returned in the response."""

    rank: int
    score: float
    chunk_id: str
    product_id: str
    product_name: str
    text: str


class AskResponse(BaseModel):
    """Successful response body for the ask endpoint."""

    question: str
    answer: str
    sources: list[SourceItem]
