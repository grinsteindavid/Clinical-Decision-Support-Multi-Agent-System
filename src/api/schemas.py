"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request body for query endpoints."""

    query: str = Field(..., min_length=1, max_length=2000)


class ThreadCreate(BaseModel):
    """Request body for creating a thread."""

    title: str = Field(default="New Chat", max_length=255)


class ThreadUpdate(BaseModel):
    """Request body for updating a thread."""

    title: str = Field(..., min_length=1, max_length=255)


class ConfidenceScore(BaseModel):
    """Confidence scores from agent processing."""

    routing: float = Field(default=0.0, ge=0.0, le=1.0)
    retrieval: float = Field(default=0.0, ge=0.0, le=1.0)
    response: float = Field(default=0.0, ge=0.0, le=1.0)
    overall: float = Field(default=0.0, ge=0.0, le=1.0)


class QueryResponse(BaseModel):
    """Response from query endpoints."""

    route: Literal["tool_finder", "org_matcher", "workflow_advisor"] | None
    response: str
    tools_results: list[dict]
    orgs_results: list[dict]
    confidence: ConfidenceScore


class MessageResponse(BaseModel):
    """Response for a chat message."""

    id: UUID
    thread_id: UUID
    role: str
    content: str
    route: str | None
    created_at: datetime


class ThreadResponse(BaseModel):
    """Response for a chat thread."""

    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime


class ThreadDetailResponse(ThreadResponse):
    """Thread response with messages included."""

    messages: list[MessageResponse]


class HealthResponse(BaseModel):
    """Response for health check endpoint."""

    status: str
    service: str


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str


class SuccessResponse(BaseModel):
    """Standard success response."""

    success: bool
