"""Ragi-fy SDK type definitions — Pydantic models for API responses."""

from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── Projects ────────────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    """Payload to create a new project."""
    name: str
    description: Optional[str] = None
    project_type: str
    llm_model: Optional[str] = "gpt-3.5-turbo"
    embedding_model: Optional[str] = "text-embedding-3-small"
    temperature: Optional[float] = 0.0
    chunk_size: Optional[int] = 1000
    chunk_overlap: Optional[int] = 200
    top_k: Optional[int] = 4
    deployment_environment: Optional[str] = "dev"
    is_public: Optional[bool] = False
    config: Optional[Dict[str, Any]] = None


class ProjectUpdate(BaseModel):
    """Payload to update a project."""
    name: Optional[str] = None
    description: Optional[str] = None
    project_type: Optional[str] = None
    llm_model: Optional[str] = None
    embedding_model: Optional[str] = None
    temperature: Optional[float] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    top_k: Optional[int] = None
    deployment_environment: Optional[str] = None
    is_public: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None


class Project(BaseModel):
    id: int
    owner_id: int
    name: str
    description: Optional[str] = None
    project_type: str
    llm_model: Optional[str] = None
    embedding_model: Optional[str] = None
    temperature: Optional[float] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    top_k: Optional[int] = None
    deployment_environment: Optional[str] = None
    is_public: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None
    created_at: datetime


# ── Documents ───────────────────────────────────────────────────────────────

class Document(BaseModel):
    id: int
    filename: str
    project_id: int
    status: str
    created_at: datetime


# ── RAG ─────────────────────────────────────────────────────────────────────

class Citation(BaseModel):
    filename: str
    page_number: Optional[int] = None
    snippet: str


class QueryResponse(BaseModel):
    """Accumulated response from a streaming RAG query."""
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    cached: bool = False


class StreamChunk(BaseModel):
    """A single chunk from a streaming RAG query (ndjson line)."""
    type: str  # "chunk", "citations", "done", "error"
    content: Optional[str] = None
    citations: Optional[List[Citation]] = None
    error: Optional[str] = None


# ── API Keys ────────────────────────────────────────────────────────────────

class APIKey(BaseModel):
    id: int
    name: Optional[str] = None
    project_id: int
    prefix: str
    is_active: bool
    created_at: datetime


class APIKeyWithPlaintext(APIKey):
    plaintext_key: str


# ── Usage ───────────────────────────────────────────────────────────────────

class UsageStats(BaseModel):
    total_queries: int
    queries_today: int
    queries_this_week: int
    total_documents: int
    total_projects: int
    avg_latency_ms: float
    rate_limit: Dict[str, Any]
    model_breakdown: List[Dict[str, Any]]
    project_breakdown: List[Dict[str, Any]]
    recent_queries: List[Dict[str, Any]]
    daily_usage: List[Dict[str, Any]]


class ProjectLog(BaseModel):
    id: int
    query: str
    model_used: str
    tokens_used: int
    latency_ms: int
    created_at: str


class ProjectLogs(BaseModel):
    total: int
    logs: List[ProjectLog]


# ── Feedback ──────────────────────────────────────────────────────────────

class Feedback(BaseModel):
    id: int
    project_id: int
    request_id: str
    rating: str
    comment: Optional[str] = None


# ── Users ───────────────────────────────────────────────────────────────────

class UserProfile(BaseModel):
    id: int
    email: str
    display_name: Optional[str] = None
    role: str
    is_active: bool


# ── Models ──────────────────────────────────────────────────────────────────

class Model(BaseModel):
    """An available LLM model from the registry."""
    id: str = ""
    name: str = ""
    provider: str = ""
    # Dynamic keys — the server returns dicts, so we accept extras
    model_config = {"extra": "allow"}
