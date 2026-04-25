
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
import time

from app.api import deps
from app.crud import project as crud_project
from app.models.user import User
from app.models.usage_log import UsageLog
from app.core.rag.retrieval import query_project
from app.core.rate_limiter import enforce_daily_query_quota
from app.core.guardrails import check_input
from app.core.query_cache import query_cache

router = APIRouter()


class RAGQuery(BaseModel):
    project_id: int = Field(..., gt=0, description="Target project ID")
    query: str = Field(..., min_length=1, max_length=2000, description="Natural language query")
    top_k: int = Field(default=4, ge=1, le=50, description="Number of chunks to retrieve")


class Citation(BaseModel):
    filename: str
    page_number: Optional[int] = None
    snippet: str


class RAGResponse(BaseModel):
    answer: str
    citations: List[Citation]
    cached: bool = False




@router.post("/query")
async def query_rag(
    request: Request,
    *,
    db: AsyncSession = Depends(deps.get_db),
    rag_query: RAGQuery,
    current_user: User = Depends(enforce_daily_query_quota),
) -> Any:
    """
    Query the RAG pipeline with caching, guardrails, and rate limiting.
    Supports API Key (Project Scoped) or Bearer Token (User Scoped).
    """
    # 0. API Key Scoping Check
    if hasattr(request.state, "api_key_project") and request.state.api_key_project:
        if request.state.api_key_project.id != rag_query.project_id:
             raise HTTPException(
                status_code=403, 
                detail="API Key is not authorized for this project."
            )

    # Input guardrail — blocks explicit content and prompt injections
    sanitized_query = check_input(rag_query.query)

    # Verify project ownership (If API key, current_user is owner, so this passes)
    project = await crud_project.get_project(
        db, project_id=rag_query.project_id, user_id=current_user.id
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    model_used = getattr(project, 'llm_model', 'gpt-3.5-turbo') or 'gpt-3.5-turbo'

    try:
        from fastapi.responses import StreamingResponse
        
        return StreamingResponse(
            query_project(
                db,
                rag_query.project_id,
                sanitized_query,
                user_id=current_user.id,
                model_id=model_used,
            ),
            media_type="application/x-ndjson"
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error("RAG Generation failed with unexpected error", exc_info=True)
        raise HTTPException(
            status_code=500, detail="An internal server error occurred while processing your request. Please try again later."
        )


@router.get("/cache/stats")
async def cache_stats(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get cache statistics."""
    return query_cache.stats
