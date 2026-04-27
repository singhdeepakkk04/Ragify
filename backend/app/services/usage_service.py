from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import tiktoken

from app.services.telemetry_models import RAGRunArtifacts

logger = logging.getLogger(__name__)


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    if not text:
        return 0
    try:
        enc = tiktoken.encoding_for_model(model)
    except Exception:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


@dataclass
class UsageRecord:
    project_id: int
    user_id: Optional[str]
    trace_id: str
    query_tier: str

    embedding_tokens: int = 0
    retrieval_chunks: int = 0
    context_tokens: int = 0
    completion_tokens: int = 0

    web_search_used: bool = False
    web_results_count: int = 0

    query_plan_ms: int = 0
    retrieval_ms: int = 0
    generation_ms: int = 0
    total_ms: int = 0


async def record_usage(record: UsageRecord, supabase) -> None:
    if not supabase:
        return

    try:
        supabase.table("query_usage").insert(
            {
                "project_id": record.project_id,
                "user_id": record.user_id,
                "trace_id": record.trace_id,
                "query_tier": record.query_tier,
                "embedding_tokens": record.embedding_tokens,
                "retrieval_chunks": record.retrieval_chunks,
                "context_tokens": record.context_tokens,
                "completion_tokens": record.completion_tokens,
                "web_search_used": record.web_search_used,
                "web_results_count": record.web_results_count,
                "query_plan_ms": record.query_plan_ms,
                "retrieval_ms": record.retrieval_ms,
                "generation_ms": record.generation_ms,
                "total_ms": record.total_ms,
            }
        ).execute()
    except Exception as e:
        logger.error(f"[Usage] Usage recording failed: {e}")


async def record_usage_from_artifacts(artifacts: RAGRunArtifacts, supabase) -> None:
    """Background-task wrapper: converts RAGRunArtifacts -> UsageRecord and inserts."""
    if not supabase:
        return

    if not artifacts or not artifacts.project_id:
        return
    if not (artifacts.trace_id or "").strip():
        return

    user_id = artifacts.supabase_user_id
    record = UsageRecord(
        project_id=artifacts.project_id,
        user_id=user_id,
        trace_id=artifacts.trace_id,
        query_tier=artifacts.query_tier,
        embedding_tokens=artifacts.embedding_tokens,
        retrieval_chunks=artifacts.retrieval_chunks,
        context_tokens=artifacts.context_tokens,
        completion_tokens=artifacts.completion_tokens,
        web_search_used=artifacts.web_search_used,
        web_results_count=artifacts.web_results_count,
        query_plan_ms=artifacts.query_plan_ms,
        retrieval_ms=artifacts.retrieval_ms,
        generation_ms=artifacts.generation_ms,
        total_ms=artifacts.total_ms,
    )
    await record_usage(record, supabase)
