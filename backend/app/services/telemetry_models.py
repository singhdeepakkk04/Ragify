from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RAGRunArtifacts:
    # Identity
    trace_id: str = ""
    project_id: int = 0
    user_id: Optional[int] = None
    supabase_user_id: Optional[str] = None

    # Query + response
    query: str = ""
    query_tier: str = "balanced"
    response: str = ""
    contexts: list[str] = field(default_factory=list)
    cached: bool = False

    # Token counts
    embedding_tokens: int = 0
    retrieval_chunks: int = 0
    context_tokens: int = 0
    completion_tokens: int = 0

    # Web search
    web_search_used: bool = False
    web_results_count: int = 0

    # Latency
    query_plan_ms: int = 0
    retrieval_ms: int = 0
    generation_ms: int = 0
    total_ms: int = 0
